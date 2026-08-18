---
name: agent-finetuning-list
description: "List all Agent-Finetuning optimization jobs for the current user. Shows job ID, status, and timestamps."
allowed-tools: Bash
metadata:
  author: protege
  version: 2.0.0
  category: agent-optimization
  tags: [list, jobs, history, agent-finetuning, protege]
---

# List Agent-Finetuning Jobs

Fetch all optimization jobs for the authenticated user, most recent first.

## Usage

```
/agent-finetuning-list
```

## Fetch & Display

```bash
protege agent-finetuning jobs
```

Each line is `<job_id>  <status>  <createdAt>` with a trailing `error=<message>` when
the job failed.

## Follow-Up

- `running` → `/monitor` with that job ID
- `completed` → `/agent-finetuning-results` with that job ID
