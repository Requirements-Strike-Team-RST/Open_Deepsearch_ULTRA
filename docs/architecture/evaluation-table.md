# Evaluation Table

> **Purpose:** ADD results: for each architectural question, 2–3 candidate solutions compared on pros, cons, complexity and testability, and the choice made.
> **Authoritative for:** option comparisons. The decision itself is recorded in the ADR named in the entry.
> **Maintained by:** each module owner adds the entries for their module; entries are integrated before SA Review (`Prompt.md` §4).
> **Last updated:** 2026-11-12

## How to Add an Entry

1. Copy the example below, take the next free `EVAL-NNN` number and keep the same fields.
2. **ASR:** list the requirements and the acceptance criteria (C-/M- IDs from `docs/req/requirements.yaml`) that shape the decision.
3. **Candidates:** describe 2–3 options; rate complexity and offline testability as Low, Medium or High.
4. **Choice:** name the chosen option and why it wins, say why each other option was rejected, then write the ADR.

## EVAL-NNN: <Question being decided>

- **Module:** <module from `architecture-blueprint.md` §4>
- **Owner:** <name>
- **Decision recorded in:** ADR-NNN
- **Status:** Open | Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-NNN | C-NNN, M-NNN | e.g. correctness, testability, cost |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | | | | | Low / Medium / High | Low / Medium / High |
| B | | | | | | |
| C (optional) | | | | | | |

**Choice:** <option> — <why it wins>.

**Rejected and why:** <option>: <reason>.

## EVAL-001: How should evaluation produce valid metric results and score an existing report?

- **Module:** evaluation
- **Owner:** DopplerXD
- **Decision recorded in:** ADR-001
- **Status:** Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-009 | C-001, C-002, C-003, C-004, M-001 | Correctness of the score; deterministic validation; failure isolation; offline testability; compatibility with the LangSmith benchmark entry |
| REQ-010 | C-001, C-002, C-003 | Separation from the research graph and search; input validation before any evaluator; documented use; low operating cost |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Harden `test/evaluators.py` in place and add a separate entry file | `test/evaluators.py`, `test/prompts.py`, a new entry script | Smallest file churn; baseline entry untouched; direct reuse of existing functions | Validation, judge construction, LangSmith serialisation and entry logic stay mixed; the import-time model side effect is harder to remove safely; no clean module boundary for pure tests | Low | Medium |
| B | New `test/evaluation/` core package plus a thin compatibility adapter in `test/evaluators.py` | New `test/evaluation/` package; `test/evaluators.py`; `test/prompts.py`; README | Deterministic validation and entry are separable and testable with a fake judge; judge is constructed lazily; baseline evaluator names and return shapes are preserved; `test/run_evaluate.py` unchanged; matches the blueprint module path | More files and an adapter mapping; a small amount of indirection | Medium | High |
| C | Duplicate the evaluators in a standalone evaluation service and leave the baseline untouched | New standalone service; existing scripts unchanged | Strong isolation from the benchmark path | Two sources of truth; REQ-009 fixes do not reach the benchmark; duplicated maintenance; violates “extend, never replace” | High | High |

**Choice:** option B — it separates deterministic validation and the evaluation-only entry from the LangSmith adapter, keeps the baseline entry compatible, and allows every REQ-009 and REQ-010 case to run offline with an injected judge. It also places the module at the path assigned by `architecture-blueprint.md` §4.

**Rejected and why:** option A: the core logic remains coupled to the evaluator functions and the import-time model construction, which makes failure isolation and offline tests harder to guarantee. option C: it duplicates metric logic, leaves the benchmark path broken, and creates two sources of truth for the same scores.

The decision, interfaces and implementation steps are in ADR-001.

**Open for module review:** `structural-constraints.md` §1 lists top-level `test/` as not for new work, while `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm the exception at module review and integration.
