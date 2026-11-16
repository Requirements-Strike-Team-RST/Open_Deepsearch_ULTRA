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

## EVAL-001: How to make the two research prompts state one identical numbered citation format without drift

- **Module:** citations
- **Owner:** NoPumpkinz
- **Decision recorded in:** ADR-001
- **Status:** Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-006 | C-001, C-002, C-003 (offline inspection); C-004 (live, `automated: false`) | Consistency of citation format (invariant), maintainability (drift prevention), testability (offline inspection), evidence/audit (live check + versioned prompt) |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Inline prompt fixes: reconcile each prompt's citation instructions independently, unifying the wording to `[n]` + `### Sources` + `[n] Title: URL` with a renumber-across-findings line. | `prompts.py` | Minimal; no new interface; fully offline-checkable. | Format still duplicated: the rules live independently in both prompts, so the drift mode that produced the defect survives; numbering correctness relies on the model. | Low | High |
| A2 | Shared constants defined directly in `prompts.py` and interpolated into both prompts. | `prompts.py` | Single source of truth; simplest possible; drift-proof; no new module; no dependency exception. | Contract lives in the shared baseline file with no owning module; no home for future INV-004 work; bypasses the blueprint §4 one-element-one-module ownership. | Low | High |
| B | Single shared citation contract: text constants in `citations/contract.py`, interpolated into both prompts at module load. | `citations/contract.py`, `prompts.py` | One source of truth, so the two prompts cannot drift; both prompts provably identical (C-003 trivial); fits blueprint §4 citations module; format-only. | Adds a `prompts.py → citations/contract.py` interface (approved exception to `structural-constraints.md` §5); needs brace-escaping discipline for `.format()`. | Medium | High |
| C | Deterministic post-processor that reformats/renumbers generated reports. | `prompts.py` (minor), `citations/` validator/rewriter | Strongest guarantee if it worked; would serve future INV-004. | Out of REQ-006 scope; implements the Deferred INV-004 property; cannot recover which URL backs an unsourced claim; expands scope (R1/R2). | High | Medium |

**Choice:** Option B — single shared citation contract. The stated defect is two instructions in one file drifting apart, so a single source of truth is what prevents recurrence while keeping the change format-only, offline-testable and inside the citations module. B wins over A2 on governance grounds: blueprint §4 assigns REQ-006 to the citations module (one architectural element = one module = one owner), whereas A2 leaves the contract unowned in the shared baseline file.

**Rejected and why:** A — reconciles the prompts inline but leaves the format duplicated, so the drift mode survives. A2 — drift-proof but leaves the contract unowned, with no home for INV-004 work and no §4 ownership. C — out of REQ-006 scope and owned by Deferred INV-004; a post-processor can reformat but cannot recover which URL backs an unsourced claim.

*Amended after module review: added Option A2 and rephrased Option A.*
