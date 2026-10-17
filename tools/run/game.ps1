<#
.SYNOPSIS
    Play the game normally after cleaning generated files, building and importing.
.DESCRIPTION
    Player saves and settings are never touched. Quit the game normally to finish.
    Runtime errors are reported as warnings; build/import errors and nonzero exits fail.
.EXAMPLE
    tools\run\game.ps1
    tools\run\game.ps1 -NoClean
#>
[CmdletBinding(PositionalBinding = $false)]
param(
    [switch]$NoClean,
    [string]$Godot
)
. (Join-Path $PSScriptRoot 'common.ps1')

$godotExe = Find-Godot $Godot
Write-Host "Godot: $godotExe"
if (-not $NoClean) { Reset-Generated }
Build-And-Import $godotExe
$ok = Invoke-GodotRun -Godot $godotExe -Name game -SkipMarkerCheck -ErrorsAreWarnings
if ($ok) { Write-Host 'Game closed.' -ForegroundColor Green; exit 0 }
Write-Host 'Game failed; see the log above.' -ForegroundColor Red
exit 1
