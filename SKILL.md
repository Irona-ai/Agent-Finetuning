---
name: AgentOpt
description: >
  Iterative Python agent optimizer running on IronLabs Studio.
  Takes agent.py, eval.py, and dataset.json, benchmarks the agent in E2B sandboxes,
  analyzes failures, and synthesizes targeted patches to improve system prompts and code.
allowed-tools: Read
metadata:
  author: ironlabs
  version: 1.0.0
  category: agent-optimization
  tags: [agentopt, optimization, ironlabs]
---

# AgentOpt

Iteratively improve a Python agent's system prompt and code by benchmarking it against a dataset, analyzing failures, and synthesizing targeted patches — running fully automated inside E2B sandboxes.

## Available Skills

| Slash | Skill | Purpose |
|-------|-------|---------|
| `/agentopt` | `agentopt:agentopt` | Overview + file format reference |
| `/smoke-test` | `agentopt:smoke-test` | Validate files + dry-run agent locally before any Studio call |
| `/create-agent-opt` | `agentopt:create-agent-opt` | Submit a new optimization job |
| `/monitor` | `agentopt:monitor` | Poll live iteration progress of a running job |
| `/agentopt-results` | `agentopt:agentopt-results` | Fetch final results for a completed job |
| `/agentopt-list` | `agentopt:agentopt-list` | List all optimization jobs |

## Setup

Run `/agentopt:setup` to configure `IRONLABS_API_KEY` and `IRONLABS_STUDIO_URL`.

## Required Files

| File | Contract |
|------|----------|
| `agent.py` | `async def run_batch(inputs: list[str], api_key: str) -> list[str]` |
| `eval.py` | `def score(expected: str, predicted: str) -> float` returning 0.0–1.0 |
| `dataset.json` | JSON array of `{"input": str, "answer": str}` — minimum 10 items |

## Reference Examples

| Benchmark | Description |
|-----------|-------------|
| `examples/gaia/` | General knowledge + tool use |
| `examples/finance_agent/` | Finance Q&A |
| `examples/trail/` | LLM trace classification |
