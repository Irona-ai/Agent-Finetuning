---
name: agent-finetuning:setup
description: Install the protege CLI (if needed) and log in so all agent-finetuning skills can authenticate
allowed-tools: Bash, Read, Edit, Write
---

# Agent-Finetuning Setup

Configure the `protege` CLI so all agent-finetuning skills can authenticate against IronLabs Studio.

## Step 1 — Check the CLI is installed

```bash
if ! command -v protege &>/dev/null; then
  echo "protege CLI not found on PATH."
  echo "Install it from a local checkout of the protege-cli repo:"
  echo "  pip install -e /path/to/protege-cli"
  exit 1
fi
protege --help >/dev/null && echo "protege CLI found."
```

If it's missing, help the user install it before continuing.

## Step 2 — Check existing login

```bash
CONFIG="${PROTEGE_CONFIG_DIR:-$HOME/.config/protege}/config.json"
if [ -f "$CONFIG" ]; then
  echo "Already logged in (config at $CONFIG)."
else
  echo "Not logged in yet."
fi
```

## Step 3 — Get the API key

1. Open your IronLabs Studio instance
2. Go to Settings → API Keys
3. Create or copy an existing key

Ask the user to paste their API key. **Do not log or echo it.**

## Step 4 — Log in

```bash
protege login --api-key "$API_KEY"
```

Only pass `--base-url` if the user wants a non-default deployment (the CLI already
defaults to IronLabs Studio's production URL):

```bash
protege login --api-key "$API_KEY" --base-url "$STUDIO_URL"
```

## Step 5 — Verify connection

```bash
protege agent-finetuning jobs
```

If this lists jobs (or prints "No jobs found.") without an auth error, the login worked.

## Done

Configuration saved. Start optimizing:

- `/smoke-test` — validate agent.py / eval.py / dataset.json locally
- `/create-agent-finetuning` — submit your first optimization job
- `/agent-finetuning-list` — see existing jobs
