# Architecture Blueprint

> **Purpose:** The system-level SA Blueprint (course deliverable D2.1): components and their responsibilities, interfaces, dependencies, data flow and deterministic boundaries.
> **Authoritative for:** architecture, the module list (§4), dependency exceptions (§6) and deterministic boundaries (§8). Changed only through an accepted ADR.
> **Maintained by:** the integrator, from the ADRs and module sections, before SA Review (`Prompt.md` §4).
> **Status:** Integrated from ADR-001 to ADR-008 and accepted in SA Review (PR #22, merged 2026-11-18).
> **Last updated:** 2026-11-20

## 1. Goals and Non-Goals

The goals are the requirements in `docs/req/requirements.yaml`; the non-goals are their `out_of_scope` entries. This document does not restate them.

## 2. Stakeholders and System Context

| Actor or system | Role |
|---|---|
| User | Asks a question through LangGraph Studio, Open Agent Platform or the LangGraph API, and receives the report with its outcome |
| Model providers (OpenAI, Anthropic, others through `init_chat_model`) | Supervisor, researcher, compression, report and evaluation judge models |
| Search providers | Tavily (client-side tool), OpenAI and Anthropic native search (inside the model call), MCP servers (client-side tools) |
| LangSmith | Benchmark datasets and evaluation runs (`test/run_evaluate.py`) |
| Team | Six module owners (§4); coding agents work under `AGENTS.md` |

## 3. Baseline System

Open Deep Research is three LangGraph graphs in `src/open_deep_research/deep_researcher.py`:

| Graph | State | Flow |
|---|---|---|
| `deep_researcher` (top level) | `AgentState` | `clarify_with_user` → `write_research_brief` → `research_supervisor` → `final_report_generation`; `clarify_with_user` may end early with a question |
| supervisor subgraph (the `research_supervisor` node) | `SupervisorState` | `supervisor` ⇄ `supervisor_tools`; `supervisor_tools` fans out to researcher subgraphs and decides when research ends |
| researcher subgraph | `ResearcherState` → `ResearcherOutputState` | `researcher` ⇄ `researcher_tools` → `compress_research` |

Shared modules: `state.py` (graph state and structured outputs), `configuration.py` (runtime `Configuration`, `SearchAPI`, `MCPConfig`), `prompts.py` (prompt templates), `utils.py` (tools, search, MCP loading, model and key helpers).

**Topology change (ADR-003):** one node, `check_research_outcome`, is added between `research_supervisor` and `final_report_generation`. It routes with `Command` to `final_report_generation` or to `END`. No other node or edge changes.

```text
clarify_with_user → write_research_brief → research_supervisor → check_research_outcome → final_report_generation → END
                                                                                        ↘ END (outcome failed)
```

## 4. Components

**Accepted (2026-10-13):** graph nodes stay thin, and each architectural element is one extension module owned by one person.

| Module | Path | Requirements | Owner | Responsibility | ADR |
|---|---|---|---|---|---|
| orchestration | `src/open_deep_research/orchestration/` | REQ-001, REQ-003 | centay | Task specs and results; coverage and loop exit | ADR-001 |
| delivery | `src/open_deep_research/delivery/` | REQ-002, REQ-004 | AlchemyHAN | Fail-isolated fan-out and join; run outcome and limitations | ADR-002, ADR-003 |
| context | `src/open_deep_research/context/` | REQ-005 | BroZhai | Token-limit recovery during compression | ADR-004 |
| citations | `src/open_deep_research/citations/` | REQ-006 | NoPumpkinz | Citation format text for the prompts | ADR-005 |
| search | `src/open_deep_research/search/` | REQ-007, REQ-008 | sszfot | Search configuration validation; ordered search fallback | ADR-006, ADR-008 |
| evaluation | `test/evaluation/` | REQ-009, REQ-010 | DopplerXD | Valid metric results; evaluation-only entry | ADR-007 |

Files, interfaces and allowed dependencies per module are in `structural-constraints.md` §10.

## 5. Interfaces

Interfaces that cross a module boundary.

| Interface | Provided by | Used by | Signature or type | Defined in |
|---|---|---|---|---|
| Task contract types | orchestration (in `state.py`) | delivery, `compress_research`, evaluation, callers | `TaskSpec`, `Source`, `Finding`, `TaskResult`, `TaskResult.failed(...)`, `unanswered_questions(results)` | ADR-001 §5 |
| Fan-out | delivery | `supervisor_tools` (orchestration's flag-on branch) | `run_delegations(specs, run_one, *, max_concurrent, research_model) -> (list[TaskResult], list[str])` | ADR-002 §3 |
| Researcher output | orchestration (`compress_research`) | delivery (`run_delegations`) | `ResearcherOutputState.task_result: TaskResult \| None` | ADR-001 §3.3 |
| Loop result | orchestration | delivery | `AgentState.task_results`, `exit_reason`, `exit_detail` | ADR-001 §6 |
| Compression recovery | context | `compress_research` | `compress_with_recovery(...) -> str`; raises `CompressionFailed(category, reason)` | ADR-004 §5 |
| Run outcome | delivery | callers, evaluation | `AgentState.research_outcome`, `outcome_detail`, `failed_tasks` | ADR-003 §5 |
| Citation format | citations | `prompts.py`; the findings block of ADR-001 | `CITATION_RULES_BLOCK` and two pointer constants | ADR-005 §5 |
| Configuration check | search | `clarify_with_user`, `researcher` | `load_search_config(config) -> Configuration` | ADR-006 §5 |
| Search fallback | search | `researcher_tools` | `apply_search_fallback(tools, configurable) -> list`; raises `AllSourcesFailedError` | ADR-008 §5 |
| Evaluation entry | evaluation | users, scripts | `evaluate_existing_report(question, report, ...) -> EvaluationResult` | ADR-007 §3 |

## 6. Dependencies

Dependency direction: `structural-constraints.md` §5. Exceptions, each justified by an ADR:

| From | To | Reason | ADR |
|---|---|---|---|
| `prompts.py` | `citations/contract.py` | `prompts.py` inserts the citation text constants at module load; the constants hold text only | ADR-005 |
| `test/evaluation/metrics.py` | a judge model created there | The module must not import `deep_researcher.py` or `utils.py`, so it cannot reuse the shared model (`structural-constraints.md` §4) | ADR-007 |
| `deep_researcher.researcher_tools` | `search/fallback.py` | The node passes the assembled tools through `apply_search_fallback`; it adds no tool (exception to `structural-constraints.md` §3) | ADR-008 |
| `test/evaluation/` | location under `test/` | New code under `test/` is allowed only here (`structural-constraints.md` §1) | ADR-007 |

## 7. Data Flow

With `task_contract_enabled` and `context_trimming` on:

1. `clarify_with_user` first validates the search configuration and checks that at least one search tool loads (search). It may end the run with a question.
2. `write_research_brief` writes the brief and resets `task_results`, `exit_reason` and `exit_detail`.
3. `supervisor` calls the model with `ConductResearch` (with `must_answer` and `scope`), `ResearchComplete` and `think_tool`.
4. `supervisor_tools` turns each `ConductResearch` call into a `TaskSpec` (orchestration) and runs the specs with `run_delegations` (delivery). At the cap, the specs end `not_run` instead.
5. Each researcher gets the task brief, runs at most `max_tool_calls` tool calls and records the URLs its tools returned (orchestration); a failed search tries the configured fallback sources (search). `compress_research` compresses with token-limit recovery (context) and builds the `TaskResult` from the findings block (orchestration).
6. `supervisor_tools` appends the results to `task_results`, sends one `ToolMessage` per task back to the supervisor and calls `select_exit`. On exit it writes `exit_reason`, `exit_detail` and `notes` (the counted findings of complete and partial tasks).
7. `check_research_outcome` decides `failed` (end, empty report, no report model call) or continues (delivery).
8. `final_report_generation` writes the report with the shared citation format (citations), then sets the final outcome and, for `partial`, appends the limitations section (delivery).
9. The output holds `final_report`, `research_outcome`, `outcome_detail`, `failed_tasks`, `task_results` and `exit_reason`.

With both flags off, steps 2–8 behave as in the baseline; step 1's validation and the citation prompts apply in every mode.

## 8. Deterministic Boundaries

Decisions where the model's output is input and deterministic code decides (`structural-constraints.md` §7).

| Decision | Requirements | Module | Enforcing component | ADR |
|---|---|---|---|---|
| Task status from sourced findings | REQ-001 | orchestration | `contracts.build_task_result` | ADR-001 |
| Research termination and exit reason | REQ-003 | orchestration | `termination.select_exit` | ADR-001 |
| Task failure category, queuing and join | REQ-002 | delivery | `execution.run_delegations` | ADR-002 |
| Run outcome and limitations section | REQ-004 | delivery | `outcome.assess_research`, `finish_outcome`, `render_limitations` | ADR-003 |
| Message removal during compression | REQ-005 | context | `trimming.trim_oldest_turn`, `recovery.compress_with_recovery` | ADR-004 |
| Evaluator score validity | REQ-009 | evaluation | `metrics.validate_rating`, `groundedness_ratio` | ADR-007 |

**Feature flags** (`structural-constraints.md` §8), all defaulting to the baseline:

| Flag | Default | Requirements | Why one flag |
|---|---|---|---|
| `task_contract_enabled` | `False` | REQ-001 to REQ-004 | REQ-002 and REQ-004 consume the REQ-001 result and the REQ-003 exit reason, so the four cannot run apart |
| `coverage_threshold` | `0.8` | REQ-003 | A setting, not a switch |
| `context_trimming` | `False` | REQ-005 | Works on its own; its failure result (C-004) needs `task_contract_enabled` |
| `search_fallback` | `[]` | REQ-008 | A list, not a switch: the empty list keeps the baseline |

Search validation, the citation prompts and the evaluation module have no flag. Only the safety-relevant decisions are in the table above; search is not safety-relevant.

## 9. State and Data

New state fields, their owning module, the nodes that write them and their lifecycle are in `memory-design.md`. In short: orchestration adds the researcher's task fields and the `task_results` / `exit_reason` / `exit_detail` loop result; delivery adds `research_outcome`, `outcome_detail` and `failed_tasks`; the other modules add no state.

## 10. Failure Handling

| Situation | Handling | Policies | Invariant |
|---|---|---|---|
| A researcher fails, is over the concurrency limit or is left at loop exit | Only that task fails; extra tasks are queued; tasks left at the cap end `not_run` | POL-001 to POL-005 | INV-007 |
| A delegation or a researcher result breaks the contract | Rejected delegation or `failed/invalid_result`; unsourced findings dropped | POL-006 to POL-008 | INV-006 |
| A researcher reaches its tool-call budget | Extra calls are not run; the researcher goes to compression | POL-009 | INV-003 |
| The supervisor claims completion early or its model fails | Request refused below the threshold; exit through `select_exit` | POL-010, POL-011 | INV-003 |
| Compression hits a token limit or another error | Oldest turns removed; explicit `token_limit` or `runtime` failure | POL-012 to POL-014 | INV-001 |
| Nothing found, report fails or findings were cut | Outcome `failed` or `partial`, never `complete` | POL-015 to POL-017 | INV-002 |
| Invalid search configuration, or no search tool available | Rejected before any model call; a researcher without a search tool fails its task | POL-018, POL-019 | INV-005 |
| A search call fails | Configured fallback sources are tried in order; otherwise an explicit failure | POL-024 | INV-010 |
| Invalid judge output, missing input or evaluator error | Only that metric is `not_evaluable` | POL-020 to POL-022 | INV-009 |
| Blank input to the evaluation entry | Rejected before any judge call | POL-023 | — |

Details: `runtime-policy-catalog.md`, `invariants.md`; design risks: `risk-list.md`.

## 11. Decisions and Open Proposals

| # | Proposal | Status |
|---|---|---|
| 1 | Thin graph nodes, one extension module per owner | Accepted 2026-10-13 |
| 2 | Python version | Resolved 2026-11-11: Python 3.12 everywhere (`.python-version`, CI, `langgraph.json`) |
| 3 | Move runtime prompts from `prompts.py` to versioned `prompts/*.yaml` loaded by `prompts.py` | Resolved 2026-11-23: consolidated into `prompts/prompt_v1.0.yaml` via `src/open_deep_research/_prompt_loader.py` |
| 4 | Remaining proposals of the earlier blueprint draft (v0.4) | Pending; not yet copied into this repository |
| 5 | Integration of the six module branches (2026-11-17), see below | Accepted in SA Review (PR #22, 2026-11-18) |
| 6 | REQ-007 open decisions U-1 to U-4: stop the run when no search tool is available (U-1 A); "rejected before the first model or search call of a run" (U-2); resolve the model provider like `init_chat_model` and check it against an explicit allowlist (U-3 B); replace the dead `len(tools) == 0` guard with a search-tool check (U-4 B) | Decided by the team in [Discussion #19](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/discussions/19), 2026-11-17; written into ADR-006 |
| 7 | REQ-008 search fallback from PR #20, integrated as ADR-008 / EVAL-008 / INV-010 / POL-024 / TC-SRC-11 to 17. Narrowed: no structured MCP load result (it depended on REQ-007 U-5, which was not adopted); a listed MCP tool that did not load is recorded as `not available` and never stops the run; a concrete rule for passing queries to MCP tools (one required string argument); one file instead of request, adapter and result layers; the four invariants merged into INV-010; D-1 to D-8 decided in ADR-008 | Accepted in SA Review (PR #22, 2026-11-18) |

**Integration decisions (#5).** Each point resolves a conflict between module drafts or removes design that no requirement asked for. Module owners should check the points that touch their module before SA Review.

| Topic | Before (module drafts) | Integrated design | Modules |
|---|---|---|---|
| Numbering | ADR-001 used by four modules; EVAL-001/002, INV-006/007, POL-001… and test IDs used twice or more | ADR and EVAL 001–007 in requirement order; INV-001–009; POL-001–023; test IDs `TC-<MODULE>-NN` (extended for REQ-008 by decision 7) | all |
| Flags | `orchestration_enabled`, `enforce_delivery_outcome` and `context_trimming`, with a four-way flag matrix | One `task_contract_enabled` for REQ-001–004; `context_trimming` stays | orchestration, delivery, context |
| Task result out of the researcher | Orchestration: `task_result`; context: a second field `research_outcome` (clashing with delivery's run outcome) plus a guard in `supervisor_tools` | One field, `ResearcherOutputState.task_result`; context raises `CompressionFailed` and `compress_research` maps it | orchestration, context, delivery |
| Failure categories | Context added `provider_transient` | Requirement categories only: `token_limit`, `runtime`, `not_run`, `invalid_result`, plus `unanswered` for coverage | context |
| `task_results` writers and reducer | Delivery: `operator.add`, two writers; orchestration: append plus final override | `override_reducer`, one writer (`supervisor_tools`), reset by `write_research_brief` | orchestration, delivery |
| `not_run` results | Orchestration's exit branch calls `run_delegations(unrun_reason=...)` | The cap branch builds `TaskResult.failed(spec, "not_run", ...)` directly | orchestration, delivery |
| Outcome node | One `finalize` node that runs twice, with a `run_finalized` marker and `report_truncated` / `report_error` fields | `check_research_outcome` before the report; the post-report step inside `final_report_generation`; fields `research_outcome`, `outcome_detail`, `failed_tasks` | delivery |
| `notes` content | Orchestration: claims rendered by code; delivery: validated findings | Counted findings of `complete` and `partial` tasks, as REQ-002 C-007 requires; the full summary only goes back to the supervisor. Possible thinner reports are RISK-013 | orchestration, delivery |
| Native search with the task contract | Orchestration rejected it inside the researcher | The search validator rejects the combination at start | orchestration, search |
| Removed as beyond the requirements | Orchestration: `finish_reason` observation, private config keys and contextvar isolation, crash-safe receipts, token cost accounting. Search: environment snapshots, an MCP load adapter that tells each MCP failure apart, configured/bound/executed states. Evaluation: HTTP 401/403 mapping, four exit codes, six files. Context: a separate classification module | — | orchestration, search, evaluation, context |
| Documents | Two risk lists in different formats; `option-ledger.md`; `orchestration-review-checklist.md` under `docs/architecture/`; an AI-preparation note in `review-memo.md` | One `risk-list.md`; the ledger's only open item moved to EVAL-004 and RISK-012; the checklist removed (review evidence, not design); the preparation note removed (its AI use is in `ai-use-log.yaml`) | all |

**Open for SA Review:**

1. Confirm the default `coverage_threshold = 0.8` (REQ-003 notes).
2. Choose the search-capable configuration for the live checks REQ-003 C-006 and REQ-006 C-004.
3. If live reports become too thin with findings-only `notes` (RISK-013), the fix is a change to REQ-002 C-007, not to the design.

## 12. Agent Workflow, Permissions, Verification, Observability and Change Policy

Each operational concern is governed by one authoritative document (`AGENTS.md` §3):

- **Coding-agent workflow:** `Prompt.md` enforces plan-before-code and role separation across Architect, Test Author, Build and Verify, with human review gates (SA Review, test approval and PR review).
- **Permissions:** `docs/architecture/permission-model.md`, enforced mechanically in `.opencode/permissions.jsonc` and `.opencode/rules.md`, restricts each role to its whitelisted paths and commands (Test Author and Build cannot edit each other's files; human-only governance files and secrets are protected).
- **Verification strategy:** `docs/code-governance/verification-constraints.md` defines three verification layers (structural, regression and behavioural) and the six blocking gates implemented through `.github/workflows/ci.yml` and PR review.
- **Observability:** runtime runs expose `task_results`, `exit_reason`, `exit_detail`, `research_outcome`, `outcome_detail` and `failed_tasks` in graph state (`docs/architecture/memory-design.md`) alongside LangGraph / LangSmith execution traces. Development supervision is audited through `docs/ai-use-log.yaml`, `docs/review-memo.md`, `docs/bug-diary.md` and `transcripts/`.
- **Change policy:** requirement changes update `docs/req/requirements.yaml` (validated by schema CI); architectural or boundary changes require a new or amended ADR (`docs/architecture/adr/`), updated module sections and human review; runtime prompt changes update `prompts/prompt_v1.0.yaml` with version tracking.

Decisions are recorded as ADRs in `docs/architecture/adr/` (template: `docs/architecture/adr/000-template.md`).
