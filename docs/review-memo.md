# Review Memo

> **Purpose:** One review memo per pull request, covering spec alignment, architecture alignment, code and test quality, and operational metadata, with security and efficiency checked throughout, ending in a verdict of APPROVE, CHANGES REQUIRED or REJECT. It also records SA Reviews (Gate 1) and the human reviews named in a requirement's fit criterion (`automated: false` checks).
> **Maintained by:** reviewers.
> **Last updated:** 2026-11-23

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
- **Base → head / commits:** `<base>` → `<head>`; head `<sha>`; merge `<sha>`
- **Operational metadata:** CI run `<link>`; merged by `<name>` on `<date>`
- **Spec alignment:** does the change meet the requirement statement and its C-/M- acceptance criteria? PASS | PARTIAL | FAIL, with the criterion IDs checked.
- **Architecture alignment:** does it follow the accepted ADR/EVAL/INV, module path and dependency rules? PASS | FAIL.
- **Code and test quality:** determinism, offline testability, test-to-criterion mapping, regression coverage. PASS | PARTIAL | FAIL.
- **Security:** secrets, credentials, local paths, data exposure and injection/trust boundaries checked. PASS | N/A, with what was checked.
- **Efficiency:** token, latency and concurrency cost of the change considered. PASS | N/A, with the note.
- **Verification evidence checked:** `docs/test-reports/<task-id>.md`, CI run link.
- **Findings:** issues raised and how each was resolved.
- **Verdict:** APPROVE | CHANGES REQUIRED | REJECT

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
- **Base → head / commits:** `main` → `docs/sa-search-provider`; head `7544a7c`
- **Operational metadata:** merged into the SA integration branch `docs/sa-integration` (PR #22, merge `c03ce4f`); this PR itself was a module draft and was not merged directly.
- **Spec alignment:** PASS — REQ-007 C-001 to C-005 are mapped to test cases; C-003 was corrected during review (see findings).
- **Architecture alignment:** PASS — ADR-001 (later renumbered ADR-006) fits the `search/` module and the `structural-constraints.md` §10 boundary.
- **Code and test quality:** PARTIAL → PASS after fixes — thin cases were expanded (ordering with a call counter, empty-MCP-url, missing-auth-token, default-config regression).
- **Security:** PASS — original transcript leaked the local username and was redacted; no secrets in the design.
- **Efficiency:** N/A — documentation-only change, no runtime cost.
- **Verdict:** APPROVE (changes requested handled in the follow-up commits to the module branch)

### PR #13: docs(sa): REQ-006 unified citation format

- **Requirements:** REQ-006 (upstream langchain-ai/open_deep_research#232)
- **Author / reviewers:** NoPumpkinz / AlchemyHAN
- **Date:** 2026-11-13 to 2026-11-16
- **Base → head / commits:** `main` → `docs/sa-citations`; head `ee9e4ee`
- **Operational metadata:** merged into the SA integration branch `docs/sa-integration` (PR #22, merge `c03ce4f`); this PR itself was a module draft and was not merged directly.
- **Spec alignment:** PASS — REQ-006 C-001 to C-004 mapped to test cases; the format `[n] Title: URL` matches the approved statement.
- **Architecture alignment:** PASS — single citation contract in `citations/contract.py`, one owner per architectural element (blueprint §4).
- **Code and test quality:** PARTIAL → PASS after fixes — deterministic exact-once/zero-count rules and byte-identical block comparison replaced vague checks.
- **Security:** N/A — document/prompt text only; no secrets or data exposure.
- **Efficiency:** PASS (noted) — format stated exactly once per prompt avoids duplicated text swelling the context.
- **Verification evidence checked:** `docs/architecture/adr/001-unified-citation-format.md`, EVAL-001, INV-006, `docs/code-governance/structural-constraints.md` §5 and §10, `docs/code-governance/verification-constraints.md` §7 (TC-001–TC-006 planned). CI: Requirements schema, Static analysis and Offline tests all PASS. Behavioural tests NOT_RUN (documentation only).
- **Findings:** issues raised and how each was resolved.
  - **EVAL missing the simplest option (AlchemyHAN):** added Option A2 (shared constants defined directly in `prompts.py`, no new module) and rephrased Option A so it is no longer a straw man. The choice of B now states the governance reason: blueprint §4 assigns one architectural element to one module/owner, and `citations/contract.py` gives future INV-004 work a home.
  - **Repeated contract (AlchemyHAN):** `CITATION_RULES_BLOCK` states the format exactly once; `SOURCES_SECTION_SPEC` became `SOURCES_SECTION_POINTER` (a pure pointer); `RENUMBER_ACROSS_FINDINGS_INSTRUCTION` refers to the Citation Rules without restating them, so each assembled prompt carries the sources instruction once, as C-001 requires.
  - **No deterministic pass/fail rules (AlchemyHAN):** replaced the rules in ADR §7 and `verification-constraints.md` with exact-once occurrence counts, zero-count banned strings (`[Title](URL)`, `List of All Relevant Sources`, …), byte-identical block comparison for `[n] Title: URL` lines, and the explicit rule that every offline assertion must FAIL on the baseline for the registered reason.
  - **Case types misaligned (AlchemyHAN):** TC-003 retyped as a normal case and compares the text between `<Citation Rules>` tags byte-for-byte across both prompts; TC-004 formats both assembled prompts with all four real placeholders (`research_brief`, `messages`, `findings`, `date`, per `deep_researcher.py:642-647`) and asserts no contract placeholder survives; new negative case TC-005 (`test_format_checks_detect_violations`) feeds synthetic violating texts to the checks; the live case was renumbered TC-006.
  - **Unaccounted instructions L296/L302/L306 (AlchemyHAN):** recorded in ADR §3 — L302's "separate line item" is folded into "one per line", L306 and L296 stay because they specify no format, and the entry format is `[n] Title: URL` one per line per the approved REQ-006 statement (adding bullets would require a `requirements.yaml` change).
  - **Truncation affects C-004 (AlchemyHAN):** ADR §8 now records the retry-truncation risk at `deep_researcher.py:682` (`findings[:findings_token_limit]` can drop a later researcher's `### Sources` block, breaking renumbering); TC-006 excludes runs that triggered truncation retries and reports them separately; flagged to the REQ-005 owner.
- **Verdict:** APPROVE (changes requested handled in commit `ee9e4ee` on the module branch)

### PR #14: docs(sa): REQ-005 Context Compression Architecture

- **Requirements:** REQ-005 (associated issues #283, #284)
- **Author / reviewers:** BroZhai / AlchemyHAN, BroZhai
- **Date:** 2026-11-13 to 2026-11-16
- **Base → head / commits:** `main` → `docs/sa-context`; head `2191bd1`
- **Operational metadata:** merged into the SA integration branch `docs/sa-integration` (PR #22, merge `c03ce4f`); this PR itself was a module draft and was not merged directly.
- **Spec alignment:** PASS — REQ-005 INV-001 mapped to TC-001–TC-012; the attempt budget was rederived to actually satisfy the invariant.
- **Architecture alignment:** PASS after fix — the writer/reader of `research_outcome` across the subgraph boundary was made consistent with REQ-001.
- **Code and test quality:** PARTIAL → PASS after two review rounds — deterministic turn pairing, explicit `max_removals_per_attempt`, and separated trim/transient budgets.
- **Security:** N/A — no credentials or data exposure in scope.
- **Efficiency:** PASS (noted) — the whole design is about token-limit cost: it trims oldest turns and splits retry budgets so a one-turn history still gets three transient retries.
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
- **Verdict:** APPROVE (both review rounds addressed)

### PR #15: docs(sa): REQ-009 and REQ-010 Evaluation Architecture

- **Requirements:** REQ-009, REQ-010 (upstream langchain-ai/open_deep_research#234)
- **Author / reviewers:** DopplerXD / AlchemyHAN, BroZhai
- **Date:** 2026-11-13 to 2026-11-16
- **Base → head / commits:** `main` → `docs/sa-evaluation`; head `b0c2904`
- **Operational metadata:** merged into the SA integration branch `docs/sa-integration` (PR #22, merge `c03ce4f`); this PR itself was a module draft and was not merged directly.
- **Spec alignment:** PASS — REQ-009 C-001 to C-004/M-001 and REQ-010 C-001 to C-003 mapped to TC-EVAL cases; C-004 test name aligned with `requirements.yaml`.
- **Architecture alignment:** PASS after fix — INV-007 import boundary fixed (no `utils`/Tavily/MCP import); `test/evaluation/` whitelisted in structural constraints.
- **Code and test quality:** PARTIAL → PASS after fixes — zero-research-call test made concrete (socket blockers, cleared credentials), missing/edge cases added, and the `not_evaluable`-not-zero rule enforced.
- **Security:** PASS (noted) — credentials are cleared in tests; judge/credential failures map to exit code 3 rather than fabricating scores.
- **Efficiency:** PASS (noted) — the evaluation-only entry avoids compiling/running research, saving tokens and search calls.
- **Verification evidence checked:** `docs/architecture/adr/001-evaluation-module.md`, EVAL-001, INV-006 and INV-007, `docs/architecture/runtime-policy-catalog.md` (POL-002–POL-011), `docs/code-governance/structural-constraints.md` §10, `docs/code-governance/verification-constraints.md` §7 (TC-EVAL-001–TC-EVAL-023 planned), `docs/ai-use-log.yaml` (AIU-008, AIU-009). CI: Requirements schema, Static analysis and Offline tests all PASS. Behavioural, authentication-mapping and live LangSmith checks NOT_RUN.
- **Findings:** issues raised and how each was resolved.
  - **`test/evaluation/` path conflict (BroZhai):** the new folder contradicts `structural-constraints.md`. Proposed adding explicit `test/evaluation/` rows to the human-maintained structural layout as a whitelist, pending integration.
  - **INV-007 contradicts the dependency allowlist (AlchemyHAN):** importing `open_deep_research.utils.get_today_str` pulls in `AsyncTavilyClient`, `MultiServerMCPClient` and the Tavily tool at import time. Replaced with local standard-library date formatting; the ADR sections 2/3.7/5/9, INV-007 and the module allowlist updated.
  - **Vague "zero research/search call" test (AlchemyHAN):** TC-EVAL-010 now names `deep_researcher_builder.compile`, `utils.tavily_search_async`, `utils.get_search_tool` and `AsyncTavilyClient.search`, clears credentials and installs socket blockers before importing the patch targets; TC-EVAL-011 checks the research graph, `utils`, `test.run_evaluate` and search/MCP modules are absent in a clean subprocess.
  - **Missing cases (AlchemyHAN):** TC-EVAL-004 covers missing, empty and whitespace-only optional inputs; TC-017 covers invalid claim booleans; TC-018 covers adapter missing inputs; TC-019 covers prompt-template placeholder contracts; TC-023 covers complete judge-request bindings.
  - **C-004 test name mismatch (AlchemyHAN):** exception isolation now uses `test_groundedness_and_errors`, matching `requirements.yaml`; ADR §7, TC-EVAL-007 and POL-006 use the same path.
  - **Ambiguous CLI exit code 1 (AlchemyHAN):** added exit code 3 for judge initialisation/credential failures and real SDK HTTP 401/403 exceptions; TC-020 to TC-022 specify those paths while preserving completed scores.
  - **Separate judge client vs. shared-client rule (AlchemyHAN):** ADR §8, EVAL-001 and `structural-constraints.md` §10 now propose a lazy evaluation-client and credential-resolution exception, comparing injection-only, a side-effect-free shared factory and the existing shared-client option.
- **Verdict:** APPROVE (review feedback addressed in commit `b0c2904`)

### PR #16: docs(sa): propose orchestration contract and termination

- **Requirements:** REQ-001, REQ-003; contributor interfaces for REQ-002 C-005/C-007
- **Author / reviewers:** centay / BroZhai, AlchemyHAN
- **Date:** 2026-11-13 to 2026-11-16
- **Base → head / commits:** `main` → `docs/sa-orchestration`; head `73aced1`
- **Operational metadata:** merged into the SA integration branch `docs/sa-integration` (PR #22, merge `c03ce4f`); this PR itself was a module draft and was not merged directly.
- **Spec alignment:** PASS — REQ-001/REQ-003 acceptance criteria mapped (53 planned cases); REQ-002 contributions limited to C-005/C-007.
- **Architecture alignment:** PASS after fix — content outside REQ-001/003 (native search, response completion, context contract) moved to the owning module; cross-module signatures kept consistent with #14/#18.
- **Code and test quality:** PARTIAL → PASS — broken ORC-043/044 table rows restored; the review checklist to be folded into the ADR or flagged before integration.
- **Security:** FAIL → PASS after fix — the raw transcript bundle would have exposed local paths, the school gateway hostname, team Google Sheet IDs with a signed export URL and the team HackMD index; the bundle was dropped.
- **Efficiency:** PASS (noted) — `select_exit` is a single pure decision, avoiding extra model calls at termination.
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
- **Verdict:** APPROVE (module branch; integration still reconciles shared documents)

### PR #18: docs(sa): REQ-002 and REQ-004 Delivery Architecture

- **Requirements:** REQ-002, REQ-004 (associated upstream issues #283, #284)
- **Author / reviewers:** AlchemyHAN / BroZhai
- **Date:** 2026-11-15 to 2026-11-16
- **Base → head / commits:** `main` → `docs/sa-delivery`; head `a43a64a`
- **Operational metadata:** merged into the SA integration branch `docs/sa-integration` (PR #22, merge `c03ce4f`); this PR itself was a module draft and was not merged directly.
- **Spec alignment:** PASS — REQ-002 (INV-002) and REQ-004 C-001 to C-006 mapped to TC-002 and TC-004 cases.
- **Architecture alignment:** PARTIAL → PASS after fixes — F1 (finalize loop) and F2 (`run_delegations` call sites) reconciled across ADR/§10; F3 (`task_results` two writers) deferred to integration.
- **Code and test quality:** PASS — flag-off regression scoped to `final_report`/`messages`/`notes`/node order; added TC-002-09 and TC-004-15.
- **Security:** N/A — no credentials or data exposure in scope.
- **Efficiency:** PASS (noted) — bounded, fail-isolated fan-out with one join; no unbounded retries.
- **Verification evidence checked:** `docs/architecture/adr/001-task-failure-isolation.md`, `docs/architecture/adr/002-finalize-node-run-outcome.md`, EVAL-001 and EVAL-002, INV-002/INV-006, `docs/architecture/memory-design.md` §5, `docs/architecture/runtime-policy-catalog.md` (POL-001–POL-009), `docs/architecture/risk-list.md` (RISK-001–RISK-005), `docs/code-governance/structural-constraints.md` §10, `docs/code-governance/verification-constraints.md` §7 (TC-002-01–10, TC-004-01–15). CI: Requirements schema, Static analysis and Offline tests all PASS. Tests and implementation NOT_RUN (documentation only).
- **Findings:** issues raised and how each was resolved.
  - **F1 — `OutcomeDecision.update` omits `run_finalized` (BroZhai, High):** ADR-002 §5's interface table contradicted §3.3/§9 and `memory-design.md` §5 and would produce a `finalize` ↔ `final_report_generation` loop at the recursion limit. The §5 `update` row now says the first pass writes `run_finalized: True` and `failed_tasks` on both branches, and the second pass writes neither.
  - **F2 — Who may call `run_delegations` for `not_run` results (BroZhai, High):** §3.4, §5 and `structural-constraints.md` §10 disagreed on whether the orchestration early-return branch calls the delivery helper or classifies tasks itself. §10 now lists the early-return branch as a call site limited to `run_delegations(..., unrun_reason="not_run")`; orchestration decides which calls are unrun while the category and reason still come from `run_delegations`, and ADR-001 §5 and rule 6 say the same.
  - **F3 — `task_results` written by two modules (BroZhai, Medium):** the integration rule forbids two modules writing one state field. Carried to integration together with the other shared-field questions (RISK-002), since it depends on how `task_results` is settled with orchestration; a duplicate-`task_id` test is still to be added.
  - **F4 — No runtime policy for `asyncio.CancelledError` (BroZhai, Low):** added POL-008 — propagate, never convert to a `TaskResult`, no retry, no outcome update (TC-002-09) — and POL-001 now excludes it explicitly.
  - **F5 — POL-006 disagrees with the report-error rule at retry exhaustion (BroZhai, Low):** POL-006 now covers only "truncated and a report was generated" (`partial`); new POL-009 covers truncation retries running out (or an unknown model token limit) as `report_error` → `failed`; `report_error` is checked before `report_truncated`, and TC-004-15 was added.
  - **F6 — Flag-off "baseline" claim overstated (BroZhai, Low):** reworded to "control flow and report content match the baseline; `run_finalized` is written and `finalize` executes once more per run", and the flag-off regression suite compares `final_report`, `messages`, `notes` and node order instead of the whole state.
- **Verdict:** APPROVE (F3 deferred to integration)

### PR #20: Docs/sa search fallback

- **Requirements:** REQ-008 (depends on REQ-007; proposed by sszfot, merged into the integration branch as ADR-008)
- **Author / reviewers:** sszfot / AlchemyHAN
- **Date:** 2026-11-17 to 2026-11-18
- **Base → head / commits:** `docs/sa-search-provider` → `docs/sa-search-fallback`; head pushed to branch, never merged as this PR.
- **Operational metadata:** PR is an unmerged draft; its content reached `main` through PR #22 (merge `c03ce4f`). Close with a link to #22.
- **Spec alignment:** PARTIAL → PASS after narrowing — REQ-008 C-001 to C-005 are covered, but the first draft over-specified beyond the criteria.
- **Architecture alignment:** PARTIAL → PASS after fix — removed the dependency on the non-adopted REQ-007 U-5 structured MCP load result and collapsed the over-engineered design into one `search/fallback.py`.
- **Code and test quality:** PARTIAL → PASS — numbering unified and cases TC-SRC-11–TC-SRC-17 added; empty result treated as success; all-failed explicit.
- **Security:** N/A — no credentials or data exposure in scope.
- **Efficiency:** PASS (noted) — fallback only runs on eligible errors, in configured order, and never adds hidden retries.
- **Verification evidence checked:** the proposed ADR, `docs/architecture/evaluation-table.md` (proposed EVAL-002), proposed INV-006–INV-009, proposed POL-003, and the proposed test cases TC-027–TC-037 / AIU-010, read against `configuration.py`, `deep_researcher.py` (`execute_tool_safely`, `researcher_tools`), `utils.py` (Tavily/httpx error types) and the Discussion #19 decisions. Documentation only; no code or tests changed. The design was reviewed against the accepted architecture, not as a runtime acceptance test.
- **Findings:** issues raised and how each was resolved (all resolved by AlchemyHAN while merging this branch into `docs/sa-integration`, not on the module branch itself).
  - **Depends on a contract we did not adopt (AlchemyHAN, major):** D-1, D-4, D-5, TC-033, TC-037 and `SearchSource.load_status` relied on the structured MCP load result (REQ-007 U-5), which was not part of the Discussion #19 decisions and was dropped from the integrated ADR-006. A tool listed in `search_fallback` but not among the loaded tools is now recorded as `not available` and the next source is tried; the run stops only when there is no search tool at all (U-1). This also settles the POL-002 exception question, so REQ-007 does not change.
  - **No rule for calling an MCP tool with a Tavily query (AlchemyHAN, major):** an MCP fallback tool must now have exactly one required string argument; Tavily → MCP sends each query as a separate call, MCP → Tavily turns the string into a one-item `queries` list.
  - **Numbering collides with the integrated docs (AlchemyHAN, major):** the proposal reused ADR-002, EVAL-002, INV-006–009, POL-003, TC-027–037 and AIU-010. Renumbered to ADR-008, EVAL-008, INV-010, POL-024, TC-SRC-11–TC-SRC-17 and AIU-022.
  - **More structure than C-001–C-005 need (AlchemyHAN, major):** `SearchRequest`, a `SearchSource` protocol, three result types, load/invoke stages and eight open decisions were collapsed to one file, `search/fallback.py` (`apply_search_fallback`, `classify_search_error`, `AllSourcesFailedError`); the four invariants were merged into INV-010; D-1–D-8 were decided in the ADR (`search_fallback: list[str] = []`, errors classified by type, unknown errors ineligible).
- **Verdict:** APPROVE — accepted as ADR-008 through the SA integration (PR #22). The PR itself stays an unmerged draft; its content reached `main` through PR #22, and it should be closed with a link to #22.

### SA-001: Architecture of all modules (Gate 1) — PR #22

- **Date:** 2026-11-18
- **Base → head / commits:** `main` → `docs/sa-integration`; head `1bf8204`; merge `c03ce4f`
- **Participants:** merged by sszfot; approved by BroZhai and DopplerXD; module draft PRs #16 (orchestration), #18 (delivery), #14 (context), #13 (citations), #12 and #20 (search), #15 (evaluation) integrated under `docs/sa-integration`.
- **Operational metadata:** CI run https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/actions/runs/44233899446 — Requirements schema, Static analysis and Offline tests all PASS.
- **Reviewed:** ADR-001–ADR-008, EVAL-001–EVAL-008, module sections in `invariants.md` (INV-001–INV-010), `memory-design.md`, `runtime-policy-catalog.md` (POL-001–POL-024), `structural-constraints.md` §10, `verification-constraints.md` §7 (test cases per C-/M-/INV) and `trace-matrix.md` (REQ-001–REQ-010 rows).
- **Spec alignment:** PASS — every C-/M- criterion of REQ-001–REQ-010 has a test case; REQ-007 updated to v1.2.
- **Architecture alignment:** PASS — one consistent design after renumbering; overlapping responsibilities removed; no dependency outside §5.
- **Code and test quality:** PASS — every criterion and invariant is linked to a named test case in the trace matrix.
- **Security:** PASS (noted) — the raw transcript bundle from #16 was excluded from the integrated branch.
- **Efficiency:** N/A — documentation-only integration.
- **Verification evidence checked:** `scripts/validate_requirements.py`: PASS; every C-/M- criterion of REQ-001–REQ-010 has a test case: PASS; documentation only (no code or tests changed). Behavioural, live and implementation checks NOT_RUN.

| Item | Finding | Resolution |
|---|---|---|
| ADR IDs | Module drafts collided on ADR-001–ADR-002 and reused EVAL/INV/POL numbers | Renumbered in requirement order (ADR-001–008, EVAL-001–008, INV-001–010, POL-001–024) and references updated |
| REQ-008 | Fallback design in PR #20 was not integrated | Integrated as ADR-008 / EVAL-008 / INV-010 / POL-024 with the narrowing above |
| Shared docs | Module branches edited the same shared documents | Integrated with `git merge`, keeping each member's history; overlapping responsibilities removed |
| REQ-007 | Discussion #19 decisions and C-004 wording needed updating | REQ-007 updated to v1.2; C-004 wording fixed |
| Integration decisions | Conflicts between module drafts and unrequested design | Resolved and recorded in `architecture-blueprint.md` §11 |

- **Decision per ADR:** ADR-001–ADR-008 Accepted.
- **Outcome:** Gate 1 passed for REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007, REQ-008, REQ-009, REQ-010.
- **Verdict:** APPROVE

### PR #24: feat: implement ADR-001 to ADR-008 for REQ-001 to REQ-010

- **Requirements:** REQ-001 to REQ-010
- **Author / reviewers:** AlchemyHAN / NoPumpkinz and DopplerXD (approved); BroZhai and sszfot reviewed, their earlier reviews were dismissed after the follow-up commits.
- **Date:** 2026-11-19 to 2026-11-23
- **Base → head / commits:** `main` → `feat/implement-adr-001-008`; head `150302f`; merge `1719638`
- **Operational metadata:** CI run https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/actions/runs/44899966336 — Requirements schema, Static analysis and Offline tests all PASS; merged by AlchemyHAN on 2026-11-23.
- **Spec alignment:** PASS — schema PASS and offline tests 172 passed; every C-/M- criterion of REQ-001–REQ-010 has an implemented, passing offline case; live and human checks remain NOT_RUN (DEBT-005).
- **Architecture alignment:** PASS — implementation follows ADR-001–ADR-008; all new behaviour is behind feature flags defaulting off, so the baseline flow is preserved.
- **Code and test quality:** PASS — 172 offline tests pass without keys; every `path::test` cited in the docs exists; the live-test defect (below) was found and fixed.
- **Security:** PASS (noted) — no secrets committed; tests run without keys; the live-test defect was a control-flow bug, not a credential exposure.
- **Efficiency:** PASS (noted) — RISK-003 shows the default `compression_model_max_tokens=8192` truncates findings with the task contract on, so the compression output limit must be raised; otherwise no extra cost.
- **Verification evidence checked:** `docs/build-reports/REQ-001-010-build.md`; PR body verification table; CI on the PR. Requirements schema PASS; `ruff check src/open_deep_research test/offline scripts` PASS (also `test/evaluation`, `test/evaluators.py`, `test/prompts.py`); offline tests `uv run pytest test/offline`: PASS, 172 passed on the committed tree without API keys; every `path::test` cited in `verification-constraints.md`, `requirements.yaml`, `runtime-policy-catalog.md`, `trace-matrix.md` and `invariants.md` exists: PASS. Live tests TC-ORC-13, TC-CIT-05: NOT_RUN (DEBT-005); human README reviews TC-SRC-10, TC-EVA-08: NOT_RUN.
- **Findings:** issues raised and how each was resolved.
  - **REQ-007/REQ-008 search review, changes requested (sszfot):** validation and ordered fallback implementation consistent with the architecture and offline evidence positive; but REQ-007 C-005 README review found the MCP section "NEEDS IMPROVEMENT" (placeholder URL not flagged, `self_hosted_search` tool name not explained, `auth_required: true` prerequisites unclear, no reviewer-runnable setup). C-005 to stay pending until the README is improved and re-reviewed and the result is recorded as a `REVIEW-NNN`; remaining live Tavily/MCP interoperability to stay documented as NOT_RUN.
  - **Live-test defect found by NoPumpkinz:** `uv run pytest test/live` failed with `TypeError: No synchronous function provided to "clarify_with_user"`. Every research-graph node is `async def`, but both live tests called the synchronous `deep_researcher.stream(...)`, so LangGraph stopped before any research ran; the tests had only ever been skipped. A test defect, not a configuration problem. Fixed in `150302f`: `test/live/conftest.py` gained a shared `run_query()` using `astream()`, both live tests use it, and the live configuration sets `allow_clarification: False`.
  - **RISK-003 observed in the manual check:** with the default `compression_model_max_tokens=8192` every findings block was truncated, so every task ended `invalid_result` and the run failed with no report; with task contract on, the compression output limit must be raised.
- **Verdict:** APPROVE (two other members' approvals per `AGENTS.md` §7.2); merged into `main` on 2026-11-23.

### PR #4: chore: approve requirements and set up governance and SA templates

- **Requirements:** none (process and governance foundation)
- **Author / reviewers:** AlchemyHAN / BroZhai, sszfot
- **Date:** 2026-11-12 to 2026-11-13
- **Base → head / commits:** `main` → `chore/governance-and-sa-templates`; head `7fed18a`; merge `827fd32`
- **Operational metadata:** merged by AlchemyHAN on 2026-11-13; no code or tests, so no offline CI gate applies beyond schema.
- **Spec alignment:** N/A — no requirement implemented; the PR sets up where requirements are recorded.
- **Architecture alignment:** PASS — introduces `AGENTS.md`, `Prompt.md`, the `.opencode/` permission model, SA templates and the three-gate workflow.
- **Code and test quality:** N/A — documentation and templates only.
- **Security:** PASS (noted) — the permission model and path-based ownership define who may write what.
- **Efficiency:** N/A.
- **Verification evidence checked:** the updated `requirements.yaml` schema validation and the reviewed templates in `docs/architecture/` and `docs/code-governance/`.
- **Findings:** templates were kept free of pre-assigned owners and of architecture content that belongs to the SA phase.
- **Verdict:** APPROVE

### PR #17: fix(opencode): rename the SA agent to architect and disable the built-in plan agent

- **Requirements:** none (tooling configuration)
- **Author / reviewers:** AlchemyHAN / no formal review
- **Date:** 2026-11-16
- **Base → head / commits:** `main` → `chore/governance-and-sa-templates`; head `7af6dec`; merge `daf6947`
- **Operational metadata:** merged by AlchemyHAN on 2026-11-16; a `.opencode/` configuration change, no code or tests touched.
- **Spec alignment:** N/A — no requirement in scope.
- **Architecture alignment:** N/A — tooling only.
- **Code and test quality:** N/A — configuration only.
- **Security:** PASS (noted) — keeps a single named architect agent rather than an ambiguous built-in plan agent.
- **Efficiency:** N/A.
- **Verification evidence checked:** `.opencode/` configuration diff.
- **Findings:** renamed the SA agent to `architect` and disabled the built-in `plan` agent to remove role ambiguity.
- **Verdict:** APPROVE
