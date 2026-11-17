# Evaluation Table

> **Purpose:** ADD results: for each architectural question, 2–3 candidate solutions compared on pros, cons, complexity and testability, and the choice made.
> **Authoritative for:** option comparisons. The decision itself is recorded in the ADR named in the entry.
> **Maintained by:** each module owner adds the entries for their module; entries are integrated before SA Review (`Prompt.md` §4).
> **Last updated:** 2026-11-13

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

## EVAL-002: Where the delegation contract and the research-loop exit decision live

- **Module:** orchestration
- **Owner:** Centay
- **Decision recorded in:** ADR-002
- **Status:** Open
## EVAL-001: How delegated research tasks are executed so that one failure neither ends the phase nor loses a sibling

- **Module:** delivery
- **Owner:** AlchemyHAN
- **Decision recorded in:** ADR-001 (task failure isolation). **Status:** Decided
## EVAL-001: Token-limit recovery in `compress_research` — how the history is reduced

- **Module:** context
- **Owner:** BroZhai
- **Decision recorded in:** ADR-005 (`docs/architecture/adr/005-context-compression.md`)
- **Status:** Open

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-001 | C-001, C-002, C-003, C-004, M-001 | Correctness, deterministic validation, offline testability |
| REQ-003 | C-001, C-002, C-003, C-004, C-005, C-006, M-001, M-002 | Determinism, boundedness, single exit reason |
| REQ-002 | C-005, C-007 (contributor only) | Failure isolation, no failure text in notes |
| REQ-005 | C-004 (contributor only) | A failed task is a typed result, not placeholder text |

**Critical drivers.** Each driver is rated weak (W), medium (M) or strong (S) against an observable runtime design property. A **fail** on any critical driver K1–K5 disqualifies the option; K6 is a secondary tradeoff. No numeric score is summed; the choice is justified qualitatively on the drivers that separate the options.

| # | Driver (observable property) | Fail means |
|---|---|---|
| K1 | **Deterministic status and exit.** Every exit produces exactly one `RunRecord`; code validates model-proposed findings and computes status/coverage/exit, without accepting a model's self-declared status or exit as authority. | A model's completion/status claim can bypass the deterministic selector or source validation. |
| K2 | **Single delta/override state protocol.** Per-turn results travel as plain list deltas that `override_reducer` appends, and the final write is one override envelope; a reader can reconstruct every task result exactly once. | Results are written twice, by two writers, or only as free text. |
| K3 | **Flag-off equivalence.** With `orchestration_enabled = False` the enabled-only code is unreachable and the baseline nodes, tools and state fields behave as at commit `827fd32`. | Enabled logic runs in the flag-off path. |
| K4 | **Scope and owner separation.** Orchestration introduces no REQ-002 dispatch/join logic and no REQ-004 outcome logic, so three owners can work in parallel on `supervisor_tools`. | One module must own another module's acceptance criteria. |
| K5 | **Reader validity.** Readers receive a validated object only, and `notes` are rendered from validated findings rather than model prose. | Failure or unverified prose can reach report generation or the outcome. |
| K6 | **Implementation and coordination cost**, a secondary tradeoff rather than an acceptance gate. | Assessed qualitatively; no schedule measurement is claimed. |

Rating anchors: **W** permits a documented bypass or violates a critical driver;
**M** covers only some paths or needs an additional manual control; **S** assigns
an explicit deterministic boundary to every specified path in the candidate's
declared support envelope. These are inspection-based design ratings, not test
verdicts. W on K1–K5 disqualifies; K6 compares cost among otherwise viable choices.
Native-search enablement, the shared reader contracts and the course input-token
policy remain explicit integration decisions; S does not claim they are approved.
| REQ-002 | C-001, C-002, C-003, C-004, C-005, C-006, C-007; M-001, M-002 | Correctness of failure isolation; testability without a network or a model; preserving completed work (cost already spent); observability of what was run |

