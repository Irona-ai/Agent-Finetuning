#!/usr/bin/env bash
# SessionStart hook — check protege CLI is installed and logged in

CONFIG="${PROTEGE_CONFIG_DIR:-$HOME/.config/protege}/config.json"

if ! command -v protege &>/dev/null; then
  echo "Agent-Finetuning: protege CLI not found — type /agent-finetuning:setup to install it."
  exit 0
fi

if [ ! -f "$CONFIG" ]; then
  echo "Agent-Finetuning: not logged in — type /agent-finetuning:setup to connect your IronLabs Studio account."
  exit 0
fi

exit 0
