---
name: create-agent-finetuning
description: "Submit a new Agent-Finetuning optimization job to Studio. Runs smoke-test first — aborts before any network call if validation fails. Use when user wants to start optimizing an agent."
allowed-tools: Bash, Read, Write
metadata:
  author: protege
  version: 2.0.0
  category: agent-optimization
  tags: [create, submit, job, agent-finetuning, protege, e2b]
---

# Create Agent-Finetuning Job

End-to-end workflow: validate files → build ZIP → create Task → launch job → print job ID.

**Smoke-test runs before any Studio network call.** If it fails, stop and help the user fix their files.

## Step 1 — Gather inputs

Ask for any missing items:

| Item | Default | Notes |
|------|---------|-------|
| `agent.py` path | `./agent.py` | Must have `async def run_batch(inputs, api_key)` |
| `eval.py` path | `./eval.py` | Must have `def score(expected, predicted) -> float` |
| `dataset.json` path | `./dataset.json` | JSON array of `{input, answer}`, min 10 items |
| `target_models` | `openai/gpt-4o-mini` | 1–5 comma-separated OpenRouter model strings |
| `n_iterations` | `15` | 1–50; use 3–5 for a quick test |

Requires `protege` installed and logged in — run `/agent-finetuning:setup` first if not.

## Step 2 — Run smoke-test

Invoke `agent-finetuning:smoke-test` on the provided files.

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
ZIP="$TMP/agent_finetuning_input.zip"
(cd "$TMP" && zip -q "$ZIP" agent.py eval.py dataset.json)
echo "ZIP: $(du -sh $ZIP | cut -f1)"
```

To include extra data files (e.g., reference corpora, tool configs):
```bash
cp extra_data.json "$TMP/files/"
(cd "$TMP" && zip -qr "$ZIP" agent.py eval.py dataset.json files/)
```

## Step 4 — Create the Task

```bash
TASK_OUT=$(protege agent-finetuning task create "$ZIP" --name "my-agent")
echo "$TASK_OUT"
TASK_ID=$(echo "$TASK_OUT" | sed -n 's/^Created task //p')
```

## Step 5 — Launch the job

```bash
TARGET_MODELS="${TARGET_MODELS:-openai/gpt-4o-mini}"
N_ITERATIONS="${N_ITERATIONS:-15}"

RUN_OUT=$(protege agent-finetuning run --task-id "$TASK_ID" \
  --target-models "$TARGET_MODELS" \
  --n-iterations "$N_ITERATIONS")
echo "$RUN_OUT"
JOB_ID=$(echo "$RUN_OUT" | sed -n 's/^Job queued: //p')

echo ""
echo "Job submitted: $JOB_ID"
echo "Monitor with: /monitor (job_id=$JOB_ID)"
```

**Full `run` flag reference:**

| Flag | Type | Default | Notes |
|------|------|---------|-------|
| `--task-id` / `--input-url` | string | — | Exactly one required; `--input-url` skips Task creation for a one-off run |
| `--target-models` | comma-separated | — | 1–5 OpenRouter model strings |
| `--n-iterations` | int | 15 | 1–50 |
| `--overall-timeout` | int (seconds) | 3600 | |
| `--llm-call-timeout` | int (seconds) | 600 | |
| `--sandbox-timeout` | int (seconds) | 3600 | |
| `--enable-mcp` | flag | off | |
| `--force-baseline` | flag | off | |
| `--run-benchmark` | flag | off | |
| `--force-benchmark` | flag | off | |
| `--env-id` | string | — | Only used with `--input-url` |
| `--team-id` | string | — | |
| `--watch` | flag | off | Poll until terminal status instead of returning immediately |

## Complete Script

```bash
#!/usr/bin/env bash
set -euo pipefail

AGENT="${1:-agent.py}"
EVAL="${2:-eval.py}"
DATASET="${3:-dataset.json}"
MODEL="${4:-openai/gpt-4o-mini}"
N="${5:-15}"

TMP=$(mktemp -d)
trap "rm -rf $TMP" EXIT
cp "$AGENT" "$TMP/agent.py"
cp "$EVAL"  "$TMP/eval.py"
cp "$DATASET" "$TMP/dataset.json"
(cd "$TMP" && zip -q input.zip agent.py eval.py dataset.json)

TASK_ID=$(protege agent-finetuning task create "$TMP/input.zip" | sed -n 's/^Created task //p')
JOB_ID=$(protege agent-finetuning run --task-id "$TASK_ID" --target-models "$MODEL" --n-iterations "$N" | sed -n 's/^Job queued: //p')

echo "Job ID: $JOB_ID"
echo "Run: /monitor (or: protege agent-finetuning status $JOB_ID)"
```

Usage:
```bash
bash submit.sh agent.py eval.py dataset.json openai/gpt-4o-mini 5
```
