# Evaluation

## Method

13 test queries were run against the live app (12 in-scope, spanning bosses, events, armors, accessories, potions, and weapons, plus 1 out-of-scope control query). For each, the retrieved sources panel (including cosine similarity scores) and generated answer were recorded, then checked for correctness against actual game data.

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

**What worked:** Retrieval was accurate across every in-scope category (bosses, events, accessories, potions, armors, weapons), including cross-entity queries that needed to pull from multiple documents at once (#10). The title-match filter fix was directly validated by the Eye of Cthulhu regression test (#1), which previously misretrieved before the fix. In-scope top similarity scores generally landed between 0.45 and 0.69, giving a rough sense of what a confident, on-topic match looks like for this embedding model.

**Notable result:** Boss and event drop data exists in the source dataset but, due to time constraints and since it's not the core focus of boss preparation, queries about drops still retrieve correctly in testing (#9) but don't show further detail on what dropped items actually do. In short, it shows *what* a boss/event drops, but not *what it does*.

**Graceful failure:** The out-of-scope control query (#13) is a stronger result than a simple "no sources" case — the system still retrieved *something* (Lunatic Cultist and Martian Madness chunks), but at very low similarity scores (0.29–0.31), well below the range seen on any in-scope query. Rather than forcing an answer from these weak matches, the system correctly recognized the low relevance and stated it lacked the information, instead of hallucinating a plausible-sounding answer. This is the behavior we want when retrieval genuinely comes up empty or off-topic.

**Fallback behavior:** During testing, the API key was briefly invalid and the generation step fell back to extractive mode (returning raw retrieved text rather than an LLM-generated answer). This shows the app degrades gracefully rather than crashing outright, keeping the chatbot usable even when the LLM call fails.
