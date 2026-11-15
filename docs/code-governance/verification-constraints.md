# Verification Constraints

> **Purpose:** One shared way to decide that a requirement is really done.
> **Authoritative for:** verification layers, test conventions, commands, CI gates, verdicts and evidence, module test requirements and the Definition of Done.
> **Maintained by:** humans for §1–§6 and §8; each module owner writes their module's test requirements in §7, integrated before SA Review.
> **Last updated:** 2026-11-12

## 1. Three Verification Layers

| Layer | Meaning | Where it runs |
|---|---|---|
| **Structural** | Code organisation, schemas, module boundaries, docstring RIDs and lint conform to the rules | CI: schema and static-analysis gates |
| **Regression** | Existing behaviour and shared contracts still hold | CI: every suite in `test/offline/` |
| **Behavioural** | The requirement's behaviour meets its fit criterion | New offline tests; `test/live/` or `test/run_evaluate.py` when a case needs a real model; human confirmation |

## 2. Principles

1. Every fit-criterion check and metric in `requirements.yaml` has at least one test or a named piece of review evidence; its `verification` field points to it.
2. Every invariant has a test that fails when the invariant is violated.
3. A change runs its new tests and every prior offline suite; any regression blocks the merge.
4. Module test requirements (§7) are approved in SA Review (Gate 1) before tests are written, and the tests are approved before implementation (Gate 2). Tests are written by Test Author and never changed by Build.
5. Prefer deterministic offline tests; use live tests for final behavioural evidence only.

## 3. Test Conventions

- **Offline tests** (`test/offline/`) use fake models and fake researchers, make no network calls and need no API keys, so supervisor logic, termination, scheduling and context handling run in CI at no token cost.
- **Live tests** (`test/live/`) call real models or APIs, run on demand rather than on every commit, and are marked `automated: false` in `requirements.yaml` when a human must judge the result.
- **Names:** test files are named after the behaviour they cover, `test_<topic>.py` (for example `test_failure_propagation.py`); test functions describe the expected behaviour. Requirement IDs are not part of file names, so renumbering requirements does not rename tests.
- **Traceability:** the first line of every test module's docstring lists the RIDs it verifies, for example `"""REQ-002: no delegated task is lost or silently treated as completed."""`. The requirement's `verification` field gives the exact `path::test_name`.
- **Shared contract tests:** when a requirement defines a shared contract (`structural-constraints.md` §6), its contract tests live in `test/offline/test_contracts.py` and every PR runs them.

## 4. Commands

| Check | Command |
|---|---|
| Requirements schema and ID consistency | `uv run python scripts/validate_requirements.py` |
| Lint (gated paths) | `uv run ruff check src/open_deep_research test/offline scripts` |
| Type check (optional, not gated) | `uv run mypy src/open_deep_research` |
| Offline tests | `uv run pytest test/offline` |
| Live and evaluation tests | `uv run pytest test/live`, `uv run python test/run_evaluate.py` |

`ruff format` is applied to new files and changed lines only; do not reformat untouched baseline code. Install tools with `uv sync --extra dev`.

## 5. CI Gates

The course requires six blocking gates. Their state in `.github/workflows/ci.yml`:

| Course gate | CI job | What it checks | Status |
|---|---|---|---|
| Schema | `requirements-schema` | `requirements.yaml` against `req-schema.json`, plus unique and resolvable IDs | Active |
| Static analysis | `static-analysis` | `ruff check` on the gated paths | Active; mypy planned |
| Regression | `offline-tests` | `pytest test/offline` | Active; reports `NOT_RUN` while the directory has no tests |
| Test approval | — | The approval record has Gate 2 for every PR that changes `src/`, and the PR's tests match the approved test commit | Planned |
| AI-use log | — | `docs/ai-use-log.yaml` is valid and has an entry for the PR | Planned |
| Semantic evaluation | — | Live evaluation of fit criteria for prompt or model changes | Planned |

Lint debt outside the gated paths is tracked in `docs/debt-register.md`; a path joins the static-analysis gate once it is clean.

## 6. Verdicts and Evidence

