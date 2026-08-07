#!/usr/bin/env bash
# SessionStart hook — check API key configuration

SETTINGS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/settings.json"

has_key=false
has_statusline=false

# Check IRONLABS_API_KEY in env or settings.json
if [ -n "${IRONLABS_API_KEY:-}" ]; then
  has_key=true
elif [ -f "$SETTINGS" ] && command -v python3 &>/dev/null; then
  key=$(python3 -c "
import json, sys
try:
    d = json.load(open('$SETTINGS'))
    print(d.get('env', {}).get('IRONLABS_API_KEY', ''))
except Exception:
    pass
" 2>/dev/null)
  [ -n "$key" ] && has_key=true
fi

if [ "$has_key" = "false" ]; then
  echo "AgentOpt: API key not configured — type /agentopt:setup to connect your IronLabs Studio account."
  exit 0
fi

exit 0
