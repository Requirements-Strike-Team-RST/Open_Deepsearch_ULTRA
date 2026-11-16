# ADR-001: Single shared citation contract for research prompts

- **Status:** Proposed
- **Date:** 2026-11-13
- **Module:** citations
- **Owner:** NoPumpkinz
- **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-006 | C-001, C-002, C-003 (offline, prompt inspection); C-004 (live, `automated: false`) | REQ-006 is typed `invariant` and imposes a hard, shared citation-format constraint on two prompts. The significance is on the quality-attribute (invariant) and governance axes (ADR + Gate 1, versioned prompt artifact), not on structure or state. The chosen design must make the format single-sourced so the two prompts cannot drift, and must remain format-only (INV-004, the retrieved-source integrity property, stays Deferred). |

## 2. Context

`compress_research_system_prompt` and `final_report_generation_prompt` both specify a
citation format, but each does so inconsistently, and they disagree with each other. Mixed
citation styles follow, which reduces trust in a report (upstream #232; fix PR #301 closed
unmerged).

Baseline defects, with locations in `src/open_deep_research/prompts.py`:

- **Compression prompt states its sources section three ways.** Guideline 4 asks for a
  `"Sources"` section (L200); the Output Format block asks for
  `**List of All Relevant Sources (with citations in the report)**` (L209); the Citation Rules
  require a `### Sources` heading (L214). One prompt names the same section three ways.
- **Report prompt gives two competing citation schemes.** Instruction 3 requires references in
  `[Title](URL)` markdown-link form (L251); Instruction 5 asks for a `"Sources"` section with
  unspecified style (L253); the Citation Rules require numbered inline citations and a
  `### Sources` list in `[n] Source Title: URL` form (L299-305). Both a link form and a numbered
  form are mandated in the same prompt.
- **Per-researcher numbering collides across findings.** Each researcher's
  `compress_research` runs independently and the compression prompt tells it to assign
  `1,2,3,4...` (L213-218). The compressed text is stored verbatim as the tool message
  (`deep_researcher.py:310`), collected into `notes` (`deep_researcher.py:259`,
  `utils.py:599-601`) and joined into `findings` (`deep_researcher.py:623`) for the report
  prompt (`deep_researcher.py:642-647`). Numbers reused by different researchers therefore
  reach the report writer for different URLs, and the report prompt never instructs the model
  to renumber across the merged findings.

Forces and constraints:

