---
name: monitor
description: "Poll a running AgentOpt job and display live status: started, completed, error. Use after /create-agent-opt to watch the optimization loop."
allowed-tools: Bash
metadata:
  author: ironlabs
  version: 2.0.0
  category: agent-optimization
  tags: [monitor, poll, status, agentopt, ironlabs]
---

# Monitor AgentOpt Job

Poll `GET /api/v1/trainingjobs` every 30 seconds, filter by `job_id`, and display live status until the job reaches a terminal state.

## Usage

```
/monitor [job_id]
```

If `job_id` is not provided, ask the user for it.

## Poll Loop

```bash
JOB_ID="${JOB_ID:?Provide job_id}"
STUDIO="${IRONLABS_STUDIO_URL:-http://localhost:3000}"
API_KEY="${IRONLABS_API_KEY:?Set IRONLABS_API_KEY}"

while true; do
  JOBS=$(curl -s "$STUDIO/api/v1/trainingjobs" \
    -H "Authorization: Bearer $API_KEY")

  python3 - "$JOB_ID" <<'EOF'
import json, sys

jobs = json.load(sys.stdin).get("data", [])
job_id = sys.argv[1]

job = next((j for j in jobs if j["id"] == job_id), None)
if not job:
    print(f"Job {job_id} not found.")
    sys.exit(1)

state    = job.get("status", "unknown")
started  = (job.get("startedAt") or "—")[:19]
completed = (job.get("completedAt") or "—")[:19]
error    = job.get("errorMessage", "")

print(f"[{(job.get('updatedAt') or '')[:19]}] status={state}")
print(f"  started:   {started}")
if completed != "—":
    print(f"  completed: {completed}")
if error:
    print(f"  error:     {error}")
EOF

  STATE=$(echo "$JOBS" | python3 -c "
import json, sys
jobs = json.load(sys.stdin).get('data', [])
job = next((j for j in jobs if j['id'] == '$JOB_ID'), None)
print(job['status'] if job else 'not_found')
")

  case "$STATE" in
    completed|partial|interrupted|failed|not_found) break ;;
  esac

  sleep 30
done

echo ""
echo "Job $STATE. Run /agentopt-results to fetch results."
```

## Status Values

| Status | Meaning |
|--------|---------|
| `queued` | Waiting to start |
| `running` | Optimization loop active |
| `completed` | Finished successfully |
| `partial` | Some models succeeded, some failed |
| `interrupted` | Timed out |
| `failed` | Fatal error — check `errorMessage` |

## TrainingJob Fields

| Field | Description |
|-------|-------------|
| `id` | Job ID (matches `job_id` from `/create-agent-opt`) |
| `status` | Current job status |
| `startedAt` | When execution began |
| `completedAt` | When execution ended |
| `errorMessage` | Error detail if failed |
| `createdAt` | When job was queued |
