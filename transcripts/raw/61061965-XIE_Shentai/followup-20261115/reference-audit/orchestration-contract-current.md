- 为什么要这个文件?
ADR 本安排在后面的 Design 阶段写, 但因为蓝图需要定下字段给其他模块, 所以ADR-002编排契约需要提前做.

- 涉及不同人的契约对接:
Alchemy: 第 2-8 节 (REQ-002 失败隔离和 REQ-004 运行结论都读写这里的类型; 第 6 节 `supervisor_tools` 里我们俩的交接点)
Tekon: 第 6 节 `compress_research` 的 except 分支 (REQ-005)
Jeremy: 第 5 节, `### Sources` 引用格式 (REQ-006) 是我解析来源的依据
Doppler: 第 8 节, 评估只读不写

## 变更点
(Centay, 2026.11.11, 讨论稿 v0.5; 按 11/11 重新编号的 requirements.yaml 对齐 v0.4. v0.4 的两轮 OpenCode 预演: 106 个离线测试通过, 只改了自己的文件)
**核心: 先把编排模块和别人模块之间传的数据定死, 大家照这个各做各的, 不用等我的代码**
1. 需求编号跟着新表走: 契约对应 REQ-001 (任务契约) 和 REQ-003 (终止); Alchemy 的 REQ-002 / REQ-004、Tekon 的 REQ-005 都通过这里的类型写失败结果
2. 任务状态只剩 `complete` / `partial` / `failed` 三种, 和 REQ-001 一致; 原来的 `not_run` 状态改成 `failed` + 类别 `not_run` (REQ-002 C-005)
3. 失败类别字段改名 `failure_category`, 取值和 REQ-002 提议的一致: `runtime`、`token_limit`、`not_run`、`invalid_result`, 再加一个 `unanswered` (跑完了但有必答问题没有带来源的发现)
4. "有来源" 按 REQ-001 定: 发现引用的每个 URL 都必须是本任务工具调用返回过的; 新增 `retrieved_urls` 由代码记录, 没来源的发现直接丢掉, 读的人拿到的每条发现都有来源
5. 结束原因优先级按 REQ-003: covered > budget_exhausted > stalled > failed; `failed` 只指 supervisor 自己的模型调用重试后仍失败, 删掉了 v0.4 的 "全部任务失败" 退出
6. 整轮覆盖率按去重后的必答问题算, 任务失败后重新派活能补回来; supervisor 会拿到原文的未回答问题列表, 重派时照抄
7. 代码行重新分 (第 6 节): 分发、并发、gather 和 except 分支 (L282-342) 归 Alchemy; 退出检查、本轮末尾的覆盖率判断、supervisor 模型失败归 Centay; `compress_research` 的 except 分支归 Tekon; 交接点是 `update_payload["task_results"]`
8. 退出时的 `notes` 改由契约生成 (只放 complete / partial 任务的摘要), 失败文本进不了报告 (REQ-002 C-007)
9. 测试文件名跟 requirements 走: `test_task_contract.py` (REQ-001)、`test_research_termination.py` (REQ-003); 共享的示例数据和 `test_contracts.py` 还是我先交

(确认后由 OpenCode 写成 ADR-002 和 `state.py`, 本讨论稿届时删除)

***

# Orchestration contract: TaskSpec, TaskResult, exit_reason

Status: draft v0.5 for review by the readers listed in section 5. After approval it becomes ADR-002 and the types in `state.py`. Requirements: REQ-001 (task contract) and REQ-003 (termination) in `docs/req/requirements.yaml`, revision of 2026-11-11. REQ-002 (failure isolation), REQ-004 (run outcome) and REQ-005 (compression recovery) create or read results only through the types and helpers defined here. Where this document and a requirement disagree, the requirement wins and this document is corrected.

## 1. Purpose and the flag

Other modules read what orchestration produces. Fixing the shape first lets every owner design, build and test against it without waiting for the orchestration code. A change to any field in this document is a shared-contract change and needs the approval of every reader.

Orchestration sits behind one configuration flag, `orchestration_enabled` (default `false`). With the flag off the graph behaves exactly as the baseline: the model sees the original `ConductResearch` tool, and none of the fields in section 4 are written. Readers do not read the flag; they read `exit_reason`, which is `None` exactly when orchestration did not run. REQ-002 and REQ-004 code that creates or reads the fields of section 4 runs only when the flag is on; whether any other REQ-002 behaviour gets a flag of its own is decided in Alchemy's ADR-003.

