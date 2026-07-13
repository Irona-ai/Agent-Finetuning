import re

def _normalize_finance(s: str) -> str:
    """Normalize financial strings: lowercase, strip $/%/commas."""
    s = s.strip().lower()
    s = re.sub(r"[$,]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()

def score(expected: str, predicted: str) -> float:
    exp = _normalize_finance(expected)
    pred = _normalize_finance(predicted)
    if exp == pred:
        return 1.0
    if exp in pred:
        return 0.5
    return 0.0
