"""Launcher regressions using isolated projects and fake engine executables."""

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
WINDOWS = os.name == "nt"


def find_bash():
    """Bash for the .sh launchers. On Windows, Git Bash: System32\\bash.exe is the WSL launcher."""
    if os.environ.get("LAUNCHER_TEST_BASH"):
        return os.environ["LAUNCHER_TEST_BASH"]
    if not WINDOWS:
        return shutil.which("bash")
    roots = [os.environ.get(v) for v in ("ProgramFiles", "ProgramW6432", "ProgramFiles(x86)", "LOCALAPPDATA")]
    git = shutil.which("git")
    candidates = [Path(r) / "Git" / "bin" / "bash.exe" for r in roots if r]
    candidates += [Path(r) / "Programs" / "Git" / "bin" / "bash.exe" for r in roots if r]
    if git:
        candidates.append(Path(git).resolve().parents[1] / "bin" / "bash.exe")
    return next((str(c) for c in candidates if c.is_file()), None)


BASH = find_bash()


@unittest.skipUnless(BASH, "Bash is required (Git Bash on Windows)")
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
            "BUILD_EXIT": "0",
            "GAME_OUTPUT": "FILM OK\nPAUSE TEST OK",
            "GAME_ERROR": "",
            "GAME_EXIT": "0",
            "EVENTS": str(self.root / "events"),
            "REAL_DOTNET": shutil.which("dotnet") or "",
        }
        for name in ("godot_console", "godot-mono", "godot4-mono", "godot4"):
            self.write_executable(name, "import sys\nsys.exit(1)\n")
        self.write_executable(
            "dotnet",
            """\
import os
import sys

# PowerShell installed as a .NET tool also starts through dotnet.
if sys.argv[1] not in ("build", "test"):
    os.execv(os.environ["REAL_DOTNET"], ["dotnet", *sys.argv[1:]])
with open(os.environ["EVENTS"], "a") as events:
    events.write(sys.argv[1] + "\\n")
print("dotnet")
if sys.argv[1] == "build":
    sys.exit(int(os.environ["BUILD_EXIT"]))
""",
        )
        self.engine = self.write_executable(
            "godot",
            """\
import os
import sys

args = sys.argv[1:]
with open(os.environ["TRACE"], "a") as trace:
    trace.write(" ".join(args) + "\\n")
if "--script" in args:
    with open(os.environ["EVENTS"], "a") as events:
        events.write("probe\\n")
    if os.environ["PROBE_MARKER"]:
        print(os.environ["PROBE_MARKER"])
    sys.exit(int(os.environ["PROBE_EXIT"]))
if "--import" in args:
    with open(os.environ["EVENTS"], "a") as events:
        events.write("import\\n")
    if os.environ["IMPORT_ERROR"]:
        print(os.environ["IMPORT_ERROR"], file=sys.stderr)
    sys.exit(int(os.environ["IMPORT_EXIT"]))
with open(os.environ["EVENTS"], "a") as events:
    events.write("game\\n")
if os.environ["GAME_OUTPUT"]:
    print(os.environ["GAME_OUTPUT"])
if os.environ["GAME_ERROR"]:
    print(os.environ["GAME_ERROR"], file=sys.stderr)
sys.exit(int(os.environ["GAME_EXIT"]))
""",
        )

    def shebang(self):
        if WINDOWS:
            # Git Bash runs shebang scripts, given a POSIX path (C:\x\python.exe -> /c/x/python.exe).
            drive, rest = os.path.splitdrive(sys.executable)
            return f"#!/{drive[0].lower()}{rest.replace(os.sep, '/')}"
        return f"#!{sys.executable}"

    def write_executable(self, name, body):
        if WINDOWS and self.shell == "pwsh":
            # PowerShell can't run a shebang script; a .cmd wrapper runs the body kept outside PATH.
            bodies = self.root / "bodies"
            bodies.mkdir(exist_ok=True)
            script = bodies / f"{name}.py"
            script.write_text(body, encoding="utf-8")
            path = self.bin / f"{name}.cmd"
            path.write_text(f'@"{sys.executable}" "{script}" %*\r\n@exit /b %ERRORLEVEL%\r\n', encoding="utf-8")
            return path
        path = self.bin / name
        path.write_text(f"{self.shebang()}\n{body}", encoding="utf-8")
        path.chmod(0o755)
        return path

    def rename_engine(self, name):
        engine = self.bin / (name + self.engine.suffix)
        self.engine.rename(engine)
        return engine

    def found(self, path):
        """A path as the launcher prints one it discovered (Git Bash prints POSIX paths)."""
        if WINDOWS and self.shell == "bash":
            return subprocess.run(
                [BASH, "-c", 'cygpath -u "$1"', "_", str(path)], capture_output=True, text=True, check=True
            ).stdout.strip()
        return str(path)

    def run_launcher(self, script="film.sh", *args, cwd=None):
        if self.shell == "pwsh":
            script = script.replace(".sh", ".ps1")
            options = {
                "--no-clean": "-NoClean", "--godot": "-Godot", "--ending": "-Ending", "--from": "-From",
            }
            command = ["pwsh", "-NoProfile", "-File"]
            args = tuple(options.get(arg, arg) for arg in args)
        else:
            command = [BASH]
        return subprocess.run(
            [*command, str(self.project / "tools" / "run" / script), *args],
            env=self.env,
            capture_output=True,
            text=True,
            timeout=60,
            cwd=cwd,
        )

    def assert_no_game(self):
        for line in self.trace.read_text().splitlines():
            self.assertTrue("--script" in line or "--import" in line, line)

    def test_standard_editor_rejected_before_cleanup(self):
        self.env["PROBE_EXIT"] = "1"
        self.env["PROBE_MARKER"] = ""
        for script, args in (("film.sh", ()), ("test.sh", ("pause",)), ("game.sh", ())):
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
        engine = self.rename_engine("editor with spaces")
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
        self.assertIn(f"Godot: {self.found(self.engine)}", result.stdout)
        self.assertIn("Cannot use Godot", result.stdout + result.stderr)

    def test_discovery_checks_install_folder_after_path(self):
        if self.shell == "pwsh":
            self.skipTest("PowerShell's install-folder fallback is Windows-specific")
        # A real Godot installed on this machine must not win the search.
        self.env["LOCALAPPDATA"] = str(self.root / "localappdata")
        self.engine.write_text(f"{self.shebang()}\nprint('standard editor')\n")
        installed = self.home / "godot" / "Godot_v4_test_mono_linux.x86_64"
        installed.parent.mkdir()
        installed.write_text(
            f"{self.shebang()}\n"
            "print('REPENTANCE GODOT OK')\nprint('FILM OK')\n",
            encoding="utf-8",
        )
        installed.chmod(0o755)
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"Godot: {self.found(installed)}", result.stdout)

    def test_import_errors_stop_all_launchers_even_after_zero_exit(self):
        for script, args in (("film.sh", ()), ("test.sh", ("pause",)), ("game.sh", ())):
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

    def test_android_plugin_shutdown_noise_does_not_block_launch(self):
        self.env["IMPORT_ERROR"] = (
            'ERROR: EditorSettings not instantiated yet when getting setting "export/android/shutdown_adb_on_exit".'
        )
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Film finished.", result.stdout)

    def test_android_plugin_sdk_path_noise_does_not_block_launch(self):
        self.env["IMPORT_ERROR"] = (
            'ERROR: EditorSettings not instantiated yet when getting setting "export/android/android_sdk_path".'
        )
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Film finished.", result.stdout)

    def test_import_warnings_do_not_block_launch(self):
        self.env["IMPORT_ERROR"] = "WARNING: harmless warning"
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Film finished.", result.stdout)

    def test_unit_suite_does_not_require_godot(self):
        self.env["GODOT"] = "/missing/editor"
        for name in ("Repentance.Rules.Tests", "Repentance.Content.Tests"):
            (self.project / "tests" / name).mkdir(parents=True)
            (self.project / "tests" / name / f"{name}.csproj").write_text("<Project />")
        result = self.run_launcher("test.sh", "unit", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("All suites passed.", result.stdout)
        self.assertFalse(self.trace.exists())
        self.assertEqual(Path(self.env["EVENTS"]).read_text().split().count("test"), 2)

    def test_unit_suite_fails_without_test_projects(self):
        result = self.run_launcher("test.sh", "unit", "--no-clean")
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("No test projects", result.stdout + result.stderr)

    def test_film_default_speed_and_options(self):
        result = self.run_launcher("film.sh", "--no-clean")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("--film=1 --ending=2 --from=act1", self.trace.read_text())
        self.assertTrue((self.project / "logs" / "film_1x.log").exists())

    def test_film_ending_titles_map_to_numbers(self):
        for ending, number in (
            ("walk-away", "1"), ("spare-the-old-man", "1-oldman"), ("Give-Up", "1-steps"),
            ("Eleanor-Escapes", "1-caleb"), ("1-caleb", "1-caleb"),
            ("escape-together", "2"), ("escape-alone", "3"), ("prison-eleanor-visits", "4"),
            ("prison-caleb-visits", "5"), ("turn-himself-in", "6"), ("last-entry", "7"),
            ("eleanor-burns-the-house", "8"), ("eleanor-confesses", "9"),
            ("she-leaves-by-the-car", "10"), ("SHE-VISITS-ONCE", "11"), ("1-oldman", "1-oldman"), ("10", "10"),
            ("kill-tony-surrender", "12"), ("Kill-Tony-Pray", "12-oldman"), ("12-oldman", "12-oldman"),
            ("alarm-run", "13"), ("Alarm-Ambush", "14"), ("14", "14"),
        ):
            with self.subTest(ending=ending):
                result = self.run_launcher("film.sh", "--ending", ending, "--no-clean")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn(
                    f"--film=1 --ending={number} --from=act1",
                    self.trace.read_text().splitlines()[-1],
                )

    def test_film_rejects_give_up_from_act3(self):
        result = self.run_launcher("film.sh", "--ending", "give-up", "--from", "act3", "--no-clean")
        self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
        self.assertFalse(self.trace.exists() and "--film" in self.trace.read_text())

    def test_bash_film_help_lists_ending_titles(self):
        if self.shell != "bash":
            self.skipTest("Bash help")
        result = self.run_launcher("film.sh", "--help")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("1-steps   give-up", result.stdout)
        self.assertIn("1-caleb   eleanor-escapes", result.stdout)
        self.assertIn("11        she-visits-once", result.stdout)
        self.assertIn("12-oldman kill-tony-pray", result.stdout)
        self.assertIn("14        alarm-ambush", result.stdout)
        self.assertNotIn("source ", result.stdout)

    def test_bash_named_film_speeds(self):
        if self.shell != "bash":
            self.skipTest("Bash named speed syntax")
        for speed in ("1", "2", "4", "8", "16", "60", "hyper"):
            for args in (("--speed", speed), ("-s", speed), (f"--speed={speed}",)):
                with self.subTest(args=args):
                    result = self.run_launcher(
                        "film.sh", "--ending=8", *args, "--from", "ending", "--no-clean"
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    self.assertIn(
                        f"--film={speed} --ending=8 --from=ending",
                        self.trace.read_text().splitlines()[-1],
                    )
                    self.assertTrue(
                        (self.project / "logs" / f"film_{speed}x_from_ending.log").exists()
                    )

    def test_bash_invalid_film_arguments_have_no_side_effects(self):
        if self.shell != "bash":
            self.skipTest("Bash argument errors")
        sentinel = self.project / ".godot" / "keep"
        sentinel.parent.mkdir()
        sentinel.touch()
        for args in (
            ("4",), ("hyper",), ("--speed",), ("-s",), ("--speed=",),
            ("--speed", "3"), ("-s", "bad"), ("--speed", "--no-clean"),
            ("--ending",), ("--from",), ("--godot",),
            ("--ending", "all"), ("--ending", "the-end"), ("--from", "bad"),
            ("--from", "act3", "--ending", "1-steps"), ("--from", "act3", "--ending", "give-up"),
        ):
            with self.subTest(args=args):
                result = self.run_launcher("film.sh", *args)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertTrue(result.stderr)
                self.assertNotIn("unbound variable", result.stderr)
                self.assertFalse(self.trace.exists())
                self.assertTrue(sentinel.exists())

    def test_game_cleans_generated_files_but_preserves_player_data(self):
        data = Path(self.env["APPDATA"]) / "Godot" / "app_userdata" / "Repentance"
        generated = [
            self.project / folder / "stale"
            for folder in (
                ".godot", ".mono", "bin", "obj", "screenshots", "frames", "logs",
                "tests/example/bin", "tests/example/obj",
            )
        ] + [data / "autoplay_saves" / "stale", data / "autoplay_settings.cfg"]
        player = [data / "saves" / "slot1.json", data / "settings.cfg"]
        for path in generated + player:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("preserve me", encoding="utf-8")
        self.env["GAME_OUTPUT"] = "Normal game closed"
        result = self.run_launcher("game.sh", "--godot", str(self.engine))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for path in generated:
            self.assertFalse(path.exists(), str(path))
        for path in player:
            self.assertEqual(path.read_text(), "preserve me")
        self.assertEqual(
            (self.root / "events").read_text().splitlines(),
            ["probe", "build", "import", "game"],
        )
        self.assertIn("Normal game closed", (self.project / "logs" / "game.log").read_text())
        self.assertIn("Game closed.", result.stdout)

    def test_game_no_clean_still_builds_imports_and_runs_normally(self):
        sentinel = self.project / ".godot" / "keep"
        sentinel.parent.mkdir()
        sentinel.touch()
        self.env["GAME_OUTPUT"] = ""
        result = self.run_launcher("game.sh", "--no-clean", "--godot", str(self.engine))
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertTrue(sentinel.exists())
        self.assertEqual(
            (self.root / "events").read_text().splitlines(),
            ["probe", "build", "import", "game"],
        )
        self.assertEqual(self.trace.read_text().splitlines()[-1], "--path . --")
        self.assertEqual((self.project / "logs" / "game.log").read_text(), "")

    def test_game_supports_engine_path_with_spaces_and_another_working_directory(self):
        engine = self.rename_engine("editor with spaces")
        self.env["GODOT"] = "/missing/editor"
        result = self.run_launcher(
            "game.sh", "--no-clean", "--godot", str(engine), cwd=self.home
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn(f"Godot: {engine}", result.stdout)
        self.assertTrue((self.project / "logs" / "game.log").exists())

    def test_game_build_and_import_exit_failures_prevent_launch(self):
        for setting in ("BUILD_EXIT", "IMPORT_EXIT"):
            with self.subTest(setting=setting):
                self.trace.unlink(missing_ok=True)
                self.env["BUILD_EXIT"] = self.env["IMPORT_EXIT"] = "0"
                self.env[setting] = "3"
                result = self.run_launcher("game.sh", "--no-clean")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assert_no_game()
                if setting == "BUILD_EXIT":
                    self.assertNotIn("--import", self.trace.read_text())

    def test_game_reports_runtime_errors_as_warnings_but_fails_on_nonzero_exit(self):
        self.env["GAME_OUTPUT"] = ""
        self.env["GAME_ERROR"] = "ERROR: Audio device unavailable"
        for status in ("0", "3"):
            with self.subTest(status=status):
                self.env["GAME_EXIT"] = status
                result = self.run_launcher("game.sh", "--no-clean")
                self.assertEqual(result.returncode, 0 if status == "0" else 1)
                self.assertIn("Audio device unavailable", result.stdout + result.stderr)
                self.assertIn("Audio device unavailable", (self.project / "logs" / "game.log").read_text())
                if status != "0":
                    self.assertIn("Godot exited with status 3", result.stdout + result.stderr)

    def test_game_unknown_and_missing_arguments_do_not_clean(self):
        sentinel = self.project / ".godot" / "keep"
        sentinel.parent.mkdir()
        sentinel.touch()
        for args in (("--bad",), ("4",), ("--godot",)):
            with self.subTest(args=args):
                result = self.run_launcher("game.sh", *args)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stdout + result.stderr)
                self.assertFalse(self.trace.exists())
                self.assertTrue(sentinel.exists())

    def test_film_and_tests_still_require_markers(self):
        self.env["GAME_OUTPUT"] = ""
        for script, args in (("film.sh", ()), ("test.sh", ("pause",))):
            with self.subTest(script=script):
                result = self.run_launcher(script, *args, "--no-clean")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertIn("None of", result.stdout + result.stderr)

    def test_resume_suites_pass_separate_arguments_and_need_their_marker(self):
        for suite, resume in (("resume-act2", "act2"), ("resume-act3", "act3")):
            with self.subTest(suite=suite):
                self.env["GAME_OUTPUT"] = "PLAYTHROUGH OK"
                result = self.run_launcher("test.sh", suite, "--no-clean")
                self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
                self.env["GAME_OUTPUT"] = "RESUME OK"
                result = self.run_launcher("test.sh", suite, "--no-clean")
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                self.assertTrue(
                    self.trace.read_text().splitlines()[-1].endswith(f"-- --playthrough --resume={resume}")
                )
                self.assertTrue((self.project / "logs" / f"{suite}.log").exists())


@unittest.skipUnless(shutil.which("pwsh"), "PowerShell is required")
class PowerShellLauncherTests(LauncherTests):
    shell = "pwsh"


if __name__ == "__main__":
    unittest.main()