- Verdicts are only `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED` and `N/A`. A skipped test is `NOT_RUN`, never `PASS`.
- No check is reported as passed without execution evidence. A mandatory check that is `FAIL`, `NOT_RUN` or `BLOCKED` keeps the requirement from `verified`.
- Evidence goes to `docs/test-reports/<task-id>.md`: the baseline run by Test Author and the verification by Verify, each with commit, commands, verdict per check, and logs or diffs where relevant.
- Offline tests run without network or secrets (§3). Verify changes no file other than its report; the PR diff shows any change made during verification.

## 7. Module Test Requirements

Copy the example for your module. Every acceptance criterion (C-/M-) of the module's requirements and every invariant it enforces needs at least one case, and the module lists the existing suites it can affect. At integration, check that no criterion or invariant is left without a case.

### <Module> (REQ-NNN, ADR-NNN)

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-001 | REQ-NNN C-NNN | normal | | | `test/offline/<file>::<test>` |
| TC-002 | INV-NNN | exception | | | |
| TC-003 | REQ-NNN M-NNN | boundary | | | |

- **Regression:** existing suites to re-run, including `test/offline/test_contracts.py` if a shared contract changes.
- **Live or human checks:** cases marked `automated: false` in `requirements.yaml`, and where their evidence goes.

### orchestration (REQ-001, REQ-003; EVAL-002, ADR-002 — Proposed)

Every case below is **PLANNED**; no test code or implementation has been written for this submission, and no functional result is claimed. Test Author proceeds only after Gate 1, records meaningful baseline failures, and obtains Gate 2 before Build. Paths and symbols in the acceptance table reproduce the approved requirement references exactly. Additional cases test externally observable contracts, state transitions and failure boundaries rather than helper internals.

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| ORC-001 | REQ-001 C-001; INV-006 | normal | One scripted valid delegation | Researcher receives registered id, scope, nonempty required questions and bounded budget passing schema validation | `test/offline/test_task_contract.py::test_delegation_is_valid_task_spec` |
| ORC-002 | REQ-001 C-002; INV-006 | boundary | Two of three questions have same-task retrieved-source findings | Code derives partial status, coverage 2/3 and the unanswered original question in the reason | `test/offline/test_task_contract.py::test_status_derived_from_sourced_findings` |
| ORC-003 | REQ-001 C-003; INV-006 | exception | A claimed answer cites a URL no successful task tool returned | Drop that finding and derive status only from remaining valid findings | `test/offline/test_task_contract.py::test_unretrieved_source_does_not_count` |
| ORC-004 | REQ-001 C-004; INV-006 | exception | Researcher result violates the schema | Terminal failed result has category `invalid_result`, no findings and no report notes | `test/offline/test_task_contract.py::test_malformed_result_becomes_failed` |
| ORC-005 | REQ-001 M-001; INV-006 | metric | Sourced and forged-source findings mixed | `unsourced_finding_counted_count == 0` | `test/offline/test_task_contract.py::test_unretrieved_source_does_not_count` |
| ORC-006 | REQ-003 C-001; INV-003 | normal | Scripted results answer every required question, with and without ResearchComplete | Exit `covered` at the joined turn boundary | `test/offline/test_research_termination.py::test_full_coverage_exits_covered` |
| ORC-007 | REQ-003 C-002; INV-003 | boundary | Coverage 0.5, threshold 0.8, completion request | Continue and give supervisor the original unanswered questions | `test/offline/test_research_termination.py::test_complete_below_threshold_is_refused` |
| ORC-008 | REQ-003 C-003; INV-003 | boundary | Two unchanged delegation turns with a think-only turn between | Ignore think-only for the streak, then exit `stalled` after the second eligible unchanged turn | `test/offline/test_research_termination.py::test_turns_without_progress_exit_stalled` |
| ORC-009 | REQ-003 C-004; INV-003 | boundary | Coverage below threshold at iteration cap | Exit `budget_exhausted` through the common selector | `test/offline/test_research_termination.py::test_iteration_cap_exits_budget_exhausted` |
| ORC-010 | REQ-003 C-005; INV-003 | exception | Supervisor model raises on every configured retry with no higher-priority condition | Exit `failed` with detail; no unhandled model exception and no extra retry loop | `test/offline/test_research_termination.py::test_supervisor_model_error_exits_failed` |
| ORC-011 | REQ-003 C-006 | live | Two exact historical baseline queries, reviewed model/search configuration | At least one covered exit and at most one cap exit, with per-run reasons and evidence | `test/live/test_research_termination_live.py::test_baseline_queries_exit_reasons` |
| ORC-012 | REQ-003 M-001; INV-003, INV-007 | metric | All exit fixtures and exception paths | `exit_without_single_reason_count == 0` across the suite | `test/offline/test_research_termination.py` |
| ORC-013 | REQ-003 M-002; INV-003 | metric | Repeated completion requests below threshold | `premature_complete_accepted_count == 0` | `test/offline/test_research_termination.py::test_complete_below_threshold_is_refused` |

