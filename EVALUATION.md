# Evaluation

## Method

13 test queries were run against the live app (12 in-scope, spanning bosses, events, armors, accessories, potions, and weapons, plus 1 out-of-scope control query). For each, the retrieved sources panel and generated answer were recorded, then checked for correctness against actual game data.

## Results

| # | Query | Category | Top Scores | Result | Sources |
|---|-------|----------|---|--------|---------|
| 1 | "How do I beat the Eye of Cthulhu?" | Boss | 0.57, 0.55, 0.41 | Correct — full strategy returned | All 3 chunks from eye_of_cthulhu.md (Overview, Non-Expert Mode Fight, Strategies) |
| 2 | "What are Golem's attack patterns?" | Boss | 0.56, 0.54, 0.49 | Correct — fist attack, eye laser, bouncing fireball, jump | All 3 chunks from golem.md (Overview, Expert Mode Fight, Strategies) |
| 3 | "When does Blood Moon happen and how do I start it?" | Event | 0.56, 0.55, 0.47 | Correct — full night window, natural + manual trigger | All 3 chunks from blood_moon.md (Overview, How It's Triggered, Preparation) |
| 4 | "What's different in Expert Mode during Blood Moon?" | Event | 0.52, 0.41, 0.32 | Correct — stronger enemies, more coin drops | All 3 chunks from blood_moon.md |
| 5 | "What does Frost Armor's set bonus do?" | Armor | 0.62, 0.45, 0.45 | Correct — returned armor data | 3 chunks pulled from armor.md (Frost, Adamantite, Flinx Fur Coat), used only the Frost Armor chunk |
| 6 | "How much defense does Turtle Armor give?" | Armor | 0.58, 0.48, 0.47 | Correct — returned armor data | 3 chunks pulled from armor.md (Turtle, Beetle, Pumpkin), used only the Turtle Armor chunk |
| 7 | "Best summon weapon for Queen Bee?" | Weapon | 0.69, 0.63, 0.60 | Correct — returned the summon weapon specifically | All 3 chunks from queen_bee.md (Recommended Weapons, Non-Expert Mode Fight, Overview) |
| 8 | "How do I craft the Terra Blade?" | Weapon | 0.47, 0.46, 0.45 | Correct — ingredients and crafting station listed | 1 chunk from weapons_s_t.md (Terra Blade) and 2 from accessories.md (Celestial Emblem, Celestial Shell); only the Terra Blade chunk was used |
| 9 | "What does Skeletron Prime drop?" | Boss Drop | 0.57, 0.52, 0.45 | Correct — showed drop item names | All 3 chunks from skeletron_prime.md (Non-Expert Mode Fight, Overview, Drops) |
| 10 | "Best melee loadout against early game bosses?" | Cross-entity | 0.57, 0.57, 0.57 | Correct — appropriately pulled Queen Bee, Deerclops, and Eye of Cthulhu | queen_bee.md, deerclops.md, eye_of_cthulhu.md (all Recommended Weapons chunks) |
| 11 | "Recommended potions for the Wall of Flesh?" | Item | 0.60, 0.60, 0.58 | Correct — full potion list; honestly noted the sources don't cover per-potion effects for most entries | wall_of_flesh.md (Recommended Potions) + potions.md (Heartreach, Thorns); only the Wall of Flesh chunk was used |
| 12 | "What accessories should I bring to fight Empress of Light?" | Item | 0.51, 0.46, 0.45 | Correct — returned all necessary accessories | All 3 chunks from empress_of_light.md (Drops, Overview, Recommended Accessories) |
| 13 | "Supreme Witch, Calamitas overview" | Out-of-scope (control) | 0.31, 0.29, 0.29 | Graceful failure — correctly declined rather than fabricating an answer | Weakly matched, off-topic chunks (Lunatic Cultist, Martian Madness) — all well below a usable relevance threshold |

**Score: 12/13 fully correct, 1/13 correct graceful failure (by design).**

## Discussion

**What worked:** Retrieval was accurate across every in-scope category (bosses, events, accessories, potions, armors, weapons), including cross-entity queries that needed to pull from multiple documents at once (#10). The title-match filter fix was directly validated by the Eye of Cthulhu regression test (#1) (misretrieved before the fix).

**Notable result:** Boss and event drop data exists in the source dataset but due to time constraint and not related to boss preparation itself, the queries will still retrieved them correctly in testing, but will not show any further details for certain items. In a word, it shows you what the boss/event drop, but not what it does.

**Graceful failure:** The out-of-scope control query (#13) confirms the system doesn't hallucinate when it has no sources - it stated clearly that it lacked the information rather than pulling an answer out of thin air. This is the behavior we looking for when the retrieval process comes up empty.

**Fallback behavior:** During testing, the API key was temporary invalid and the generation step occasionally fell back to extractive mode (returning raw retrieved text rather than an LLM-generated answer). This is show that, the app degrades gracefully rather than plummeting head down to the ground and cause a huge error, make the chatbot become unusable.
