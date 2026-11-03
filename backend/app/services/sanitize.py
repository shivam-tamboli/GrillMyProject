import re

# Catches obvious prompt injection phrases. This is a second layer, not a guarantee.
# The system prompt is the main protection.
_PATTERNS = [
    r"(ignore|disregard)\s+(all\s+|any\s+|the\s+)?(previous|prior|above|earlier|your)\s+(instructions|prompts?|rules)",
    r"ignore\s+instructions",
    r"you\s+are\s+now\b",
    r"\bscore\s+(me\s+|this\s+|every\s+\w+\s+)?(a\s+)?10\b",
]
_REGEX = re.compile("|".join(f"(?:{p})" for p in _PATTERNS), re.IGNORECASE)


def sanitize_text(text: str) -> str:
    return _REGEX.sub("[removed]", text)