The task contract itself — `TaskSpec`, `TaskResult`, the error categories and `derive_task_status` — belongs to REQ-001 and is owned by the orchestration module (ADR-00X, owner centay); this ADR proposes placing the types in the shared `state.py` so that neither extension module imports the other. This entry assumes that contract and decides only how the delivery module consumes it.
| REQ-005 (invariant, `safety_relevant: true`) | C-001 (M-001 `latest_turn_preservation_rate == 1.0`) | Correctness: the newest research is never lost; determinism of the trimming decision (`structural-constraints.md` §7) |
| REQ-005 | C-002 (M-002 `orphan_tool_message_count == 0`) | Data integrity: no tool result without its requesting AI message |
| REQ-005 | C-003 | Correctness: token-limit errors are recognised for the model that made the call (`compression_model`, not `research_model`) |
| REQ-005 | C-004 | Fail-closed behaviour: an unreducible history ends the task as failed `token_limit` through the declared `research_outcome` output field, never as placeholder text returned as a summary |
| REQ-001 (dependency) | task result carries status and reason | Coupling: the failure category must reach the supervisor through the REQ-001 task-result contract |
| INV-001 | fallback chain | Testability offline: trimming must be provable with fake models and no network |

The decision has to answer four distinct sub-questions sharing one loop: (a) the unit of removal, (b) how the protected region (topic, compression instruction, latest AI turn, tool results after it) is computed and kept, (c) how token-limit errors are classified per model, (d) what happens when the history can no longer be reduced. The candidates below are end-to-end strategies, not isolated patches, because the four sub-questions interact.

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Patch `supervisor_tools` in place: `asyncio.gather(..., return_exceptions=True)`, classify each outcome inline, replace the overflow slice `[:max]` with a loop that runs the remaining calls after the first batch, and filter `get_notes_from_tool_calls` | `deep_researcher.py` (`supervisor_tools`), `utils.py` | Smallest diff; no new package; no new state field | Four unrelated concerns (fan-out, queuing, classification, note filtering) stay inside one ~150-line node; the exception branch cannot be exercised without driving the whole node; the join guarantee from C-006 has nowhere to live; no place to record per-task outcomes | Medium | Low: only end-to-end node tests |
| B | New `delivery/execution.py`: `run_delegations(specs, researcher, ...)` builds one `TaskRunRecord` per call, launches them all and bounds concurrency with an `asyncio.Semaphore(max_concurrent_research_units)`, collects every outcome with `asyncio.gather(return_exceptions=True)`, classifies exceptions into `token_limit` / `runtime`, produces a `TaskResult` for every call including those left unrun, and returns `DelegationOutcome(records, results, notes, failures)`; `supervisor_tools` becomes a thin caller | New `delivery/execution.py`; `deep_researcher.py` (`supervisor_tools`); `state.py` (task contract) | Each concern has one function that can be unit-tested with a fake researcher; concurrency scheduling, classification and join are testable in isolation; per-call records make `dropped_delegation_count` measurable; a semaphore keeps every slot busy, so a slow task does not stall the queue; matches the "one element, one module" rule and the thin-node rule | New subpackage must be added to `packages` in `pyproject.toml`; `supervisor_tools` keeps a small amount of glue | Medium | High: fake researchers, no model or network |
| C | `asyncio.TaskGroup` (or `anyio` task groups) for structured concurrency: cancel the group when one researcher raises | `deep_researcher.py` (`supervisor_tools`) | Python-native; guarantees no task outlives the block | A task group cancels its siblings when one child fails, so a successful sibling's findings are discarded — directly contradicts C-002 and M-001; cancellation also spends tokens on work whose result is thrown away | Low | Medium: cancellation timing is hard to assert deterministically |

**Choice:** B — it is the only candidate whose units line up one-to-one with the acceptance criteria: queuing is C-004, classification is C-001/C-003, join is C-006, note separation is C-007, each with an interface that a fake researcher can drive offline.

