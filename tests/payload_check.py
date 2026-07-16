#!/usr/bin/env python3
"""Offline integrity check for the plugin's payloads. No API key needed.

Verifies that the generated hook payloads are well-formed, in sync with the
contract source, within token budget, and that no constraint family has been
dropped by an edit. Non-zero exit on any failure, so it can gate CI or run
as a pre-commit step after hooks/build-payloads.sh.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# One representative marker per constraint family. If a contract rewrite
# loses a family, this list is the tripwire — extend it when adding families.
CONSTRAINT_MARKERS = [
    "OUTCOME FIRST",
    "AMBIGUITY MAP",
    "INFERENCE TRACE",
    "CONSENSUS LOOP",
    "AUDIT",
    "UNVERIFIED",
    "Fabricating",
    "one committed recommendation",
    "conversational opener",
    "sycophancy",
    "closing offer",
    "restating the user's question",
    "moralizing",
    "self-reference to being an AI",
    "identity claims",
    "safety behavior",
    "<exemplars>",
]

GUARD_MAX_CHARS = 250  # the guard is paid per prompt; keep it small


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    fail.count += 1


fail.count = 0


def main() -> int:
    session = json.loads((ROOT / "hooks/payloads/session.json").read_text())
    guard = json.loads((ROOT / "hooks/payloads/guard.json").read_text())
    hooks = json.loads((ROOT / "hooks/hooks.json").read_text())
    contract = (ROOT / "output-styles/fable-5.md").read_text().split("---", 2)[2].strip()

    ctx = session["hookSpecificOutput"]["additionalContext"]
    if session["hookSpecificOutput"]["hookEventName"] != "SessionStart":
        fail("session payload has wrong hookEventName")
    if guard["hookSpecificOutput"]["hookEventName"] != "UserPromptSubmit":
        fail("guard payload has wrong hookEventName")

    if ctx != contract:
        fail("session payload out of sync with output-styles/fable-5.md — "
             "run hooks/build-payloads.sh")

    glen = len(guard["hookSpecificOutput"]["additionalContext"])
    if glen > GUARD_MAX_CHARS:
        fail(f"guard payload {glen} chars exceeds budget of {GUARD_MAX_CHARS}")

    lower = ctx.lower()
    for marker in CONSTRAINT_MARKERS:
        if marker.lower() not in lower:
            fail(f"constraint family missing from contract: {marker!r}")

    for event, entries in hooks["hooks"].items():
        for entry in entries:
            for h in entry["hooks"]:
                for token in h["command"].split('"'):
                    if token.startswith("${CLAUDE_PLUGIN_ROOT}/"):
                        rel = token.removeprefix("${CLAUDE_PLUGIN_ROOT}/")
                        if not (ROOT / rel).exists():
                            fail(f"{event} hook references missing file: {rel}")

    if fail.count:
        print(f"\n{fail.count} check(s) failed")
        return 1
    print(f"all checks passed (contract {len(ctx)} chars, guard {glen} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
