# AIU-037 — REQ-007 / REQ-008 Implementation Review

- Session: `ses_e2bdd7ea1fferC4tLbkCJeovtC`
- Source: OpenCode JSON export
- Message indices: 326–378 (zero-based, inclusive)
- Scope: implementation review, local corrections, tests, documentation
- Status: draft; requires human redaction and completeness review

## Disclosure

This transcript preserves user and assistant text, with basic
redaction of common credential and local-path patterns.
Tool outputs and structured tool arguments are omitted from
this draft and must be reviewed separately against the original
export if required for evidence completeness.
The C-005 human review remains NOT_RUN.

## Message 326 — user

Time (UTC): 2026-11-20T15:56:24.565000+00:00

Please help me verify the current implementation of REQ-007 and REQ-008 in this repository.

Context:
- Project: Open_Deepsearch_ULTRA
- REQ-007: Search Configuration Validation
- REQ-008: Ordered Search Fallback
- LangGraph Studio starts successfully, but the end-to-end workflow is blocked by an external OpenAI API error: HTTP 403, "Country, region, or territory not supported".
- The OpenAI SDK can connect successfully over IPv4, so this is no longer simply a missing API key or TLS issue.
- I want to continue verification without relying on external model APIs.

Please perform the following tasks step by step:

1. Inspect the current Git branch, working tree, and relevant REQ-007/REQ-008 implementation files.
2. Read the requirements, ADRs, invariants, traceability matrix, and existing tests.
3. Identify the actual implementation and acceptance criteria for both requirements.
4. Run all relevant offline tests using mocks or stubs. Do not call external APIs.
5. Verify REQ-007, including valid configuration, invalid configuration, provider/tool consistency, and failure before model execution.
6. Verify REQ-008, including ordered fallback, eligible failures, ineligible failures, empty successful results, and all-provider failure reporting.
7. Run the relevant Ruff checks and identify any outstanding lint errors.
8. Check whether existing tests genuinely cover the acceptance criteria or merely test implementation details.
9. Produce a verification report containing:
   - Test commands and results
   - Passed and failed acceptance criteria
   - Missing test coverage
   - Implementation defects, if any
   - Environmental limitations
   - Recommended next steps

Important constraints:
- Do not modify production code or tests without my approval.
- Do not change Git branches, commit, push, or create a PR.
- Do not expose API keys or credentials.
- Do not make external API calls.
- Distinguish clearly between verified results, assumptions, and untested behavior.
- Do not claim end-to-end verification passed.
- Preserve existing project architecture and invariants.

Start with repository inspection and report your findings before making any changes.

## Message 327 — assistant

Time (UTC): 2026-11-20T15:56:24.644000+00:00

I'll start with repository inspection. This is read-only verification; I won't modify anything.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 328 — assistant

Time (UTC): 2026-11-20T15:56:31.596000+00:00

The implementation exists: `search/validation.py`, `search/fallback.py`, and both offline test files. Let me read the actual implementation and the REQ-007/REQ-008 architecture docs (now ADR-001 and ADR-008 per the renumbering).

**Tool:** `read`

*Structured arguments and output omitted in draft.*

**Tool:** `read`

*Structured arguments and output omitted in draft.*

**Tool:** `read`

*Structured arguments and output omitted in draft.*

## Message 329 — assistant

Time (UTC): 2026-11-20T15:56:34.596000+00:00

Implementation is real and references ADR-006 (REQ-007) and ADR-008 (REQ-008), INV-005/INV-010, POL-018/019/024. Let me confirm how these are wired into `deep_researcher.py`/`utils.py`, and read the offline tests for both requirements.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 330 — assistant

Time (UTC): 2026-11-20T15:56:39.451000+00:00

Wiring confirmed: validation at `clarify_with_user` (L134-135) and `researcher` (L668-673); fallback applied post-assembly (L754). Let me read the config field and the two offline test files.

**Tool:** `read`

*Structured arguments and output omitted in draft.*

**Tool:** `read`

*Structured arguments and output omitted in draft.*

## Message 331 — assistant

Time (UTC): 2026-11-20T15:56:42.875000+00:00

Good coverage for REQ-007. Now the REQ-008 test file and the offline helpers.

**Tool:** `read`

*Structured arguments and output omitted in draft.*

## Message 332 — assistant

Time (UTC): 2026-11-20T15:56:45.578000+00:00

Tests are substantive and map to named TC-SRC IDs (not just implementation details). Now let me run the actual offline tests (no external calls), then Ruff. First confirm test infra and that no env var forces live calls.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 333 — assistant

Time (UTC): 2026-11-20T15:56:48.764000+00:00

The helpers are offline-only fakes. Now run the two REQ-007/REQ-008 test files.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 334 — assistant

Time (UTC): 2026-11-20T15:56:52.869000+00:00

All 59 tests in the two files pass offline (0.42s, no network). Let me get the full count/summary and the earlier (header) portion to confirm the REQ-007 test IDs, then run Ruff.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 335 — assistant

Time (UTC): 2026-11-20T15:56:56.779000+00:00

59 passed. Ruff reports 7 errors. Let me see all 7 and check the project's ruff config and whether gated CI covers `src/` — this matters for whether these are "outstanding lint errors" or pre-existing style debt.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 336 — assistant

Time (UTC): 2026-11-20T15:57:00.713000+00:00

All 7 are the same `UP045` (`Optional[X]` → `X | None`) in the new search module. The project's `UP` ruleset is enabled and `UP007` is ignored but `UP045` is not — so these are genuine lint errors in code that the CI static-analysis gate covers. Let me confirm the CI gate paths and whether the full offline suite passes (regression scope).

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 337 — assistant

Time (UTC): 2026-11-20T15:57:05.166000+00:00

Full offline suite: **172 passed**. CI runs `ruff check src/open_deep_research test/offline scripts`, so the 7 `UP045` errors **would fail the static-analysis gate**. Let me quantify scope: are these 7 the only lint issues repo-wide, or are there pre-existing ones on this branch? This determines whether the branch is CI-green apart from the new code.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 338 — assistant

Time (UTC): 2026-11-20T15:57:09.583000+00:00

