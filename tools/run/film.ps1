<#
.SYNOPSIS
    Film mode: watch the game play itself to "The End", at 1x to 60x ("hyper") speed, from any chapter.
.DESCRIPTION
    Resets every generated file (imports, builds, logs, test saves) and rebuilds, then plays the canonical story.
    Your input is ignored, except Space (pause), F11 (full screen) and Esc (stop). Your own saves are never touched.
    -From starts at a chapter: the earlier story still plays, unseen and muted, at 60x behind a black screen.
.PARAMETER Ending
    The ending to play, by number or by title (case-insensitive); default 2. The numbers are the ones used in
    docs/story-overview.md ("Branches and endings") and by the playthrough routes; 1-oldman and 1-steps are other
    routes to ending 1, and 12-oldman to ending 12.

    Number    Title                    Ending
    1         walk-away                Micah lowers the gun on Tony; coffee with Rose
    1-oldman  spare-the-old-man        He prays the Our Father and spares the old man; coffee with Rose
    1-steps   give-up                  He gives up on the cathedral steps; coffee with Rose
    2         escape-together          Evidence or fire, Eleanor convinced; out of town with her
    3         escape-alone             Evidence or fire, Eleanor not convinced; out of town alone
    4         prison-eleanor-visits    Neither, Eleanor convinced; prison, Eleanor visits
    5         prison-caleb-visits      Neither, Eleanor not convinced; prison, Caleb visits
    6         turn-himself-in          He turns himself in; prison, Rose visits
    7         last-entry               He shoots Eleanor and/or himself; Caleb writes the last entry
    8         eleanor-burns-the-house  Eleanor strikes the old man and burns the cellar; Rose, then Eleanor alone
    9         eleanor-confesses        Eleanor strikes the old man; Rose, then she confesses to Caleb in prison
    10        she-leaves-by-the-car    Eleanor follows after the shot, evidence or fire; she leaves him by the car
    11        she-visits-once          Eleanor follows after the shot, nothing taken; prison, she visits once
    12        kill-tony-surrender      He kills Tony, confesses to Caleb and turns himself in; prison, Caleb visits
    12-oldman kill-tony-pray           He kills Tony, confesses, spares the old man, then gives himself up
.EXAMPLE
    tools\run\film.ps1                  # 1x, ending 2
    tools\run\film.ps1 -Speed 4 -Ending 5
    tools\run\film.ps1 -Speed 4 -Ending prison-caleb-visits   # the same as -Ending 5
    tools\run\film.ps1 -Speed 2 -Ending 1-oldman   # ending 1 variants: 1 (Tony), 1-oldman, 1-steps
    tools\run\film.ps1 -Speed hyper -From ending -Ending 8
#>
param(
    [ValidateSet('1', '2', '4', '8', '16', '60', 'hyper')][string]$Speed = '1',
    [ValidateSet('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '1-oldman', '1-steps', '12-oldman',
        'walk-away', 'spare-the-old-man', 'give-up', 'escape-together', 'escape-alone', 'prison-eleanor-visits',
        'prison-caleb-visits', 'turn-himself-in', 'last-entry', 'eleanor-burns-the-house', 'eleanor-confesses',
        'she-leaves-by-the-car', 'she-visits-once', 'kill-tony-surrender', 'kill-tony-pray')][string]$Ending = '2',
    [ValidateSet('act1', 'interlude1', 'act2', 'interlude2', 'act3', 'ending')][string]$From = 'act1',
    [switch]$NoClean,
    [string]$Godot
)
. (Join-Path $PSScriptRoot 'common.ps1')

# Ending titles to the numbers the game takes; keep in step with .PARAMETER Ending and film.sh.
$endingNumbers = @{
    'walk-away' = '1'; 'spare-the-old-man' = '1-oldman'; 'give-up' = '1-steps'
    'escape-together' = '2'; 'escape-alone' = '3'; 'prison-eleanor-visits' = '4'; 'prison-caleb-visits' = '5'
    'turn-himself-in' = '6'; 'last-entry' = '7'; 'eleanor-burns-the-house' = '8'; 'eleanor-confesses' = '9'
    'she-leaves-by-the-car' = '10'; 'she-visits-once' = '11'
    'kill-tony-surrender' = '12'; 'kill-tony-pray' = '12-oldman'
}
if ($endingNumbers.ContainsKey($Ending)) { $Ending = $endingNumbers[$Ending] }

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