## 2. Types (to live in `state.py`)

```python
TaskStatus = Literal["complete", "partial", "failed"]
ExitReason = Literal["covered", "budget_exhausted", "stalled", "failed"]
FailureCategory = Literal[
    "unanswered",      # partial or failed: the task ran, but some or all required questions have no sourced finding (REQ-001)
    "invalid_result",  # failed: the researcher output did not pass contract validation (REQ-001 C-004)
    "runtime",         # failed: the researcher or its compression raised (REQ-002 C-001)
    "token_limit",     # failed: a token or context limit that could not be recovered (REQ-002 C-003, REQ-005 C-004)
    "not_run",         # failed: the delegation was still unrun when the research loop exited (REQ-002 C-005)
]

class ConductResearchV2(BaseModel):
    """Delegation tool bound to the supervisor model only when orchestration_enabled is true.
    The baseline ConductResearch class is not changed. The tool name the model sees stays
    "ConductResearch", so the baseline filters on tool_call["name"] match both versions."""
    research_topic: str = Field(description="The topic to research, described in detail.")
    must_answer: list[str] = Field(default=[], description="Questions this delegation must answer, one per item, at most 5.")
    scope: str = Field(default="", description="What is in and out of scope for this delegation.")

class TaskSpec(BaseModel):
    """Built by orchestration code from one delegation call. Never filled by a model."""
    task_id: str            # "T1", "T2", ... unique within one supervisor run
    research_topic: str
    must_answer: list[str]  # never empty: an empty list from the model becomes [research_topic]
    scope: str
    max_tool_calls: int     # 1 to max_react_tool_calls, in the same unit (researcher tool-calling turns)

class Source(BaseModel):
    source_id: str          # "S1", "S2", ... unique within one task
    url: str
    title: str = ""

class Finding(BaseModel):
    claim: str
    source_ids: list[str]   # at least one; each id exists in TaskResult.sources
    answers: list[str] = [] # must_answer items this claim addresses, exact text

class TaskCost(BaseModel):
    tool_calls: int = 0     # tool calls actually made by the researcher (REQ-001)
    input_tokens: int = 0
    output_tokens: int = 0

class TaskResult(BaseModel):
    task_id: str
    status: TaskStatus
    failure_category: Optional[FailureCategory] = None
    failure_reason: Optional[str] = None  # the error message, or the unanswered questions; one paragraph, no stack trace
    summary: str = ""                     # the compressed research text; "" unless the task ran to compression
    findings: list[Finding] = []          # sourced findings only
    sources: list[Source] = []
    retrieved_urls: list[str] = []        # every http(s) URL that appeared in a tool result of this task, recorded by code
    must_answer: list[str]                # copied from the TaskSpec, never empty
    coverage: float = 0.0                 # 0.0 to 1.0, computed by code only
    cost: TaskCost = TaskCost()

    def unanswered(self) -> list[str]:
        """must_answer items that no finding lists in `answers`, in must_answer order."""
```

```python
class RunRecord(BaseModel):
    """One supervisor run as a whole. Orchestration builds it and writes its fields to state;
    readers rebuild it with RunRecord.from_state(state)."""
    exit_reason: ExitReason
    exit_detail: Optional[str] = None
    run_coverage: float
    coverage_threshold: float
    task_results: list[TaskResult] = []

    @classmethod
    def from_state(cls, state: Mapping[str, Any]) -> Optional["RunRecord"]:
        """None when exit_reason is None and task_results is empty (orchestration did not run).
        Raises ValueError for any state that breaks this contract, including task_results without exit_reason."""

    def to_state_update(self) -> dict:
        """The state update orchestration returns at loop exit: the five fields of section 4
        (task_results as an override) and notes built from the results (section 3, rule 8)."""
```

Helpers in `src/open_deep_research/orchestration/`, the only way other code creates these objects:

| Helper | Returns | Called by |
|---|---|---|
| `build_task_spec(tool_call, task_id, config)` | `TaskSpec` | REQ-002 dispatch |
| `render_task_message(spec)` | the text of the researcher's first `HumanMessage`: topic, scope, required questions, budget | REQ-002 dispatch |
| `build_task_result(spec, summary, researcher_messages)` | `TaskResult` with status derived per rule 1 | `compress_research` |
| `validate_task_result(output, spec)` | the output's `TaskResult`, or a `failed` / `invalid_result` one | REQ-002 result handling |
| `failed_result(spec, category, message)` | a `failed` `TaskResult` | REQ-002, REQ-005, `compress_research` |
| `not_run_result(spec)` | a `failed` / `not_run` `TaskResult` | exit check |