Important: across the CI ruff scope there are **24 `UP045` errors** — 7 in the new search module and 17 pre-existing in `state.py`/`utils.py`. This means the static-analysis gate is failing across the repo, not just for REQ-007/008. Let me confirm `state.py`/`utils.py` are baseline (not new) and check whether the branch's CI is expected to be green.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 339 — assistant

Time (UTC): 2026-11-20T15:57:13.227000+00:00

The 24 `UP045` errors all originate from commit `c8a008c` (the "implement ADR-001 to ADR-008" commit) — i.e. the implementation PR introduced them, including 17 in files it touched (`state.py`, `utils.py`). So the branch is **not** CI-green on the static-analysis gate. Let me verify the requirements/ADR acceptance criteria mapping and trace matrix so I can judge coverage against true criteria rather than test names.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 340 — assistant

Time (UTC): 2026-11-20T15:57:18.406000+00:00

Now I have everything. Note a key nuance: the trace matrix says the code is on `feat/implement-adr-001-008` "not yet committed or merged," but we are on `review/pr24` where it **is** committed (`c8a008c`). Let me confirm the acceptance criteria descriptions in full for the report, and check C-005 (by-design human review, not automated).

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 341 — assistant

Time (UTC): 2026-11-20T15:57:21.546000+00:00

I now have complete evidence to verify each acceptance criterion against the actual tests. Let me confirm the two verifier-facing subtleties: (a) REQ-007 C-005 is human review (README), not automated; (b) whether the `AllSourcesFailed` message could ever be mistaken for the empty marker, and the `researcher_tools` integration point. Let me quickly check `researcher_tools` how fallback result/errors become ToolMessages.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 342 — assistant

Time (UTC): 2026-11-20T15:57:25.355000+00:00

Critical integration observation: `apply_search_fallback` is applied in `researcher_tools` (L753-754) but `execute_tool_safely` (L711-716) still catches every exception and converts it to text `"Error executing tool: {e}"`. So an `AllSourcesFailedError` becomes `"Error executing tool: All search sources failed: ..."` — the explicit failure **does** reach the researcher and is **not** the empty marker (C-003 satisfied end-to-end), but it is wrapped as a generic tool error string. That's correct per the ADR design ("wrapper only raises; text conversion stays in execute_tool_safely").

I have all evidence needed. Here is the verification report.

---

# REQ-007 & REQ-008 Verification Report (offline)

## 1. Repository state
- **Branch:** `review/pr24` (working tree clean). Note: the trace matrix still says the code lives on `feat/implement-adr-001-008` "not yet committed or merged," but on this branch the implementation **is** committed (`c8a008c feat: implement ADR-001 to ADR-008 behind feature flags`; `d813c83` added tests). This is a **documentation staleness** issue, not a code issue.
- **Implementation files (verified present and wired):**
  - `src/open_deep_research/search/validation.py` — REQ-007 (`load_search_config`, `validate_search_config`, `model_provider`, `require_search_tools`, `SearchConfigError`, `SearchUnavailableError`).
  - `src/open_deep_research/search/fallback.py` — REQ-008 (`apply_search_fallback`, `classify_search_error`, `AllSourcesFailedError`).
  - `configuration.py`: `search_fallback: List[str]` (default `[]`) + comma-split validator.
  - `deep_researcher.py`: validation at `clarify_with_user` L134-135 and `researcher` L668-673; fallback applied at `researcher_tools` L753-754.
- **Architecture docs:** `docs/architecture/adr/006-search-configuration-validation.md` (REQ-007), `adr/008-search-fallback.md` (REQ-008); invariants INV-005 (search config) and INV-010 (fallback); POL-018/019 (REQ-007), POL-024 (REQ-008). ADRs were **accepted** in SA Review PR #22 (per trace matrix note); so architecture is accepted, code is implemented, but **not yet verified**.

## 2. Requirements mapping
- REQ-007 (`approved`): checks C-001…C-005, with C-005 **by design a human review** (`docs/review-memo.md`), not automated.
- REQ-008 (`approved`, `depends_on: REQ-007`): checks C-001…C-005, all `automated: true`.
- Trace matrix rows REQ-007 (TC-SRC-01…09, 18) and REQ-008 (TC-SRC-11…17) align with the test files.

## 3. Test commands and results

| Command | Result |
|---|---|
| `uv run pytest test/offline/test_search_configuration.py test/offline/test_search_fallback.py` | **59 passed**, 0 failed, 0.27s |
| `uv run pytest test/offline` (full regression) | **172 passed** |
| `uv run ruff check src/open_deep_research test/offline scripts` (CI scope) | **24 errors (all UP045)** |
| `uv run ruff check src/open_deep_research/search ...` | **7 errors (all UP045)** |

No external APIs were contacted; tests use fake tools/models (`test/offline/helpers.py`, `ForbiddenModel`, `FakeSearchTool`), no network.

## 4. Passed acceptance criteria (offline-verified)

**REQ-007**
| Criterion | Test | Status |
|---|---|---|
| C-001 native provider ↔ model mismatch rejected | `test_native_search_model_mismatch_rejected` | ✅ PASS |
| C-002 `none` without usable MCP rejected (3 malformed MCP shapes) | `test_no_search_tool_rejected` | ✅ PASS |
| C-003 unsupported provider lists supported set (config **and** env) | `test_unsupported_provider_rejected` | ✅ PASS |
| C-004 valid Tavily accepted, `tavily_search` present | `test_valid_tavily_configuration_accepted` | ✅ PASS |
| C-005 README setup review | human review | ⚠️ **NOT_RUN** (by design) |

