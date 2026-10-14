# Repentance and salvation: dialogue addition map

Implemented additions to existing conversations in `dialogue/repentance.ink`.
No locations, characters, choices or story flags have been added. The room scripts
already trigger these conversations. The lines are biblical paraphrases or thematic
applications, not direct Scripture quotations. References link to the public-domain
King James Version.

| Existing conversation and placement | Biblical grounding | Implemented addition |
|---|---|---|
| `caleb_act2`: after Caleb calls despair the Devil's oldest trick, before Micah's "I'll think about that" | [Mark 1:15](https://www.biblegateway.com/passage/?search=Mark%201%3A15&version=KJV); [Acts 3:19](https://www.biblegateway.com/passage/?search=Acts%203%3A19&version=KJV); [Ephesians 2:8-9](https://www.biblegateway.com/passage/?search=Ephesians%202%3A8-9&version=KJV): repentance, belief and salvation by grace, not earned wages | **Caleb:** "Turn back to God and believe, Micah. Salvation isn't wages for being good; it's grace." |
| `caleb_club`: after "You know that isn't true" | [Ezekiel 18:21-23](https://www.biblegateway.com/passage/?search=Ezekiel%2018%3A21-23&version=KJV); [1 John 1:9](https://www.biblegateway.com/passage/?search=1%20John%201%3A9&version=KJV): whoever turns from his sins is forgiven | **Caleb:** "Repentance isn't for saints at the end of their lives, Micah. It's for anyone, any day they still draw breath." / "If a man truly repents, the Lord forgives him. Every time." |
| `caleb_club`: answers Micah's "I'm too far gone" | [Proverbs 16:18](https://www.biblegateway.com/passage/?search=Proverbs%2016%3A18&version=KJV); [Romans 5:20](https://www.biblegateway.com/passage/?search=Romans%205%3A20&version=KJV): pride, and grace greater than sin; a thematic application | **Caleb:** rebukes despair as pride: arrogant and self-serving, "another way of putting yourself first" |
| `caleb_club`: closes the conversation | [Luke 15:17-24](https://www.biblegateway.com/passage/?search=Luke%2015%3A17-24&version=KJV): the prodigal returns and his father runs to welcome him | **Caleb:** "The prodigal thought he was past it too. Then he turned for home, and his father ran to meet him." |
| `caleb_warn`: directly answers Micah's "I asked nicely first" | [Luke 3:8](https://www.biblegateway.com/passage/?search=Luke%203%3A8&version=KJV): conduct worthy of repentance, applied to Micah's violence | **Caleb:** "Repentance means more than asking nicely. Put the gun away." |
| `caleb_last`: between "I never could" and Caleb's promise to pray | [Psalm 51:17](https://www.biblegateway.com/passage/?search=Psalm%2051%3A17&version=KJV): God does not despise a broken and contrite heart | **Caleb:** "God doesn't turn away a contrite heart, Micah. You don't have to be whole to turn to Him." |
| `rose_coffee`: after "Nothing. Not tonight", before the coffee invitation | [Acts 26:20](https://www.biblegateway.com/passage/?search=Acts%2026%3A20&version=KJV): deeds fitting repentance; a thematic application, not an explicit Scripture reference in the dialogue | **Micah:** "I'm not asking you to believe I've changed. I'd like to start showing you." |

## Placement and tone

- The central message appears in `caleb_act2`, so it is not confined to optional
  church visits. Later lines answer the immediate conversation in two sentences
  or fewer rather than interrupting it with a sermon.
- Connect repentance with turning from wrongdoing and receiving God's grace,
  not earning salvation through suffering or good deeds.
- Keep Rose's response cautious. Reconciliation with her is not proof of
  salvation, and forgiveness does not entitle Micah to restored trust. Her dialogue
  is unchanged. Micah does not attribute advice to an optional Caleb conversation
  the player might have skipped.
- Agatha already mentions Micah 6:8 and Jezebel. Her later condemnation works
  better as a contrast to Caleb's invitation to repent than as the game's
  authoritative teaching.
- Leave the hotel and speakeasy exchanges unchanged. Explicit references fit
  less naturally there; preserving them maintains the noir voices and pacing.

## Reference accuracy

- Luke 15 describes the father seeing his returning son from afar and running to
  him. It does not explicitly say the father had been waiting continuously; that
  claim was removed from the original proposal. The welcome is not earned.
- Luke 3:8 and Acts 26:20 connect repentance to changed conduct. Putting away the
  gun and offering to demonstrate change are story-specific applications, not
  actions prescribed verbatim by those passages.
- Psalm 51:17 concerns contrition, not merely distress. The dialogue retains
  "contrite" rather than implying that being hurt alone is repentance.

## Review consensus

Claude Opus 5.5 and Grok 4.7 reviewed the references and surrounding dialogue.
Both approved the final wording and placements for biblical fidelity and natural
character voice, with paraphrases distinguished from thematic applications.
The revisions remove the unsupported waiting claim, avoid a second consecutive
"Micah" in Caleb's warning, and keep Rose's conversation free of forced citations.
