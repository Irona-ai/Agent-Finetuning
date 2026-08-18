---
name: agent-finetuning
description: "IronLabs Agent-Finetuning overview — iterative Python agent optimizer. Invokes sub-skills for smoke-testing, job creation, monitoring, and result retrieval. Use when user wants to optimize an agent's system prompt or code against a benchmark."
allowed-tools: Read
metadata:
  author: protege
  version: 2.0.0
  category: agent-optimization
  tags: [agent-finetuning, optimization, llm, benchmark, e2b, skillopt, protege]
---

# Agent-Finetuning

Iteratively improve a Python agent's system prompt and code by benchmarking it against a dataset, analyzing failures, and synthesizing targeted patches — running fully automated inside E2B sandboxes.

## What It Does

**Pipeline per optimization job:**

```
Baseline run
  → [Improvement (SkillOpt mini-batch patch synthesis OR standard Claude proposer)
     → Edit phase (Claude implements patches)
     → Benchmark (agent runs on train set in E2B)
     → Score (eval.py judges predictions)
     → Decision: KEEP if score > best, else DISCARD] × N iterations
  → Final test eval (held-out 30% of dataset)
```

**SkillOpt** (used automatically based on internal heuristics, not a client-configurable job parameter): splits failures into mini-batches, calls DeepSeek/OpenRouter to generate structured edit patches per batch, merges hierarchically, ranks by impact, applies top edits. Faster and more targeted than full-context improvement.

**Standard mode**: Claude reads full failure context and writes an `improvement.md` hypothesis, then implements it.

## Required Files

| File | Contract |
|------|----------|
| `agent.py` | Must contain `async def run_batch(inputs: list[str], api_key: str) -> list[str]` — returns one prediction string per input |
| `eval.py` | Must contain `def score(expected: str, predicted: str) -> float` — returns 0.0–1.0 |
| `dataset.json` | JSON array of `{"input": str, "answer": str}` — minimum 10 items; split 70/30 train/test deterministically |

### agent.py template

```python
import asyncio

MODEL = "openai/gpt-4o-mini"  # injected by benchmark — do not remove

CONCURRENT_REQUESTS = 5
DEPENDENCIES = []

SYSTEM_PROMPT = "Your system prompt here"


async def run_batch(inputs: list[str], api_key: str) -> list[str]:
    if not api_key:
        return ["unknown"] * len(inputs)

    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")
    semaphore = asyncio.Semaphore(CONCURRENT_REQUESTS)

    async def _call(inp: str) -> str:
        async with semaphore:
            response = await client.chat.completions.create(
                model=MODEL,
                temperature=0,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": inp},
                ],
            )
            return (response.choices[0].message.content or "").strip()

    return list(await asyncio.gather(*(_call(inp) for inp in inputs)))
```

### eval.py template

```python
import re

def _normalize(s: str) -> str:
    return re.sub(r"[.,;:!?\-]$", "", s.strip().lower())

def score(expected: str, predicted: str) -> float:
    exp = _normalize(expected)
    pred = _normalize(predicted)
    if exp == pred:
        return 1.0
    if exp in pred:
        return 0.5
    return 0.0
```

## Setup

Requires the `protege` CLI installed and on `PATH`. Run `/agent-finetuning:setup` once to install it and run `protege login`.

## Sub-Skills

| Skill | Slash | When to use |
|-------|-------|-------------|
| `agent-finetuning:smoke-test` | `/smoke-test` | Validate files + dry-run agent locally before any Studio call |
| `agent-finetuning:create-agent-finetuning` | `/create-agent-finetuning` | Submit a new optimization job (runs smoke-test first) |
| `agent-finetuning:monitor` | `/monitor` | Poll live iteration progress of a running job |
| `agent-finetuning:agent-finetuning-results` | `/agent-finetuning-results` | Fetch final results for a completed job |
| `agent-finetuning:agent-finetuning-list` | `/agent-finetuning-list` | List all optimization jobs |

## Job Parameters (`protege agent-finetuning run` flags)

| Flag | Type | Default | Notes |
|------|------|---------|-------|
| `--target-models` | comma-separated | — | 1–5 OpenRouter model strings |
| `--n-iterations` | int | 15 | 1–50 |
| `--overall-timeout` | int (seconds) | 3600 | |
| `--llm-call-timeout` | int (seconds) | 600 | |
| `--sandbox-timeout` | int (seconds) | 3600 | |
| `--enable-mcp` | flag | off | |
| `--force-baseline` | flag | off | Re-run baseline instead of using the cache |
| `--run-benchmark` | flag | off | Runs the Claude-Sonnet reference-solve benchmark phase |
| `--force-benchmark` | flag | off | Re-run the benchmark instead of using the cache |
| `--env-id` | string | — | Only used with `--input-url`; Task-based runs use the Task's own env |
| `--team-id` | string | — | |
| `--watch` | flag | off | Poll until the job reaches a terminal status |

## Reference Examples

| Benchmark | Description |
|-----------|-------------|
| `examples/gaia/` | General knowledge + tool use (python_interpreter) |
| `examples/finance_agent/` | Finance Q&A |
| `examples/trail/` | LLM trace classification |

## Trigger

Invoke this skill when the user says things like:
- "optimize my agent"
- "run agent-finetuning on my files"
- "improve my system prompt"
- "benchmark and improve my agent"
- `/agent-finetuning`

Then guide them to the right sub-skill based on what they need.
