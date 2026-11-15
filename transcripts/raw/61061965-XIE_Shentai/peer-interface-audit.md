# Read-only peer interface audit for orchestration SA

Date: 2026-11-14 (Asia/Taipei). Scope: compare downloaded peer SA proposals with the historical Centay v0.5 contract and main `827fd32f956a0601df3e1fd253d5cc98044fff88`. This is an AI static audit, not a human review, gate approval, experiment or implementation result. No peer file was changed.

## Evidence revisions

The exact snapshots are recorded in `peer-sa-snapshots/manifest.json`:

| Branch | Revision |
|---|---|
| `docs/sa-context` | `2f74868a0dc4719c7cf1023f00f45cd0ed6359e1` |
| `docs/sa-citations` | `a6feb7447010cf270b2fd9f2bb1cc1d36807a934` |
| `docs/sa-search-provider` | `adb8d0a5e48fae45ce4dc7b020008db910645a6d` |
| `docs/sa-evaluation` | `e3507afcdda5b715227cf9f51edff822bac40a36` |

All four ADRs say **Proposed**. Their design choices are useful compatibility inputs; none supplies a Gate 1 acceptance or permission to change another owner's scope.

## Context: preserve its text interface and protected messages

Evidence: `peer-sa-snapshots/sa-context/docs/architecture/adr/005-context-adr.md`.

- Lines 59–76 protect the preamble, the compression instruction and the newest AI turn with its tool results, removing only whole older turns. Put the task topic/scope/questions/budget in the initial HumanMessage preamble; preserve its exact question strings. An orchestration findings instruction must be in a protected system prompt or in the final compression HumanMessage, not an expendable old AI turn.
- Lines 109–112 define `compress_with_recovery(...)->CompressionOutcome(summary: str, raw_notes: str, removed_turn_indices: tuple[int,...])`. Lines 204–206 explicitly obtain `summary=str(response.content)`. Replacing the passed model with one that directly returns a Pydantic object would break this interface.
- Lines 88–90 and 115–121 require `TokenLimitExceeded` to map at the node to the REQ-001 failed/token_limit result. Keep the public factory `failed_result(spec, "token_limit", message)` and the actual fields `failure_category` / `failure_reason`; peer prose's shorthand `category` / `reason` is not a new field schema. No stack trace or failure text belongs in summary/notes.
- Lines 125–129 leave state to REQ-001 and let non-token exceptions propagate for delivery to isolate. Orchestration should not put alternative trimming or exception-isolation logic into its helpers.
- Lines 195–196 propose context-local `ResearchTurn.source_urls`. Do **not** treat this as orchestration's authoritative provenance ledger: it is derived from potentially trimmed history and is not specified to exclude reflection/error outputs. Provenance and actual tool-call counters must survive outside mutable message history.

Required integration decisions:

1. The node's success-result mapping must happen after either compression path returns. Context owns recovery; orchestration owns successful `TaskResult` construction. Avoid two competing complete rewrites of `compress_research`.
2. Peer step 10 (lines 221–224) also edits the `supervisor_tools` consumer default, overlapping delivery ownership. Assign this hunk once at integration; orchestration only defines invalid-result/failure helpers.
3. Define all four flag combinations: `context_trimming` and `orchestration_enabled`. In particular, context-on/orchestration-off has no v0.5 TaskSpec, yet context promises failed/token_limit while v0.5 forbids writing orchestration state when disabled. Do not silently introduce an alternate result type or a hidden flag dependency.
4. Recovery attempts (default 3) are compression model attempts, not researcher tool calls. Do not debit them as tool calls or change context's retry budget as a side effect of REQ-001.

## Citations: keep the canonical Markdown contract

Evidence: `peer-sa-snapshots/sa-citations/docs/architecture/adr/001-unified-citation-format.md`.

Lines 65–83 establish the exact proposed grammar:

- Inline references are `[n]`.
- Each unique URL has one citation number.
- The final section heading is exactly `### Sources`.
- Entries are `[n] Title: URL`, numbered consecutively from 1, one entry per URL.
- The report prompt asks the model to renumber across independent researcher findings.

