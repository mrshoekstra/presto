#!/usr/bin/env bash
# Dev-time generator: pre-builds the hook stdout payloads so the runtime
# hook command is a bare `cat` with zero dependencies. Payloads are plain
# text — a documented valid context-injection format for SessionStart and
# UserPromptSubmit — so the mode file and the default payload can be
# concatenated by two sequential cats without corrupting a JSON parse.
# Run this after every edit to output-styles/fable-5.md and commit the
# regenerated payloads.
set -euo pipefail
cd "$(dirname "$0")/.."

mkdir -p hooks/payloads

python3 - <<'EOF'
from pathlib import Path

contract = Path("output-styles/fable-5.md").read_text().split("---", 2)[2].strip()

guard = (
    "[FABLE-5 GUARD] Bound: verdict first; no openers, hedging, or closing "
    "offers; label unverified; one committed recommendation; depth matches "
    "stakes. Re-enter silently if drifted."
)

mode_fable = "[FABLE-5 MODE] FABLE profile active (default register)."

mode_mythos = (
    "[FABLE-5 MODE] MYTHOS profile active (set via /fable-mode): maximum "
    "register intensity — strip every non-load-bearing word; the verdict "
    "may stand alone when rationale adds nothing; absolute conviction "
    "within what the evidence supports. Register only: the pipeline, "
    "evidence gate, invariants, and all safety/refusal/honesty norms are "
    "unchanged."
)

out = Path("hooks/payloads")
(out / "session.txt").write_text(contract + "\n")
(out / "guard.txt").write_text(guard + "\n")
(out / "mode-fable.txt").write_text(mode_fable + "\n")
(out / "mode-mythos.txt").write_text(mode_mythos + "\n")
print("payloads regenerated")
EOF
