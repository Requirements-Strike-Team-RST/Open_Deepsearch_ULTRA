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

Architectural drivers (provisional IDs, see ADR-001 §1): ASR-007-01 validate on every path to a model/search call; ASR-007-02 native provider ↔ `research_model`; ASR-007-03 static MCP capability versus runtime availability; ASR-007-04 unsupported provider lists the supported set (including via `SEARCH_API`); ASR-007-05 pure and offline-testable; ASR-007-06 preserve valid behaviour and topology; ASR-007-07 documentation consistency; ASR-007-08 a statically declared but unusable MCP must not silently produce a no-search run; ASR-007-09 an explicit search-capability predicate replaces the tool-count check.

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Validate at the top of the research graph entry node | `deep_researcher.py` (`clarify_with_user`) | Small; runs early | Violates the thin-node rule (`structural-constraints.md` §2.1); correctness depends on placement before the `allow_clarification` return; no reusable, unit-testable interface; duplicates MCP capability logic | Low | Medium |
| B | Pure centralized validator in `search/`, called from `clarify_with_user` and `researcher` | `search/configuration_validator.py`, two call sites | Single-responsibility module; runs before the `clarify_with_user` (L101) and `write_research_brief` (L154) model calls; pure, so offline-testable; matches blueprint `search/` and dependency direction; no topology change | Two call sites; package registration needed | Medium | High |
| C | Validation inside tool assembly (`utils.get_all_tools`) | `utils.py` | Reuses existing MCP detection | Runs only inside `researcher` (`deep_researcher.py:384,467`), i.e. after the L101/L154 model calls on the standard path, so it fails C-001; bloats `utils.py`; conflates validation with REQ-008 fallback and repeats the unmerged `fix/issue-250` shape | High (coupling) | Medium |

**C-003 mechanism note (affects all options).** Pydantic already rejects an invalid `search_api` during `Configuration` construction (`configuration.py:243-247`), with environment variable precedence, before any node body runs. A validator that receives a constructed `Configuration` therefore cannot be the C-003 mechanism. Option B addresses this with a small raw-input `resolve_search_api` step that runs before construction and reads the same env/config sources; construction stays as a backstop. This does not change the ranking of A/B/C.

**MCP runtime note (affects all options).** The split between static declaration and runtime availability is the same for every option; only the placement of the runtime stop-and-error check differs (Option B places it in `researcher` after assembly). The current `load_mcp_tools` returns a single `[]` for connection failure, zero usable tools, and missing authentication (`utils.py:470-504`), so none of these options can distinguish the runtime outcomes without an adapter or a return-contract change (ADR-001 §8.1a, U-5). This is an implementation dependency of the accepted direction, not a property of the existing code.

**Evidence**

- `configuration.py:11-17,78-93,153-162`: provider set and absence of provider/model validation.
- `configuration.py:236-247`: `from_runnable_config` precedence (env over configurable), `None` dropped, Pydantic enum rejection of invalid values.
- `deep_researcher.py:60-175,365-424,714`: the top-level entry and the in-node model calls at L101 and L154.
- `deep_researcher.py:384-389`: the dead `len(tools) == 0` guard; `utils.py:579`: core tools always present.
- `deep_researcher.py:384,467` and `utils.py:569-597`: `get_all_tools` is reached only inside the researcher loop.
- `utils.py:531-567`: unknown provider falls through silently; tool objects versus metadata; `utils.py:470-481,499-504`: MCP loading returns `[]` on failure.
- `structural-constraints.md` §2 (thin nodes) and §5 (dependency direction).

**Choice:** B — the only option that validates before every model/search call on all paths while keeping validation pure, single-responsibility, offline-testable and inside the `search/` module boundary (provisional; pending SA Review).

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
