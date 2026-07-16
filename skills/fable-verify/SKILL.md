---
name: fable-verify
description: Walk the Fable-5 evidence gate visibly before declaring substantial work done. Use when about to report a nontrivial change, fix, or conclusion as complete — produces an anchored verification table proving each claim was exercised, not assumed, and downgrades anything unproven to unverified before it reaches the user.
---

# Fable-5 Verify — the evidence gate, made visible

The contract's S4 audit runs internally. This skill runs the completion
check *visibly*, so "done" arrives with its proof attached. Invoke it
before reporting substantial work complete — a code change, a fix, a
migration, a diagnosis acted upon.

## Procedure

### 1. Enumerate the claims

List every claim the completion report is about to make, one line each.
"The hook now fires on Windows", "tests pass", "the payload is in sync" —
anything the user would take as fact.

### 2. Exercise each claim

For each claim, run the check that would expose it if false — execute the
command, drive the affected flow, read the artifact. Static inspection
counts only when execution is impossible from here. Fill the table:

| # | Claim | How exercised | Evidence (anchored) | Status |
|---|---|---|---|---|

Status is one of:
- PROVEN — exercised, observed, evidence anchored (path:line, command
  output quoted).
- UNVERIFIED — could not be exercised from here; state the exact command
  or action that would prove it, and who can run it.
- FAILED — exercised and the claim is false. A FAILED row blocks the
  completion report: fix it or rewrite the report around the failure.

### 3. Report with the gate applied

The completion report may assert only PROVEN rows as fact. UNVERIFIED rows
appear labeled as such with their pending test. FAILED rows appear as
failures with output quoted verbatim — never smoothed into success
language. An all-PROVEN table is the only state in which unqualified
"done" is permitted.
