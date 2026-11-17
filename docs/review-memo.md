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
