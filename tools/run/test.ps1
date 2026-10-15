<#
.SYNOPSIS
    Runs the test suites from a clean slate and prints a summary. Exits non-zero if any suite fails.
.DESCRIPTION
    Suites: unit (xunit, including the story-integrity and exhaustive Ink-walk tests), art (Python),
    autoplay, settings, pause, walk, playthrough (Godot runs). 'all' runs every one.
    Unless -NoClean is given, every generated file is deleted first and the project is rebuilt and reimported.
    Godot logs go to logs/<suite>.log; a Godot suite passes only with its marker and no ERROR lines (as in CI).
.EXAMPLE
    tools\run\test.ps1                          # everything
    tools\run\test.ps1 -Suite unit, playthrough -NoClean
#>
param(
    [ValidateSet('all', 'unit', 'art', 'autoplay', 'settings', 'pause', 'walk', 'playthrough')]
    [string[]]$Suite = @('all'),
    [switch]$NoClean,
    [string]$Godot
)
. (Join-Path $PSScriptRoot 'common.ps1')

$godotSuites = [ordered]@{
    autoplay    = @{ Args = @('--autoplay'); Marker = 'AUTOPLAY OK' }
    settings    = @{ Args = @('--settings-test'); Marker = 'SETTINGS TEST OK' }
    pause       = @{ Args = @('--pause-test'); Marker = 'PAUSE TEST OK' }
    walk        = @{ Args = @('--walk-test'); Marker = 'WALK TEST OK' }
    playthrough = @{ Args = @('--playthrough'); Marker = 'PLAYTHROUGH OK' }
}
$order = @('unit', 'art') + @($godotSuites.Keys)
$selected = if ($Suite -contains 'all') { $order } else { $order | Where-Object { $Suite -contains $_ } }
$needsGodot = @($selected | Where-Object { $godotSuites.Contains($_) }).Count -gt 0

if ($needsGodot) {
    $godotExe = Find-Godot $Godot
    Write-Host "Godot: $godotExe"
}
if (-not $NoClean) { Reset-Generated }
if ($needsGodot) {
    Build-And-Import $godotExe
}

$results = [ordered]@{}
foreach ($s in $selected) {
    $start = Get-Date
    Push-Location $Root
    try {
        switch ($s) {
            'unit' {
                Write-Host '== unit' -ForegroundColor Cyan
                dotnet test tests/Repentance.Tests/Repentance.Tests.csproj --nologo
                $ok = $LASTEXITCODE -eq 0
            }
            'art' {
                Write-Host '== art' -ForegroundColor Cyan
                $py = Find-Python
                $pyArgs = @($py | Select-Object -Skip 1)
                & $py[0] @pyArgs -m unittest discover -s tests/art -v
                $ok = $LASTEXITCODE -eq 0
                & $py[0] @pyArgs -m unittest discover -s tests -p test_character_art.py -v
                $ok = $ok -and $LASTEXITCODE -eq 0
            }
            default {
                $g = $godotSuites[$s]
                # Not --headless: AutoPlay captures viewport screenshots, which need a real renderer.
                $ok = Invoke-GodotRun -Godot $godotExe -Name $s -UserArgs $g.Args -Markers @($g.Marker) `
                    -EngineArgs @('--audio-driver', 'Dummy')
            }
        }
    }
    catch { Write-Host $_ -ForegroundColor Red; $ok = $false }
    finally { Pop-Location }
    $results[$s] = @{ Ok = $ok; Seconds = [int]((Get-Date) - $start).TotalSeconds }
}

Write-Host "`n== Summary" -ForegroundColor Cyan
$failed = 0
foreach ($s in $results.Keys) {
    $r = $results[$s]
    $state = if ($r.Ok) { 'PASS' } else { 'FAIL' }
    if (-not $r.Ok) { $failed++ }
    Write-Host ('  {0,-12} {1}  {2,5}s' -f $s, $state, $r.Seconds) -ForegroundColor $(if ($r.Ok) { 'Green' } else { 'Red' })
}
if ($failed) { Write-Host "$failed suite(s) failed. Godot logs: logs\" -ForegroundColor Red; exit 1 }
Write-Host 'All suites passed.' -ForegroundColor Green
exit 0
