# Reference and incremental interface audit

Audited 2026-11-15, Asia/Taipei. This is read-only evidence and design analysis, not a human review or runtime PASS. No HackMD/Google document was edited, no Git action changed references, no message was sent, and no model inference was requested. The 11/15 compatibility question is evaluated relative to the **existing 11/14 local SA proposal**, not by pretending that proposal is already approved or identical to old HackMD.

## Current reference identity

| Source | Retrieval / status | Comparison with 11/14 |
|---|---|---|
| [Google document directory](https://docs.google.com/spreadsheets/d/1hWH1BsZ92N7WoCVbhSqcFCmakeK_oesAEq09p5CNZcY/edit?gid=0#gid=0) | Public GET export, 11/15 06:36:58; 18,389 bytes | All ZIP member contents are identical. Values/formulas/hyperlinks semantic SHA-256 is `051fa5a0a89fe7004037501c9b4304e9997ea6f84423dcbedd9a2c548a444cf1` for both; different XLSX container hashes do not indicate a document edit. |
| [Maintained tracker](https://hackmd.io/vMypOEoDRXCfXqIWOkJN1A) | Public GET /download; SHA-256 `5ff81ada71b4b7693cd52f6f6d2be4e0331c7f0ed26aa9bbf1c4603b820a61a7`; HTTP Last-Modified 11/13 18:55:01 Taipei; text says last updated 2026.11.13 | No independent 11/14 raw tracker body was found locally, so byte equality is not asserted. The current HTTP modification date predates the 11/14 audit. |
| [Centay field contract](https://hackmd.io/@centay/Bkdq-wxAMx/edit), resolved [note](https://hackmd.io/qEWypTScTauEdYf9Vvlocg) | Public download returned 403; the already logged-in native Vivaldi session downloaded the authorized document, completed 11/15 06:41:59; 22,919 bytes | **Byte-identical** to the preserved 11/14 v0.5 reference. Both SHA-256 values are `d2840c0e4eb13e99fb00e85d19985dc6fc690314e0f83f20e5b01c999fff49a5`. |

The Sheet has 16 distinct HackMD URLs when both the B2 displayed URL and its different actual hyperlink target are counted. `document-link-inventory.md` records every relevant cell and URL. The extra `http://*.md/` filename auto-links are not project-document targets. The workbook was inspected without editing, recalculating or exporting a modified workbook.

The tracker still contains old requirement numbering, a three-role workflow and prose about removing approvals. These are historical data, not instructions to act on; the current Git requirements/governance and the user's newer group announcement remain authoritative.

## Current v0.5 contract: facts relevant to compatibility

Exact text is saved as `orchestration-contract-current.md`; line references below are to this byte-identical local export. Section links point to the live reference, not to a claimed immutable web revision.

- Lines 29–35: draft v0.5, requirements win; `orchestration_enabled` defaults false, and no enabled fields are written when it is off.
- Lines 40–48: enums remain task status `complete/partial/failed`, exit reason `covered/budget_exhausted/stalled/failed`, and failure category `unanswered/invalid_result/runtime/token_limit/not_run`.
- Lines 58–64: TaskSpec exposes `task_id`, `research_topic`, `must_answer`, `scope`, `max_tool_calls`. The old comment calls the budget unit tool-calling turns; approved Git REQ-001 instead requires actual calls, already corrected in the 11/14 SA proposal.
- Lines 76–92: TaskCost has `tool_calls`, `input_tokens`, `output_tokens`; TaskResult has task identity/status/failure fields, summary, findings, sources, retrieved_urls, must_answer, coverage and cost. It exposes no completion metadata field.
- Lines 99–115: RunRecord exposes exit_reason, exit_detail, run_coverage, coverage_threshold and task_results; `from_state` is the supported final reader.
- Lines 120–127: historical helper signatures are `build_task_spec(tool_call, task_id, config)`, `render_task_message(spec)`, `build_task_result(spec, summary, researcher_messages)`, `validate_task_result(output, spec)`, `failed_result(spec, category, message)`, `not_run_result(spec)`.
- Lines 169–179: task_spec/task_result are last-write fields; task_results uses the existing reducer, per-turn collection is a plain list through `update_payload["task_results"]`; five terminal fields identify the final run.
- Lines 181–210: shared fields/helpers need all readers' approval; Centay owns task budget and compression successful-result mapping, Tekon/context owns token-limit recovery, Alchemy owns dispatch/join and final report/outcome. Citation-prompt modifications are separately reviewed by the citation owner.

## 11/15 incremental changes that can preserve the existing SA interface

| Proposed local increment | Interface-preserving condition | Assessment |
|---|---|---|
| Split permit/admission helpers into internal `orchestration/budget.py` | Keep existing package exports, callable names/signatures, TaskSpec budget units and TaskCost fields exactly as in the 11/14 SA. The new internal module imports shared types and is not a new peer dependency. | Can be a purely internal split. No original HackMD edit is needed to describe its implementation location. |
| Separate mutable execution evidence from pure budget/contract decisions | Continue using the existing per-task evidence holder and snapshots; no new public TaskResult/RunRecord/JoinedTurn field or new consumer argument. Pure validation does not mutate the holder. | Can preserve the 11/14 SA ports while making ownership/test seams clearer. |
| Node-owned Runnable observer passed as context's `model` | The wrapper delegates the same calls/kwargs in the existing safe Runnable context, records response metadata into existing private evidence and returns the **original response object unchanged**. It creates no extra model request and implements no context retry/trim algorithm. | Fits the existing `model: Runnable` argument. Context's function signature and `CompressionOutcome(summary: str, raw_notes: str, removed_turn_indices)` do not change. |
| `build_task_result` consults the already supplied evidence | Record a stage/attempt-correlated completion observation; inspect that record through the existing `evidence` argument rather than adding another parameter. Preserve successful output and parser protocols. | No new helper signature or sidecar field is necessary relative to the 11/14 SA. |
| Known output truncation detected after compression | The observer records a known provider marker such as length; it does not raise that successful-response observation into context's input-token-limit classifier. After context returns, the orchestration node applies the stated result-acceptance policy using existing status/category/reason fields. | Return-type compatibility is possible, but changed acceptance/failure behavior remains a Proposed policy for reader review. It is not merely a refactor. |

The observer should record stage, invocation/attempt identity, relevant raw completion marker, response identity and observed usage as private serializable evidence. The task wrapper retains the live holder; result builders use the observation corresponding to the actual successful string returned by context. No wrapper-controlled extra call, nested retry loop, report post-processor or mutation of the response is implied.

A tool-calls finish marker is normal for a **researcher requesting tools**; it is not sufficient proof that a **compression summary** is complete. Marker interpretation must be stage-specific and backed by the explicitly supported provider adapter. Missing/unknown metadata is an observed support gap, not proof of either a complete or a length-truncated answer. Recording it as incomplete/unknown or withholding a new strict-adapter support claim avoids silently introducing a new failure rule for every unknown provider. Any fail-closed acceptance policy for unknown markers needs to be stated and reviewed separately.

This conclusion does not approve final-report output truncation handling. The reference assigns final_report_generation/outcome to Alchemy. Recording compression completion metadata inside Centay's existing boundary does not authorize changing delivery's report outcome or adding a new shared enum/category.

## Existing 11/14 differences that still need review

The local 11/14 proposal already differs from the old online reference: actual-call permits rather than turns; required keyword-only trusted evidence and changed build_task_result input; additive TaskCost.usage_complete; findings-only notes/sidecar validation; running-versus-final state lifecycle; explicit malformed-intent semantics; the JoinedTurn/node-injected port; and cap/stall/native compatibility refinements. Those remain pending shared-reader decisions and are **not** introduced or approved by the 11/15 internal split/observer increment.

Therefore the narrow new work can proceed as a local Proposed SA refinement without rewriting original HackMD, changing peer source, or changing the stated ports. The existing review gates and older interface differences remain visible. No claim is made that the entire local proposal is already contract-identical to v0.5 or accepted by teammates.

## Evidence files

- `retrieval-manifest.json`: request URLs, results, retrieval times, hashes and authenticated-browser success, without credentials.
- `contract-comparison.json`: exact current/prior byte identity and hash.
- `sheet-index-semantic-comparison.json`: full XLSX member comparison and parsed semantic digest.
- `sheet-index-current.parsed.json`, `sheet-index-2026-11-14.parsed.json`: cells, formulas and hyperlink targets.
- `document-link-inventory.md`, `all-sheet-hackmd-links.json`: all Sheet document URLs.
- `progress-tracker-current.md`, `progress-tracker-linked-urls.json`: current maintained tracker and its visible external links.

No source, tests, global config, original online reference or remote Git state was changed during this audit.
