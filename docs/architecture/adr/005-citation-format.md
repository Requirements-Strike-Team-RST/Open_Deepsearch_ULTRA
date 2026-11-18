# ADR-005: One shared citation format for the research prompts

- **Status:** Proposed
- **Date:** 2026-11-17
- **Module:** citations
- **Owner:** NoPumpkinz
- **Evaluation:** EVAL-005 (`docs/architecture/evaluation-table.md`)
- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-006 | C-001, C-002, C-003 | Both prompts must state one identical format. The format should be written once, so that the two prompts cannot drift apart again. |
| REQ-006 | C-004 (live, `automated: false`) | Renumbering across findings is left to the report model; it can be monitored, not enforced. |

## 2. Context

Baseline (`prompts.py`, line numbers at commit `daf6947`):

- `compress_research_system_prompt` names its sources section three ways: `"Sources"` (L200), `**List of All Relevant Sources (with citations in the report)**` (L209) and `### Sources` (L214).
- `final_report_generation_prompt` asks for `[Title](URL)` links (L251) and also for numbered citations with a `[n] Source Title: URL` list (L299-305).
- Each researcher numbers its sources from 1, and the report prompt never asks the model to renumber across findings, so the same number can mean different URLs.

`prompts.py` holds templates only (`structural-constraints.md` §5). Deterministic checking of generated reports is out of scope (INV-004, Deferred).

## 3. Decision

Use EVAL-005 option B. `src/open_deep_research/citations/contract.py` holds three text constants and nothing else:

- `CITATION_RULES_BLOCK` — the complete rules, written once:

  ```text
  <Citation Rules>
  - Assign each unique URL a single citation number as an inline marker in your text, e.g. [1].
  - End with a section headed ### Sources that lists every cited source, one per line, as [n] Title: URL.
  - Number sources sequentially without gaps (1,2,3,4...) in the final list.
  - Example format:
    [1] Source Title: URL
    [2] Source Title: URL
  </Citation Rules>
  ```

- `SOURCES_SECTION_POINTER` — "End with the Sources section specified in the Citation Rules below." It does not repeat the format.
- `RENUMBER_ACROSS_FINDINGS_INSTRUCTION` — report prompt only: the findings come from several researchers that each numbered from 1; renumber all citations into one sequence so that each URL has one number.

`prompts.py` imports the constants and puts them into both templates once, at module load, with `str.replace` on the placeholders `{citation_rules}`, `{sources_section_pointer}` and `{renumber_across_findings_instruction}`. The module-level prompt names stay plain strings with only their existing runtime placeholders, so the `.format(...)` calls in `deep_researcher.py` (L547, L642-647) do not change. The constants contain no `{` or `}`.

Edits to the prompts: replace both inline `<Citation Rules>` blocks; replace guideline 4 of the compression prompt (L200, which asks for a "Sources" section) with the pointer and delete the "List of All Relevant Sources" label (L209), so each prompt has one pointer and one rules block (C-001); delete the `[Title](URL)` instruction; add the renumbering instruction to the report prompt. L296 states no format and stays. The emphasis sentence at L306 sits inside the report prompt's rules block; it moves to just after `{citation_rules}`, outside the tags, so that both prompts have identical text between the tags (C-003). L302 ("each source a separate line item") is covered by "one per line" in the block.

The flag-on findings block of ADR-001 §3.3 sits before `### Sources` and refers to the source numbers of this format; it does not state a second format.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — fix both prompts inline | The rules stay written twice, so they can drift apart again. |
| A2 — shared constants inside `prompts.py` | Also drift-proof and simpler, but leaves the citation contract without an owning module (blueprint §4) and without a home for INV-004 work. |
| C — rewrite citations in generated reports with code | Out of REQ-006 scope (INV-004 Deferred), and code cannot recover which URL backs an unsourced claim. |

The full comparison is in EVAL-005.

## 5. Components and Interfaces

| Component | Responsibility | Interface | Called by |
|---|---|---|---|
| `citations/contract.py` | The citation format, as text | `CITATION_RULES_BLOCK: str`, `SOURCES_SECTION_POINTER: str`, `RENUMBER_ACROSS_FINDINGS_INSTRUCTION: str` | `prompts.py` |
| `prompts.py` | Assemble both prompts from the constants | existing names `compress_research_system_prompt`, `final_report_generation_prompt` | `deep_researcher.py` (unchanged call sites) |

Dependency exception: `prompts.py → citations/contract.py`, recorded in blueprint §6. No `state.py` type or code interface of another module changes.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** none.
- **Runtime policies:** none.
- **Invariants:** INV-008 (INV-004 stays Deferred).
- **Deterministic boundary:** none at runtime; the prompts are advice to the model. The deterministic parts are the constant text and the offline tests.

## 7. Verification

Cases in `verification-constraints.md` §7 (citations). C-001 to C-003 inspect the assembled prompt strings and fail on the baseline. C-004 is a live check; runs in which the report findings were truncated are reported separately, because truncation can cut a researcher's `### Sources` list (REQ-004, ADR-003).

## 8. Consequences

- **Positive:** one source of truth; C-003 becomes a direct comparison; no node changes.
- **Negative:** `prompts.py` depends on an extension module (recorded exception); the constants must stay free of braces.
- **Neutral:** whether the model renumbers correctly is only monitored (C-004). The prompt change needs a semantic evaluation (`Prompt.md` §9); until the `prompts/` version scheme is decided (blueprint §11, #3), the PR names the changed prompts and the evaluation evidence.

## 9. Implementation Steps

1. Add `citations/__init__.py` and `citations/contract.py` with the three constants; add `open_deep_research.citations` to `[tool.setuptools] packages`. Docstring names `REQ-006, ADR-005, INV-008`.
2. `prompts.py`: import the constants, replace the inline text with the placeholders of §3, and resolve them once at module load with `str.replace`.
3. Run the checks in `verification-constraints.md` §4 and record them in `docs/build-reports/REQ-006.md`.
