<#
.SYNOPSIS
    Film mode: watch the game play itself to "The End", at 1x to 60x ("hyper") speed, from any chapter.
.DESCRIPTION
    Resets every generated file (imports, builds, logs, test saves) and rebuilds, then plays the canonical story.
    Your input is ignored, except Space (pause), F11 (full screen) and Esc (stop). Your own saves are never touched.
    -From starts at a chapter: the earlier story still plays, unseen and muted, at 60x behind a black screen.
.PARAMETER Ending
    The ending to play, by number or by title (case-insensitive); default 2. The numbers are the ones used in
    docs/story-overview.md ("Branches and endings") and by the playthrough routes; a suffixed number (1-oldman,
    15-steps-caleb, 8-kill...) is another route to the same ending, each a different final scene.

    Number         Title                           Ending
    1              walk-away                       Micah lowers the gun on Tony; coffee with Rose
    1-oldman       spare-the-old-man               He prays the Our Father and spares the old man; coffee with Rose
    1-steps        give-up                         He gives up on the cathedral steps; coffee with Rose
    1-steps-caleb  give-up-eleanor-escapes         As 1-steps, and Eleanor held out; Rose, then Eleanor and Caleb
    1-caleb        eleanor-escapes                 Eleanor held out, he lowers the gun on Tony; Rose, then Eleanor and Caleb
    1-bed          eleanor-back-to-bed             Eleanor held out, he prays; she goes back to bed, he goes to Rose
    2              escape-together                 Evidence or fire, Eleanor convinced; out of town with her
    3              escape-alone                    Evidence or fire, Eleanor not convinced; out of town alone
    4              prison-eleanor-visits           Neither, Eleanor convinced; prison, Eleanor visits
    5              prison-caleb-visits             Neither, Eleanor not convinced; prison, Caleb visits
    6              turn-himself-in                 He turns himself in; prison, Rose visits
    7              last-entry                      He shoots Eleanor, then himself; Caleb writes the last entry
    7-alone        last-entry-alone                Four turns without her, the footsteps; he shoots himself alone
    8              eleanor-burns-the-house         Eleanor strikes the old man and burns the cellar; Rose, then Eleanor alone
    8-kill         kill-tony-eleanor-burns         As 12-oldman, Eleanor held out; she strikes him and burns the cellar
    9              eleanor-confesses               Eleanor strikes the old man; Rose, then she confesses to Caleb in prison
    9-kill         kill-tony-eleanor-confesses     As 12-oldman, Eleanor held out; she strikes him and confesses to Caleb
    10             she-leaves-by-the-car           Eleanor follows after the shot, evidence or fire; she leaves him by the car
    11             she-visits-once                 Eleanor follows after the shot, nothing taken; prison, she visits once
    12             kill-tony-surrender             He kills Tony, confesses to Caleb and turns himself in; prison, Caleb visits
    12-oldman      kill-tony-pray                  He kills Tony, confesses, spares the old man, then gives himself up
    12-bed         kill-tony-eleanor-back-to-bed   As 12-oldman, Eleanor held out; she goes back to bed, he to the station
    13             alarm-run                       A warning shot; the unseen alarm rings and he runs; out of Chicago, alone
    13-caleb       alarm-run-eleanor-escapes       As 13, and Eleanor held out; then Eleanor and Caleb at the city's edge
    14             alarm-ambush                    A warning shot; the unseen alarm rings and he goes in; shot in the kitchen
    14-caleb       alarm-ambush-eleanor-escapes    As 14, and Eleanor held out; then Eleanor and Caleb at the city's edge
    15             sunday-visits                   He walks away from Tony without having pressed Rose; she refuses the coffee
    15-caleb       sundays-eleanor-escapes         As 15, and Eleanor held out; Rose's door, then Eleanor and Caleb
    15-steps       sundays-give-up                 As 1-steps without having pressed Rose; she refuses the coffee
    15-steps-caleb sundays-give-up-eleanor-escapes As 15-steps, and Eleanor held out; Rose's door, then Eleanor and Caleb
    15-oldman      sundays-spare-the-old-man       As 1-oldman without having pressed Rose; she refuses the coffee
    15-bed         sundays-eleanor-back-to-bed     As 1-bed without having pressed Rose; she refuses the coffee