**Rejected and why:** A — the acceptance criteria C-004, C-006 and C-007 would all land in one node body, so each test would re-simulate the whole supervisor turn and a regression in one concern would be hard to localise; it also leaves no record from which `dropped_delegation_count` can be computed. C — structured concurrency cancels successful siblings, which is exactly the loss REQ-002 forbids; it is the right tool for "all or nothing" work, not for "keep every completed task".

## EVAL-002: Where the research outcome is computed and how it reaches the run output

- **Module:** delivery
- **Owner:** AlchemyHAN
- **Decision recorded in:** ADR-002 (graph shape and run outcome); the task-execution half is ADR-001
## EVAL-001: How to make the two research prompts state one identical numbered citation format without drift

- **Module:** citations
- **Owner:** NoPumpkinz
- **Decision recorded in:** ADR-001
- **Status:** Decided
## EVAL-001: Where search configuration is validated before research

- **Module:** search
- **Owner:** sszfot
- **Decision recorded in:** ADR-001
- **Status:** Open (provisional selection of B; awaiting SA Review)
## EVAL-001: How should evaluation produce valid metric results and score an existing report?

- **Module:** evaluation
- **Owner:** DopplerXD
- **Decision recorded in:** ADR-001
- **Status:** Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-004 | C-001, C-002, C-003, C-004, C-005, C-006; M-001 | Caller-visible correctness of `complete` / `partial` / `failed`; the report model must not be able to make a failed run look complete; testability of both the pre-report and post-report decision |
| REQ-002 | C-005, C-007 | The failed-task list must survive into the output, which needs structured records, not note text |

The outcome depends on information from two different moments: the research exit reason and task results (available before report generation) and report-generation success or truncation (known only after it). The decision has to see both.
| REQ-006 | C-001, C-002, C-003 (offline inspection); C-004 (live, `automated: false`) | Consistency of citation format (invariant), maintainability (drift prevention), testability (offline inspection), evidence/audit (live check + versioned prompt) |
| REQ-007 | C-001, C-002, C-003, C-004, C-005 | correctness (fail before model/search calls), testability, modularity, behaviour preservation |

