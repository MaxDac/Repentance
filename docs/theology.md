# Theology

Repentance is a story about sin, turning back and grace. This page checks the game's theologically loaded lines
against the two traditions its characters live in, marks where Catholic and Protestant teaching differ, and reads
the fourteen endings in that light. It is a writer's reference, not a verdict on anybody's soul: the endings show
what people did, and none of them claims to know how God judged them.

Spoilers throughout. Story spec: [Walkthrough](../Walkthrough.md); recap: [Story overview](story-overview.md);
writing rules: [Story and dialogue](story-and-dialogue.md#voice-and-scripture).

## Sources

The game is set in Chicago in 1927, so the Catholic side is read as a priest of 1927 learned it, and the modern
Catechism (1992) is noted only where it differs.

| Tradition | Sources |
|---|---|
| Catholic, 1927 | Council of Trent (Sessions V, VI, XIII, XIV, XXII, XXIV, XXV); the 1917 Code of Canon Law (CIC); the *Rituale Romanum*; the Baltimore Catechism No. 2; Aquinas, *Summa Theologiae* (ST) |
| Lutheran | Augsburg Confession (AC, 1530) and its Apology (Ap); Formula of Concord (FC); Luther's practice of private confession |
| Reformed | Westminster Confession of Faith (WCF, 1646) and Larger Catechism (WLC); Heidelberg Catechism (HC, 1563) |
| Catholic, modern | Catechism of the Catholic Church (CCC, 1992), only for contrast |

## The characters

- **Caleb Jones** is a Catholic priest of 1927: he hears confessions, says Mass, absolves in Latin and keeps the seal.
  His one grave fault is a prudential silence: he hides the girls who run from the Club, and in exchange keeps quiet
  about the Club. He confesses that silence every week, and means to break it "the day it won't bury the girls we
  hid": a purpose of amendment bound to a prudential judgment. Whether the silence is still licit material cooperation
  is a question of proportion, not something the game settles. Ending 1 ends it if Micah took the papers (Caleb carries them to the Tribune); in ending 9, Eleanor does it for him.
- **Micah Jones** is a Catholic, born and raised, who practises irregularly. His *theology* leans Protestant: grace over
  works, sin as a power that lives in a man (Romans 7), doubt that he needs a priest between him and God. When he
  does turn to God he does it as a Catholic: "Bless me, Father", Mass, holding back from Communion when he isn't in a
  state of grace. The finished Our Father in the bedroom ends with the doxology "For Thine is the Kingdom, the Power
  and the Glory" (`MansionBedroom.Doxology`). The 1927 Roman Mass and Catholic private prayer ended at "deliver us
  from evil"; the doxology was the Protestant use (Book of Common Prayer; Matthew 6:13 in the KJV). It stays, as the
  clearest mark of Micah's Protestant leaning.
- **Mother Superior Agatha** ("Sister Agatha, to the Lord") is a nun, so she can hear nothing sacramentally and absolve
  nobody; Eleanor says so ("The priest hears confessions on Saturdays"). Her failures are hers, not the Church's
  teaching: harsh condemnation, and a temptation she turns on the girl. A superior was normally addressed "Mother
  Agatha"; her own humility explains the "Sister".
- **Eleanor Harrington** is a coerced woman, drugged and kept by the Club. The game is careful that coerced sin and
  free sin differ: what she suffers is done to her. What she chooses (to hold out, to strike, to burn, to confess)
  is hers.
- **Rose** stays cautious throughout: forgiveness is not restored trust, and neither tradition says it must be.

## Topic by topic

Each row: what 1927 Catholic teaching says, what the Lutheran and Reformed confessions say, where they differ, the
lines in the game, and the verdict.

### Grace and justification

- **Catholic:** justification is a free gift; nothing before it, faith or works, merits it (Trent VI ch. 8). Grace is
  infused, and the justified cooperate with it and grow in it (VI ch. 7, 10, 16). "Faith alone" in the sense of mere
  trust is rejected (VI can. 9, 12).
- **Lutheran / Reformed:** justified by grace through faith alone, righteousness imputed (AC IV; WCF XI; HC 60).
  Good works are the fruit, never the cause (AC XX; WCF XVI).
- **Differ on:** how grace works (infused and cooperated with, versus imputed and received), and whether works done
  in grace merit. **Agree:** nobody earns the beginning of salvation.
- **Lines:** Caleb, `caleb_act2`: "Turn back to God and believe, Micah. Salvation isn't wages for being good; it's
  grace." (Mark 1:15; Ephesians 2:8-9.)
- **Verdict:** sound for both. A Catholic priest can say it word for word, and it is the line Micah's Protestant
  leaning hears best.

### Repentance and forgiveness

- **Catholic:** contrition, confession and satisfaction (Trent XIV ch. 3-4, 8). Perfect contrition (sorrow from love
  of God) forgives at once, but includes the intention to confess; attrition (sorrow from fear) is enough only with
  the sacrament (XIV ch. 4).
- **Lutheran:** repentance is contrition and faith; private absolution is kept and prized, but listing every sin is
  not required (AC XI, XII, XXV; Ap XII). **Reformed:** "repentance unto life" toward God, with confession to God,
  and to the wronged person where the sin wronged him (WCF XV.4-6).
- **Differ on:** whether a priest's absolution is needed for grave sin after baptism; whether satisfaction is part of
  repentance.
- **Lines:** Caleb, `caleb_club`: "If a man truly repents, the Lord forgives him. Every time." and "Repentance isn't
  for saints at the end of their lives..."; `caleb_last`: "God doesn't turn away a contrite heart" (Psalm 51:17);
  the prodigal (Luke 15).
- **Verdict:** sound for both. For Caleb, "truly repents" carries the Catholic sense (contrition, which reaches for the
  sacrament); Micah can hear it the Protestant way.

### Despair and presumption

- **Catholic:** despair is a sin against hope (ST II-II q. 20); its main root is *acedia*, spiritual sloth (q. 20 a.
  4). Presumption, counting on mercy without turning, is the opposite sin, and that one springs from pride (q. 21 a.
  4). Both traditions keep despair as a theological matter apart from melancholy and grief.
- **Protestant:** despair of God's mercy is unbelief; the remedy is the promise, not one's own state (AC XII; HC 1).
- **Differ on:** little. **Lines:** Caleb, `caleb_club`: "You think your sins are too big for God to forgive? That's
  not humility, brother. That's pride." and "Despair is just another way of putting yourself first."
- **Verdict:** sound as a pastoral judgment on *Micah*: Caleb ties it to Micah's lifelong arrogance ("Always the one
  who had to carry everything"). It shouldn't be cited as Aquinas's general doctrine, and the game doesn't.

### Sin as a power, and free will

- **Catholic:** concupiscence remains after baptism, inclines to sin, but is not sin in the strict sense unless
  consented to (Trent V can. 5); free will was weakened, not extinguished (VI can. 5).
- **Lutheran:** without grace the will cannot turn to God (FC II), but keeps a freedom in civil matters (AC XVIII).
  **Reformed:** the will is in bondage to sin, yet never forced (WCF IX.1, IX.3).
- **Differ on:** how free the fallen will is, and whether concupiscence is itself sin (Lutheran and Reformed: yes).
  **Agree:** a man consents to his adultery and his killings; nothing excuses him.
- **Lines:** OfficeStorm: "Sin is a beast. It doesn't wait outside the door. / It climbs inside a man and wears him"
  (Genesis 4:7; Romans 7:17-20). Micah, the fire escape: "Some things a man doesn't decide. They decide him."
- **Verdict:** the beast is Romans 7 told the Protestant way, and in character for Micah; a Catholic would add that
  the beast walks him nowhere he didn't consent to go. The fire-escape line is a lover's noir excuse, not doctrine:
  read as an excuse, it is unsound in all three traditions, and the story treats it as one.

### The seal of confession

- **Catholic:** the seal is inviolable; the confessor may betray the penitent "by no word or sign or any other way,
  for no cause" (1917 CIC c. 889 §1), may not use the knowledge to the penitent's burden (c. 890), and a direct
  breach meant excommunication reserved to the Holy See (c. 2369). Manualists commonly let a confessor speak with the
  penitent's free and express leave, though prudence advised against it, and some held the seal itself remained.
  Modern: CCC 1467.
- **Lutheran:** confidentiality of private confession was kept in Luther's practice and the church orders (AC XXV is
  about absolution and not enumerating sins, not the seal). **Reformed:** no sacramental seal; pastoral confidence.
