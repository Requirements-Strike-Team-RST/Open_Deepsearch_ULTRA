# Orchestration module — local SA review pack

- **Owner:** Centay / XIE Shentai, 61061965.
- **Scope:** REQ-001 and REQ-003; REQ-002 C-005/C-007 contributor interfaces.
- **Baseline:** `827fd32f956a0601df3e1fd253d5cc98044fff88` (merged PR #4 templates).
- **Local branch:** `docs/sa-orchestration`.
- **Revision:** 2026-11-15; 11/14 package retained as the historical v1 checkpoint.
- **State:** Proposed; ready for human review after the local checks below. No human
  module review, SA Review, test approval, implementation or runtime verification
  is claimed. The student handles publication and final Git/shared actions.

## Read this first

1. [ADR-002](adr/002-orchestration-contract-and-termination.md): decisions, precise
   interfaces, boundary algorithms, context assembly and future implementation steps.
2. EVAL-002 in [evaluation-table.md](evaluation-table.md): three candidates and
   critical-driver comparison; ratings are design analysis, not test evidence.
3. INV-003/006/007, orchestration memory/runtime sections, structural §10,
   verification §7 and trace-matrix REQ-001/003 rows.
4. [Annotated D5 record](../../transcripts/61061965-XIE_Shentai.md) and linked raw
   prompts/events/exports. D1 records AIU-008–012 are drafts for the student's review;
   review-memo's PREP record is explicitly AI preparation, not a human approval.

Tekon's context design and Alchemy's main-branch governance are the primary quality
references. Their useful practices are explicit failure boundaries, implementable
steps, exact acceptance mappings and honest verdicts; their drafts are not approval
of this module. Other peer drafts are interface context only.

## Concrete interface decisions for the readers

| Item | Proposed contract / review question | Readers / decision needed |
|---|---|---|
| R-01 Delegation acceptance | Validate before dispatch; every accepted valid spec has one result. Invalid raw intents have rejected diagnostic receipts and feedback, without fake questions. Same-ID replay is idempotent; changed arguments preserve the original task and reject the new intent. | Alchemy and Centay: confirm accepted-delegation versus rejected-intent terminology and transport diagnostics against REQ-001/002. |
| R-02 Evidence and cost | Per-task code-owned holder, copied private runtime config, serializable state snapshots; `build_task_result`, `validate_task_result`, `failed_result` require keyword-only evidence. Wrapper preserves spent calls on exception; additive TaskCost.usage_complete marks incomplete token totals. Ambient as well as bound model config is cleaned. Unknown crash-window execution is not automatically replayed. | Alchemy, Tekon and Centay: agree receipt handoff, helper arguments, checkpoint reconstruction and unfinished-receipt policy before Build. |
| R-03 Dispatch and finalization | Delivery receives an ordered RegisteredDelegation list, retained per-task evidence and injected contract callables; its proposed JoinedTurn port returns one ordered plain-list result delta regardless of completion order; node writes it once. Terminal finalization overrides the complete subgraph results/notes; compiled output is a plain list appended once to the parent channels cleared by the brief boundary. All tasks join before any end-of-turn exit; raw rejections are node-owned feedback, not result variants. Valid typed results with missing auxiliary summary text are rendered canonically, never replaced by a placeholder. | Alchemy: approve the exact shared hunk/call order. Delivery owns queues, isolation, join, missing-output handling and run outcome. |
| R-04 Compression and citations | Keep `CompressionOutcome.summary: str`; exactly one version-1 JSON findings sidecar before final unique `### Sources`; `[n] Title: URL` format stays. Discard free-text body and sidecar from reader-facing strings, render complete/partial validated findings, then return to delivery; notes use only those findings/sources. | Tekon and citations owner: approve the prompt/parser boundary, protected system instructions and single retry owner. This does not add final-report semantic citation validation. |
| R-05 Flags | Off/off baseline; on/off typed results with baseline context recovery; on/on one context retry loop; off/on lacks TaskSpec and needs context/delivery exception policy. | Tekon and Alchemy: resolve off/on explicitly. That part of ORC-036 is BLOCKED until their decision; no silent flag dependency. |
| R-06 Native search | Enabled path refuses native search before a researcher request capable of server-side tool execution, until strict pre-request caps and auditable counts/provenance exist. No provider switch or hidden fallback. | Search owner, Alchemy and Centay: approve narrowed compatibility or supply an audited adapter. Search's REQ-007 validator remains separate. |
| R-07 Exit semantics | Distinct normalized questions; exact fractions and decimal threshold; processed-turn counter with N=1/N=2 behavior; think-only ignored for stall; completion-only/no-tool eligible; covered > cap > stall > supervisor error. | Alchemy/Centay: confirm threshold 0.8, all mixed/cap/pending examples and delivery's interpretation of covered with partial/not_run tasks. |
| R-08 Fresh versus resumed runs | Main resets public run fields; keep default per-invocation subgraph compilation for fresh private channels. Same-call resume keeps checkpoints; do not reset based on None exit_reason. Flag comparisons use fresh state; cross-mode reuse of a prior enabled checkpoint requires an agreed reset/migration policy and is not claimed as supported here. | Centay/Alchemy: ORC-039 must prove this on locked LangGraph before claiming runtime behavior. No new node or per-thread persistence mode is proposed. |
| R-09 Shared source hunk | Context ADR-005 proposes editing the missing-summary consumer inside supervisor_tools; that is also delivery's result-collection region. | Alchemy and Tekon: choose one implementation owner; the integrator must reconcile rather than merge two competing edits. |
| R-10 Recovery and query details | Caller retains evidence outside clean recovery context; parse once after a matching normal return (length/unknown: zero parses); max_attempts=3 permits failure/failure/success. Context recomputes instruction position/indices for each current trimmed list. RunRecord.unanswered_questions derives from existing question/answer fields; no task-count ratio or one-decimal rounding. | Tekon/Alchemy confirm these boundary conditions in their own drafts; no recovery.py implementation or indexing failure is claimed observed. |
| R-11 Response completion | Node-owned observing Runnable keeps context's signature/CompressionOutcome.summary:str and all DTO/helper arguments unchanged. Observe attempts inside existing retry, then accept once after return: compression length→failed/token_limit, unknown→failed/runtime, normal→parse; unusable control response enters existing model-operation failure boundary. No new request/enum/graph path. | Alchemy/Tekon and enabled-model readers: review conservative support/failure policy and phase mappings. Alchemy separately resolves final-report output truncation; do not equate it with input omission partial. |
| R-12 Internal budget placement | budget.py owns existing admission/capability policy; evidence.py owns the same receipt's actual starts/results/source/usage/completion observations. No second counter, lock, runtime key, public field or argument; preserve stable exports/compatibility entry if already referenced. | Centay internal organization; readers confirm no qualified-import dependency. This is not a new shared budget service or Alchemy scheduling change. |

All rows are **pending reader review**, not approved decisions. Local field/ADR/
EVAL/INV/POL/AIU numbers can collide with peer branches and must be reconciled during
integration while retaining each member's commits.

## Simulated peer challenge requested by the student

Two fresh OpenCode plan sessions independently walked the proposed contract from
Alchemy's delivery requirements and Tekon/BroZhai's context draft perspectives.
They are AI simulations, not those students' reviews or approval. Follow-up
reconciliation and all original findings are preserved in D5, including retractions.

- **Adopted:** a precise ordered JoinedTurn port; missing auxiliary legacy-string
  behavior with one valid typed result; producer output-field completeness;
  caller-retained evidence, one parse and one retry owner; cap-entry diagnostic
  publication and the computed unanswered-question reader. ORC-044–046 supplement
  the inventory; ORC-043 covers the entry diagnostic edge.
- **Corrected AI assumptions:** questions/answer links were already present in
  TaskResult; task counts are not question coverage. The concrete shared example
  yields 9/10 and delivery partial despite covered. Failure/failure/success is
  three calls within max_attempts=3. A computed floating value is not the literal
  configured default, and no one-decimal rounding is proposed.
- **Remains human integration work:** shared consumer-hunk ownership, off/on
  policy, recovery index contract in the context draft and the existing R-01–R-10
  reader decisions. No product/runtime test was run by these walkthroughs.

## Changes from the historical v0.5 discussion

| Historical assumption | Proposed correction and reason |
|---|---|
| max_tool_calls counted tool-calling turns | Count actual started executable invocations, as approved REQ-001 states; retain a separate model-turn watchdog. |
| Build provenance from researcher messages | Capture trusted execution receipts before trimming, excluding reflection/error/prose; preserve actual cost on failure. |
| Complete/partial summaries are safe report notes | Discard raw compression prose from reader-facing strings; render only complete/partial tasks' validated findings and their sources. |
| task_results cannot exist without exit_reason | That is the **final main reader** contract. Running supervisor ledger/checkpoints legitimately precede terminal fields. |
| Abstract schema/prompt extraction | Exact sidecar grammar, typed rejection rules, question/source identity, strict cost constraints and a parse/strip boundary. |
| Ambiguous cap/stall behavior | Processed-turn counter, N=1/N=2 examples, think-only treatment, exact fractions and registration before final denominator calculation. |
| Helper failures default cost to zero | Required trusted evidence preserves spent calls; not_run alone is zero by construction. Additive usage_complete=False exposes incomplete token observations. |

Public status/category/reason names, TaskCost.tool_calls, external ConductResearch
name and the per-turn result-delta handoff remain recognizable. All refinements are
Proposed and require shared-reader agreement; the online reference was not edited.

## 2026-11-15 follow-up: compatible internal refinement

The current Google document index and field-contract reference were read again.
The index's cell values/formulas/hyperlinks and the v0.5 field-contract bytes match
the 11/14 captures. No online document was edited. This revision preserves the
previous local draft's DTOs, enums, helper arguments and context return type;
previous R-01–R-10 differences still require reader review. Internal placement and
new failure-policy proposals do not constitute their acceptance.

- Split budget admission from factual evidence ownership while retaining one
  receipt; contracts remain read-only consumers of it.
- Add explicit response-completion acceptance before control dispatch or sidecar
  parsing, with zero extra completion retries and no context API change.
- Add ORC-047–053: **53 planned cases total**, with POL-011/012. None are product
  tests yet. Gateway probes and isolated baseline/adapter experiments supply the
  diagnosis, not a passing orchestration fix or an SA gate.
- Keep final-report outcome and proactive input-token policy with their existing
  owners. Unsupported adapter mappings remain explicit compatibility review.

See the [dated experiment and reference record](../../transcripts/raw/61061965-XIE_Shentai/followup-20261115-experiments.md)
for exact commands, captured markers, limitations and attribution. Three direct
school-DeepSeek requests were made across the investigation; they were Codex-run
HTTP probes, not additional OpenCode sessions. No Claude call occurred.

## Course and integration items outside this module's acceptance

- Course D2.2 requires an input-token cap and compaction threshold. Current config
  provides output caps and a character limit; context ADR-005 provides bounded
  reactive recovery. A proactive, model-window-aware input budget remains a
  **Gate 1 integration gap** for Tekon/Alchemy. Do not substitute output max_tokens
  or a guessed tokenizer/window value.
- The course permission prose calls for default deny/explicit whitelists, while
  current accepted project governance permits broad routine reads/SA edits. Several
  of the six required CI gates are still Planned. Review these globally; this
  branch changes no permissions, governance rules or CI configuration.
- Course D4 verdict wording, the blueprint packaging location and the transcript
  count differ between source passages/templates. Follow current Git paths during
  module work; the integrator confirms final course packaging and human records.
- D5 here covers SA only. Human plan approval, Test Author baseline failures,
  Gate 2, Build, Verify and test-driven architecture revision require later genuine
  evidence. The AI preparation memo cannot substitute for a teammate review.

The detailed course/peer audits are preserved alongside the D5 raw evidence, with
source page numbers. Canvas was accessed with GET only; no coursework was submitted.

## Verification actually performed

| Check | Verdict / evidence |
|---|---|
| Current Git main and isolated branch | PASS: main resolved to the baseline above; old checkout edits preserved. |
| Existing requirement schema validator | PASS: 10 requirements valid. Command: `uv run --no-project --python /opt/homebrew/bin/python3.12 --with pyyaml --with jsonschema python scripts/validate_requirements.py`. Temporary tool environment; project dependency files unchanged. |
| Whitespace, scope, references, YAML, table/link checks and raw capture integrity | PASS: 14 external static checks, including every assigned C-/M- reference and 53 planned cases in the 11/15 revision. Exact commands/results: [static audit](../../transcripts/raw/61061965-XIE_Shentai/followup-20261115-static-validation.md). No functional PASS is implied. |
| OpenCode provider/role | PASS: school DeepSeek preflight and exported sessions identify CityU provider / plan. No Claude request was made. |
| OpenCode authoring completeness | Round 2 wrote EVAL-002, then hit its 8,192-token output limit before an ADR write completed. Codex and read-only AI assistants completed the proposed ADR/module tables; bounded OpenCode reviews and their dispositions are recorded separately. Final round 4 found no remaining contradiction in the supplied ADR, explicitly a limited static reading. |
| Artifact credentials and old checkout preservation | PASS: no exact known credential matches in the Git-visible artifacts; original blueprint hashes and checkout status are unchanged. Raw reports record the scan scope and limits. |
| Runtime/contract/regression/live tests | NOT_RUN: no test or implementation code was written in SA. |
| Human module review, Gate 1 / Gate 2 | NOT_RUN; shared-reader decisions above remain pending. |

## Publishing and integration handoff

The student reviews the diff/patch, confirms interface decisions with readers and
publishes a Draft PR to main with at least one reviewer. Do not merge individual
module Draft PRs. The integrator later merges member branches into one integration
branch, reconciles IDs/interfaces/state, writes the system blueprint and obtains
the whole-team SA Review. Tests and implementation start only after their gates.
