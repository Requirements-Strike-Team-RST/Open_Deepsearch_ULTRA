# Evaluation Table

> **Purpose:** ADD results: for each architectural question, 2–3 candidate solutions compared on pros, cons, complexity and testability, and the choice made.
> **Authoritative for:** option comparisons. The decision itself is recorded in the ADR named in the entry.
> **Maintained by:** each module owner adds the entries for their module; entries are integrated before SA Review (`Prompt.md` §4).
> **Last updated:** 2026-11-17

## How to Add an Entry

1. Copy the template at the end, take the next free `EVAL-NNN` number and keep the same fields. EVAL and ADR numbers match where one entry leads to one ADR.
2. **ASR:** list the requirements and the acceptance criteria (C-/M- IDs from `docs/req/requirements.yaml`) that shape the decision.
3. **Candidates:** describe 2–3 options; rate complexity and offline testability as Low, Medium or High.
4. **Choice:** name the chosen option and why it wins, say why each other option was rejected, then write the ADR. Add **Reconsider when** if a rejected option may become the better choice later.

## EVAL-001: Where the task contract and the research-loop exit decision live

- **Module:** orchestration
- **Owner:** centay
- **Decision recorded in:** ADR-001
- **Status:** Decided (Proposed until SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-001 | C-001, C-002, C-003, C-004, M-001 | Correctness of task status, deterministic validation, offline testability |
| REQ-003 | C-001, C-002, C-003, C-004, C-005, M-001, M-002 | One exit reason per run, bounded loop, model claims not trusted |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Prompt-only: add required questions and a completion rubric to the supervisor prompt | `prompts.py` | Smallest change; no new state | Status, coverage and exit stay model decisions; C-002, C-003 and REQ-003 cannot be enforced | Low | Low |
| B | Shared types in `state.py`; `orchestration/` builds specs and results and decides the exit; existing nodes call it | `state.py`, `configuration.py`, `orchestration/`, thin calls in `supervisor`, `supervisor_tools`, `researcher_tools`, `compress_research` | Every decision is a pure function; delivery keeps the fan-out; one flag | New state fields and one subpackage; `supervisor_tools` is shared with delivery | Medium | High |
| C | Orchestration replaces `supervisor_tools` completely, including dispatch and join | `deep_researcher.py`, `orchestration/` | One coherent loop | Takes REQ-002's fan-out away from delivery; largest merge risk | High | High |

**Choice:** B — the only option where status and exit are decided by code while each owner keeps their own part of `supervisor_tools`.

**Rejected and why:** A: cannot make status or exit deterministic. C: moves delivery's acceptance criteria into another module.

## EVAL-002: How delegated tasks run so that one failure neither ends the phase nor loses a sibling

- **Module:** delivery
- **Owner:** AlchemyHAN
- **Decision recorded in:** ADR-002
- **Status:** Decided (Proposed until SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-002 | C-001 to C-007, M-001, M-002 | Failure isolation, keeping completed work, offline testability |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Patch `supervisor_tools` in place: `gather(return_exceptions=True)`, a loop for the overflow, filtered notes | `deep_researcher.py`, `utils.py` | No new package | Queuing, classification and join stay in one long node; tests must drive a whole supervisor turn | Medium | Low |
| B | `delivery/execution.py`: `run_delegations` with a semaphore and `gather(return_exceptions=True)`, one `TaskResult` per spec | `delivery/`, `supervisor_tools` | Each concern is a function a fake researcher can drive; the semaphore keeps every slot busy | One new subpackage | Medium | High |
| C | `asyncio.TaskGroup` | `supervisor_tools` | Standard library; nothing outlives the block | Cancels siblings when one fails, which discards their findings (breaks C-002) | Low | Medium |

**Choice:** B — its functions line up with the criteria: queuing (C-004), classification (C-001, C-003), join (C-006).

**Rejected and why:** A: concerns stay mixed in one node and are hard to test. C: cancels successful siblings.

## EVAL-003: Where the run outcome is decided and how it reaches the output

- **Module:** delivery
- **Owner:** AlchemyHAN
- **Decision recorded in:** ADR-003
- **Status:** Decided (Proposed until SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-004 | C-001 to C-006, M-001 | A failed run never looks complete; the report model cannot hide failures; testability of the pre- and post-report decisions |

The decision needs facts from two moments: the exit reason and task results (before the report) and report errors or truncation (inside report generation).

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Decide inside `final_report_generation` from `notes` | `final_report_generation` | No topology change | The report model has already started, so C-004 fails; `notes` carry no task status | Low | Medium |
| B | New node `check_research_outcome` before the report decides `failed` or continues; `final_report_generation` folds in report errors and truncation; both call pure functions in `delivery/outcome.py` | `delivery/outcome.py`, one node, `final_report_generation`, `state.py` | C-004 holds before any model call; one rule in one module; pure functions | One node added to the topology | Medium | High |
| C | A separate error node behind a conditional edge | two new nodes, conditional edge | Failed runs have their own path | The outcome is assembled in two places | Medium | Medium |

**Choice:** B — the only option that stops the report model when nothing was found, with all outcome logic in one module.

**Rejected and why:** A: cannot satisfy C-004. C: two places can decide `complete`. A single `finalize` node that runs twice (an earlier draft) was dropped: it needs a pass marker and can loop if the marker is missed.

## EVAL-004: How compression recovers from a token-limit error

- **Module:** context
- **Owner:** BroZhai
- **Decision recorded in:** ADR-004
- **Status:** Decided (Proposed until SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-005 | C-001 to C-004, M-001, M-002 | The newest research is never lost; no orphan tool messages; deterministic trimming; offline testability |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Turn-aware trimming written inside `compress_research` | `compress_research`, `utils.py` | Smallest diff | Logic in a graph node; testable only through the node | Low | Medium |
| B | `context/` module: pure `trim_oldest_turn` and one recovery loop, called from `compress_research` | `context/`, `compress_research`, `configuration.py` | Trimming is a pure function; classification fixed in one place; failures map to the REQ-001 result | One new subpackage | Medium | High |
| C | Estimate tokens before the call and trim early | `context/`, `configuration.py`, a tokenizer | Avoids the failed call | Needs a tokenizer for every provider (new dependency) and token-limit configuration (out of REQ-005 scope); still needs B as a backstop | High | Medium |

**Choice:** B.

**Rejected and why:** A: puts logic in a node. C: larger scope and a new dependency.

**Reconsider when:** compression often fails with `token_limit` in live runs, or a tokenizer becomes available without a new dependency (RISK-012).

## EVAL-005: How both prompts state one citation format without drifting apart

- **Module:** citations
- **Owner:** NoPumpkinz
- **Decision recorded in:** ADR-005
- **Status:** Decided (Proposed until SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-006 | C-001, C-002, C-003; C-004 (live) | Consistency, resistance to drift, offline inspection |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Fix each prompt inline | `prompts.py` | Smallest change | The rules stay written twice and can drift again | Low | High |
| A2 | Shared constants defined in `prompts.py` | `prompts.py` | One source of truth; no new module | The contract has no owning module (blueprint §4) | Low | High |
| B | Text constants in `citations/contract.py`, inserted into both prompts at module load | `citations/`, `prompts.py` | One source of truth with an owner; C-003 is a direct comparison | `prompts.py` imports an extension module (recorded exception) | Medium | High |
| C | Code that rewrites citations in generated reports | `citations/`, report node | Strongest guarantee if it worked | Out of REQ-006 scope (INV-004); cannot recover which URL backs a claim | High | Medium |

**Choice:** B — drift-proof and owned by the citations module.

**Rejected and why:** A: drift survives. A2: no owner. C: out of scope.

## EVAL-006: Where the search configuration is validated

- **Module:** search
- **Owner:** sszfot
- **Decision recorded in:** ADR-006
- **Status:** Decided (Proposed until SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-007 | C-001 to C-005 | Fail before any model or search call; valid set-ups unchanged; clear messages |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Checks written at the top of `clarify_with_user` | `clarify_with_user` | Small; runs early | Logic in a node; the researcher subgraph entry needs a copy | Low | Medium |
| B | Pure validator in `search/validation.py`, called first in `clarify_with_user` and `researcher` | `search/`, two call sites | Runs before the first model call; reusable; testable without a model | Two call sites | Low | High |
| C | Checks inside `utils.get_all_tools` | `utils.py` | Reuses tool assembly | Runs after the model calls in `clarify_with_user` and `write_research_brief`, so C-001 fails | Medium | Medium |

**Choice:** B.

**Rejected and why:** A: logic in a node, duplicated at the subgraph entry. C: too late.

## EVAL-007: How evaluation produces valid scores and scores an existing report

- **Module:** evaluation
- **Owner:** DopplerXD
- **Decision recorded in:** ADR-007
- **Status:** Decided (Proposed until SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-009 | C-001 to C-004, M-001 | Valid scores, deterministic validation, failure isolation, compatibility with the LangSmith benchmark |
| REQ-010 | C-001 to C-003 | No research or search calls; input checked before any evaluator; documented use |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Fix `test/evaluators.py` in place and add an entry script | `test/evaluators.py`, `test/prompts.py`, a script | Fewest files | Validation, judge creation and LangSmith formatting stay mixed; the import-time model client stays | Low | Medium |
| B | `test/evaluation/` package with the logic; `test/evaluators.py` becomes a thin adapter | `test/evaluation/`, `test/evaluators.py`, `test/prompts.py`, README | Pure validation tested with a fake judge; lazy judge; benchmark entry unchanged | An adapter layer | Medium | High |
| C | A separate evaluation service next to the old evaluators | new service | Strong isolation | Two copies of every metric; fixes do not reach the benchmark | High | High |

**Choice:** B.

**Rejected and why:** A: core logic stays coupled to import-time side effects. C: duplicated metrics.

## Template

```markdown
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

**Choice:** <option> — <why it wins>.

**Rejected and why:** <option>: <reason>.

**Reconsider when:** <optional: observable condition>.
```
**Rejected and why:** A — breaks the thin-node rule and is placement-fragile. C — validates too late (after the clarification and brief model calls) and couples validation to tool assembly and REQ-008.

## EVAL-002: Where ordered search fallback is executed on failure

- **Module:** search
- **Owner:** sszfot
- **Decision recorded in:** ADR-002
- **Status:** Open (provisional selection of B with a thin C-style tool adapter; awaiting SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-008 | C-001, C-002, C-003, C-004, C-005 | correctness (ordered fallback, explicit failure), testability, modularity, behaviour preservation |

Architectural drivers (provisional IDs, see ADR-002 §1): ASR-008-01 ordered fallback over Tavily/MCP sources; ASR-008-02 eligible-vs-ineligible classification gates fallback; ASR-008-03 empty result is success and suppresses fallback; ASR-008-04 all-sources-failed is explicit and lists each source; ASR-008-05 a success is used identically regardless of source; ASR-008-06 fallback operates only on client-side sources (native excluded); ASR-008-07 error classification is deterministic and offline-testable; ASR-008-08 with no fallback configured, behaviour is unchanged; ASR-008-09 REQ-008 explicitly depends on REQ-007 (especially U-5), the dependency is tracked and unapproved REQ-007 decisions are not treated as implemented guarantees; ASR-008-10 a configured-but-unloadable MCP source is represented deterministically; ASR-008-11 the fallback path exposes one stable model-callable search tool.

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Researcher-level fallback: `execute_tool_safely`/`researcher_tools` loops over sources on exception | `deep_researcher.py` (`execute_tool_safely`, `researcher_tools`) | Small change in one node | Puts the fallback loop and classification in the orchestration node, violating the thin-node rule (`structural-constraints.md` §2.1); classification happens after `execute_tool_safely` has flattened the exception to a string (`deep_researcher.py:427-432`), destroying error identity; no reusable, unit-testable interface; entangles with REQ-007 node validation | Medium | Low |
| B | Dedicated fallback coordinator in `search/`: ordered attempt loop, classification, normalisation and aggregation over injected sources | `search/fallback.py`, `search/errors.py`, `search/adapters/` | Single-responsibility module; classifies typed exceptions **before** stringification; empty-vs-error decided on a typed result; one place builds the all-failed aggregate; pure over injected sources, so offline-testable; matches blueprint `search/` and dependency direction | Needs a way to be exposed to the model as one tool; depends on a structured MCP load result (REQ-007 U-5) for the load-stage distinction | Medium | High |
| C | Thin tool-facing adapter that exposes B's coordinator as the single model-callable search tool (complements B; does not re-implement the algorithm) | `search/` tool registration; `get_all_tools` assembly | Keeps `tools_by_name` dispatch stable (`deep_researcher.py:468-471`); isolates the model-facing schema from the algorithm; thin and testable | On its own it does not implement fallback; it is only useful as the face of B | Low (as an adapter) | High |

**Option C clarification (not a competing algorithm).** Option C is evaluated here as a **thin tool-facing adapter over Option B**, not as a second fallback implementation. The genuine alternatives are A (fallback in the researcher node) versus B (fallback in a dedicated coordinator), with a thin C-style adapter being the mechanism that exposes B to the model while keeping tool-name dispatch intact. This is distinct from REQ-007's rejected "validation inside tool assembly" alternative (ADR-001 §4 Option C), which concerned validation timing, not result routing.

**MCP load-result note (affects all options).** The current `load_mcp_tools` collapses connection failure, zero usable tools and missing authentication into a single empty list (`utils.py:478-479,502-504`). No option can honestly distinguish a source that could not be loaded from one that simply returned nothing without the structured load result proposed in ADR-001 §8.1a (REQ-007 U-5). REQ-008 therefore depends on that contract or an equivalent; it does not silently degrade an unavailable MCP source to an empty tool list.

**Evidence**

- `deep_researcher.py:427-432`: `execute_tool_safely` catches every exception and returns `"Error executing tool: ..."`, so classification must happen before this point.
- `deep_researcher.py:468-471`: `tools_by_name` keys tools by `tool.name` (or `.get("name","web_search")`); a fallback path must remain addressable under a stable tool name.
- `deep_researcher.py:466-479`: `researcher_tools` reloads tools via `get_all_tools` and runs all calls in parallel through `execute_tool_safely`.
- `utils.py:125-127`: an empty Tavily result is a specific success string, not an error.
- `utils.py:43-49`: Tavily's tool signature is `queries: List[str]`; MCP tools expose server-defined schemas, so per-source adapters are required.
- `utils.py:385-447`: `wrap_mcp_authenticate_tool` re-raises non-MCP errors and converts MCP `-32003` to `ToolException`, so some MCP error structure is lost unless classified before wrapping.
- `utils.py:449-524`: `load_mcp_tools` returns `[]` for every failure (the dependency on ADR-001 §8.1a / U-5).
- `structural-constraints.md` §2.1 (thin nodes) and §5 (dependency direction).

**Choice:** B with a thin C-style tool adapter — the coordinator owns the fallback algorithm and classifies typed errors before they are stringified, while a thin adapter exposes it as one stable model-callable search tool (provisional; pending SA Review).

**Rejected and why:** A — puts fallback and classification in the orchestration node and classifies after the exception is already a string. C as a standalone — it only routes results; it does not decide ordering, classification or aggregation, so it complements B rather than replacing it.
