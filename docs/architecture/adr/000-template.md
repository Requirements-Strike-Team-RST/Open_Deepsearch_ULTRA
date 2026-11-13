# ADR-NNN: <Decision Title>

> Copy this file to `NNN-<short-slug>.md` with the next free number (`001`, `002`, ...) and fill every section. Never reuse a number; a replaced decision is marked *Superseded* and links to its successor.

- **Status:** Proposed | Accepted | Superseded by ADR-NNN | Rejected
- **Date:** YYYY-MM-DD
- **Module:** <module>
- **Owner:** <name>
- **Evaluation:** EVAL-NNN (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-NNN | C-NNN, M-NNN | |

## 2. Context

The problem, the forces and constraints, and the baseline behaviour being changed (file and line).

## 3. Decision

The chosen option, stated so that a coding agent can implement it without guessing.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| | |

The full comparison is in EVAL-NNN.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| | | | |

Shared contracts changed (`structural-constraints.md` §6): none | list, with the owners who must approve.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** fields added or changed, or "none" (details in `memory-design.md`).
- **Runtime policies:** POL IDs, or "none" (details in `runtime-policy-catalog.md`).
- **Invariants:** INV IDs, or "none" (details in `invariants.md`).
- **Deterministic boundary:** which decision is made by code rather than by the model, or "none".

## 7. Verification

How each acceptance criterion and invariant above is verified; the cases are listed in the module section of `verification-constraints.md`.

## 8. Consequences

Positive, negative and neutral consequences, including effects on other modules.

## 9. Implementation Steps

Ordered steps for the coding agent, each naming the files it changes, e.g.:

1. Add `<type>` to `src/open_deep_research/<module>/<file>.py`.
2. Call it from `<node>` in `deep_researcher.py`, keeping the node thin.
3. Add the configuration flag `<field>` with the baseline as default.
