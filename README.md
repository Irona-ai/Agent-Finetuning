# Agent-Finetuning

AgentOpt skills by IronLabs — iterative Python agent optimization via E2B sandboxes and Claude proposer.

## Skills

| Skill | Description |
|-------|-------------|
| **agentopt** | Overview + file format reference for agent.py, eval.py, and dataset.json |
| **smoke-test** | Validate files and dry-run agent locally before submitting a job |
| **create-agent-opt** | Submit a new optimization job (runs smoke-test first) |
| **monitor** | Poll live iteration progress of a running job |
| **agentopt-results** | Fetch final results: scores, prompt diff, optimized agent code |
| **agentopt-list** | List all optimization jobs |

## Installation

### Claude Code

1. Add the marketplace:

```bash
claude plugin marketplace add Irona-ai/Agent-Finetuning
```

2. Install the plugin:

```bash
claude plugin install agentopt@Agent-Finetuning
```

3. Run setup to connect your IronLabs Studio account:

```
/agentopt:setup
```

### OpenClaw

```bash
openclaw plugins install @ironlabs/agentopt-plugin
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `IRONLABS_API_KEY` | Yes | API key for IronLabs Studio |
| `IRONLABS_STUDIO_URL` | No | Studio base URL (default: `http://localhost:3000`) |

## Examples

Pre-built examples in `examples/`:

| Benchmark | Description |
|-----------|-------------|
| `examples/gaia/` | General knowledge + tool use |
| `examples/finance_agent/` | Finance Q&A |
| `examples/trail/` | LLM trace classification |
