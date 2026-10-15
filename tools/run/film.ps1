<#
.SYNOPSIS
    Film mode: watch the whole game play itself, title to "The End", at 1x, 2x or 4x speed.
.DESCRIPTION
    Resets every generated file (imports, builds, logs, test saves) and rebuilds, then plays the canonical story.
    Your input is ignored, except Space (pause), F11 (full screen) and Esc (stop). Your own saves are never touched.
.EXAMPLE
    tools\run\film.ps1                  # 1x, ending 2
    tools\run\film.ps1 -Speed 4 -Ending 5
    tools\run\film.ps1 -Speed 2 -Ending 1-oldman   # ending 1 variants: 1 (Tony), 1-oldman, 1-steps
#>
param(
    [ValidateSet(1, 2, 4)][int]$Speed = 1,
    [ValidateSet('1', '2', '3', '4', '5', '6', '7', '1-oldman', '1-steps')][string]$Ending = '2',
    [switch]$NoClean,
    [string]$Godot
)
. (Join-Path $PSScriptRoot 'common.ps1')

$godotExe = Find-Godot $Godot
Write-Host "Godot: $godotExe"
if (-not $NoClean) { Reset-Generated }
Build-And-Import $godotExe
$ok = Invoke-GodotRun -Godot $godotExe -Name "film_${Speed}x" -UserArgs @("--film=$Speed", "--ending=$Ending") `
    -Markers @('FILM OK', 'FILM STOPPED') -ErrorsAreWarnings
if ($ok) { Write-Host 'Film finished.' -ForegroundColor Green; exit 0 }
Write-Host 'Film failed; see the log above.' -ForegroundColor Red
exit 1
