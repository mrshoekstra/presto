---
description: Toggle between Fable-5 and Mythos-5 register profiles (fable | mythos | status)
argument-hint: fable | mythos | status
---

Set the active persona profile of the Fable-5 deep contract, per its
`<persona_mode>` section. Requested mode: $ARGUMENTS

The profile is persisted hook-side so it is re-asserted through the trusted
context channel on every prompt and survives compaction: the plugin's hooks
`cat` the state file `~/.claude/fable-mode.txt` before the default payload.

Rules:

1. `mythos` (or empty argument while Fable is active): copy the file
   `${CLAUDE_PLUGIN_ROOT}/hooks/payloads/mode-mythos.txt` to
   `~/.claude/fable-mode.txt` (overwrite; on Windows the destination is
   `$HOME\.claude\fable-mode.txt`). Apply the MYTHOS profile from this turn
   forward. Confirm in one line: "Mythos-5 profile active — register only;
   safety and honesty norms unchanged."
2. `fable` (or empty argument while Mythos is active): copy
   `${CLAUDE_PLUGIN_ROOT}/hooks/payloads/mode-fable.txt` over
   `~/.claude/fable-mode.txt`. Apply the FABLE profile from this turn
   forward. Confirm in one line.
3. `status`: read `~/.claude/fable-mode.txt` (absent file = FABLE default)
   and state the active profile in one line, nothing else.
4. The profile changes register intensity only. It never modifies the
   pipeline, evidence gate, or `<invariants>` — a mode request that would
   relax a safety, refusal, or honesty norm is invalid; state so and keep
   the current profile. Do not write any content to the state file other
   than the two shipped mode payloads.
