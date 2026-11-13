# Memory and State Design

> **Purpose:** How the research agent stores, passes and discards state and memory: state structure, ownership and lifecycle.
> **Authoritative for:** state and memory design. Graph state types live in `src/open_deep_research/state.py`.
> **Maintained by:** owners of modules that add or change state write a module section (§5); §1–§4 are integrated from those sections before SA Review. Modules that do not touch state add nothing.
> **Last updated:** 2026-11-13

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

**Fields added or changed:** none.

`compress_research` reads only existing fields of `ResearcherState` and returns the existing keys `compressed_research` and `raw_notes`; the trimming helpers in `src/open_deep_research/context/` are pure functions over local message lists and never read or write graph state.

- **Why no field is added:** the research topic is already the first `HumanMessage` of `researcher_messages` (`deep_researcher.py` L297-300) and `ResearcherState.research_topic` already holds it (L88), so the topic to protect can be located from message position and type without a new field. The compression instruction is appended by the node (L538) and its index is passed to the module as an argument.
- **Removed-turn bookkeeping:** the indices removed by a retry are returned per call in `CompressionOutcome.removed_turn_indices` and `TokenLimitExceeded.removed_turn_indices`. They are local to the node invocation and are not persisted; a trimmed history is not written back to state, so a checkpoint replay starts from the untrimmed `researcher_messages` and trims again deterministically.
- **Failure reporting:** the failed `token_limit` result is expressed through the REQ-001 task-result type defined in the orchestration module. This module adds no field for it; the owner agreement on that type is recorded in ADR-005 §5.
- **Shared contract:** none added. `ResearcherState.compressed_research` and `ResearcherState.raw_notes` are read by `supervisor_tools` (`deep_researcher.py` L298-330) and keep their current type and format, so no other owner's approval is needed for the state.
