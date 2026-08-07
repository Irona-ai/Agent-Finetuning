---
name: agentopt-results
description: "Fetch and display final results for a completed AgentOpt job: original vs optimized prompt diff, scores, cost, and per-iteration breakdown."
allowed-tools: Bash, Write
metadata:
  author: ironlabs
  version: 2.0.0
  category: agent-optimization
  tags: [results, scores, prompt-diff, agentopt, ironlabs]
---

# AgentOpt Results

Fetch optimized prompts and scores for a completed job.

## Usage

```
/agentopt-results [job_id]
```

If `job_id` is not provided, ask the user for it.

## Step 1 — List results for the job

```bash
JOB_ID="${JOB_ID:?Provide job_id}"
STUDIO="${IRONLABS_STUDIO_URL:-http://localhost:3000}"
API_KEY="${IRONLABS_API_KEY:?Set IRONLABS_API_KEY}"

curl -s "$STUDIO/api/v1/optimized-prompts" \
  -H "Authorization: Bearer $API_KEY" | python3 - "$JOB_ID" <<'EOF'
import json, sys, difflib

data  = json.load(sys.stdin).get("data", [])
job_id = sys.argv[1]

results = [r for r in data if r.get("trainingJobId") == job_id]

if not results:
    print(f"No results found for job {job_id}.")
    print("Job may still be running — check /monitor first.")
    sys.exit(0)

for r in results:
    print("=" * 60)
    print(f"Model:    {', '.join(r.get('model', []))}")
    print(f"Name:     {r.get('name', '')}")

    metrics = r.get("metrics") or {}
    if metrics:
        train    = metrics.get("trainScore", "—")
        test     = metrics.get("testScore", "—")
        baseline = metrics.get("baselineScore")
        delta    = f"{(train or 0) - baseline:+.3f}" if baseline is not None else "—"
        print(f"Train:    {train}  (baseline: {baseline}, delta: {delta})")
        print(f"Test:     {test}")
        print(f"Iters:    {metrics.get('iterationsRun','—')} run / {metrics.get('iterationsKept','—')} kept")

    cost = (r.get("costBreakdown") or {}).get("totalCostUsd")
    if cost is not None:
        print(f"Cost:     ${cost:.4f}")

    orig = r.get("originalPrompt", "")
    opt  = r.get("optimizedPrompt", orig)
    print()
    if orig == opt:
        print("Prompt unchanged.")
    else:
        diff = difflib.unified_diff(
            orig.splitlines(keepends=True),
            opt.splitlines(keepends=True),
            fromfile="original",
            tofile="optimized",
            lineterm="",
        )
        print("--- Prompt diff ---")
        print("".join(diff))

    print()
    print(f"Prompt ID (for full detail): {r['id']}")
EOF
```

## Step 2 — Full detail with iteration series (optional)

Use the `Prompt ID` printed above:

```bash
PROMPT_ID="<id-from-above>"

curl -s "$STUDIO/api/v1/optimized-prompts/$PROMPT_ID" \
  -H "Authorization: Bearer $API_KEY" | python3 -c "
import json, sys
data  = json.load(sys.stdin).get('data', {})
iters = (data.get('TrainingJob') or {}).get('OptimizationIteration', [])
print(f'Iterations: {len(iters)}')
for it in iters:
    print(f'  iter={it[\"iteration\"]}  decision={it.get(\"decision\",\"?\")}  score={it.get(\"score\",\"?\")}  best={it.get(\"bestScore\",\"?\")}')
"
```

## OptimizedPrompt Fields

| Field | Description |
|-------|-------------|
| `id` | Optimized prompt ID |
| `trainingJobId` | Links to `job_id` from `/create-agent-opt` |
| `model` | Target model(s) |
| `originalPrompt` | SYSTEM_PROMPT from original agent.py |
| `optimizedPrompt` | Best SYSTEM_PROMPT found |
| `metrics` | `trainScore`, `testScore`, `baselineScore`, `iterationsRun`, `iterationsKept` |
| `costBreakdown` | `totalCostUsd` and component breakdown |
| `agentCodeUrl` | Presigned URL to download optimized agent.py |