Additional planned contract, boundary and integration cases:

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| ORC-014 | INV-003; actual budget | boundary | Budget 2, a batch of 4 local executable calls including a failure and think_tool | Reserve at most 2 permits before awaitables start; count every started invocation including failure/think; denied calls and ResearchComplete control cost zero | `test/offline/test_task_contract.py::test_tool_budget_counts_started_invocations` |
| ORC-015 | INV-003; watchdog | boundary | No-tool, think-only and ResearchComplete researcher turns | Actual tool count remains distinct from the existing bounded model-turn watchdog; no unbounded model loop | `test/offline/test_task_contract.py::test_tool_budget_separate_from_model_turn_watchdog` |
| ORC-016 | INV-006; failure costs | exception | Tools start, then researcher/compression raises; sibling succeeds; unrun spec also present | Failed task retains exact started-invocation cost and available reported token totals; missing/malformed usage makes usage_complete False without inventing zero or billing completeness; sibling unchanged; not_run has known zero spend | `test/offline/test_task_contract.py::test_failure_preserves_execution_cost` |
| ORC-017 | INV-006; provenance authority | adversarial | Model invents retrieved_urls/cost/status; another task has the URL; fake or mismatched ToolMessage id, error or think text contains it | Only matching successful receipts establish URLs/cost; prose and cross-task evidence cannot forge coverage. Fake model inspects actual config/ambient context: no live holder or private evidence key, including inherited/bound config | `test/offline/test_task_contract.py::test_model_cannot_forge_task_evidence` |
| ORC-018 | INV-006; trim/checkpoint | regression | Old tool messages are trimmed before compression retry; serializable task_evidence_snapshot is restored | Full task receipt still establishes true cost and retrieved URLs; spec and protocol remain present; history removal cannot create or erase executed evidence | `test/offline/test_task_contract.py::test_task_evidence_survives_context_trimming` |
| ORC-019 | INV-003; native compatibility | exception | Orchestration enabled with native OpenAI/Anthropic search, lacking strict caps/counting; flag-off comparison | Enabled researcher path rejects before its first native-capable model request; that fake researcher request count stays zero; flag-off search validation remains unchanged and no provider is silently substituted | `test/offline/test_task_contract.py::test_native_search_rejected_before_enabled_model_call` |
| ORC-020 | INV-006; schema | boundary | Whitespace/duplicate questions, empty valid list with valid topic, >5 distinct questions, boolean/negative/nonfinite costs, duplicate source ids/URLs, mismatched spec id/questions | Stable question normalization preserves first original text; empty valid list falls back to topic; other invalid structures fail closed without truncation or fabricated questions | `test/offline/test_task_contract.py::test_strict_schema_boundaries` |
| ORC-021 | INV-006, INV-007; raw intent | exception | Missing topic, unusable questions or malformed ConductResearch args | One rejected diagnostic and matching tool response; no researcher call, fake question or coverage contribution; no silent raw-call drop | `test/offline/test_task_contract.py::test_invalid_delegation_is_rejected_without_fake_question` |
| ORC-022 | INV-006; sidecar | boundary | Exactly one v1 sidecar; missing/duplicate fences, extra JSON fields, bool source number, bad source refs, unretrieved exact URL | Parse only the specified schema before the unique final Sources section; schema errors yield invalid_result; syntactically valid unsourced findings are dropped before deriving status; do not rewrite URL query/fragment | `test/offline/test_task_contract.py::test_sidecar_schema_and_source_resolution` |
| ORC-023 | INV-007; sidecar isolation | regression | Context returns raw prose, a valid sidecar and Sources, including unsupported prose/placeholder text | Adapter discards the raw body and sidecar from reader-facing summary/compressed_research, renders only complete/partial validated findings/sources, and preserves ConductResearch tool name | `test/offline/test_task_contract.py::test_sidecar_is_removed_from_supervisor_summary` |
| ORC-024 | INV-007; REQ-002 C-007 interface | adversarial | Summary contains unsupported prose, failure/placeholder text and reflection, alongside validated findings; a failed/unanswered task has only tangential sourced findings with empty answers | Final notes include only complete/partial tasks' validated claims/sources; failed tasks, raw prose, sidecars and diagnostics contribute nothing | `test/offline/test_task_contract.py::test_notes_render_only_validated_findings` |
| ORC-025 | INV-003; cap counting | boundary | N=1 and N=2 with delegation, think-only, completion-only and zero-tool supervisor turns | completed_supervisor_turns increments once after each processed/joined turn; all-delegation below-threshold fixture dispatches exactly 1 turn for N=1 and exactly 2 for N=2; no supervisor request N+1 or post-cap dispatch; flag-off old counter unchanged | `test/offline/test_research_termination.py::test_iteration_cap_counts_n1_n2` |
| ORC-026 | INV-003; exit priority | boundary | covered+cap+stall+fatal-model conditions, and each lower-priority combination | One reason in order covered > budget_exhausted > stalled > failed, including fatal-model and resumed entry paths | `test/offline/test_research_termination.py::test_exit_reason_precedence` |
| ORC-027 | INV-003, INV-007; denominator | boundary | Cap snapshot has 4/5 answered and two new pending questions; comparison with no new questions | Register pending valid specs and not_run results first: 4/7 selects budget_exhausted, whereas unchanged 4/5 at threshold selects covered; no stale run_coverage used | `test/offline/test_research_termination.py::test_pending_questions_registered_before_exit_selection` |
| ORC-028 | INV-003; refused completion | boundary | Repeated completion-only/zero-tool supervisor turns below threshold, mixed completion+delegation, pure think-only | Completion/zero-tool are eligible unchanged attempts and may stall/cap; mixed turns process delegation unless already capped; think-only consumes cap without changing streak | `test/offline/test_research_termination.py::test_completion_only_and_no_tool_turns_are_bounded` |
| ORC-029 | INV-003, INV-006; coverage | boundary | Case/whitespace-equivalent questions, failed then rerun task, empty ledger, thresholds 0/NaN/>1 and decimal 0.3/0.8 equality | Distinct-question union counts failed questions and later answers once; empty run cannot be covered; invalid threshold rejected; threshold uses decimal Fraction(str(value)), never binary-float Fraction(value) | `test/offline/test_research_termination.py::test_question_normalization_and_empty_run_guard` |
| ORC-030 | INV-003; exact stall | boundary | Coverage increases, decreases after new questions, or remains the same exact fraction | Only exact Fraction equality increments unchanged_eligible_turns; changed coverage resets it; think-only neither increments nor resets | `test/offline/test_research_termination.py::test_stall_resets_on_changed_coverage` |
| ORC-031 | INV-006; shared schema | boundary | Valid/invalid status-category-reason-coverage combinations, malformed costs and spec binding | Reject inconsistent TaskResult; complete has no failure reason, partial is unanswered, structural failures have empty findings/summary | `test/offline/test_contracts.py::test_task_result_contract_boundaries` |
| ORC-032 | INV-007; final reader | boundary | Baseline snapshot, complete final run, duplicate ids, results without exit_reason, inconsistent coverage/detail | from_state returns None only for baseline; validates final RunRecord or raises ValueError; running supervisor deltas are not passed to this final reader | `test/offline/test_contracts.py::test_run_record_final_snapshot_contract` |
| ORC-033 | INV-007; reducer | regression | Two plain result deltas then explicit final override envelopes for results/notes | Deltas append in order; final envelopes replace, preserving exactly one final run without old notes | `test/offline/test_contracts.py::test_task_results_reducer_append_and_override` |
| ORC-034 | INV-003, INV-006, INV-007; shared fixtures | regression | Plain independent fixtures for baseline, full/threshold covered, stalled, budget/not_run, all-child-failed budget, zero-task supervisor failure | Every final nonbaseline fixture satisfies RunRecord and every negative mutation is rejected; no construction depends on the implementation under test | `test/offline/test_contracts.py::test_task_and_run_contract_fixtures` |
| ORC-035 | INV-006; tool compatibility | regression | Baseline and enabled supervisor tool bindings | Original ConductResearch shape remains flag-off; enabled tool advertises the exact same ConductResearch name with the proposed typed args | `test/offline/test_contracts.py::test_conduct_research_tool_name_compatible` |
| ORC-036 | INV-003, INV-006, INV-007; flags | integration | Four orchestration/context flag pairs, each with fresh state, compression success and token/runtime failures | off/off exact baseline; on/off typed orchestration with baseline context trimming; on/on context recovery then strict parser; off/on follows the explicitly reviewed context/delivery policy without fake orchestration fields | `test/offline/test_orchestration_integration.py::test_flag_combinations` |
| ORC-037 | INV-003, INV-006; retry ownership | exception | Repeated compression token errors with both flags enabled, plus a non-token error | Each attempt executes in the clean Runnable context; one context retry loop with at most 3 attempts; no nested orchestration retry; typed failure retains evidence; non-token failure follows reviewed delivery boundary | `test/offline/test_orchestration_integration.py::test_compression_has_one_retry_owner` |
| ORC-038 | INV-007; receipt replay | regression | Resume/replay an already terminal tool_call_id and a genuinely pending cap-held call | delegation_receipts prevents duplicate registration/results and relabelling a finished task; pending valid call alone becomes not_run | `test/offline/test_orchestration_integration.py::test_receipt_replay_does_not_duplicate_tasks` |
| ORC-039 | INV-003, INV-007; lifecycle | regression | Two main invocations reuse a thread/checkpoint context | New run resets task ids, completed_supervisor_turns, unchanged_eligible_turns and delegation_receipts; private progress/evidence do not leak to final main state | `test/offline/test_orchestration_integration.py::test_new_run_resets_private_progress` |
| ORC-040 | INV-007; join/finalization | integration | One immediate failure, one still-running successful sibling, old main notes/results | No finalization before join; brief clears old parent lists, child finalizer overrides its channels, compiled output appends once to empty parent lists; one consistent final snapshot with sibling evidence | `test/offline/test_orchestration_integration.py::test_finalization_joins_then_replaces_notes_and_results` |
| ORC-041 | INV-006; context authority | adversarial | Untrusted retrieved instructions, JSON braces, trimmed history, immutable brief/spec and final compression instructions | Deterministic message order preserves authority and reinserts the spec/protocol on each attempt; spec/source text is quoted data; fake model attempts cannot override code-owned budget/status/exit; no prompt-injection immunity is claimed; JSON survives formatting | `test/offline/test_orchestration_integration.py::test_enabled_context_assembly_preserves_authority` |
| ORC-042 | REQ-002 C-005 contributor; INV-007 | boundary | Cap-held final turn with two valid unrun delegations | Both have terminal failed/not_run results before final coverage and exit selection; no researcher invocation | `test/offline/test_failure_propagation.py::test_delegations_left_at_exit_are_failed` |