- **Differ on:** whether the seal is absolute sacramental law.
- **Lines (before the fix):** endings 1, 12, 13 and 14 had Eleanor's story come from Caleb's confessional "without
  breaking the seal"; ending 9 from "her own confession, at her asking"; ending 7 published Micah's confession of Tony.
- **Verdict (fixed):** the seal follows the sacrament, not the room: where a confession was heard is no ground for
  repeating it. So Caleb's accounts rest only on what Eleanor said in open court, or told him again, plainly and
  apart from any confession, with the express request that he write it down (ending 9: "what she told the court, and
  what she told me again plainly afterwards"; endings 1, 12, 13, 14: she came and told him). Ending 7 gives only what
  the police found ("What else I know of it, I may not write."). Ending 14 no longer says "I hear her confession,
  and I can do nothing else", which would betray by sign that her confession binds him; it says he sees her at Mass,
  or, after her escape (`caleb_escape`), that he put her on a truck out of Chicago and she told him at the city's edge.

### Absolution needs sorrow (Eleanor, ending 9)

- **Catholic:** absolution is valid only with at least attrition, and sorrow must be universal: sorrow for every
  mortal sin, a purpose of amendment (Trent XIV ch. 4; Baltimore Catechism No. 2, on Contrition). The priest raises
  his right hand over the penitent (*Rituale Romanum*, Ordo ministrandi sacramentum poenitentiae).
- **Lutheran:** the same need for real repentance (AC XII). Private absolution is kept, and it is God's own
  forgiving word that truly remits sins (AC XI; Apology XII.39-41), but without the Catholic judicial sentence,
  enumeration of all sins or satisfaction.
- **Reformed:** the same need for real repentance (WCF XV.2), but no sacramental priestly absolution; the minister
  declares the promise to the penitent (Heidelberg Q. 84).
- **Lines (before the fix):** "Every one but the last. God help me, Father, I can't be sorry for the last one." /
  "Then be sorry that it came to it." Caleb absolved a penitent who refused sorrow for a killing: invalid.
- **Verdict (fixed):** Eleanor is afraid of him and wanted him dead, and can't tell which held the candlestick. Caleb:
  "Then don't sort it. Be sorry for every part of you that wanted him dead, and leave the sorting to God." She is, "for all of it",
  and "won't call that part good"; then the absolution. She needn't regret escaping; she must regret what was vengeance.
  The thought now says a hand was *raised over* her, as the rite does, not that it touched her.

### Self-denunciation and penance (`caleb_tony`)

- **Catholic:** the confessor judges contrition and the purpose of amendment, and imposes a salutary penance (1917 CIC
  c. 887). He may urge a penitent to give himself up, and must require restitution of harm, but may not impose
  public self-denunciation for a hidden sin as the sacramental penance or make absolution depend on it (*nemo
  tenetur se detegere*), unless another is wrongly accused.
- **Protestant:** the magistrate's sword is God's (Romans 13; AC XVI; WCF XXIII); accepting civil punishment is fruit
  of repentance, not payment for forgiveness.
- **Differ on:** penance as part of the sacrament. **Agree:** forgiveness doesn't cancel the debt to Tony's mother or
  to the law.
- **Lines (before the fix):** Caleb never said the absolution, and the knot's comment called the walk to the police
  "the only penance a priest can't give himself".
- **Verdict (fixed):** Caleb asks "Are you sorry for it? Not scared, Micah. Sorry." and for "no more blood"; requires
  that he do what he can for Tony's mother all his life (restitution); gives the penance (prayer for Tony and his mother); absolves him; then, "as your brother", asks him to walk to the station.
  The choice and flags are unchanged. In endings 10 and 11, Micah's "it starts at a police station" and "Some things
  you can't say the Our Father over until you've said them out loud" are his own conscience, not Church law (Trent
  XIII ch. 7 asks for confession before Communion, not surrender).

