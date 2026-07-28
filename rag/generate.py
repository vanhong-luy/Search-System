"""
Generation: turn retrieved chunks + a query into a final answer.

Two modes are provided:
- "extractive": no API key needed, works immediately. Just stitches together
  the retrieved chunks so you can verify retrieval quality independent of
  generation quality.
- "llm" (default for the final submission): calls Gemini (via Google AI
  Studio's free-tier API) to write a real, grounded answer from the retrieved
  context, citing which source(s) it used. Get a free API key at
  https://aistudio.google.com/apikey and set it as the GEMINI_API_KEY
  environment variable.
"""

import os
from typing import List, Tuple

from .ingest import Chunk

# Tried in order; falls through to the next on ANY failure (model retired,
# quota/rate-limit hit, etc.) so one dead or exhausted model doesn't take down
# a live demo. Google has been retiring Gemini model IDs quickly in 2026, so
# this list is more resilient than pinning to a single model name - if all of
# these are ever retired, check https://aistudio.google.com/ for current
# free-tier model IDs and update this list.
LLM_MODEL_CANDIDATES = [
    "gemini-3.1-flash-lite",
    "gemini-3-flash-preview",
    "gemini-2.5-flash-lite",
]

NO_MATCH_MESSAGE = (
    "I'm sorry, but I couldn't help you with this topic, as my job is "
    "to show player bosses' overview, preparation and some strategies."
    " To enjoy the game, you need to play and experience it yourself."
    " And if you believe that your topic is related but got an error instead,"
    " try rephrasing, or check that the right category is selected."
)


def extractive_answer(query: str, retrieved: List[Tuple[Chunk, float]]) -> str:
    if not retrieved:
        return NO_MATCH_MESSAGE
    lines = [f"Top passages related to: \u201c{query}\u201d\n"]
    for chunk, score in retrieved:
        lines.append(f"[{chunk.doc_title}, score={score:.2f}] {chunk.text}\n")
    return "\n".join(lines)


def _build_prompt(query: str, retrieved: List[Tuple[Chunk, float]]) -> str:
    context = "\n\n".join(
        f"Source: {c.doc_title} \u2014 {c.section or 'General'} (category: {c.category})\n{c.text}"
        for c, _ in retrieved
    )
    return (
        "You are answering a question using ONLY the sources below. Do not use "
        "outside knowledge, even if you happen to know the answer.\n\n"
        f"{context}\n\n"
        f"Question: {query}\n\n"
        "Instructions:\n"
        "- Answer using only the information in the sources above.\n"
        "- If the sources don't actually contain the answer, say plainly that "
        "you don't have enough information, instead of guessing.\n"
        "- Non-Expert Mode mean the boss or event behavior on Journey Mode and Normal Mode\n"
        "- Expert Mode mean the boss or event behavior on Expert Mode\n"
        "- All bosses except Lunatic Cultist, change their AI to more advanced AI om higer difficulties\n"
        "- If the boss or event not mention about Master Mode, it does not change anything from previous difficulty, "
        " besides much higher health and deal double damage.\n"
        "- If the boss or event not mention about Legendary Mode/Secret Mode/, it does not change anything from previous difficulty, "
        " besides much higher health and deal double damage.\n"
        "- Easter Egg: If user type number '7355608' in, you response with 'Bomb has been planted'.\n"
        "- When listing potions, accessories or armors, searching through their respected data file: "
        "items/accessories.md, items/potions.md and items/armor.md"
        "- End your answer with a line listing which source title(s) you used, "
        "e.g. \"Sources used: King Slime \u2014 Strategies\".\n\n"
        "Answer:"
    )


def llm_answer(query: str, retrieved: List[Tuple[Chunk, float]]) -> str:
    if not retrieved:
        # Prevent it from hallucinating.
        # Don't even joke lad.
        return NO_MATCH_MESSAGE

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return (
            "[LLM mode not configured] Set the GEMINI_API_KEY environment "
            "variable (get a free key at https://aistudio.google.com/apikey) "
            "to enable grounded LLM answers. Falling back to extractive "
            "mode:\n\n" + extractive_answer(query, retrieved)
        )

    prompt = _build_prompt(query, retrieved)

    try:
        from google import genai
    except ImportError:
        return (
            "[LLM mode not configured] Install the Gemini SDK "
            "(pip install google-genai) to enable grounded LLM answers. "
            "Falling back to extractive mode:\n\n" + extractive_answer(query, retrieved)
        )

    client = genai.Client(api_key=api_key)
    last_error = None
    for model_name in LLM_MODEL_CANDIDATES:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
            )
            return response.text
        except Exception as e:
            last_error = e
            continue  # try next model

    # Basic error handling for API failures (all candidates retired, rate
    # limited, bad key, network, etc.) so a live demo degrades gracefully
    # instead of crashing the app.
    return (
        f"[LLM call failed: {last_error}] Falling back to extractive mode:\n\n"
        + extractive_answer(query, retrieved)
    )


def generate_answer(query: str, retrieved: List[Tuple[Chunk, float]], mode: str = "llm") -> str:
    if mode == "extractive":
        return extractive_answer(query, retrieved)
    return llm_answer(query, retrieved)