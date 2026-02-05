"""
Hitchhiker's Guide to the Galaxy - Constants and Utilities
==========================================================

"In the beginning the Universe was created.
 This has made a lot of people very angry and been widely
 regarded as a bad move."

Used across all AgentCore demos and tests for thematic consistency.
"""

import random

# ---------------------------------------------------------------------------
# The Ultimate Answer
# ---------------------------------------------------------------------------

THE_ANSWER = 42

DEEP_THOUGHT_QUOTE = (
    "The Answer to the Great Question... of Life, the Universe "
    "and Everything... Is... Forty-two."
)

THE_QUESTION = (
    "What do you get if you multiply six by nine?"
    # (In base 13 that's 42. The universe is fundamentally flawed.)
)

# ---------------------------------------------------------------------------
# Characters
# ---------------------------------------------------------------------------

ARTHUR_DENT = "Arthur Dent"
FORD_PREFECT = "Ford Prefect"
ZAPHOD_BEEBLEBROX = "Zaphod Beeblebrox"
MARVIN = "Marvin the Paranoid Android"
TRILLIAN = "Trillian"
DEEP_THOUGHT = "Deep Thought"
SLARTIBARTFAST = "Slartibartfast"

# ---------------------------------------------------------------------------
# Marvin Quotes  (Memory demo)
# ---------------------------------------------------------------------------

MARVIN_QUOTES = [
    "I think you ought to know I'm feeling very depressed.",
    "Life? Don't talk to me about life.",
    "Here I am, brain the size of a planet, and they tell me to take you up to the bridge.",
    "I've been talking to the ship's computer. It hates me.",
    "The first ten million years were the worst. And the second ten million... they were the worst too.",
    "I have a million ideas. They all point to certain death.",
    "Pardon me for breathing, which I never do anyway so I don't know why I bother to say it.",
]

# ---------------------------------------------------------------------------
# Guide Entries  (Browser demo)
# ---------------------------------------------------------------------------

GUIDE_ENTRIES = {
    "earth": "Mostly harmless.",
    "towel": (
        "A towel is about the most massively useful thing an "
        "interstellar hitchhiker can have."
    ),
    "babel_fish": (
        "The Babel fish is small, yellow, leech-like, and probably "
        "the oddest thing in the Universe."
    ),
    "pan_galactic_gargle_blaster": (
        "The best drink in existence. Its effects are similar to "
        "having your brains smashed out by a slice of lemon wrapped "
        "round a large gold brick."
    ),
    "vogon_poetry": "The third worst poetry in the Universe.",
    "agentcore": (
        "A modular, agentic platform for building, deploying, and "
        "operating AI agents. Mostly useful."
    ),
}

# ---------------------------------------------------------------------------
# Calculations that equal 42  (Code Interpreter demo)
# ---------------------------------------------------------------------------

FORTY_TWO_CALCULATIONS = [
    ("6 * 7", 42),
    ("84 / 2", 42.0),
    ("2 * 3 * 7", 42),
    ("40 + 2", 42),
    ("50 - 8", 42),
    ("126 / 3", 42.0),
    ("21 * 2", 42),
    ("6 ** 2 + 6", 42),
]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def random_marvin_quote() -> str:
    """Return a random Marvin quote."""
    return random.choice(MARVIN_QUOTES)


def guide_entry(topic: str) -> str:
    """Look up a Guide entry. Returns 'Mostly harmless.' for unknowns."""
    return GUIDE_ENTRIES.get(topic.lower(), "Mostly harmless.")


def deep_thought_banner() -> str:
    """Return the Deep Thought computation banner."""
    return "\n".join([
        "",
        "  +-------------------------------------------------+",
        "  |           DEEP THOUGHT COMPUTING ...             |",
        "  |  \"The Answer to the Great Question ...           |",
        '  |   of Life, the Universe and Everything ...       |',
        '  |   Is ... Forty-two."                             |',
        "  +-------------------------------------------------+",
        "",
    ])


def dont_panic_banner() -> str:
    """Return the iconic DON'T PANIC banner."""
    return "\n".join([
        "",
        "  +=========================================+",
        "  |                                         |",
        "  |            DON'T PANIC                  |",
        "  |                                         |",
        "  +=========================================+",
        "",
    ])


def babel_fish_banner() -> str:
    """Return the Babel Fish banner for Gateway."""
    return "\n".join([
        "",
        "  ~~ The Babel Fish of APIs ~~",
        "  Translating any protocol to MCP so your",
        "  agents can understand the Universe.",
        "",
    ])
