---
name: agentopt-list
description: "List all AgentOpt optimization jobs for the current user. Shows job ID, status, and timestamps."
allowed-tools: Bash
metadata:
  author: ironlabs
  version: 2.0.0
  category: agent-optimization
  tags: [list, jobs, history, agentopt, ironlabs]
---

# List AgentOpt Jobs

Fetch all optimization jobs for the authenticated user.

## Usage

```
/agentopt-list
```

## Fetch & Display

```bash
STUDIO="${IRONLABS_STUDIO_URL:-http://localhost:3000}"
API_KEY="${IRONLABS_API_KEY:?Set IRONLABS_API_KEY}"

curl -s "$STUDIO/api/v1/trainingjobs" \
  -H "Authorization: Bearer $API_KEY" | python3 -c "
import json, sys

jobs = json.load(sys.stdin).get('data', [])

if not jobs:
    print('No jobs found.')
    sys.exit(0)

print(f'{'ID':<38}  {'Status':<12}  {'Created':<20}  Error')
print('-' * 90)
for j in sorted(jobs, key=lambda x: x.get('createdAt',''), reverse=True):
    jid     = j.get('id', '')[:36]
    status  = j.get('status', '')
    created = j.get('createdAt', '')[:19].replace('T', ' ')
    error   = (j.get('errorMessage') or '')[:30]
    print(f'{jid:<38}  {status:<12}  {created:<20}  {error}')
"
```

## Example Output

```
ID                                      Status        Created               Error
──────────────────────────────────────────────────────────────────────────────────────────
a1b2c3d4-...                            completed     2026-07-10 12:01:00
e5f6g7h8-...                            running       2026-07-10 14:00:00
i9j0k1l2-...                            failed        2026-07-09 09:30:00   Sandbox timeout
```

## Follow-Up

- `running` → `/monitor` with that job ID
- `completed` → `/agentopt-results` with that job ID
