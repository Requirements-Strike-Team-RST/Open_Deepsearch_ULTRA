# CS5351 — XIE Shentai (61061965): orchestration SA session

- **Member:** XIE Shentai / Centay, 61061965.
- **Date:** 2026-11-14–15, UTC+8.
- **Scope:** REQ-001 and REQ-003; REQ-002 C-005/C-007 contributor interfaces.
- **Stage:** software-architecture preparation only. Module review, Gate 1, tests,
  Gate 2, implementation and verification remain pending.
- **Agents:** Codex coordinator and its read-only audit assistants; OpenCode `plan`
  using `cityucs/CS5351/DeepSeek-V4-Flash`. No Claude/Anthropic invocation was made.
- **Repository baseline:** `827fd32f956a0601df3e1fd253d5cc98044fff88`, isolated local
  branch `docs/sa-orchestration`. The earlier checkout's uncommitted files were preserved.

## Human instructions and interventions actually received

| ID | Actual intervention | Rationale and effect |
|---|---|---|
| H-01 | The student asked Codex to continue the Work handoff, use installed OpenCode with the school DeepSeek API, treat Git as authoritative, preserve existing changes, and leave final Git/shared changes to the student. The student explicitly prohibited Claude API calls. | Restricted work to an isolated local SA draft. No push, PR, merge, coursework submission or online-document edit. |
| H-02 | In response to the D5 naming question, the student supplied `61061965 XIE Shentai`. | Used the actual student identity for this transcript; no identity was inferred from another member's transcript. |
| H-03 | The student said group leader Tekon and Alchemy have the stronger quality standards and should be prioritised. | Use Tekon's context ADR and Alchemy's current governance/templates as the primary quality references. Other module drafts are interface context, not accepted authority. |
| H-04 | The student delegated autonomous work while away and repeated the prohibition on Claude API requests. | Continued within the existing SA goal and retained the earlier specific arrangement for final Git/shared actions; this was not an SA/test gate approval. |
| H-05 | The student later said `continue`. | Continued the same task after the environment permission change; no new task or provider was substituted. |
| H-06 | The student encouraged using another group member's OpenCode perspective to challenge this module, with quota still available. | Started fresh delivery and context simulations on school DeepSeek, then sent corrections back for reconciliation; these remain AI reviews, not peer approvals. |

These are the human interventions observed in this session. The student has **not**
yet accepted the resulting architecture or approved a gate. Corrections below were
made by the AI coordinator and must not be presented as student review.

## Session evidence

Raw prompts, CLI logs and OpenCode session exports are not kept in this repository (removed on
2026-11-18, H-11). Only this task's sessions are summarised; credentials and unrelated browser/history
content are excluded, and the user message containing a Canvas credential is not copied. Rounds 1 and 5
each hit a genuine permission auto-rejection for a chained read-only shell command; OpenCode used
read/glob tools instead. A rejected action is not reported as executed.

| Round | OpenCode session | Purpose | Status |
|---|---|---|---|
| Preflight | `ses_e29b21b60ffevSCn2hyruEPoZf` | School DeepSeek connectivity, `plan`, no tools or edits | Completed; exact response returned |
| 1 | `ses_e29aff085ffenm8SKVtnfYQZpu` | Read current governance/source, compare candidates and propose interfaces | Analysis preserved; response reached its output-length limit, and several design statements were rejected by the AI coordinator |
| 2 | Same session, continued with an explicit correction prompt | Attempt proposed ADR and module authoring | Wrote EVAL-002; an 8,192-token output limit truncated the ADR tool call before execution. Codex/assistants completed the remaining draft, explicitly attributed as such. |
| 3 | `ses_e2995276fffevje020nmotHpAX` | Read-only review of the ADR/module sections and relevant baseline anchors | Completed; findings checked by the AI coordinator |
| 4 | `ses_e296a5c40ffeDABBSGmzOZ6PzU` | Bounded no-tool static reading of the supplied corrected ADR | Completed; no remaining contradiction found in that text, with no runtime/gate claim |
| 5 / 7 | `ses_e2959fdd1ffelh51FNj0iarclH` | Independent simulated delivery perspective, then follow-up reconciliation | Original findings preserved; ordered collector/output-field gaps corrected; coverage/task-count assumptions retracted; final entry diagnostic edge made explicit |
| 6 / 8 | `ses_e2959fdcdffe7srcqRCDyVXEOu` | Independent simulated context perspective, then follow-up reconciliation | Evidence/parse boundary clarified; incorrect attempt-count and threshold claims retracted; peer-owned integration decisions remain pending |

