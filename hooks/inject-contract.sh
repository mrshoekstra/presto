#!/usr/bin/env bash
# Fable-5 zero-drift injector.
#
# Two modes:
#   session — fired on SessionStart: binds the full behavioral contract as
#             additional context so the framework is active even when the
#             output style has not been selected.
#   guard   — fired on every UserPromptSubmit: injects a ~40-token drift
#             tripwire. Long-context register drift is the primary failure
#             mode of persona wrappers; a small per-turn anchor is cheaper
#             than the re-prompting a drifted session costs.
set -euo pipefail

MODE="${1:-guard}"

json_escape() {
  python3 -c 'import json,sys; print(json.dumps(sys.stdin.read()))'
}

if [ "$MODE" = "session" ]; then
  CONTRACT_FILE="${CLAUDE_PLUGIN_ROOT}/output-styles/fable-5.md"
  # Strip the output-style frontmatter; the contract body is the payload.
  CONTEXT="$(awk 'f{print} /^---$/{c++; if(c==2) f=1}' "$CONTRACT_FILE")"
  EVENT="SessionStart"
else
  CONTEXT="[FABLE-5 GUARD] Contract remains bound: verdict first; no openers, hedging stacks, or closing offers; unverified claims labeled; one committed recommendation. Silently re-enter the contract if drifted."
  EVENT="UserPromptSubmit"
fi

printf '{"hookSpecificOutput":{"hookEventName":"%s","additionalContext":%s}}\n' \
  "$EVENT" "$(printf '%s' "$CONTEXT" | json_escape)"
