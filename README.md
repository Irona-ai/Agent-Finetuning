# Agent-Finetuning

Agent-Finetuning skills by IronLabs — iterative Python agent optimization via E2B sandboxes and Claude proposer.

## Skills

| Skill | Description |
|-------|-------------|
| **agent-finetuning** | Overview + file format reference for agent.py, eval.py, and dataset.json |
| **smoke-test** | Validate files and dry-run agent locally before submitting a job |
| **create-agent-finetuning** | Submit a new optimization job (runs smoke-test first) |
| **monitor** | Poll live iteration progress of a running job |
| **agent-finetuning-results** | Fetch final results: scores, prompt diff, optimized agent code |
| **agent-finetuning-list** | List all optimization jobs |

## Installation

### Claude Code

1. Add the marketplace:

```bash
claude plugin marketplace add Irona-ai/Agent-Finetuning
```

2. Install the plugin:

```bash
claude plugin install agent-finetuning@Agent-Finetuning
```

3. Run setup to install the `protege` CLI and connect your IronLabs Studio account:

```
/agent-finetuning:setup
```

### OpenClaw

```bash
openclaw plugins install @ironlabs/agent-finetuning-plugin
```

## Requirements

These skills shell out to the `protege` CLI (a separate Python package, `protege-cli`).
`/agent-finetuning:setup` checks for it and walks you through installing it
(`pip install -e /path/to/protege-cli` — not yet published to PyPI) and running
`protege login`. Credentials are stored by the CLI at `~/.config/protege/config.json`,
not by this plugin.

## Examples

Pre-built examples in `examples/`:

| Benchmark | Description |
|-----------|-------------|
| `examples/gaia/` | General knowledge + tool use |
| `examples/finance_agent/` | Finance Q&A |
| `examples/trail/` | LLM trace classification |
