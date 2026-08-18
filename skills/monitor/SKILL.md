---
name: monitor
description: "Poll a running Agent-Finetuning job and display live status: started, completed, error. Use after /create-agent-finetuning to watch the optimization loop."
allowed-tools: Bash
metadata:
  author: protege
  version: 2.0.0
  category: agent-optimization
  tags: [monitor, poll, status, agent-finetuning, protege]
---

# Monitor Agent-Finetuning Job

Poll `protege agent-finetuning status <job_id>` every 30 seconds and display live status
until the job reaches a terminal state.

Tip: `protege agent-finetuning run --watch` does this automatically right after launch —
this skill is for watching a job that's already running.

## Usage

```
/monitor [job_id]
```

If `job_id` is not provided, ask the user for it.

## Poll Loop

```bash
JOB_ID="${JOB_ID:?Provide job_id}"

while true; do
  OUT=$(protege agent-finetuning status "$JOB_ID")
  echo "$OUT"

  STATE=$(echo "$OUT" | sed -n "s/^Job $JOB_ID: //p")

  case "$STATE" in
    completed|partial|interrupted|failed|"") break ;;
  esac

  sleep 30
done

echo ""
echo "Job $STATE. Run /agent-finetuning-results to fetch results."
```

## Status Values

| Status | Meaning |
|--------|---------|
| `queued` | Waiting to start |
| `running` | Optimization loop active |
| `completed` | Finished successfully |
| `partial` | Some models succeeded, some failed |
| `interrupted` | Timed out |
| `failed` | Fatal error, or job ID not found |

The CLI's `status` command prints one line per target model with its latest
iteration and score (`<model>: iteration=<n> score=<s>`) below the job status line —
more detail (timestamps, error messages) is only available via `/agent-finetuning-results`
or the Studio UI, not this command.