.EXAMPLE
    tools\run\film.ps1                  # 1x, ending 2
    tools\run\film.ps1 -Speed 4 -Ending 5
    tools\run\film.ps1 -Speed 4 -Ending prison-caleb-visits   # the same as -Ending 5
    tools\run\film.ps1 -Speed 2 -Ending 1-oldman   # ending 1 variants: 1 (Tony), 1-oldman, 1-steps, 1-steps-caleb, 1-caleb, 1-bed
    tools\run\film.ps1 -Speed hyper -From ending -Ending 8
#>
param(
    [ValidateSet('1', '2', '4', '8', '16', '60', 'hyper')][string]$Speed = '1',
    [ValidateSet('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15', '1-oldman',
        '1-steps', '1-steps-caleb', '1-caleb', '1-bed', '7-alone', '8-kill', '9-kill', '12-oldman', '12-bed',
        '13-caleb', '14-caleb', '15-caleb', '15-steps', '15-steps-caleb', '15-oldman', '15-bed',
        'walk-away', 'spare-the-old-man', 'give-up', 'give-up-eleanor-escapes', 'eleanor-escapes',
        'eleanor-back-to-bed', 'escape-together', 'escape-alone', 'prison-eleanor-visits', 'prison-caleb-visits',
        'turn-himself-in', 'last-entry', 'last-entry-alone', 'eleanor-burns-the-house', 'kill-tony-eleanor-burns',
        'eleanor-confesses', 'kill-tony-eleanor-confesses', 'she-leaves-by-the-car', 'she-visits-once',
        'kill-tony-surrender', 'kill-tony-pray', 'kill-tony-eleanor-back-to-bed', 'alarm-run',
        'alarm-run-eleanor-escapes', 'alarm-ambush', 'alarm-ambush-eleanor-escapes', 'sunday-visits',
        'sundays-eleanor-escapes', 'sundays-give-up', 'sundays-give-up-eleanor-escapes', 'sundays-spare-the-old-man',
        'sundays-eleanor-back-to-bed')][string]$Ending = '2',
    [ValidateSet('act1', 'interlude1', 'act2', 'interlude2', 'act3', 'ending')][string]$From = 'act1',
    [switch]$NoClean,
    [string]$Godot
)
. (Join-Path $PSScriptRoot 'common.ps1')

# Ending titles to the numbers the game takes; keep in step with .PARAMETER Ending and film.sh.
$endingNumbers = @{
    'walk-away' = '1'; 'spare-the-old-man' = '1-oldman'; 'give-up' = '1-steps'
    'give-up-eleanor-escapes' = '1-steps-caleb'; 'eleanor-escapes' = '1-caleb'; 'eleanor-back-to-bed' = '1-bed'
    'escape-together' = '2'; 'escape-alone' = '3'; 'prison-eleanor-visits' = '4'; 'prison-caleb-visits' = '5'
    'turn-himself-in' = '6'; 'last-entry' = '7'; 'last-entry-alone' = '7-alone'; 'eleanor-burns-the-house' = '8'
    'kill-tony-eleanor-burns' = '8-kill'; 'eleanor-confesses' = '9'; 'kill-tony-eleanor-confesses' = '9-kill'
    'she-leaves-by-the-car' = '10'; 'she-visits-once' = '11'; 'kill-tony-surrender' = '12'
    'kill-tony-pray' = '12-oldman'; 'kill-tony-eleanor-back-to-bed' = '12-bed'; 'alarm-run' = '13'
    'alarm-run-eleanor-escapes' = '13-caleb'; 'alarm-ambush' = '14'; 'alarm-ambush-eleanor-escapes' = '14-caleb'
    'sunday-visits' = '15'; 'sundays-eleanor-escapes' = '15-caleb'; 'sundays-give-up' = '15-steps'
    'sundays-give-up-eleanor-escapes' = '15-steps-caleb'; 'sundays-spare-the-old-man' = '15-oldman'
    'sundays-eleanor-back-to-bed' = '15-bed'
}
if ($endingNumbers.ContainsKey($Ending)) { $Ending = $endingNumbers[$Ending] }

if ($From -eq 'act3' -and $Ending -like '*-steps*') {
    Write-Host "Ending $Ending ends in the Second Interlude, before Act 3; pick another -From." -ForegroundColor Red
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
