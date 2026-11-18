# Raw SA evidence — 61061965 XIE Shentai

This directory preserves only this task's OpenCode/Codex-assisted SA evidence. It contains no original user credential message or unrelated sessions.

- `*-prompt.md`: exact coordinator prompts sent to OpenCode; these are AI coordinator prompts, not invented student interventions.
- `*.raw.txt`: captured CLI stdout/stderr, preserved byte-for-byte (the .txt suffix keeps these required records visible under the repository's existing *.log ignore rule) from the local run. Rounds1/5 each include a genuine ANSI permission-auto-rejection diagnostic; it is not deleted or called a successful action.
- `*.events.jsonl`: explicit normalized derivative containing all parseable JSON events, in original order. Non-JSON diagnostics remain in raw.txt.
- `*.session.json`: OpenCode `session export --standalone --sanitize` snapshots. Round2 includes the earlier round1 history; the final delivery/context exports include their respective follow-ups because each pair continued the same session. Use the round-specific raw CLI streams to distinguish activity. Truncated streaming tool text is evidence of attempted generation, not a successful file edit.
- `*.meta.json`: launcher model/role, process-only provider restrictions, times and exit code; no environment credential values.

| Round | Role/provider/model | Actual outcome |
|---|---|---|
| preflight | plan / cityucs / CS5351/DeepSeek-V4-Flash | Exact READY response, no tools/edits |
| round1-analysis | same | Read-only analysis; final response reached 8192 output tokens and was retained, with design errors subsequently corrected |
| round2-authoring | same | EVAL-002 written; ADR write was truncated at 8192 output tokens before execution. Remaining documents were authored by Codex/assistants |
| round3-review | same | Read-only inspection and findings; no file writes |
| round4-final-review | same | No-tool static reading of the supplied corrected ADR before the added peer challenge; no runtime/gate claim |
| round5-delivery-peer / round7-delivery-followup | same | Independent simulated delivery review and reconciliation; original findings plus retractions retained, not real Alchemy review |
| round6-context-peer / round8-context-followup | same | Independent simulated context review and reconciliation; incorrect attempt/precision claims retracted, peer-owned integration decisions remain pending |

[peer-scenario-arithmetic.json](peer-scenario-arithmetic.json) records direct fraction arithmetic for example literals, not execution of project code or product tests.

See [coordinator-review-resolutions.md](coordinator-review-resolutions.md) for dispositions, [framework-source-audit.md](framework-source-audit.md) for framework reasoning, [course-sa-requirements-audit.md](course-sa-requirements-audit.md) and [peer-interface-audit.md](peer-interface-audit.md) for source audits, and [baseline-query-reference.md](baseline-query-reference.md) for recovered queries.

The external static audit output is [sa-static-validation.md](sa-static-validation.md) with detailed [JSON](sa-static-validation.json). Its audit-tool source is preserved as [validate-sa-docs.py.txt](validate-sa-docs.py.txt); this is document-checking evidence, not product implementation/test code. The original tool is outside the project clone and does not execute project source, pytest, network or model requests.

[Raw bundle manifest](raw-bundle-manifest.json) gives content hashes. It excludes itself to avoid a recursive hash. Static validation does not approve an architecture, confirm a fit criterion, or replace later human gates.