Wherever a requirement says a task ends failed "with reason X" or "with category X" for one of the five values above, it means `failure_category == X`.

A finding is sourced when every `url` of its listed sources is in `retrieved_urls` (REQ-001). `build_task_result` drops findings that are not sourced before the object is built, so a reader never sees one.

Validators in `state.py` (Pydantic `model_validator`). Every rule below is enforced in code, so an object that breaks it cannot be built and readers never see one.

`TaskResult`:

1. `must_answer` is not empty; `coverage` is between 0.0 and 1.0 and equals the share of `must_answer` items that at least one finding lists in `answers`. The same non-empty rule applies to `TaskSpec.must_answer`, and `TaskSpec.max_tool_calls` is at least 1.
2. `failure_category` and `failure_reason` are both set when `status` is `partial` or `failed`, and both `None` when `status` is `complete`.
3. Every finding is sourced: it lists at least one source id, every id exists in `sources`, and every such source's `url` is in `retrieved_urls`; every item in `answers` is one of `must_answer`.
4. `status` agrees with `coverage` (REQ-001): `complete` has 1.0; `partial` is above 0.0 and below 1.0, with category `unanswered`; `failed` has 0.0. A `failed` result with category `invalid_result`, `runtime`, `token_limit` or `not_run` has no findings and an empty `summary`.

`RunRecord`:

5. `task_id` values are unique.
6. `run_coverage` equals the formula in section 3, rule 2.
7. `exit_detail` is set whenever `exit_reason` is not `covered`.
8. `covered` has at least one task and `run_coverage >= coverage_threshold`; `budget_exhausted` and `stalled` have `run_coverage < coverage_threshold`. `failed` has no coverage condition.

## 3. Rules orchestration guarantees

1. Task `status` is derived by code from the sourced findings, never by the model (REQ-001): `complete` when every required question has one, `partial` when some but not all do, `failed` when none do; `partial` and this kind of `failed` carry category `unanswered`, and `failure_reason` names the unanswered questions. An output that fails contract validation becomes `failed` / `invalid_result`. The other categories are set by the code that meets the failure: `runtime` and `token_limit` by REQ-002 result handling and by `compress_research` (REQ-005 for an unrecoverable token limit), `not_run` by the exit check.
2. Run coverage `run_coverage` is computed over distinct required questions. A question is normalised by case-folding and collapsing white space; it counts as answered when at least one task of the run has a finding that lists it. `run_coverage` = answered distinct questions over all distinct questions in `task_results`, failed tasks included, and 0.0 when there are none. A task that fails and is re-delegated with the same question therefore does not lower coverage once the new task answers it.
3. With the flag on, the supervisor loop exits only through a `RunRecord`, so `exit_reason`, `exit_detail`, `run_coverage`, `coverage_threshold` and `task_results` are written together, once (REQ-003). When several conditions hold at once they take precedence in this order:
   1. `covered`: `run_coverage` is at least `coverage_threshold` (configuration, default 0.8).
   2. `budget_exhausted`: the iteration cap is reached.
   3. `stalled`: two consecutive supervisor turns that do more than call `think_tool` leave `run_coverage` unchanged.
   4. `failed`: the supervisor's own model call fails after its retries; `exit_detail` names the error. This may happen with zero tasks.
   Coverage, `covered` and `stalled` are checked at the end of every `supervisor_tools` turn, after that turn's tasks have joined; the iteration cap is checked at the start of the turn, before dispatch. A `ResearchComplete` call, or a turn without tool calls, is only a request: it ends the loop when rule 3.1 holds; otherwise the tool response tells the supervisor which required questions are still unanswered, verbatim, so that a re-delegation can copy them, and the loop continues.
