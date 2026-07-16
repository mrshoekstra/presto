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
    "<persona_mode",
    "MYTHOS",
    "never relaxes any safety, refusal, or honesty norm",
]

GUARD_MAX_CHARS = 250   # the guard is paid per prompt; keep it small
MODE_MAX_CHARS = 500    # mode payloads are also paid per prompt when active


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    fail.count += 1


fail.count = 0


def main() -> int:
    payloads = ROOT / "hooks/payloads"
    contract = (ROOT / "output-styles/fable-5.md").read_text().split("---", 2)[2].strip()

    session = (payloads / "session.txt").read_text().strip()
    guard = (payloads / "guard.txt").read_text().strip()
    mode_fable = (payloads / "mode-fable.txt").read_text().strip()
    mode_mythos = (payloads / "mode-mythos.txt").read_text().strip()

    if session != contract:
        fail("session payload out of sync with output-styles/fable-5.md — "
             "run hooks/build-payloads.sh")

    if len(guard) > GUARD_MAX_CHARS:
        fail(f"guard payload {len(guard)} chars exceeds budget of {GUARD_MAX_CHARS}")

    for name, mode in (("mode-fable", mode_fable), ("mode-mythos", mode_mythos)):
        if len(mode) > MODE_MAX_CHARS:
            fail(f"{name} payload {len(mode)} chars exceeds budget of {MODE_MAX_CHARS}")
        if not mode.startswith("[FABLE-5 MODE]"):
            fail(f"{name} payload missing [FABLE-5 MODE] prefix")

    if "safety/refusal/honesty norms are unchanged" not in mode_mythos.replace("\n", " "):
        fail("mode-mythos payload missing the safety-unchanged clause")

    lower = contract.lower()
    for marker in CONSTRAINT_MARKERS:
        if marker.lower() not in lower:
            fail(f"constraint family missing from contract: {marker!r}")

    hooks = json.loads((ROOT / "hooks/hooks.json").read_text())
    for event, entries in hooks["hooks"].items():
        for entry in entries:
            for h in entry["hooks"]:
                for token in h["command"].split('"'):
                    if token.startswith("${CLAUDE_PLUGIN_ROOT}/"):
                        rel = token.removeprefix("${CLAUDE_PLUGIN_ROOT}/")
                        if not (ROOT / rel).exists():
                            fail(f"{event} hook references missing file: {rel}")
                # The ${HOME}/.claude/fable-mode.txt reference is runtime
                # user state and intentionally optional — not checked here.

    if fail.count:
        print(f"\n{fail.count} check(s) failed")
        return 1
    print(f"all checks passed (contract {len(contract)} chars, guard {len(guard)} chars, "
          f"mode payloads {len(mode_fable)}/{len(mode_mythos)} chars)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
