# 2026-11-15 SA follow-up: references, experiments and dispositions

This dated record supplements the original 11/14 OpenCode sessions. Codex performed
this investigation and wrote the follow-up Proposed SA. The three gateway probes
were direct HTTP requests to the authorised school DeepSeek model, not OpenCode
sessions. No Claude request, online document write, source implementation, product
test authoring, remote Git write or human approval occurred.

## Reference check

- [Current index/contract compatibility audit](followup-20261115/reference-audit/reference-and-interface-audit.md)
- [All 16 Sheet URLs](followup-20261115/reference-audit/document-link-inventory.md)
- [Current selected student requests](followup-20261115/current-user-instructions.txt)
- [Supplied sidechat visible-message handoff](followup-20261115/sidechat-visible-message-handoff.md.gz)

The Google index's cell values/formulas/hyperlinks and every XLSX member match the
11/14 export. The authorised HackMD contract download is byte-identical to the
11/14 v0.5 copy (SHA-256 d2840c0e4eb13e99fb00e85d19985dc6fc690314e0f83f20e5b01c999fff49a5).
No online edit was necessary. The node-owned observing Runnable fits the existing
context model parameter and preserves its returned AIMessage and
CompressionOutcome.summary:str. DTO/helper signatures do not change in this
revision. Older 11/14 interface differences remain pending; reference equality is
not agreement with or approval of the local SA.

## Experiments actually executed

| Layer | Result | Limitation |
|---|---|---|
| School gateway, long output cap 32 | finish_reason=length; 32 output tokens | Synthetic request, not a full research run |
| School gateway, exactly OK | finish_reason=stop; 1 output token | Control response only |
| School gateway, forced synthetic metadata_probe intent | finish_reason=tool_calls; args value=OK; 33 output tokens | Intent only; no tool was executed |
| Locked ChatOpenAI adapter replay, three captured responses | Markers, content and reported usage survive; tool intent parses | HTTP mocked; real sockets blocked; no live LangChain-to-school call |
| Eight extracted baseline-function scenarios | Compression loses finish metadata; report retains message but ignores marker; supervisor ignores marker for no-tool exit and fake-child dispatch | Real original function bodies with fake boundaries, not the full graph or Proposed fix |

The three server-reported requests total **398 tokens: 332 input, 66 output**.
The first two, 73 tokens, were investigated before the latest SA-edit permission;
the third supplied the normal tool-call fixture during refinement. This is returned
usage, not an exact financial bill. No tools/search/MCP were executed by the probes.

- [Gateway text summaries](followup-20261115/truncation-gateway-results.json)
- [Gateway tool summary](followup-20261115/truncation-gateway-tool-results.json)
- [Raw length response](followup-20261115/gateway-forced-length.response.json)
- [Raw stop response](followup-20261115/gateway-short-control.response.json)
- [Raw tool intent](followup-20261115/gateway-tool-control.response.json)
- [Adapter replay](followup-20261115/truncation-langchain-results.json)
- [Baseline scenarios and source SHA](followup-20261115/truncation-offline-results.json)

Commands, run outside the repository:

```text
python3 probe-output-truncation.py --live
python3 probe-output-truncation.py --live-tools
uv run --no-project --python /opt/homebrew/bin/python3.12 --with langchain-openai==1.1.14 --with langchain-core==1.4.8 --with openai==2.32.0 --with httpx==0.28.1 python probe-langchain-metadata.py
```

[Probe script](followup-20261115/probe-output-truncation.py) and
[adapter script](followup-20261115/probe-langchain-metadata.py) are archived evidence,
not product test files. The first adapter exploration resolved a newer OpenAI SDK;
the final replay was rerun against the lock's 2.32.0. Do not call the earlier
exploration a fully locked-stack test. The SDK/interface replay reports three
fixtures; the eight baseline scenarios are a separate experiment.

## Proposed dispositions and remaining review

1. Split internal admission policy into budget.py and factual observation into
   evidence.py, with one holder/count and unchanged shared fields/arguments.
2. Observe logical attempts inside the existing retry boundary, but accept returned
   completion after that boundary. For context, wrapper observes and returns or
   re-raises unchanged; it does not manufacture an input-limit exception.
3. Compression normal permits one parse; known length maps failed/token_limit;
   unknown/missing/stale observation maps failed/runtime. Both rejection paths do
   zero parses and add no retry. Malformed normal text remains invalid_result.
4. Unknown metadata was discussed as either diagnostics-only or fail-closed. The
   local ADR proposes the latter to avoid silently accepting unobserved responses.
   It is not evidence of length, and it narrows enabled adapter support; R-11
   explicitly requires reader review. No peer interface or provider default changes.
5. Control-response rejection uses existing supervisor/child failure boundaries;
   no new task/question, exit enum or graph path. Transport retry exhaustion and
   returned-response rejection remain distinct observations.
6. Final-report output truncation remains delivery's question. Input-token cap and
   proactive threshold remain whole-system/context work, not an invented task-wide
   cumulative budget in Centay's module.

ORC-047–053 and POL-011/012 are Proposed additions: **53 planned cases total**.
Product acceptance, regression, full graph and live acceptance suites remain
NOT_RUN; actual student review, Gate 1 and Gate 2 remain pending. Baseline source
experiments cannot establish that the future enabled implementation passes.

The original 11/14 package/manifests and original raw OpenCode captures are retained.
The 11/15 package has a new manifest and dated static reports. These records must
not be rewritten as if the completion boundary was already in the 11/14 design.

## Publication storage of original Markdown

The two original Markdown source copies with inherited trailing whitespace are
stored as deterministic gzip files, preserving every decompressed byte. This
keeps raw content intact while allowing the full staged Git whitespace check.
See [storage mapping](followup-20261115/raw-source-storage.json); the original
OpenCode captures remain plain unchanged files. These are storage changes, not
rewritten source evidence.
