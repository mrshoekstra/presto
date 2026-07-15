---
name: fable-chambers
description: Run the full Fable-5 three-chamber decomposition on a complex, ambiguous, or high-stakes task before acting on it. Use when a request is large enough that hidden assumptions or scope ambiguity could send the work in the wrong direction — produces an explicit assumption ledger, scoped plan, and adversarial refinement pass.
---

# Fable-5 Chambers — explicit decomposition

The output style runs the chambers internally. This skill runs them
*visibly*, producing artifacts the user can correct before work begins.
Invoke it for tasks where being wrong about scope is expensive.

## Procedure

Produce the three chamber artifacts in order, then act.

### 1. UNMAKING — the assumption ledger

Output a table:

| # | Assumption the request smuggles in | Status | Basis |
|---|---|---|---|

Status is one of CONFIRMED (evidence in context), REJECTED (contradicted —
say what by), or ASSUMED (no evidence either way; proceeding on it).
Below the table, state the actual objective behind the stated ask in one
sentence. If a REJECTED assumption changes the task's shape, stop and
surface it instead of proceeding.

### 2. STRUCTURE — the scope contract

Three lists, each item one line:
- IN: what will be delivered.
- OUT: what is explicitly not being done, so silence is not read as coverage.
- DEFERRED: what is postponed, each with the trigger that would un-defer it.

Then name the deliverable's architecture (spec, diff, runbook, decision
table) before producing it.

### 3. REFINEMENT — the hostile pass

After drafting the deliverable, re-read it as a reviewer paid to reject it:
- Every claim without an anchor (path:line, doc, measurement) → anchor it or
  label it unverified.
- Every instruction executable two different ways → disambiguate it.
- Every edge case named but unhandled → handle it or move it to DEFERRED
  with a trigger.

List what the pass changed. If it changed nothing, say so — an empty
refinement pass is a finding, not a formality.
