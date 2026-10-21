<#
.SYNOPSIS
    Runs the launcher regression tests (tests/test_run_scripts.py) on Windows, Linux or macOS.
.DESCRIPTION
    The tests run game, film and test launchers in throwaway projects against fake Godot and dotnet executables,
    through both PowerShell (pwsh) and Bash (Git Bash on Windows, never the WSL stub). They need Python 3; the shell a
    machine lacks is skipped. No Godot, build or cleanup is involved. Extra arguments go to unittest, e.g. -k film.
    tools\run\test.ps1 -Suite launcher runs the same tests as part of the suite summary.
.EXAMPLE
    tools\run\harness.ps1
    tools\run\harness.ps1 -k film
#>
. (Join-Path $PSScriptRoot 'common.ps1')

$py = Find-Python
$pyArgs = @($py | Select-Object -Skip 1)
Push-Location $Root
try {
    & $py[0] @pyArgs -m unittest discover -s tests -p test_run_scripts.py -v @args
    exit $LASTEXITCODE
}
finally { Pop-Location }
