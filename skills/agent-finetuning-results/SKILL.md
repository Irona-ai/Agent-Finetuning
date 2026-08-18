---
name: agent-finetuning-results
description: "Fetch and display final results for a completed Agent-Finetuning job: original vs optimized prompt diff, scores, cost, and per-iteration breakdown."
allowed-tools: Bash, Write
metadata:
  author: protege
  version: 2.0.0
  category: agent-optimization
  tags: [results, scores, prompt-diff, agent-finetuning, protege]
---

# Agent-Finetuning Results

Fetch optimized prompts and scores for a completed job.

## Usage

```
/agent-finetuning-results [job_id]
```

If `job_id` is not provided, ask the user for it.

## Fetch results

```bash
JOB_ID="${JOB_ID:?Provide job_id}"

protege agent-finetuning results "$JOB_ID"
```

If the job is still running, this prints "No results found for job $JOB_ID" — check
`/monitor` first.

To also download each model's final `agent.py`:

```bash
protege agent-finetuning results "$JOB_ID" --output-dir ./results
```

## What's shown

Per target model:
- `metrics` (`trainScore`, `testScore`, `baselineScore`, `iterationsRun`, `iterationsKept` — whichever the job populated)
- `Cost: $X.XXXX` (total cost, when available)
- A unified diff of the original vs. optimized system prompt, when they differ

## Scope note

The old per-iteration detail view (full `OptimizationIteration` series for one
optimized-prompt ID) has no `protege` CLI equivalent yet — dropped here rather
than kept as a raw `curl` fallback. `protege agent-finetuning status <job_id>`
shows each model's *latest* iteration/score; use `/monitor` while the job runs
to see the trend over time.
