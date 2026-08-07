---
name: create-agent-opt
description: "Submit a new AgentOpt optimization job to Studio. Runs smoke-test first — aborts before any network call if validation fails. Use when user wants to start optimizing an agent."
allowed-tools: Bash, Read, Write
metadata:
  author: ironlabs
  version: 2.0.0
  category: agent-optimization
  tags: [create, submit, job, agentopt, ironlabs, e2b]
---

# Create AgentOpt Job

End-to-end workflow: validate files → build ZIP → host ZIP → verify URL → submit job → print job ID.

**Smoke-test runs before any Studio network call.** If it fails, stop and help the user fix their files.

## Step 1 — Gather inputs

Ask for any missing items:

| Item | Default | Notes |
|------|---------|-------|
| `agent.py` path | `./agent.py` | Must have `async def run_batch(inputs, api_key)` |
| `eval.py` path | `./eval.py` | Must have `def score(expected, predicted) -> float` |
| `dataset.json` path | `./dataset.json` | JSON array of `{input, answer}`, min 10 items |
| `target_models` | `["openai/gpt-4o-mini"]` | 1–5 OpenRouter model strings |
| `n_iterations` | `15` | 1–50; use 3–5 for a quick test |
| `IRONLABS_API_KEY` | env var | Bearer token |
| `IRONLABS_STUDIO_URL` | `http://localhost:3000` | Studio base URL |

## Step 2 — Run smoke-test

Invoke `agentopt:smoke-test` on the provided files.

**If any smoke-test step fails → stop here. Do NOT proceed to ZIP or Studio.**

Help the user fix the failing check before retrying.

## Step 3 — Build ZIP

```bash
AGENT_FILE="${AGENT_FILE:-agent.py}"
EVAL_FILE="${EVAL_FILE:-eval.py}"
DATASET_FILE="${DATASET_FILE:-dataset.json}"

TMP=$(mktemp -d)
cp "$AGENT_FILE"   "$TMP/agent.py"
cp "$EVAL_FILE"    "$TMP/eval.py"
cp "$DATASET_FILE" "$TMP/dataset.json"
ZIP="$TMP/agentopt_input.zip"
(cd "$TMP" && zip -q "$ZIP" agent.py eval.py dataset.json)
echo "ZIP: $(du -sh $ZIP | cut -f1)"
```

To include extra data files (e.g., reference corpora, tool configs):
```bash
cp extra_data.json "$TMP/files/"
(cd "$TMP" && zip -qr "$ZIP" agent.py eval.py dataset.json files/)
```

## Step 4 — Host ZIP (get input_url)

The ZIP must be reachable by Studio. Options:

**Option A — Simple local HTTP server (dev/testing only):**
```bash
# In a separate terminal, serve the ZIP directory
PORT=8888
python3 -m http.server $PORT --directory "$TMP" &
INPUT_URL="http://host.docker.internal:$PORT/agentopt_input.zip"
# Use host.docker.internal if Studio runs in Docker; otherwise use your machine's IP
```

**Option B — User provides pre-hosted URL:**
```bash
INPUT_URL="https://your-cdn.example.com/agentopt_input.zip"
```

**Option C — Upload to any public storage (S3, GCS, etc.):**
Use provider's CLI; capture the resulting public URL as `INPUT_URL`.

## Step 5 — Verify URL reachability

```bash
VERIFY=$(curl -s -X POST "${IRONLABS_STUDIO_URL:-http://localhost:3000}/api/agentopt/verify-input-url" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${IRONLABS_API_KEY:?Set IRONLABS_API_KEY}" \
  -d "{\"url\": \"$INPUT_URL\"}")

echo "$VERIFY" | python3 -c "
import json, sys
d = json.load(sys.stdin)
if not d.get('reachable'):
    print('ERROR: Studio cannot reach input_url:', d.get('error', 'unknown'))
    sys.exit(1)
print('URL OK:', d.get('content_type'), d.get('content_length'), 'bytes')
" || exit 1
```

## Step 6 — Submit job

```bash
TARGET_MODELS="${TARGET_MODELS:-[\"openai/gpt-4o-mini\"]}"
N_ITERATIONS="${N_ITERATIONS:-15}"

JOB=$(curl -s -X POST "${IRONLABS_STUDIO_URL:-http://localhost:3000}/api/agentopt/optimize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${IRONLABS_API_KEY}" \
  -d "{
    \"input_url\": \"$INPUT_URL\",
    \"target_models\": $TARGET_MODELS,
    \"n_iterations\": $N_ITERATIONS
  }")

echo "$JOB" | python3 -m json.tool
JOB_ID=$(echo "$JOB" | python3 -c "import json,sys; print(json.load(sys.stdin)['job_id'])")
echo ""
echo "Job submitted: $JOB_ID"
echo "Monitor with: /monitor (job_id=$JOB_ID)"
```

**Full request body reference:**

| Field | Type | Default | Notes |
|-------|------|---------|-------|
| `input_url` | string | — | Public URL to ZIP |
| `target_models` | string[] | — | 1–5 OpenRouter model strings |
| `n_iterations` | int | 15 | 1–50 |
| `overall_timeout_seconds` | int | 3600 | 300–7200 |
| `llm_call_timeout_seconds` | int | 600 | 30–600 |
| `sandbox_timeout_seconds` | int | 3600 | 60–7200 |
| `minibatch_size` | int | 3 | SkillOpt batch size; 1 = standard mode |
| `edit_budget` | int | 5 | Max edits per iteration |

**Response:**
```json
{"job_id": "uuid", "status": "queued"}
```

## Complete Script

```bash
#!/usr/bin/env bash
set -euo pipefail

API_KEY="${IRONLABS_API_KEY:?Set IRONLABS_API_KEY}"
STUDIO="${IRONLABS_STUDIO_URL:-http://localhost:3000}"
AGENT="${1:-agent.py}"
EVAL="${2:-eval.py}"
DATASET="${3:-dataset.json}"
MODEL="${4:-openai/gpt-4o-mini}"
N="${5:-15}"

# Build ZIP
TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT
cp "$AGENT" "$TMP/agent.py"
cp "$EVAL"  "$TMP/eval.py"
cp "$DATASET" "$TMP/dataset.json"
(cd "$TMP" && zip -q input.zip agent.py eval.py dataset.json)

# Host ZIP locally (dev)
python3 -m http.server 8888 --directory "$TMP" &
HTTP_PID=$!
trap "kill $HTTP_PID; rm -rf $TMP" EXIT
INPUT_URL="http://host.docker.internal:8888/input.zip"

# Verify
curl -sf -X POST "$STUDIO/api/agentopt/verify-input-url" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "{\"url\":\"$INPUT_URL\"}" | python3 -c \
  "import json,sys; d=json.load(sys.stdin); sys.exit(0 if d.get('reachable') else 1)"

# Submit
JOB=$(curl -sf -X POST "$STUDIO/api/agentopt/optimize" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $API_KEY" \
  -d "{\"input_url\":\"$INPUT_URL\",\"target_models\":[\"$MODEL\"],\"n_iterations\":$N}")

JOB_ID=$(echo "$JOB" | python3 -c "import json,sys; print(json.load(sys.stdin)['job_id'])")
echo "Job ID: $JOB_ID"
echo "Run: /monitor (or set JOB_ID=$JOB_ID and poll status endpoint)"
```

Usage:
```bash
IRONLABS_API_KEY=sk_... bash submit.sh agent.py eval.py dataset.json openai/gpt-4o-mini 5
```