4. A failing research task never ends the loop on its own (REQ-002); it becomes a `failed` task result.
5. Every delegation in the turn on which the iteration cap is reached becomes a `not_run` result before the `RunRecord` is built, so no delegation is missing from `task_results` (REQ-002 C-005). Delegations above the concurrency limit are queued and joined within their own turn (REQ-002), so the cap turn is the only source of `not_run` results.
6. Because `covered` takes precedence, a run that ends with `budget_exhausted` or `stalled` has `run_coverage` below the threshold, so at least one task is not `complete`. `exit_reason` is the primary signal; `task_results` explain it. How a non-covered exit is reported to the caller is REQ-004.
7. One supervisor run per main-graph invocation. `task_results` is written as an override at exit, so the main state never mixes tasks from two runs.
8. With the flag on, `notes` at exit holds the `summary` of every `complete` or `partial` task, in task order, and nothing else: no failure text, no placeholder and no `think_tool` reflection reaches report generation as a finding (REQ-002 C-007). This contract reads "validated findings" in C-007 as the summaries of results that passed validation; the summary keeps the compressed research the report writer needs. `raw_notes` and the tool messages are filled as in the baseline.

## 4. State fields

| State | Field | Type and default | Reducer | Written by |
|---|---|---|---|---|
| `ResearcherState` | `task_spec` | `Optional[TaskSpec] = None` | last write wins | REQ-002 dispatch, when it starts a researcher |
| `ResearcherState`, `ResearcherOutputState` | `task_result` | `Optional[TaskResult] = None` | last write wins | `compress_research`, through `build_task_result` or `failed_result` |
| `SupervisorState`, `AgentState` | `task_results` | `list[TaskResult] = []` | `override_reducer` | REQ-002 result handling appends each turn's results; the exit writes the override |
| `SupervisorState`, `AgentState` | `exit_reason` | `Optional[ExitReason] = None` | last write wins | the exit check, the end-of-turn check, or `supervisor` for `failed` |
| `SupervisorState`, `AgentState` | `exit_detail` | `Optional[str] = None` | last write wins | same as `exit_reason` |
| `SupervisorState`, `AgentState` | `coverage_threshold` | `Optional[float] = None` | last write wins | same as `exit_reason` (the value used in this run) |
| `SupervisorState`, `AgentState` | `run_coverage` | `Optional[float] = None` | last write wins | same as `exit_reason` |

The `AgentState` fields receive the values from the supervisor subgraph because the names match. Readers use `state.get(...)`, never `state[...]`, for the new fields.

Hand-over inside `supervisor_tools`: the REQ-002 block (dispatch to except branch) puts this turn's results in `update_payload["task_results"]` as a plain list, one result per delegation it started, and never exits the loop or computes coverage. The end-of-turn check reads `state.get("task_results", []) + update_payload.get("task_results", [])`.

## 5. Ownership and readers

| Item | Defined and written by | Read by | Who may change it |
|---|---|---|---|
| `ConductResearchV2`, `TaskSpec`, the flag, `coverage_threshold` | Centay (REQ-001, REQ-003) | Alchemy (REQ-002 dispatch) | Centay, with an ADR-002 update |
| `TaskResult`, `Finding`, `Source`, `FailureCategory`, `TaskCost`, `RunRecord`, the state fields, the helpers | Centay; Alchemy (REQ-002) and Tekon (REQ-005) create failed results only through the helpers | Alchemy (REQ-004 outcome), Doppler (evaluation), everyone | Centay, with approval of all readers |
| The `### Sources` citation format in the compression prompt, from which `Source` entries are parsed | Jeremy (REQ-006) | Centay (`build_task_result`) | Jeremy, with Centay's approval |

Outside this contract, in Alchemy's ADR-003: how REQ-002 maps exceptions to categories, queues delegations above the concurrency limit and joins tasks; and the REQ-004 research outcome, failed-task list, limitations section and any new `AgentState` field for them. The outcome check is called from `final_report_generation`; no node is added.

## 6. Code ownership, so no two owners edit the same lines

Line numbers are those of `deep_researcher.py` at commit c42e13e (`main`); `src/open_deep_research` is identical at f4a016e and unchanged since commit 1f24f11. Each row names the lines where its owner places the call into their own extension module (blueprint section 5.2); the logic itself lives in that module.

