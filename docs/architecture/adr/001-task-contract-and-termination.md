# ADR-001: Typed research tasks and coverage-based termination

- **Status:** Accepted
- **Date:** 2026-11-17
- **Module:** orchestration
- **Owner:** centay
- **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)
- **SA Review:** passed in the SA integration PR [#22](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/pull/22) (approved by BroZhai and DopplerXD, merged 2026-11-18)

## 1. Architecturally Significant Requirements

| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
|---|---|---|
| REQ-001 | C-001 | The supervisor must hand each researcher a task specification built by code, not free text. |
| REQ-001 | C-002, C-003, M-001 | Task status must be derived by code from findings whose URLs a tool in that task actually returned. The model's own claims are input, not the decision. |
| REQ-001 | C-004 | A result that does not match the contract must become a typed failure. |
| REQ-003 | C-001, C-002, M-002 | `ResearchComplete` and a turn without tool calls are requests. Only a deterministic coverage check ends the loop. |
| REQ-003 | C-003, C-004, C-005, M-001 | Stall, iteration cap and supervisor failure must go through one exit decision that records exactly one reason. |
| REQ-003 | C-006 | Live evidence only; it does not shape the design. |

## 2. Context

Baseline (`src/open_deep_research/`, line numbers at commit `daf6947`):

- `state.py` L15-19: `ConductResearch` has one free-text field, `research_topic`. L92-96: the researcher returns free text and raw notes, with no task id, status or sources.
- `deep_researcher.py` L246-262: `supervisor_tools` ends the loop on the iteration cap, a turn without tool calls, or a `ResearchComplete` call. Nothing checks whether the brief was answered and no exit reason is stored. L214: an error in the supervisor's own model call aborts the whole run.
- `deep_researcher.py` L492: the researcher budget counts model turns (`tool_call_iterations`), not tool calls.
- `utils.py` L599-601: `get_notes_from_tool_calls` copies every tool message into `notes`, including failure text.
- `utils.py` L131-132: Tavily results contain one `URL: <url>` line per source, so retrieved URLs can be read from tool messages without changing the search tool.

Constraints: thin nodes and fixed topology (`structural-constraints.md` §2), shared types in `state.py` so that extension modules do not import each other (§5, §6), deterministic code for safety-relevant decisions (§7), offline tests with fake models (`verification-constraints.md` §3).

## 3. Decision

Use EVAL-001 option B: the shared types live in `state.py`; the logic lives in `src/open_deep_research/orchestration/` and is called from the existing nodes. Everything below is active only when `Configuration.task_contract_enabled` is `True` (default `False`). This flag also switches on ADR-002 and ADR-003, because REQ-002 to REQ-004 depend on the task contract.

### 3.1 Delegation

- When the flag is on, the supervisor binds `ConductResearchTask` instead of `ConductResearch`. It has `research_topic: str`, `must_answer: list[str] = []` and `scope: str = ""`, and its schema title is `ConductResearch`, so the model still sees a tool named `ConductResearch`. The baseline class is unchanged.
- `build_task_specs` turns each call into a `TaskSpec`. Questions are de-duplicated after collapsing whitespace and ignoring case; the first spelling is kept. An empty list becomes `[research_topic]`. The budget is `max_tool_calls = max_react_tool_calls`.
- A call with a blank topic, a non-string question or more than five distinct questions is rejected: it gets an error `ToolMessage` and a `TaskResult` with status `failed`, category `invalid_result` and no required questions. So the delegation is not dropped (REQ-002), but it adds no question to coverage and is never run.
- Task ids are `T1`, `T2`, ... in delegation order within one run.
- The researcher's first message is `render_task_brief(spec)`: topic, scope, the required questions and the tool-call budget.

### 3.2 Tool-call budget and retrieved URLs

- `researcher_tools` runs at most `max_tool_calls - tool_calls_spent` calls of a batch, in the order the model gave them. The remaining calls get a `ToolMessage` saying the budget is used up and are not run. Every executed call counts, including a call that fails and `think_tool`. When the budget is used up, the researcher goes to `compress_research`. The baseline turn limit (`tool_call_iterations`) stays as a second limit.
- After the calls run, `extract_urls(tool_messages)` adds every `http(s)` URL found in the text of tool messages to `ResearcherState.retrieved_urls`. The text is the message content when it is a string, otherwise the `text` parts of its content blocks joined (MCP tools return blocks). Skipped: `think_tool` messages, budget messages, and failed calls (content starting with `Error executing tool:`, the prefix of `execute_tool_safely`), so URLs in error text never count. URLs are compared as exact strings.
- Native OpenAI and Anthropic search run inside the model call and return no tool message, so their URLs cannot be checked. With the flag on, `search_api` must be `tavily` or `none` with MCP tools; ADR-006 rejects other values before the run starts.

### 3.3 Task result

When the flag is on, `compress_research` adds `task_findings_instruction` (in `prompts.py`) to its final instruction. It asks the model to put one findings block before the `### Sources` section:

```text
<task_findings>
{"findings": [{"claim": "...", "answers": ["<one required question, copied exactly>"], "sources": [1, 2]}]}
</task_findings>
### Sources
[1] Title: https://example.org/a
[2] Title: https://example.org/b
```

The JSON braces of this example are written as `{{` and `}}` in the template, because the template is filled with `.format(must_answer=...)`.

`build_task_result(spec, text, retrieved_urls, tool_calls)` then decides, without a model:

1. The text must contain exactly one findings block with valid JSON of the shape above, every `answers` entry must match a required question of the spec (same normalisation as §3.1), and every source number must appear in the `### Sources` list as `[n] Title: URL`. Otherwise the result is `failed` with category `invalid_result`.
2. A finding counts only if it cites at least one source and every one of its URLs is in `retrieved_urls`. Other findings are dropped.
3. Status: `complete` when every required question has a counted finding, `partial` (category `unanswered`) when some do, `failed` (category `unanswered`) when none do. A non-complete result lists the unanswered questions in `reason`.
4. `summary` is the compression text with the findings block removed. It is empty when the status is `failed`.

The node returns this `TaskResult` in the new output field `task_result`. When context recovery raises `CompressionFailed` (ADR-004), the node returns `TaskResult.failed(spec, category, reason, tool_calls=tool_calls_spent)` instead. With `context_trimming` off, a failed compression returns the baseline placeholder, which has no findings block and therefore becomes `invalid_result`.

### 3.4 Coverage and loop exit

Coverage counts distinct required questions across all task results of the run, including failed and `not_run` ones: `coverage = answered / total`, and `0` when there is no question. A question is answered when any task has a counted finding for it.

`supervisor_tools` handles one supervisor turn in this order:

1. Handle `think_tool` calls as today and reject invalid delegations (§3.1).
2. `cap_reached = research_iterations > max_researcher_iterations` (the baseline cap test) is evaluated on every turn, with or without delegations. When it is true, every accepted spec of this turn becomes `TaskResult.failed(spec, "not_run", ...)` and is not run (REQ-002 C-005). Otherwise ADR-002's `run_delegations` runs the specs.
3. Each `ConductResearch` call gets one `ToolMessage` built by `render_result_message(result)`: task id, status, unanswered questions and the summary.
4. `select_exit` decides with the results before and after the turn, in this order of precedence:
   1. `covered`: there is at least one question and coverage ≥ `coverage_threshold`;
   2. `budget_exhausted`: `cap_reached` is true;
   3. `stalled`: `stalled_turns` reaches 2. A turn that does more than call `think_tool` (delegation, `ResearchComplete`, or no tool call) adds 1 when the number of answered questions did not grow and resets the counter to 0 when it grew. (New questions that stay unanswered lower the ratio but are not progress.) A turn with only `think_tool` calls leaves the counter as it is;
   4. `failed`: only when the supervisor's model call failed (step 5);
   5. otherwise continue.
5. In `supervisor`, if the model call still fails after its configured retries, the node calls `select_exit` with `supervisor_error=True`, `before` and `after` both set to the current `task_results`, `turn_is_eligible=False`, the current `stalled_turns`, and `cap_reached` from the same test as step 2. It ends the loop with the reason returned, so a covered run is still reported as `covered`. It writes the same fields as step 7.
6. A `ResearchComplete` call or a turn without tool calls does not end the loop while coverage is below the threshold. The supervisor gets the list of unanswered questions: in the `ToolMessage` of the `ResearchComplete` call, or in a `HumanMessage` when there was no tool call.
7. On exit the node writes `exit_reason`, `exit_detail` (a short reason for any exit other than `covered`) and `notes` as an override with `render_notes(task_results)`: one entry per `complete` or `partial` task, in task order, holding only its counted findings in this form:

   ```text
   Task T1: <research topic>
   - <claim> [1][2]
   ### Sources
   [1] <title>: <url>
   ```

   Source numbers start at 1 in each entry, in order of first use; the report prompt renumbers them across tasks (ADR-005). REQ-002 C-007 requires that `notes` contain only validated findings, so neither the free-text summary nor failure text enters `notes`. The summary still reaches the supervisor in the `ToolMessage` of step 3.

`coverage_threshold` is a new `Configuration` field, default `0.8`, valid range `0 < x ≤ 1`.

## 4. Rejected Options

| Option | Reason for rejection |
|---|---|
| A — prompt-only rules | Status, coverage and exit stay model decisions, so REQ-001 C-002/C-003 and REQ-003 C-001–C-005 cannot be enforced. |
| C — one module replaces the whole `supervisor_tools` | Takes over the fan-out and join that REQ-002 assigns to delivery, and puts three owners' work in one module. |
| Putting task summaries into `notes` (considered at integration) | Keeps more text for the report writer, but the summaries can contain claims whose findings were dropped, which breaks REQ-002 C-007 ("notes contain only validated findings"). Revisit only through a requirement change (RISK-013). |
| Tracking `finish_reason`, private config keys and crash-safe receipts (an earlier draft) | Not required by REQ-001 or REQ-003. A truncated findings block already fails as `invalid_result`. |

The full comparison is in EVAL-001.

## 5. Components and Interfaces

| Component | Responsibility | Interface | Called by |
|---|---|---|---|
| `state.py` | Shared types and two pure helpers | `ConductResearchTask`, `TaskSpec`, `Source`, `Finding`, `TaskResult`, `TaskResult.failed(spec, category, reason, tool_calls=0)`, `normalize_question(text) -> str`, `unanswered_questions(results) -> list[str]` | all modules |
| `orchestration/contracts.py` | Build specs and results | `build_task_specs(calls, first_index, config) -> tuple[list[TaskSpec], list[ToolMessage]]`; `render_task_brief(spec) -> str`; `extract_urls(tool_messages) -> list[str]`; `build_task_result(spec, text, retrieved_urls, tool_calls) -> TaskResult`; `render_result_message(result) -> str`; `render_notes(results) -> list[str]` | `supervisor_tools`, `researcher_tools`, `compress_research` |
| `orchestration/termination.py` | Coverage and exit decision | `coverage(results) -> float`; `select_exit(before, after, *, stalled_turns, turn_is_eligible, cap_reached, supervisor_error, threshold) -> tuple[ExitReason \| None, int]` | `supervisor`, `supervisor_tools` |

Shared types in `state.py`, all Pydantic `BaseModel`s like the existing structured outputs, so they validate on construction and serialise with the graph state:

| Type | Fields |
|---|---|
| `TaskSpec` | `task_id: str`, `research_topic: str`, `scope: str`, `must_answer: list[str]` (1–5), `max_tool_calls: int` |
| `Source` | `title: str`, `url: str` |
| `Finding` | `claim: str`, `answers: list[str]`, `sources: list[Source]` (at least one) |
| `TaskResult` | `task_id: str`, `status: "complete" \| "partial" \| "failed"`, `must_answer: list[str]`, `findings: list[Finding]` (counted findings only), `summary: str`, `tool_calls: int`, `failure_category: "unanswered" \| "invalid_result" \| "runtime" \| "token_limit" \| "not_run" \| None`, `reason: str` |

Rules: `complete` has no category and an empty reason; `partial` and `failed` have a category and a reason. A `failed` result has no findings and an empty summary.

Shared contracts changed (`structural-constraints.md` §6): the types above and the state fields in §6. Readers who must approve changes: delivery (AlchemyHAN), context (BroZhai). The findings-block instruction must keep the citation format of ADR-005; citations (NoPumpkinz) reviews it.

## 6. State, Failure Handling and Deterministic Boundary

- **State:** `ResearcherState.task_spec`, `retrieved_urls`, `tool_calls_spent`; `ResearcherOutputState.task_result`; `SupervisorState` and `AgentState` `task_results`, `exit_reason`, `exit_detail`; `SupervisorState.stalled_turns`. Details and writers in `memory-design.md` §5.
- **Runtime policies:** POL-004, POL-006 to POL-011.
- **Invariants:** INV-003, INV-006; INV-007 for `not_run` results at the cap; INV-002 for `notes`.
- **Deterministic boundary:** task status, coverage and the exit reason are computed by code from the model's findings block and the tool messages. The model proposes claims; it never decides status or exit.

## 7. Verification

Each criterion of REQ-001 and REQ-003 has a case in `verification-constraints.md` §7 (orchestration), using fake models and fake researchers. REQ-003 C-006 is a live check and is `NOT_RUN`; it needs a configuration with a client-side search source (Tavily or MCP), because the team's earlier baseline ran with search disabled.

## 8. Consequences

- **Positive:** a caller and the other modules can read typed results; a model's "done" claim no longer ends research; every exit has one recorded reason; all decisions run offline in tests.
- **Negative:** the strict findings block can turn useful output into `invalid_result` (RISK-003). The report writer gets claims and sources instead of the full compressed text, so reports may be shorter (RISK-013). The tool-call budget is tighter than the baseline turn budget (RISK-005). Native search cannot be used with the flag on (RISK-010). A URL in the findings block proves retrieval, not that the source supports the claim (RISK-004).
- **Neutral:** with the flag off, the tools, prompts and state behave as in the baseline; the new fields stay empty.

## 9. Implementation Steps

1. `state.py`: add the types and helpers of §5 and the fields of §6. Keep `ConductResearch` and the existing reducers.
2. `configuration.py`: add `task_contract_enabled: bool = False` and `coverage_threshold: float = 0.8` with `x_oap_ui_config` metadata; reject a threshold outside `(0, 1]`.
3. Add `orchestration/__init__.py`, `contracts.py` and `termination.py`; add `open_deep_research.orchestration` to `[tool.setuptools] packages` (human confirms the `pyproject.toml` change).
4. `prompts.py`: add `task_findings_instruction` (placeholder `{must_answer}`) and one line in `lead_researcher_prompt`'s flag-on variant that explains `must_answer` and `scope`. Do not restate the citation format; refer to the Citation Rules.
5. `write_research_brief`: when the flag is on, reset `task_results` (override `[]`), `exit_reason` and `exit_detail`.
6. `supervisor`: bind `ConductResearchTask` when the flag is on; catch the error left after the configured retries and end through `select_exit` (§3.4 step 5). Its return type becomes `Command[Literal["supervisor_tools", "__end__"]]`, and on that path it writes `exit_reason`, `exit_detail` and `notes`.
7. `supervisor_tools`: follow §3.4 steps 1–7. The dispatch in step 2 calls ADR-002's `run_delegations`; agree the code split with the delivery owner before editing.
8. `researcher_tools`: apply the budget and record `tool_calls_spent` and `retrieved_urls` (§3.2).
9. `compress_research`: add the findings instruction, call `build_task_result` or map `CompressionFailed` (§3.3), and return `compressed_research = task_result.summary`, `raw_notes` and `task_result`.
10. Run the checks in `verification-constraints.md` §4 and record them in `docs/build-reports/REQ-001.md` and `REQ-003.md`.