- `prompts.py` is currently template-only (`structural-constraints.md` §5, "No logic in
  configuration and prompts"); any contract imported by `prompts.py` must itself hold text
  only, and the assembly in `prompts.py` must stay a pure string substitution so `prompts.py`
  remains a template assembler.
- The citation module must not perform deterministic validation of generated reports:
  that is out of scope for REQ-006 (`requirements.yaml` scope) and is the Deferred invariant
  INV-004 (`invariants.md`).
- The defect is fundamentally "two instructions in one file drifting apart"; the chosen design
  must remove the duplication, not just reconcile it once.
- Prompts are `format()`-filled templates; a prompt change is a versioned artifact and needs
  semantic evaluation (`Prompt.md` §9).

## 3. Decision

Adopt a single shared citation contract in `src/open_deep_research/citations/contract.py`,
holding **text constants only**, and have `prompts.py` assemble both prompts from those
constants at module load. The contract is the one source of truth; neither prompt restates the
rules inline. No node in `deep_researcher.py` is edited; the existing `.format(date=...)` call
sites stay unchanged.

**Canonical constants in `src/open_deep_research/citations/contract.py`** (module docstring
names `REQ-006, ADR-001`; strings only, no functions, no imports of model or graph code):

- `CITATION_RULES_BLOCK` — the complete citation rules, stated **exactly once**:

  ```
  <Citation Rules>
  - Assign each unique URL a single citation number as an inline marker in your text, e.g. [1].
  - End with a section headed ### Sources that lists every cited source, one per line, as [n] Title: URL.
  - Number sources sequentially without gaps (1,2,3,4...) in the final list.
  - Example format:
    [1] Source Title: URL
    [2] Source Title: URL
  </Citation Rules>
  ```

  This is the only place the format is written. The sentence "Each source should be a separate
  line item ... rendered as a list" is folded into "one per line" here. The block contains **no**
  `[Title](URL)` instruction and **no** "List of All Relevant Sources" label.
- `SOURCES_SECTION_POINTER` — a short pointer only, used in the Output Format block and in the
  report Instruction 5: "End with the Sources section specified in the Citation Rules below." It
  does **not** restate the heading, the entry format or the numbering; it only points at
  `CITATION_RULES_BLOCK`, so the format is not duplicated.
- `RENUMBER_ACROSS_FINDINGS_INSTRUCTION` — the report-only instruction, referring to the rules
  without restating them: "The findings may come from several independent researchers and each
  numbered its sources from 1. Renumber the citations of all findings into one sequence so that
  each URL has exactly one number in the report, following the Citation Rules below." It states
  no heading, entry format or numbering of its own.

**Assembly in `src/open_deep_research/prompts.py`** (string substitution only):

- At module load, `prompts.py` imports the three constants from
  `open_deep_research.citations.contract` and defines the two prompt strings with the
  placeholders `{citation_rules}`, `{sources_section_pointer}` and
  `{renumber_across_findings_instruction}` in place of the current inline text, then resolves
  them once with chained `str.replace()` — e.g.
  `compress_research_system_prompt = _REASONING_TEMPLATE.replace("{citation_rules}", CITATION_RULES_BLOCK).replace("{sources_section_pointer}", SOURCES_SECTION_POINTER)`
  and, for the report prompt, the same plus
  `.replace("{renumber_across_findings_instruction}", RENUMBER_ACROSS_FINDINGS_INSTRUCTION)`.
  Because the substitution happens at definition time, the module-level names
  `compress_research_system_prompt` and `final_report_generation_prompt` remain plain strings
  with only the existing runtime placeholders (`{date}`, `{messages}`, `{findings}`,
  `{research_brief}`), so the `.format(...)` calls in `deep_researcher.py:547` and
  `deep_researcher.py:642-647` stay untouched. Note: `compress_research` formats the compression
  prompt with `date` only (`deep_researcher.py:547`); `final_report_generation` formats the
  report prompt with **`research_brief`, `messages`, `findings` and `date`**
  (`deep_researcher.py:642-647`), not `date` alone.
- `compress_research_system_prompt`: replace the inline `<Citation Rules>` block (L212-219)
  with `{citation_rules}`, and replace the `**List of All Relevant Sources ...**` line in the
  Output Format block (L209) and the `"Sources"` wording (L200) with `{sources_section_pointer}`.
  After the change the prompt states the format exactly once (`CITATION_RULES_BLOCK`) and refers
  to it elsewhere only through the pointer.
- `final_report_generation_prompt`: delete Instruction 3's `[Title](URL)` requirement (L251)
  and rewrite Instruction 5 (L253) to use `{sources_section_pointer}`; replace the inline
  `<Citation Rules>` block (L298-307) with `{citation_rules}`; add
  `{renumber_across_findings_instruction}` after the rules so the report renumbers across all
  findings. The format-neutral emphasis sentence at L306 ("Citations are extremely important
  ...") stays in the report prompt, and L296 ("include source references where appropriate")
  stays because it specifies no format and conflicts with nothing.
- The three contract placeholders must be resolved before any `.format()` is applied: the
  contract text must contain no unescaped `{` or `}`, or those characters must be escaped, so
  the later `.format(...)` does not raise `KeyError`/`ValueError`.

**Recorded decisions (module review):**

- The canonical entry format is `[n] Title: URL`, one per line. This is fixed by the approved
  REQ-006 statement; adding Markdown bullet markers would require a change to
  `requirements.yaml` and is not done here.
- The format is stated once (in `CITATION_RULES_BLOCK`); every other site uses
  `SOURCES_SECTION_POINTER` or `RENUMBER_ACROSS_FINDINGS_INSTRUCTION`, neither of which
  restates it. This keeps the assembled prompts from stating the format two or three times,
  which would violate C-001 itself.
- L296 ("include source references where appropriate") and L306 (the emphasis sentence) stay
  because they specify no format.


**New interface edge (approved exception):** `prompts.py → citations/contract.py`, the
direction being `deep_researcher.py → prompts.py → citations/contract.py`. Recorded as an
exception in `structural-constraints.md` §5/§6 and as an interface in blueprint §5 because
`prompts.py` was previously template-only.

**Boundary:** the contract and prompts are **advisory** to the model. The deterministic
artifacts are the contract text itself and the offline inspection tests (C-001..C-003).
Renumbering correctness is **monitored, not enforced**, by the live check (C-004). No code
validates or rewrites generated reports (INV-004 Deferred).

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — inline prompt fixes in `prompts.py` only | Reconciles each prompt inline but leaves the format duplicated: the citation rules still live independently in both prompts, so the drift mode that produced this defect survives, and a future edit to one copy reintroduces a competing instruction. It treats the symptom, not the single-source cause. |
| A2 — shared constants defined directly in `prompts.py`, interpolated into both prompts | Single source of truth with no new module and no dependency exception, so it is the simplest possible drift-proof option. Rejected on governance grounds: it leaves the citation contract in the shared baseline file with no owning module (blueprint §4 assigns one architectural element to one module and one owner), gives future INV-004 work no home, and bypasses the §4 one-element-one-module ownership. |
| C — deterministic post-processor that reformats/renumbers generated reports | Out of REQ-006 scope: it is "deterministic checking of citations in generated reports" (`requirements.yaml` scope) and implements the property owned by Deferred INV-004 (`invariants.md`). A post-processor can reformat and renumber what is present, but cannot recover which URL backs an unsourced claim, so it cannot deliver the integrity guarantee it appears to promise; it also widens scope beyond a format-only change. |

The full comparison is in EVAL-001.

## 5. Components and Interfaces

| Component | Responsibility | Interface (signature or type) | Called by |
|---|---|---|---|
| `citations/contract.py` | Single source of truth for the citation format: text constants only | `CITATION_RULES_BLOCK: str`, `SOURCES_SECTION_POINTER: str`, `RENUMBER_ACROSS_FINDINGS_INSTRUCTION: str` | `prompts.py` (module import) |
| `prompts.py` (changed) | Import the contract constants and assemble both prompts by module-load `.replace()` of `{citation_rules}`, `{sources_section_pointer}`, `{renumber_across_findings_instruction}`; remains template-only and exposes plain strings | existing `compress_research_system_prompt`, `final_report_generation_prompt` (unchanged names and runtime placeholders) | `deep_researcher.py` (`compress_research`, `final_report_generation`) — unchanged call sites |

`deep_researcher.py` is not modified: the `.format(...)` call sites at L547 (compression,
`date`) and L642-647 (report, `research_brief`, `messages`, `findings`, `date`) keep
working because the contract placeholders are resolved at module load.

Shared contracts changed (`structural-constraints.md` §6): the new dependency edge
`prompts.py → citations/contract.py` is an approved exception to §5 (prompts were
template-only). It changes no `state.py` type and no interface another module reads in code, so
no other module owner must approve it; the citation module owner records the exception in
`structural-constraints.md` §5/§6 and blueprint §5.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none. No `state.py` field or type changes.
- **Runtime policies:** none. The contract adds no exception, retry or failure handling; it is
  format text only.
- **Invariants:** INV-006 (Proposed) details the REQ-006 citation-format consistency property; its enforcing component is `citations/contract.py` as the single source of truth and its verification is C-001..C-003. INV-004 (retrieved-source integrity) remains **Deferred** and is neither implemented nor changed by this ADR.
- **Deterministic boundary:** the format instruction is **advisory** to the model. The
  deterministic artifacts are (a) the contract text in `citations/contract.py` and (b) the
  offline inspection tests C-001..C-003, which assert on the assembled prompt/constant text.
  Renumbering correctness in generated reports is **monitored, not enforced**, by the live check
  C-004. No code decides on model output; the model still produces the report. This is consistent
  with REQ-006 being `safety_relevant: false`.

## 7. Verification

| Criterion | Verification |
|---|---|
| C-001 (compression prompt has exactly one sources-section instruction, `### Sources`, no competing label) | `test/offline/test_prompt_citation_contract.py::test_compression_prompt_has_single_sources_format` — `CITATION_RULES_BLOCK` occurs exactly once; banned strings `[Title](URL)` and `List of All Relevant Sources` occur zero times; example lines match `^\s*\[\d+\] .+: .+$` |
| C-002 (report prompt requires numbered citations, contains no `[Title](URL)`, asks for one renumbered sequence) | `test/offline/test_prompt_citation_contract.py::test_report_prompt_has_single_citation_format` — `CITATION_RULES_BLOCK` and `RENUMBER_ACROSS_FINDINGS_INSTRUCTION` each occur exactly once; banned strings occur zero times |
| C-003 (both prompts' sources-entry formats are identical) | `test/offline/test_prompt_citation_contract.py::test_prompts_share_citation_format` — the text between `<Citation Rules>` and `</Citation Rules>` is byte-identical across both prompts (this FAILS on the baseline, where the blocks differ) |
| INV-006 guard (ADR-001 §3 precondition) | `test/offline/test_prompt_citation_contract.py::test_assembled_prompts_format_without_leftover_placeholders` — both assembled prompts formatted with all real placeholders (`research_brief`, `messages`, `findings`, `date`) raise no exception and leave no `{citation_rules}` / `{sources_section_pointer}` / `{renumber_across_findings_instruction}` placeholder |
| C-001..C-003 negative | `test/offline/test_prompt_citation_contract.py::test_format_checks_detect_violations` — synthetic violating texts (one containing `[Title](URL)`; two differing Citation Rules blocks; a duplicated block) are each flagged by the check helpers, proving the assertions are not vacuous |
| C-004 (live reports use numbered citations with exactly one matching Sources entry per citation) | `test/live/test_report_citations_live.py::test_reports_use_numbered_citations` (live, `automated: false`); runs that triggered truncation retries are excluded and reported separately |

All offline assertions must FAIL on the baseline prompts for the registered reason (`Prompt.md`
§5). The cases are listed in the citations module section of `verification-constraints.md` §7.
Traceability: `trace-matrix.md` REQ-006 row.

## 8. Consequences

- **Positive:** the format has one source of truth, so the two prompts cannot drift apart
  (removes the finding-A recurrence mode); both prompts provably share one format (C-003
  becomes a direct comparison); the change is confined to `citations/contract.py` and
  `prompts.py` with no node edits; it stays format-only and offline-testable.
- **Negative:** `prompts.py` gains a dependency on the citations module, adding an interface
  surface and an approved exception to `structural-constraints.md` §5 that must be maintained;
  the contract text must contain no unescaped braces so the later `.format()` calls do not fail.
- **Neutral:** no state, data-flow or topology change; `deep_researcher.py` call sites are
  untouched; the report writer still produces the final numbering, so renumbering correctness
  relies on the model following the instruction and is only monitored (C-004), not guaranteed.
- **Other modules:** none affected; `delivery` (REQ-004) is untouched.
- **Risk — retry truncation (out of REQ-006 scope):** on a token-limit retry,
  `final_report_generation` truncates findings from the end
  (`findings[:findings_token_limit]` in `deep_researcher.py`), which can drop later
  researchers' `### Sources` blocks; renumbering then cannot map those citations back to URLs.
  A truncation retry is therefore incompatible with C-004 evidence. Precondition for C-004:
  the baseline queries must not trigger truncation retries, or truncation-affected runs are
  reported separately and excluded from the citation result. This is a REQ-004 concern, not a
  REQ-006 one; the context module (REQ-005) owner should be informed, since it owns the
  token-limit retry behaviour.

## 9. Implementation Steps

The governance records — the `prompts.py → citations/contract.py` exception in
`structural-constraints.md` §5/§6 and the interface row in blueprint §5 — and the prompt version
bump with semantic evaluation (`Prompt.md` §9) are **preconditions owned by this SA phase
(Plan/owner) and the integrator**, tracked in the citations module sections; they are not Build
steps. The offline tests (C-001..C-003) and the live check (C-004) are authored by the Test
Author against these interfaces and approved at Gate 2 before Build starts (`Prompt.md` §5-6).
Build implements only the code steps below.

1. Create `src/open_deep_research/citations/__init__.py` and
   `src/open_deep_research/citations/contract.py` with the three text constants only
   (`CITATION_RULES_BLOCK`, `SOURCES_SECTION_POINTER`, `RENUMBER_ACROSS_FINDINGS_INSTRUCTION`);
   docstring names `REQ-006, ADR-001`. The format is stated once, in `CITATION_RULES_BLOCK`
   (inline `[n]`; each unique URL one number; `### Sources`; one source per line as
   `[n] Title: URL`; sequential without gaps; the `[1]`/`[2]` example). No functions, no imports
   of model or graph code, and no unescaped `{`/`}` in the text.
2. Edit `src/open_deep_research/prompts.py`: import the three constants from
   `open_deep_research.citations.contract`; in `compress_research_system_prompt` replace the
   inline Citation Rules block with `{citation_rules}` and the `**List of All Relevant
   Sources**` label and `"Sources"` wording with `{sources_section_pointer}`; in
   `final_report_generation_prompt` remove the `[Title](URL)` instruction, point Instruction 5
   at `{sources_section_pointer}`, replace the inline Citation Rules block with
   `{citation_rules}`, and add `{renumber_across_findings_instruction}`. Keep L296 and L306.
3. In the same `src/open_deep_research/prompts.py`, resolve the three placeholders at module
   load with chained `.replace(...)` on the two template strings, so the module-level names are
   plain strings carrying only the existing runtime placeholders and the `.format(...)` call
   sites in `deep_researcher.py` (L547, L642-647) are unchanged.