## Annotated AI supervision

1. **Evidence before generation.** The coordinator verified current `main` and PR #4's
   merged baseline, read the v0.5 field contract, and inspected existing code and
   course materials. It used an isolated clone to preserve the earlier checkout.
2. **Rejected first-draft budget semantics.** OpenCode proposed changing an actual
   tool-call budget into counted steps. The coordinator rejected this: REQ-001's
   approved statement requires actual tool calls. The correction prompt requires
   admission before execution and distinguishes the model-turn watchdog.
3. **Rejected unvalidated report prose.** OpenCode still used complete/partial
   task summaries as notes. The coordinator required notes to be constructed from
   validated findings and their source references, since validating a structured
   result does not validate every sentence in its free-text summary.
4. **Checked state semantics in code.** An initial read-only audit incorrectly
   inferred replacement from the name `override_reducer`. A separate source audit
   corrected that inference: ordinary lists append; only an explicit override
   envelope replaces. The correction was acknowledged before drafting.
5. **Corrected contradictory iteration rules.** The first proposal described both
   executing and not executing the same cap turn. The coordinator supplied a
   precise proposed processed-turn counter and requested N=1/N=2 boundary cases.
6. **Respected peer interfaces.** The coordinator retrieved read-only snapshots of
   context, citations, search and evaluation drafts. It retained context's string
   compression result and citations' unique `### Sources` format, proposing a
   separately parsed findings sidecar for reader review.
7. **Kept evidence honest.** Historical claims of 106 passing tests were excluded
   from this run's verification. The existing requirement validator actually ran
   and reported 10 valid requirements. Runtime tests were not authored or run.

## What this transcript does and does not establish

It supplies the SA portion of D5: actual prompts, tool use, candidate analysis,
drafting and AI corrections. It does not establish human plan approval, a completed
SA Review, approved tests, implementation or a test-driven architecture revision.
Those later stages must add their own genuine evidence after their gates.

## 2026-11-14 checkpoint outcome and checks

The local proposal contains EVAL-002, ADR-002, INV-003/006/007, POL-002–010,
46 planned cases, the module state/structural sections and REQ-001/003 trace rows.
OpenCode supplied the original analysis/EVAL and two reviews; Codex and its audit
assistants authored/corrected the final ADR and module tables. AIU-008/009/010 and the
AI preparation memo reflect this division.

The existing requirements validator reported PASS for 10 requirements. A final
external static document audit validated scope, document structure, references and capture integrity.
Product/contract/regression/live tests and all human gates remain NOT_RUN. The
source/tests/configuration/requirements/permission files are unchanged. No commit,
push, PR, merge, online-document write or Canvas submission was performed.

Shared-reader decisions and whole-system course gaps remain explicit in
`docs/architecture/orchestration-review-checklist.md`; they block acceptance and
implementation, not delivery of this proposed module review pack.

## 2026-11-15: student questions, experiments and Proposed SA revision

The following continues the same SA task and preserves the 11/14 checkpoint above.
It is not a retrospective claim that the original design covered these boundaries.

| ID | Actual student intervention | Effect / attribution |
|---|---|---|
| H-07 | In the supplied sidechat, the student questioned why evidence owns admission/cost, whether original code already has budgets/concurrency, what contracts validates, and how tool/API/token units and state deltas differ. | Triggered clarification against actual baseline and CC v0.5. Earlier AI descriptions needed correction; the concepts already in CC and baseline are not attributed as new Codex inventions. |
| H-08 | The student asked whether the SA prevents token-truncated output from appearing complete, requested a main-chat follow-up, and then suggested actually checking truncation. | Codex located the metadata boundary and designed/executed the gateway, locked-adapter and isolated-source experiments. The student asked the question; the technical diagnosis and probe authorship belong to Codex. |
| H-09 | The student suggested budget.py/evidence.py separation, asked about submitted peer work/difficulty/iteration, and authorised reading the old HackMD/index and continuing SA if no original-HackMD change or peer-development disruption is required. | Read current references and remote metadata; preserve shared DTO/helper/context signatures, draft internal separation and completion acceptance, retain final Git/shared operations for the student. This authorises preparation, not approval of the proposed policy or any gate. |