Architectural drivers (provisional IDs, see ADR-001 §1): ASR-007-01 validate on every path to a model/search call; ASR-007-02 native provider ↔ `research_model`; ASR-007-03 static MCP capability versus runtime availability; ASR-007-04 unsupported provider lists the supported set (including via `SEARCH_API`); ASR-007-05 pure and offline-testable; ASR-007-06 preserve valid behaviour and topology; ASR-007-07 documentation consistency; ASR-007-08 a statically declared but unusable MCP must not silently produce a no-search run; ASR-007-09 an explicit search-capability predicate replaces the tool-count check.
| REQ-009 | C-001, C-002, C-003, C-004, M-001 | Correctness of the score; deterministic validation; failure isolation; offline testability; compatibility with the LangSmith benchmark entry |
| REQ-010 | C-001, C-002, C-003 | Separation from the research graph and search; input validation before any evaluator; documented use; low operating cost |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | **Prompt-only gating:** add must-answer questions and a completion rubric to `lead_researcher_prompt`; the supervisor model is asked to call `ResearchComplete` only when every question is answered; no new type or state field; `notes` stay as returned. | `prompts.py` only | Smallest diff; no new state; cannot break reducers | K1 **fail**: loop exit, status and coverage stay model decisions, so REQ-001 C-002/C-003 and REQ-003 C-001…C-005 cannot fail offline for the right reason; K2 **fail**: no typed result exists; K5 **fail**: notes remain model prose. | Low | Low |
| B | **Deterministic orchestration module over typed shared state (preferred):** `state.py` holds the types and the orchestration fields; `orchestration/` holds helpers (`contracts`, `budget`, `evidence`, `termination`) over one receipt that import those types; `supervisor_tools` keeps its baseline structure and calls the helpers at the existing boundaries; REQ-002 dispatch/join and REQ-005 trimming stay with their owners. | `state.py`, `orchestration/`, `configuration.py`, thin calls from `supervisor`, `supervisor_tools`, `researcher_tools`, `compress_research`, `prompts.py` (draft, Jeremy's approval) | K1–K5 all strong: the selector is one pure function over exact fractions; deltas use the existing append reducer; enabled-only code sits behind one flag; each owner keeps their own lines; every case is a fake-model offline test | Adds fields to four state classes (an honest change to those classes) and one subpackage; a coordinated hand-over inside `supervisor_tools` | Medium | High |
| C | **Whole-node takeover:** orchestration supplies a complete replacement `supervisor_tools` (and a matching `supervisor`) that performs dispatch, queuing, join, validation and the exit decision in one module. | `deep_researcher.py` node bodies replaced, `orchestration/` | K1, K2 and K5 can be strong: a single module holds one coherent loop | K4 **fail**: takes REQ-002 dispatch, queuing and join and REQ-004 outcome inputs away from their owners, so those owners cannot implement or test their own criteria in their own lines; K6 **weak**: largest coordination surface and highest merge-conflict risk for parallel module work | High | High (but the delivered tests would belong to the wrong module) |

**Choice:** **B**, provisionally. Within the declared support envelope it assigns boundaries for K1–K5: a pure exit selector over validated results, baseline append/final-override semantics, a disabled-path switch, scoped module ownership and findings-only notes. Its implementation/coordination cost is Medium (K6). Reader agreement and the listed course integration gaps must be resolved before acceptance; the design ratings are not proof of implemented behavior.

**Rejected and why:**

- **A:** fails K1, K2 and K5. Prompt text cannot make a task status or an exit reason deterministic, and REQ-003 explicitly rejects trusting the model's completion claim.
- **C:** rejected on owner scope and coordination cost (K4 fail, K6 weak), not on correctness — it could produce a correct loop, but it moves other owners' acceptance criteria into one module and maximises merge conflict in the one node three owners must edit.
| A | Compute the outcome inside `final_report_generation`, reading only `notes` and the retry state | `deep_researcher.py` (`final_report_generation`) | No topology change; one file | `notes` is a list of free-text strings, so the task id, status and reason of a failed task are already lost — the failed-task list of C-002 cannot be produced; C-004 ("the report model is not called") cannot be honoured because the node has already started | Low | Medium |
| B | New `delivery/outcome.py`, called from a new `finalize` node: `research_supervisor → finalize → final_report_generation → finalize → END`. The first pass computes the pre-report outcome from the exit reason and task results and decides whether the report model may run at all; the second pass folds in report success or truncation, appends the system-written limitations section and writes `research_outcome` and `failed_tasks` | `delivery/outcome.py`; `deep_researcher.py` (one new node and three edges); `state.py` (`research_outcome`, `failed_tasks`) | The decision sees structured task records, so the failed-task list is exact; the "no report model on a failed run" rule (C-004) is enforced before the model is called; both passes are pure functions of state, so they are testable with no graph and no model; the three baseline graph nodes keep their bodies | Adds one node and three edges to a topology that the baseline rules keep fixed, so it needs this ADR and SA Review; the node runs twice, which readers may find surprising | Medium | High: both passes are pure functions over a state dict |
| C | Keep two nodes and route with a conditional edge: `conditional_edge(research_supervisor)` sends failed runs to a separate `emit_outcome` node and everything else to `final_report_generation` → `emit_outcome` | `deep_researcher.py` (two new nodes, a conditional edge, a new edge) | Failed runs have an obvious dedicated path; no node runs twice | Two nodes must both assemble the outcome and the limitations text, so the same logic is duplicated; the conditional must reach the same verdict as the later node, giving two places where `complete` can be decided; more edges to keep consistent | Medium | Medium |

**Choice:** B — the outcome is computed by pure functions that take structured state, and the same function is used before and after report generation, so there is exactly one place that can produce `complete`. Enforcing "no report model when nothing was found" before the model call is what makes C-004 deterministic rather than a post-hoc check.

**Rejected and why:** A — free-text notes cannot carry per-task status, so the failed-task list and C-004 are unimplementable; it also leaves the report model as the only thing standing between a failed run and a normal-looking report, which is the harm REQ-004 exists to remove. C — duplicating the outcome assembly in two nodes creates two sources of truth for the same decision and more edges than B, for no gain in testability.

**Cross-module note:** both entries consume the REQ-001 task contract and the REQ-003 exit reason owned by orchestration (centay). Neither delivery module imports orchestration: ADR-001 §5 places the task contract in the shared `state.py`, and the interface between the two modules is a shared contract that the orchestration owner must approve in the PR review (`structural-constraints.md` §10).
| A | **Turn-aware trimming inside `deep_researcher.py`.** `compress_research` splits `researcher_messages` into typed segments (preamble, research turns defined as one `AIMessage` plus the `ToolMessage`s that follow it, compression instruction), computes the protected region (instruction + latest turn + its tool results, and the research topic/task spec from the REQ-001 task specification carried on the message), then removes whole turns from the oldest end and retries. Classification uses `configurable.compression_model`. When no removable turn is left, the node returns the failed task result of category `token_limit`. | `deep_researcher.py` (`compress_research` only), `utils.py` (replace `remove_up_to_last_ai_message` with a turn-aware helper) | Smallest diff; no new module; no new output field | Logic lives in a graph node, which `structural-constraints.md` §2 (thin nodes) and §8 (logic goes in the owner's extension module) forbid; the helper is a free function with no place to unit-test the protected region on its own; leaks REQ-001 task-result construction into the node | Low | Medium: can be tested through the node with fake models, but only end-to-end |
| B | **Dedicated `context` module — pure compaction policy plus an explicit `Compressor` loop.** `src/open_deep_research/context/` exposes (1) a pure, deterministic function `plan_trim(messages, protected, removable_turn_ids) -> TrimPlan` (returns the messages to keep and the turn IDs removed, or `None` when nothing removable is left), (2) `classify_token_limit(exc, model_name) -> bool` as the single entry point for the loop, and (3) `compress_with_recovery(...)`, a small orchestrator that runs the retry loop, asks the model, applies the plan, and on exhaustion raises a typed `TokenLimitExceeded` (or returns a failed task result of category `token_limit`). `compress_research` in `deep_researcher.py` becomes a thin node that calls `compress_with_recovery` and maps the outcome to the state. Failed results are emitted through the REQ-001 task-result type. Configuration flag `context_trimming` (default: baseline behaviour) so the improvement can be A/B-compared. | New `src/open_deep_research/context/` (`plan_trim`, `classify_token_limit`, `compress_with_recovery`, `TrimPlan` type, `TokenLimitExceeded` error); `deep_researcher.py` (`compress_research` becomes thin); `utils.py` (`is_token_limit_exceeded` kept, re-exported/delegated); `configuration.py` (one flag); `state.py` unchanged | Fits the blueprint module list (`context/`, REQ-005) and the thin-node rule; the trimming decision is pure and deterministic, so C-001/C-002/M-001/M-002 are unit-testable without any model; the classification bug (C-003) is fixed at one place; the failure path (C-004) is a typed result that the REQ-001 contract already expects; the flag keeps baseline behaviour until `verified` | More files and one new public interface; the module must not import `deep_researcher.py`, so the node supplies the task spec/topic to protect; coordination needed with the orchestration owner on the REQ-001 task-result type (shared contract, `structural-constraints.md` §6); tests must also prove the node is thin | Medium | High: `plan_trim`, `classify_token_limit` and the exhaustion path are pure functions tested with lists of fake messages and fake exception classes; only the loop needs a fake model |
| C | **Token-budget estimator ahead of the call (proactive trimming).** Instead of reacting to a provider error, the context module estimates the serialised size of the request with a token counter for the `compression_model` (using `utils.get_model_token_limit` plus a character/token heuristic), trims oldest whole turns before the first call so the request fits, and keeps the reactive token-limit branch only as a backstop. | New `context/` module with a counter and a budget planner; `configuration.py` (margin and counter settings); `deep_researcher.py`; `utils.py` | Avoids a wasted provider call and the per-turn removal loop; gives a deterministic pre-call invariant that is easy to monitor; helps models whose token-limit errors are not detectable by pattern | Token estimates are approximate (no universal tokenizer across OpenAI/Anthropic/Gemini), so a margin is still needed and the reactive path cannot be removed; the counter becomes a second source of truth that can drift from the provider; much larger scope than REQ-005 asks for (REQ-005's `out_of_scope` excludes token-limit configuration); a real tokenizer dependency would need human agreement (`AGENTS.md` §4) | High | Medium: the planner is testable with a fake counter, but the end-to-end guarantee (C-001) still depends on the reactive path, so it does not remove any test written for B |

**Choice:** **B** — a dedicated `context` module with a pure `plan_trim` decision, a single `classify_token_limit` entry point, and a `compress_with_recovery` loop called from a thin `compress_research`. It is the only option that keeps the safety-relevant decision deterministic and separately testable while staying inside the blueprint's module list, the thin-node rule and the REQ-005 scope. The remaining questions are settled inside B as follows: **(a)** the unit of removal is a *research turn* = one `AIMessage` + the `ToolMessage`s whose `tool_call_id` it issued (paired by id, not by position); **(b)** the protected region is the research topic / task specification, the compression instruction (always the last message), and the newest AI turn together with its tool results — computed from message types, not from the model's text, and the original message order is preserved when the list is rebuilt; **(c)** classification is `classify_token_limit(exc, configurable.compression_model)` and delegates unchanged to `utils.is_token_limit_exceeded` with no cross-provider fallback, because passing the compression model is what fixes C-003 and a fallback would let OpenAI's unguarded `invalid_request_error` rule misclassify other providers; **(d)** when `plan_trim` returns `None` the loop stops and the failure leaves the researcher subgraph through the declared `ResearcherOutputState.research_outcome` field — with category `token_limit`, or `provider_transient` when a non-token error exhausts its separate retry budget — together with a descriptive `compressed_research` sentence, and `supervisor_tools` reads the field through a guard whose `else` branch is the baseline line unchanged.

**Rejected and why:** **A**: the fix is correct but puts architectural logic in a graph node, against `structural-constraints.md` §2 and §8, and leaves the protected region untestable on its own; it would have to be moved once a second requirement touches compression. **C**: solves a different problem (avoiding the failed call) rather than REQ-005's problem (recovering correctly after it), needs a tokenizer with no provider-neutral answer and a new dependency, and contradicts REQ-005's stated scope boundary around token-limit configuration; the reactive path it keeps is exactly B, so C is a later extension on top of B, not an alternative to it.

**Ledger:** the rejected options are tracked as OPL-001 (A, Dropped) and OPL-002 (C, Deferred) in `docs/architecture/option-ledger.md`, together with the conditions that would reopen them. Risks this decision carries are RISK-001 to RISK-007 in `docs/architecture/risk-list.md`.
| A | Inline prompt fixes: reconcile each prompt's citation instructions independently, unifying the wording to `[n]` + `### Sources` + `[n] Title: URL` with a renumber-across-findings line. | `prompts.py` | Minimal; no new interface; fully offline-checkable. | Format still duplicated: the rules live independently in both prompts, so the drift mode that produced the defect survives; numbering correctness relies on the model. | Low | High |
| A2 | Shared constants defined directly in `prompts.py` and interpolated into both prompts. | `prompts.py` | Single source of truth; simplest possible; drift-proof; no new module; no dependency exception. | Contract lives in the shared baseline file with no owning module; no home for future INV-004 work; bypasses the blueprint §4 one-element-one-module ownership. | Low | High |
| B | Single shared citation contract: text constants in `citations/contract.py`, interpolated into both prompts at module load. | `citations/contract.py`, `prompts.py` | One source of truth, so the two prompts cannot drift; both prompts provably identical (C-003 trivial); fits blueprint §4 citations module; format-only. | Adds a `prompts.py → citations/contract.py` interface (approved exception to `structural-constraints.md` §5); needs brace-escaping discipline for `.format()`. | Medium | High |
| C | Deterministic post-processor that reformats/renumbers generated reports. | `prompts.py` (minor), `citations/` validator/rewriter | Strongest guarantee if it worked; would serve future INV-004. | Out of REQ-006 scope; implements the Deferred INV-004 property; cannot recover which URL backs an unsourced claim; expands scope (R1/R2). | High | Medium |

**Choice:** Option B — single shared citation contract. The stated defect is two instructions in one file drifting apart, so a single source of truth is what prevents recurrence while keeping the change format-only, offline-testable and inside the citations module. B wins over A2 on governance grounds: blueprint §4 assigns REQ-006 to the citations module (one architectural element = one module = one owner), whereas A2 leaves the contract unowned in the shared baseline file.

**Rejected and why:** A — reconciles the prompts inline but leaves the format duplicated, so the drift mode survives. A2 — drift-proof but leaves the contract unowned, with no home for INV-004 work and no §4 ownership. C — out of REQ-006 scope and owned by Deferred INV-004; a post-processor can reformat but cannot recover which URL backs an unsourced claim.

*Amended after module review: added Option A2 and rephrased Option A.*
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
| A | Harden `test/evaluators.py` in place and add a separate entry file | `test/evaluators.py`, `test/prompts.py`, a new entry script | Smallest file churn; baseline entry untouched; direct reuse of existing functions | Validation, judge construction, LangSmith serialisation and entry logic stay mixed; the import-time model side effect is harder to remove safely; no clean module boundary for pure tests | Low | Medium |
| B | New `test/evaluation/` core package plus a thin compatibility adapter in `test/evaluators.py` | New `test/evaluation/` package; `test/evaluators.py`; `test/prompts.py`; README | Deterministic validation and entry are separable and testable with a fake judge; judge is constructed lazily; baseline evaluator names and return shapes are preserved; `test/run_evaluate.py` unchanged; matches the blueprint module path | More files and an adapter mapping; a small amount of indirection | Medium | High |
| C | Duplicate the evaluators in a standalone evaluation service and leave the baseline untouched | New standalone service; existing scripts unchanged | Strong isolation from the benchmark path | Two sources of truth; REQ-009 fixes do not reach the benchmark; duplicated maintenance; violates “extend, never replace” | High | High |

**Choice:** option B — it separates deterministic validation and the evaluation-only entry from the LangSmith adapter, keeps the baseline entry compatible, and allows every REQ-009 and REQ-010 case to run offline with an injected judge. It also places the module at the path assigned by `architecture-blueprint.md` §4.

**Rejected and why:** option A: the core logic remains coupled to the evaluator functions and the import-time model construction, which makes failure isolation and offline tests harder to guarantee. option C: it duplicates metric logic, leaves the benchmark path broken, and creates two sources of truth for the same scores.

The decision, interfaces and implementation steps are in ADR-001.

**Open for module review:** the following remain proposed until SA Review:

- **Path whitelist:** `structural-constraints.md` §1 lists top-level `test/` as not for new work, while `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. BroZhai's suggestion is to add `test/evaluation/` as the only whitelisted `test/` subdirectory for new architecture code; tests remain in `test/offline/` and `test/live/`.
- **Evaluation judge client:** `judge.py` needs one lazy, injectable evaluation-only chat client, which is an exception to `structural-constraints.md` §4 because `configurable_model` lives in `deep_researcher.py` and §5 forbids importing it. Provider credential resolution is part of the same proposed exception.
- **Raw judge interface:** confirm that rating and `grounded` fields stay raw until `validation.py` checks them, before any Pydantic conversion.
- **Judge failure semantics:** confirm exit code `3` for judge initialisation, real OpenAI 401 `AuthenticationError` and 403 `PermissionDeniedError`, with per-metric results and completed scores preserved.
- **LangSmith live behaviour:** SDK type compatibility is checked; live `aevaluate` and UI behaviour with a null score remain `NOT_RUN`.

Confirm these at module review and integration.