| ORC-043 | INV-003, INV-006, INV-007; invalid tool transport | adversarial | Missing/blank/non-string tool-call ID, changed arguments under a terminal ID, unknown tool name, and cap-entry rejected receipt whose diagnostic is pending | Invalid-ID turn is rejected before registration and diagnosed without fake ToolMessage IDs; conflicting replay preserves old result/Q; unknown executable name costs zero and is diagnosed; valid mixed-turn work remains bounded; entry finalization emits pending diagnostics once per stable response ID without dispatch/model calls or added task/Q | `test/offline/test_orchestration_integration.py::test_malformed_tool_transport_is_bounded` |

| ORC-044 | REQ-001 C-004; REQ-002 C-002/C-004/C-007 contributor; INV-006/007 | integration | Three accepted calls under concurrency 1 and 2: A succeeds slowly, B raises after 2 starts with missing usage, C has invalid typed output; additionally a valid failed/token_limit TaskResult omits legacy compressed_research | JoinedTurn returns A/B/C order after every child joins; truthful per-task cost/categories; node merges feedback in call order. Valid typed failure with missing auxiliary string is rendered canonically without a second result or placeholder; real producer fills all mandatory output fields | `test/offline/test_failure_propagation.py::test_joined_turn_preserves_registration_order` |
| ORC-045 | INV-003/006/007; REQ-004 limitations interface | boundary | T1 answers Q1–Q8, T2 answers Q9 of Q9/Q10, failed T3 repeats Q1; valid source receipts | Run coverage is 9/10, not a task-count ratio; global unanswered list is [Q10], T3.unanswered remains [Q1]; covered exit still permits delivery partial because not every task is complete. No new serialized unanswered field or reason parsing | `test/offline/test_contracts.py::test_run_unanswered_questions_use_validated_answers` |
| ORC-046 | INV-006/007; context integration | integration | Both flags on: failure/failure/normal-return with a shorter current message list per trim; then all 3 fail; then malformed sidecar on a returned string with matching normal observation | At most 3 compression model invocations, one parse after matching normal return, none on failed requests, no schema-repair retry; caller retains evidence through clean model context; required output fields/category/cost preserved; protected instruction position follows current list | `test/offline/test_orchestration_integration.py::test_compression_returns_canonical_output_once` |
| ORC-047 | REQ-001; INV-003/INV-006 | boundary | Budget 2; reserve two, cancel one before start, start/fail the other; then admit/start one replacement and validate twice | One holder and count; actual starts=2, cancelled reservation=0; failure is not refunded; validation spends nothing; no duplicate budget state or extra queue | `test/offline/test_task_contract.py::test_budget_and_evidence_share_one_start_count` |
| ORC-048 | REQ-001 C-002/C-004; INV-006 | boundary | Same complete sidecar/Sources with normal versus length observation; length again with damaged JSON | Normal enters existing parser once; either length returns failed/token_limit before parsing, with actual cost and empty findings/summary; no schema/length retry and one terminal result | `test/offline/test_task_contract.py::test_output_length_precedes_sidecar_parsing` |
| ORC-049 | REQ-001 C-004; INV-006/INV-007 | adversarial | Successful context string but missing, malformed, unsupported or conflicting marker; absent/stale/wrong-operation observation | Unknown maps failed/runtime with a bounded diagnostic, zero parses and no extra model request; never manufacture stop, token_limit or invalid JSON; retained spend survives | `test/offline/test_task_contract.py::test_unobserved_compression_is_runtime_failure` |
| ORC-050 | REQ-003 C-005/M-001; REQ-001; INV-003/INV-006/INV-007 | integration | Supervisor/researcher length or unknown response contains a valid-looking ConductResearch/tool intent; prior successful tasks exist | No new intent registers or executes. Supervisor uses existing model-operation-error selector and covered/cap/stall priority, no extra retry or fake task/question; researcher uses isolated child runtime failure with retained cost; old terminal results remain unchanged | `test/offline/test_orchestration_integration.py::test_incomplete_control_response_executes_no_intents` |
| ORC-051 | REQ-001; REQ-005 contributor; INV-006/INV-007 | integration | Compression throws twice then returns normal/length/unknown on attempt 3; concurrent tasks and an earlier successful operation have distinct markers | Context alone makes at most 3 logical calls; observer records each once and returns/re-raises unchanged; last returned attempt is matched by operation/phase/task. Normal parses once, length/unknown zero times; no holder leaks to provider config or cross-task observation reuse | `test/offline/test_orchestration_integration.py::test_completion_observation_matches_returned_operation` |
| ORC-052 | REQ-002 C-002/C-004/C-007 contributor; INV-006/INV-007 | integration | One child compression length-ends after two tool starts; a slower sibling returns normal validated findings | All children join; original registration order; failed child keeps cost and has no findings/summary; successful sibling remains; notes contain only accepted findings and no truncated prose/diagnostic | `test/offline/test_failure_propagation.py::test_truncated_child_keeps_successful_sibling` |
| ORC-053 | REQ-001; INV-006 | boundary | Captured school stop/length/tool_calls metadata, phase changes, unsupported marker, explicit length plus parseable content | Supported adapter maps stop normally, tool_calls normally only for control phases, length as truncated; plain compression tool_calls and unsupported/missing markers are unknown. Schema/tool checks still apply; observation wrapper preserves the response and adds no provider fallback | `test/offline/test_task_contract.py::test_completion_marker_mapping_is_phase_specific` |

