"""Launcher regressions using isolated projects and fake engine executables."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("bash"), "Bash is required")
class LauncherTests(unittest.TestCase):
    shell = "bash"

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        shutil.copytree(ROOT / "tools" / "run", self.project / "tools" / "run")
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.home = self.root / "home"
        self.home.mkdir()
        self.trace = self.root / "trace"
        self.env = {
            **os.environ,
            "PATH": str(self.bin) + os.pathsep + os.environ["PATH"],
            "HOME": str(self.home),
            "APPDATA": str(self.root / "userdata"),
            "GODOT": "",
            "GODOT_FLAGS": "",
            "TRACE": str(self.trace),
            "IMPORT_ERROR": "",
            "IMPORT_EXIT": "0",
            "PROBE_EXIT": "0",
            "PROBE_MARKER": "REPENTANCE GODOT OK",
        }
        self.write_executable("dotnet", 'print("dotnet")\n')
        self.engine = self.write_executable(
            "godot",
            """\
import os
import sys

args = sys.argv[1:]
with open(os.environ["TRACE"], "a") as trace:
    trace.write(" ".join(args) + "\\n")
if "--script" in args:
    if os.environ["PROBE_MARKER"]:
        print(os.environ["PROBE_MARKER"])
    sys.exit(int(os.environ["PROBE_EXIT"]))
if "--import" in args:
    if os.environ["IMPORT_ERROR"]:
        print(os.environ["IMPORT_ERROR"], file=sys.stderr)
    sys.exit(int(os.environ["IMPORT_EXIT"]))
print("FILM OK")
print("PAUSE TEST OK")
""",
        )

    def write_executable(self, name, body):
        path = self.bin / name
        path.write_text(f"#!{sys.executable}\n{body}", encoding="utf-8")
        path.chmod(0o755)
        return path

    def run_launcher(self, script="film.sh", *args):
        if self.shell == "pwsh":
            script = script.replace(".sh", ".ps1")
            options = {"--no-clean": "-NoClean", "--godot": "-Godot"}
            command = ["pwsh", "-NoProfile", "-File"]
            args = tuple(options.get(arg, arg) for arg in args)
        else:
            command = ["bash"]
        return subprocess.run(
            [*command, str(self.project / "tools" / "run" / script), *args],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=20,
        )

    def assert_no_game(self):
        for line in self.trace.read_text().splitlines():
            self.assertTrue("--script" in line or "--import" in line, line)

    def test_standard_editor_rejected_before_cleanup(self):
        self.env["PROBE_EXIT"] = "1"
        self.env["PROBE_MARKER"] = ""
        for script, args in (("film.sh", ()), ("test.sh", ("pause",))):
            with self.subTest(script=script):
                sentinel = self.project / ".godot" / "keep"
                sentinel.parent.mkdir(exist_ok=True)
                sentinel.touch()
                result = self.run_launcher(script, *args, "--godot", str(self.engine))
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(".NET/Mono", result.stderr)
                self.assertTrue(sentinel.exists())
                self.assertNotIn("dotnet", result.stdout)
                self.assert_no_game()

    def test_probe_needs_marker_even_after_zero_exit(self):
        self.env["PROBE_MARKER"] = ""
        result = self.run_launcher("film.sh", "--godot", str(self.engine))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn("dotnet", result.stdout)
        self.assert_no_game()

    def test_probe_accepts_windows_line_endings(self):
        self.env["PROBE_MARKER"] = "REPENTANCE GODOT OK\r"
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_explicit_path_takes_precedence_over_environment(self):
        self.env["GODOT"] = "/missing/editor"
        engine = self.bin / "editor with spaces"
        self.engine.rename(engine)
        result = self.run_launcher("film.sh", "--no-clean", "--godot", str(engine))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"Godot: {engine}", result.stdout)

    def test_invalid_environment_does_not_fall_back(self):
        self.env["GODOT"] = "/missing/editor"
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("/missing/editor", result.stderr)
        self.assertFalse(self.trace.exists())

    def test_discovery_skips_standard_editor(self):
        self.write_executable("godot_console", 'print("standard editor")\n')
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"Godot: {self.engine}", result.stdout)
        self.assertIn("Cannot use Godot", result.stdout + result.stderr)

    def test_discovery_checks_install_folder_after_path(self):
        if self.shell == "pwsh":
            self.skipTest("PowerShell's install-folder fallback is Windows-specific")
        self.engine.write_text(f"#!{sys.executable}\nprint('standard editor')\n")
        installed = self.home / "godot" / "Godot_v4_test_mono_linux.x86_64"
        installed.parent.mkdir()
        shutil.copy(self.bin / "dotnet", installed)
        installed.write_text(
            f"#!{sys.executable}\n"
            "print('REPENTANCE GODOT OK')\nprint('FILM OK')\n",
            encoding="utf-8",
        )
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"Godot: {installed}", result.stdout)

    def test_import_errors_stop_film_and_test_even_after_zero_exit(self):
        for script, args in (("film.sh", ()), ("test.sh", ("pause",))):
            for error in (
                "ERROR: No loader found",
                "SCRIPT ERROR: Parse Error",
                "USER ERROR: Failed",
                "Unhandled exception: Failed",
            ):
                with self.subTest(script=script, error=error):
                    self.trace.unlink(missing_ok=True)
                    self.env["IMPORT_ERROR"] = error
                    result = self.run_launcher(script, *args, "--no-clean")
                    self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn("Godot import logged errors", result.stderr)
                    self.assertIn(error, (self.project / "logs" / "import.log").read_text())
                    self.assert_no_game()

    def test_nonzero_import_exit_stops_launch(self):
        self.env["IMPORT_EXIT"] = "3"
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exit code 3", result.stderr)
        self.assert_no_game()

    def test_import_warnings_do_not_block_launch(self):
        self.env["IMPORT_ERROR"] = "WARNING: harmless warning"
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Film finished.", result.stdout)

    def test_unit_suite_does_not_require_godot(self):
        self.env["GODOT"] = "/missing/editor"
        result = self.run_launcher("test.sh", "unit", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("All suites passed.", result.stdout)
        self.assertFalse(self.trace.exists())


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell is required")
class PowerShellLauncherTests(LauncherTests):
    shell = "pwsh"


if __name__ == "__main__":
    unittest.main()
