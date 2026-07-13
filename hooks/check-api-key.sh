#!/usr/bin/env bash
set -euo pipefail

COMMAND=$(cat | jq -r '.tool_input.command // empty')

# Only intercept IronLabs Studio API calls
if [[ "$COMMAND" != *"api/v1/agent-optimizer"* ]] && \
   [[ "$COMMAND" != *"api/v1/trainingjobs"* ]] && \
   [[ "$COMMAND" != *"api/v1/optimized-prompts"* ]]; then
  exit 0
fi

# Block if no API key
if [ -z "${IRONLABS_API_KEY:-}" ]; then
  jq -n '{ decision: "block", reason: "IRONLABS_API_KEY is not set. Run /agentopt:setup first." }'
  exit 0
fi

exit 0