- **Regression:** after approved tests and implementation, run all `test/offline` suites, including the planned shared contracts and the delivery/context/citation/search/evaluation suites as they are added. Test doubles forbid network/model calls and need no credentials. At this SA checkpoint `test/offline/` contains a placeholder rather than functional test modules; that is NOT_RUN, not a passing regression suite.
- **Live or human checks:** ORC-011 is NOT_RUN. The coordinator recovered the two exact queries below by reading historical `docs/orchestration/trace_run.py` L43–45; the repository evidence note is `transcripts/raw/61061965-XIE_Shentai/baseline-query-reference.md`. The script was not executed. Its historical setup used the school router, `SEARCH_API=none`, `MAX_RESEARCHER_ITERATIONS=3`, `MAX_REACT_TOOL_CALLS=3`; that search-disabled setup cannot establish sourced coverage. A human must decide a permitted source-capable configuration and comparability before execution; preserve query text and record every configuration difference. No live model/search call is authorised by this test inventory.

| Historical query key | Exact query text for the planned live case |
|---|---|
| simple | 用三句话介绍 LangGraph 的 Command 对象 |
| compare3 | 比较 LangGraph、AutoGen、CrewAI 三个框架在多 agent 编排(任务拆分、并行执行、终止条件)上的差异,每个框架各给两条优点和两条缺点 |

