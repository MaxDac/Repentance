<#
.SYNOPSIS
    Film mode: watch the game play itself to "The End", at 1x to 60x ("hyper") speed, from any chapter.
.DESCRIPTION
    Resets every generated file (imports, builds, logs, test saves) and rebuilds, then plays the canonical story.
    Your input is ignored, except Space (pause), F11 (full screen) and Esc (stop). Your own saves are never touched.
    -From starts at a chapter: the earlier story still plays, unseen and muted, at 60x behind a black screen.
.EXAMPLE
    tools\run\film.ps1                  # 1x, ending 2
    tools\run\film.ps1 -Speed 4 -Ending 5
    tools\run\film.ps1 -Speed 2 -Ending 1-oldman   # ending 1 variants: 1 (Tony), 1-oldman, 1-steps
    tools\run\film.ps1 -Speed hyper -From ending -Ending 8
#>
param(
    [ValidateSet('1', '2', '4', '8', '16', '60', 'hyper')][string]$Speed = '1',
    [ValidateSet('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '1-oldman', '1-steps')][string]$Ending = '2',
    [ValidateSet('act1', 'interlude1', 'act2', 'interlude2', 'act3', 'ending')][string]$From = 'act1',
    [switch]$NoClean,
    [string]$Godot
)
. (Join-Path $PSScriptRoot 'common.ps1')

if ($From -eq 'act3' -and $Ending -eq '1-steps') {
    Write-Host 'Ending 1-steps ends in the Second Interlude, before Act 3; pick another -From.' -ForegroundColor Red
    exit 2
}
$godotExe = Find-Godot $Godot
Write-Host "Godot: $godotExe"
if (-not $NoClean) { Reset-Generated }
Build-And-Import $godotExe
$name = "film_${Speed}x" + $(if ($From -ne 'act1') { "_from_$From" } else { '' })
$ok = Invoke-GodotRun -Godot $godotExe -Name $name -UserArgs @("--film=$Speed", "--ending=$Ending", "--from=$From") `
    -Markers @('FILM OK', 'FILM STOPPED') -ErrorsAreWarnings
if ($ok) { Write-Host 'Film finished.' -ForegroundColor Green; exit 0 }
Write-Host 'Film failed; see the log above.' -ForegroundColor Red
exit 1
