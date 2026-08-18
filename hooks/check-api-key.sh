#!/usr/bin/env bash
set -euo pipefail

COMMAND=$(cat | jq -r '.tool_input.command // empty')

if [[ "$COMMAND" != *"protege agent-finetuning"* ]]; then
  exit 0
fi

CONFIG="${PROTEGE_CONFIG_DIR:-$HOME/.config/protege}/config.json"
if [ ! -f "$CONFIG" ]; then
  jq -n '{ decision: "block", reason: "Not logged in to protege. Run /agent-finetuning:setup first." }'
  exit 0
fi

exit 0