### Prayer for the dead and purgatory

- **Catholic:** purgatory, and the souls there helped by prayer and above all by the Mass (Trent XXII ch. 2; XXV,
  Decree on Purgatory).
- **Lutheran:** no purgatory, and no Mass applied for the dead, but prayer for the dead is not forbidden (Ap XXIV.94:
  "which we do not prohibit"). **Reformed:** forbidden (WCF XXI.4).
- **Differ on:** all three disagree.
- **Lines (fixed):** ending 7: "I prayed for him every day of his life... I pray for his soul still." Ending 14: "I
  say Mass for him, and leave the rest to God's mercy." Both are hope, not a claim to know where Micah is.

### Burying a suicide

- **Catholic, 1917:** those who killed themselves *deliberato consilio* were denied ecclesiastical burial unless they
  gave some sign of repentance before death (CIC c. 1240 §1 n. 3); in doubt, the bishop was consulted and, if doubt
  remained, burial given (§2); those denied burial were denied the funeral Mass too (c. 1241). Modern: CCC 2282-2283
  stresses diminished responsibility and hope.
- **Protestant:** no canonical rule; pastors buried case by case.
- **Lines (fixed):** ending 7, when Eleanor lives: "She heard him ask forgiveness before the end. I don't know what
  that word weighed. God does." Words said and followed at once by the shot are not the retracted will the canon looks
  for, so Caleb claims no Church burial; he leaves the word to God. When he shot her too, there was no witness, and
  Caleb's entry claims no funeral.
