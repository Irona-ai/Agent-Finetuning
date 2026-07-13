import json as _json

def _norm(s: str) -> str:
    return s.strip().lower().replace(" ", "").replace("_", "").replace("-", "")

def score(expected: str, predicted: str) -> float:
    """
    TRAIL scoring: predicted may be a JSON string
    ({"errors": [{"category": ...}], ...}) or plain text.
    Extract the first error category from JSON when possible,
    then compare case-insensitively ignoring spaces/underscores.
    """
    # Try to parse JSON output from the model
    category = predicted.strip()
    try:
        data = _json.loads(predicted)
        errors = data.get("errors", [])
        if errors:
            category = errors[0].get("category", predicted)
        else:
            # No errors → "no_error" or similar
            category = "no error"
    except Exception:
        pass

    exp = _norm(expected)
    pred = _norm(category)

    if exp == pred:
        return 1.0
    if exp in pred or pred in exp:
        return 0.5
    return 0.0