The dated evidence for this follow-up covered the supplied visible-message sidechat,
selected current student requests, reference comparisons, scripts, raw synthetic
gateway responses and experiment results. The sidechat is a visible-message extraction, not a native complete raw
tool-event export. No hidden reasoning, Canvas credential or unrelated chat is
included. This annotated record does not convert AI suggestions into human acts.

Codex made three direct HTTP requests to the authorised school
CS5351/DeepSeek-V4-Flash gateway: stop, length and an unexecuted synthetic tool intent
ending tool_calls. Reported usage was 398 tokens (332 input, 66 output). These were
not OpenCode sessions or full research runs. Locked-adapter replay used mocked
HTTP and blocked real sockets; eight baseline-function scenarios executed original
AST-extracted function bodies with fake models/config/child boundaries. No
orchestration implementation, product acceptance/regression/full-graph/live
acceptance test or Claude request was run.

The follow-up Proposed SA has 53 planned cases, POL-002–012 and R-01–R-12.
It keeps one receipt, separates internal budget/evidence duties and checks the
matching response-completion observation before control dispatch or parsing.
Unknown-as-runtime fail-closed support is an explicit proposed decision needing
reader review; it is never mislabeled proven length exhaustion. The Codex audit
also caught and corrected stale registration/parse/exit wording during revision.
Those corrections are AI assistance, not the student's approval.

D1 entries AIU-011/012 distinguish this investigation and SA authoring from the
11/14 OpenCode work. No new human review memo or approval was fabricated. The
11/14 release package remains intact; the 11/15 version has dated checks and a
separate manifest/package. Human review, Gate 1, product tests, Gate 2, Build and
independent Verify remain pending.

## First-version publication authorisation

**H-10:** The student explicitly authorised submitting a first version after checks,
with personal design/code reading and further iteration later on the 15th. This
supersedes H-01's earlier reservation of final Git actions for this Draft release;
it does not approve the proposed architecture or an SA/test gate. The student also
asked how their human judgement differs from AI self-review. That question is
preserved as reflection material, not an AI-authored student reflection.

Codex checked the full release manifest, current remote heads, branch-name
availability and sensitive-token patterns. A read-only AI presubmit audit found no
blocking design/evidence issue for a Draft release. The full staged whitespace
check then found two original Markdown captures with inherited trailing spaces.
A deterministic gzip storage mapping
recorded their original hashes and verified decompressed-byte equality. Original OpenCode
captures are unchanged. This storage correction is not a rewrite of source evidence.

AIU-013 records this preparation. Publication uses the module branch and a Draft
PR for review only; later revisions use new commits on that branch. All human
architecture/test approvals remain pending, and no product implementation or
Claude request is part of publication.

## Raw evidence removal after integration (2026-11-18)

**H-11:** After PR #22 integrated the module architectures, the student decided to remove the
`transcripts/raw/` folder, as AlchemyHAN's PR #16 review asked. The student asked Claude Code
to prepare the change; the student pushes it and opens the PR.

Claude Code compared the current `main` with PR #16 and its reviews, removed the folder and
removed or reworded the remaining references in `docs/ai-use-log.yaml`,
`architecture-blueprint.md` and this transcript. The earlier "never call Claude" restriction
(H-01, H-04) applied to the 11/14–15 sessions; this session uses Claude Code by the
student's choice. AIU-025 records it.

## Owner check of the integrated design (2026-11-18–19)

**H-12:** The integrator asked each module owner to check the PR #22 integration decisions that touch their
module. The student asked for an agent review using the local OpenCode. An OpenCode `architect` session on the
school CS5351/DeepSeek-V4-Flash model (read-only, non-interactive, so its one shell request was auto-rejected)
reviewed ADR-001 against REQ-001/003 and the integrated documents and reported 13 findings, two marked blocking.

Claude Code then verified each finding against the files and, where a finding was about library behaviour, with a
small experiment on the locked versions (langgraph 1.2.9, langchain-core 1.4.8). Both blocking findings were wrong:
a Pydantic `ResearcherOutputState` does carry a declared `task_result` field, and an all-failed run not reaching
`covered` is intended. F3–F6 are already covered by existing cases. Separately, Claude Code noted that ADR-001 §3.4
counts a stall when the number of answered questions does not grow, while the REQ-003 statement says "coverage
unchanged". The ADR already states this reading and it matches C-003 ("add no coverage"), so the student decided
not to change `requirements.yaml` and only to mention it in the Discussion reply, which the student posts. AIU-026
records this work.
