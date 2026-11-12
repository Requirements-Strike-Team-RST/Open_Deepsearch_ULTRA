# Coding Agent Rules

> **HUMAN-ONLY FILE — agents must not modify it.**
> **Purpose:** The always-on behaviour rules for every coding agent role (Plan, Test Author, Build, Verify).
> **Authoritative for:** agent behaviour. Paths and tools each role may use are in `docs/architecture/permission-model.md`; the workflow is in `Prompt.md`.
> **Last updated:** 2026-11-12

## R1. Scope

1. Work only on the assigned requirement ID (RID) and within its approved scope.
2. Do not add unrelated functionality, refactor or reformat untouched code, or widen the scope silently.
3. Follow the accepted ADRs, the architecture blueprint, invariants and structural constraints; do not bypass shared contracts or security boundaries.

## R2. Approval Gates

1. A requirement enters software architecture only when its status in `docs/req/requirements.yaml` is `approved`.
2. No test is written before the architecture passes SA Review (Gate 1, `Prompt.md` §4), and no source code before the tests are approved (Gate 2, `Prompt.md` §6).
3. A proposed ADR or invariant is not approved until SA Review accepts it.
4. If implementation must deviate from the accepted ADR, or touches a shared contract or invariant, stop: that is an architecture change (`Prompt.md` §10).

## R3. Role Discipline

- **Plan** drafts the software architecture (EVAL entries, ADRs, module sections); it never writes source or test code and never switches itself into another role.
- **Test Author** writes the tests for the module's approved test cases and shows that they fail on the baseline; it never writes source code.
- **Build** implements only approved files until the approved tests pass; it never changes those tests, approves its own plan or weakens acceptance criteria, and pushes only when the human confirms.
- **Verify** verifies independently; it never fixes source code and never edits tests, thresholds or evidence to make a check pass.

## R4. Verification Honesty

1. Use only the verdicts `PASS / FAIL / NOT_RUN / BLOCKED / N/A`. A skipped check is not a pass.
2. Never claim a check passed without execution evidence.
3. A failed, blocked or unrun mandatory check keeps the requirement from being marked `verified`.
4. Never remove, weaken or rewrite a test to hide a failure.

Verification layers and evidence rules: `docs/code-governance/verification-constraints.md`.

## R5. Traceability

1. Keep the RID identical across `requirements.yaml`, EVAL entries, ADRs, module sections, tests, test evidence, code docstrings and `trace-matrix.md`.
2. When a requirement changes, list the affected ADRs, module sections, tests, invariants and trace-matrix rows in the report.
3. Record significant architectural decisions as an ADR or an `evaluation-table.md` entry.

## R6. Governance Protection

Human-owned files are listed in `docs/architecture/permission-model.md` §3. Agents modify them only when the human explicitly asks and confirms, and never modify permission configuration or approval records. If a rule is outdated, incomplete or contradictory: identify it, explain the proposed change, and request human review; governance changes go through the normal PR review.

## R7. Conflict Handling

If instructions conflict between the accepted ADRs, architectural constraints, verification rules, these rules or any governance document:

1. Do not choose an interpretation silently.
2. Report the conflicting instructions and their sources.
3. Request human clarification.
4. Resume only after the conflict is resolved.

The precedence order in `AGENTS.md` §3 tells you which document is likely to prevail; it does not remove the duty to report.

## R8. Secrets and Safety

1. Never read, print or commit `.env*` files, credentials or other secrets.
2. Code implementing a requirement marked `safety_relevant: true` follows `docs/code-governance/structural-constraints.md` §7: the decision is made by deterministic code, not by a model.
