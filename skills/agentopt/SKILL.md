---
name: agentopt
description: "IronLabs AgentOpt overview — iterative Python agent optimizer. Invokes sub-skills for smoke-testing, job creation, monitoring, and result retrieval. Use when user wants to optimize an agent's system prompt or code against a benchmark."
allowed-tools: Read
metadata:
  author: ironlabs
  version: 2.0.0
  category: agent-optimization
  tags: [agentopt, optimization, llm, benchmark, e2b, skillopt, ironlabs]
---

# AgentOpt

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

**SkillOpt** (default when `minibatchSize > 1`): splits failures into mini-batches, calls DeepSeek/OpenRouter to generate structured edit patches per batch, merges hierarchically, ranks by impact, applies top edits. Faster and more targeted than full-context improvement.

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

## Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `IRONLABS_API_KEY` | Yes | — | Bearer token for Studio API |
| `IRONLABS_STUDIO_URL` | No | `http://localhost:3000` | Studio base URL |

## Sub-Skills

| Skill | Slash | When to use |
|-------|-------|-------------|
| `agentopt:smoke-test` | `/smoke-test` | Validate files + dry-run agent locally before any Studio call |
| `agentopt:create-agent-opt` | `/create-agent-opt` | Submit a new optimization job (runs smoke-test first) |
| `agentopt:monitor` | `/monitor` | Poll live iteration progress of a running job |
| `agentopt:agentopt-results` | `/agentopt-results` | Fetch final results for a completed job |
| `agentopt:agentopt-list` | `/agentopt-list` | List all optimization jobs |

## Job Parameters

| Field | Type | Default | Range |
|-------|------|---------|-------|
| `target_models` | string[] | — | 1–5 OpenRouter model strings |
| `n_iterations` | int | 15 | 1–50 |
| `overall_timeout_seconds` | int | 3600 | 300–7200 |
| `llm_call_timeout_seconds` | int | 600 | 30–600 |
| `sandbox_timeout_seconds` | int | 3600 | 60–7200 |
| `minibatch_size` | int | 3 | ≥1 — batch size for SkillOpt; set to 1 to use standard mode |
| `edit_budget` | int | 5 | Max edits to apply per iteration |

## Reference Examples

| Benchmark | Description |
|-----------|-------------|
| `examples/gaia/` | General knowledge + tool use (python_interpreter) |
| `examples/finance_agent/` | Finance Q&A |
| `examples/trail/` | LLM trace classification |

## Trigger

Invoke this skill when the user says things like:
- "optimize my agent"
- "run agentopt on my files"
- "improve my system prompt"
- "benchmark and improve my agent"
- `/agentopt`

Then guide them to the right sub-skill based on what they need.