- Endings 3, 4, 5 and 13 don't show a burial; "Rose, I'm sorry" in the unsent prison letter (4, 5) would be a weaker
  sign.

### Sacramentals

- **Catholic:** the cross and the ring are sacramentals: they dispose to grace through the Church's prayer (*ex opere
  operantis Ecclesiae*), and treating them as charms is superstition.
- **Protestant:** wary of objects; the Lutherans keep crucifixes, the Reformed do not.
- **Lines:** Caleb: "Take this cross, brother. Not as a bargain with God. As a reminder."
- **Verdict:** sound for both: Caleb warns against the superstition both sides fear. The Our Father gate (ring, cross,
  the return to the church, pressing Rose) is a narrative sign that Micah is ready, not merit that buys grace.

### Marriage

- **Catholic:** the bond survives adultery; separation is allowed, remarriage is not (Trent XXIV can. 7).
- **Reformed:** the innocent party may divorce and remarry (WCF XXIV.5-6). **Lutheran:** the same, from Luther and the
  church orders.
- **Bears on:** Rose in every ending. Under Westminster she could leave Micah; nothing in either tradition frees
  Micah. Ending 1's promises "said again", at Caleb's church or at St. Anne's, Caleb blessing them, are a private renewal (there was no
  rite for it in 1927) in a Catholic church (CIC c. 1258 forbids a priest taking part in non-Catholic worship).

### Smaller points

- Agatha's quiz: "I will shew thee, O man, what is good" is Micheas 6:8 in the Douay-Rheims, as a 1927 nun would know it.
- Agatha's "Begone, Satan!" (fixed from the KJV "Get thee behind me") is the Douay-Rheims Matthew 4:10.
- Caleb knows of the trafficking from girls at his church door, not under the seal, so he may act on it.
- The Club's "groves and wells and fires on the hilltops" are idolatry to both traditions; no divergence.

## The endings

Each ending is classed by what it *shows*: repentance shown, left unresolved, or apparent refusal. Neither tradition
lets a reader see God's judgment.

- **Catholic:** grace is lost by every mortal sin and restored by penance; no one can be certain of his own salvation
  without special revelation (Trent VI ch. 9, 12, 14-15). Last-moment contrition is always possible.
