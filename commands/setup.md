---
name: agentopt:setup
description: Connect your IronLabs Studio account by configuring IRONLABS_API_KEY and IRONLABS_STUDIO_URL
allowed-tools: Bash, Read, Edit, Write
---

# AgentOpt Setup

Configure your IronLabs Studio credentials so all agentopt skills can authenticate.

## Step 1 — Check existing config

```bash
SETTINGS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json"

python3 -c "
import json, os
settings_path = os.path.expandvars('${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json')
try:
    d = json.load(open(settings_path))
    env = d.get('env', {})
    key = env.get('IRONLABS_API_KEY', '')
    url = env.get('IRONLABS_STUDIO_URL', '')
    if key:
        print(f'IRONLABS_API_KEY: {key[:8]}...{key[-4:]} (already set)')
    else:
        print('IRONLABS_API_KEY: not set')
    if url:
        print(f'IRONLABS_STUDIO_URL: {url} (already set)')
    else:
        print('IRONLABS_STUDIO_URL: not set (will default to http://localhost:3000)')
except FileNotFoundError:
    print('settings.json not found — will create')
"
```

## Step 2 — Get your API key

1. Open your IronLabs Studio instance
2. Go to Settings → API Keys
3. Create or copy an existing key (starts with `sk-`)

Ask the user to paste their API key. **Do not log or echo it.**

## Step 3 — Set IRONLABS_STUDIO_URL (optional)

Ask: "What is your Studio URL? (press Enter for default: `http://localhost:3000`)"

Typical values:
- Local dev: `http://localhost:3000`
- Production: `https://stg-studio.irona.ai/` (or your custom domain)

## Step 4 — Save to settings.json

```bash
SETTINGS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json"
API_KEY="<from user>"
STUDIO_URL="${STUDIO_URL:-http://localhost:3000}"

python3 - <<'EOF'
import json, os, sys

settings_path = os.path.expandvars(os.environ.get("SETTINGS", os.path.expanduser("~/.claude/settings.json")))
api_key = os.environ["API_KEY"]
studio_url = os.environ["STUDIO_URL"]

try:
    with open(settings_path) as f:
        d = json.load(f)
except FileNotFoundError:
    d = {}

d.setdefault("env", {})
d["env"]["IRONLABS_API_KEY"] = api_key
d["env"]["IRONLABS_STUDIO_URL"] = studio_url

with open(settings_path, "w") as f:
    json.dump(d, f, indent=2)

print(f"Saved to {settings_path}")
EOF
```

## Step 5 — Verify connection

```bash
STUDIO="${IRONLABS_STUDIO_URL:-http://localhost:3000}"
API_KEY="${IRONLABS_API_KEY}"

curl -s "$STUDIO/api/v1/trainingjobs" \
  -H "Authorization: Bearer $API_KEY" | python3 -c "
import json, sys
try:
    d = json.load(sys.stdin)
    jobs = d.get('data', [])
    print(f'Connection OK — Studio responded. {len(jobs)} job(s) found.')
except Exception as e:
    print(f'Connection check failed: {e}')
    print('Verify IRONLABS_STUDIO_URL is correct and Studio is running.')
"
```

## Done

Configuration saved. Start optimizing:

- `/smoke-test` — validate agent.py / eval.py / dataset.json locally
- `/create-agent-opt` — submit your first optimization job
- `/agentopt-list` — see existing jobs
