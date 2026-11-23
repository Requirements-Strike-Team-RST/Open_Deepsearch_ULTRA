# Review Memo

> **Purpose:** Records of SA Reviews (Gate 1), pull request reviews (Gate 3) and the human reviews named in a requirement's fit criterion (`automated: false` checks).
> **Maintained by:** reviewers.
> **Last updated:** 2026-11-16

## SA Review Template

### SA-NNN: <scope, e.g. architecture of all modules>

- **Date:** YYYY-MM-DD
- **Participants:** <names>
- **Reviewed:** ADR-NNN, EVAL-NNN, module sections in `invariants.md`, `memory-design.md`, `runtime-policy-catalog.md`, `structural-constraints.md` §10, `verification-constraints.md` §7, `trace-matrix.md`

| Item | Finding | Resolution |
|---|---|---|
| ADR-NNN | | |

- **Decision per ADR:** ADR-NNN Accepted | changes requested
- **Outcome:** Gate 1 passed for REQ-NNN, ... | another review needed

## PR Review Template

### PR #NNN: <title>

- **Requirements:** REQ-NNN
- **Author / reviewers:** <names>
- **Date:** YYYY-MM-DD
- **Verification evidence checked:** `docs/test-reports/<task-id>.md`, CI run link
- **Findings:** issues raised and how each was resolved.
- **Decision:** approved | changes requested

## Requirement Review Template

### REVIEW-NNN: <requirement and check, e.g. REQ-007 C-005 search provider configuration review>

- **Reviewer:** <name>
- **Date:** YYYY-MM-DD
- **Procedure:** what the reviewer did.
- **Verdict:** PASS | FAIL | NOT_RUN | BLOCKED | N/A, with reasons.

## Records

### PR #12: docs(sa): REQ-007 Search Configuration Validation Architecture

