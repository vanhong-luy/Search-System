# Evaluation

## Method

13 test queries were run against the live app (12 in-scope, spanning bosses, events, items, and weapons, plus 1 out-of-scope control query). For each, the retrieved sources panel and generated answer were recorded, then checked for correctness against actual game data.

## Results

| # | Query | Category | Result | Sources |
|---|-------|----------|--------|---------|
| 1 | "How do I beat the Eye of Cthulhu?" | Boss — regression case | Correct — full strategy returned | All 3 from Eye of Cthulhu doc — confirms the title-match filter fix holds (this query previously misretrieved a different boss's chunk due to cross-boss semantic similarity) |
| 2 | "What are Golem's attack patterns?" | Boss | Correct — fist attack, eye laser, bouncing fireball, jump | All 3 from Golem doc |
| 3 | "When does Blood Moon happen and how do I start it?" | Event | Correct — full night window, natural + manual trigger | Blood Moon doc only |
| 4 | "What's different in Expert Mode during Blood Moon?" | Event | Correct — stronger enemies, more coin drops | Correct source |
| 5 | "What does Frost Armor's set bonus do?" | Item | Correct | Returned armor data source |
| 6 | "How much defense does Turtle Armor give?" | Item | Correct | Returned armor data source |
| 7 | "Best summon weapon for Queen Bee?" | Weapon | Correct | Returned weapon for Queen Bee, specifically the summon weapon source |
| 8 | "How do I craft the Terra Blade?" | Weapon | Correct — ingredients and crafting station listed | Correct source |
| 9 | "What does Skeletron Prime drop?" | Drop table (expected weak spot) | Correct | Shows the drop item names, sourced correctly |
| 10 | "Best melee loadout against early game bosses?" | Cross-entity | Correct — appropriately pulled Queen Bee, Deerclops, and Eye of Cthulhu | Multiple boss docs |
| 11 | "Recommended potions for the Wall of Flesh?" | Item | Correct — full potion list; honestly noted the sources don't cover per-potion effects for most entries | 3 sources, correctly scoped |
| 12 | "Accessories for Empress of Light?" | Item | Correct | Returned all necessary accessories, correctly sourced |
| 13 | "Supreme Witch, Calamitas overview" | Out-of-scope (control) | Graceful failure — correctly declined rather than fabricating an answer | None (correctly abstained) |

**Score: 12/13 fully correct, 1/13 correct graceful failure (by design).**

## Discussion

**What worked:** Retrieval was accurate across every in-scope category (bosses, events, items, weapons), including cross-entity queries that needed to pull from multiple documents at once (#10). The title-match filter fix was directly validated by the Eye of Cthulhu regression test (#1), which previously misretrieved before the fix.

**Notable result:** Drop-table queries were flagged as a known limitation during development, since drop data is stored per-item rather than per-boss/event. In practice (#9), retrieval still surfaced the correct drop information — this is a positive result worth calling out rather than a weakness, though it should be tested more broadly before calling the limitation fully resolved.

**Graceful failure:** The out-of-scope control query (#13) confirms the system doesn't hallucinate when it has no grounding — it explicitly stated it lacked the information rather than inventing a plausible-sounding answer. This is the behavior we want to see when retrieval genuinely comes up empty.

**Fallback behavior:** During testing, the generation step occasionally fell back to extractive mode (returning raw retrieved text rather than an LLM-generated answer) when the API key was temporarily invalid. This is a resilience feature — the app degrades gracefully rather than crashing when the LLM call fails.