| Code | Owner | Change |
|---|---|---|
| `supervisor` tool binding, L202 | Centay (REQ-001) | Bind `ConductResearchV2` instead of `ConductResearch` when the flag is on |
| `supervisor` model call, L212-223 | Centay (REQ-003) | Exit with `failed` when the supervisor's own model call fails after its retries |
| `supervisor_tools` exit check, L240-262 | Centay (REQ-003; REQ-002 C-005 as its contributor) | Iteration cap with `not_run` results for the turn's delegations; `ResearchComplete` and turns without tool calls handled as requests |
| `supervisor_tools` `think_tool` handling, L264-281 | baseline | Unchanged |
| `supervisor_tools` dispatch, gather and result handling, L282-330 | Alchemy (REQ-002) | Queueing instead of dropping, per-task isolation, join; `build_task_spec` and `render_task_message` for each researcher, `validate_task_result` for each output, results into `update_payload["task_results"]` |
| `supervisor_tools` except branch, L332-342 (`or True`) | Alchemy (REQ-002) | An exception never ends the research phase on its own |
| `supervisor_tools` end of turn, L344-349 | Centay (REQ-003) | Coverage, `covered` or `stalled` exit through `RunRecord`, otherwise back to the supervisor |
| `researcher_tools` budget check, L491-498 | Centay (REQ-001) | Use `task_spec.max_tool_calls` when a task spec is present |
| `compress_research` success return, L559-563 | Centay (REQ-001) | Add `task_result` from `build_task_result` |
| `compress_research` except branch, L565-574, and `remove_up_to_last_ai_message` in `utils.py` | Tekon (REQ-005) | Oldest-first trimming, classification with the compression model, `failed_result(..., "token_limit", ...)` when nothing more can be removed |
| `compress_research` after the retries, L576-585 | Centay (REQ-001; REQ-002 C-007 as contributor) | Replace the placeholder with `failed_result`: `token_limit` when the last attempt failed on a token limit, `runtime` otherwise |
| `final_report_generation`, L607 onward, plus `delivery/` | Alchemy (REQ-004) | Research outcome, failed-task list, limitations section |
| `state.py`: the types of section 2 and the fields of section 4 | Centay | New types and fields only; the baseline classes are not changed |
| `lead_researcher_prompt` in `prompts.py`, L79, and any findings instruction in the compression prompt | Centay drafts | Jeremy approves (prompt owner, REQ-006) |
| `configuration.py`: `orchestration_enabled`, `coverage_threshold` | Centay | Two new fields; no other field changes |
| `pyproject.toml` `[tool.setuptools] packages` | the owner who adds a subpackage | Add that subpackage in the same pull request |

## 7. What orchestration delivers to the other owners

1. `test/offline/fixtures/orchestration.py`: plain literals, built without any orchestration code. Each fixture is a state dict with `research_brief`, `notes`, `exit_reason`, `exit_detail`, `run_coverage`, `coverage_threshold` and `task_results`, and every non-baseline fixture passes `RunRecord.from_state`:
   1. `covered_full`: every task complete, `run_coverage` 1.0.
   2. `covered_threshold`: one task partial, `run_coverage` 0.8.
   3. `stalled`; `budget_exhausted` with two `not_run` tasks; `budget_exhausted_all_failed`, where every task failed with `runtime` or `token_limit`; `failed_supervisor_error`, with no tasks.
   4. `baseline`: a state with none of the new keys, as the baseline graph produces today.
2. `test/offline/test_contracts.py`: validates every fixture against the types and the eight validators, with one negative test per validator, and checks that the delegation tool is named `ConductResearch`. A field change breaks this test, so the CI regression gate blocks a silent contract change.
3. The requirement tests named in `docs/req/requirements.yaml`: `test/offline/test_task_contract.py` (REQ-001) and `test/offline/test_research_termination.py` (REQ-003). Every other owner writes the test file named in their own requirement and may import the fixtures; a change to a fixture is a change to this contract. Only the state fixtures are shared: fake models and fake researchers are each owner's own test code.

## 8. What readers may rely on

1. They never see an invalid `TaskResult` or an inconsistent run: both are rejected when they are built, and every finding they see is sourced.
2. `exit_reason is None` means orchestration did not run; then `task_results` is empty and the baseline fields are filled as before. This is the only case readers must handle besides the four exit reasons.
3. `task_results` without an `exit_reason` cannot occur, because both are written together from one `RunRecord`.
4. Every delegation of the run has exactly one entry in `task_results`. A `complete` task has a sourced finding for every required question; a `budget_exhausted` or `stalled` run has at least one task that is not `complete`; a `failed` run always carries `exit_detail`.
5. `notes` at exit contains no failure or placeholder text.
6. `RunRecord.from_state(state)` is the supported way to read the run. Every contract violation it detects raises `ValueError`, so a reader handles a broken state in one place; whether it then fails closed or re-raises is the reader's own policy (for the run outcome: REQ-004).
