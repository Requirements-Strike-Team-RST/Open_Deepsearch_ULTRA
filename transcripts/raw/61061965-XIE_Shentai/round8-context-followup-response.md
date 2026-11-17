# Reconciliation of G1–G5

No tools were used. No runtime PASS, no approval.

## G1 — Stale trim indices after a successful trim — **RETAINED (risk, not demonstrated bug)**

- **Source-supported part:** `plan_trim` receives `instruction_index` and returns `ResearchTurn.index` values, but the recovery loop reuses the same call for a *shorter* list after a trim. Nothing in the proposed interface says indices are recomputed or rebased.
- **Retracted:** my earlier claim "factually impossible" (introduced as a demonstrated defect). Context has **no implemented `recovery.py`** in this baseline, so this is a design-seam risk, not an observed bug.
- **Remaining issue:** the contract must say explicitly that after each trim the instruction is re-located and turn indices are relative to the list just passed in. This stays an open integration requirement for the context owner to resolve; orchestration cannot assume it is already handled.

## G2 — Attempt counting — **RETRACTED**

My reading of the loop was wrong. `attempt = 0; while attempt < 3: attempt += 1` on exception gives failure/failure/success = **3 model calls**, which matches "at most three attempts". Success counting does not imply two calls. No budget mismatch exists.

## G3 — Parse frequency — **PARTLY RETRACTED, RETAINED NARROWLY**

- **Retracted:** "the parser might run per attempt in a second LLM pass" and "body can leak into notes when the consumer hunk is unchanged." The new text says parsing occurs **exactly once after the selected recovery path returns a successful string**, and `render_supervisor_result` explicitly never becomes report findings.
- **Also retracted:** my claim that ORC-044–046 were absent. They are now planned.
- **RETAINED as an unresolved integration issue:** the raw consumer hunk (L310) and off/on are still **declared reader decisions**, not resolved contracts. Two conditional edits to the same delivery line remain a coordination risk, and R-09's single-owner assignment is still pending. This is not a contradiction, only an open hand-off.

## G4 — Evidence at the failure mapping — **RETRACTED**

The new node-retained evidence map plus "the node saves strong local references before calling recovery and maps outside the clean context" fully answers this. `compress_with_recovery` needs **no** `evidence` parameter; the helper returns success or a typed exception to a node that still holds the receipt. For off/on, the absence of a TaskSpec and RunRecord is a **declared** decision; the ordinary runtime-exception category on that combination remains an **open context/delivery policy**, which I keep as such.

## G5 — Precision wording and the baseline overclaim — **RETRACTED (both parts)**

- Default `0.8` → `Fraction("4/5")` is exact. A caller supplying `0.1 + 0.7` has supplied `0.7999999999999999`, a **different configured value**; rounding to one decimal would be wrong. My "0.1 + 0.7 equals threshold" case was invalid.
- **Retracted:** "propagates as today" as a factual error. The baseline **swallowed** ordinary exceptions and fell through to the placeholder. The ADR wording was loose, not contradicted by the new text.
- **Retained correction to my own row 6:** the concrete coverage case (T1 Q1–Q8; T2 Q9 of Q9/Q10; T3 failed repeats Q1 → distinct 9/10, global unanswered `[Q10]`, T3 local `[Q1]`, delivery `partial` despite `covered`, task count 3 ≠ coverage) is fully consistent with `must_answer`/`findings.answers`, `TaskResult.unanswered()` and `RunRecord.unanswered_questions()`. No new serialized field is needed.

## Verdict

- **Real unresolved integration items:** G1 (trim-index contract must be pinned), G3's narrow part (single owner of the shared consumer hunk; off/on runtime category).
- **Retracted:** G2, G4, most of G3, and all of G5.
- All remaining items are design-level and PLANNED/NOT_RUN. No test gate or human approval exists.