- **Requirements:** REQ-007 (upstream langchain-ai/open_deep_research#250)
- **Author / reviewers:** sszfot / BroZhai, AlchemyHAN
- **Date:** 2026-11-13 to 2026-11-16
- **Verification evidence checked:** `docs/architecture/adr/001-search-configuration-validation.md`, `docs/architecture/evaluation-table.md` (EVAL-001), `docs/architecture/invariants.md` (INV-005), `docs/code-governance/structural-constraints.md` §10, `docs/code-governance/verification-constraints.md` §7 (TC-001–TC-026 planned), `docs/ai-use-log.yaml` (AIU-008, AIU-009). CI: Requirements schema, Static analysis and Offline tests all PASS. Behavioural and acceptance tests NOT_RUN (documentation only).
- **Findings:** issues raised and how each was resolved.
  - **Transcript file name and redaction (BroZhai):** renamed `transcripts/AIU-008-REQ-007-opencode.md` to `transcripts/<SID>-<Name>.md` and removed the local username from the `ls` output in the transcript.
  - **Runtime MCP loading failure (BroZhai, U-1):** a correct MCP connection setting that still fails to connect must tell the user the MCP is unavailable and stop the process. Recorded as the runtime MCP-failure policy and settled from discussion #19.
  - **C-003 baseline was wrong (AlchemyHAN):** `Configuration.from_runnable_config` (`configuration.py:236-247`) already rejects unknown `search_api` values through pydantic (`"bing"`, `""`, `"TAVILY"` raise `ValidationError`), while `None` is filtered and falls back to `tavily`, so the validator never saw unknown values. The design now validates the raw `config["configurable"]` (accounting for environment overrides such as `SEARCH_API`) or wraps the `ValidationError` at the call site; §2 and the `None` expectation in TC-003 were corrected.
  - **Open decisions U-1–U-4 (AlchemyHAN):** discussed in repository discussion #19 and written into ADR-001, the runtime-policy catalog and the test cases.
  - **Thin test cases (AlchemyHAN):** added a valid native-provider case for C-001, an ordering test using a fake model with a call counter (0 model calls with `allow_clarification` both True and False), empty-MCP-url and missing-auth-token cases for C-002, removed the duplicate TC-005, gave each new INV-005 clause its own case, and added a default-config (`tavily` + `openai:gpt-4.1`) regression case.
  - **Call sites vs. "every entry path" (AlchemyHAN):** stated that `deep_researcher` is the only public entry and removed or justified the redundant `researcher` check.
  - **INV-005 rework (AlchemyHAN):** U-2 resolved, wording aligned with the `memory-design`/blueprint change, statement shortened to the template's one-or-two sentences, and the non-guarantee "static declaration ≠ runtime availability" moved out of the invariant.
  - **Small fixes (AlchemyHAN):** TC-004 now names `tavily_search` (the tool `.name`, not the `web_search` metadata); `POL-DEF-001` renamed to the `POL-NNN` format.
- **Decision:** approved (changes requested handled in the follow-up commits to the module branch)

### PR #13: docs(sa): REQ-006 unified citation format

- **Requirements:** REQ-006 (upstream langchain-ai/open_deep_research#232)
- **Author / reviewers:** NoPumpkinz / AlchemyHAN
- **Date:** 2026-11-13 to 2026-11-16
- **Verification evidence checked:** `docs/architecture/adr/001-unified-citation-format.md`, EVAL-001, INV-006, `docs/code-governance/structural-constraints.md` §5 and §10, `docs/code-governance/verification-constraints.md` §7 (TC-001–TC-006 planned). CI: Requirements schema, Static analysis and Offline tests all PASS. Behavioural tests NOT_RUN (documentation only).
- **Findings:** issues raised and how each was resolved.
  - **EVAL missing the simplest option (AlchemyHAN):** added Option A2 (shared constants defined directly in `prompts.py`, no new module) and rephrased Option A so it is no longer a straw man. The choice of B now states the governance reason: blueprint §4 assigns one architectural element to one module/owner, and `citations/contract.py` gives future INV-004 work a home.
  - **Repeated contract (AlchemyHAN):** `CITATION_RULES_BLOCK` states the format exactly once; `SOURCES_SECTION_SPEC` became `SOURCES_SECTION_POINTER` (a pure pointer); `RENUMBER_ACROSS_FINDINGS_INSTRUCTION` refers to the Citation Rules without restating them, so each assembled prompt carries the sources instruction once, as C-001 requires.
  - **No deterministic pass/fail rules (AlchemyHAN):** replaced the rules in ADR §7 and `verification-constraints.md` with exact-once occurrence counts, zero-count banned strings (`[Title](URL)`, `List of All Relevant Sources`, …), byte-identical block comparison for `[n] Title: URL` lines, and the explicit rule that every offline assertion must FAIL on the baseline for the registered reason.
  - **Case types misaligned (AlchemyHAN):** TC-003 retyped as a normal case and compares the text between `<Citation Rules>` tags byte-for-byte across both prompts; TC-004 formats both assembled prompts with all four real placeholders (`research_brief`, `messages`, `findings`, `date`, per `deep_researcher.py:642-647`) and asserts no contract placeholder survives; new negative case TC-005 (`test_format_checks_detect_violations`) feeds synthetic violating texts to the checks; the live case was renumbered TC-006.
  - **Unaccounted instructions L296/L302/L306 (AlchemyHAN):** recorded in ADR §3 — L302's "separate line item" is folded into "one per line", L306 and L296 stay because they specify no format, and the entry format is `[n] Title: URL` one per line per the approved REQ-006 statement (adding bullets would require a `requirements.yaml` change).
  - **Truncation affects C-004 (AlchemyHAN):** ADR §8 now records the retry-truncation risk at `deep_researcher.py:682` (`findings[:findings_token_limit]` can drop a later researcher's `### Sources` block, breaking renumbering); TC-006 excludes runs that triggered truncation retries and reports them separately; flagged to the REQ-005 owner.
- **Decision:** approved (changes requested handled in commit `ee9e4ee` on the module branch)

### PR #14: docs(sa): REQ-005 Context Compression Architecture

- **Requirements:** REQ-005 (associated issues #283, #284)
- **Author / reviewers:** BroZhai / AlchemyHAN, BroZhai
- **Date:** 2026-11-13 to 2026-11-16
- **Verification evidence checked:** `docs/architecture/adr/005-context-compression.md`, EVAL-001, INV-001, `docs/architecture/memory-design.md` §5, `docs/architecture/runtime-policy-catalog.md` (POL-001–POL-003), `docs/architecture/risk-list.md` (RISK-001–RISK-007), `docs/architecture/option-ledger.md`, `docs/code-governance/structural-constraints.md` §10, `docs/code-governance/verification-constraints.md` §7 (TC-001–TC-012 and their test names). CI: Requirements schema, Static analysis and Offline tests all PASS. Behavioural tests NOT_RUN (documentation only).
- **Findings:** issues raised and how each was resolved.
  - **`memory-design.md` reverted (AlchemyHAN):** the branch had deleted §1–§5 of `main`'s template through an 8/38 diff. Restored from `origin/main` and the context section appended instead, so the diff is now additive (17/0 at that round).
  - **`token_limit` cannot leave the researcher subgraph (AlchemyHAN):** `ResearcherOutputState` is a two-field pydantic model, so an undeclared key is dropped and `supervisor_tools` only sees a missing `compressed_research`. Declared the output field `research_outcome` and later added the consumer guard in `supervisor_tools` L308-313, whose `else` branch is the baseline expression character for character, so the flag-off path is unchanged.
  - **Flag-off behaviour contradicted itself (AlchemyHAN):** step 10 edited `supervisor_tools` and required a zero-hit grep while step 8 promised an unchanged baseline. Resolved by keeping the baseline branch untouched, changing the grep rule to "exactly two intentional hits, neither on the `context_trimming = True` path", rewriting TC-010/TC-011, and rewriting RISK-007.
  - **Non-token errors do not "propagate as today" (AlchemyHAN):** the baseline retries three times and then returns the placeholder, so re-raising would be a regression that also discards every parallel researcher through `asyncio.gather`. The new path retries without trimming and ends the task `failed`, and the category is now named `provider_transient` (carried by `TransientCompressionError`) instead of an unnamed REQ-001 value.
  - **Attempt budget could not match REQ-005 (AlchemyHAN):** a fixed budget of 3 removes at most two turns. The budget is now derived from the removable turns, then split into two independent counters after the follow-up review (see below).
  - **`max_removals` never passed (AlchemyHAN):** the signature default changed from `None` (removes everything) to `1` and the node passes `max_removals_per_attempt=1` explicitly, so the caller never relies on an implicit value.
  - **`segment_turns` problems (AlchemyHAN):** turns are now paired by `tool_call_id` rather than position (7a); the unreachable `trailing` branch removed and an orphan `ToolMessage` is described instead (7b); the rebuild preserves preamble → surviving turns → instruction-last order and `instruction_index` is only a segmentation input (7c).
  - **Unnecessary cross-provider fallback (AlchemyHAN):** removed; `classify_token_limit` now delegates unchanged to `utils.is_token_limit_exceeded(exc, model_name)`, and ADR §3(c) records the misclassification mechanism (the OpenAI `invalid_request_error` rule checked without a provider guard).
  - **Smaller fixes (AlchemyHAN):** stale `005-context-adr.md` references updated to `005-context-compression.md`; `ADD-005` typo corrected to `ADR-005`; TC-007–TC-009 test names added to ADR §7.
  - **Writer without a reader and short retry budget (BroZhai follow-up):** a declared-but-unread `research_outcome` still loses the failure, and `compressed_research` was left as `...`. Added the `supervisor_tools` read guard, defined the failure `compressed_research` sentence, and split the single budget into `max_trim_attempts` (removable turns + 1) and `max_transient_attempts` (3, the baseline value), so a one-turn history still gets three transient retries. TC-008 gained its three cases, TC-012 asserts all removable turns are consumed, and RISK-005 is marked Resolved.
- **Decision:** approved (both review rounds addressed)

### PR #15: docs(sa): REQ-009 and REQ-010 Evaluation Architecture

- **Requirements:** REQ-009, REQ-010 (upstream langchain-ai/open_deep_research#234)
- **Author / reviewers:** DopplerXD / AlchemyHAN, BroZhai
- **Date:** 2026-11-13 to 2026-11-16
- **Verification evidence checked:** `docs/architecture/adr/001-evaluation-module.md`, EVAL-001, INV-006 and INV-007, `docs/architecture/runtime-policy-catalog.md` (POL-002–POL-011), `docs/code-governance/structural-constraints.md` §10, `docs/code-governance/verification-constraints.md` §7 (TC-EVAL-001–TC-EVAL-023 planned), `docs/ai-use-log.yaml` (AIU-008, AIU-009). CI: Requirements schema, Static analysis and Offline tests all PASS. Behavioural, authentication-mapping and live LangSmith checks NOT_RUN.
- **Findings:** issues raised and how each was resolved.
  - **`test/evaluation/` path conflict (BroZhai):** the new folder contradicts `structural-constraints.md`. Proposed adding explicit `test/evaluation/` rows to the human-maintained structural layout as a whitelist, pending integration.
  - **INV-007 contradicts the dependency allowlist (AlchemyHAN):** importing `open_deep_research.utils.get_today_str` pulls in `AsyncTavilyClient`, `MultiServerMCPClient` and the Tavily tool at import time. Replaced with local standard-library date formatting; the ADR sections 2/3.7/5/9, INV-007 and the module allowlist updated.
  - **Vague "zero research/search call" test (AlchemyHAN):** TC-EVAL-010 now names `deep_researcher_builder.compile`, `utils.tavily_search_async`, `utils.get_search_tool` and `AsyncTavilyClient.search`, clears credentials and installs socket blockers before importing the patch targets; TC-EVAL-011 checks the research graph, `utils`, `test.run_evaluate` and search/MCP modules are absent in a clean subprocess.
  - **Missing cases (AlchemyHAN):** TC-EVAL-004 covers missing, empty and whitespace-only optional inputs; TC-017 covers invalid claim booleans; TC-018 covers adapter missing inputs; TC-019 covers prompt-template placeholder contracts; TC-023 covers complete judge-request bindings.
  - **C-004 test name mismatch (AlchemyHAN):** exception isolation now uses `test_groundedness_and_errors`, matching `requirements.yaml`; ADR §7, TC-EVAL-007 and POL-006 use the same path.
  - **Ambiguous CLI exit code 1 (AlchemyHAN):** added exit code 3 for judge initialisation/credential failures and real SDK HTTP 401/403 exceptions; TC-020 to TC-022 specify those paths while preserving completed scores.
  - **Separate judge client vs. shared-client rule (AlchemyHAN):** ADR §8, EVAL-001 and `structural-constraints.md` §10 now propose a lazy evaluation-client and credential-resolution exception, comparing injection-only, a side-effect-free shared factory and the existing shared-client option.
- **Decision:** approved (review feedback addressed in commit `b0c2904`)

### PR #16: docs(sa): propose orchestration contract and termination

- **Requirements:** REQ-001, REQ-003; contributor interfaces for REQ-002 C-005/C-007
- **Author / reviewers:** centay / BroZhai, AlchemyHAN
- **Date:** 2026-11-13 to 2026-11-16
- **Verification evidence checked:** `docs/architecture/adr/002-orchestration-contract-and-termination.md`, EVAL-001, `docs/architecture/invariants.md`, `docs/architecture/memory-design.md`, `docs/architecture/runtime-policy-catalog.md` (POL-011/012), `docs/code-governance/structural-constraints.md` §10, `docs/code-governance/verification-constraints.md` §7 (53 planned cases), `docs/architecture/orchestration-review-checklist.md` (R-01–R-12). CI: Requirements schema, Static analysis and Offline tests all PASS. Product, regression and full-graph acceptance tests NOT_RUN; the SA evidence (school DeepSeek probes, mocked locked-adapter replays, isolated baseline-function scenarios) is not a product acceptance test.
- **Findings:** issues raised and how each was resolved.
  - **Ten architecture documents checked clean (BroZhai):** the ADR and the shared documents were confirmed correct; the concern was the additional transcript material.
  - **`transcripts/raw/` bundle (BroZhai):** questioned whether the bulk of raw working files belongs in the commit and suggested the annotated transcript alone is enough.
  - **Cross-module changes required (BroZhai):** pointed at REQ-005 (PR #14) `U-1` and `U-2`, restated in the review comment; the orchestration DTO/helper/context signatures and the shared reader decisions were kept consistent with the delivery/context proposals.
  - **Privacy and scope of the raw bundle (AlchemyHAN):** asked to drop `transcripts/raw/` because the public repository would expose local paths, the school gateway hostname, team Google Sheet IDs plus a signed export URL and the team HackMD index; the raw material is to stay private and be referenced from the transcript.
  - **Self-review record in this memo (AlchemyHAN):** the `PREP-CENTAY-…` entry written by the author was removed from `docs/review-memo.md`, which is for reviewers, and moved to the AI-use log/transcript.
  - **ADR content outside REQ-001/003 (AlchemyHAN):** native search rejection in §3.2 belongs to the search module; §3.5 response completion and the §6 "per-turn context and compaction contract" belong to REQ-005. These were moved to open questions or the owning module, and the gateway `finish_reason` experiments kept in the transcript rather than the ADR.
  - **Broken table in `verification-constraints.md` (AlchemyHAN):** blank lines at L134/L136 dropped ORC-043/044 from the table; table restored.
  - **`orchestration-review-checklist.md` not in the AGENTS.md doc map (AlchemyHAN):** to be folded into the ADR or flagged to the team before integration.
- **Decision:** approved (module branch; integration still reconciles shared documents)

### PR #18: docs(sa): REQ-002 and REQ-004 Delivery Architecture

- **Requirements:** REQ-002, REQ-004 (associated upstream issues #283, #284)
- **Author / reviewers:** AlchemyHAN / BroZhai
- **Date:** 2026-11-15 to 2026-11-16
- **Verification evidence checked:** `docs/architecture/adr/001-task-failure-isolation.md`, `docs/architecture/adr/002-finalize-node-run-outcome.md`, EVAL-001 and EVAL-002, INV-002/INV-006, `docs/architecture/memory-design.md` §5, `docs/architecture/runtime-policy-catalog.md` (POL-001–POL-009), `docs/architecture/risk-list.md` (RISK-001–RISK-005), `docs/code-governance/structural-constraints.md` §10, `docs/code-governance/verification-constraints.md` §7 (TC-002-01–10, TC-004-01–15). CI: Requirements schema, Static analysis and Offline tests all PASS. Tests and implementation NOT_RUN (documentation only).
- **Findings:** issues raised and how each was resolved.
  - **F1 — `OutcomeDecision.update` omits `run_finalized` (BroZhai, High):** ADR-002 §5's interface table contradicted §3.3/§9 and `memory-design.md` §5 and would produce a `finalize` ↔ `final_report_generation` loop at the recursion limit. The §5 `update` row now says the first pass writes `run_finalized: True` and `failed_tasks` on both branches, and the second pass writes neither.
  - **F2 — Who may call `run_delegations` for `not_run` results (BroZhai, High):** §3.4, §5 and `structural-constraints.md` §10 disagreed on whether the orchestration early-return branch calls the delivery helper or classifies tasks itself. §10 now lists the early-return branch as a call site limited to `run_delegations(..., unrun_reason="not_run")`; orchestration decides which calls are unrun while the category and reason still come from `run_delegations`, and ADR-001 §5 and rule 6 say the same.
  - **F3 — `task_results` written by two modules (BroZhai, Medium):** the integration rule forbids two modules writing one state field. Carried to integration together with the other shared-field questions (RISK-002), since it depends on how `task_results` is settled with orchestration; a duplicate-`task_id` test is still to be added.
  - **F4 — No runtime policy for `asyncio.CancelledError` (BroZhai, Low):** added POL-008 — propagate, never convert to a `TaskResult`, no retry, no outcome update (TC-002-09) — and POL-001 now excludes it explicitly.
  - **F5 — POL-006 disagrees with the report-error rule at retry exhaustion (BroZhai, Low):** POL-006 now covers only "truncated and a report was generated" (`partial`); new POL-009 covers truncation retries running out (or an unknown model token limit) as `report_error` → `failed`; `report_error` is checked before `report_truncated`, and TC-004-15 was added.
  - **F6 — Flag-off "baseline" claim overstated (BroZhai, Low):** reworded to "control flow and report content match the baseline; `run_finalized` is written and `finalize` executes once more per run", and the flag-off regression suite compares `final_report`, `messages`, `notes` and node order instead of the whole state.
- **Decision:** approved (F3 deferred to integration)
