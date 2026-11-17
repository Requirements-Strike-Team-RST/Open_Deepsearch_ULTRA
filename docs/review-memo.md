# Review Memo

> **Purpose:** Records of SA Reviews (Gate 1), pull request reviews (Gate 3) and the human reviews named in a requirement's fit criterion (`automated: false` checks).
> **Maintained by:** reviewers.
> **Last updated:** 2026-11-12

## SA Review Template

### SA-NNN: <scope, e.g. architecture of all modules>

- **Date:** YYYY-MM-DD
- **Participants:** <names>
- **Reviewed:** ADR-NNN, EVAL-NNN, module sections in `invariants.md`, `memory-design.md`, `runtime-policy-catalog.md`, `structural-constraints.md` §10, `verification-constraints.md` §7, `trace-matrix.md`

| Item | Finding | Resolution |
|---|---|---|
| ADR-NNN | | |

- **Decision per ADR:** ADR-NNN Accepted | changes requested
- **Outcome:** Gate 1 passed for REQ-NNN, ... | another review needed

## PR Review Template

### PR #NNN: <title>

- **Requirements:** REQ-NNN
- **Author / reviewers:** <names>
- **Date:** YYYY-MM-DD
- **Verification evidence checked:** `docs/test-reports/<task-id>.md`, CI run link
- **Findings:** issues raised and how each was resolved.
- **Decision:** approved | changes requested

## Requirement Review Template

### REVIEW-NNN: <requirement and check, e.g. REQ-007 C-005 search provider configuration review>

- **Reviewer:** <name>
- **Date:** YYYY-MM-DD
- **Procedure:** what the reviewer did.
- **Verdict:** PASS | FAIL | NOT_RUN | BLOCKED | N/A, with reasons.

## Records

### PREP-CENTAY-20261114: orchestration draft preparation (AI assistance)

- **Requirements:** REQ-001, REQ-003; contributor interfaces for REQ-002 C-005/C-007.
- **Date:** 2026-11-14, UTC+8.
- **Reviewer:** Codex AI coordinator and read-only AI audit assistants. This is not a
  teammate's PR review or an SA Review.
- **Procedure:** inspect the approved requirements and baseline source, compare the
  OpenCode proposal with the v0.5 reference and peer drafts, and correct the local draft.
- **Findings:** the first OpenCode proposal conflated model turns with actual tool calls,
  retained unvalidated summaries in notes and gave contradictory cap rules. A corrective
  prompt was issued. The subsequent draft and final disposition are documented in
  `docs/architecture/orchestration-review-checklist.md` and the annotated transcript.
- **Evidence:** `transcripts/61061965-XIE_Shentai.md` and its linked raw session files.
- **AI-check disposition:** the initial findings were corrected. Final OpenCode round 4
  found no remaining contradiction in the supplied ADR; 14 external document checks
  passed before the additional peer challenge. At the student's request, two independent
  simulated peer sessions and follow-ups then challenged delivery/context interfaces;
  actual gaps were corrected and unsupported AI assumptions were retracted. The final
  static audit is preserved in D5. None is a product-test verdict or a human review.
- **Human-review verdict:** NOT_RUN. No PR was opened; no human approval, Gate 1 or
  Gate 2 was recorded. The student and named module readers must review the final draft.

This preparation record contributes genuine review findings. It does not replace the
course D4 PR review memo that a human reviewer must write when the draft is published.