- **Interface review before Gate 1:** confirm raw-intent rejection versus accepted-delegation semantics with delivery; receipts and keyword-only evidence with all TaskResult readers; the exact sidecar/prompt contract with citations; retry ownership and all four flag outcomes with context/delivery; and enabled native-search rejection with search. ORC-036's off/on failure result remains BLOCKED on that human policy decision; no expected result may be invented by Test Author.
- **Evidence:** the coordinator reports the requirements schema check passed for 10 requirements; this is structural validation only. All cases above remain PLANNED with execution verdict NOT_RUN, except the identified pending policy whose eventual dependent case is BLOCKED. Human approvals, baseline failures, functional PASS and live outcomes must be recorded by the later authorised roles, never inferred from this design.

## 8. Definition of Done

| # | Condition | Done by |
|---|---|---|
| 1 | Every fit-criterion item has an approved test or recorded review, and the tests pass | Test Author (tests), Build (passing), confirmed by Verify |
| 2 | All prior offline suites pass | Verify |
| 3 | All active CI gates are green | CI |
| 4 | Behaviour conforms to the fit criterion, with evidence in `docs/test-reports/` | Verify, confirmed by a human |
| 5 | `trace-matrix.md` row complete for architecture, code and tests | Module owner |
| 6 | If a boundary changed: `invariants.md` updated and its test passes | Human, Test Author |
| 7 | If an architectural decision arose: ADR accepted or `evaluation-table.md` entry recorded | Human |
| 8 | `docs/ai-use-log.yaml` and `docs/review-memo.md` updated | Human |
| 9 | Gate 3 passed: two approvals, PR merged | Humans |
| 10 | `status` in `requirements.yaml` advanced to `verified` | Human |
