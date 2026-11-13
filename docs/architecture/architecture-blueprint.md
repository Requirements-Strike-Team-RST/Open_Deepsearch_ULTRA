# Architecture Blueprint

> **Purpose:** The system-level SA Blueprint (course deliverable D2.1): components and their responsibilities, interfaces, dependencies, data flow and deterministic boundaries.
> **Authoritative for:** architecture, the module list (§4), dependency exceptions and deterministic boundaries. Changed only through an accepted ADR.
> **Maintained by:** the integrator, from the ADRs and module sections, before SA Review (`Prompt.md` §4).
> **Status:** Skeleton. *TBD* sections are filled at integration; items marked *Proposed* are not binding.
> **Last updated:** 2026-11-12

## 1. Goals and Non-Goals

The goals are the requirements in `docs/req/requirements.yaml`; the non-goals are their `out_of_scope` entries. This document does not restate them.

## 2. Stakeholders and System Context

*TBD.*

## 3. Baseline System

Open Deep Research is three LangGraph graphs in `src/open_deep_research/deep_researcher.py`:

| Graph | State | Flow |
|---|---|---|
| `deep_researcher` (top level) | `AgentState` | `clarify_with_user` → `write_research_brief` → `research_supervisor` → `final_report_generation`; `clarify_with_user` may end early with a question |
| supervisor subgraph (the `research_supervisor` node) | `SupervisorState` | `supervisor` ⇄ `supervisor_tools`; `supervisor_tools` fans out to researcher subgraphs and decides when research ends |
| researcher subgraph | `ResearcherState` → `ResearcherOutputState` | `researcher` ⇄ `researcher_tools` → `compress_research` |

Shared modules: `state.py` (graph state and structured outputs), `configuration.py` (runtime `Configuration`, `SearchAPI`, `MCPConfig`), `prompts.py` (prompt templates), `utils.py` (tools, search, MCP loading, model and key helpers). This topology stays unchanged unless an ADR changes it (`structural-constraints.md` §2).

## 4. Components

**Accepted (2026-10-13):** graph nodes stay thin, and each architectural element is one extension module owned by one person.

Module names below are used by every other architecture document. Final paths and responsibilities are fixed by each module's ADR.

| Module | Path (*Proposed*) | Requirements | Responsibility |
|---|---|---|---|
| orchestration | `src/open_deep_research/orchestration/` | REQ-001, REQ-003 | Task contract, delegation, termination |
| delivery | `src/open_deep_research/delivery/` | REQ-002, REQ-004 | Task failure handling, run outcome |
| context | `src/open_deep_research/context/` | REQ-005 | Context trimming during compression |
| citations | `src/open_deep_research/citations/` | REQ-006 | Citation format |
| search | `src/open_deep_research/search/` | REQ-007, REQ-008 | Search configuration validation, fallback |
| evaluation | `test/evaluation/` | REQ-009, REQ-010 | Evaluator validity, evaluation-only entry |

## 5. Interfaces

*TBD.* One row per interface that crosses a module boundary.

| Interface | Provided by | Used by | Signature or type | Defined in |
|---|---|---|---|---|
| | | | | ADR-NNN |

## 6. Dependencies

Dependency direction: `structural-constraints.md` §5. Exceptions, each justified by an ADR:

| From | To | Reason | ADR |
|---|---|---|---|
| `utils.py` | `search/` | `get_all_tools()` assembles search tools (*Proposed*) | TBD |

## 7. Data Flow

*TBD.* How a request, the research brief, task specifications and results, notes and the final report move through the components.

## 8. Deterministic Boundaries

Decisions where the model's output is input and deterministic code decides (`structural-constraints.md` §7). *Proposed*, from the requirements marked `safety_relevant: true`:

| Decision | Requirements | Module | Enforcing component | ADR |
|---|---|---|---|---|
| Task status from sourced findings | REQ-001 | orchestration | TBD | TBD |
| Research termination and exit reason | REQ-003 | orchestration | TBD | TBD |
| Task failure, queuing and join | REQ-002 | delivery | TBD | TBD |
| Run outcome and limitations section | REQ-004 | delivery | TBD | TBD |
| Message eviction during compression | REQ-005 | context | TBD | TBD |
| Evaluator score validity | REQ-009 | evaluation | TBD | TBD |

## 9. State and Data

*TBD;* integrated from `memory-design.md`.

## 10. Failure Handling

*TBD;* integrated from `runtime-policy-catalog.md` and `invariants.md`.

## 11. Decisions and Open Proposals

| # | Proposal | Status |
|---|---|---|
| 1 | Thin graph nodes, one extension module per owner | Accepted 2026-10-13 |
| 2 | Python version | Resolved 2026-11-11: Python 3.12 everywhere (`.python-version`, CI, `langgraph.json`) |
| 3 | Move runtime prompts from `prompts.py` to versioned `prompts/*.yaml` loaded by `prompts.py` | Pending |
| 4 | Remaining proposals of the earlier blueprint draft (v0.4) | Pending; not yet copied into this repository |

Decisions are recorded as ADRs in `adr/` (template: `adr/000-template.md`).