- **Lutheran:** a believer can fall from grace and be restored (AC XII.7). **Reformed:** the truly regenerate
  persevere, though assurance can be shaken and sin may grieve the Spirit (WCF XVII.1-3, XVIII.4).

| # | What happens | Shows | Catholic reading | Protestant reading |
|---|---|---|---|---|
| 1 | Micah gives up the search, walks away from Tony, or spares the old man with the Our Father; coffee with Rose, a year later their promises said again | Repentance | Conversion, return to the sacraments; restitution through the papers if he took them (Caleb carries them) | Fruit of repentance (Luke 3:8); the marriage restored by grace, not law |
| 2 | Out of town with Eleanor; she leaves again, he drinks | Refusal | Adultery unrepented, a state of mortal sin; despair growing | Same judgment; no sign of faith or repentance |
| 3 | Out of town alone; the stained last page | Refusal, then suicide | Suicide with no sign of repentance; burial would be denied (c. 1240) | Despair and self-murder (WLC 136); judgment left to God |
| 4, 5 | Prison, Eleanor or Caleb visits; "They took my belt. They left me the sheets." | Unresolved, then suicide | "Rose, I'm sorry" a weak sign; the burial question as above; hope never extinguished | Sorrow toward Rose, but none toward God shown |
| 6 | He turns himself in; Rose visits; "I returned to the faith" | Repentance | Contrition, confession (with the papers), satisfaction accepted as temporal punishment | Repentance and faith; the sentence is Romans 13, not payment |
| 7 | Murder and suicide (or suicide alone, Eleanor living) | Apparent refusal, with a last plea | "Forgive me..." spoken before the shot, not the retracted will c. 1240 asks for; Caleb prays for his soul and leaves the word to God | Forgiveness asked at the last; only God knows if it was faith |
| 8 | Eleanor strikes the old man, burns the house, walks out of the city | Unresolved | The blow: possibly defence against a captor between her and the only door, but with vengeance in it ("Good girl."); arson endangering others; no confession shown | Same moral analysis (WLC 135-136); no sacrament needed, repentance not shown |
| 9 | Eleanor strikes him, stays, is tried, confesses to Caleb, testifies | Repentance | Valid absolution after sorrow for every part that wanted him dead; testimony as restitution to the girls | Repentance and public confession of the truth; prison as Romans 13 |
| 10 | Micah shoots the old man; Eleanor leaves to look for her peace | Unresolved, turning | Homicide of an unarmed but dangerous man: legitimate defence or rescue is narrow (ST II-II q. 64 a. 3, 7); he holds back from Communion, rightly, until confession | His conscience demands confession of the killings; the station is his choice, not a condition of grace |
| 11 | Prison; Eleanor visits once | Repentance beginning | Same homicide; if Tony died, he confessed it in court ("said them out loud"); Caleb on the first Sunday of the month suggests the sacraments resumed | "Peace is a direction": sanctification as a road |
| 12 | Micah killed Tony and turned himself in; Caleb visits | Repentance | Confession and absolution (`caleb_tony`), restitution (letters to Tony's mother), satisfaction | Repentance and civil justice; the letters as fruit, not price |
| 13 | He runs from the alarm; Omaha, the revolver on the washstand | Unresolved, despair | Despair, no sign of turning; the death only implied, so final impenitence is *not* shown | Same; assurance absent, judgment unknown |
| 14 | He goes in for her and is shot in the kitchen | Unresolved | "Not repentance, but the right direction": no contrition shown, last-moment contrition possible; Caleb says Mass for him | Both traditions require repentance and faith, so not softer; the direction is not conversion |

Further points the endings raise:

- **Killing to free a captive (8, 9, 10, 11).** Both traditions allow defence of self and others, with necessity,
  proportion and right intention (ST II-II q. 64 a. 7; WLC 135-136; HC 105-107). Harrington is unarmed, but he stands
  between Eleanor and the door with his men across the landing, and he keeps her by drugs and force. What fails the
  test is not the blow as such but the will to make him pay (Romans 12:19). That is why ending 9's absolution asks
  for sorrow for the vengeance, not the escape.
- **The prayer, and leaving the captive.** On the prayer route Micah renounces killing and walks out, leaving Eleanor
  behind. Renouncing vengeance is right; it doesn't discharge the duty to help a captive. The game leaves that
  incompleteness standing, and Eleanor's own coda answers it.
- **Coercion is not consent.** Whether Eleanor held out (the interlude gate to endings 8 to 11) is a narrative branch,
  not a measure of her worth: what was forced on her is not her sin in either tradition.
- **Satisfaction versus fruit.** In 1, 6, 9 and 12 the same deeds (prison, restitution, testimony) are satisfaction
  and temporal punishment for a Catholic, and the fruit of repentance for a Protestant. The game words them so that
  both readings stand ("Tony's mother doesn't, and I don't ask her to").
- **Caleb's own turning.** His silence is the one sin the story lets him carry; ending 1 with the papers (the Tribune) and ending 9
  (Eleanor's testimony, "She did, in one afternoon, what I had not the courage to do") are his reckoning.

## Fix log

| Where | Was | Now | Why |
|---|---|---|---|
| `epilogue`, ending 1 | Caleb told what he could "without breaking the seal" of her confession | She told him on the rectory steps and asked him to let Micah know | Seal (c. 889) |
| `epilogue`, ending 7 | Caleb published Micah's confession of Tony | Tony found behind the Blue Lantern; "What else I know of it, I may not write." | Seal |
| `epilogue`, ending 7 | "I prayed for him every day of his life" | adds "I pray for his soul still"; if Eleanor lived, she heard him ask forgiveness, and Caleb leaves what that word weighed to God | Prayer for the dead (Trent XXV); no burial claimed (c. 1240) |
| `epilogue`, ending 9 | "from her own confession, at her asking" | what she told the court, and told him again plainly afterwards, at her asking | Seal follows the sacrament, not the place |
| `epilogue`, ending 12 | Caleb's note: "She came to my confessional" | she told him all of it, months after, and asked him to write it in | Seal |
| `epilogue`, ending 13 | "She came to his confessional" | she came to him and told him, and asked him to pass it on (after her escape: told him the night he got her out of Chicago) | Seal |
| `epilogue`, ending 14 | "she told me herself, in my confessional"; no prayer | she told him on the church steps (after her escape: at the city's edge, the night he got her out); "I hear her confession, and I can do nothing else" becomes "I see her at Mass" (after her escape: he put her on a truck out of Chicago); "I say Mass for him" | Seal (no betrayal by sign); prayer for the dead |
| `epilogue`, ending 1 (Tony shot) | vows renewed "in a little white church downstate", Caleb "to say the words" | promises said again at St. Anne's, a Catholic church; Caleb blesses them | No renewal rite in 1927; c. 1258 |
| `epilogue`, ending 1 (Tony not shot) | "Rose and I renewed our vows today, at Caleb's church" | "said our promises again today, at Caleb's church. He blessed us." | No renewal rite in 1927 |
| `prison_eleanor_caleb` | absolution though she "can't be sorry for the last one"; touched forehead | sorrow "for all of it", and for every part that wanted him dead; a hand raised over her | Trent XIV ch. 4; *Rituale Romanum* |
| `caleb_tony` | no absolution; the station as "the only penance a priest can't give himself" | sorrow, "no more blood", amends to Tony's mother, penance, absolution; the station asked as a brother | c. 887; no imposed self-denunciation |
| `caleb_club` | "I confess it every week. It doesn't get lighter." | "I confess the silence every week, and I mean to break it the day it won't bury the girls we hid. That day hasn't come." | Confession needs a purpose of amendment |
| `interlude_agatha_night` | "Get thee behind me!" (KJV) | "Begone, Satan!" (Douay-Rheims, Matthew 4:10) | A 1927 nun's Bible |

Kept on purpose: the Our Father doxology (Micah's Protestant leaning), Caleb's "That's pride" (pastoral, about Micah),
and the fire-escape "They decide him" (Micah's excuse, which the story doesn't endorse).