Lines 85–112 preserve the public prompt names as plain strings and resolve citation placeholders at module load before existing runtime `.format(...)`. Lines 119–122 leave generated-report citation validation/rewriting out of scope; INV-004 remains Deferred.

Compatible orchestration proposal for review:

1. Keep compression output as one Markdown string using that same citation grammar. Do not replace it with a JSON-only answer or add a second Sources format.
2. When orchestration is enabled, add one explicitly delimited, schema-validated JSON findings sidecar **before** the canonical Sources section. Candidate entries contain `claim`, `answers` (exact TaskSpec question strings) and numeric citation references resolving through that one Sources list. The sidecar supplies the claim/question relation that Markdown alone cannot determine.
3. Orchestration parses the sidecar as untrusted input, resolves candidate references, checks each URL against the task's code-recorded provenance, discards unsourced findings and derives status/coverage itself. Missing or malformed required machine structure becomes invalid_result, never an inferred complete result.
4. Strip the sidecar from the stored human-readable summary. Render final notes from validated findings and their sources rather than accepting the complete free-text summary as validated evidence. Preserve the agreed Sources grammar in those rendered task notes; leave final cross-task numbering to the report prompt.
5. Append the orchestration instruction after the base citation prompt has been runtime-formatted, or escape any literal JSON braces. Preserve citations' string-substitution interface and do not add unresolved format keys.

This is a **proposal**, not peer approval. The citations owner must review the flag-on prompt composition and its regression cases. A structured-response object with a Markdown `summary` field is another option only if the context outcome is deliberately revised jointly; it is not compatible with the present `str(response.content)` implementation plan.

## Search: native support is valid configuration, not a budget guarantee

Evidence: `peer-sa-snapshots/sa-search-provider/docs/architecture/adr/001-search-configuration-validation.md`.

- Lines 23–30 and 88–114 accept native `anthropic` / `openai` only with a matching `research_model` prefix; Tavily accepts any research model; `none` requires statically declared MCP tools. Credential absence is runtime, not configuration invalidity.
- Lines 58 and 73–79 leave `get_all_tools`, `get_search_tool`, `load_mcp_tools`, state and configuration fields unchanged. REQ-008 fallback is expressly outside this draft.
- Lines 112–114 and 156–161 distinguish static MCP declaration from runtime availability; an unreachable declared MCP is an unresolved ownership decision, not an implemented failure signal.

Orchestration must preserve the validator and the single tool assembly entry. Its native-search problem remains open: native tools execute inside the model request before `researcher_tools`, and existing detector helpers return bool rather than actual counts. A strict task-call cap requires request-before-execution limits plus trustworthy actual count/provenance adapters, including retry accounting. A post-response count cannot prevent overspend.

Do not silently switch provider, disable a native tool, claim the peer supplied a budget adapter, or assume MCP static validity proves evidence exists. If the enabled orchestration mode temporarily rejects a provider whose cap cannot be enforced, record this as an explicit cross-module Review decision and runtime limitation; do not change the search validator without its owner's agreement.

## Evaluation: optional evidence remains independent

Evidence: `peer-sa-snapshots/sa-evaluation/docs/architecture/adr/001-evaluation-module.md`, lines 60–88 and 130–143.

The public entry takes an existing question/report plus optional `research_brief` and `evidence` (`raw_notes` equivalent). It does not require TaskResult or RunRecord and must never invoke the research graph. Missing evidence makes only groundedness not_evaluable; missing brief makes only completeness not_evaluable. Preserve `research_brief` and compatible raw_notes outputs, and do not present run coverage as an evaluator score or change the evaluation entry to depend on orchestration code. Its draft changes no shared state types.

## Suggested module Review agenda

1. Citations + context: approve the optional machine-readable sidecar and protected prompt placement while preserving the canonical Markdown and string recovery interface.
2. Context + delivery: agree sole ownership of compression node mappings and consumer default removal; decide context-on/orchestration-off failure behavior.
3. Search + delivery: decide supported native budget/provenance adapters and declared-but-unavailable MCP behavior, with no silent provider fallback.
4. All shared-contract readers: approve final snapshot vs running ledger semantics, failure factories, provenance rules and notes made only from validated findings.
