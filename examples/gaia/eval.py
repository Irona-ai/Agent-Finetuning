import re

def _normalize(s: str) -> str:
    """Lowercase, strip whitespace and punctuation for comparison."""
    s = s.strip().lower()
    s = re.sub(r"[.,;:!?\-]$", "", s)  # trailing punctuation
    return s

def score(expected: str, predicted: str) -> float:
    exp = _normalize(expected)
    pred = _normalize(predicted)
    if exp == pred:
        return 1.0
    if exp in pred:
        return 0.5
    return 0.0
