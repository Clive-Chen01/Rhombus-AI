import re
from typing import Optional

INTENT_TO_REGEX = {
    "email": r"\\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,7}\\b",
    "phone": r"(?:(?:\\+?61|0)[2-478])(?!0)\\d{7,8}", # AU-ish simplification
    "url": r"https?://[^\\s]+",
    "postcode": r"\\b\\d{4}\\b"
}


EXPLANATIONS = {
    "email": "Matches standard email addresses",
    "phone": "Rough AU phone detection (not perfect)",
    "url": "Matches http/https URLs",
    "postcode": "4-digit Australian postcodes"
}


def nl_to_regex(nl: str) -> tuple[str, Optional[str]]:
    """Very small heuristic to infer regex if LLM is not configured.
    Returns (pattern, explanation)."""
    text = nl.lower()
    for k, pattern in INTENT_TO_REGEX.items():
        if k in text:
            return pattern, EXPLANATIONS.get(k)
    # naive fallback: pass-through if user provided a regex-like string
    if any(ch in nl for ch in ["\\d", "[A-Z]", "("]):
        return nl, "User-supplied pattern (treated as regex)"
    # default extremely permissive word-like token
    return r"\\b\\w+\\b", "Fallback token matcher (please refine your prompt)"




def safe_compile(pattern: str) -> re.Pattern:
    try:
        return re.compile(pattern)
    except re.error as e:
        raise ValueError(f"Invalid regex: {e}")