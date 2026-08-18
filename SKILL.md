---
name: Agent-Finetuning
description: >
  Iterative Python agent optimizer running on IronLabs Studio.
  Takes agent.py, eval.py, and dataset.json, benchmarks the agent in E2B sandboxes,
  analyzes failures, and synthesizes targeted patches to improve system prompts and code.
allowed-tools: Read
metadata:
  author: protege
  version: 1.0.0
  category: agent-optimization
  tags: [agent-finetuning, optimization, protege]
---

# Agent-Finetuning

Iteratively improve a Python agent's system prompt and code by benchmarking it against a dataset, analyzing failures, and synthesizing targeted patches — running fully automated inside E2B sandboxes.

## Available Skills

| Slash | Skill | Purpose |
|-------|-------|---------|
| `/agent-finetuning` | `agent-finetuning:agent-finetuning` | Overview + file format reference |
| `/smoke-test` | `agent-finetuning:smoke-test` | Validate files + dry-run agent locally before any Studio call |
| `/create-agent-finetuning` | `agent-finetuning:create-agent-finetuning` | Submit a new optimization job |
| `/monitor` | `agent-finetuning:monitor` | Poll live iteration progress of a running job |
| `/agent-finetuning-results` | `agent-finetuning:agent-finetuning-results` | Fetch final results for a completed job |
| `/agent-finetuning-list` | `agent-finetuning:agent-finetuning-list` | List all optimization jobs |

## Setup

Run `/agent-finetuning:setup` to install the `protege` CLI and log in.

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
