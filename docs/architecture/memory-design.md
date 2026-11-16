# Memory and State Design

> **Purpose:** How the research agent stores, passes and discards state and memory: state structure, ownership and lifecycle.
> **Authoritative for:** state and memory design. Graph state types live in `src/open_deep_research/state.py`.
> **Maintained by:** owners of modules that add or change state write a module section (§5); §1–§4 are integrated from those sections before SA Review. Modules that do not touch state add nothing.
> **Last updated:** 2026-11-12

## 1. State Model

| State type | Graph | Key fields | Owning module | Shared contract? |
|---|---|---|---|---|
| `AgentState` | `deep_researcher` | TBD | TBD | TBD |
| `SupervisorState` | supervisor subgraph | TBD | TBD | TBD |
| `ResearcherState` / `ResearcherOutputState` | researcher subgraph | TBD | TBD | TBD |

## 2. Lifecycle

How each field is created, updated (reducer), passed between graphs and cleared. *TBD.*

## 3. Context and Memory Limits

Token budgets, trimming and compression rules. *TBD.*

## 4. Persistence

Checkpointers and anything stored beyond a single run. *TBD.*

## 5. Module Sections

Copy the example for your module. Before SA Review, check §5 of the other modules for conflicting field names, reducers or owners.

### <Module> (REQ-NNN, ADR-NNN)

**Fields added or changed**

| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |
|---|---|---|---|---|---|---|
| `SupervisorState` | `<field>` | `<type>` | override / append | `<component>` | `<components>` | `<when>` → `<when>` |

- **Ownership:** which component is the only writer of each field.
- **Lifecycle:** when the fields are created, updated and cleared within a run.
- **Shared contract:** whether other modules read these fields, and which owners must approve changes (`structural-constraints.md` §6).

### context (REQ-005, ADR-005)

**Fields added or changed**

| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |
|---|---|---|---|---|---|---|
| `ResearcherOutputState` | `research_outcome` | `ResearchOutcome \| None` (default `None`) | none (single value) | `compress_research` (the `token_limit` and `provider_transient` failure paths only) | `supervisor_tools` in `deep_researcher.py`, at the guard in L308-313 | set when the task ends `failed` → never cleared within a run |

- **Ownership:** `compress_research` is the only writer. `supervisor_tools` only reads it; it never sets or clears it.
- **Lifecycle:** absent (`None`) on every successful run and on every baseline run (`context_trimming = False`), so the success path and the flag-off path are unchanged. Set exactly once, when the compression history cannot be reduced (`token_limit`) or the provider rejects the request repeatedly (`provider_transient`). It is not cleared, because a researcher subgraph instance runs once per `ConductResearch` call.
- **Why a field is needed at all:** `ResearcherOutputState` is a Pydantic model that keeps only the fields it declares, so any extra key returned by `compress_research` is filtered out before `supervisor_tools` sees it. Without a declared field the failure cannot leave the researcher subgraph. An exception cannot carry it either: `supervisor_tools` gathers all parallel researchers with `asyncio.gather` (`deep_researcher.py` L305), so one raising researcher would discard every other researcher's result. A declared output field keeps the failure local to the researcher that produced it.
- **Who reads it:** exactly one place, the guard added to `supervisor_tools` at L308-313 (`observation.get("research_outcome")` followed by a `status == "failed"` check). Nothing else in the repository reads a researcher subgraph result. Because the field is always `None` when `context_trimming = False`, the guard's `else` branch reproduces the baseline line unchanged.
- **Type owner:** `ResearchOutcome` is REQ-001's task-result type (owner: centay, orchestration). REQ-005 does not define a second type; ADR-005 §5 records the approval gate. The category values `token_limit` and `provider_transient` are REQ-005's own vocabulary inside that type.
- **Shared contract:** the field is read by `supervisor_tools`, which belongs to orchestration/REQ-002. Adding it is a joint change and needs centay's approval before implementation (`structural-constraints.md` §6).
- **Companion value:** on the failure path `compressed_research` is a descriptive sentence naming the task and the category, not an empty string, so a supervisor that ignores `research_outcome` still sees why the result is missing (ADR-005 §3(d)).
- **Existing fields untouched:** `compressed_research` and `raw_notes` keep their current type and format, so the data `supervisor_tools` already consumes does not change.

**Trimming is not persisted.** Turn removal happens on a local message list inside `context/recovery.py`; the trimmed history is never written back to `ResearcherState.researcher_messages`. The removed indices (`CompressionOutcome.removed_turn_indices`, `TokenLimitExceeded.removed_turn_indices`) are call-local values, not state. A checkpoint replay therefore starts from the untrimmed history and trims again, deterministically, because `plan_trim` is pure. No field is added to `ResearcherState` for trimming.
