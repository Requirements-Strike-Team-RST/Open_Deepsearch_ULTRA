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

## EVAL-001: Where search configuration is validated before research

- **Module:** search
- **Owner:** sszfot
- **Decision recorded in:** ADR-001
- **Status:** Open (provisional selection of B; awaiting SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-007 | C-001, C-002, C-003, C-004, C-005 | correctness (fail before model/search calls), testability, modularity, behaviour preservation |

Architectural drivers (provisional IDs, see ADR-001 §1): ASR-007-01 validate on every path to a model/search call; ASR-007-02 native provider ↔ `research_model`; ASR-007-03 static MCP capability versus runtime availability; ASR-007-04 unsupported provider lists the supported set; ASR-007-05 pure and offline-testable; ASR-007-06 preserve valid behaviour and topology; ASR-007-07 documentation consistency; ASR-007-08 a statically declared but unreachable MCP must not silently produce a no-search run (placement unresolved; ADR-001 §12 U-1).

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Validate at the top of the research graph entry node | `deep_researcher.py` (`clarify_with_user`) | Small; runs early | Violates the thin-node rule (`structural-constraints.md` §2.1); correctness depends on placement before the `allow_clarification` return; no reusable, unit-testable interface; duplicates MCP capability logic | Low | Medium |
| B | Pure centralized validator in `search/`, called from `clarify_with_user` and `researcher` | `search/configuration_validator.py`, two call sites | Single-responsibility module; runs before the `clarify_with_user` (L101) and `write_research_brief` (L154) model calls; pure, so offline-testable; matches blueprint `search/` and dependency direction; no topology change | Two call sites; package registration needed | Medium | High |
| C | Validation inside tool assembly (`utils.get_all_tools`) | `utils.py` | Reuses existing MCP detection | Runs only inside `researcher` (`deep_researcher.py:384,467`), i.e. after the L101/L154 model calls on the standard path, so it fails C-001; bloats `utils.py`; conflates validation with REQ-008 fallback and repeats the unmerged `fix/issue-250` shape | High (coupling) | Medium |

**Evidence**

- `configuration.py:11-17,78-93,153-162`: provider set and absence of provider/model validation.
- `deep_researcher.py:60-175,365-424,714`: the top-level entry and the in-node model calls at L101 and L154.
- `deep_researcher.py:384,467` and `utils.py:569-597`: `get_all_tools` is reached only inside the researcher loop.
- `utils.py:531-567`: unknown provider falls through silently; `utils.py:583,881-890`: bare enum `ValueError` on an unsupported value; `utils.py:470-481,499-504`: MCP loading returns `[]` on failure.
- `structural-constraints.md` §2 (thin nodes) and §5 (dependency direction).

**Choice:** B — the only option that validates before every model/search call on all paths while keeping validation pure, single-responsibility, offline-testable and inside the `search/` module boundary (provisional; pending SA Review).

**Rejected and why:** A — breaks the thin-node rule and is placement-fragile. C — validates too late (after the clarification and brief model calls) and couples validation to tool assembly and REQ-008.
