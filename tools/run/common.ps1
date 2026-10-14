# Shared helpers for film.ps1 and test.ps1. Dot-source it; don't run it directly.
# Works in Windows PowerShell 5.1 and PowerShell 7.

$ErrorActionPreference = 'Stop'
$Root = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$LogDir = Join-Path $Root 'logs'

# The same rule as CI: Game.Run catches script exceptions with GD.PushError, so a run can print its marker after one.
$ErrorPattern = '^(ERROR|SCRIPT ERROR|USER ERROR):|Unhandled exception'

function Find-Godot([string]$Explicit) {
    if ($Explicit) { return (Resolve-Path $Explicit).Path }
    if ($env:GODOT) { return $env:GODOT }
    foreach ($name in 'godot_console', 'godot4', 'godot') {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($cmd) { return $cmd.Source }
    }
    $installs = @()
    foreach ($dir in "$env:LOCALAPPDATA\Godot", "$env:ProgramFiles\Godot", "$HOME\Godot") {
        if ($dir -and (Test-Path $dir)) {
            $installs += Get-ChildItem $dir -Recurse -Filter 'Godot_v*_mono_*console.exe' -ErrorAction SilentlyContinue
        }
    }
    $best = $installs | Sort-Object Name -Descending | Select-Object -First 1
    if ($best) { return $best.FullName }
    throw "Godot 4 .NET not found. Pass -Godot <path to the console exe>, or set `$env:GODOT."
}

function Get-UserDataDir {
    if ($env:APPDATA) { return Join-Path $env:APPDATA 'Godot\app_userdata\Repentance' }
    if ($IsMacOS) { return Join-Path $HOME 'Library/Application Support/Godot/app_userdata/Repentance' }
    $base = if ($env:XDG_DATA_HOME) { $env:XDG_DATA_HOME } else { Join-Path $HOME '.local/share' }
    return Join-Path $base 'godot/app_userdata/Repentance'
}

# Deletes everything generated (imports, builds, screenshots, frames, logs, the test-only saves and settings).
# Player saves (user://saves) and settings (user://settings.cfg) are never touched.
function Reset-Generated {
    Write-Host '== Clean reset' -ForegroundColor Cyan
    $targets = @('.godot', '.mono', 'bin', 'obj', 'screenshots', 'frames', 'logs') | ForEach-Object { Join-Path $Root $_ }
    $targets += Get-ChildItem (Join-Path $Root 'tests') -Directory -Recurse -Include 'bin', 'obj' -ErrorAction SilentlyContinue |
        ForEach-Object FullName
    $userData = Get-UserDataDir
    $targets += (Join-Path $userData 'autoplay_saves'), (Join-Path $userData 'autoplay_settings.cfg')
    foreach ($t in $targets) {
        if (Test-Path $t) {
            Remove-Item $t -Recurse -Force
            Write-Host "  removed $t"
        }
    }
}

function Invoke-Checked([string]$What, [scriptblock]$Block) {
    Write-Host "== $What" -ForegroundColor Cyan
    & $Block
    if ($LASTEXITCODE -ne 0) { throw "$What failed (exit code $LASTEXITCODE)." }
}

# The Ink importer is C#, so the build must come before the import.
function Build-And-Import([string]$Godot) {
    Push-Location $Root
    try {
        Invoke-Checked 'dotnet build' { dotnet build Repentance.csproj --nologo -v quiet }
        Invoke-Checked 'Godot import' { & $Godot --headless --path . --import 2>&1 | ForEach-Object { "$_" } | Out-Host }
    }
    finally { Pop-Location }
}

# Runs the game with the given user args, tees the output to logs/<Name>.log, and returns $true when the run exited
# cleanly, printed one of the markers and logged no errors.
function Invoke-GodotRun {
    param(
        [string]$Godot, [string]$Name, [string[]]$UserArgs, [string[]]$Markers,
        [string[]]$EngineArgs = @()
    )
    New-Item -ItemType Directory -Force $LogDir | Out-Null
    $log = Join-Path $LogDir "$Name.log"
    Write-Host "== $Name ($($UserArgs -join ' '))" -ForegroundColor Cyan
    Push-Location $Root
    try {
        $all = @('--path', '.') + $EngineArgs + @('--') + $UserArgs
        & $Godot @all 2>&1 | ForEach-Object { "$_" } | Tee-Object -FilePath $log | Out-Host
        $code = $LASTEXITCODE
    }
    finally { Pop-Location }
    $text = @(Get-Content $log)
    $ok = $true
    if ($code -ne 0) { Write-Host "Godot exited with status $code" -ForegroundColor Red; $ok = $false }
    $found = @($Markers | Where-Object { $m = $_; @($text | Where-Object { $_.Contains($m) }).Count -gt 0 })
    if ($found.Count -eq 0) { Write-Host "None of '$($Markers -join "', '")' found in $log" -ForegroundColor Red; $ok = $false }
    $errors = $text | Select-String -CaseSensitive -Pattern $ErrorPattern
    if ($errors) {
        Write-Host 'Godot logged errors:' -ForegroundColor Red
        $errors | ForEach-Object { Write-Host "  $log`:$($_.LineNumber): $($_.Line)" -ForegroundColor Red }
        $ok = $false
    }
    return $ok
}

function Find-Python {
    # Run each candidate: python/python3 can be Microsoft Store stubs that only print an install hint.
    $candidates = @()
    if ($env:PYTHON) { $candidates += , @($env:PYTHON) }
    $candidates += @(@('py', '-3'), @('python'), @('python3'))
    if ($env:LOCALAPPDATA) {
        Get-ChildItem "$env:LOCALAPPDATA\Programs\Python\Python3*\python.exe" -ErrorAction SilentlyContinue |
            Sort-Object { [int]($_.Directory.Name -replace '\D', '') } -Descending | ForEach-Object { $candidates += , @($_.FullName) }
    }
    foreach ($c in $candidates) {
        if (-not (Get-Command $c[0] -ErrorAction SilentlyContinue)) { continue }
        $rest = @($c | Select-Object -Skip 1)
        & $c[0] @rest -c 'import sys; sys.exit(sys.version_info[0] != 3)' *> $null
        if ($LASTEXITCODE -eq 0) { return , $c }
    }
    throw 'Python 3 not found (needed for the art tests, with pillow and numpy). Set $env:PYTHON to its path.'
}
