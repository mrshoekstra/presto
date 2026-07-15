#!/usr/bin/env bash
# Dev-time generator: pre-builds the hook stdout payloads so the runtime
# hook command is a bare `cat` with zero dependencies (no bash logic, no
# python3, no awk on the user's machine). Run this after every edit to
# output-styles/fable-5.md and commit the regenerated payloads.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p hooks/payloads

python3 - <<'EOF'
import json
from pathlib import Path

contract = Path("output-styles/fable-5.md").read_text().split("---", 2)[2].strip()
guard = (
    "[FABLE-5 GUARD] Bound: verdict first; no openers, hedging, or closing "
    "offers; label unverified; one committed recommendation; depth matches "
    "stakes. Re-enter silently if drifted."
)

def payload(event, context):
    return json.dumps(
        {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}},
        ensure_ascii=False,
    ) + "\n"

Path("hooks/payloads/session.json").write_text(payload("SessionStart", contract))
Path("hooks/payloads/guard.json").write_text(payload("UserPromptSubmit", guard))
print("payloads regenerated")
EOF