Additional verified: provider allowlist (bare/prefixed accepted, others fail closed) `test_native_search_provider_allowlist`; **no model call before validation** (`ForbiddenModel.calls == 0`) via `test_mcp_without_tools_stops_run`, `test_researcher_entry_validates`, `test_researcher_entry_validates_its_tools`; unknown `search_fallback` entry rejected (`test_unknown_fallback_entry_rejected`, covering REQ-008's config rule); task-contract/native-search conflict (`test_task_contract_rejects_native_search`).

**REQ-008**
| Criterion | Test | Status |
|---|---|---|
| C-001 primary timeout → fallback result, primary tried once | `test_primary_failure_uses_fallback` | ✅ PASS |
| C-002 three sources, first two eligible-fail, third result, in order | `test_fallbacks_follow_configured_order` | ✅ PASS |
| C-003 all fail → explicit message naming each source+error, ≠ empty marker | `test_all_sources_fail_explicitly` | ✅ PASS |
| C-004 empty result → success, no fallback | `test_empty_result_does_not_trigger_fallback` | ✅ PASS |
| C-005 malformed query (ineligible) → original error, no fallback | `test_ineligible_error_does_not_trigger_fallback` | ✅ PASS |

Additional verified: typed classification across 19 signals incl. Tavily errors, MCP codes (408, −32000), HTTP 4xx/5xx, `__cause__` chains, exception groups, and **message text never parsed**; MCP→Tavily fallback with schema adaptation; no wrapping when no other source listed; wrapped tools keep name/description/schema; empty `search_fallback` returns tools unchanged (backward compatibility).

## 5. Failed acceptance criteria
- **None of the automated C-001…C-005 fail.** All 10 automated criteria pass.
- **C-005 (REQ-007) is unverified** — it requires a human README-setup review in `docs/review-memo.md`, which is `NOT_RUN`.

## 6. Missing test coverage (gaps, not failures)
1. **No end-to-end graph test** of REQ-008 through `researcher_tools` → `execute_tool_safely`: the unit tests call `apply_search_fallback` directly; no test asserts that an `AllSourcesFailedError` becomes a `ToolMessage` whose content starts with the failure marker (not the empty marker) when routed through the real node + `execute_tool_safely` wrapper. The wiring exists (L753-754, L711-716) but is only unit-covered.
2. **REQ-007 C-005** human review not recorded.
3. **Native-search runtime** (`openai`/`anthropic` binding/execution) not exercised — by design offline; only config-time allowlist is tested.
4. **`task_contract_enabled` interaction** tested only for the rejection case, not the full enabled path with search fallback.

## 7. Implementation defects
- **No functional defects found** in REQ-007/REQ-008 logic under offline testing. Validation is pure and runs before model calls; fallback honours ordering, eligibility, empty-success and explicit all-failed; integration points are correctly wired.
- **Observation (not a defect):** `execute_tool_safely` converts `AllSourcesFailedError` to `"Error executing tool: All search sources failed: ..."`. This satisfies C-003 (explicit, not empty) but the researcher sees a generic tool-error string rather than a typed failure — consistent with ADR design, worth confirming as intended in the report.
- **Documentation staleness (defect in docs, not code):** trace matrix says the code is "not yet committed or merged," but it is committed on `review/pr24`.

## 8. Lint (outstanding)
- **24 × `UP045`** (`Optional[X]` → `X | None`) across the CI ruff scope: **7 in the new search module** (`validation.py`, `fallback.py`) and **17 pre-existing** in `state.py`/`utils.py`, all introduced by `c8a008c`.
- The project enables `UP` but ignores only `UP006/UP007/UP035`, **not** `UP045`. CI runs `ruff check src/open_deep_research test/offline scripts`, so **the static-analysis gate currently fails**. All 24 are auto-fixable (`ruff --fix`), but fixing them is a code change I will not make without approval.

## 9. Environmental limitations
- **E2E blocked by OpenAI HTTP 403 "Country, region, or territory not supported."** No model/API calls were made. All results are **offline (mocked)** only; live/model-dependent paths are `NOT_RUN`.
- Real Tavily, real MCP servers and native OpenAI/Anthropic search were not exercised.
- **Do not treat this as end-to-end verification.** It is offline unit/regression verification.

## 10. Test-quality assessment (criteria vs implementation detail)
- The tests are **mostly behaviour-level**: they assert observable outcomes (which source's result is returned, ordering of attempts, error content/prefix, empty vs failure, zero model calls) against named TC-SRC IDs traceable to C-001…C-005. Classification tests target the public `classify_search_error`, not internals.
- Minor coupling: `test_all_sources_fail_explicitly` asserts exact `attempts` tuples and exact prefix string; `test_mcp_primary_falls_back_to_tavily` monkeypatches `utils.tavily_search.coroutine` (implementation detail of the shared tool) — acceptable but slightly white-box. These still verify the requirement, not mere internals.

## 11. Verified vs assumed vs untested
- **Verified (offline):** all automated REQ-007 and REQ-008 acceptance criteria; zero-model-call-before-validation; classification taxonomy; backward compatibility with empty fallback.
- **Assumed:** that `get_all_tools` assembles real MCP/Tavily tools identically to the fakes (the fakes mirror the shapes but not live behaviour).
- **Untested:** full graph run; live providers; native search execution; README human review; the `execute_tool_safely`-wrapped all-failed message at graph level.

## 12. Recommended next steps (no changes made)
1. **Approval needed to fix lint:** run `uv run ruff check --fix` (or `ruff format`) on the 7 new `UP045` in `search/` — and decide whether to also fix the 17 pre-existing `state.py`/`utils.py` ones so CI passes.
2. **Record the REQ-007 C-005 human review** in `docs/review-memo.md` (human task).
3. **Add one integration test** through `researcher_tools` + `execute_tool_safely` asserting the all-failed `ToolMessage` is explicit and not the empty marker.
4. **Correct the trace matrix staleness** (code-committed status).
5. Perform **live E2E** once a supported region/endpoint is available (external blocker).

Stopping here — no files modified, no branch/commit/PR changes, no external calls. Awaiting your decision on whether to proceed with lint fixes or integration-test additions.

## Message 343 — user

Time (UTC): 2026-11-20T15:59:00.088000+00:00

Continue from your REQ-007 / REQ-008 verification report on branch `review/pr24`.

I approve local changes for the following limited tasks:

1. Fix all 24 Ruff UP045 errors within the CI static-analysis scope. Use minimal syntax-only changes and preserve runtime behavior.
2. Add an offline integration test covering the REQ-008 all-sources-failed path through `researcher_tools` and `execute_tool_safely`. Verify that the resulting ToolMessage explicitly identifies the failure and is not treated as an empty successful search result.
3. Inspect the README against REQ-007 C-005. Prepare a human-review checklist and identify any documentation problems. Do not mark the human review as approved on my behalf.
4. Correct objectively outdated implementation-status references in the traceability matrix without changing requirement or architecture approval statuses.

After making changes:

- Run `uv run ruff check src/open_deep_research test/offline scripts`.
- Run `uv run pytest test/offline -q`.
- Run any additional focused tests.
- Show `git diff --check`, `git diff --stat`, and `git status --short`.
- Explain every modified file and why the change was necessary.
- Report any remaining failures, warnings, or coverage gaps.

Important constraints:

- Do not change business requirements, fallback semantics, or architecture decisions.
- Do not access external model or search APIs.
- Do not modify secrets or `.env`.
- Do not commit, push, merge, or create a pull request.
- Do not claim that live end-to-end verification or human approval has been completed.
- Stop after producing the results and wait for my review.

## Message 344 — assistant

Time (UTC): 2026-11-20T15:59:00.125000+00:00

Approved for tasks 1–4. Let me start by capturing the exact 24 UP045 locations, then fix them minimally.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 345 — assistant

Time (UTC): 2026-11-20T15:59:03.853000+00:00

The distribution differs from my earlier read (my earlier filter caught only some). The actual 24 span 7 files. `UP045` is reliably auto-fixable and syntax-only. I'll use `ruff --fix` scoped to these files, then verify behavior is unchanged via the test suite.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Patch event:** omitted in draft

## Message 346 — assistant

Time (UTC): 2026-11-20T15:59:07.769000+00:00

UP045 fixed (24), but 7 different errors surfaced — likely other `UP` rules previously masked by the UP045 fix ordering. Let me see them.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 347 — assistant

Time (UTC): 2026-11-20T15:59:11.061000+00:00

The UP045 fix left now-unused `Optional` imports (F401). These are the direct consequence of the syntax change and must be removed. Auto-fix them too.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Patch event:** omitted in draft

## Message 348 — assistant

Time (UTC): 2026-11-20T15:59:14.484000+00:00

Lint clean across CI scope. Let me confirm the diff is syntax-only (no behavior change) — check that `Optional[X]` became `X | None` and imports were the only changes.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 349 — assistant

Time (UTC): 2026-11-20T15:59:18.217000+00:00

Purely syntactic (`Optional[X]` → `X | None`, unused import removal). Now **Task 2**: add an offline integration test through `researcher_tools` + `execute_tool_safely`. Let me study the existing helpers for building a researcher_tools scenario and the node's structure.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 350 — assistant

Time (UTC): 2026-11-20T15:59:21.785000+00:00

**Tool:** `read`

*Structured arguments and output omitted in draft.*

## Message 351 — assistant

Time (UTC): 2026-11-20T15:59:27.652000+00:00

I understand the integration path. `researcher_tools` calls `get_all_tools` (I'll monkeypatch) then `apply_search_fallback`, then `execute_tool_safely` → `ToolMessage`. I'll build a test where `search_api=tavily`, `search_fallback=["self_hosted_search"]`, the primary Tavily raises an eligible timeout, and the MCP fallback is absent, so all sources fail. Let me check the helper `install_model`/`command_goto` and how tests build `AIMessage` with tool_calls.

**Tool:** `read`

*Structured arguments and output omitted in draft.*

## Message 352 — assistant

Time (UTC): 2026-11-20T15:59:30.772000+00:00

`researcher_tools` doesn't instantiate a model, so I don't need `install_model`. I need `get_all_tools` monkeypatched to return a real Tavily-like tool + an MCP tool, and build an `AIMessage` with a `tavily_search` tool call. Let me append the integration test to `test_search_fallback.py`.

**Tool:** `read`

*Structured arguments and output omitted in draft.*

## Message 353 — assistant

Time (UTC): 2026-11-20T15:59:34.275000+00:00

Now I'll add the integration test at the end of the file. It drives the real `researcher_tools` node with a failing wrapped Tavily and an unloadable MCP fallback, asserting the `ToolMessage` content is an explicit failure distinct from the empty marker.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Patch event:** omitted in draft

## Message 354 — assistant

Time (UTC): 2026-11-20T15:59:40.163000+00:00

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 355 — assistant

Time (UTC): 2026-11-20T15:59:44.105000+00:00

Integration test passes. Let me confirm it genuinely exercises the path (not a false pass) by checking the actual ToolMessage content it produces, then run the modules and lint.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 356 — assistant

Time (UTC): 2026-11-20T15:59:49+00:00

The generated content confirms the real behavior: `Error executing tool: All search sources failed: tavily_search (timeout): ...; self_hosted_search (not available): ...` — explicit, names both sources and categories, and is not the empty marker.

Now **Task 3**: inspect README against REQ-007 C-005 (search provider configuration review). C-005 requires a reviewer to configure each built-in provider and an MCP search server from docs alone, and find required credentials.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 357 — assistant

Time (UTC): 2026-11-20T15:59:52.916000+00:00

The README appears thorough. Let me read the full Search API section (lines 75–100) to assess against C-005 precisely (per-provider config, MCP recipe, credentials, model compatibility).

**Tool:** `read`

*Structured arguments and output omitted in draft.*

## Message 358 — assistant

Time (UTC): 2026-11-20T15:59:56.409000+00:00

The README (`75–98`) substantially satisfies C-005: per-provider table, model-compatibility rules, credentials, MCP recipe, validation behavior, and fallback. Let me do one factual cross-check — the table says `tavily` needs `TAVILY_API_KEY` "plus the key of the `summarization_model`" and `none` needs "whatever the MCP server needs". I'll verify the summarization-key claim against `utils.py`, and then produce the checklist without marking it approved.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 359 — assistant

Time (UTC): 2026-11-20T16:00:00.351000+00:00

README is factually accurate (summarization model + Tavily keys confirmed). Now **Task 4**: fix objectively outdated implementation-status references in the trace matrix — but **not** requirement/architecture approval statuses. Let me find the stale "not yet committed or merged" text and any `NOT_RUN`/`planned:` markers that are now objectively false.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 360 — assistant

Time (UTC): 2026-11-20T16:00:06.836000+00:00

The objectively outdated claim is "implemented on branch `feat/implement-adr-001-008`, which is not yet committed or merged" — false on `review/pr24` (committed in `c8a008c`, tests in `d813c83`). I'll correct only that status sentence, preserving all approval statuses (`approved`, ADR accepted, `NOT_RUN` live/human). This is markdown, allowed by task 4.

**Tool:** `edit`

*Structured arguments and output omitted in draft.*

**Patch event:** omitted in draft

## Message 361 — assistant

Time (UTC): 2026-11-20T16:00:11.632000+00:00

Now run all required validations: full ruff, full offline suite, focused tests, and git checks.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 362 — assistant

Time (UTC): 2026-11-20T16:00:17.834000+00:00

Ruff clean; full offline suite **173 passed** (was 172; +1 integration test). Focused search suite **60 passed** (was 59). Now the git reports.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 363 — assistant

Time (UTC): 2026-11-20T16:00:23.800000+00:00

All tasks complete and validated. Here is the report.

## 1. Tasks completed

### Task 1 — Fix 24 Ruff UP045 errors (CI scope) ✅
`syntax-only` changes: `Optional[X]` → `X | None`, then removal of the now-unused `typing.Optional` imports (F401). No logic touched.

| File | Errors fixed | Change |
|---|---|---|
| `configuration.py` | 6 | 6 `Optional[X]`→`X\|None`, drop unused import |
| `state.py` | 7 | 7 annotations |
| `search/fallback.py` | 3 | 3 annotations |
| `search/validation.py` | 4 | 4 annotations |
| `delivery/outcome.py` | 2 | 2 annotations |
| `orchestration/termination.py` | 1 | 1 annotation |
| `utils.py` | 1 | 1 annotation |

Result: `uv run ruff check src/open_deep_research test/offline scripts` → **All checks passed!**

### Task 2 — Offline integration test ✅
Added `test_search_fallback.py::test_all_sources_failed_reaches_tool_message_explicitly` (64 lines). It drives the **real `researcher_tools` node → `apply_search_fallback` → `execute_tool_safely` → `ToolMessage`** with a timing-out Tavily primary and an unloaded MCP fallback. Verified actual output:
```
Error executing tool: All search sources failed: tavily_search (timeout): ...; self_hosted_search (not available): ...
```
Assertions: prefix `All search sources failed:` present, both sources + `timeout` named, and `EMPTY_RESULT_TEXT` absent (not mistaken for an empty success). PASS.

### Task 3 — README vs C-005 checklist ✅ (not marked approved)
The README Search API section (`75–98`) is strong. **Human-review checklist for C-005** (to be completed by a reviewer; no approval asserted):
- [ ] A reader can select **each** provider (`tavily`, `openai`, `anthropic`, `none`) from the table alone.
- [ ] Native model-compatibility rules (incl. bare `gpt-`/`claude` and rejection of Azure/Bedrock/OpenRouter) are clear.
- [ ] Required credentials are discoverable: `TAVILY_API_KEY` + summarization key; `OPENAI_API_KEY`; `ANTHROPIC_API_KEY`; MCP "whatever the server needs".
- [ ] `SEARCH_API` env precedence over the config field is understandable.
- [ ] An **MCP search server** can be configured from the JSON example + `url`/`tools`/`auth_required`/`mcp_prompt` description.
- [ ] `search_fallback` semantics and validation errors are understood.

**Documentation problems found (minor, non-blocking):**
- Line 77: grammatical errors ("Has full MCP compatibility and work native web search for Anthropic and OpenAI") — cosmetic.
- C-005 remains **NOT_RUN** until a human completes the checklist above; I have not marked it approved.

### Task 4 — Trace-matrix staleness ✅
Corrected **one** objectively false sentence only: "implemented on branch `feat/implement-adr-001-008`, which is not yet committed or merged" → now states it **is committed** (`c8a008c`/`d813c83`) and under review on `review/pr24`, not yet merged. **Approval statuses unchanged** (REQ approval, ADR acceptance, `NOT_RUN` live/human verdicts preserved).

## 2. Validation results
- `uv run ruff check src/open_deep_research test/offline scripts`: **All checks passed!**
- `uv run pytest test/offline -q`: **173 passed** (was 172; +1 integration test)
- Focused: `test_search_configuration.py` + `test_search_fallback.py`: **60 passed** (was 59)
- `git diff --check`: **CLEAN**

## 3. Modified files (why)
- `src/…/configuration.py`, `delivery/outcome.py`, `orchestration/termination.py`, `search/fallback.py`, `search/validation.py`, `state.py`, `utils.py` — **lint only** (UP045/F401, syntax-only) to make the CI static-analysis gate pass.
- `test/offline/test_search_fallback.py` — **new integration test** (C-003 end-to-end through `researcher_tools`).
- `docs/architecture/trace-matrix.md` — **status wording only** (committed/under-review, not-yet-merged); no requirement/architecture status changed.

## 4. Remaining failures / warnings / gaps
- **No failures.** Remaining pytest output is **32 warnings**, all third-party deprecations (Pydantic V2 `Field`/class `config`, LangGraph `config_schema`/`output`/`input`) — pre-existing, not from these changes.
- **Coverage gaps (unchanged, by design):** REQ-007 **C-005 human review NOT_RUN**; live/native-search execution untested (external blocker: OpenAI HTTP 403 region); real Tavily/MCP servers not exercised.
- **No live end-to-end or human approval claimed.**

## 5. Git state
```
git diff --check: CLEAN
git diff --stat: 9 files, +95/−31
git status --short:
 M docs/architecture/trace-matrix.md
 M src/open_deep_research/{configuration,s tate,utils,delivery/outcome,orchestration/termination,search/fallback,search/validation}.py
 M test/offline/test_search_fallback.py
```
No commit, push, merge, or PR; no requirement/architecture/fallback-semantics changes; no external APIs; no secrets touched.

Stopping for your review. Two items need your decision: (a) whether to reword the minor grammatical README issues, and (b) who will perform the C-005 human review (I have prepared its checklist but not marked it approved).

## Message 364 — user

Time (UTC): 2026-11-20T16:03:21.259000+00:00

Continue the pre-merge review of PR #24 on branch `review/pr24`.

Previous verification results:
- 173 offline tests passed.
- 60 focused search tests passed.
- Ruff static analysis passed.
- The REQ-008 all-sources-failed integration test passed.
- Nine files have uncommitted changes.
- REQ-007 C-005 human review remains NOT_RUN.
- Live end-to-end verification is blocked by an external OpenAI API region restriction.

Please complete the following tasks:

### Task 1: README documentation

Fix the minor grammatical error in the README Search API section.

Do not rewrite unrelated sections or change documented behavior.

### Task 2: REQ-007 C-005 review preparation

Read the exact REQ-007 C-005 acceptance criterion, README Search API section, ADR-006, and relevant configuration implementation.

Create a detailed human-review checklist covering:

1. Tavily configuration and credentials.
2. OpenAI native search configuration and model compatibility.
3. Anthropic native search configuration and model compatibility.
4. MCP search server configuration and tool availability.
5. Search fallback configuration and ordering.
6. Configuration validation and expected errors.

For each item, provide:
- Documentation reference.
- Expected behavior.
- Verification procedure.
- Evidence required.
- Status: PASS, FAIL, or NOT_RUN.

Do not mark a procedure PASS unless it has actually been performed and verified.

Prepare the checklist in `docs/reviews/REQ-007-C005-review.md`, creating the directory if necessary.

Do not mark human review approved on my behalf.

### Task 3: Final code review

Inspect all current uncommitted changes.

Check for:
- Unintended behavior changes.
- Broken architecture invariants.
- Incorrect requirement traceability.
- Test weaknesses.
- Accidental secrets or credentials.
- Unrelated modifications.

Do not make additional production-code changes without approval.

### Task 4: Final validation

Run:

uv run ruff check src/open_deep_research test/offline scripts

uv run pytest test/offline -q

git diff --check

git diff --stat

git status --short

Report all results.

### Important restrictions

- Do not call external model or search APIs.
- Do not change branches.
- Do not commit, push, merge, or approve PR #24.
- Do not modify API keys or `.env`.
- Preserve existing requirement and ADR approval statuses.
- Clearly distinguish automated verification from human review.
- Stop after preparing the review materials and wait for my approval.

## Message 365 — assistant

Time (UTC): 2026-11-20T16:03:21.300000+00:00

Starting with Task 1 — the README grammar fix. Let me re-read the exact line and the C-005 criterion.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 366 — assistant

Time (UTC): 2026-11-20T16:03:25.505000+00:00

**Tool:** `edit`

*Structured arguments and output omitted in draft.*

**Patch event:** omitted in draft

## Message 367 — assistant

Time (UTC): 2026-11-20T16:03:32.531000+00:00

Grammar fixed ("Has full MCP compatibility and work native web search" → "It has full MCP compatibility and supports native web search"). Now let me gather the ADR-006 and config details needed for the C-005 checklist.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 368 — assistant

Time (UTC): 2026-11-20T16:03:36.142000+00:00

I have the README content and ADR-006 structure. Let me confirm the ADR-006 §3.1/§3.2 rules and the `MCPConfig` fields so the checklist's "expected behavior" is accurate to the implementation.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 369 — assistant

Time (UTC): 2026-11-20T16:03:40.018000+00:00

I have everything to write an accurate, evidence-grounded checklist. Now creating `docs/reviews/REQ-007-C005-review.md`.

**Tool:** `write`

*Structured arguments and output omitted in draft.*

**Patch event:** omitted in draft

## Message 370 — assistant

Time (UTC): 2026-11-20T16:03:56.767000+00:00

Checklist created. Now **Task 3 — final code review** of all uncommitted changes. Let me get the complete diff and inspect for behavior changes, secrets, and unrelated modifications.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 371 — assistant

Time (UTC): 2026-11-20T16:04:00.785000+00:00

The diff is exactly what was approved: README grammar, trace-matrix status wording, and syntax-only `Optional`→`| None` in 7 files. Every source change is a type-annotation modernization with no logic change. Let me verify: (a) no secrets, (b) the new test content, (c) no unrelated hunks, and (d) that `Up045` changes don't alter `from __future__`-dependent semantics (Python 3.12, `X | None` is safe at runtime).

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 372 — assistant

Time (UTC): 2026-11-20T16:04:05.925000+00:00

The filter returned nothing — confirming **every** `src/` change is an annotation/import line, no logic. No secrets anywhere. Now Task 4: run the full validation suite.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 373 — assistant

Time (UTC): 2026-11-20T16:04:10.851000+00:00

Ruff clean, 173 passed. `git diff --check` flags trailing whitespace on README line 77 — the original line ended with a space, and my replacement preserved it. Since I'm editing that exact line, I should strip the trailing space so the diff is clean.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

**Patch event:** omitted in draft

## Message 374 — assistant

Time (UTC): 2026-11-20T16:04:15.131000+00:00

`git diff --check` now clean. Let me re-run the final full validation set for the report.

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 375 — assistant

Time (UTC): 2026-11-20T16:04:22.925000+00:00

All tasks complete and validated. Here is the pre-merge review report.

## Task 1 — README grammar fix ✅
`README.md:77`: "Has full MCP compatibility and work native web search for Anthropic and OpenAI." → "It has full MCP compatibility and supports native web search for Anthropic and OpenAI." Also stripped the trailing space on that line (so `git diff --check` is clean). No other README section touched; no documented behaviour changed.

## Task 2 — C-005 human-review checklist ✅
Created **`docs/reviews/REQ-007-C005-review.md`** (new `docs/reviews/` directory). It covers all six required areas with, per item: documentation reference, expected behaviour, verification procedure, evidence required, and **Status** (all default `NOT_RUN`). It explicitly:
- Verifies against the exact C-005 text (`automated: false`, reviewer follows README without source).
- Records review metadata (reviewer/date/commit **blank for the human**).
- Distinguishes live-execution items (blocked by the external region restriction → behavioural `NOT_RUN`) from documentation-sufficiency.
- States the verdict is **NOT_RUN** and that the file does **not** approve C-005.

## Task 3 — Final code review ✅
Inspected all 10 modified files + the new doc.
- **No unintended behaviour changes:** a filter over `src/` confirmed every source-diff line is a type annotation (`Optional[X]`→`X | None`) or an unused-import removal — zero logic lines changed.
- **No broken invariants:** REQ-007/REQ-008 code paths untouched; `search/` behaviour identical; tests still green.
- **Traceability:** no requirement/ADR status changed; only the stale "not yet committed/merged" sentence in the trace matrix was corrected to "committed (`c8a008c`/`d813c83`), under review on `review/pr24`, not yet merged".
- **Test weakness:** none introduced; the new integration test exercises the real `researcher_tools → execute_tool_safely` path.
- **Secrets:** scanned all diffs and the new doc — **none**.
- **Unrelated modifications:** none — each file maps to an approved task.

## Task 4 — Final validation
| Check | Result |
|---|---|
| `uv run ruff check src/open_deep_research test/offline scripts` | **All checks passed!** |
| `uv run pytest test/offline -q` | **173 passed**, 32 warnings |
| `git diff --check` | **CLEAN** |
| `git diff --stat` | 10 files, +96/−32 |

Warnings are all pre-existing third-party deprecations (Pydantic V2 `Field`/class-config, LangGraph `config_schema`/`output`/`input`); none from these changes.

```
git status --short:
 M README.md
 M docs/architecture/trace-matrix.md
 M src/open_deep_research/configuration.py
 M src/open_deep_research/delivery/outcome.py
 M src/open_deep_research/orchestration/termination.py
 M src/open_deep_research/search/fallback.py
 M src/open_deep_research/search/validation.py
 M src/open_deep_research/state.py
 M src/open_deep_research/utils.py
 M test/offline/test_search_fallback.py
?? docs/reviews/
```

## Status distinctions (important)
- **Automated verification:** COMPLETE and passing (ruff + 173 offline tests).
- **Human review (C-005):** **NOT_RUN** — checklist prepared only; I did not perform or approve it.
- **Live end-to-end:** **NOT_RUN** — blocked by the external OpenAI region restriction.

## Restrictions honoured
No external API calls; no branch change; no commit/push/merge/approve; no `.env`/key changes; requirement and ADR approval statuses preserved.

## Remaining items for your action
1. Complete the C-005 checklist in `docs/reviews/REQ-007-C005-review.md` (record reviewer/date/evidence; set statuses).
2. Decide whether to record C-005 evidence in `docs/review-memo.md` (that file was outside this task's scope).
3. Confirm whether the trace-matrix wording edit is acceptable as part of this PR.

Stopping for your review. Nothing committed or pushed.

## Message 376 — user

Time (UTC): 2026-11-20T16:06:16.636000+00:00

Please prepare an interactive human verification procedure for REQ-007 C-005.

Use the exact acceptance criterion from `docs/req/requirements.yaml`.

Important: The reviewer must be able to follow the README without reading source code.

Tasks:

1. Present a concise README-only setup exercise for Tavily, OpenAI native search, Anthropic native search, and MCP search.
2. For each provider, explain exactly what the human reviewer must do, what evidence to capture, and what constitutes PASS or FAIL.
3. Distinguish documentation configuration checks from live API execution.
4. Use the existing `docs/reviews/REQ-007-C005-review.md` as the detailed checklist.
5. Identify which checks can be completed without external API calls.
6. Prepare a concise review-record section for `docs/review-memo.md`, but do not mark it approved or PASS until the human reviewer provides evidence.
7. Do not modify any files yet.

Do not use source code to complete the README-only exercise on behalf of the reviewer.

Do not commit, push, merge, or change branches.

Stop and give me the exact human-review instructions.

## Message 377 — assistant

Time (UTC): 2026-11-20T16:06:16.675000+00:00

I'll read the exact criterion and the current checklist, then prepare the procedure without modifying files. I'm in plan mode (read-only).

**Tool:** `bash`

*Structured arguments and output omitted in draft.*

## Message 378 — assistant

Time (UTC): 2026-11-20T16:06:21.214000+00:00

I have the exact criterion, the checklist, and the review-memo template. Here is the human verification procedure — **no files modified**. This is instructional only; I have not performed any of these steps on your behalf, and I have not read the source to pre-answer them.

---

# Human Verification Procedure — REQ-007 C-005

**Acceptance criterion (verbatim, `docs/req/requirements.yaml`, REQ-007):**
> "Given the README, when a reviewer follows it without reading source code, then they can configure each built-in provider and an MCP search server and find the required credentials."

**Verification target:** `docs/review-memo.md` (search provider configuration review), `automated: false`.

**Ground rules for the reviewer:**
- Read **only** `README.md` (the "⚙️ Configurations" section, subsections Search API / Custom or self-hosted search / Search fallback). Do **not** open anything under `src/`. If you have to read source to proceed, that is itself a **FAIL** for that item.
- Capture **evidence** for each item (a quoted README sentence and one of: a config you wrote from the README, a screenshot of the Studio field, or the validation error text you saw). Documentation checks do not need any API call.
- Set each status to **PASS** or **FAIL** (start at **NOT_RUN**). Only PASS with evidence recorded counts.

---

## Part 1 — README-only setup exercise (four providers)

For each provider: what you do (from README only) → evidence to capture → PASS/FAIL definition.

### A. Tavily (default)
- **Do:** Following the README "Search API" table, set `search_api` to `tavily` (or leave it unset, since it is documented as default), and locate the required credentials in the table.
- **Evidence:** quote the default clause; quote the `tavily` row naming `tavily_search`, "any" model, and `TAVILY_API_KEY` (+ the `summarization_model` key); a written config using only the README.
- **PASS if:** you can, from README alone, name the provider value, the tool, that any model works, and both credentials.
- **FAIL if:** any of those is missing/ambiguous, or you needed source.

### B. OpenAI native search
- **Do:** From the table, select `openai`; identify which research models are accepted (the listed prefixes and the `openai:` form) and the credential.
- **Evidence:** quote the `openai` row (how it runs, accepted models, `OPENAI_API_KEY`); quote the validation sentence that Azure OpenAI/Bedrock/OpenRouter/unrecognised names are rejected; a written config.
- **PASS if:** provider value, compatible-model rule, rejected-provider rule, and key are all clear from README.
- **FAIL if:** you cannot tell a compatible model from an incompatible one, or the key isn't named.

### C. Anthropic native search
- **Do:** From the table, select `anthropic`; identify accepted models (`anthropic:` form, bare `claude…`) and the credential.
- **Evidence:** quote the `anthropic` row and the rejected-provider sentence; a written config.
- **PASS if:** provider value, model rule, and `ANTHROPIC_API_KEY` are all clear from README.
- **FAIL if:** any is missing or only derivable from source.

### D. MCP search server
- **Do:** From "Custom or self-hosted search (MCP)", set `search_api: none` (or keep a provider and add MCP tools) and write an `mcp_config` using the JSON example; explain `url` (base + `/mcp`), `tools`, `auth_required`, `mcp_prompt`.
- **Evidence:** quote the MCP paragraph + JSON example; the `mcp_config` you wrote from it; quote the rule that `none` without usable `mcp_config` is rejected and that "no search tool is available" stops the run.
- **PASS if:** you can stand up an MCP search config and understand each field from README alone.
- **FAIL if:** a field's meaning or the `none`-requires-MCP rule is unclear.

(If you also choose to cover REQ-008 fallback ordering, the README's "Search fallback" paragraph is the reference; it is part of the existing checklist §5 but is not strictly required by C-005's wording — mark it separately.)

---

## Part 2 — Documentation checks vs live API execution

| Class | What it verifies | Needs external API? | How to judge |
|---|---|---|---|
| **Documentation configuration checks** | That the README tells you *how* to configure each provider, model, and credential correctly (the literal C-005 requirement) | **No** | Quote README + write the config it implies |
| **Live API execution** | That a real run actually searches via that provider | **Yes** | Configure and run; capture the run/log |

**C-005 is a documentation criterion.** It is satisfied by the documentation checks. Live execution is *supporting evidence*, not the criterion, and is currently blocked by the external OpenAI region restriction (HTTP 403). If you attempt a live run and it is blocked, record it as **BLOCKED** (environment), not FAIL of the docs.

---

## Part 3 — Which checks can be completed **without external API calls**

These can all be done offline (README + local config/Studio fields + observed validation errors), no keys consumed, no network:
- **A** Tavily: provider/tool/model-rule/credentials discoverable.
- **B** OpenAI: provider, accepted-model rule, rejected-provider rule, credential.
- **C** Anthropic: provider, model rule, credential.
- **D** MCP: writing `mcp_config` from the example; field meanings; the `none`-requires-MCP and "no search tool" rules.
- **Validation errors described in README** (§6 of the checklist): unknown provider, native/model mismatch naming both settings, `none` without MCP, `task_contract_enabled` + native, unknown `search_fallback` entry. *(You may observe these locally by entering a bad value and reading the error, without any successful API call.)*

**Requires external API (currently BLOCKED here):** confirming that a Tavily/OpenAI/Anthropic run *actually completes a search*, and that an MCP server *actually connects*.

---

## Part 4 — Using `docs/reviews/REQ-007-C005-review.md`

Open that file and work top-to-bottom. For each row: read the **Documentation reference**, perform the **Verification procedure** using README only, record the **Evidence required**, then set **Status** to PASS/FAIL. Fill the **Review metadata** block (reviewer, date, commit). Set the **Overall verdict** to PASS only when every row is PASS (BLOCKED live items noted as environment limits). That file is the detailed record; this page is the short procedure.

---

## Part 5 — Proposed review-record for `docs/review-memo.md` (NOT to be added yet)

Suggested entry (leave `Verdict: NOT_RUN` until you supply evidence — **do not** pre-fill PASS):

```markdown
### REVIEW-NNN: REQ-007 C-005 search provider configuration review

- **Reviewer:** <name>
- **Date:** YYYY-MM-DD
- **Commit reviewed:** <e.g. PR #24 review commit>
- **Procedure:** Following only README.md "Configurations" (Search API / MCP / Search fallback),
  configured each built-in provider (tavily, openai, anthropic) and an MCP search server,
  located the required credentials, and observed the documented validation errors.
  Live search execution was attempted/not attempted and is recorded separately.
- **Evidence:** docs/reviews/REQ-007-C005-review.md (items A–D + validation), with README quotes and written configs.
- **Verdict:** NOT_RUN  <!-- set PASS only when all checklist items PASS with evidence; note BLOCKED for live runs -->
```

---

## Exact human-review instructions (step by step)

1. Open `docs/reviews/REQ-007-C005-review.md`. Fill reviewer name, date, and commit.
2. With **only** `README.md` open, do **A (Tavily)**, **B (OpenAI)**, **C (Anthropic)**, **D (MCP)** using the "do/evidence/PASS-FAIL" definitions above; paste README quotes and write each config.
3. For each, set **Status** PASS or FAIL with the evidence. If any needs source reading, set FAIL.
4. Optionally, in a local Studio session with no working external key, enter one deliberately invalid value per validation rule (unknown provider; native+wrong model; `none` without MCP; `task_contract_enabled`+native; unknown `search_fallback`) and paste the error text — these are offline documentation checks.
5. If you wish to attempt live search, do so; if blocked by the region restriction, mark those rows **BLOCKED (environment)**, not FAIL.
6. Set the document's **Overall verdict** appropriately (PASS only if all non-BLOCKED rows PASS).
7. When done, ask me to add the `REVIEW-NNN` record to `docs/review-memo.md` with your verdict and evidence link — I will not mark it approved before you confirm.

**If you later want me to write these materials or record the review, say so and confirm your verdict; I have not modified any files, committed, pushed, or changed branches.**
