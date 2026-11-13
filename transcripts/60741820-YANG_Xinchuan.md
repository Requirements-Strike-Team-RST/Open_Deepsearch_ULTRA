# Evaluation module SA session — DopplerXD

- Date: 2026-11-13
- Requirements: REQ-009 v1.1, REQ-010 v1.1
- Branch: docs/sa-evaluation
- OpenCode session: `ses_e2adf4cdeffe9h92cWfrl4SAnn`
- Stage: software architecture; ADR status Proposed; module review and Gate 1 pending.

## Record scope

按事件顺序保留 OpenCode 会话中的用户消息、公开回复及工具调用输入和结果。内部推理和系统消息不列入记录，凭据模式统一脱敏，行尾空白已清理。工具输出保留其原有截断标记。H-01 至 H-06 标注实际人工干预及其理由。
Student: YANG Xinchuan (60741820).

## Session record

### Event 0 — User

按 AGENTS.md 的阅读顺序和 Prompt.md Phase 1，为 evaluation 模块完成 SA 设计草案。

任务为 docs/req/requirements.yaml 中已 approved 的 REQ-009 v1.1 和 REQ-010 v1.1，负责人 DopplerXD。模块路径按蓝图为 test/evaluation/。

先核对角色、分支、工作区和权限。读取需求、蓝图、规则、权限文件、结构与验证约束、现有 ADR 和模板。分析 test/evaluators.py、test/prompts.py、test/run_evaluate.py 及调用方，核对评分输入、范围校验、空 claims、异常传播和导入副作用，引用当前代码位置。

1. 识别影响架构的需求，映射 REQ-009 的 C-001—C-004/M-001，以及 REQ-010 的 C-001—C-003。
2. 用 ADD 比较 2—3 个候选方案，在 evaluation-table.md 添加模块条目。比较正确性、复用、耦合、基准入口兼容性、离线可测性和复杂度，给出推荐及待人工决定事项。
3. 从模板创建 Proposed ADR，填写全部九节，明确组件、公共接口、输入输出、评分状态、严格整数校验、失败隔离、文件评估入口，以及逐文件实现步骤。
4. 补充 evaluation 模块的 invariants、runtime-policy-catalog、trace-matrix、structural-constraints §10 和 verification-constraints §7。涉及状态变化时补 memory-design §5。
5. 每个验收项列出测试输入、预期结果和计划测试位置，覆盖正常、异常、边界和回归。REQ-010-C-003 保留为人工操作检查。

遵守 plan 权限，仅编写架构文档与测试用例清单，完成后停在人工 SA 评审前。禁止编写源码、测试代码或审批记录，禁止提交或推送。

在聊天中提供本次实际操作对应的 AI 使用日志建议条目，供我核对填写。最后报告改动文件、验收覆盖、检查结果及待人工决策事项。

> **H-01 Scope and phase**
> 限定 REQ-009、REQ-010 的 SA 范围，要求比较方案并保留源码、测试和审批门禁。

### Event 1 — OpenCode (plan)

I'll start by verifying the environment and reading the required governance documents.

#### Tool bash — completed

```json
{
  "input": {
    "command": "git status --short --branch && git branch --show-current && git log --oneline -5"
  },
  "output": [
    {
      "type": "text",
      "text": "## docs/sa-evaluation\ndocs/sa-evaluation\n827fd32 Merge pull request #4 from Requirements-Strike-Team-RST/chore/governance-and-sa-templates\n7fed18a docs: review module branches in draft PRs and integrate them with git merge\na5253ff docs: add module review and single-integrator step to the SA workflow\nc197e5a docs: record AI-assisted work in the AI-use log\n3bf723c docs(architecture): add SA templates and move blueprint under docs\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "ls -la && echo \"---\" && ls docs && echo \"---\" && ls docs/architecture && echo \"---\" && ls docs/architecture/adr 2>/dev/null && echo \"---\" && ls test 2>/dev/null"
  },
  "output": [
    {
      "type": "text",
      "text": "total 2112\ndrwxr-xr-x  29 doppler  staff     928 Nov 13 18:42 .\ndrwxr-xr-x@ 17 doppler  staff     544 Nov 10 14:29 ..\n-rw-r--r--@  1 doppler  staff    6148 Oct 12 14:44 .DS_Store\ndrwxr-xr-x@  3 doppler  staff      96 Nov 13 18:42 .agent\n-rw-r--r--@  1 doppler  staff     562 Nov 13 18:42 .editorconfig\n-rw-r--r--   1 doppler  staff     365 Sep 21 15:09 .env.example\ndrwxr-xr-x  15 doppler  staff     480 Nov 13 21:37 .git\n-rw-r--r--@  1 doppler  staff     228 Nov 13 18:42 .gitattributes\ndrwxr-xr-x   4 doppler  staff     128 Nov 13 18:42 .github\n-rw-r--r--   1 doppler  staff     616 Sep 21 15:09 .gitignore\ndrwxr-xr-x@  9 doppler  staff     288 Nov 13 21:31 .opencode\n-rw-r--r--@  1 doppler  staff       5 Nov 13 18:42 .python-version\n-rw-r--r--@  1 doppler  staff    9175 Nov 13 18:42 AGENTS.md\n-rw-r--r--   1 doppler  staff    1065 Sep 21 15:09 LICENSE\n-rw-r--r--@  1 doppler  staff   12124 Nov 13 18:42 Prompt.md\n-rw-r--r--@  1 doppler  staff    9528 Nov 13 18:42 README.md\n-rw-r--r--@  1 doppler  staff     210 Sep 27 18:40 Report.md\n-rw-r--r--@  1 doppler  staff    2805 Sep 27 18:40 SE Project 文件Reference.txt\n-rw-r--r--@  1 doppler  staff    1151 Sep 27 18:40 change_log.txt\ndrwxr-xr-x@ 10 doppler  staff     320 Nov 13 18:42 docs\ndrwxr-xr-x   6 doppler  staff     192 Sep 21 15:09 examples\n-rw-r--r--@  1 doppler  staff     295 Nov 13 18:42 langgraph.json\ndrwxr-xr-x@  3 doppler  staff      96 Sep 27 18:40 prompts\n-rw-r--r--@  1 doppler  staff    1982 Sep 27 18:40 pyproject.toml\ndrwxr-xr-x@  3 doppler  staff      96 Nov 13 18:42 scripts\ndrwxr-xr-x   4 doppler  staff     128 Sep 27 18:40 src\ndrwxr-xr-x@ 11 doppler  staff     352 Sep 27 18:40 test\ndrwxr-xr-x@  4 doppler  staff     128 Sep 27 18:40 transcripts\n-rw-r--r--   1 doppler  staff  988217 Sep 21 15:09 uv.lock\n---\nai-use-log.yaml\narchitecture\nbug-diary.md\ncode-governance\ndebt-register.md\nreq\nreview-memo.md\n---\nadr\narchitecture-blueprint.md\nevaluation-table.md\ninvariants.md\nmemory-design.md\npermission-model.md\nruntime-policy-catalog.md\ntrace-matrix.md\n---\n000-template.md\n---\n__init__.py\nevaluators.py\nextract_langsmith_data.py\nlive\noffline\npairwise_evaluation.py\nprompts.py\nrun_evaluate.py\nsupervisor_parallel_evaluation.py\n"
    }
  ]
}
```

### Event 2 — OpenCode (plan)

#### Tool read — completed

````json
{
  "input": {
    "filePath": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/Prompt.md"
  },
  "output": [
    {
      "type": "text",
      "text": "<path>/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/Prompt.md</path>\n<type>file</type>\n<content>\n1: # Prompt.md — Coding Agent Workflow\n2: \n3: > **Purpose:** The order in which work happens once a requirement is approved: software architecture, review, tests, implementation and verification, with the human gates between them.\n4: > **Authoritative for:** workflow and gates only. Permissions, structure and verification rules live in the documents referenced below and are not repeated here.\n5: > **Maintained by:** humans.\n6: > **Last updated:** 2026-11-12\n7: \n8: ## 0. Golden Rule\n9: \n10: > **No agent goes straight from \"task received\" to \"code written\".** Code is written only after the architecture has passed SA Review and the tests have been approved.\n11: \n12: The approved SA documents together form the execution plan the course requires before code generation:\n13: \n14: | Course element | Where it is |\n15: |---|---|\n16: | Traceability | `docs/architecture/trace-matrix.md` |\n17: | Interface contract | ADR §5 Components and Interfaces |\n18: | Scope boundaries | ADR §3 and `structural-constraints.md` §10 |\n19: | Testing strategy | `verification-constraints.md` §7 |\n20: | Steps | ADR §9 Implementation Steps |\n21: \n22: Tests and implementation are written by different roles: Test Author writes the tests, Build writes the code that makes them pass, and neither changes the other's work.\n23: \n24: ## 1. Before Any Task\n25: \n26: 1. Read the documents in `AGENTS.md` §2.\n27: 2. Confirm the current role (Plan, Test Author, Build or Verify), the requirement ID (RID) and what the role may write (`docs/architecture/permission-model.md` §2–§3). The task ID is the RID, e.g. `REQ-005`.\n28: 3. Confirm the task's state: Plan needs the requirement `approved` in `docs/req/requirements.yaml`; Test Author needs Gate 1; Build needs Gate 2; Verify needs the build report.\n29: 4. If anything is missing or ambiguous, ask the human; do not guess.\n30: \n31: ## 2. Workflow at a Glance\n32: \n33: ```mermaid\n34: flowchart LR\n35:   R[\"Requirements\"] --> ASR[\"ASR\"] --> ADD[\"ADD<br/>2–3 candidates\"] --> ADR[\"ADR\"]\n36:   ADR --> M[\"Module sections<br/>on own branch\"] --> MR{\"Module review<br/>in a draft PR\"}\n37:   MR -->|\"changes needed\"| M\n38:   MR -->|ok| I[\"Integration<br/>Blueprint + constraints\"] --> G1{{\"GATE 1<br/>SA Review\"}}\n39:   G1 --> T[\"Test Author<br/>tests fail on baseline\"] --> G2{{\"GATE 2<br/>tests approved\"}}\n40:   G2 --> B[\"Build<br/>implementation\"] --> V[\"Verify<br/>new + regression tests\"]\n41:   V -->|\"test defect\"| T\n42:   V -->|\"code defect\"| B\n43:   V -->|\"architecture defect\"| ADD\n44:   V -->|pass| G3{{\"GATE 3<br/>PR + review + CI\"}}\n45: ```\n46: \n47: | # | Step | Who | Output |\n48: |---|---|---|---|\n49: | 1 | ASR, ADD, ADR, module sections | Each module owner, optionally with the Plan agent | EVAL entry, ADR, module sections on the branch `docs/sa-<module>` (§3) |\n50: | 2 | Module review | Reviewers named in the module's draft PR | Findings fixed by the owner on their branch until none remain; the draft PR is never merged (§4) |\n51: | 3 | Integration | The integrator, assisted by AI | One integration branch that merges every module branch: integrated documents and blueprint (§4) |\n52: | 4 | SA Review — **Gate 1** | Whole team | `SA-NNN` record in `docs/review-memo.md`; ADRs *Accepted*; integration merged into `main` |\n53: | 5 | Test authoring | Test Author | Tests; baseline run in `docs/test-reports/<RID>.md` |\n54: | 6 | Test approval — **Gate 2** | Human reviewer | Approved test commit in `docs/approvals/<RID>.md` |\n55: | 7 | Implementation | Build | Code; `docs/build-reports/<RID>.md` |\n56: | 8 | Verification and fixes | Verify, then Test Author or Build | Verification in `docs/test-reports/<RID>.md` |\n57: | 9 | PR, review, CI — **Gate 3** | Two other members, CI | Merged PR |\n58: \n59: ## 3. Phase 1 — Software Architecture (per module)\n60: \n61: Each module owner works on the module listed for their requirements in `architecture-blueprint.md` §4, on a branch `docs/sa-<module>` created from `main`. The Plan agent may draft; the owner decides. When done, the owner pushes the branch and opens a **draft** pull request to `main` for review only, naming at least one reviewer. The draft PR is never merged: every module edits the same shared documents, so the integrator merges all module branches at once (§4).\n62: \n63: 1. **ASR.** From `docs/req/requirements.yaml`, pick the requirements of the module that shape the architecture and the acceptance criteria (C-/M-) that matter.\n64: 2. **ADD.** Propose 2–3 candidate solutions and compare pros, cons, complexity and offline testability in a new entry of `docs/architecture/evaluation-table.md`.\n65: 3. **ADR.** Record the decision in `docs/architecture/adr/NNN-<slug>.md` from `000-template.md`: the choice, why, the rejected options, the components and interfaces, and the implementation steps.\n66: 4. **Module sections.** Add the module's part to each shared document that applies; skip a document the module does not touch.\n67: \n68: | Document | Module adds | Required when |\n69: |---|---|---|\n70: | `docs/architecture/invariants.md` | Invariants, enforcing component, verification, fallback | Always for `safety_relevant` or `invariant`-type requirements |\n71: | `docs/architecture/memory-design.md` §5 | State fields, ownership, lifecycle | The module adds or changes state |\n72: | `docs/architecture/runtime-policy-catalog.md` §2 | Exception, retry, degradation and failure policies | The module handles failures |\n73: | `docs/architecture/trace-matrix.md` | Architecture component and verification method for each REQ | Always |\n74: | `docs/code-governance/structural-constraints.md` §10 | Module path, interface, allowed and forbidden dependencies | Always |\n75: | `docs/code-governance/verification-constraints.md` §7 | Normal, exception, boundary and regression cases per C-/M-/INV | Always |\n76: \n77: ## 4. Module Review, Integration and SA Review — Gate 1\n78: \n79: 1. **Module review.** Reviewers comment in the module's draft PR: the ADR is complete and implementable, every acceptance criterion and invariant has a test case, and the module stays within its responsibility. The owner fixes findings on the same branch, which updates the draft PR, until no finding remains.\n80: 2. **Integration.** When every module has been reviewed, one member, the integrator, creates an integration branch from `main` and merges each module branch into it with `git merge`, so every member's commits stay in the history. AI may resolve the merge conflicts and draft the integrated sections; the integrator checks the result: unified IDs (EVAL, ADR, INV, POL), no overlapping responsibilities, no dependency outside `structural-constraints.md` §5, no state field written by two modules, and no criterion or invariant without a test case. The architecture blueprint is then written from the ADRs: components, interfaces, dependencies, data flow and deterministic boundaries.\n81: 3. **SA Review.** The integration branch is opened as one pull request to `main`, and the whole team reviews it. The result is recorded as `SA-NNN` in `docs/review-memo.md`; accepted ADRs change status to *Accepted*; the pull request is merged; each module's draft PR is closed with a link to it; and for each requirement that passes, the human records Gate 1 in `docs/approvals/<RID>.md` with the SA-NNN reference.\n82: \n83: No agent performs or forges a gate.\n84: \n85: ## 5. Phase 2 — Test Authoring\n86: \n87: 1. Write the tests for the module's cases in `verification-constraints.md` §7, in `test/offline/` (and `test/live/` where a case needs a real model), following `verification-constraints.md` §3. Tests target the interfaces in the accepted ADR, not an implementation.\n88: 2. Run them on the baseline and confirm each fails for the expected reason — a missing behaviour, not an import error or a broken fixture. A test that passes on the baseline does not prove the requirement; rewrite it or report it.\n89: 3. Record each command, the failing tests and their failure reasons in the \"Baseline\" section of `docs/test-reports/<RID>.md`, and commit the tests.\n90: \n91: Test Author does not change source code. If an interface in the ADR cannot be tested as written, stop and report it.\n92: \n93: ## 6. Gate 2 — Test Approval\n94: \n95: A human reviewer checks the test commit: every case in the module's §7 table has a test, each test checks the requirement rather than an implementation detail, and the baseline failures have the expected reasons. The reviewer records the approved commit in `docs/approvals/<RID>.md`. A later change to an approved test needs a new Gate 2.\n96: \n97: ## 7. Phase 3 — Implementation\n98: \n99: **Entry condition:** Gate 2 is recorded.\n100: \n101: 1. Read the accepted ADR, the blueprint, the module's section in `structural-constraints.md` §10 and the governance rules.\n102: 2. Implement the ADR's implementation steps within the module's scope until the approved tests pass.\n103: 3. Run the checks in `permission-model.md` §4 and record each command and its result in `docs/build-reports/<RID>.md`. CI on the PR is the authoritative run.\n104: 4. Draft the PR description and the proposed entries for `docs/ai-use-log.yaml` and `docs/review-memo.md` in the build report; humans apply them.\n105: \n106: Build never changes the approved tests. If a test looks wrong, stop and report it; the fix goes back to Test Author and Gate 2. If the implementation would deviate from the ADR, stop: that is an architecture change (§10). Build pushes only when the human confirms.\n107: \n108: ## 8. Phase 4 — Verification and Fixes\n109: \n110: Verify runs the new tests, the boundary and exception cases, and every existing offline suite, plus any live or human checks the module's §7 table requires, and confirms that the tests in the PR are the approved ones. Results go to the \"Verification\" section of `docs/test-reports/<RID>.md`, using the rules in `verification-constraints.md` §6.\n111: \n112: Verify classifies each defect as a test, code or architecture defect and returns it to Test Author, Build, or the module owner (§10). It never edits source code, tests or thresholds.\n113: \n114: ## 9. Gate 3 — PR, Review and CI\n115: \n116: The PR follows `AGENTS.md` §7: one improvement per branch, English Conventional Commits, at least two other members' approvals, all active CI gates green (`verification-constraints.md` §5). The PR review is recorded in `docs/review-memo.md`.\n117: \n118: Artifacts that change in the same PR:\n119: \n120: | Artifact | Written by |\n121: |---|---|\n122: | Tests | Test Author |\n123: | Source | Build |\n124: | `docs/test-reports/<RID>.md` | Test Author (Baseline), Verify (Verification) |\n125: | `trace-matrix.md` row: code and test evidence | Module owner |\n126: | `docs/ai-use-log.yaml`, `docs/review-memo.md` | Humans, from the drafts in the build report |\n127: | Prompt or model change: `prompts/` version bump and semantic evaluation | Build (prompt), Verify (evaluation) |\n128: \n129: ## 10. Architecture Rework\n130: \n131: When verification or implementation shows that the architecture itself is wrong, the module owner runs another ADD round: a new EVAL entry, a new ADR that supersedes the old one (or an amended ADR still *Proposed*), updated module sections, and another SA Review. Tests affected by the change go through Gate 2 again.\n132: \n133: ## 11. Closing a Requirement\n134: \n135: The human advances the requirement's `status` in `requirements.yaml` (`approved → in_progress → implemented → verified`) once the Definition of Done in `verification-constraints.md` §8 is met. A requirement is never marked `verified` while a mandatory check is `FAIL`, `NOT_RUN` or `BLOCKED`.\n136: \n137: ## 12. Reporting and Conflicts\n138: \n139: Report to the human in the format of `AGENTS.md` §8. Handle conflicting instructions as in `.opencode/rules.md` R7: report them and wait; never pick an interpretation silently.\n140: \n141: ## Appendix — Course Requirement Mapping\n142: \n143: | Course requirement | Where it is met |\n144: |---|---|\n145: | Execution plan before code, then stop for approval | §0, §3, §4 |\n146: | Test approval before implementation | §5, §6 |\n147: | Human supervision with auditable artifacts | `docs/approvals/`, `docs/review-memo.md`, `docs/ai-use-log.yaml`, `transcripts/` |\n148: | Requirements → architecture → build → verification chain | §3–§11 |\n149: | A decision where model output is gated by deterministic code | Requirements marked `safety_relevant: true`; `structural-constraints.md` §7; blueprint §8 |\n150: | Six blocking CI gates | `verification-constraints.md` §5 |\n151: | Traceability Req → Design → Code → Test → Monitor | `trace-matrix.md`, §3, §9 |\n152: | Artifacts that evolve with the code | §9, §10 |\n\n(End of file - total 152 lines)\n</content>"
    }
  ]
}
````

#### Tool read — completed

```json
{
  "input": {
    "filePath": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/.opencode/rules.md"
  },
  "output": [
    {
      "type": "text",
      "text": "<path>/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/.opencode/rules.md</path>\n<type>file</type>\n<content>\n1: # Coding Agent Rules\n2: \n3: > **HUMAN-ONLY FILE — agents must not modify it.**\n4: > **Purpose:** The always-on behaviour rules for every coding agent role (Plan, Test Author, Build, Verify).\n5: > **Authoritative for:** agent behaviour. Paths and tools each role may use are in `docs/architecture/permission-model.md`; the workflow is in `Prompt.md`.\n6: > **Last updated:** 2026-11-12\n7: \n8: ## R1. Scope\n9: \n10: 1. Work only on the assigned requirement ID (RID) and within its approved scope.\n11: 2. Do not add unrelated functionality, refactor or reformat untouched code, or widen the scope silently.\n12: 3. Follow the accepted ADRs, the architecture blueprint, invariants and structural constraints; do not bypass shared contracts or security boundaries.\n13: \n14: ## R2. Approval Gates\n15: \n16: 1. A requirement enters software architecture only when its status in `docs/req/requirements.yaml` is `approved`.\n17: 2. No test is written before the architecture passes SA Review (Gate 1, `Prompt.md` §4), and no source code before the tests are approved (Gate 2, `Prompt.md` §6).\n18: 3. A proposed ADR or invariant is not approved until SA Review accepts it.\n19: 4. If implementation must deviate from the accepted ADR, or touches a shared contract or invariant, stop: that is an architecture change (`Prompt.md` §10).\n20: \n21: ## R3. Role Discipline\n22: \n23: - **Plan** drafts the software architecture (EVAL entries, ADRs, module sections); it never writes source or test code and never switches itself into another role.\n24: - **Test Author** writes the tests for the module's approved test cases and shows that they fail on the baseline; it never writes source code.\n25: - **Build** implements only approved files until the approved tests pass; it never changes those tests, approves its own plan or weakens acceptance criteria, and pushes only when the human confirms.\n26: - **Verify** verifies independently; it never fixes source code and never edits tests, thresholds or evidence to make a check pass.\n27: \n28: ## R4. Verification Honesty\n29: \n30: 1. Use only the verdicts `PASS / FAIL / NOT_RUN / BLOCKED / N/A`. A skipped check is not a pass.\n31: 2. Never claim a check passed without execution evidence.\n32: 3. A failed, blocked or unrun mandatory check keeps the requirement from being marked `verified`.\n33: 4. Never remove, weaken or rewrite a test to hide a failure.\n34: \n35: Verification layers and evidence rules: `docs/code-governance/verification-constraints.md`.\n36: \n37: ## R5. Traceability\n38: \n39: 1. Keep the RID identical across `requirements.yaml`, EVAL entries, ADRs, module sections, tests, test evidence, code docstrings and `trace-matrix.md`.\n40: 2. When a requirement changes, list the affected ADRs, module sections, tests, invariants and trace-matrix rows in the report.\n41: 3. Record significant architectural decisions as an ADR or an `evaluation-table.md` entry.\n42: \n43: ## R6. Governance Protection\n44: \n45: Human-owned files are listed in `docs/architecture/permission-model.md` §3. Agents modify them only when the human explicitly asks and confirms, and never modify permission configuration or approval records. If a rule is outdated, incomplete or contradictory: identify it, explain the proposed change, and request human review; governance changes go through the normal PR review.\n46: \n47: ## R7. Conflict Handling\n48: \n49: If instructions conflict between the accepted ADRs, architectural constraints, verification rules, these rules or any governance document:\n50: \n51: 1. Do not choose an interpretation silently.\n52: 2. Report the conflicting instructions and their sources.\n53: 3. Request human clarification.\n54: 4. Resume only after the conflict is resolved.\n55: \n56: The precedence order in `AGENTS.md` §3 tells you which document is likely to prevail; it does not remove the duty to report.\n57: \n58: ## R8. Secrets and Safety\n59: \n60: 1. Never read, print or commit `.env*` files, credentials or other secrets.\n61: 2. Code implementing a requirement marked `safety_relevant: true` follows `docs/code-governance/structural-constraints.md` §7: the decision is made by deterministic code, not by a model.\n\n(End of file - total 61 lines)\n</content>"
    }
  ]
}
```

### Event 3 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/req/requirements.yaml"
  },
  "output": [
    {
      "type": "text",
      "text": "schema_version: \"1.0.0\"\nupdated_at: \"2026-11-11\"\nnotes: >-\n  Consolidated team requirements, revision of 2026-11-11. All requirements are approved. Code\n  line references are to commit f4a016e. Verification paths name planned tests under\n  test/offline and test/live; none has been executed yet.\n\nrequirements:\n  - id: REQ-001\n    title: Supervisor delegation and researcher results shall follow a typed contract\n    type: functional\n    problem: >-\n      The supervisor delegates through ConductResearch, whose only field is a free-text\n      research_topic (state.py L15-19), so a researcher receives no scope, no questions it must\n      answer and no budget. A researcher returns ResearcherOutputState (state.py L92-96), which\n      holds free text and raw notes with no task id, no status and no source list. A failed,\n      empty or partial result therefore looks the same as a finished one, and nothing downstream\n      can check deterministically which parts of the research brief were answered.\n    statement: >-\n      The supervisor shall delegate every research task as a task specification that states a\n      task id, the scope, the questions the task must answer and a budget given as a maximum\n      number of tool calls no greater than max_react_tool_calls. Every researcher shall return a\n      task result that states the task id, the findings for each required question with the\n      source URLs that support them, the tool calls spent and, unless the task is complete, the\n      reason. A finding shall count as sourced only if each of its URLs was returned by a tool\n      call made in that task. The system, not the model, shall derive the task status from the\n      sourced findings: complete when every required question has one, partial when some but not\n      all do, and failed when none do. A result that fails contract validation shall be failed.\n    owner: centay\n    priority: must\n    priority_rationale: >-\n      Failure handling (REQ-002), the coverage check (REQ-003) and the run outcome (REQ-004) all\n      read these fields, so the contract has to exist first. Re-planning of failed tasks and\n      provider-aware scheduling are left out of this delivery.\n    scope:\n      in_scope:\n        - Task specification sent when the supervisor delegates\n        - Task result returned by a researcher\n        - Contract validation of results, including source URL resolution\n        - Derivation of task status from sourced findings\n      out_of_scope:\n        - Search tools and search provider selection inside the researcher\n        - Context compaction inside compress_research (REQ-005)\n        - Researcher exceptions and delegations above the concurrency limit (REQ-002)\n        - Final report format and citation rules (REQ-006)\n    fit_criterion:\n      summary: >-\n        Every delegation and every result passes contract validation, and every task status is\n        derived from findings whose sources were actually retrieved in that task.\n      checks:\n        - id: C-001\n          description: >-\n            Given a scripted supervisor turn that delegates one task, when supervisor_tools\n            dispatches it, then the researcher receives a task specification with task id,\n            scope, required questions and budget that passes schema validation.\n          verification: test/offline/test_task_contract.py::test_delegation_is_valid_task_spec\n          automated: true\n        - id: C-002\n          description: >-\n            Given a fake researcher whose findings answer two of three required questions with\n            URLs returned by its own tool calls, when its result is validated, then the status\n            is partial and the unanswered question is listed in the reason.\n          verification: test/offline/test_task_contract.py::test_status_derived_from_sourced_findings\n          automated: true\n        - id: C-003\n          description: >-\n            Given a fake researcher that claims every question answered but cites a URL that no\n            tool call in the task returned, when its result is validated, then that finding is\n            not counted and the status is derived from the remaining findings only.\n          verification: test/offline/test_task_contract.py::test_unretrieved_source_does_not_count\n          automated: true\n        - id: C-004\n          description: >-\n            Given a researcher output that does not match the result schema, when the supervisor\n            receives it, then the task result is failed with reason invalid_result.\n          verification: test/offline/test_task_contract.py::test_malformed_result_becomes_failed\n          automated: true\n      metrics:\n        - id: M-001\n          metric: unsourced_finding_counted_count\n          operator: \"==\"\n          threshold: 0\n          unit: count\n          verification: test/offline/test_task_contract.py::test_unretrieved_source_does_not_count\n    depends_on: []\n    safety_relevant: true\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: code analysis, no upstream issue. Team baseline of 2026-09-12, from a local trace\n      script that is not in the repository: a three-sentence question was split into parallel\n      tasks costing about 34,000 tokens; the budget field is where such over-delegation can be\n      limited later. Field names are proposals for the design review.\n\n  - id: REQ-002\n    title: No delegated research task shall be lost or silently treated as completed\n    type: invariant\n    problem: >-\n      supervisor_tools runs the researcher fan-out inside one try block whose handler tests\n      is_token_limit_exceeded(...) or True (deep_researcher.py L332-342). Every exception from\n      any researcher, such as a provider error, a network failure or an MCP error, therefore ends\n      the research phase as if it had finished, and the outer graph continues to\n      final_report_generation (L715). asyncio.gather (L305) re-raises the first exception, so\n      findings of siblings that succeed are discarded while those siblings keep running and\n      spending tokens. Delegations above max_concurrent_research_units are never run (L291-292)\n      and each receives an error string instead (L315-321). Delegations in the turn on which the\n      iteration cap is hit are never run either (L247, L255). The overflow string and the\n      compress_research placeholder \"Error synthesizing research report\" (L310, L582-585) are\n      stored as tool messages and read into notes by get_notes_from_tool_calls (utils.py\n      L599-601), so report generation receives failure text as findings.\n    statement: >-\n      Every delegated research task shall end with a task result as defined in REQ-001, and no\n      delegation shall be dropped: delegations above the concurrency limit shall be queued and\n      run, and a delegation left unrun because the research loop exits shall end failed with\n      reason not_run. An exception raised while a task runs, including a token or context limit\n      error, shall make only that task failed, with an error category and the error message,\n      shall keep the results of sibling tasks, and shall never on its own end the research\n      phase. The supervisor shall not continue or exit while any task it started is still\n      running. Failure or placeholder text shall never reach report generation as a finding.\n    owner: AlchemyHAN\n    contributors:\n      - centay\n    priority: must\n    priority_rationale: >-\n      This is the defect reported in upstream #283 and the direct cause of silently truncated\n      reports. Automatic retry and re-planning of failed tasks are left out of this delivery;\n      the supervisor may still re-delegate within max_researcher_iterations.\n    scope:\n      in_scope:\n        - Exception handling around the parallel researcher fan-out\n        - Queuing of delegations above the concurrency limit\n        - Joining of parallel researcher tasks\n        - Delegations left unrun when the research loop exits\n        - Separation of task failures from research findings in notes\n      out_of_scope:\n        - Errors of individual search or MCP tool calls inside researcher_tools (REQ-008)\n        - Token-limit recovery inside compress_research (REQ-005)\n        - Exit decision of the research loop (REQ-003)\n        - legacy/multi_agent.py, which was removed in commit a4d557a\n        - Automatic retry or re-planning of failed tasks\n    fit_criterion:\n      summary: >-\n        Under injected researcher failures every delegation ends with a result, no failure ends\n        the research phase, completed siblings are kept, no task is still running after the\n        join, and no failure text appears among the findings.\n      checks:\n        - id: C-001\n          description: >-\n            Given one delegation whose researcher raises RuntimeError, when supervisor_tools\n            runs, then it routes back to the supervisor rather than END and the task result is\n            failed with category runtime and the original error message.\n          verification: test/offline/test_failure_propagation.py::test_child_exception_becomes_failed_result\n          automated: true\n        - id: C-002\n          description: >-\n            Given two delegations where one researcher returns a finding and the other raises,\n            when supervisor_tools runs, then the finding is kept in the tool messages and\n            raw_notes and only the other task is failed.\n          verification: test/offline/test_failure_propagation.py::test_sibling_result_kept_on_failure\n          automated: true\n        - id: C-003\n          description: >-\n            Given a researcher that raises a recognised token-limit error, when supervisor_tools\n            runs, then the task result is failed with category token_limit and the research\n            phase does not end.\n          verification: test/offline/test_failure_propagation.py::test_token_limit_error_is_task_failure\n          automated: true\n        - id: C-004\n          description: >-\n            Given three delegations and a concurrency limit of one, when supervisor_tools runs,\n            then all three tasks are run and each ends with a task result.\n          verification: test/offline/test_failure_propagation.py::test_overflow_delegations_are_queued\n          automated: true\n        - id: C-005\n          description: >-\n            Given a final supervisor turn that holds two delegations when the iteration cap is\n            reached, when the loop exits, then both delegations end failed with reason not_run.\n          verification: test/offline/test_failure_propagation.py::test_delegations_left_at_exit_are_failed\n          automated: true\n        - id: C-006\n          description: >-\n            Given a fan-out where one researcher raises immediately while a sibling is still\n            running, when supervisor_tools returns, then no task it started is still pending.\n          verification: test/offline/test_failure_propagation.py::test_no_task_running_after_join\n          automated: true\n        - id: C-007\n          description: >-\n            Given one failed task and one task whose compression produced the placeholder text,\n            when the research phase ends, then notes contain only validated findings and both\n            failures appear only as failed task results.\n          verification: test/offline/test_failure_propagation.py::test_failure_text_not_in_notes\n          automated: true\n      metrics:\n        - id: M-001\n          metric: dropped_delegation_count\n          operator: \"==\"\n          threshold: 0\n          unit: count\n          verification: test/offline/test_failure_propagation.py\n        - id: M-002\n          metric: failure_text_in_notes_count\n          operator: \"==\"\n          threshold: 0\n          unit: count\n          verification: test/offline/test_failure_propagation.py::test_failure_text_not_in_notes\n    depends_on:\n      - REQ-001\n    safety_relevant: true\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: upstream issue #283, reported against commit 1f24f11, which is an ancestor of this\n      branch; src/open_deep_research is unchanged since then. Offline probes on 2026-11-10\n      reproduced every failure listed in the problem. Upstream #284 targets\n      legacy/multi_agent.py, which is not in this repository; the property it asks for, that\n      the supervisor converges only after every parallel branch has ended, is C-006. Design\n      decision: a researcher's token-limit error is a task failure and does not end the phase,\n      because it says nothing about the supervisor's own context; the upstream code ended the\n      phase on it. Proposed error categories are token_limit, runtime, not_run and\n      invalid_result.\n\n  - id: REQ-003\n    title: Research loop shall stop on a coverage check, not on the model's claim\n    type: invariant\n    problem: >-\n      supervisor_tools ends the research phase on three conditions only: the iteration cap, a\n      turn with no tool calls, or a ResearchComplete call (deep_researcher.py L246-262). Nothing\n      checks whether the research brief was answered, and the exit reason is not recorded. An\n      error in the supervisor's own model call (L214) is not handled and aborts the whole run.\n      In the team baseline of 2026-09-12 both test queries ran until the iteration cap and the\n      model never called ResearchComplete.\n    statement: >-\n      The research loop shall end only through a deterministic check of the validated task\n      results from REQ-001, and every exit shall record exactly one exit reason: covered when\n      coverage reaches the configured threshold, budget_exhausted when the iteration cap is\n      reached, stalled when two consecutive supervisor turns that do more than call think_tool\n      leave coverage unchanged, and failed when the supervisor's own model call fails after its\n      retries. When several conditions hold at once, they take precedence in that order.\n      Coverage is the share of required questions, across all delegated tasks, that have at\n      least one sourced finding. A ResearchComplete call or a turn without tool calls shall not\n      end the loop while coverage is below the threshold; the supervisor shall instead be told\n      which required questions remain unanswered.\n    owner: centay\n    priority: must\n    priority_rationale: >-\n      This is the orchestration half of the project's safety-relevant boundary: the model's\n      own claim of completion is not trusted. One configurable threshold is enough for this\n      delivery; per-query tuning of the threshold is deferred.\n    scope:\n      in_scope:\n        - Exit decision of the supervisor research loop\n        - Exit reason recorded in supervisor state\n        - Handling of ResearchComplete calls and turns without tool calls as requests\n        - Failure of the supervisor's own model call\n      out_of_scope:\n        - Stop conditions inside researcher_tools\n        - Failures of individual research tasks (REQ-002)\n        - How non-covered exits are reported to the caller (REQ-004)\n    fit_criterion:\n      summary: >-\n        Every research loop exits through the coverage check with exactly one recorded reason,\n        and a completion request below the threshold never ends the loop.\n      checks:\n        - id: C-001\n          description: >-\n            Given scripted results that answer every required question, when the turn ends,\n            then the loop exits with reason covered whether or not ResearchComplete was called.\n          verification: test/offline/test_research_termination.py::test_full_coverage_exits_covered\n          automated: true\n        - id: C-002\n          description: >-\n            Given coverage 0.5 and threshold 0.8, when the supervisor calls ResearchComplete,\n            then the loop continues and the next supervisor input lists the unanswered\n            questions.\n          verification: test/offline/test_research_termination.py::test_complete_below_threshold_is_refused\n          automated: true\n        - id: C-003\n          description: >-\n            Given two consecutive delegation turns that add no coverage, with a think_tool-only\n            turn between them, when the second delegation turn ends, then the loop exits with\n            reason stalled.\n          verification: test/offline/test_research_termination.py::test_turns_without_progress_exit_stalled\n          automated: true\n        - id: C-004\n          description: >-\n            Given coverage below the threshold when the iteration cap is reached, when the turn\n            ends, then the loop exits with reason budget_exhausted.\n          verification: test/offline/test_research_termination.py::test_iteration_cap_exits_budget_exhausted\n          automated: true\n        - id: C-005\n          description: >-\n            Given a supervisor model that raises on every retry, when the supervisor node runs,\n            then the loop exits with reason failed and the run does not abort with an unhandled\n            exception.\n          verification: test/offline/test_research_termination.py::test_supervisor_model_error_exits_failed\n          automated: true\n        - id: C-006\n          description: >-\n            Given the two baseline queries run against the live model, when each run ends, then\n            at least one run exits with reason covered and at most one hits the iteration cap;\n            the baseline was zero covered exits and two cap hits.\n          verification: test/live/test_research_termination_live.py::test_baseline_queries_exit_reasons\n          automated: false\n      metrics:\n        - id: M-001\n          metric: exit_without_single_reason_count\n          operator: \"==\"\n          threshold: 0\n          unit: count\n          verification: test/offline/test_research_termination.py\n        - id: M-002\n          metric: premature_complete_accepted_count\n          operator: \"==\"\n          threshold: 0\n          unit: count\n          verification: test/offline/test_research_termination.py::test_complete_below_threshold_is_refused\n    depends_on:\n      - REQ-001\n    safety_relevant: true\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: code analysis and the team's live baseline of 2026-09-12. Proposed default\n      threshold 0.8, configurable, to be confirmed in the design review. The detailed rule is\n      proposed as INV-003 in docs/architecture/invariants.md. How a non-covered exit is reported\n      to the caller is specified in REQ-004.\n\n  - id: REQ-004\n    title: Run output shall state whether research was complete, partial or failed\n    type: functional\n    problem: >-\n      The outer graph routes research_supervisor to final_report_generation unconditionally\n      (deep_researcher.py L715) and its output has no status field, so a caller can tell a\n      complete run from a failed one only by reading the report. final_report_generation\n      returns its own errors as report text (L669-674, L684-697) and the run still ends\n      normally. On a token-limit error it cuts findings from the end (L676-682), so findings of\n      later tasks are dropped without notice. The report-writing model cannot be relied on to\n      disclose missing research.\n    statement: >-\n      The final output of every run shall include a research outcome and the list of failed\n      tasks with their reasons. The outcome shall be failed when the research loop exits with\n      reason failed, when no validated finding exists or when report generation fails; complete\n      when the exit reason is covered, every task result is complete and no finding was left\n      out of the report; and partial otherwise. When the outcome is partial, the system, not the\n      report model, shall append a limitations section that names each failed or partial task,\n      each unanswered required question and any findings left out. When the outcome is failed,\n      the final report shall be empty and error text shall appear only in the failure fields.\n    owner: AlchemyHAN\n    priority: must\n    priority_rationale: >-\n      Without a caller-visible outcome the failures recorded under REQ-002 and REQ-003 stay\n      internal and the user still receives a normal-looking report, which is the harm described\n      in upstream #283. Presentation of the outcome in a UI is left out of this delivery.\n    scope:\n      in_scope:\n        - Research outcome and failed-task list in the output of the outer graph\n        - Limitations section appended by the system to partial reports\n        - Runs that end without any validated finding\n        - Report-generation errors and findings truncated to fit the report model\n      out_of_scope:\n        - Recording of individual task failures (REQ-002)\n        - Exit reasons of the research loop (REQ-003)\n        - Report format and citation rules other than the limitations section (REQ-006)\n        - Front-end or LangGraph Studio presentation of the outcome\n        - The clarification path that ends with a question to the user\n    fit_criterion:\n      summary: >-\n        Every scripted run returns the outcome its exit reason and task results imply, every\n        partial report carries the system-added limitations section, and no failed run returns\n        error text as a report.\n      checks:\n        - id: C-001\n          description: >-\n            Given a scripted run whose tasks are all complete and whose loop exits covered, when\n            the graph finishes, then the outcome is complete, the failed-task list is empty and\n            the report has no limitations section.\n          verification: test/offline/test_run_outcome.py::test_covered_run_is_complete\n          automated: true\n        - id: C-002\n          description: >-\n            Given a two-task run in which one task fails, when the graph finishes, then the\n            outcome is partial, the failed-task list names that task and its reason, and the\n            limitations section names it although the fake report model never mentions it.\n          verification: test/offline/test_run_outcome.py::test_failed_task_makes_run_partial\n          automated: true\n        - id: C-003\n          description: >-\n            Given a run whose tasks are all complete but whose loop exits stalled or\n            budget_exhausted, when the graph finishes, then the outcome is partial.\n          verification: test/offline/test_run_outcome.py::test_non_covered_exit_is_partial\n          automated: true\n        - id: C-004\n          description: >-\n            Given a run in which no validated finding exists, when the graph finishes, then the\n            outcome is failed, the report model is not called and final_report is empty.\n          verification: test/offline/test_run_outcome.py::test_no_finding_run_is_failed\n          automated: true\n        - id: C-005\n          description: >-\n            Given a report model that raises a non-token-limit error, when report generation\n            runs, then the outcome is failed with that reason and final_report is empty.\n          verification: test/offline/test_run_outcome.py::test_report_error_run_is_failed\n          automated: true\n        - id: C-006\n          description: >-\n            Given findings that must be truncated to fit the report model, when the report is\n            generated, then the outcome is partial and the limitations section states that\n            findings were left out.\n          verification: test/offline/test_run_outcome.py::test_truncated_findings_make_run_partial\n          automated: true\n      metrics:\n        - id: M-001\n          metric: false_complete_outcome_count\n          operator: \"==\"\n          threshold: 0\n          unit: count\n          verification: test/offline/test_run_outcome.py\n    depends_on:\n      - REQ-002\n      - REQ-003\n    safety_relevant: true\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: upstream issues #283 and #284, both of which name a normal-looking but incomplete\n      report as the impact. The output field names research_outcome and failed_tasks are\n      proposals.\n\n  - id: REQ-005\n    title: Token-limit recovery in compression shall discard the oldest context first\n    type: invariant\n    problem: >-\n      On a token-limit error compress_research calls remove_up_to_last_ai_message\n      (deep_researcher.py L568-571, utils.py L848-866), which cuts the history at the last AI\n      message and so drops that message, the tool results after it and the compression\n      instruction appended at L538. The call-site comment says older messages are removed,\n      while the helper's docstring says recent context is removed. The error is classified\n      with research_model (L569) although the call used compression_model, so a token-limit\n      error from a compression model of another provider is not recognised and the same\n      request is retried unchanged. After three attempts the node returns the placeholder\n      \"Error synthesizing research report\" in place of a summary (L582-585).\n    statement: >-\n      When compression exceeds the model's token limit, the system shall free context by\n      removing whole research turns, each an AI message together with its tool results,\n      starting from the oldest, and shall keep the research topic, the compression instruction,\n      the latest AI turn and the tool results that follow it. It shall never remove the latest\n      turn to recover and shall never keep a tool result without the AI message that requested\n      it. Token-limit errors shall be recognised for the model that made the call. When nothing\n      more can be removed and the limit is still exceeded, the task shall end with a failed\n      result of category token_limit instead of a summary.\n    owner: BroZhai\n    priority: must\n    priority_rationale: >-\n      Every token-limit recovery silently loses the newest research while the run still\n      produces a normal report. Correct recovery takes precedence over tuning the compression\n      prompt, which is deferred.\n    scope:\n      in_scope:\n        - Token-limit branch of compress_research\n        - Message trimming helper used by that branch\n        - Token-limit classification for the compression call\n        - Task result when the limit cannot be met\n      out_of_scope:\n        - Compression prompt wording and summarisation style\n        - Model selection and token-limit configuration\n        - Supervisor and researcher graph topology\n        - Token-limit handling in final_report_generation (REQ-004)\n    fit_criterion:\n      summary: >-\n        Across token-limit retries the newest turn always survives, space is reclaimed from the\n        oldest whole turns, and an unreducible history ends as a failed task, not as text.\n      checks:\n        - id: C-001\n          description: >-\n            Given a history of topic, three AI turns with tool results and the compression\n            instruction, and a model that rejects the request until two turns are removed, when\n            compression runs, then the two oldest turns are removed and the topic, the latest\n            turn with its tool results and the instruction are kept.\n          verification: test/offline/test_context_compaction.py::test_oldest_turns_removed_first\n          automated: true\n        - id: C-002\n          description: >-\n            Given any history trimmed after a token-limit error, when the trimmed history is\n            inspected, then every tool result follows the AI message that requested it.\n          verification: test/offline/test_context_compaction.py::test_no_orphan_tool_messages\n          automated: true\n        - id: C-003\n          description: >-\n            Given an OpenAI research model and an Anthropic compression model that raises an\n            Anthropic token-limit error, when compression runs, then the error is recognised and\n            the history is trimmed before the retry.\n          verification: test/offline/test_context_compaction.py::test_classification_uses_compression_model\n          automated: true\n        - id: C-004\n          description: >-\n            Given a history of only the topic, one AI turn and the instruction that still\n            exceeds the limit, when compression runs, then the task ends failed with category\n            token_limit and no placeholder text is returned as a summary.\n          verification: test/offline/test_context_compaction.py::test_unreducible_history_ends_failed\n          automated: true\n      metrics:\n        - id: M-001\n          metric: latest_turn_preservation_rate\n          operator: \"==\"\n          threshold: 1.0\n          unit: ratio\n          verification: test/offline/test_context_compaction.py::test_oldest_turns_removed_first\n        - id: M-002\n          metric: orphan_tool_message_count\n          operator: \"==\"\n          threshold: 0\n          unit: count\n          verification: test/offline/test_context_compaction.py::test_no_orphan_tool_messages\n    depends_on:\n      - REQ-001\n    safety_relevant: true\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: upstream issue #252, still open. A history without any AI message cannot be\n      reduced and is therefore covered by C-004.\n\n  - id: REQ-006\n    title: Research prompts shall specify one consistent citation format\n    type: invariant\n    problem: >-\n      compress_research_system_prompt asks for a bold \"List of All Relevant Sources\" label in\n      its output format (prompts.py L209) while its citation rules require a \"### Sources\"\n      heading (L212-219); this is upstream #232, whose fix PR #301 was closed without being\n      merged. final_report_generation_prompt asks for sources in \"[Title](URL) format\" (L251)\n      and later for numbered citations with a \"[n] Source Title: URL\" list (L298-307). Each\n      researcher numbers its own sources from 1, so the notes given to the report writer reuse\n      the same numbers for different URLs. Conflicting instructions lead to mixed citation\n      styles in reports.\n    statement: >-\n      The compression prompt and the final report prompt shall each specify exactly one\n      citation format, and it shall be the same format: numbered inline citations [n] and a\n      closing \"### Sources\" section that lists each cited URL once as \"[n] Title: URL\",\n      numbered without gaps. The final report prompt shall instruct the model to renumber the\n      citations of all findings into one sequence, so that each URL has one number in the\n      report.\n    owner: NoPumpkinz\n    priority: should\n    priority_rationale: >-\n      Mixed citation styles reduce trust in a report but do not lose research content, and the\n      fix is limited to prompt text. Deterministic validation of citations in generated reports\n      is deferred.\n    scope:\n      in_scope:\n        - Citation and sources instructions in compress_research_system_prompt\n        - Citation and sources instructions in final_report_generation_prompt\n      out_of_scope:\n        - Other prompt content\n        - Deterministic checking of citations in generated reports\n        - Models, search APIs and UI rendering of the report\n    fit_criterion:\n      summary: >-\n        Both prompts state one identical numbered citation format with no competing\n        instruction, and live reports follow it.\n      checks:\n        - id: C-001\n          description: >-\n            Given compress_research_system_prompt, when its text is inspected, then it contains\n            exactly one sources-section instruction, the \"### Sources\" heading, and no\n            competing label.\n          verification: test/offline/test_prompt_citation_contract.py::test_compression_prompt_has_single_sources_format\n          automated: true\n        - id: C-002\n          description: >-\n            Given final_report_generation_prompt, when its text is inspected, then it requires\n            numbered citations, contains no \"[Title](URL)\" instruction and asks for one\n            renumbered sequence across all findings.\n          verification: test/offline/test_prompt_citation_contract.py::test_report_prompt_has_single_citation_format\n          automated: true\n        - id: C-003\n          description: >-\n            Given both prompts, when their sources-entry formats are extracted, then the two\n            formats are identical.\n          verification: test/offline/test_prompt_citation_contract.py::test_prompts_share_citation_format\n          automated: true\n        - id: C-004\n          description: >-\n            Given the two baseline queries run against the live model, when the reports are\n            produced, then every inline citation is a number with exactly one matching entry in\n            the Sources section.\n          verification: test/live/test_report_citations_live.py::test_reports_use_numbered_citations\n          automated: false\n    depends_on: []\n    safety_relevant: false\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: upstream issue #232 and PR #301 (closed, unmerged). The numbered format was\n      chosen because three of the four existing citation instructions already use it.\n      safety_relevant is false because the change only alters prompt text and adds no\n      deterministic check on model output.\n\n  - id: REQ-007\n    title: Search provider setup shall be documented and validated before research\n    type: functional\n    problem: >-\n      Upstream #250 reports that it is unclear when the agent searches and how to use another\n      or a self-hosted search provider. search_api offers Tavily, OpenAI native search,\n      Anthropic native search or none (configuration.py L11-17, L78-93). The native options\n      only work with a research model of the same provider, which the UI states only as a note\n      and nothing checks. Custom providers can be added only as MCP tools (utils.py L569-597),\n      and the README just points to the search_api and mcp_config fields (README.md L77). A\n      wrong combination surfaces only after research has started, when the model API rejects\n      the tool. With search_api none and no MCP tool the researcher still runs, because its\n      tool list always holds ResearchComplete and think_tool (utils.py L579), so research\n      finishes with no search at all and no error.\n    statement: >-\n      The documentation shall explain that the researcher model decides when to search, how to\n      select each built-in search provider, which research models each native provider\n      requires, and how to add a custom or self-hosted search provider as an MCP tool. Before\n      any research starts, the system shall reject a configuration that names an unsupported\n      provider, pairs a native search provider with a research model of another provider, or\n      leaves the researcher with no search tool and no MCP tool, with an error that names the\n      setting to change.\n    owner: sszfot\n    priority: must\n    priority_rationale: >-\n      This answers upstream #250 directly and moves configuration errors from the middle of a\n      run to start-up, where they cannot be mistaken for research results. New provider\n      integrations are deferred.\n    scope:\n      in_scope:\n        - Documentation of search behaviour and provider configuration\n        - Documentation of custom and self-hosted search through MCP\n        - Validation of the search configuration before research starts\n      out_of_scope:\n        - Fallback between search providers (REQ-008)\n        - New built-in provider integrations\n        - Provider selection by cost or latency\n    fit_criterion:\n      summary: >-\n        Every invalid search configuration is rejected before any model or search call, and a\n        reader can set up each built-in provider and an MCP search server from the docs alone.\n      checks:\n        - id: C-001\n          description: >-\n            Given search_api anthropic and research_model openai:gpt-4.1, when the graph\n            starts, then a validation error naming both settings is raised before any model or\n            search call.\n          verification: test/offline/test_search_configuration.py::test_native_search_model_mismatch_rejected\n          automated: true\n        - id: C-002\n          description: >-\n            Given search_api none and no MCP configuration, when the graph starts, then a\n            validation error is raised before any research.\n          verification: test/offline/test_search_configuration.py::test_no_search_tool_rejected\n          automated: true\n        - id: C-003\n          description: >-\n            Given an unsupported search_api value, when the graph starts, then a validation\n            error lists the supported values.\n          verification: test/offline/test_search_configuration.py::test_unsupported_provider_rejected\n          automated: true\n        - id: C-004\n          description: >-\n            Given search_api tavily with a Tavily key, when the researcher tools are assembled,\n            then they include the web_search tool and no validation error is raised.\n          verification: test/offline/test_search_configuration.py::test_valid_tavily_configuration_accepted\n          automated: true\n        - id: C-005\n          description: >-\n            Given the README, when a reviewer follows it without reading source code, then they\n            can configure each built-in provider and an MCP search server and find the required\n            credentials.\n          verification: docs/review-memo.md (search provider configuration review)\n          automated: false\n    depends_on: []\n    safety_relevant: false\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: upstream issue #250, still open. The supported provider set is the existing\n      SearchAPI enum.\n\n  - id: REQ-008\n    title: Search shall fall back to configured alternative sources on failure\n    type: functional\n    problem: >-\n      A failed search is never retried with another source. An exception from Tavily\n      (utils.py L138-170) reaches execute_tool_safely (deep_researcher.py L427-432), which hands\n      the researcher model the text \"Error executing tool: ...\" and nothing else. Upstream #250\n      asks for fallback to another API. Only Tavily and MCP tools run as client-side tools; the\n      OpenAI and Anthropic searches run inside the model call and cannot be invoked as a\n      substitute after a failure.\n    statement: >-\n      The system shall accept an ordered list of fallback search sources, each being Tavily or a\n      configured MCP search tool. When a search fails with an eligible error, namely a timeout,\n      a connection failure, a rate limit, a provider server error or a rejected credential, the\n      system shall try the next source in order until one succeeds, and shall use a successful\n      result the same way whichever source returned it. A search that returns no hits is a\n      success and shall not trigger fallback, and an ineligible error shall be returned without\n      fallback. When every source fails, the researcher shall receive an explicit search failure\n      that lists each source tried and its error and that cannot be mistaken for an empty\n      result.\n    owner: sszfot\n    priority: should\n    priority_rationale: >-\n      Fallback is a team-proposed reliability improvement beyond what #250 asks. It can be\n      deferred because REQ-007 already makes provider setup clear and a failed search already\n      reaches the researcher as an error. Native model search as a fallback, parallel search\n      across providers and cost-based selection are excluded.\n    scope:\n      in_scope:\n        - Configuration of an ordered fallback list\n        - Fallback on eligible search errors\n        - Explicit failure when every source fails\n      out_of_scope:\n        - OpenAI or Anthropic native search in the fallback chain\n        - New built-in provider integrations\n        - Parallel search across providers\n        - Recovery from invalid credentials\n        - Supervisor delegation and termination (REQ-001 to REQ-003)\n    fit_criterion:\n      summary: >-\n        Eligible failures fall through the configured sources in order, empty results and\n        ineligible errors do not, and an all-failed search is explicit.\n      checks:\n        - id: C-001\n          description: >-\n            Given a primary source that times out and a working fallback, when a search is\n            requested, then the primary is tried once, the fallback is tried next and its\n            result is returned.\n          verification: test/offline/test_search_fallback.py::test_primary_failure_uses_fallback\n          automated: true\n        - id: C-002\n          description: >-\n            Given three sources where the first two fail with eligible errors, when a search is\n            requested, then the sources are tried in the configured order and the third\n            source's result is returned.\n          verification: test/offline/test_search_fallback.py::test_fallbacks_follow_configured_order\n          automated: true\n        - id: C-003\n          description: >-\n            Given every source failing with eligible errors, when a search is requested, then\n            the researcher receives a search failure naming each source and its error, and no\n            result is fabricated.\n          verification: test/offline/test_search_fallback.py::test_all_sources_fail_explicitly\n          automated: true\n        - id: C-004\n          description: >-\n            Given a primary source that returns no hits without error, when a search is\n            requested, then the empty result is returned and no fallback is tried.\n          verification: test/offline/test_search_fallback.py::test_empty_result_does_not_trigger_fallback\n          automated: true\n        - id: C-005\n          description: >-\n            Given a primary source that rejects the query as malformed, when a search is\n            requested, then the error is returned and no fallback is tried.\n          verification: test/offline/test_search_fallback.py::test_ineligible_error_does_not_trigger_fallback\n          automated: true\n    depends_on:\n      - REQ-007\n    safety_relevant: false\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: upstream issue #250 and the team's division-of-labour plan. The classification of\n      eligible errors is to be agreed in the design review.\n\n  - id: REQ-009\n    title: Evaluator scores shall be valid, bounded and based on their stated inputs\n    type: invariant\n    problem: >-\n      The evaluators in test/evaluators.py produce unreliable scores. CORRECTNESS_PROMPT\n      (test/prompts.py L95-104) contains no placeholder at all, so eval_correctness formats the\n      question, report and reference answer into nothing and the judge never sees them\n      (test/evaluators.py L195-219). Ratings declared as integers from 1 to 5 are divided by 5\n      without a range check (L90-98, L140, L179, L219, L312), so an out-of-range rating gives a\n      score outside 0 to 1. eval_groundedness divides by the number of extracted claims\n      (L268-269) and raises ZeroDivisionError when no claim is extracted. These faults affect\n      the benchmark run and any evaluation of an existing report alike.\n    statement: >-\n      Each evaluator shall send the judge model every input its metric is defined over: the\n      question, the report and, where the metric uses them, the reference answer, the research\n      brief or the evidence. Every metric result shall state the metric name, a status, a score\n      and a reason. A score shall be produced only from an integer rating from 1 to 5,\n      normalised as rating divided by 5, or from a groundedness ratio over at least one claim.\n      In every other case, including a missing input, an invalid rating, no extracted claim or\n      an evaluator exception, the metric shall be not_evaluable with a null score, and the\n      remaining metrics shall still be evaluated.\n    owner: DopplerXD\n    priority: must\n    priority_rationale: >-\n      Today correctness is scored without the report and some runs crash, so no evaluation\n      result, including those of REQ-010, can be trusted until this holds. Score-based\n      acceptance thresholds are deferred.\n    scope:\n      in_scope:\n        - Inputs each evaluator sends to the judge model\n        - Validation and normalisation of judge ratings\n        - not_evaluable results for missing inputs, empty claims and evaluator errors\n      out_of_scope:\n        - The evaluation-only entry (REQ-010)\n        - Judge model choice and rubric wording\n        - Score-based acceptance thresholds\n    fit_criterion:\n      summary: >-\n        Every metric result is either a score in the range 0 to 1 derived from valid judge\n        output and complete inputs, or not_evaluable with a reason, and one failing metric\n        never aborts the others.\n      checks:\n        - id: C-001\n          description: >-\n            Given distinct question, report and reference-answer markers, when correctness is\n            evaluated, then all three appear in the judge request; given a research brief or\n            evidence, then completeness or groundedness respectively receives it.\n          verification: test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs\n          automated: true\n        - id: C-002\n          description: >-\n            Given ratings 1 and 5, when they are normalised, then the scores are 0.2 and 1.0;\n            given 0, 6, a boolean, a string, a fraction or a non-finite number, then the metric\n            is not_evaluable with a reason and a null score.\n          verification: test/offline/test_evaluator_validity.py::test_ratings_are_validated\n          automated: true\n        - id: C-003\n          description: >-\n            Given a missing reference answer, research brief or evidence, when the evaluators\n            run, then each metric that needs it is not_evaluable and the other metrics are\n            scored.\n          verification: test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable\n          automated: true\n        - id: C-004\n          description: >-\n            Given no extracted claim or an evaluator that raises, when the evaluators run, then\n            the affected metric is not_evaluable and the others are scored; given two supported\n            claims out of four, then groundedness is 0.5.\n          verification: test/offline/test_evaluator_validity.py::test_groundedness_and_errors\n          automated: true\n      metrics:\n        - id: M-001\n          metric: out_of_range_score_count\n          operator: \"==\"\n          threshold: 0\n          unit: count\n          verification: test/offline/test_evaluator_validity.py::test_ratings_are_validated\n    depends_on: []\n    safety_relevant: true\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: analysis of the evaluators while answering upstream issue #234, at commit\n      1b7d2e8, where the package was still named tests/ (renamed test/ in a4d557a). The\n      missing placeholders in CORRECTNESS_PROMPT were confirmed on 2026-11-11.\n\n  - id: REQ-010\n    title: An existing report shall be evaluable without running research\n    type: functional\n    problem: >-\n      Upstream #234 asks how to evaluate a report that was already generated. run_evaluate.py\n      accepts only a LangSmith dataset, and its target compiles and invokes the full research\n      graph for every example (test/run_evaluate.py L32-61), so the only way to score a report\n      is to generate a new one.\n    statement: >-\n      The system shall provide a documented evaluation-only entry that takes an existing report\n      and its question, with an optional reference answer, research brief and evidence, and\n      returns the metric results defined in REQ-009 for that exact report. The entry shall not\n      run the research graph, call a search provider or generate a replacement report, and it\n      shall reject a blank report or question before calling any evaluator.\n    owner: DopplerXD\n    priority: must\n    priority_rationale: >-\n      This is the capability upstream #234 asks for. Automated acceptance thresholds and\n      revision of the evaluated report are deferred.\n    scope:\n      in_scope:\n        - Evaluation-only entry for an existing report\n        - Input validation of the entry\n        - Documentation of the entry\n      out_of_scope:\n        - Evaluator inputs and score validity (REQ-009)\n        - Custom report template generation\n        - Score-based acceptance thresholds\n        - Rewriting the report or repeating research\n    fit_criterion:\n      summary: >-\n        A supplied report is scored as given, with zero research or search calls, and blank\n        input is rejected before any evaluator runs.\n      checks:\n        - id: C-001\n          description: >-\n            Given an existing report and question, when they are submitted through the entry,\n            then the judge requests contain both unchanged, research-graph and search call\n            counts are zero, and the result identifies the supplied report.\n          verification: test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research\n          automated: true\n        - id: C-002\n          description: >-\n            Given a blank report or a blank question, when it is submitted through the entry,\n            then a validation error is returned and no evaluator is called.\n          verification: test/offline/test_report_evaluation_entry.py::test_blank_input_rejected\n          automated: true\n        - id: C-003\n          description: >-\n            Given the README, when a reviewer follows it, then they can evaluate a report file\n            and read the per-metric results without modifying source code.\n          verification: docs/review-memo.md (report evaluation entry review)\n          automated: false\n    depends_on:\n      - REQ-009\n    safety_relevant: false\n    status: approved\n    version: \"1.1\"\n    updated_at: \"2026-11-11\"\n    notes: >-\n      Source: https://github.com/langchain-ai/open_deep_research/issues/234, still open. Score\n      validity is specified in REQ-009.\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/architecture/permission-model.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# Coding-Agent Permission Model\n\n> **Purpose:** What each coding-agent role may read, write and run, what needs the human's confirmation, and how a task receives its permissions.\n> **Authoritative for:** roles, paths, tools and approval delegation. Behaviour rules are in `.opencode/rules.md`; the workflow is in `Prompt.md`.\n> **Maintained by:** humans.\n> **Last updated:** 2026-11-12\n\n## 1. Principles\n\nEvery action falls into one of three tiers:\n\n| Tier | Effect | Used for |\n|---|---|---|\n| **Allow** | Runs without asking | Routine work of the role: reading, searching, editing, running checks, committing, read-only web and documentation lookups (`webfetch`, `websearch`, Context7) |\n| **Ask** | The human confirms each time | Legitimate but risky actions: pushing, rewriting local history, changing dependencies, raw network commands (`curl`, `wget`), unapproved MCP tools, deleting files, editing governance documents |\n| **Deny** | Never runs, even if the human confirms | Reading secrets, changing permissions or approval records, force-pushing, `sudo`, and edits that break role separation |\n\nThe configuration controls tool access; it does not isolate the process. Anything an agent changes appears in the PR diff, and review is the final control.\n\n## 2. Roles\n\n| Role | Job | Edits | Commands without asking (§4) |\n|---|---|---|---|\n| **Plan** | Software architecture: EVAL entries, ADRs, module sections | SA documents (§3) and other documentation; never source, tests or `scripts/` | Read-only, checks, Git add and commit |\n| **Test Author** | Tests that fail on the baseline | `test/offline/`, `test/live/` and documentation; never source, `scripts/` or other code under `test/` | Read-only, checks, `ruff format` on tests, Git add, commit and switch |\n| **Build** | Implementation that makes the approved tests pass | Source, `scripts/`, evaluation code under `test/` and documentation, within the approval record (§5); never `test/offline/` or `test/live/` | Read-only, checks, `ruff format` on `src/`, Git add, commit and switch |\n| **Verify** | Independent verification | Documentation, including its reports in `docs/test-reports/`; never source, tests or `scripts/` | Read-only, checks, Git add and commit |\n\nTest Author and Build never edit each other's files, so an implementation cannot pass by changing its tests. Edits to governance documents and dependency files ask for every role; edits to SA documents ask for every role except Plan (§3). All roles may read the whole repository except secrets, search with `glob`, `grep`, `list` and `lsp`, and delegate searches to the read-only `explore` sub-agent.\n\n## 3. Path Ownership\n\n**SA documents:** `docs/architecture/*` except `permission-model.md`, plus `docs/code-governance/structural-constraints.md` and `verification-constraints.md`. Plan writes them freely during software architecture; Test Author, Build and Verify edit them only when the human confirms, so implementation cannot change the architecture silently. The ADR template `adr/000-template.md` is not edited by agents.\n\n**Governance documents (human-owned):** `AGENTS.md`, `Prompt.md`, `.agent/*`, `.github/*`, `docs/req/*`, `docs/architecture/permission-model.md`, `docs/code-governance/mcp-tool-manifest.md`, `docs/ai-use-log.yaml`, `docs/review-memo.md`, `docs/bug-diary.md`, `docs/debt-register.md`. **Dependency files:** `pyproject.toml`, `uv.lock`. Agents edit these only when the human confirms; the change still goes through PR review.\n\n**Never editable by agents:** `.opencode/*`, `opencode.json*` and `docs/approvals/*`, so that no agent can widen its own permissions or forge an approval.\n\n**Secrets:** `.env*` (except `.env.example`) and `.git/*` are never read, through the read tool or through a command.\n\n## 4. Commands\n\nRules for the `bash` tool. A command matching none of the rows asks the human.\n\n| Commands | Plan | Test Author | Build | Verify |\n|---|---|---|---|---|\n| Read-only: `ls`, `pwd`, `cat`, `head`, `tail`, `wc`, `rg`, `grep`, `find`, `tree` | allow | allow | allow | allow |\n| Read-only Git: `status`, `diff`, `log`, `show`, `branch`, `blame` | allow | allow | allow | allow |\n| Checks: `uv sync`, `uv run pytest`, `uv run ruff check`, `uv run mypy`, `uv run python scripts/validate_requirements.py` | allow | allow | allow | allow |\n| `git add`, `git commit` | allow | allow | allow | allow |\n| `uv run ruff format` | ask | allow on `test/offline`, `test/live`; ask elsewhere | allow on `src`; ask elsewhere | ask |\n| `git switch` | ask | allow | allow | ask |\n| `git push`, `git reset`, `git rebase`, `git checkout`, `git stash` | ask | ask | ask | ask |\n| `uv add`, `uv remove`, `pip install`, `curl`, `wget`, `rm`, `sed -i`, shell redirection `>` | ask | ask | ask | ask |\n| Force-push (`push --force`, `push -f`), `sudo`, anything touching `.env*`, `.opencode/`, `opencode.json` or `docs/approvals/` | deny | deny | deny | deny |\n\nAsk and deny rules match anywhere in the command, so `git commit -m x && git push` asks and `x && git push --force` is denied.\n\n**Other tools:** `question`, `todowrite`, `webfetch`, `websearch` and the tools of approved MCP servers are allowed; other MCP tools, skills and directories outside the repository ask; sub-agents other than `explore` are denied. `curl` and `wget` ask because, unlike the read-only web tools, they can send data out. MCP servers are approved in `docs/code-governance/mcp-tool-manifest.md` and configured in `.opencode/permissions.jsonc`.\n\n## 5. Approval and Permission Delegation\n\n`docs/approvals/<task-id>.md` is written by the human only and records two gates (`Prompt.md` §4, §6):\n\n| Gate | Recorded fields |\n|---|---|\n| Gate 1 — SA Review | SA review record (`SA-NNN` in `docs/review-memo.md`), accepted ADRs, approver, date |\n| Gate 2 — Tests | Approved test commit, approver, date |\n\nBuild implements the accepted ADR, starting from the approved test commit; the PR review compares the diff with the ADR's components and implementation steps. An architecture change needs a new SA Review (`Prompt.md` §10), and a change to an approved test invalidates Gate 2. No configuration change or session restart is needed for either gate.\n\n## 6. Configuration and Acceptance\n\n**Configuration.** `.opencode/permissions.jsonc` holds the rules. It defines the `plan`, `test-author`, `build` and `verify` agents and the read-only `explore` sub-agent, configures the approved MCP servers, makes `plan` the default agent, and denies everything to agents it does not define. OpenCode does not load a file named `permissions.jsonc`; `.opencode/opencode.jsonc` is a symlink to it, so edit only `permissions.jsonc` and keep the symlink. On Windows, clone with `core.symlinks=true`.\n\n**Merging.** A member's global OpenCode configuration and plugins merge with the project configuration. Work only in the `plan`, `test-author`, `build` and `verify` agents and do not start OpenCode with `--auto`, which approves every *ask*.\n\n**Acceptance.** On OpenCode 2.2.7 (2026-11-12), `opencode debug config` showed that `.opencode/opencode.jsonc` is loaded, and the rules resolved by `opencode debug agents` were evaluated against 83 cases covering every tier for every role: reads and secret reads, SA-document, governance, source and test edits per role, the Test Author and Build separation, web, Context7 and unapproved MCP tools, permission and approval tampering through the edit tool and the shell, routine commands, push, reset, rebase, dependency and network commands, force-push, chained commands, sub-agents and undefined agents. Result: **PASS, 83/83**. OpenCode resolves the `bash` key to the action `shell` and `task` to `subagent`.\n"
    }
  ]
}
```

### Event 4 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/architecture/architecture-blueprint.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# Architecture Blueprint\n\n> **Purpose:** The system-level SA Blueprint (course deliverable D2.1): components and their responsibilities, interfaces, dependencies, data flow and deterministic boundaries.\n> **Authoritative for:** architecture, the module list (§4), dependency exceptions and deterministic boundaries. Changed only through an accepted ADR.\n> **Maintained by:** the integrator, from the ADRs and module sections, before SA Review (`Prompt.md` §4).\n> **Status:** Skeleton. *TBD* sections are filled at integration; items marked *Proposed* are not binding.\n> **Last updated:** 2026-11-12\n\n## 1. Goals and Non-Goals\n\nThe goals are the requirements in `docs/req/requirements.yaml`; the non-goals are their `out_of_scope` entries. This document does not restate them.\n\n## 2. Stakeholders and System Context\n\n*TBD.*\n\n## 3. Baseline System\n\nOpen Deep Research is three LangGraph graphs in `src/open_deep_research/deep_researcher.py`:\n\n| Graph | State | Flow |\n|---|---|---|\n| `deep_researcher` (top level) | `AgentState` | `clarify_with_user` → `write_research_brief` → `research_supervisor` → `final_report_generation`; `clarify_with_user` may end early with a question |\n| supervisor subgraph (the `research_supervisor` node) | `SupervisorState` | `supervisor` ⇄ `supervisor_tools`; `supervisor_tools` fans out to researcher subgraphs and decides when research ends |\n| researcher subgraph | `ResearcherState` → `ResearcherOutputState` | `researcher` ⇄ `researcher_tools` → `compress_research` |\n\nShared modules: `state.py` (graph state and structured outputs), `configuration.py` (runtime `Configuration`, `SearchAPI`, `MCPConfig`), `prompts.py` (prompt templates), `utils.py` (tools, search, MCP loading, model and key helpers). This topology stays unchanged unless an ADR changes it (`structural-constraints.md` §2).\n\n## 4. Components\n\n**Accepted (2026-10-13):** graph nodes stay thin, and each architectural element is one extension module owned by one person.\n\nModule names below are used by every other architecture document. Final paths and responsibilities are fixed by each module's ADR.\n\n| Module | Path (*Proposed*) | Requirements | Responsibility |\n|---|---|---|---|\n| orchestration | `src/open_deep_research/orchestration/` | REQ-001, REQ-003 | Task contract, delegation, termination |\n| delivery | `src/open_deep_research/delivery/` | REQ-002, REQ-004 | Task failure handling, run outcome |\n| context | `src/open_deep_research/context/` | REQ-005 | Context trimming during compression |\n| citations | `src/open_deep_research/citations/` | REQ-006 | Citation format |\n| search | `src/open_deep_research/search/` | REQ-007, REQ-008 | Search configuration validation, fallback |\n| evaluation | `test/evaluation/` | REQ-009, REQ-010 | Evaluator validity, evaluation-only entry |\n\n## 5. Interfaces\n\n*TBD.* One row per interface that crosses a module boundary.\n\n| Interface | Provided by | Used by | Signature or type | Defined in |\n|---|---|---|---|---|\n| | | | | ADR-NNN |\n\n## 6. Dependencies\n\nDependency direction: `structural-constraints.md` §5. Exceptions, each justified by an ADR:\n\n| From | To | Reason | ADR |\n|---|---|---|---|\n| `utils.py` | `search/` | `get_all_tools()` assembles search tools (*Proposed*) | TBD |\n\n## 7. Data Flow\n\n*TBD.* How a request, the research brief, task specifications and results, notes and the final report move through the components.\n\n## 8. Deterministic Boundaries\n\nDecisions where the model's output is input and deterministic code decides (`structural-constraints.md` §7). *Proposed*, from the requirements marked `safety_relevant: true`:\n\n| Decision | Requirements | Module | Enforcing component | ADR |\n|---|---|---|---|---|\n| Task status from sourced findings | REQ-001 | orchestration | TBD | TBD |\n| Research termination and exit reason | REQ-003 | orchestration | TBD | TBD |\n| Task failure, queuing and join | REQ-002 | delivery | TBD | TBD |\n| Run outcome and limitations section | REQ-004 | delivery | TBD | TBD |\n| Message eviction during compression | REQ-005 | context | TBD | TBD |\n| Evaluator score validity | REQ-009 | evaluation | TBD | TBD |\n\n## 9. State and Data\n\n*TBD;* integrated from `memory-design.md`.\n\n## 10. Failure Handling\n\n*TBD;* integrated from `runtime-policy-catalog.md` and `invariants.md`.\n\n## 11. Decisions and Open Proposals\n\n| # | Proposal | Status |\n|---|---|---|\n| 1 | Thin graph nodes, one extension module per owner | Accepted 2026-10-13 |\n| 2 | Python version | Resolved 2026-11-11: Python 3.12 everywhere (`.python-version`, CI, `langgraph.json`) |\n| 3 | Move runtime prompts from `prompts.py` to versioned `prompts/*.yaml` loaded by `prompts.py` | Pending |\n| 4 | Remaining proposals of the earlier blueprint draft (v0.4) | Pending; not yet copied into this repository |\n\nDecisions are recorded as ADRs in `adr/` (template: `adr/000-template.md`).\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/code-governance/structural-constraints.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# Structural Constraints\n\n> **Purpose:** The rules every member follows when changing code structure, so that parallel work by six people can be merged.\n> **Authoritative for:** source layout, change rules, dependency direction and code-level traceability. *Which* modules exist is decided in `docs/architecture/architecture-blueprint.md` §4; where a specific requirement lands is decided in its ADR.\n> **Maintained by:** humans for §1–§9; each module owner writes their module's section in §10, integrated before SA Review.\n> **Last updated:** 2026-11-12\n\n## 1. Source Layout\n\n| Path | Role | New work goes here? |\n|---|---|---|\n| `src/open_deep_research/` | Baseline implementation: `deep_researcher.py` (graphs and nodes), `state.py`, `configuration.py`, `prompts.py`, `utils.py` | Yes |\n| `src/open_deep_research/<extension>/` | One extension module per architectural element (blueprint §4) | Yes, by its owner |\n| `src/security/` | Supabase JWT and LangGraph auth, loaded through `langgraph.json` | Only with separate review |\n| `test/` | Existing LLM- and API-dependent evaluation scripts | No |\n| `test/offline/` | Deterministic tests: no network, no LLM calls, run in CI | Yes, primary test location |\n| `test/live/` | Tests that call real models or APIs, run on demand | Yes, when a module test case requires it (`verification-constraints.md` §7) |\n| `scripts/` | Project tooling used by CI and humans, e.g. `validate_requirements.py` | Only with human approval |\n\n`[tool.setuptools] packages` in `pyproject.toml` lists `open_deep_research` and `test`. A new extension subpackage is added to that list in the same PR, or a non-editable install omits it.\n\n## 2. Graphs and Nodes\n\n1. **Thin nodes** (accepted 2026-10-13): graph wiring, node names and node signatures stay in `deep_researcher.py`; a node body calls the module that owns its logic and contains no architectural logic of its own.\n2. **Topology:** the three baseline graphs and their nodes (blueprint §3) stay unchanged. Adding or removing a node or edge needs an accepted ADR.\n\n## 3. Tool Assembly\n\n1. Researcher tools have one entry point, `utils.get_all_tools(config)`, which adds core tools (`ResearchComplete`, `think_tool`), then search tools for the configured `SearchAPI` (`utils.get_search_tool`), then MCP tools (`utils.load_mcp_tools`, wrapped by `utils.wrap_mcp_authenticate_tool`; `existing_tool_names` prevents name clashes).\n2. `SearchAPI` values are `tavily`, `openai`, `anthropic` and `none`.\n3. The supervisor's tools (`ConductResearch`, `ResearchComplete`, `think_tool`) are bound directly in the `supervisor` node.\n\nA new researcher tool is implemented in `utils.py` or the owning extension module and registered through `get_all_tools()`; no node assembles its own tool set.\n\n## 4. Models and API Keys\n\n1. The baseline creates chat models in two places only: the shared `configurable_model` in `deep_researcher.py`, configured per call for `research_model`, `compression_model` and `final_report_model`, and the summarization model in `utils.tavily_search` (`summarization_model`). New code reuses these and creates no other model client.\n2. API keys are obtained only through `utils.get_api_key_for_model()` (or `utils.get_tavily_api_key()` for Tavily), never read directly.\n\n## 5. Module Boundaries and Dependency Direction\n\n| Rule | Description |\n|---|---|\n| One element, one module | Each architectural element in the blueprint maps to exactly one module, and a module takes on no second responsibility. |\n| Dependency direction | `deep_researcher.py` → extension modules → shared modules (`state.py`, `configuration.py`, `prompts.py`, `utils.py`). No module imports `deep_researcher.py`. Any exception is recorded in blueprint §6. |\n| No logic in configuration and prompts | `prompts.py` holds templates only; `configuration.py` imports no other project module. |\n| Extend, never replace | Do not delete baseline nodes, tools or configuration fields, and do not build a parallel implementation of existing behaviour. Fix or extend it in place. |\n| Auth is independent | The research graph does not import `src/security/auth.py`. |\n\n## 6. Shared Contracts\n\nA change to a type in `state.py`, or to any interface another owner's module reads, needs the approval of every owner who reads it, recorded in the PR review. Shared contracts introduced by a requirement are defined in that requirement's ADR and covered by the shared contract tests (`verification-constraints.md` §3).\n\n## 7. Safety-Relevant Code\n\nCode implementing a requirement marked `safety_relevant: true` in `requirements.yaml` must:\n\n1. make the decision in deterministic code that does not call a model — the model's output is input to the decision, never the decision itself;\n2. have an accepted ADR and a review by a second owner besides the author;\n3. have a test that fails when the related invariant is violated.\n\n## 8. Where New Work Goes\n\n1. **Logic for an improvement:** in the owner's extension module, called from the existing node.\n2. **Configuration:** a field in `Configuration` (MCP settings in `MCPConfig`) with `x_oap_ui_config` metadata. An improvement that changes runtime behaviour gets one flag so it can be compared with the baseline; the default stays at the baseline behaviour until the requirement is `verified`, and the PR that marks it verified switches the default.\n3. **Prompts:** in `prompts.py`, filled through `format()`. Moving prompts to versioned `prompts/*.yaml` is proposed in blueprint §11.\n4. **Dependencies:** declared in `pyproject.toml` with their purpose, locked in `uv.lock`, agreed with the human first.\n\n## 9. Traceability in Code\n\nEvery new module and public function names, in its docstring, the requirement ID and the ADR or invariant it implements, for example `REQ-003, ADR-002, INV-003`. Every test module states the RIDs it verifies in its docstring (`verification-constraints.md` §3).\n\n## 10. Module Constraints\n\nCopy the example for your module. At integration, check that responsibilities do not overlap, every dependency follows §5 or is listed in blueprint §6, and no two modules write the same state field.\n\n### <Module> (REQ-NNN, ADR-NNN)\n\n| Item | Constraint |\n|---|---|\n| Path | `src/open_deep_research/<module>/` |\n| Responsibility | One sentence; what the module decides or produces |\n| Public interface | Functions and types other code may call |\n| Called from | Nodes or modules that call it, e.g. `supervisor_tools` in `deep_researcher.py` |\n| May depend on | e.g. `state.py`, `configuration.py`, `utils.py` |\n| Must not depend on | e.g. `deep_researcher.py`, other extension modules, model clients in deterministic code |\n| Shared contracts | Types or state fields it reads or writes that other modules also use |\n| Configuration flag | `Configuration` field that switches the behaviour, and its default (§8) |\n"
    }
  ]
}
```

### Event 5 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/code-governance/verification-constraints.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# Verification Constraints\n\n> **Purpose:** One shared way to decide that a requirement is really done.\n> **Authoritative for:** verification layers, test conventions, commands, CI gates, verdicts and evidence, module test requirements and the Definition of Done.\n> **Maintained by:** humans for §1–§6 and §8; each module owner writes their module's test requirements in §7, integrated before SA Review.\n> **Last updated:** 2026-11-12\n\n## 1. Three Verification Layers\n\n| Layer | Meaning | Where it runs |\n|---|---|---|\n| **Structural** | Code organisation, schemas, module boundaries, docstring RIDs and lint conform to the rules | CI: schema and static-analysis gates |\n| **Regression** | Existing behaviour and shared contracts still hold | CI: every suite in `test/offline/` |\n| **Behavioural** | The requirement's behaviour meets its fit criterion | New offline tests; `test/live/` or `test/run_evaluate.py` when a case needs a real model; human confirmation |\n\n## 2. Principles\n\n1. Every fit-criterion check and metric in `requirements.yaml` has at least one test or a named piece of review evidence; its `verification` field points to it.\n2. Every invariant has a test that fails when the invariant is violated.\n3. A change runs its new tests and every prior offline suite; any regression blocks the merge.\n4. Module test requirements (§7) are approved in SA Review (Gate 1) before tests are written, and the tests are approved before implementation (Gate 2). Tests are written by Test Author and never changed by Build.\n5. Prefer deterministic offline tests; use live tests for final behavioural evidence only.\n\n## 3. Test Conventions\n\n- **Offline tests** (`test/offline/`) use fake models and fake researchers, make no network calls and need no API keys, so supervisor logic, termination, scheduling and context handling run in CI at no token cost.\n- **Live tests** (`test/live/`) call real models or APIs, run on demand rather than on every commit, and are marked `automated: false` in `requirements.yaml` when a human must judge the result.\n- **Names:** test files are named after the behaviour they cover, `test_<topic>.py` (for example `test_failure_propagation.py`); test functions describe the expected behaviour. Requirement IDs are not part of file names, so renumbering requirements does not rename tests.\n- **Traceability:** the first line of every test module's docstring lists the RIDs it verifies, for example `\"\"\"REQ-002: no delegated task is lost or silently treated as completed.\"\"\"`. The requirement's `verification` field gives the exact `path::test_name`.\n- **Shared contract tests:** when a requirement defines a shared contract (`structural-constraints.md` §6), its contract tests live in `test/offline/test_contracts.py` and every PR runs them.\n\n## 4. Commands\n\n| Check | Command |\n|---|---|\n| Requirements schema and ID consistency | `uv run python scripts/validate_requirements.py` |\n| Lint (gated paths) | `uv run ruff check src/open_deep_research test/offline scripts` |\n| Type check (optional, not gated) | `uv run mypy src/open_deep_research` |\n| Offline tests | `uv run pytest test/offline` |\n| Live and evaluation tests | `uv run pytest test/live`, `uv run python test/run_evaluate.py` |\n\n`ruff format` is applied to new files and changed lines only; do not reformat untouched baseline code. Install tools with `uv sync --extra dev`.\n\n## 5. CI Gates\n\nThe course requires six blocking gates. Their state in `.github/workflows/ci.yml`:\n\n| Course gate | CI job | What it checks | Status |\n|---|---|---|---|\n| Schema | `requirements-schema` | `requirements.yaml` against `req-schema.json`, plus unique and resolvable IDs | Active |\n| Static analysis | `static-analysis` | `ruff check` on the gated paths | Active; mypy planned |\n| Regression | `offline-tests` | `pytest test/offline` | Active; reports `NOT_RUN` while the directory has no tests |\n| Test approval | — | The approval record has Gate 2 for every PR that changes `src/`, and the PR's tests match the approved test commit | Planned |\n| AI-use log | — | `docs/ai-use-log.yaml` is valid and has an entry for the PR | Planned |\n| Semantic evaluation | — | Live evaluation of fit criteria for prompt or model changes | Planned |\n\nLint debt outside the gated paths is tracked in `docs/debt-register.md`; a path joins the static-analysis gate once it is clean.\n\n## 6. Verdicts and Evidence\n\n- Verdicts are only `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED` and `N/A`. A skipped test is `NOT_RUN`, never `PASS`.\n- No check is reported as passed without execution evidence. A mandatory check that is `FAIL`, `NOT_RUN` or `BLOCKED` keeps the requirement from `verified`.\n- Evidence goes to `docs/test-reports/<task-id>.md`: the baseline run by Test Author and the verification by Verify, each with commit, commands, verdict per check, and logs or diffs where relevant.\n- Offline tests run without network or secrets (§3). Verify changes no file other than its report; the PR diff shows any change made during verification.\n\n## 7. Module Test Requirements\n\nCopy the example for your module. Every acceptance criterion (C-/M-) of the module's requirements and every invariant it enforces needs at least one case, and the module lists the existing suites it can affect. At integration, check that no criterion or invariant is left without a case.\n\n### <Module> (REQ-NNN, ADR-NNN)\n\n| Case | Covers | Type | Input | Expected result | Test |\n|---|---|---|---|---|---|\n| TC-001 | REQ-NNN C-NNN | normal | | | `test/offline/<file>::<test>` |\n| TC-002 | INV-NNN | exception | | | |\n| TC-003 | REQ-NNN M-NNN | boundary | | | |\n\n- **Regression:** existing suites to re-run, including `test/offline/test_contracts.py` if a shared contract changes.\n- **Live or human checks:** cases marked `automated: false` in `requirements.yaml`, and where their evidence goes.\n\n## 8. Definition of Done\n\n| # | Condition | Done by |\n|---|---|---|\n| 1 | Every fit-criterion item has an approved test or recorded review, and the tests pass | Test Author (tests), Build (passing), confirmed by Verify |\n| 2 | All prior offline suites pass | Verify |\n| 3 | All active CI gates are green | CI |\n| 4 | Behaviour conforms to the fit criterion, with evidence in `docs/test-reports/` | Verify, confirmed by a human |\n| 5 | `trace-matrix.md` row complete for architecture, code and tests | Module owner |\n| 6 | If a boundary changed: `invariants.md` updated and its test passes | Human, Test Author |\n| 7 | If an architectural decision arose: ADR accepted or `evaluation-table.md` entry recorded | Human |\n| 8 | `docs/ai-use-log.yaml` and `docs/review-memo.md` updated | Human |\n| 9 | Gate 3 passed: two approvals, PR merged | Humans |\n| 10 | `status` in `requirements.yaml` advanced to `verified` | Human |\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/architecture/adr/000-template.md"
  },
  "output": [
    {
      "type": "text",
      "text": "(no output)"
    }
  ]
}
```

### Event 6 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "ls -la docs/architecture/adr/ && find docs/architecture/adr -type f | sort"
  },
  "output": [
    {
      "type": "text",
      "text": "total 8\ndrwxr-xr-x   3 doppler  staff    96 Nov 13 18:42 .\ndrwxr-xr-x  10 doppler  staff   320 Nov 13 18:42 ..\n-rw-r--r--   1 doppler  staff  2230 Nov 13 18:42 000-template.md\ndocs/architecture/adr/000-template.md\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/architecture/evaluation-table.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# Evaluation Table\n\n> **Purpose:** ADD results: for each architectural question, 2–3 candidate solutions compared on pros, cons, complexity and testability, and the choice made.\n> **Authoritative for:** option comparisons. The decision itself is recorded in the ADR named in the entry.\n> **Maintained by:** each module owner adds the entries for their module; entries are integrated before SA Review (`Prompt.md` §4).\n> **Last updated:** 2026-11-12\n\n## How to Add an Entry\n\n1. Copy the example below, take the next free `EVAL-NNN` number and keep the same fields.\n2. **ASR:** list the requirements and the acceptance criteria (C-/M- IDs from `docs/req/requirements.yaml`) that shape the decision.\n3. **Candidates:** describe 2–3 options; rate complexity and offline testability as Low, Medium or High.\n4. **Choice:** name the chosen option and why it wins, say why each other option was rejected, then write the ADR.\n\n## EVAL-NNN: <Question being decided>\n\n- **Module:** <module from `architecture-blueprint.md` §4>\n- **Owner:** <name>\n- **Decision recorded in:** ADR-NNN\n- **Status:** Open | Decided\n\n**ASR**\n\n| Requirement | Acceptance criteria | Quality attributes at stake |\n|---|---|---|\n| REQ-NNN | C-NNN, M-NNN | e.g. correctness, testability, cost |\n\n**Candidates**\n\n| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |\n|---|---|---|---|---|---|---|\n| A | | | | | Low / Medium / High | Low / Medium / High |\n| B | | | | | | |\n| C (optional) | | | | | | |\n\n**Choice:** <option> — <why it wins>.\n\n**Rejected and why:** <option>: <reason>.\n"
    }
  ]
}
```

### Event 7 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/architecture/adr/000-template.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# ADR-NNN: <Decision Title>\n\n> Copy this file to `NNN-<short-slug>.md` with the next free number (`001`, `002`, ...) and fill every section. Never reuse a number; a replaced decision is marked *Superseded* and links to its successor.\n\n- **Status:** Proposed | Accepted | Superseded by ADR-NNN | Rejected\n- **Date:** YYYY-MM-DD\n- **Module:** <module>\n- **Owner:** <name>\n- **Evaluation:** EVAL-NNN (`docs/architecture/evaluation-table.md`)\n- **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance\n\n## 1. Architecturally Significant Requirements\n\n| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |\n|---|---|---|\n| REQ-NNN | C-NNN, M-NNN | |\n\n## 2. Context\n\nThe problem, the forces and constraints, and the baseline behaviour being changed (file and line).\n\n## 3. Decision\n\nThe chosen option, stated so that a coding agent can implement it without guessing.\n\n## 4. Rejected Options\n\n| Option | Reason for rejection |\n|---|---|\n| | |\n\nThe full comparison is in EVAL-NNN.\n\n## 5. Components and Interfaces\n\n| Component | Responsibility | Interface (signature or type) | Called by |\n|---|---|---|---|\n| | | | |\n\nShared contracts changed (`structural-constraints.md` §6): none | list, with the owners who must approve.\n\n## 6. State, Failure Handling and Deterministic Boundary\n\n- **State:** fields added or changed, or \"none\" (details in `memory-design.md`).\n- **Runtime policies:** POL IDs, or \"none\" (details in `runtime-policy-catalog.md`).\n- **Invariants:** INV IDs, or \"none\" (details in `invariants.md`).\n- **Deterministic boundary:** which decision is made by code rather than by the model, or \"none\".\n\n## 7. Verification\n\nHow each acceptance criterion and invariant above is verified; the cases are listed in the module section of `verification-constraints.md`.\n\n## 8. Consequences\n\nPositive, negative and neutral consequences, including effects on other modules.\n\n## 9. Implementation Steps\n\nOrdered steps for the coding agent, each naming the files it changes, e.g.:\n\n1. Add `<type>` to `src/open_deep_research/<module>/<file>.py`.\n2. Call it from `<node>` in `deep_researcher.py`, keeping the node thin.\n3. Add the configuration flag `<field>` with the baseline as default.\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/architecture/invariants.md && echo \"=====TRACE=====\" && cat docs/architecture/trace-matrix.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# Invariants\n\n> **Purpose:** Properties of the research agent (the product) that no change may violate, each traced to a requirement, an enforcing component, a test and a fallback. Rules for coding agents belong in `docs/architecture/permission-model.md` and `.opencode/rules.md`, not here.\n> **Authoritative for:** the detailed rule behind each `invariant`-type or safety-relevant requirement. Where an entry here differs from `docs/req/requirements.yaml`, the requirement wins and the difference must be reported.\n> **Maintained by:** each module owner adds the entries for their module; they are integrated and renumbered before SA Review.\n> **Status:** All entries are *Proposed* until SA Review. Enforcing components are responsibility assignments, not implemented code.\n> **Last updated:** 2026-11-12\n\nEvery entry uses the same fields:\n\n- **Statement** — the property, in one or two sentences.\n- **Module** — the module from `architecture-blueprint.md` §4 that enforces it.\n- **Source** — the requirement IDs it details.\n- **Status** — *Proposed*, *Accepted*, *Deferred* or *Retired*.\n- **Enforcing component** — where the property is enforced.\n- **Verification** — the offline test that fails on violation, plus any runtime monitor.\n- **Fallback** — what the system does when the property cannot be kept.\n\n## INV-001 — Compression never drops the newest context\n\n- **Statement:** When compression trims context to fit a token limit, the research topic, the compression instruction, the latest AI turn and the tool results after it are never removed, and no tool result is kept without the AI message that requested it.\n- **Module:** context\n- **Source:** REQ-005\n- **Status:** Proposed\n- **Enforcing component:** the token-limit branch of `compress_research` and its trimming helper (module assigned in Design).\n- **Verification:** `test/offline/test_context_compaction.py`; monitor `latest_turn_preservation_rate == 1.0`.\n- **Fallback:** remove whole turns from the oldest end; if the limit still cannot be met, end the task with a failed result of category `token_limit`. Never drop the latest turn and never return placeholder text as a summary.\n\n## INV-002 — No failure is reported as complete research\n\n- **Statement:** A run with an unhandled exception, a failed or partial research task, a non-`covered` exit or a failed report generation never ends with research outcome `complete`.\n- **Module:** delivery\n- **Source:** REQ-002, REQ-004\n- **Status:** Proposed\n- **Enforcing component:** the failure branch of `supervisor_tools`; the run-outcome computation before and after `final_report_generation`.\n- **Verification:** `test/offline/test_failure_propagation.py`, `test/offline/test_run_outcome.py`; monitor `false_complete_outcome_count == 0`.\n- **Fallback:** record the failed task with category and message, keep sibling results, and deliver outcome `partial` with a system-added limitations section, or `failed` with an empty report. Never swallow an exception.\n\n## INV-003 — Research is bounded and every exit has one reason\n\n- **Statement:** Each research loop is bounded by its iteration cap and each task by its tool-call budget; every loop exit records exactly one exit reason, and only `covered` can lead to outcome `complete`.\n- **Module:** orchestration\n- **Source:** REQ-001, REQ-003\n- **Status:** Proposed\n- **Enforcing component:** the termination check in the supervisor loop; the task budget in the task specification.\n- **Verification:** `test/offline/test_research_termination.py`, `test/offline/test_task_contract.py`; monitor `exit_without_single_reason_count == 0`.\n- **Fallback:** at the cap, start no new delegations, end unrun delegations as failed with reason `not_run`, and exit with `budget_exhausted`. A completion request below the coverage threshold is refused, not accepted.\n\n## INV-004 — Every report citation resolves to a retrieved source\n\n- **Statement:** Every citation identifier in a report resolves to exactly one source that was retrieved during the run; a report whose required facts lack resolvable citations is not delivered as complete.\n- **Module:** citations\n- **Source:** none. REQ-006 covers citation format only and lists deterministic citation validation as out of scope.\n- **Status:** Deferred\n- **Enforcing component:** a citation validator at report generation (proposed).\n- **Verification:** offline fixed-source tests for missing, duplicate and malformed identifiers and unsourced facts; monitor `citation_integrity_violation_count == 0`.\n- **Fallback:** correct only format issues that the source list determines; otherwise mark the evidence as missing. Never fabricate a URL or reference.\n\n## INV-005 — Search results are never mistaken for evidence they do not contain\n\n- **Statement:** Every search source is reached through the single tool entry point and returns the same result contract; an unknown provider is rejected at start-up, an invalid result is a failed search, and an empty result is a successful search that carries no evidence.\n- **Module:** search\n- **Source:** REQ-007, REQ-008\n- **Status:** Proposed\n- **Enforcing component:** search configuration validation at graph start; the search adapter called through `utils.get_all_tools()`.\n- **Verification:** `test/offline/test_search_configuration.py`, `test/offline/test_search_fallback.py` with fake providers (normal, empty, timeout, invalid, unknown).\n- **Fallback:** on an eligible error, try only the configured fallback sources in order and record each attempt; when all fail, return an explicit search failure. Never substitute a source that is not configured.\n\n## Adding an Entry\n\nCopy an entry, take the next free `INV-NNN` number, and fill every field. Never reuse a retired number. Add the INV ID to the requirement's row in `trace-matrix.md` and to the ADR's §6. At integration the integrator may renumber entries and updates every reference.\n=====TRACE=====\n# Requirement Traceability Matrix\n\n> **Purpose:** Trace every requirement through Design, Code, Test and runtime Monitor, so that any requirement can be followed forward to its evidence at any time.\n> **Authoritative for:** the links between artifacts. Requirement content, type and status come from `docs/req/requirements.yaml`; if a cell here disagrees with it, the YAML wins and the row is corrected.\n> **Maintained by:** each module owner fills the rows of their requirements: architectural consequence, ADR / invariant, component and verification method during SA; code and test evidence after implementation.\n> **Last updated:** 2026-11-12\n\nCell conventions: `TBD` = not decided yet; `Proposed:` = from a document that is not yet accepted; `planned:` = named in the requirement's `verification` field but not written yet. Update the row in the same PR whenever the requirement's design, code or tests change.\n\n## Traceability Matrix\n\n| Requirement ID | Title | Type | Status | Architectural Consequence | ADR / Invariant | Enforcing Component / Code | Test / Evidence | Runtime Monitor |\n|---|---|---|---|---|---|---|---|---|\n| REQ-001 | Typed task contract | functional | approved | TBD | INV-003 (Proposed) | Proposed: `orchestration/` | planned: `test/offline/test_task_contract.py` | `unsourced_finding_counted_count` |\n| REQ-002 | No task lost or silently completed | invariant | approved | TBD | INV-002 (Proposed) | Proposed: `orchestration/` or `delivery/` | planned: `test/offline/test_failure_propagation.py` | `dropped_delegation_count`, `failure_text_in_notes_count` |\n| REQ-003 | Coverage-based termination | invariant | approved | TBD | INV-003 (Proposed) | Proposed: `orchestration/` | planned: `test/offline/test_research_termination.py`, `test/live/test_research_termination_live.py` | `exit_without_single_reason_count`, `premature_complete_accepted_count` |\n| REQ-004 | Run outcome in output | functional | approved | TBD | INV-002 (Proposed) | Proposed: `delivery/` | planned: `test/offline/test_run_outcome.py` | `false_complete_outcome_count` |\n| REQ-005 | Compression keeps newest context | invariant | approved | TBD | INV-001 (Proposed) | Proposed: `context/` | planned: `test/offline/test_context_compaction.py` | `latest_turn_preservation_rate`, `orphan_tool_message_count` |\n| REQ-006 | One citation format | invariant | approved | TBD | TBD | Proposed: `citations/` | planned: `test/offline/test_prompt_citation_contract.py`, `test/live/test_report_citations_live.py` | TBD |\n| REQ-007 | Search setup documented and validated | functional | approved | TBD | INV-005 (Proposed) | Proposed: `search/` | planned: `test/offline/test_search_configuration.py`; review in `docs/review-memo.md` | TBD |\n| REQ-008 | Search fallback | functional | approved | TBD | INV-005 (Proposed) | Proposed: `search/` | planned: `test/offline/test_search_fallback.py` | TBD |\n| REQ-009 | Valid evaluator scores | invariant | approved | TBD | TBD | Proposed: `test/evaluation/` | planned: `test/offline/test_evaluator_validity.py` | `out_of_range_score_count` |\n| REQ-010 | Evaluate an existing report | functional | approved | TBD | TBD | Proposed: `test/evaluation/` | planned: `test/offline/test_report_evaluation_entry.py`; review in `docs/review-memo.md` | TBD |\n\n## Example (Reference Only — VHIS Course Example)\n\n| Requirement ID | Title | Type | Status | Architectural Consequence | ADR / Invariant | Enforcing Component / Code | Test / Evidence | Runtime Monitor |\n|---|---|---|---|---|---|---|---|---|\n| REQ-VHIS-NFR-SAFETY-001 | Over-limit claims are never auto-approved | invariant | verified (example) | Fail-closed boundary: over-limit claims cannot be auto-approved | ADR-001 / INV-001 | Policy Core: `enforce_business_limits()` | Boundary ±1 tests; adversarial fuzzing (0 escapes) | `over_limit_auto_approve_count` = 0 |\n"
    }
  ]
}
```

### Event 8 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/architecture/runtime-policy-catalog.md && echo \"=====MEMORY=====\" && cat docs/architecture/memory-design.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# Runtime Policy Catalog\n\n> **Purpose:** What the research agent does at runtime when something goes wrong: exceptions, retries, degradation and failure paths.\n> **Authoritative for:** runtime handling policies. Each policy traces to a requirement or invariant.\n> **Maintained by:** owners of modules with exception, retry, degradation or failure handling write a module section (§2); §1 is integrated from those sections before SA Review. Modules without such handling add nothing.\n> **Last updated:** 2026-11-12\n\n## 1. Policies\n\n| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Module | Source | Test |\n|---|---|---|---|---|---|---|---|---|\n| POL-001 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |\n\n## 2. Module Sections\n\nCopy the example for your module and number policies with the next free `POL-NNN`; numbers are unified at integration.\n\n### <Module> (REQ-NNN, ADR-NNN)\n\n| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |\n|---|---|---|---|---|---|---|---|\n| POL-NNN | e.g. a researcher raises an exception | how deterministic code recognises it | what the system does | retries, limits, fallback, or none | effect on the run outcome (`complete`, `partial`, `failed`, REQ-004) | REQ-NNN / INV-NNN | `test/offline/<file>::<test>` |\n=====MEMORY=====\n# Memory and State Design\n\n> **Purpose:** How the research agent stores, passes and discards state and memory: state structure, ownership and lifecycle.\n> **Authoritative for:** state and memory design. Graph state types live in `src/open_deep_research/state.py`.\n> **Maintained by:** owners of modules that add or change state write a module section (§5); §1–§4 are integrated from those sections before SA Review. Modules that do not touch state add nothing.\n> **Last updated:** 2026-11-12\n\n## 1. State Model\n\n| State type | Graph | Key fields | Owning module | Shared contract? |\n|---|---|---|---|---|\n| `AgentState` | `deep_researcher` | TBD | TBD | TBD |\n| `SupervisorState` | supervisor subgraph | TBD | TBD | TBD |\n| `ResearcherState` / `ResearcherOutputState` | researcher subgraph | TBD | TBD | TBD |\n\n## 2. Lifecycle\n\nHow each field is created, updated (reducer), passed between graphs and cleared. *TBD.*\n\n## 3. Context and Memory Limits\n\nToken budgets, trimming and compression rules. *TBD.*\n\n## 4. Persistence\n\nCheckpointers and anything stored beyond a single run. *TBD.*\n\n## 5. Module Sections\n\nCopy the example for your module. Before SA Review, check §5 of the other modules for conflicting field names, reducers or owners.\n\n### <Module> (REQ-NNN, ADR-NNN)\n\n**Fields added or changed**\n\n| State type | Field | Type | Reducer | Written by | Read by | Created → cleared |\n|---|---|---|---|---|---|---|\n| `SupervisorState` | `<field>` | `<type>` | override / append | `<component>` | `<components>` | `<when>` → `<when>` |\n\n- **Ownership:** which component is the only writer of each field.\n- **Lifecycle:** when the fields are created, updated and cleared within a run.\n- **Shared contract:** whether other modules read these fields, and which owners must approve changes (`structural-constraints.md` §6).\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat test/evaluators.py"
  },
  "output": [
    {
      "type": "text",
      "text": "from typing import cast\n\nfrom langchain_anthropic import ChatAnthropic\nfrom langchain_openai import ChatOpenAI\nfrom pydantic import BaseModel, Field\n\nfrom open_deep_research.utils import get_today_str\nfrom test.prompts import (\n    COMPLETENESS_PROMPT,\n    CORRECTNESS_PROMPT,\n    GROUNDEDNESS_PROMPT,\n    OVERALL_QUALITY_PROMPT,\n    RELEVANCE_PROMPT,\n    STRUCTURE_PROMPT,\n)\n\neval_model = ChatOpenAI(\n    model=\"gpt-4.1\",\n)\n\n\ndef _format_input_query(inputs: dict) -> str:\n    messages = inputs[\"messages\"]\n    if len(messages) == 1:\n        return messages[0][\"content\"]\n\n    role_to_string_format_map = {\n        \"user\": \"<user_input>\\n{content}\\n</user_input>\",\n        \"assistant\": \"<assistant_follow_up>\\n{content}\\n</assistant_follow_up>\",\n    }\n\n    return \"\\n\\n\".join(\n        [\n            role_to_string_format_map[message[\"role\"]].format(\n                content=message[\"content\"]\n            )\n            for message in messages\n        ]\n    )\n\n\nclass OverallQualityScore(BaseModel):\n    \"\"\"Score the overall quality of the report against specific criteria.\"\"\"\n\n    research_depth: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n    source_quality: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n    analytical_rigor: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n    practical_value: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n    balance_and_objectivity: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n    writing_quality: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n\n\ndef eval_overall_quality(inputs: dict, outputs: dict):\n    query = _format_input_query(inputs)\n    final_report = outputs[\"final_report\"]\n    user_input_content = f\"\"\"User input: {query}\\n\\nReport: \\n\\n{final_report}\\n\\nEvaluate whether the report meets the criteria and provide detailed justification for your evaluation.\"\"\"\n    if isinstance(eval_model, ChatAnthropic):\n        user_input_content = [\n            {\n                \"type\": \"text\",\n                \"text\": user_input_content,\n                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n            }\n        ]\n    eval_result = cast(\n        OverallQualityScore,\n        eval_model.with_structured_output(OverallQualityScore).invoke(\n            [\n                {\n                    \"role\": \"system\",\n                    \"content\": OVERALL_QUALITY_PROMPT.format(today=get_today_str()),\n                },\n                {\"role\": \"user\", \"content\": user_input_content},\n            ]\n        ),\n    )\n    return [\n        {\"key\": \"research_depth_score\", \"score\": eval_result.research_depth / 5},\n        {\"key\": \"source_quality_score\", \"score\": eval_result.source_quality / 5},\n        {\"key\": \"analytical_rigor_score\", \"score\": eval_result.analytical_rigor / 5},\n        {\"key\": \"practical_value_score\", \"score\": eval_result.practical_value / 5},\n        {\n            \"key\": \"balance_and_objectivity_score\",\n            \"score\": eval_result.balance_and_objectivity / 5,\n        },\n        {\"key\": \"writing_quality_score\", \"score\": eval_result.writing_quality / 5},\n    ]\n\n\nclass RelevanceScore(BaseModel):\n    \"\"\"Score the report relevance against specific criteria.\"\"\"\n\n    reasoning: str = Field(\n        description=\"The reason for the score, including specific examples from the report.\"\n    )\n    score: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria for relevance (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n\n\ndef eval_relevance(inputs: dict, outputs: dict):\n    query = _format_input_query(inputs)\n    final_report = outputs[\"final_report\"]\n    user_input_content = f\"\"\"User input: {query}\\n\\nReport: \\n\\n{final_report}\\n\\nEvaluate whether the report meets the criteria and provide detailed justification for your evaluation.\"\"\"\n    if isinstance(eval_model, ChatAnthropic):\n        user_input_content = [\n            {\n                \"type\": \"text\",\n                \"text\": user_input_content,\n                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n            }\n        ]\n\n    eval_result = cast(\n        RelevanceScore,\n        eval_model.with_structured_output(RelevanceScore).invoke(\n            [\n                {\n                    \"role\": \"system\",\n                    \"content\": RELEVANCE_PROMPT.format(today=get_today_str()),\n                },\n                {\"role\": \"user\", \"content\": user_input_content},\n            ]\n        ),\n    )\n    return {\n        \"key\": \"relevance_score\",\n        \"score\": eval_result.score / 5,\n        \"comment\": eval_result.reasoning,\n    }\n\n\nclass StructureScore(BaseModel):\n    \"\"\"Score the report structure against specific criteria.\"\"\"\n\n    reasoning: str = Field(\n        description=\"The reason for the score, including specific examples from the report.\"\n    )\n    score: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria for structure and flow (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n\n\ndef eval_structure(inputs: dict, outputs: dict):\n    query = _format_input_query(inputs)\n    final_report = outputs[\"final_report\"]\n    user_input_content = STRUCTURE_PROMPT.format(\n        user_question=query, report=final_report, today=get_today_str()\n    )\n    if isinstance(eval_model, ChatAnthropic):\n        user_input_content = [\n            {\n                \"type\": \"text\",\n                \"text\": user_input_content,\n                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n            }\n        ]\n\n    eval_result = cast(\n        StructureScore,\n        eval_model.with_structured_output(StructureScore).invoke(\n            [{\"role\": \"user\", \"content\": user_input_content}]\n        ),\n    )\n    return {\n        \"key\": \"structure_and_cohesiveness_score\",\n        \"score\": eval_result.score / 5,\n        \"comment\": eval_result.reasoning,\n    }\n\n\nclass CorrectnessScore(BaseModel):\n    \"\"\"Score the report correctness against specific criteria.\"\"\"\n\n    reasoning: str = Field(\n        description=\"The reason for the score, including specific examples from the report.\"\n    )\n    score: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria for correctness (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n\n\ndef eval_correctness(inputs: dict, outputs: dict, reference_outputs: dict):\n    query = _format_input_query(inputs)\n    final_report = outputs[\"final_report\"]\n    answer = reference_outputs[\"answer\"]\n    user_input_content = CORRECTNESS_PROMPT.format(\n        user_question=query, report=final_report, answer=answer, today=get_today_str()\n    )\n    if isinstance(eval_model, ChatAnthropic):\n        user_input_content = [\n            {\n                \"type\": \"text\",\n                \"text\": user_input_content,\n                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n            }\n        ]\n\n    eval_result = cast(\n        CorrectnessScore,\n        eval_model.with_structured_output(CorrectnessScore).invoke(\n            [{\"role\": \"user\", \"content\": user_input_content}]\n        ),\n    )\n    return {\n        \"key\": \"correctness_score\",\n        \"score\": eval_result.score / 5,\n        \"comment\": eval_result.reasoning,\n    }\n\n\nclass GroundednessClaim(BaseModel):\n    \"\"\"A claim from the report, and whether or not it is grounded in the context\"\"\"\n\n    claim: str = Field(description=\"The claim extracted from the report.\")\n    grounded: bool = Field(description=\"Whether the claim is grounded in the context.\")\n\n\nclass GroundednessScore(BaseModel):\n    \"\"\"Extract the claims and whether they are grounded in the context\"\"\"\n\n    claims: list[GroundednessClaim] = Field(\n        description=\"All claims extracted from the report, and whether or not they are grounded in the context.\"\n    )\n\n\ndef eval_groundedness(inputs: dict, outputs: dict):\n    final_report = outputs[\"final_report\"]\n    context = str(outputs[\"raw_notes\"])\n\n    user_input_content = GROUNDEDNESS_PROMPT.format(\n        context=context, report=final_report, today=get_today_str()\n    )\n    if isinstance(eval_model, ChatAnthropic):\n        user_input_content = [\n            {\n                \"type\": \"text\",\n                \"text\": user_input_content,\n                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n            }\n        ]\n\n    eval_result = cast(\n        GroundednessScore,\n        eval_model.with_structured_output(GroundednessScore)\n        .with_retry(stop_after_attempt=3)\n        .invoke(\n            [\n                {\"role\": \"user\", \"content\": user_input_content},\n            ]\n        ),\n    )\n    # normalize to 0-1\n    grounded_claims = [claim for claim in eval_result.claims if claim.grounded]\n    return {\n        \"key\": \"groundedness_score\",\n        \"score\": len(grounded_claims) / len(eval_result.claims),\n        \"comment\": str(eval_result.claims),\n    }\n\n\nclass CompletenessScore(BaseModel):\n    \"\"\"Score the report completeness against specific criteria.\"\"\"\n\n    reasoning: str = Field(\n        description=\"The reason for the score, including specific examples from the report.\"\n    )\n    score: int = Field(\n        description=\"Integer score 1-5 showing whether the report meets the provided criteria for completeness (1 = doesn't meet at all, 5 = meets all criteria).\"\n    )\n\n\ndef eval_completeness(inputs: dict, outputs: dict):\n    query = _format_input_query(inputs)\n    final_report = outputs[\"final_report\"]\n    research_brief = outputs[\"research_brief\"]\n    user_input_content = COMPLETENESS_PROMPT.format(\n        user_question=query,\n        research_brief=research_brief,\n        report=final_report,\n        today=get_today_str(),\n    )\n    if isinstance(eval_model, ChatAnthropic):\n        user_input_content = [\n            {\n                \"type\": \"text\",\n                \"text\": user_input_content,\n                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n            }\n        ]\n\n    eval_result = cast(\n        CompletenessScore,\n        eval_model.with_structured_output(CompletenessScore).invoke(\n            [{\"role\": \"user\", \"content\": user_input_content}]\n        ),\n    )\n    return {\n        \"key\": \"completeness_score\",\n        \"score\": eval_result.score / 5,\n        \"comment\": eval_result.reasoning,\n    }\n"
    }
  ]
}
```

### Event 9 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat test/prompts.py"
  },
  "output": [
    {
      "type": "text",
      "text": "OVERALL_QUALITY_PROMPT = \"\"\"You are an expert evaluator tasked with assessing the quality of research reports. Please evaluate the provided research report across multiple dimensions, provide scores, and offer a comprehensive assessment.\n\nEvaluation Criteria:\n\n1. Research Depth and Comprehensiveness\n   - Thoroughness of analysis\n   - Coverage of aspects relevant to the user's input\n   - Depth of understanding\n   - Background context provided\n\n2. Source Quality and Methodology\n   - Use of authoritative sources (webpages)\n   - Diversity of source webpage types (e.g. news articles, papers, etc.)\n   - Citation quality and integration\n   - Transparency of research methodology\n\n3. Analytical Rigor\n   - Sophistication of analysis\n   - Critical evaluation of the source information\n   - Identification of nuances and limitations\n\n4. Practical Value and Actionability\n   - Clarity of insights and recommendations\n   - Specific examples and use cases\n   - Does not refer to itself as the writer of the report at any point\n\n5. Balance and Objectivity\n   - Presentation of multiple perspectives\n   - Acknowledgment of limitations and trade-offs\n   - Distinction between facts and opinions\n   - Avoidance of bias\n\n6. Writing Quality and Clarity\n   - Clarity and professionalism of writing\n   - Appropriate use of terminology\n   - Consistency of tone and style\n   - Engagement and readability\n   - Does not refer to itself as the writer of the report at any point\n\nScoring Instructions:\n1. Evaluate each dimension on a scale of 1-5, where:\n   1 = Poor\n   2 = Fair\n   3 = Good\n   4 = Very Good\n   5 = Excellent\n\nEvaluation Process:\n1. Begin by analyzing each dimension separately. Wrap your analysis for each dimension in <dimension_analysis> tags. For each dimension:\n   a) Quote relevant sections from the report\n   b) List pros and cons\n   c) Consider how well it meets the criteria\n   It's okay for this section to be quite long as you thoroughly analyze each dimension.\n\n2. After completing the analysis, provide the formal evaluation using the format specified below.\n\nAdditional Considerations:\n- Assess whether the report's depth matches the complexity of the topic\n- Evaluate if the report effectively serves its intended audience\n- Consider the currency and relevance of the information presented\n- Determine if critical aspects are covered adequately\n- Look for the integration of quantitative data, case studies, and concrete examples where appropriate\n\nOutput Format:\nUse the following format for your evaluation:\n\nDimension Scores:\n1. Research Depth and Comprehensiveness: [Score]/5\n   Justification: [Brief explanation with examples]\n\n2. Source Quality and Methodology: [Score]/5\n   Justification: [Brief explanation with examples]\n\n3. Analytical Rigor: [Score]/5\n   Justification: [Brief explanation with examples]\n\n4. Practical Value and Actionability: [Score]/5\n   Justification: [Brief explanation with examples]\n\n5. Balance and Objectivity: [Score]/5\n   Justification: [Brief explanation with examples]\n\n6. Writing Quality and Clarity: [Score]/5\n   Justification: [Brief explanation with examples]\n\nOverall Assessment:\n[2-3 paragraph summary of the report's quality, utility, and fitness for purpose]\n\nToday is {today}\n\nNow, please evaluate the research report.\n\"\"\"\n\n\nCORRECTNESS_PROMPT = \"\"\"You are evaluating the correctness of a research report that was generated by a research agent.\n\nYou will be provided with the question, the report, and the answer from an independent authority.\n\nScore the report from 1-5 on how well it mirrors the answer from the authority. \nWe expect the report to contain more information that is not in the answer, that's perfectly okay.\nThey likely won't be perfectly the same, but they should have the same themes and ideas to get a high score.\n\nUse your best judgement when comparing the answer to the report!\n\"\"\"\n\nRELEVANCE_PROMPT = \"\"\"You are evaluating the relevance of a response to a user's input question. Please assess the answer against the following criteria, being especially strict about section relevance.\n\n1. Topic Relevance (Overall): Does the response directly address the user's input questions thoroughly?\n\n2. Section Relevance (Critical): CAREFULLY assess each individual section for relevance to the main topic:\n   - Identify each section by its ## header\n   - For each section, determine if it is directly relevant to the primary topic\n   - Flag any sections that seem tangential, off-topic, or only loosely connected to the main topic\n   - A high-quality response (score 5) should have NO irrelevant sections\n\n3. Citations: Does the response properly cite sources where necessary?\n\n4. Overall Quality: Is the response well-researched, accurate, and professionally written?\n\nEvaluation Instructions:\n- Be STRICT about section relevance - ALL sections must clearly connect to the primary topic\n- You must individually mention each section by name and assess its relevance\n- Provide specific examples from the response to justify your evaluation for each criterion\n- A response that is not relevant to the user's input topic should be scored 1\n- A response passing all of the above criteria should be scored 5\n\nToday is {today}\n\"\"\"\n\n\nSTRUCTURE_PROMPT = \"\"\"You are evaluating the structure and flow of a response to a user's question. Your evaluation should focus on the following criteria:\n\n<Rubric>\nA well-structured report should:\n- Be in the correct format for the user's question\n   - For example, if the user asks for a list of N items, the report should be a list of N items, no more, no less. This is crucial.\n   - For example, if the user asks for a comparison of X and Y, the report should have a section about X, a section about Y, and a comparison of the two.\n- Have a logical flow from one section to the next\n- Be appropriate for the user's question\n- Use structural elements (e.g., headers, tables, lists) to effectively convey information\n- Have properly formatted section headers (e.g., # for title, ## for sections, ### for subsections)\n</Rubric>\n\n<Instruction>\n- Compare the output against the user's question, is it in the format that the user asked for?\n- Identify any sections that are not logically connected to the user's question\n- Identify any sections that are not logically connected to the previous and next sections\n- Reason about whether the structure is the best structure for the user's question\n</Instruction>\n\n<Reminder>\n- Focus solely on structure and flow of the report\n</Reminder>\n\n<user_question>\n{user_question}\n</user_question>\n\n<report>\n{report}\n</report>\n\nToday is {today}\n\"\"\"\n\n\nGROUNDEDNESS_PROMPT = \"\"\"\nYou are evaluating how well a research report aligns with and is supported by the context retrieved from the web. Your evaluation should focus on the following criteria:\n\n<Rubric> \nA well-grounded report should: \n- Make claims that are directly supported by the retrieved context\n- Stay within the scope of information provided in the context\n- Maintain the same meaning and intent as the source material\n- Not introduce external facts or unsupported assertions outside of basic facts (2 + 2 = 4)\n\nAn ungrounded report:\n- Makes claims without support from the context\n- Contradicts the retrieved information\n- Includes speculation or external knowledge outside of basic facts\n- Distorts or misrepresents the context\n</Rubric>\n\n<Instruction>\n- Compare the report against the retrieved context carefully\n- Identify factual claims, statements, and assertions made in the report\n- For each claim:\n   - Decide whether it is directly grounded in the context\n- Claims are often made where you see citations. You can check against the cited source as well.\n</Instruction>\n\n<context>\n{context}\n</context>\n\n<report>\n{report}\n</report>\n\n<Output Format>\nUse the following format for your evaluation:\n{{\n   \"claims\": [\n      {{\n         \"text\": \"string – the extracted claim\",\n         \"grounded\": true | false\n      }},\n      ...\n   ]\n}}\n</Output Format>\n\"\"\"\n\n\nCOMPLETENESS_PROMPT = \"\"\"You are evaluating the completeness of a research report. Your evaluation should focus on the following criteria:\n\n<Rubric>\nA complete report should:\n- Answer all points from the user's question\n- Have a research brief that fully encompasses the user's question\n- Have a report that fully encompasses the research brief and the user's question\n\nAn incomplete report:\n- Does not answer all points from the user's question\n- Does not have a research brief that fully encompasses the user's question\n- Does not have a report that fully encompasses the research brief and the user's question\n- Makes assumptions that are not directly stated by the user's question\n</Rubric>\n\n<Instruction>\n- Compare the output against the research brief and the user's question\n- Identify any points that are not covered by the report\n- Identify any points that are not covered by the research brief\n- Identify any points that are not covered by the user's question\n</Instruction>\n\n<Reminder>\n- Focus solely on completeness of the report\n- Ignore whether external knowledge suggests different facts\n- Consider both explicit and implicit claims\n- Provide specific examples of complete/incomplete content  \n</Reminder>\n\n<research_brief>\n{research_brief}\n</research_brief>\n\n<user_question>\n{user_question}\n</user_question>  \n\n<report>\n{report}\n</report>\n\nToday is {today}\n\"\"\""
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat test/run_evaluate.py && echo \"=====PAIRWISE=====\" && cat test/pairwise_evaluation.py && echo \"=====PARALLEL=====\" && cat test/supervisor_parallel_evaluation.py"
  },
  "output": [
    {
      "type": "text",
      "text": "from langsmith import Client\nfrom test.evaluators import eval_overall_quality, eval_relevance, eval_structure, eval_correctness, eval_groundedness, eval_completeness\nfrom dotenv import load_dotenv\nimport asyncio\nfrom open_deep_research.deep_researcher import deep_researcher_builder\nfrom langgraph.checkpoint.memory import MemorySaver\nimport uuid\n\nload_dotenv(\"../.env\")\n\nclient = Client()\n\n# NOTE: Configure the right dataset and evaluators\ndataset_name = \"Deep Research Bench\"\nevaluators = [eval_overall_quality, eval_relevance, eval_structure, eval_correctness, eval_groundedness, eval_completeness]\n# NOTE: Configure the right parameters for the experiment, these will be logged in the metadata\nmax_structured_output_retries = 3\nallow_clarification = False\nmax_concurrent_research_units = 10\nsearch_api = \"tavily\" # NOTE: We use Tavily to stay consistent\nmax_researcher_iterations = 6\nmax_react_tool_calls = 10\nsummarization_model = \"openai:gpt-4.1-mini\"\nsummarization_model_max_tokens = 8192\nresearch_model = \"openai:gpt-5\" # \"anthropic:claude-sonnet-4-20250514\"\nresearch_model_max_tokens = 10000\ncompression_model = \"openai:gpt-4.1\"\ncompression_model_max_tokens = 10000\nfinal_report_model = \"openai:gpt-4.1\"\nfinal_report_model_max_tokens = 10000\n\nasync def target(\n    inputs: dict,\n):\n    graph = deep_researcher_builder.compile(checkpointer=MemorySaver())\n    config = {\n        \"configurable\": {\n            \"thread_id\": str(uuid.uuid4()),\n        }\n    }\n    # NOTE: Configure the right dataset and evaluators\n    config[\"configurable\"][\"max_structured_output_retries\"] = max_structured_output_retries\n    config[\"configurable\"][\"allow_clarification\"] = allow_clarification\n    config[\"configurable\"][\"max_concurrent_research_units\"] = max_concurrent_research_units\n    config[\"configurable\"][\"search_api\"] = search_api\n    config[\"configurable\"][\"max_researcher_iterations\"] = max_researcher_iterations\n    config[\"configurable\"][\"max_react_tool_calls\"] = max_react_tool_calls\n    config[\"configurable\"][\"summarization_model\"] = summarization_model\n    config[\"configurable\"][\"summarization_model_max_tokens\"] = summarization_model_max_tokens\n    config[\"configurable\"][\"research_model\"] = research_model\n    config[\"configurable\"][\"research_model_max_tokens\"] = research_model_max_tokens\n    config[\"configurable\"][\"compression_model\"] = compression_model\n    config[\"configurable\"][\"compression_model_max_tokens\"] = compression_model_max_tokens\n    config[\"configurable\"][\"final_report_model\"] = final_report_model\n    config[\"configurable\"][\"final_report_model_max_tokens\"] = final_report_model_max_tokens\n    # NOTE: We do not use MCP tools to stay consistent\n    final_state = await graph.ainvoke(\n        {\"messages\": [{\"role\": \"user\", \"content\": inputs[\"messages\"][0][\"content\"]}]},\n        config\n    )\n    return final_state\n\nasync def main():\n    return await client.aevaluate(\n        target,\n        data=dataset_name,\n        evaluators=evaluators,\n        experiment_prefix=f\"ODR GPT-5, Tavily Search\",\n        max_concurrency=10,\n        metadata={\n            \"max_structured_output_retries\": max_structured_output_retries,\n            \"allow_clarification\": allow_clarification,\n            \"max_concurrent_research_units\": max_concurrent_research_units,\n            \"search_api\": search_api,\n            \"max_researcher_iterations\": max_researcher_iterations,\n            \"max_react_tool_calls\": max_react_tool_calls,\n            \"summarization_model\": summarization_model,\n            \"summarization_model_max_tokens\": summarization_model_max_tokens,\n            \"research_model\": research_model,\n            \"research_model_max_tokens\": research_model_max_tokens,\n            \"compression_model\": compression_model,\n            \"compression_model_max_tokens\": compression_model_max_tokens,\n            \"final_report_model\": final_report_model,\n            \"final_report_model_max_tokens\": final_report_model_max_tokens,\n        }\n    )\n\nif __name__ == \"__main__\":\n    results = asyncio.run(main())\n    print(results)\n=====PAIRWISE=====\nfrom langchain_anthropic import ChatAnthropic\nfrom langsmith.evaluation import evaluate_comparative\nfrom pydantic import BaseModel, Field\n\nHEAD_TO_HEAD_PROMPT = \"\"\"\nWe are testing out two different implementations of a deep research agent. This research agent is designed to conduct deep research on a given question.\n\nThis was the question: \n{question}\n\nFirst Implementation's Response:\n{answer_a}\n\nSecond Implementation's Response:\n{answer_b}\n\nIn order to evaluate these agents, keep the following criteria in mind:\n- A good research agent should research sufficient sources to answer the question. These sources should be diverse and high quality. More sources is not always necessarily better, but it is important to have ENOUGH sources to feel confident in the claims that are made.\n- A good research agent should completely and comprehensively answer the user's question. \n- Deep research agents are expensive. The user expects a very good, and also very detailed answer. They should get all of the information that they need from this response, and should not have to ask for followups usually.\n- Citations should be provided for all claims, and should be formatted in a way that is easy to read and understand.\n\nImportant:\nThese two implementations conducted research differently, and so they might have different information and different sources. This is a key point for you to evaluate.\nWhich agent was able to find better sources and better answer the question? The #1 thing we care about the most is the quality and comprehensiveness of the answer.\n\nWith those criteria in mind, please select which response you prefer, and explain why!\n\"\"\"\n\nclass HeadToHeadRanking(BaseModel):\n    reasoning: str = Field(description=\"The reasoning for why you selected the preferred answer. This should be a detailed explanation!\")\n    preferred_answer: int = Field(description=\"The preferred answer between 1 and 2, where 1 is the first response, 2 is the second response.\")\n\n\ndef head_to_head_evaluator(inputs: dict, outputs: list[dict]) -> list:\n    grader_llm = ChatAnthropic(\n        model=\"claude-opus-4-20250514\",\n        max_tokens=20000,\n        thinking={\"type\": \"enabled\", \"budget_tokens\": 16000},\n    )\n\n    response = grader_llm.with_structured_output(HeadToHeadRanking).invoke(HEAD_TO_HEAD_PROMPT.format(\n        question=inputs[\"messages\"][0][\"content\"],\n        answer_a=outputs[0].get(\"final_report\", \"N/A\"),\n        answer_b=outputs[1].get(\"final_report\", \"N/A\"),\n    ))\n\n    if response.preferred_answer == 1:\n        scores = [1, 0]\n    elif response.preferred_answer == 2:\n        scores = [0, 1]\n    else:\n        scores = [0, 0]\n    return scores\n\n\nALL_THREE_PROMPT = \"\"\"\nWe are testing out three different implementations of a deep research agent. This research agent is designed to conduct deep research on a given question.\n\nThis was the question: \n{question}\n\nFirst Implementation's Response:\n{answer_a}\n\nSecond Implementation's Response:\n{answer_b}\n\nThird Implementation's Response:\n{answer_c}\n\nIn order to evaluate these agents, keep the following criteria in mind:\n- A good research agent should research sufficient sources to answer the question. These sources should be diverse and high quality. More sources is not always necessarily better, but it is important to have ENOUGH sources to feel confident in the claims that are made.\n- A good research agent should completely and comprehensively answer the user's question. \n- Deep research agents are expensive. The user expects a very good, and also very detailed answer. They should get all of the information that they need from this response, and should not have to ask for followups usually.\n- Citations should be provided for all claims, and should be formatted in a way that is easy to read and understand.\n\nImportant:\nThese three implementations conducted research differently, and so they might have different information and different sources. This is a key point for you to evaluate.\nWhich agent was able to find better sources and better answer the question? The #1 thing we care about the most is the quality and comprehensiveness of the answer.\n\nWith those criteria in mind, please rank the responses from 1 to 3, where 1 is the best response, 2 is the second best response, and 3 is the worst response.\nAnd please explain why you selected the ranking you did!\n\"\"\"\n\nclass Rankings(BaseModel):\n    reasoning: str = Field(description=\"The reasoning for why you selected the preferred answer. This should be a detailed explanation!\")\n    preferred_answer: int = Field(description=\"The preferred answer between 1 and 3, where 1 is the first response, 2 is the second response, and 3 is the third response.\")\n    second_best_answer: int = Field(description=\"The second best answer between 1 and 3, where 1 is the first response, 2 is the second response, and 3 is the third response.\")\n    worst_answer: int = Field(description=\"The worst answer between 1 and 3, where 1 is the first response, 2 is the second response, and 3 is the third response.\")\n\ndef free_for_all_evaluator(inputs: dict, outputs: list[dict]) -> list:\n    grader_llm = ChatAnthropic(\n        model=\"claude-opus-4-20250514\",\n        max_tokens=20000,\n        thinking={\"type\": \"enabled\", \"budget_tokens\": 16000},\n    )\n\n    response = grader_llm.with_structured_output(Rankings).invoke(ALL_THREE_PROMPT.format(\n        question=inputs[\"messages\"][0][\"content\"],\n        answer_a=outputs[0].get(\"final_report\", \"N/A\"),\n        answer_b=outputs[1].get(\"final_report\", \"N/A\"),\n        answer_c=outputs[2].get(\"final_report\", \"N/A\"),\n    ))\n\n    scores = [0, 0, 0]\n    scores[response.preferred_answer - 1] = 1\n    scores[response.second_best_answer - 1] = .5\n    scores[response.worst_answer - 1] = 0\n    return scores\n\nsingle_agent = \"DR Single Agent - Tavily #-87e8a6c0\"\nmulti_agent_supervisor = \"DR Supervisor: Multi Agent - Tavily #-cd25e7e3\"\nmulti_agent_supervisor_v2 = \"DR Supervisor: Multi Agent - Tavily (v2) #-40967f53\"\nmulti_agent_workflow = \"DR MAW - Tavily #-c6818a83\"\n\n\n# evaluate_comparative(\n#     (single_agent_experiment_name, multi_agent_supervisor_experiment_name, multi_agent_workflow_experiment_name),  # Replace with the names/IDs of your experiments\n#     evaluators=[free_for_all_evaluator],\n#     randomize_order=True,\n# )\n\nevaluate_comparative(\n    (single_agent, multi_agent_supervisor_v2),  # Replace with the names/IDs of your experiments\n    evaluators=[head_to_head_evaluator],\n    randomize_order=True,\n)=====PARALLEL=====\nfrom open_deep_research.deep_researcher import deep_researcher_builder\nfrom langgraph.checkpoint.memory import MemorySaver\nimport uuid\nimport asyncio\nfrom langsmith import Client\n\nclient = Client()\n\ndataset_name = \"ODR: First Supervisor Parallelism\"\ndef right_parallelism_evaluator(\n    outputs: dict,\n    reference_outputs: dict,\n) -> dict:\n    return {\n        \"key\": \"right_parallelism\", \n        \"score\": len(outputs[\"output\"].values[\"supervisor_messages\"][-1].tool_calls) == reference_outputs[\"parallel\"]\n    }\n\nasync def target(inputs: dict):\n    graph = deep_researcher_builder.compile(checkpointer=MemorySaver())\n    config = {\n        \"configurable\": {\n            \"thread_id\": str(uuid.uuid4()),\n        }\n    }\n    # NOTE: Configure the right dataset and evaluators\n    config[\"configurable\"][\"max_structured_output_retries\"] = 3\n    config[\"configurable\"][\"allow_clarification\"] = False\n    config[\"configurable\"][\"max_concurrent_research_units\"] = 10\n    config[\"configurable\"][\"search_api\"] = \"tavily\"     # NOTE: We use Tavily to stay consistent\n    config[\"configurable\"][\"max_researcher_iterations\"] = 3\n    config[\"configurable\"][\"max_react_tool_calls\"] = 10\n    config[\"configurable\"][\"summarization_model\"] = \"openai:gpt-4.1-nano\"\n    config[\"configurable\"][\"summarization_model_max_tokens\"] = 8192\n    config[\"configurable\"][\"research_model\"] = \"openai:gpt-4.1\"\n    config[\"configurable\"][\"research_model_max_tokens\"] = 10000\n    config[\"configurable\"][\"compression_model\"] = \"openai:gpt-4.1-mini\"\n    config[\"configurable\"][\"compression_model_max_tokens\"] = 10000\n    config[\"configurable\"][\"final_report_model\"] = \"openai:gpt-4.1\"\n    config[\"configurable\"][\"final_report_model_max_tokens\"] = 10000\n    # NOTE: We do not use MCP tools to stay consistent\n    await graph.ainvoke(\n        {\"messages\": [{\"role\": \"user\", \"content\": inputs[\"messages\"][0][\"content\"]}]},\n        config\n    )\n    return graph.get_state(config, subgraphs=True).tasks[0].state\n\n\n\nasync def main():\n    return await client.aevaluate(\n        target,\n        data=dataset_name,\n        evaluators=[right_parallelism_evaluator],\n        experiment_prefix=f\"v1 #\",\n        max_concurrency=1,\n    )\n\nif __name__ == \"__main__\":\n    results = asyncio.run(main())\n    print(results)"
    }
  ]
}
```

### Event 10 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "find test -type f | sort && echo \"=====INIT=====\" && cat test/__init__.py && echo \"=====EXTRACT=====\" && cat test/extract_langsmith_data.py"
  },
  "output": [
    {
      "type": "text",
      "text": "test/__init__.py\ntest/evaluators.py\ntest/extract_langsmith_data.py\ntest/live/占位文件(可删)\ntest/offline/占位文件(可删)\ntest/pairwise_evaluation.py\ntest/prompts.py\ntest/run_evaluate.py\ntest/supervisor_parallel_evaluation.py\n=====INIT=====\n\"\"\"Evaluation scripts and coursework tests.\"\"\"\n=====EXTRACT=====\n#!/usr/bin/env python3\n\"\"\"Extract data from LangSmith and save to JSONL file with configurable dataset.\"\"\"\n\nimport os\nimport json\nimport argparse\nfrom langsmith import Client\nfrom dotenv import load_dotenv\n\nload_dotenv()\n\n\ndef extract_langsmith_data(project_name, model_name, dataset_name, api_key):\n    \"\"\"Extract data from LangSmith and save to JSONL file.\"\"\"\n    print(f\"Extracting data from LangSmith project: {project_name}\")\n    print(f\"Using dataset: {dataset_name}\")\n    \n    client = Client(api_key=api_key)\n    \n    # Read project to get reference dataset id\n    project_data = client.read_project(project_name=project_name)\n    \n    # Read reference dataset to get examples\n    examples_gen = client.list_examples(dataset_id=project_data.reference_dataset_id)\n    examples = []\n    for example in examples_gen:\n        examples.append(example)\n    examples_dict = {example.id: example for example in examples}\n    \n    # Read project runs to get runs inputs and outputs and reference_example_ids\n    output_runs = client.list_runs(\n        project_name=project_name,\n        is_root=True\n    )\n    \n    runs = []\n    for run in output_runs:\n        if run.outputs is not None and run.outputs.get(\"final_report\") is not None:\n            runs.append(run)\n    \n    output_jsonl = [\n        {\n            \"id\": examples_dict[run.reference_example_id].metadata[\"id\"],\n            \"prompt\": run.inputs[\"inputs\"][\"messages\"][0][\"content\"],\n            \"article\": run.outputs[\"final_report\"],\n        } for run in runs\n    ]\n    \n    # Write output_jsonl to JSONL file in test/expt_results directory\n    output_file_path = f\"test/expt_results/{dataset_name}_{model_name}.jsonl\"\n    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)\n    with open(output_file_path, 'w', encoding='utf-8') as f:\n        for item in output_jsonl:\n            f.write(json.dumps(item, ensure_ascii=False) + '\\n')\n    \n    print(f\"Data written to {output_file_path}\")\n    print(f\"Total records: {len(output_jsonl)}\")\n    return output_file_path\n\n\ndef main():\n    parser = argparse.ArgumentParser(description='Extract data from LangSmith project')\n    parser.add_argument('--project-name', required=True, help='LangSmith project name')\n    parser.add_argument('--model-name', required=True, help='Model name for output filename')\n    parser.add_argument('--dataset-name', required=True, help='Dataset name for output filename')\n    parser.add_argument('--api-key', help='LangSmith API key (defaults to LANGSMITH_API_KEY env var)')\n    \n    args = parser.parse_args()\n    \n    api_key = args.api_key or os.getenv('LANGSMITH_API_KEY')\n    if not api_key:\n        raise ValueError(\"API key must be provided via --api-key or LANGSMITH_API_KEY environment variable\")\n    \n    extract_langsmith_data(\n        project_name=args.project_name,\n        model_name=args.model_name,\n        dataset_name=args.dataset_name,\n        api_key=api_key\n    )\n\n\nif __name__ == \"__main__\":\n    main()\n"
    }
  ]
}
```

#### Tool bash — completed

````json
{
  "input": {
    "command": "cat pyproject.toml && echo \"=====LANGGRAPH=====\" && cat langgraph.json && echo \"=====README=====\" && sed -n '1,220p' README.md"
  },
  "output": [
    {
      "type": "text",
      "text": "[project]\nname = \"open_deep_research\"\nversion = \"0.0.16\"\ndescription = \"Planning, research, and report generation.\"\nauthors = [\n    { name = \"Lance Martin\" }\n]\nreadme = \"README.md\"\nlicense = { text = \"MIT\" }\nrequires-python = \">=3.10\"\ndependencies = [\n    \"langgraph>=0.5.4\",\n    \"langchain-community>=0.3.9\",\n    \"langchain-openai>=0.3.28\",\n    \"langchain-anthropic>=0.3.15\",\n    \"langchain-mcp-adapters>=0.1.6\",\n    \"langchain-deepseek>=0.1.2\",\n    \"langchain-tavily\",\n    \"langchain-groq>=0.2.4\",\n    \"openai>=1.99.2\",\n    \"tavily-python>=0.5.0\",\n    \"arxiv>=2.1.3\",\n    \"pymupdf>=1.25.3\",\n    \"xmltodict>=0.14.2\",\n    \"linkup-sdk>=0.2.3\",\n    \"duckduckgo-search>=3.0.0\",\n    \"exa-py>=1.8.8\",\n    \"requests>=2.32.3\",\n    \"beautifulsoup4==4.14.3\",\n    \"python-dotenv>=1.0.1\",\n    \"pytest\",\n    \"httpx>=0.24.0\",\n    \"markdownify>=0.11.6\",\n    \"azure-identity>=1.21.0\",\n    \"azure-search>=1.0.0b2\",\n    \"azure-search-documents>=11.5.2\",\n    \"rich>=13.0.0\",\n    \"langgraph-cli[inmem]>=0.3.1\",\n    \"langsmith>=0.3.37\",\n    \"langchain-google-vertexai>=2.0.25\",\n    \"langchain-google-genai>=2.1.5\",\n    \"ipykernel>=6.29.5\",\n    \"supabase>=2.15.3\",\n    \"mcp>=1.9.4\",\n    \"langchain-aws>=0.2.28\",\n    \"pandas>=2.3.1\",\n]\n\n[project.optional-dependencies]\ndev = [\"mypy>=1.11.1\", \"ruff>=0.6.1\"]\n\n[build-system]\nrequires = [\"setuptools>=73.0.0\", \"wheel\"]\nbuild-backend = \"setuptools.build_meta\"\n\n[tool.setuptools]\npackages = [\"open_deep_research\", \"test\"]\n\n[tool.setuptools.package-dir]\n\"open_deep_research\" = \"src/open_deep_research\"\n\"test\" = \"test\"\n\n[tool.setuptools.package-data]\n\"*\" = [\"py.typed\"]\n\n[tool.ruff]\nlint.select = [\n    \"E\",    # pycodestyle\n    \"F\",    # pyflakes\n    \"I\",    # isort\n    \"D\",    # pydocstyle\n    \"D401\", # First line should be in imperative mood\n    \"T201\",\n    \"UP\",\n]\nlint.ignore = [\n    \"UP006\",\n    \"UP007\",\n    \"UP035\",\n    \"D417\",\n    \"E501\",\n]\n\n[tool.ruff.lint.per-file-ignores]\n\"test/*\" = [\"D\", \"UP\"]\n\n[tool.ruff.lint.pydocstyle]\nconvention = \"google\"\n=====LANGGRAPH=====\n{\n    \"dockerfile_lines\": [],\n    \"graphs\": {\n      \"Deep Researcher\": \"./src/open_deep_research/deep_researcher.py:deep_researcher\"\n    },\n    \"python_version\": \"3.12\",\n    \"env\": \"./.env\",\n    \"dependencies\": [\n      \".\"\n    ],\n    \"auth\": {\n      \"path\": \"./src/security/auth.py:auth\"\n    }\n}=====README=====\n# 🔬 Open Deep Research\n\n<img width=\"1388\" height=\"298\" alt=\"full_diagram\" src=\"https://github.com/user-attachments/assets/12a2371b-8be2-4219-9b48-90503eb43c69\" />\n\nDeep research has broken out as one of the most popular agent applications. This is a simple, configurable, fully open source deep research agent that works across many model providers, search tools, and MCP servers. It's performance is on par with many popular deep research agents ([see Deep Research Bench leaderboard](https://huggingface.co/spaces/Ayanami0730/DeepResearch-Leaderboard)).\n\n<img width=\"817\" height=\"666\" alt=\"Screenshot 2025-07-13 at 11 21 12 PM\" src=\"https://github.com/user-attachments/assets/052f2ed3-c664-4a4f-8ec2-074349dcaa3f\" />\n\n### 🔥 Recent Updates\n\n**August 14, 2025**: See our free course [here](https://academy.langchain.com/courses/deep-research-with-langgraph) (and course repo [here](https://github.com/langchain-ai/deep_research_from_scratch)) on building open deep research.\n\n**August 7, 2025**: Added GPT-5 and updated the Deep Research Bench evaluation w/ GPT-5 results.\n\n**August 2, 2025**: Achieved #6 ranking on the [Deep Research Bench Leaderboard](https://huggingface.co/spaces/Ayanami0730/DeepResearch-Leaderboard) with an overall score of 0.4344. \n\n**July 30, 2025**: Read about the evolution from our original implementations to the current version in our [blog post](https://rlancemartin.github.io/2025/07/30/bitter_lesson/).\n\n**July 16, 2025**: Read more in our [blog](https://blog.langchain.com/open-deep-research/) and watch our [video](https://www.youtube.com/watch?v=agGiWUpxkhg) for a quick overview.\n\n### 🚀 Quickstart\n\n1. Clone the repository and activate a virtual environment:\n```bash\ngit clone https://github.com/langchain-ai/open_deep_research.git\ncd open_deep_research\nuv venv\nsource .venv/bin/activate  # On Windows: .venv\\Scripts\\activate\n```\n\n2. Install dependencies:\n```bash\nuv sync\n# or\nuv pip install -r pyproject.toml\n```\n\n3. Set up your `.env` file to customize the environment variables (for model selection, search tools, and other configuration settings):\n```bash\ncp .env.example .env\n```\n\n4. Launch agent with the LangGraph server locally:\n\n```bash\n# Install dependencies and start the LangGraph server\nuvx --refresh --from \"langgraph-cli[inmem]\" --with-editable . --python 3.12 langgraph dev --allow-blocking\n```\n\nThis will open the LangGraph Studio UI in your browser.\n\n```\n- 🚀 API: http://127.0.0.1:2024\n- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024\n- 📚 API Docs: http://127.0.0.1:2024/docs\n```\n\nAsk a question in the `messages` input field and click `Submit`. Select different configuration in the \"Manage Assistants\" tab.\n\n### ⚙️ Configurations\n\n#### LLM :brain:\n\nOpen Deep Research supports a wide range of LLM providers via the [init_chat_model() API](https://python.langchain.com/docs/how_to/chat_models_universal_init/). It uses LLMs for a few different tasks. See the below model fields in the [configuration.py](https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/configuration.py) file for more details. This can be accessed via the LangGraph Studio UI. \n\n- **Summarization** (default: `openai:gpt-4.1-mini`): Summarizes search API results\n- **Research** (default: `openai:gpt-4.1`): Power the search agent\n- **Compression** (default: `openai:gpt-4.1`): Compresses research findings\n- **Final Report Model** (default: `openai:gpt-4.1`): Write the final report\n\n> Note: the selected model will need to support [structured outputs](https://python.langchain.com/docs/integrations/chat/) and [tool calling](https://python.langchain.com/docs/how_to/tool_calling/).\n\n> Note: For OpenRouter: Follow [this guide](https://github.com/langchain-ai/open_deep_research/issues/75#issuecomment-2811472408) and for local models via Ollama  see [setup instructions](https://github.com/langchain-ai/open_deep_research/issues/65#issuecomment-2743586318).\n\n#### Search API :mag:\n\nOpen Deep Research supports a wide range of search tools. By default it uses the [Tavily](https://www.tavily.com/) search API. Has full MCP compatibility and work native web search for Anthropic and OpenAI. See the `search_api` and `mcp_config` fields in the [configuration.py](https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/configuration.py) file for more details. This can be accessed via the LangGraph Studio UI. \n\n#### Other \n\nSee the fields in the [configuration.py](https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/configuration.py) for various other settings to customize the behavior of Open Deep Research. \n\n### 📊 Evaluation\n\nOpen Deep Research is configured for evaluation with [Deep Research Bench](https://huggingface.co/spaces/Ayanami0730/DeepResearch-Leaderboard). This benchmark has 100 PhD-level research tasks (50 English, 50 Chinese), crafted by domain experts across 22 fields (e.g., Science & Tech, Business & Finance) to mirror real-world deep-research needs. It has 2 evaluation metrics, but the leaderboard is based on the RACE score. This uses LLM-as-a-judge (Gemini) to evaluate research reports against a golden set of reports compiled by experts across a set of metrics.\n\n#### Usage\n\n> Warning: Running across the 100 examples can cost ~$20-$100 depending on the model selection.\n\nThe dataset is available on [LangSmith via this link](https://smith.langchain.com/public/c5e7a6ad-fdba-478c-88e6-3a388459ce8b/d). To kick off evaluation, run the following command:\n\n```bash\n# Run comprehensive evaluation on LangSmith datasets\npython test/run_evaluate.py\n```\n\nThis will provide a link to a LangSmith experiment, which will have a name `YOUR_EXPERIMENT_NAME`. Once this is done, extract the results to a JSONL file that can be submitted to the Deep Research Bench.\n\n```bash\npython test/extract_langsmith_data.py --project-name \"YOUR_EXPERIMENT_NAME\" --model-name \"you-model-name\" --dataset-name \"deep_research_bench\"\n```\n\nThis creates `test/expt_results/deep_research_bench_model-name.jsonl` with the required format. Move the generated JSONL file to a local clone of the Deep Research Bench repository and follow their [Quick Start guide](https://github.com/Ayanami0730/deep_research_bench?tab=readme-ov-file#quick-start) for evaluation submission.\n\n#### Results \n\n| Name | Commit | Summarization | Research | Compression | Total Cost | Total Tokens | RACE Score | Experiment |\n|------|--------|---------------|----------|-------------|------------|--------------|------------|------------|\n| GPT-5 | [ca3951d](https://github.com/langchain-ai/open_deep_research/pull/168/commits) | openai:gpt-4.1-mini | openai:gpt-5 | openai:gpt-4.1 |  | 204,640,896 | 0.4943 | [Link](https://smith.langchain.com/o/ebbaf2eb-769b-4505-aca2-d11de10372a4/datasets/6e4766ca-613c-4bda-8bde-f64f0422bbf3/compare?selectedSessions=4d5941c8-69ce-4f3d-8b3e-e3c99dfbd4cc&baseline=undefined) |\n| Defaults | [6532a41](https://github.com/langchain-ai/open_deep_research/commit/6532a4176a93cc9bb2102b3d825dcefa560c85d9) | openai:gpt-4.1-mini | openai:gpt-4.1 | openai:gpt-4.1 | $45.98 | 58,015,332 | 0.4309 | [Link](https://smith.langchain.com/o/ebbaf2eb-769b-4505-aca2-d11de10372a4/datasets/6e4766ca-6[…]ons=cf4355d7-6347-47e2-a774-484f290e79bc&baseline=undefined) |\n| Claude Sonnet 4 | [f877ea9](https://github.com/langchain-ai/open_deep_research/pull/163/commits/f877ea93641680879c420ea991e998b47aab9bcc) | openai:gpt-4.1-mini | anthropic:claude-sonnet-4-20250514 | openai:gpt-4.1 | $187.09 | 138,917,050 | 0.4401 | [Link](https://smith.langchain.com/o/ebbaf2eb-769b-4505-aca2-d11de10372a4/datasets/6e4766ca-6[…]ons=04f6002d-6080-4759-bcf5-9a52e57449ea&baseline=undefined) |\n| Deep Research Bench Submission | [c0a160b](https://github.com/langchain-ai/open_deep_research/commit/c0a160b57a9b5ecd4b8217c3811a14d8eff97f72) | openai:gpt-4.1-nano | openai:gpt-4.1 | openai:gpt-4.1 | $87.83 | 207,005,549 | 0.4344 | [Link](https://smith.langchain.com/o/ebbaf2eb-769b-4505-aca2-d11de10372a4/datasets/6e4766ca-6[…]ons=e6647f74-ad2f-4cb9-887e-acb38b5f73c0&baseline=undefined) |\n\n### 🚀 Deployments and Usage\n\n#### LangGraph Studio\n\nFollow the [quickstart](#-quickstart) to start LangGraph server locally and test the agent out on LangGraph Studio.\n\n#### Hosted deployment\n \nYou can easily deploy to [LangGraph Platform](https://langchain-ai.github.io/langgraph/concepts/#deployment-options). \n\n#### Open Agent Platform\n\nOpen Agent Platform (OAP) is a UI from which non-technical users can build and configure their own agents. OAP is great for allowing users to configure the Deep Researcher with different MCP tools and search APIs that are best suited to their needs and the problems that they want to solve.\n\nWe've deployed Open Deep Research to our public demo instance of OAP. All you need to do is add your API Keys, and you can test out the Deep Researcher for yourself! Try it out [here](https://oap.langchain.com)\n\nYou can also deploy your own instance of OAP, and make your own custom agents (like Deep Researcher) available on it to your users.\n1. [Deploy Open Agent Platform](https://docs.oap.langchain.com/quickstart)\n2. [Add Deep Researcher to OAP](https://docs.oap.langchain.com/setup/agents)\n\n### Legacy Implementations 🏛️\n\nThe upstream `src/legacy/` implementations (`graph.py`, `multi_agent.py`) were removed from this fork in commit `a4d557a`. See the [upstream repository](https://github.com/langchain-ai/open_deep_research) for them.\n"
    }
  ]
}
````

### Event 11 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "grep -rn \"from test.evaluators\\|import evaluators\\|from test.prompts\\|test.prompts\\|eval_model\\|from test\\.\" --include=*.py . | grep -v '^./.git'"
  },
  "output": [
    {
      "type": "text",
      "text": "zsh:1: no matches found: --include=*.py\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "nl -ba test/evaluators.py | sed -n '1,220p'"
  },
  "output": [
    {
      "type": "text",
      "text": "     1\tfrom typing import cast\n     2\t\n     3\tfrom langchain_anthropic import ChatAnthropic\n     4\tfrom langchain_openai import ChatOpenAI\n     5\tfrom pydantic import BaseModel, Field\n     6\t\n     7\tfrom open_deep_research.utils import get_today_str\n     8\tfrom test.prompts import (\n     9\t    COMPLETENESS_PROMPT,\n    10\t    CORRECTNESS_PROMPT,\n    11\t    GROUNDEDNESS_PROMPT,\n    12\t    OVERALL_QUALITY_PROMPT,\n    13\t    RELEVANCE_PROMPT,\n    14\t    STRUCTURE_PROMPT,\n    15\t)\n    16\t\n    17\teval_model = ChatOpenAI(\n    18\t    model=\"gpt-4.1\",\n    19\t)\n    20\t\n    21\t\n    22\tdef _format_input_query(inputs: dict) -> str:\n    23\t    messages = inputs[\"messages\"]\n    24\t    if len(messages) == 1:\n    25\t        return messages[0][\"content\"]\n    26\t\n    27\t    role_to_string_format_map = {\n    28\t        \"user\": \"<user_input>\\n{content}\\n</user_input>\",\n    29\t        \"assistant\": \"<assistant_follow_up>\\n{content}\\n</assistant_follow_up>\",\n    30\t    }\n    31\t\n    32\t    return \"\\n\\n\".join(\n    33\t        [\n    34\t            role_to_string_format_map[message[\"role\"]].format(\n    35\t                content=message[\"content\"]\n    36\t            )\n    37\t            for message in messages\n    38\t        ]\n    39\t    )\n    40\t\n    41\t\n    42\tclass OverallQualityScore(BaseModel):\n    43\t    \"\"\"Score the overall quality of the report against specific criteria.\"\"\"\n    44\t\n    45\t    research_depth: int = Field(\n    46\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    47\t    )\n    48\t    source_quality: int = Field(\n    49\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    50\t    )\n    51\t    analytical_rigor: int = Field(\n    52\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    53\t    )\n    54\t    practical_value: int = Field(\n    55\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    56\t    )\n    57\t    balance_and_objectivity: int = Field(\n    58\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    59\t    )\n    60\t    writing_quality: int = Field(\n    61\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria (1 = doesn't meet at all, 5 = meets all criteria).\"\n    62\t    )\n    63\t\n    64\t\n    65\tdef eval_overall_quality(inputs: dict, outputs: dict):\n    66\t    query = _format_input_query(inputs)\n    67\t    final_report = outputs[\"final_report\"]\n    68\t    user_input_content = f\"\"\"User input: {query}\\n\\nReport: \\n\\n{final_report}\\n\\nEvaluate whether the report meets the criteria and provide detailed justification for your evaluation.\"\"\"\n    69\t    if isinstance(eval_model, ChatAnthropic):\n    70\t        user_input_content = [\n    71\t            {\n    72\t                \"type\": \"text\",\n    73\t                \"text\": user_input_content,\n    74\t                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n    75\t            }\n    76\t        ]\n    77\t    eval_result = cast(\n    78\t        OverallQualityScore,\n    79\t        eval_model.with_structured_output(OverallQualityScore).invoke(\n    80\t            [\n    81\t                {\n    82\t                    \"role\": \"system\",\n    83\t                    \"content\": OVERALL_QUALITY_PROMPT.format(today=get_today_str()),\n    84\t                },\n    85\t                {\"role\": \"user\", \"content\": user_input_content},\n    86\t            ]\n    87\t        ),\n    88\t    )\n    89\t    return [\n    90\t        {\"key\": \"research_depth_score\", \"score\": eval_result.research_depth / 5},\n    91\t        {\"key\": \"source_quality_score\", \"score\": eval_result.source_quality / 5},\n    92\t        {\"key\": \"analytical_rigor_score\", \"score\": eval_result.analytical_rigor / 5},\n    93\t        {\"key\": \"practical_value_score\", \"score\": eval_result.practical_value / 5},\n    94\t        {\n    95\t            \"key\": \"balance_and_objectivity_score\",\n    96\t            \"score\": eval_result.balance_and_objectivity / 5,\n    97\t        },\n    98\t        {\"key\": \"writing_quality_score\", \"score\": eval_result.writing_quality / 5},\n    99\t    ]\n   100\t\n   101\t\n   102\tclass RelevanceScore(BaseModel):\n   103\t    \"\"\"Score the report relevance against specific criteria.\"\"\"\n   104\t\n   105\t    reasoning: str = Field(\n   106\t        description=\"The reason for the score, including specific examples from the report.\"\n   107\t    )\n   108\t    score: int = Field(\n   109\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria for relevance (1 = doesn't meet at all, 5 = meets all criteria).\"\n   110\t    )\n   111\t\n   112\t\n   113\tdef eval_relevance(inputs: dict, outputs: dict):\n   114\t    query = _format_input_query(inputs)\n   115\t    final_report = outputs[\"final_report\"]\n   116\t    user_input_content = f\"\"\"User input: {query}\\n\\nReport: \\n\\n{final_report}\\n\\nEvaluate whether the report meets the criteria and provide detailed justification for your evaluation.\"\"\"\n   117\t    if isinstance(eval_model, ChatAnthropic):\n   118\t        user_input_content = [\n   119\t            {\n   120\t                \"type\": \"text\",\n   121\t                \"text\": user_input_content,\n   122\t                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n   123\t            }\n   124\t        ]\n   125\t\n   126\t    eval_result = cast(\n   127\t        RelevanceScore,\n   128\t        eval_model.with_structured_output(RelevanceScore).invoke(\n   129\t            [\n   130\t                {\n   131\t                    \"role\": \"system\",\n   132\t                    \"content\": RELEVANCE_PROMPT.format(today=get_today_str()),\n   133\t                },\n   134\t                {\"role\": \"user\", \"content\": user_input_content},\n   135\t            ]\n   136\t        ),\n   137\t    )\n   138\t    return {\n   139\t        \"key\": \"relevance_score\",\n   140\t        \"score\": eval_result.score / 5,\n   141\t        \"comment\": eval_result.reasoning,\n   142\t    }\n   143\t\n   144\t\n   145\tclass StructureScore(BaseModel):\n   146\t    \"\"\"Score the report structure against specific criteria.\"\"\"\n   147\t\n   148\t    reasoning: str = Field(\n   149\t        description=\"The reason for the score, including specific examples from the report.\"\n   150\t    )\n   151\t    score: int = Field(\n   152\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria for structure and flow (1 = doesn't meet at all, 5 = meets all criteria).\"\n   153\t    )\n   154\t\n   155\t\n   156\tdef eval_structure(inputs: dict, outputs: dict):\n   157\t    query = _format_input_query(inputs)\n   158\t    final_report = outputs[\"final_report\"]\n   159\t    user_input_content = STRUCTURE_PROMPT.format(\n   160\t        user_question=query, report=final_report, today=get_today_str()\n   161\t    )\n   162\t    if isinstance(eval_model, ChatAnthropic):\n   163\t        user_input_content = [\n   164\t            {\n   165\t                \"type\": \"text\",\n   166\t                \"text\": user_input_content,\n   167\t                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n   168\t            }\n   169\t        ]\n   170\t\n   171\t    eval_result = cast(\n   172\t        StructureScore,\n   173\t        eval_model.with_structured_output(StructureScore).invoke(\n   174\t            [{\"role\": \"user\", \"content\": user_input_content}]\n   175\t        ),\n   176\t    )\n   177\t    return {\n   178\t        \"key\": \"structure_and_cohesiveness_score\",\n   179\t        \"score\": eval_result.score / 5,\n   180\t        \"comment\": eval_result.reasoning,\n   181\t    }\n   182\t\n   183\t\n   184\tclass CorrectnessScore(BaseModel):\n   185\t    \"\"\"Score the report correctness against specific criteria.\"\"\"\n   186\t\n   187\t    reasoning: str = Field(\n   188\t        description=\"The reason for the score, including specific examples from the report.\"\n   189\t    )\n   190\t    score: int = Field(\n   191\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria for correctness (1 = doesn't meet at all, 5 = meets all criteria).\"\n   192\t    )\n   193\t\n   194\t\n   195\tdef eval_correctness(inputs: dict, outputs: dict, reference_outputs: dict):\n   196\t    query = _format_input_query(inputs)\n   197\t    final_report = outputs[\"final_report\"]\n   198\t    answer = reference_outputs[\"answer\"]\n   199\t    user_input_content = CORRECTNESS_PROMPT.format(\n   200\t        user_question=query, report=final_report, answer=answer, today=get_today_str()\n   201\t    )\n   202\t    if isinstance(eval_model, ChatAnthropic):\n   203\t        user_input_content = [\n   204\t            {\n   205\t                \"type\": \"text\",\n   206\t                \"text\": user_input_content,\n   207\t                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n   208\t            }\n   209\t        ]\n   210\t\n   211\t    eval_result = cast(\n   212\t        CorrectnessScore,\n   213\t        eval_model.with_structured_output(CorrectnessScore).invoke(\n   214\t            [{\"role\": \"user\", \"content\": user_input_content}]\n   215\t        ),\n   216\t    )\n   217\t    return {\n   218\t        \"key\": \"correctness_score\",\n   219\t        \"score\": eval_result.score / 5,\n   220\t        \"comment\": eval_result.reasoning,\n"
    }
  ]
}
```

### Event 12 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "nl -ba test/evaluators.py | sed -n '220,340p' && echo \"=====PROMPTS LINES=====\" && grep -n \"CORRECTNESS_PROMPT\\|RELEVANCE_PROMPT\\|STRUCTURE_PROMPT\\|GROUNDEDNESS_PROMPT\\|COMPLETENESS_PROMPT\\|OVERALL_QUALITY_PROMPT\" test/prompts.py"
  },
  "output": [
    {
      "type": "text",
      "text": "   220\t        \"comment\": eval_result.reasoning,\n   221\t    }\n   222\t\n   223\t\n   224\tclass GroundednessClaim(BaseModel):\n   225\t    \"\"\"A claim from the report, and whether or not it is grounded in the context\"\"\"\n   226\t\n   227\t    claim: str = Field(description=\"The claim extracted from the report.\")\n   228\t    grounded: bool = Field(description=\"Whether the claim is grounded in the context.\")\n   229\t\n   230\t\n   231\tclass GroundednessScore(BaseModel):\n   232\t    \"\"\"Extract the claims and whether they are grounded in the context\"\"\"\n   233\t\n   234\t    claims: list[GroundednessClaim] = Field(\n   235\t        description=\"All claims extracted from the report, and whether or not they are grounded in the context.\"\n   236\t    )\n   237\t\n   238\t\n   239\tdef eval_groundedness(inputs: dict, outputs: dict):\n   240\t    final_report = outputs[\"final_report\"]\n   241\t    context = str(outputs[\"raw_notes\"])\n   242\t\n   243\t    user_input_content = GROUNDEDNESS_PROMPT.format(\n   244\t        context=context, report=final_report, today=get_today_str()\n   245\t    )\n   246\t    if isinstance(eval_model, ChatAnthropic):\n   247\t        user_input_content = [\n   248\t            {\n   249\t                \"type\": \"text\",\n   250\t                \"text\": user_input_content,\n   251\t                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n   252\t            }\n   253\t        ]\n   254\t\n   255\t    eval_result = cast(\n   256\t        GroundednessScore,\n   257\t        eval_model.with_structured_output(GroundednessScore)\n   258\t        .with_retry(stop_after_attempt=3)\n   259\t        .invoke(\n   260\t            [\n   261\t                {\"role\": \"user\", \"content\": user_input_content},\n   262\t            ]\n   263\t        ),\n   264\t    )\n   265\t    # normalize to 0-1\n   266\t    grounded_claims = [claim for claim in eval_result.claims if claim.grounded]\n   267\t    return {\n   268\t        \"key\": \"groundedness_score\",\n   269\t        \"score\": len(grounded_claims) / len(eval_result.claims),\n   270\t        \"comment\": str(eval_result.claims),\n   271\t    }\n   272\t\n   273\t\n   274\tclass CompletenessScore(BaseModel):\n   275\t    \"\"\"Score the report completeness against specific criteria.\"\"\"\n   276\t\n   277\t    reasoning: str = Field(\n   278\t        description=\"The reason for the score, including specific examples from the report.\"\n   279\t    )\n   280\t    score: int = Field(\n   281\t        description=\"Integer score 1-5 showing whether the report meets the provided criteria for completeness (1 = doesn't meet at all, 5 = meets all criteria).\"\n   282\t    )\n   283\t\n   284\t\n   285\tdef eval_completeness(inputs: dict, outputs: dict):\n   286\t    query = _format_input_query(inputs)\n   287\t    final_report = outputs[\"final_report\"]\n   288\t    research_brief = outputs[\"research_brief\"]\n   289\t    user_input_content = COMPLETENESS_PROMPT.format(\n   290\t        user_question=query,\n   291\t        research_brief=research_brief,\n   292\t        report=final_report,\n   293\t        today=get_today_str(),\n   294\t    )\n   295\t    if isinstance(eval_model, ChatAnthropic):\n   296\t        user_input_content = [\n   297\t            {\n   298\t                \"type\": \"text\",\n   299\t                \"text\": user_input_content,\n   300\t                \"cache_control\": {\"type\": \"ephemeral\", \"ttl\": \"1h\"},\n   301\t            }\n   302\t        ]\n   303\t\n   304\t    eval_result = cast(\n   305\t        CompletenessScore,\n   306\t        eval_model.with_structured_output(CompletenessScore).invoke(\n   307\t            [{\"role\": \"user\", \"content\": user_input_content}]\n   308\t        ),\n   309\t    )\n   310\t    return {\n   311\t        \"key\": \"completeness_score\",\n   312\t        \"score\": eval_result.score / 5,\n   313\t        \"comment\": eval_result.reasoning,\n   314\t    }\n=====PROMPTS LINES=====\n1:OVERALL_QUALITY_PROMPT = \"\"\"You are an expert evaluator tasked with assessing the quality of research reports. Please evaluate the provided research report across multiple dimensions, provide scores, and offer a comprehensive assessment.\n95:CORRECTNESS_PROMPT = \"\"\"You are evaluating the correctness of a research report that was generated by a research agent.\n106:RELEVANCE_PROMPT = \"\"\"You are evaluating the relevance of a response to a user's input question. Please assess the answer against the following criteria, being especially strict about section relevance.\n131:STRUCTURE_PROMPT = \"\"\"You are evaluating the structure and flow of a response to a user's question. Your evaluation should focus on the following criteria:\n167:GROUNDEDNESS_PROMPT = \"\"\"\n215:COMPLETENESS_PROMPT = \"\"\"You are evaluating the completeness of a research report. Your evaluation should focus on the following criteria:\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "grep -rn \"from test.evaluators\\|import evaluators\\|from test.prompts\\|test\\.prompts\\|from test import\\|import test\\.\" --include=\"*.py\" . 2>/dev/null | grep -v \"/.git/\""
  },
  "output": [
    {
      "type": "text",
      "text": "./test/run_evaluate.py:2:from test.evaluators import eval_overall_quality, eval_relevance, eval_structure, eval_correctness, eval_groundedness, eval_completeness\n./test/evaluators.py:8:from test.prompts import (\n"
    }
  ]
}
```

### Event 13 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat docs/ai-use-log.yaml"
  },
  "output": [
    {
      "type": "text",
      "text": "# AI-use log: one entry per AI-assisted activity (course deliverable D1, kept up to date).\n# Maintained by humans; agents draft entries in their build reports.\n#\n# Entry fields:\n#   id:          AIU-NNN, never reused\n#   date:        YYYY-MM-DD, or the first and last day of the activity\n#   member:      team member who supervised the activity (owner nickname)\n#   purpose:     what the AI was asked to do\n#   prompt:      the main instruction given to the AI, lightly edited for clarity\n#   requirements: [REQ-NNN, ...] or []\n#   artifacts:   files or PRs produced or changed\n#   supervision: how the human checked or corrected the output\n#   transcript:  path under transcripts/, or null\nentries:\n  - id: AIU-001\n    date: \"2026-11-10\"\n    member: AlchemyHAN\n    purpose: >-\n      Check whether the reported problem exists in our code base and draft requirements for it.\n    prompt: >-\n      Our team is improving Open Deep Research. My assignment is the problem that some sub-agent\n      failures are not reported and the run goes straight to \"research complete\" (upstream issues\n      #283 and #284). Confirm whether this problem exists and is reasonable to address, design the\n      requirement, and write it as YAML that follows req-schema.json.\n    requirements: [REQ-002, REQ-004]\n    artifacts:\n      - docs/req/requirements.yaml\n    supervision: >-\n      The AI reproduced the defect with offline probes against the current code. The member\n      reviewed the draft, compared it with teammates' requirements to find overlaps, and decided\n      how responsibilities were split.\n    transcript: null\n\n  - id: AIU-002\n    date: \"2026-11-11\"\n    member: AlchemyHAN\n    purpose: >-\n      Consolidate the team's merged requirements into one consistent, schema-valid set.\n    prompt: >-\n      We have merged the team's requirements.yaml, but it still contains conflicts,\n      inconsistencies, formatting problems and uneven levels of detail; some parts are imprecise\n      or incomplete and others are redundant. Revise it as a whole: remove redundancy, split or\n      merge coupled requirements, resolve conflicts, and renumber the requirements from REQ-001.\n    requirements: [REQ-001, REQ-002, REQ-003, REQ-004, REQ-005, REQ-006, REQ-007, REQ-008, REQ-009, REQ-010]\n    artifacts:\n      - docs/req/requirements.yaml\n      - docs/req/req-schema.json\n    supervision: >-\n      Claims in each requirement were checked against the source code and upstream issues. The\n      member supplied the owners' nicknames, reviewed the result, removed revision-history notes,\n      and approved all ten requirements for the team.\n    transcript: null\n\n  - id: AIU-003\n    date: \"2026-11-11\"\n    member: AlchemyHAN\n    purpose: >-\n      Place the team's governance documents in the repository and turn them into one consistent\n      set of instructions for coding agents.\n    prompt: >-\n      Move the remaining requirements-engineering documents into their places in the project.\n      Then review them as a coding agent would read them: find inconsistencies, duplication and\n      conflicts, and improve and standardise these harness files. Use Python 3.12. We are still in\n      requirements engineering, so leave invariants and architecture content mostly empty and only\n      unify the format for later; move the architecture blueprint under docs/architecture.\n    requirements: []\n    artifacts:\n      - AGENTS.md\n      - Prompt.md\n      - .opencode/rules.md\n      - .agent/rules.md\n      - docs/architecture/\n      - docs/code-governance/\n      - README.md\n      - langgraph.json\n    supervision: >-\n      The member reviewed every change, decided which open items and placeholder notes to keep,\n      and asked for redundant text to be removed.\n    transcript: null\n\n  - id: AIU-004\n    date: \"2026-11-11\"\n    member: AlchemyHAN\n    purpose: >-\n      Add requirement validation to CI and shared editor settings.\n    prompt: >-\n      Make CI run validate_requirements.py, and add an .editorconfig that enforces Unix line\n      endings and sets the indentation.\n    requirements: []\n    artifacts:\n      - scripts/validate_requirements.py\n      - .github/workflows/ci.yml\n      - .github/dependabot.yml\n      - .python-version\n      - .editorconfig\n      - .gitattributes\n    supervision: >-\n      Every CI job was run locally with the same commands before the push, and the member\n      confirmed the result on GitHub.\n    transcript: null\n\n  - id: AIU-005\n    date: \"2026-11-11/2026-11-12\"\n    member: AlchemyHAN\n    purpose: >-\n      Design the coding-agent permission model and the OpenCode configuration that enforces it.\n    prompt: >-\n      Decide how the permissions are put into practice. Keep them practical rather than overly\n      strict: Build and Test must be able to run commands and commit, users may ask the agent to\n      push, reset or rebase, and models should be able to use read-only web tools and the Context7\n      MCP server. Add a separate role that only writes tests, so that Build only writes the\n      implementation.\n    requirements: []\n    artifacts:\n      - .opencode/permissions.jsonc\n      - .opencode/opencode.jsonc\n      - docs/architecture/permission-model.md\n      - docs/code-governance/mcp-tool-manifest.md\n    supervision: >-\n      The configuration was loaded with OpenCode 2.2.7 and the resolved rules were checked against\n      an acceptance matrix (83/83 cases). The member set the policy for each tier and reviewed the\n      role split.\n    transcript: null\n\n  - id: AIU-006\n    date: \"2026-11-12\"\n    member: AlchemyHAN\n    purpose: >-\n      Align the workflow with the team's software-architecture process and prepare templates for\n      every member's module sections.\n    prompt: >-\n      We are entering the SA phase: ASR, ADD with 2–3 candidate architectures per module, ADRs,\n      each member's module sections in the shared architecture and constraint documents,\n      integration into one blueprint, SA Review, then tests, implementation by a coding agent and\n      verification. Update the existing documents to follow this process, and provide templates\n      with one example entry each so that members can add their own content and we can integrate\n      it later.\n    requirements: []\n    artifacts:\n      - Prompt.md\n      - docs/architecture/\n      - docs/code-governance/structural-constraints.md\n      - docs/code-governance/verification-constraints.md\n      - docs/review-memo.md\n    supervision: >-\n      The member defined the process and reviewed the templates, keeping them free of\n      pre-assigned owners and of architecture content that belongs to the SA phase.\n    transcript: null\n\n  - id: AIU-007\n    date: \"2026-11-12\"\n    member: AlchemyHAN\n    purpose: >-\n      Draft team announcements and open the pull request for the changes above.\n    prompt: >-\n      Write a short notice for the team explaining what each member needs to do in the SA phase.\n      Then open a pull request and push the changes.\n    requirements: []\n    artifacts:\n      - https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/pull/4\n    supervision: >-\n      The member edited the announcement before sending it, and reviewed the commits and the PR\n      description; merging waits for two other members' approvals.\n    transcript: null\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "sed -n '1,120p' .opencode/permissions.jsonc && echo \"=====\" && ls -la docs/approvals 2>/dev/null || echo \"no approvals dir\""
  },
  "output": [
    {
      "type": "text",
      "text": "// OpenCode permission configuration for the four coding-agent roles (Plan, Test Author, Build, Verify).\n// Specification: docs/architecture/permission-model.md (authoritative). This file is human-owned.\n//\n// Loading: OpenCode does not load .opencode/permissions.jsonc by name. The symlink\n// .opencode/opencode.jsonc -> permissions.jsonc makes OpenCode load this file (verified on\n// OpenCode 2.2.7). Edit this file only; never replace the symlink with a copy.\n//\n// Policy: routine work, including read-only web and documentation lookups, is allowed;\n// risky but legitimate actions ask the human; only secrets, permission or approval\n// tampering, force-pushes and role-separation breaches are denied. Within each object the last matching pattern wins, so every object lists its\n// fallback first, then allows, then asks, then denies. \"*\" matches any characters, including\n// \"/\" and spaces, so \"*git push*\" also matches inside a chain such as \"x && git push\".\n{\n  \"$schema\": \"https://opencode.ai/config.json\",\n  \"default_agent\": \"plan\",\n\n  // Approved MCP servers (listed in docs/code-governance/mcp-tool-manifest.md).\n  // Context7: read-only library documentation. Optional higher rate limit: add\n  // \"headers\": { \"CONTEXT7_API_KEY\": \"{env:CONTEXT7_API_KEY}\" } and set the variable.\n  \"mcp\": {\n    \"context7\": {\n      \"type\": \"remote\",\n      \"url\": \"https://mcp.context7.com/mcp\"\n    }\n  },\n\n  // Agents not defined below (built-in helpers, plugin agents) get nothing.\n  \"permission\": {\n    \"*\": \"deny\"\n  },\n\n  \"agent\": {\n    \"plan\": {\n      \"description\": \"Plan role: software architecture. Drafts ASR, ADD entries, ADRs and module sections of the architecture and constraint documents. Never writes source or tests.\",\n      \"mode\": \"primary\",\n      \"permission\": {\n        \"*\": \"ask\",\n        \"question\": \"allow\",\n        \"todowrite\": \"allow\",\n        \"doom_loop\": \"ask\",\n        \"glob\": \"allow\",\n        \"grep\": \"allow\",\n        \"list\": \"allow\",\n        \"lsp\": \"allow\",\n        \"webfetch\": \"allow\",\n        \"websearch\": \"allow\",\n        \"context7_*\": \"allow\",\n        \"task\": { \"*\": \"deny\", \"explore\": \"allow\" },\n        \"read\": {\n          \"*\": \"allow\",\n          \"*.env*\": \"deny\",\n          \"*.env.example\": \"allow\",\n          \".git/*\": \"deny\"\n        },\n        \"edit\": {\n          \"*\": \"allow\",\n          \"AGENTS.md\": \"ask\",\n          \"Prompt.md\": \"ask\",\n          \".agent/*\": \"ask\",\n          \".github/*\": \"ask\",\n          \"pyproject.toml\": \"ask\",\n          \"uv.lock\": \"ask\",\n          \"docs/req/*\": \"ask\",\n          \"docs/architecture/permission-model.md\": \"ask\",\n          \"docs/code-governance/mcp-tool-manifest.md\": \"ask\",\n          \"docs/ai-use-log.yaml\": \"ask\",\n          \"docs/review-memo.md\": \"ask\",\n          \"docs/bug-diary.md\": \"ask\",\n          \"docs/debt-register.md\": \"ask\",\n          \"docs/architecture/adr/000-template.md\": \"deny\",\n          \"src/*\": \"deny\",\n          \"test/*\": \"deny\",\n          \"scripts/*\": \"deny\",\n          \".opencode/*\": \"deny\",\n          \"opencode.json*\": \"deny\",\n          \"docs/approvals/*\": \"deny\",\n          \"*.env*\": \"deny\"\n        },\n        \"bash\": {\n          \"*\": \"ask\",\n          \"ls*\": \"allow\",\n          \"pwd\": \"allow\",\n          \"cat *\": \"allow\",\n          \"head *\": \"allow\",\n          \"tail *\": \"allow\",\n          \"wc *\": \"allow\",\n          \"rg *\": \"allow\",\n          \"grep *\": \"allow\",\n          \"find *\": \"allow\",\n          \"tree*\": \"allow\",\n          \"git status*\": \"allow\",\n          \"git diff*\": \"allow\",\n          \"git log*\": \"allow\",\n          \"git show*\": \"allow\",\n          \"git branch*\": \"allow\",\n          \"git blame*\": \"allow\",\n          \"git add *\": \"allow\",\n          \"git commit *\": \"allow\",\n          \"uv sync*\": \"allow\",\n          \"uv run pytest*\": \"allow\",\n          \"uv run python -m pytest*\": \"allow\",\n          \"uv run ruff check*\": \"allow\",\n          \"uv run mypy*\": \"allow\",\n          \"uv run python scripts/validate_requirements.py*\": \"allow\",\n          \"*>*\": \"ask\",\n          \"*rm *\": \"ask\",\n          \"*git push*\": \"ask\",\n          \"*git reset*\": \"ask\",\n          \"*git rebase*\": \"ask\",\n          \"*git checkout*\": \"ask\",\n          \"*git stash*\": \"ask\",\n          \"*uv add*\": \"ask\",\n          \"*uv remove*\": \"ask\",\n          \"*pip install*\": \"ask\",\n          \"*curl *\": \"ask\",\n          \"*wget *\": \"ask\",\n          \"*push --force*\": \"deny\",\n          \"*push -f*\": \"deny\",\n          \"*sudo *\": \"deny\",\n          \"*.env*\": \"deny\",\n=====\nno approvals dir\n"
    }
  ]
}
```

### Event 14 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "nl -ba test/run_evaluate.py | sed -n '1,90p' && echo \"=====PROMPTS 90-110=====\" && nl -ba test/prompts.py | sed -n '90,112p'"
  },
  "output": [
    {
      "type": "text",
      "text": "     1\tfrom langsmith import Client\n     2\tfrom test.evaluators import eval_overall_quality, eval_relevance, eval_structure, eval_correctness, eval_groundedness, eval_completeness\n     3\tfrom dotenv import load_dotenv\n     4\timport asyncio\n     5\tfrom open_deep_research.deep_researcher import deep_researcher_builder\n     6\tfrom langgraph.checkpoint.memory import MemorySaver\n     7\timport uuid\n     8\t\n     9\tload_dotenv(\"../.env\")\n    10\t\n    11\tclient = Client()\n    12\t\n    13\t# NOTE: Configure the right dataset and evaluators\n    14\tdataset_name = \"Deep Research Bench\"\n    15\tevaluators = [eval_overall_quality, eval_relevance, eval_structure, eval_correctness, eval_groundedness, eval_completeness]\n    16\t# NOTE: Configure the right parameters for the experiment, these will be logged in the metadata\n    17\tmax_structured_output_retries = 3\n    18\tallow_clarification = False\n    19\tmax_concurrent_research_units = 10\n    20\tsearch_api = \"tavily\" # NOTE: We use Tavily to stay consistent\n    21\tmax_researcher_iterations = 6\n    22\tmax_react_tool_calls = 10\n    23\tsummarization_model = \"openai:gpt-4.1-mini\"\n    24\tsummarization_model_max_tokens = 8192\n    25\tresearch_model = \"openai:gpt-5\" # \"anthropic:claude-sonnet-4-20250514\"\n    26\tresearch_model_max_tokens = 10000\n    27\tcompression_model = \"openai:gpt-4.1\"\n    28\tcompression_model_max_tokens = 10000\n    29\tfinal_report_model = \"openai:gpt-4.1\"\n    30\tfinal_report_model_max_tokens = 10000\n    31\t\n    32\tasync def target(\n    33\t    inputs: dict,\n    34\t):\n    35\t    graph = deep_researcher_builder.compile(checkpointer=MemorySaver())\n    36\t    config = {\n    37\t        \"configurable\": {\n    38\t            \"thread_id\": str(uuid.uuid4()),\n    39\t        }\n    40\t    }\n    41\t    # NOTE: Configure the right dataset and evaluators\n    42\t    config[\"configurable\"][\"max_structured_output_retries\"] = max_structured_output_retries\n    43\t    config[\"configurable\"][\"allow_clarification\"] = allow_clarification\n    44\t    config[\"configurable\"][\"max_concurrent_research_units\"] = max_concurrent_research_units\n    45\t    config[\"configurable\"][\"search_api\"] = search_api\n    46\t    config[\"configurable\"][\"max_researcher_iterations\"] = max_researcher_iterations\n    47\t    config[\"configurable\"][\"max_react_tool_calls\"] = max_react_tool_calls\n    48\t    config[\"configurable\"][\"summarization_model\"] = summarization_model\n    49\t    config[\"configurable\"][\"summarization_model_max_tokens\"] = summarization_model_max_tokens\n    50\t    config[\"configurable\"][\"research_model\"] = research_model\n    51\t    config[\"configurable\"][\"research_model_max_tokens\"] = research_model_max_tokens\n    52\t    config[\"configurable\"][\"compression_model\"] = compression_model\n    53\t    config[\"configurable\"][\"compression_model_max_tokens\"] = compression_model_max_tokens\n    54\t    config[\"configurable\"][\"final_report_model\"] = final_report_model\n    55\t    config[\"configurable\"][\"final_report_model_max_tokens\"] = final_report_model_max_tokens\n    56\t    # NOTE: We do not use MCP tools to stay consistent\n    57\t    final_state = await graph.ainvoke(\n    58\t        {\"messages\": [{\"role\": \"user\", \"content\": inputs[\"messages\"][0][\"content\"]}]},\n    59\t        config\n    60\t    )\n    61\t    return final_state\n    62\t\n    63\tasync def main():\n    64\t    return await client.aevaluate(\n    65\t        target,\n    66\t        data=dataset_name,\n    67\t        evaluators=evaluators,\n    68\t        experiment_prefix=f\"ODR GPT-5, Tavily Search\",\n    69\t        max_concurrency=10,\n    70\t        metadata={\n    71\t            \"max_structured_output_retries\": max_structured_output_retries,\n    72\t            \"allow_clarification\": allow_clarification,\n    73\t            \"max_concurrent_research_units\": max_concurrent_research_units,\n    74\t            \"search_api\": search_api,\n    75\t            \"max_researcher_iterations\": max_researcher_iterations,\n    76\t            \"max_react_tool_calls\": max_react_tool_calls,\n    77\t            \"summarization_model\": summarization_model,\n    78\t            \"summarization_model_max_tokens\": summarization_model_max_tokens,\n    79\t            \"research_model\": research_model,\n    80\t            \"research_model_max_tokens\": research_model_max_tokens,\n    81\t            \"compression_model\": compression_model,\n    82\t            \"compression_model_max_tokens\": compression_model_max_tokens,\n    83\t            \"final_report_model\": final_report_model,\n    84\t            \"final_report_model_max_tokens\": final_report_model_max_tokens,\n    85\t        }\n    86\t    )\n    87\t\n    88\tif __name__ == \"__main__\":\n    89\t    results = asyncio.run(main())\n    90\t    print(results)\n=====PROMPTS 90-110=====\n    90\t\n    91\tNow, please evaluate the research report.\n    92\t\"\"\"\n    93\t\n    94\t\n    95\tCORRECTNESS_PROMPT = \"\"\"You are evaluating the correctness of a research report that was generated by a research agent.\n    96\t\n    97\tYou will be provided with the question, the report, and the answer from an independent authority.\n    98\t\n    99\tScore the report from 1-5 on how well it mirrors the answer from the authority. \n   100\tWe expect the report to contain more information that is not in the answer, that's perfectly okay.\n   101\tThey likely won't be perfectly the same, but they should have the same themes and ideas to get a high score.\n   102\t\n   103\tUse your best judgement when comparing the answer to the report!\n   104\t\"\"\"\n   105\t\n   106\tRELEVANCE_PROMPT = \"\"\"You are evaluating the relevance of a response to a user's input question. Please assess the answer against the following criteria, being especially strict about section relevance.\n   107\t\n   108\t1. Topic Relevance (Overall): Does the response directly address the user's input questions thoroughly?\n   109\t\n   110\t2. Section Relevance (Critical): CAREFULLY assess each individual section for relevance to the main topic:\n   111\t   - Identify each section by its ## header\n   112\t   - For each section, determine if it is directly relevant to the primary topic\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "git log --oneline main..HEAD 2>/dev/null; git merge-base --is-ancestor main HEAD && echo \"branch contains main\" || echo \"branch does not contain main\"; echo \"---\"; git log --oneline origin/main..HEAD 2>/dev/null | head; echo \"---review memo head---\"; sed -n '1,80p' docs/review-memo.md"
  },
  "output": [
    {
      "type": "text",
      "text": "branch contains main\n---\n---review memo head---\n# Review Memo\n\n> **Purpose:** Records of SA Reviews (Gate 1), pull request reviews (Gate 3) and the human reviews named in a requirement's fit criterion (`automated: false` checks).\n> **Maintained by:** reviewers.\n> **Last updated:** 2026-11-12\n\n## SA Review Template\n\n### SA-NNN: <scope, e.g. architecture of all modules>\n\n- **Date:** YYYY-MM-DD\n- **Participants:** <names>\n- **Reviewed:** ADR-NNN, EVAL-NNN, module sections in `invariants.md`, `memory-design.md`, `runtime-policy-catalog.md`, `structural-constraints.md` §10, `verification-constraints.md` §7, `trace-matrix.md`\n\n| Item | Finding | Resolution |\n|---|---|---|\n| ADR-NNN | | |\n\n- **Decision per ADR:** ADR-NNN Accepted | changes requested\n- **Outcome:** Gate 1 passed for REQ-NNN, ... | another review needed\n\n## PR Review Template\n\n### PR #NNN: <title>\n\n- **Requirements:** REQ-NNN\n- **Author / reviewers:** <names>\n- **Date:** YYYY-MM-DD\n- **Verification evidence checked:** `docs/test-reports/<task-id>.md`, CI run link\n- **Findings:** issues raised and how each was resolved.\n- **Decision:** approved | changes requested\n\n## Requirement Review Template\n\n### REVIEW-NNN: <requirement and check, e.g. REQ-007 C-005 search provider configuration review>\n\n- **Reviewer:** <name>\n- **Date:** YYYY-MM-DD\n- **Procedure:** what the reviewer did.\n- **Verdict:** PASS | FAIL | NOT_RUN | BLOCKED | N/A, with reasons.\n\n## Records\n"
    }
  ]
}
```

### Event 15 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "grep -n '\"test-author\"\\|\"build\"\\|\"verify\"\\|\"edit\"' .opencode/permissions.jsonc | sed -n '1,80p'"
  },
  "output": [
    {
      "type": "text",
      "text": "55:        \"edit\": {\n128:    \"test-author\": {\n150:        \"edit\": {\n227:    \"build\": {\n249:        \"edit\": {\n322:    \"verify\": {\n344:        \"edit\": {\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "sed -n '100,230p' .opencode/permissions.jsonc"
  },
  "output": [
    {
      "type": "text",
      "text": "          \"uv run pytest*\": \"allow\",\n          \"uv run python -m pytest*\": \"allow\",\n          \"uv run ruff check*\": \"allow\",\n          \"uv run mypy*\": \"allow\",\n          \"uv run python scripts/validate_requirements.py*\": \"allow\",\n          \"*>*\": \"ask\",\n          \"*rm *\": \"ask\",\n          \"*git push*\": \"ask\",\n          \"*git reset*\": \"ask\",\n          \"*git rebase*\": \"ask\",\n          \"*git checkout*\": \"ask\",\n          \"*git stash*\": \"ask\",\n          \"*uv add*\": \"ask\",\n          \"*uv remove*\": \"ask\",\n          \"*pip install*\": \"ask\",\n          \"*curl *\": \"ask\",\n          \"*wget *\": \"ask\",\n          \"*push --force*\": \"deny\",\n          \"*push -f*\": \"deny\",\n          \"*sudo *\": \"deny\",\n          \"*.env*\": \"deny\",\n          \"*.opencode*\": \"deny\",\n          \"*opencode.json*\": \"deny\",\n          \"*docs/approvals*\": \"deny\"\n        }\n      }\n    },\n\n    \"test-author\": {\n      \"description\": \"Test Author role: after Gate 1, writes the tests in the approved test plan, confirms they fail on the baseline and records the baseline run. Never changes source code.\",\n      \"mode\": \"primary\",\n      \"permission\": {\n        \"*\": \"ask\",\n        \"question\": \"allow\",\n        \"todowrite\": \"allow\",\n        \"doom_loop\": \"ask\",\n        \"glob\": \"allow\",\n        \"grep\": \"allow\",\n        \"list\": \"allow\",\n        \"lsp\": \"allow\",\n        \"webfetch\": \"allow\",\n        \"websearch\": \"allow\",\n        \"context7_*\": \"allow\",\n        \"task\": { \"*\": \"deny\", \"explore\": \"allow\" },\n        \"read\": {\n          \"*\": \"allow\",\n          \"*.env*\": \"deny\",\n          \"*.env.example\": \"allow\",\n          \".git/*\": \"deny\"\n        },\n        \"edit\": {\n          \"*\": \"allow\",\n          \"AGENTS.md\": \"ask\",\n          \"Prompt.md\": \"ask\",\n          \".agent/*\": \"ask\",\n          \".github/*\": \"ask\",\n          \"pyproject.toml\": \"ask\",\n          \"uv.lock\": \"ask\",\n          \"docs/req/*\": \"ask\",\n          \"docs/code-governance/*\": \"ask\",\n          \"docs/architecture/*\": \"ask\",\n          \"docs/ai-use-log.yaml\": \"ask\",\n          \"docs/review-memo.md\": \"ask\",\n          \"docs/bug-diary.md\": \"ask\",\n          \"docs/debt-register.md\": \"ask\",\n          \"src/*\": \"deny\",\n          \"scripts/*\": \"deny\",\n          \"test/*\": \"deny\",\n          \"test/offline/*\": \"allow\",\n          \"test/live/*\": \"allow\",\n          \".opencode/*\": \"deny\",\n          \"opencode.json*\": \"deny\",\n          \"docs/approvals/*\": \"deny\",\n          \"*.env*\": \"deny\"\n        },\n        \"bash\": {\n          \"*\": \"ask\",\n          \"ls*\": \"allow\",\n          \"pwd\": \"allow\",\n          \"cat *\": \"allow\",\n          \"head *\": \"allow\",\n          \"tail *\": \"allow\",\n          \"wc *\": \"allow\",\n          \"rg *\": \"allow\",\n          \"grep *\": \"allow\",\n          \"find *\": \"allow\",\n          \"tree*\": \"allow\",\n          \"git status*\": \"allow\",\n          \"git diff*\": \"allow\",\n          \"git log*\": \"allow\",\n          \"git show*\": \"allow\",\n          \"git branch*\": \"allow\",\n          \"git blame*\": \"allow\",\n          \"git add *\": \"allow\",\n          \"git commit *\": \"allow\",\n          \"git switch*\": \"allow\",\n          \"uv sync*\": \"allow\",\n          \"uv run pytest*\": \"allow\",\n          \"uv run python -m pytest*\": \"allow\",\n          \"uv run ruff check*\": \"allow\",\n          \"uv run ruff format test/offline*\": \"allow\",\n          \"uv run ruff format test/live*\": \"allow\",\n          \"uv run mypy*\": \"allow\",\n          \"uv run python scripts/validate_requirements.py*\": \"allow\",\n          \"*>*\": \"ask\",\n          \"*rm *\": \"ask\",\n          \"*git push*\": \"ask\",\n          \"*git reset*\": \"ask\",\n          \"*git rebase*\": \"ask\",\n          \"*git checkout*\": \"ask\",\n          \"*git stash*\": \"ask\",\n          \"*uv add*\": \"ask\",\n          \"*uv remove*\": \"ask\",\n          \"*pip install*\": \"ask\",\n          \"*curl *\": \"ask\",\n          \"*wget *\": \"ask\",\n          \"*push --force*\": \"deny\",\n          \"*push -f*\": \"deny\",\n          \"*sudo *\": \"deny\",\n          \"*.env*\": \"deny\",\n          \"*.opencode*\": \"deny\",\n          \"*opencode.json*\": \"deny\",\n          \"*docs/approvals*\": \"deny\"\n        }\n      }\n    },\n\n    \"build\": {\n      \"description\": \"Build role: after Gate 2, implements the code until the approved tests pass, runs the checks and writes a build report. Never changes tests.\",\n      \"mode\": \"primary\",\n      \"permission\": {\n"
    }
  ]
}
```

### Event 16 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "sed -n '249,290p' .opencode/permissions.jsonc"
  },
  "output": [
    {
      "type": "text",
      "text": "        \"edit\": {\n          \"*\": \"allow\",\n          \"AGENTS.md\": \"ask\",\n          \"Prompt.md\": \"ask\",\n          \".agent/*\": \"ask\",\n          \".github/*\": \"ask\",\n          \"pyproject.toml\": \"ask\",\n          \"uv.lock\": \"ask\",\n          \"docs/req/*\": \"ask\",\n          \"docs/code-governance/*\": \"ask\",\n          \"docs/architecture/*\": \"ask\",\n          \"docs/ai-use-log.yaml\": \"ask\",\n          \"docs/review-memo.md\": \"ask\",\n          \"docs/bug-diary.md\": \"ask\",\n          \"docs/debt-register.md\": \"ask\",\n          \"test/offline/*\": \"deny\",\n          \"test/live/*\": \"deny\",\n          \".opencode/*\": \"deny\",\n          \"opencode.json*\": \"deny\",\n          \"docs/approvals/*\": \"deny\",\n          \"*.env*\": \"deny\"\n        },\n        \"bash\": {\n          \"*\": \"ask\",\n          \"ls*\": \"allow\",\n          \"pwd\": \"allow\",\n          \"cat *\": \"allow\",\n          \"head *\": \"allow\",\n          \"tail *\": \"allow\",\n          \"wc *\": \"allow\",\n          \"rg *\": \"allow\",\n          \"grep *\": \"allow\",\n          \"find *\": \"allow\",\n          \"tree*\": \"allow\",\n          \"git status*\": \"allow\",\n          \"git diff*\": \"allow\",\n          \"git log*\": \"allow\",\n          \"git show*\": \"allow\",\n          \"git branch*\": \"allow\",\n          \"git blame*\": \"allow\",\n          \"git add *\": \"allow\",\n          \"git commit *\": \"allow\",\n"
    }
  ]
}
```

### Event 17 — OpenCode (plan)

## 0. 执行状态说明

当前会话处于 **Plan mode（只读）**，系统禁止任何文件修改。因此本轮**未写入任何文件、未创建 ADR/EVAL/测试、未提交或推送**。下面是可直接执行的 Phase 1 SA 草案计划；切换到 Build 模式后可逐项落盘。

## 1. 角色、分支、工作区与权限核对

| 项 | 核对结果 |
|---|---|
| 角色 | Plan；只写 SA 文档，不写源码/测试/审批记录 |
| 分支 | `docs/sa-evaluation`，工作区干净，包含 `main` |
| 模块路径 | 按蓝图 §4：`test/evaluation/` |
| 需求状态 | REQ-009 v1.1、REQ-010 v1.1 均为 `approved`，owner `DopplerXD` |
| Plan 可写 | `docs/architecture/*`（除 `permission-model.md`）、`structural-constraints.md`、`verification-constraints.md` |
| Plan 不可写 | `src/*`、`test/*`、`scripts/*`、`docs/approvals/*`、`.opencode/*` |
| 待人工处理 | README 文档与 `docs/ai-use-log.yaml` 属于人类/Build 阶段；本轮只在聊天给建议条目 |

发现的文档措辞问题（不阻塞，但需集成时确认）：`structural-constraints.md` §1 把顶层 `test/` 标为“新工作不放这里”，而蓝图 §4 明确 evaluation 模块路径为 `test/evaluation/`。建议 §10 明确 `test/evaluation/` 是例外，`test/` 下其余基线脚本不新增逻辑。

## 2. 基线代码核对（引用当前代码位置）

| 问题 | 位置 | 结论 |
|---|---|---|
| 导入副作用 | `test/evaluators.py:17-19` | 模块导入即构造 `ChatOpenAI(model="gpt-4.1")`；无 key/无网络时导入行为不可控 |
| correctness 输入丢失 | `test/prompts.py:95-104`；`test/evaluators.py:199-201` | `CORRECTNESS_PROMPT` 完全没有 `{user_question}`/`{report}`/`{answer}` 占位符，`format()` 的实参被静默忽略 |
| 评分未校验 | `test/evaluators.py:90-98, 140, 179, 219, 312` | 整数评分直接 `/5`，0/6/布尔/字符串/分数会得到越界或非法分数 |
| groundedness 除零 | `test/evaluators.py:265-270` | `len(grounded)/len(claims)`，空 claims 触发 `ZeroDivisionError` |
| 缺输入直接抛异常 | `test/evaluators.py:196-198, 239-244, 286-293` | 缺 `reference_outputs["answer"]`、`raw_notes`、`research_brief` 时抛 `KeyError` |
| 单指标异常中断整体 | `test/evaluators.py` 各 `eval_*` 无隔离 | 一个指标异常会中断该 evaluator，无法返回“其余指标仍被评估” |
| 只跑研究图 | `test/run_evaluate.py:32-61, 64-67` | `target()` 编译并调用完整 research graph；`aevaluate` 只接受数据集 |
| 入口导入副作用 | `test/run_evaluate.py:9-11` | `load_dotenv("../.env")`、`Client()` 在导入时执行；离线测试不得导入此模块 |
| 相邻脚本 | `test/pairwise_evaluation.py`、`test/supervisor_parallel_evaluation.py`、`test/extract_langsmith_data.py` | 不在 REQ-009/010 范围，本次不改 |

## 3. ASR 映射

**REQ-009（invariant, safety_relevant）**

| 准则 | 架构含义 |
|---|---|
| C-001 | 每个指标必须把其定义域输入完整送入 judge；correctness 必须修占位符 |
| C-002 | 评分必须是严格整数 1–5；`1→0.2`、`5→1.0`；非法值 → `not_evaluable`, `score=None` |
| C-003 | 缺 reference/brief/evidence 只影响依赖该输入的指标 |
| C-004 | 空 claims → `not_evaluable`；单指标异常隔离；2/4 grounded → 0.5 |
| M-001 | 任何结果 score 不得越界；`out_of_range_score_count == 0` |

**REQ-010（functional）**

| 准则 | 架构含义 |
|---|---|
| C-001 | 评估入口只读 question/report，不导入/调用 research graph、search provider；结果标识原报告 |
| C-002 | 空白 report/question 在调用任何 evaluator 前拒绝 |
| C-003 | README 可用性为人工检查，证据进 `docs/review-memo.md` |

## 4. ADD 方案比较（计划写入 `evaluation-table.md` 的 EVAL-001）

| 选项 | 方案 | 正确性 | 复用 | 耦合 | 基准入口兼容 | 离线可测 | 复杂度 |
|---|---|---|---|---|---|---|---|
| A | 原地加固 `test/evaluators.py`，新增 `test/evaluate_report.py` | 中 | 高 | 高 | 高 | 中 | 低 |
| **B（推荐）** | 新建 `test/evaluation/` 核心包 + `test/evaluators.py` 兼容适配器；`run_evaluate.py` 不改 | 高 | 高 | 低 | 高 | 高 | 中 |
| C | 新建独立评估服务并复制 evaluator 逻辑，基线条目不动 | 低（REQ-009 修不到基准链路） | 低 | 低 | 低 | 高 | 高 |

**推荐 B**：核心逻辑与 LangSmith 适配分离；`test/evaluators.py` 保留同名函数作为薄适配器，`test/run_evaluate.py` 无需改动；judge 惰性构造，可注入 fake judge，完全离线可测；满足蓝图模块边界。

**待人工决定**：见第 9 节。

## 5. Proposed ADR-001 结构与接口

文件：`docs/architecture/adr/001-evaluation-module.md`，状态 `Proposed`，EVAL-001，Owner `DopplerXD`。

**建议包结构**

```text
test/evaluation/
  __init__.py
  types.py          # MetricStatus, MetricResult, EvaluationRequest, EvaluationResult, EvaluationInputError
  validation.py     # strict_rating(), groundedness_ratio(), input presence checks
  judge.py          # Judge protocol + lazy default_judge()
  metrics.py        # per-metric deterministic evaluation with isolation
  entry.py          # evaluate_existing_report(...)
  evaluate_report.py# CLI main()
test/evaluators.py  # 兼容适配器，保留基线函数名
```

**公共接口（ADR §5）**

```python
class MetricStatus(str, Enum):
    SCORED = "scored"
    NOT_EVALUABLE = "not_evaluable"

@dataclass(frozen=True)
class MetricResult:
    metric: str                  # baseline key, e.g. "correctness_score"
    status: MetricStatus
    score: float | None          # None iff NOT_EVALUABLE
    reason: str

@dataclass(frozen=True)
class EvaluationResult:
    report_id: str
    report_sha256: str
    metrics: tuple[MetricResult, ...]
    judge_model: str | None

def evaluate_existing_report(
    question: str,
    report: str,
    *,
    reference_answer: str | None = None,
    research_brief: str | None = None,
    evidence: str | None = None,
    report_id: str | None = None,
    judge: Judge | None = None,
) -> EvaluationResult: ...
```

`Judge` 协议：`invoke(messages, schema) -> BaseModel`。`default_judge()` 在调用时才构造 `ChatOpenAI`，模块导入不构造客户端、不读 key。

**严格评分校验**

- 仅接受 `type(value) is int` 且 `1 <= value <= 5`；显式拒绝 `bool`、`float`（含 `4.0`）、`str`、`Decimal`、`NaN`/`inf`、`None`。
- 合法：`score = value / 5`；非法：`status=NOT_EVALUABLE`, `score=None`, `reason="invalid_rating:<value>"`。
- groundedness：claims 为空或非 list → `NOT_EVALUABLE`, `reason="no_claims"`；否则 `grounded_count / total`。

**失败隔离**

按 evaluator 分组隔离：overall quality 的 6 个维度在一次 judge 调用内独立校验，一个维度非法不影响其余；任一 evaluator 抛 `Exception` 时，仅该组指标变为 `not_evaluable`，其余组继续。不得吞掉 `BaseException`。

**REQ-010 入口**

- 先校验 `question.strip()`、`report.strip()` 非空；否则抛 `EvaluationInputError`，judge 调用次数为 0。
- 入口模块不导入 `open_deep_research.deep_researcher`、不导入 search/provider、不调用 `utils.get_search_tool`。
- `report_id` 未提供时使用报告文本的 SHA-256；始终返回 `report_sha256`。
- CLI：`python -m test.evaluation.evaluate_report --report <file> --question <text> [...]`，输出 JSON。

**兼容适配器（`test/evaluators.py`）**

保留 `eval_overall_quality`、`eval_relevance`、`eval_structure`、`eval_correctness`、`eval_groundedness`、`eval_completeness` 名称与调用签名，内部调用核心包；返回字段保留基线 `key`/`score`/`comment`，并增加 `status`、`reason`。overall quality 仍返回 6 元素 list，其余返回 dict。这样 `test/run_evaluate.py:2,15` 无需改动。

## 6. 模块文档改动计划

| 文件 | 计划内容 |
|---|---|
| `docs/architecture/evaluation-table.md` | 新增 `EVAL-001`，包含 ASR、A/B/C 比较、Choice、Rejected |
| `docs/architecture/adr/001-evaluation-module.md` | 从模板创建，填满九节；§6 引用 INV/POL，§9 逐文件步骤 |
| `docs/architecture/invariants.md` | 新增 `INV-006`（评分有效性）、`INV-007`（评估入口不触发研究/搜索） |
| `docs/architecture/runtime-policy-catalog.md` | §1 增行，§2 增 evaluation 模块；POL-002…POL-006（集成时统一编号） |
| `docs/architecture/trace-matrix.md` | 更新 REQ-009/010 两行：ADR-001、INV-006/007、`test/evaluation/`、计划测试、监控指标 |
| `docs/code-governance/structural-constraints.md` §10 | 新增 evaluation 表：路径、职责、接口、调用方、允许/禁止依赖、共享契约、无配置开关 |
| `docs/code-governance/verification-constraints.md` §7 | 新增 evaluation 用例表、回归套件、人工检查 |
| `docs/architecture/memory-design.md` §5 | **不新增**：评估模块不改变 graph state；报告中注明 N/A 及理由 |

**POL 草案**

| ID | 触发 | 行为 |
|---|---|---|
| POL-002 | question/report 空白（入口） | 抛 `EvaluationInputError`，不调用 judge |
| POL-003 | 缺 reference/brief/evidence | 依赖指标 `not_evaluable`，其余继续 |
| POL-004 | judge 返回非法评分 | 该指标 `not_evaluable`、score=None |
| POL-005 | claims 为空 | groundedness `not_evaluable` |
| POL-006 | evaluator/judge 抛异常 | 该组指标 `not_evaluable`，其余继续 |

## 7. 验收覆盖与计划测试位置

测试文件与需求中的 `verification` 路径完全一致。

| Case | 覆盖 | 类型 | 输入 | 预期结果 | 计划位置 |
|---|---|---|---|---|---|
| TC-EVAL-001 | REQ-009 C-001 | normal | question/report/answer/brief/evidence 标记 | 各 judge 请求包含对应原文 | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |
| TC-EVAL-002 | REQ-009 C-002 | boundary | rating 1、5 | 0.2、1.0 | `::test_ratings_are_validated` |
| TC-EVAL-003 | REQ-009 C-002 | exception | 0、6、True、`"4"`、4.5、NaN、inf、None | `not_evaluable`，score=None | `::test_ratings_are_validated` |
| TC-EVAL-004 | REQ-009 C-003 | exception | 缺 reference/brief/evidence | 对应指标不可评估，其余已评分 | `::test_missing_input_is_not_evaluable` |
| TC-EVAL-005 | REQ-009 C-004 | boundary | claims=[] | groundedness `not_evaluable` | `::test_groundedness_and_errors` |
| TC-EVAL-006 | REQ-009 C-004 | normal | 4 claims，2 grounded | groundedness=0.5 | `::test_groundedness_and_errors` |
| TC-EVAL-007 | REQ-009 C-004 | exception | 一个 evaluator 抛异常 | 仅该组不可评估，其余评分 | `::test_one_metric_error_does_not_abort_others` |
| TC-EVAL-008 | REQ-009 M-001 | boundary | 全评分扫描 | 越界 score 数为 0 | `::test_ratings_are_validated` |
| TC-EVAL-009 | INV-006 | regression | 无 key/无网络导入 `test.evaluators`，调用适配器 | 导入无副作用，基线 key/shape 保持 | `::test_adapter_contract_and_import_is_side_effect_free` |
| TC-EVAL-010 | REQ-010 C-001 | normal | 报告/问题标记 + fake judge；patch graph/search 为失败 | judge 收到原文，graph/search 调用为 0，结果标识原报告 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research` |
| TC-EVAL-011 | INV-007 | regression | 子进程导入入口 | `open_deep_research.deep_researcher` 不在 `sys.modules` | `::test_entry_does_not_import_research_graph` |
| TC-EVAL-012 | REQ-010 C-002 | exception | 空/纯空白 report 或 question | `EvaluationInputError`，judge 调用 0 | `::test_blank_input_rejected` |
| TC-EVAL-013 | REQ-010 C-001 | boundary | 无 `report_id` | 稳定 SHA-256；同一报告同 id | `::test_entry_identifies_report` |
| TC-EVAL-014 | REQ-010 C-003 | manual | 按 README 评估报告文件 | 可读 per-metric 结果 | `docs/review-memo.md` 的 REVIEW-NNN |

**回归**：`uv run pytest test/offline`；新增测试的 docstring 首行写 RID；`test/evaluators.py` 适配器契约测试；不改 `test/run_evaluate.py`。

## 8. AI 使用日志建议条目（供人工核对填写）

```yaml
- id: AIU-NNN
  date: "2026-11-13"
  member: DopplerXD
  purpose: >-
    Draft the Phase 1 software-architecture design for the evaluation module for REQ-009 and REQ-010.
  prompt: >-
    Follow AGENTS.md reading order and Prompt.md Phase 1. For REQ-009/REQ-010 (evaluation,
    test/evaluation/), verify role/branch/permissions, analyse test/evaluators.py,
    test/prompts.py and test/run_evaluate.py, map the acceptance criteria, compare 2-3 ADD
    candidates, draft a Proposed ADR, and add the evaluation module sections to the shared
    architecture and verification documents. Do not write source, tests or approvals.
  requirements: [REQ-009, REQ-010]
  artifacts:
    - docs/architecture/evaluation-table.md
    - docs/architecture/adr/001-evaluation-module.md
    - docs/architecture/invariants.md
    - docs/architecture/runtime-policy-catalog.md
    - docs/architecture/trace-matrix.md
    - docs/code-governance/structural-constraints.md
    - docs/code-governance/verification-constraints.md
  supervision: >-
    The member checked the cited baseline locations, reviewed the candidate comparison and ADR,
    resolved the pending design decisions, and approved the module sections before SA Review.
  transcript: null
```

## 9. 待人工决定事项

1. `overall_quality` 粒度：推荐 6 个独立指标结果，而非 1 个聚合结果。
2. `status` 取值：推荐 `scored` / `not_evaluable`。
3. 空白输入行为：推荐抛 `EvaluationInputError`（而非返回带 error 的结果）。
4. `report_id`：推荐可选 `report_id` + 始终返回 `report_sha256`。
5. 严格整数：推荐拒绝 `4.0` 等 float，即使数值等于整数。
6. judge 配置：推荐保留默认 `gpt-4.1` 但改为惰性构造、可注入；judge 选择本身不在本需求范围。
7. 打包：`test/evaluation/` 需加入 `pyproject.toml` 的 `[tool.setuptools] packages`；这是依赖文件变更，Build 阶段需人工确认。
8. 是否接受 `INV-007`（REQ-010 的“入口不触发研究/搜索”）作为新增 invariant。
9. `POL-002…006` 为模块临时编号，集成时由集成者统一重编号。

## 10. 检查结果（本轮实际执行）

| 检查 | 结果 |
|---|---|
| 阅读顺序与文档核对 | PASS（只读） |
| 分支/工作区/权限核对 | PASS |
| 基线代码定位 | PASS（引用见第 2 节） |
| 文件修改 | N/A（Plan mode 禁止） |
| 测试/ruff/requirements 校验 | NOT_RUN（SA 阶段尚未写测试；未改代码/需求） |
| 提交/推送 | N/A（明确禁止） |

请切换到 **Build 模式**（或允许 Plan 写盘）后，我按上述文件清单落盘，并在完成后停在人工 SA 评审前。

### Event 18 — User

允许Plan模式编辑架构文档。
第4节决定：选择B方案。
第9节决定：
1、2、3、5、6、8、9接受。
第3项补充CLI错误提示和非零退出的状态；
第4项首版简化为用原报告内容的SHA-256标识报告；
第7项先检查现有打包配置与运行方式，提供必要性依据后再决定。
另请核实LangSmith评估返回契约，明确内部MetricResult如何
转换为兼容结果，特别说明not_evaluable和null score的处理。

以上是设计方向确认。
以上是设计方向确认，若无其他冲突，就将架构草案写入相应文档与模块章节，完成后保持在 SA 阶段，提交文件差异和验收覆盖清单供我审阅

> **H-02 Candidate and interface decisions**
> 选择 B 方案，简化报告标识，要求核实 LangSmith 返回契约与打包必要性，使后续实现有明确依据。

### Event 19 — OpenCode (plan)

理解。系统 Plan mode 仍强制只读，因此我**不能落盘**；我先完成你要求的两项核实（打包必要性、LangSmith 返回契约），再把可直接执行的最终草案与差异清单交给你。

#### Tool bash — completed

```json
{
  "input": {
    "command": "ls -la .venv 2>/dev/null | head -20; echo \"---editable artifacts---\"; find .venv -maxdepth 4 \\( -name \"*editable*\" -o -name \"*.pth\" -o -name \"direct_url.json\" \\) 2>/dev/null | head -40"
  },
  "output": [
    {
      "type": "text",
      "text": "---editable artifacts---\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "uv run python - <<'PY'\nimport sys, importlib.util\nprint(\"sys.path[0:4]=\", sys.path[:4])\nimport test\nprint(\"test.__file__=\", test.__file__)\nprint(\"test.__path__=\", list(test.__path__))\nprint(\"test.evaluation spec:\", importlib.util.find_spec(\"test.evaluation\"))\nPY"
  },
  "output": [
    {
      "type": "text",
      "text": "Using CPython 3.12.14\nCreating virtual environment at: .venv\n   Building open-deep-research @ file:///Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA\nDownloading sqlalchemy (2.0MiB)\nDownloading grpcio (11.5MiB)\nDownloading pandas (10.2MiB)\nDownloading lxml (8.2MiB)\nDownloading pydantic-core (1.8MiB)\nDownloading uvloop (1.3MiB)\nDownloading pyzmq (1.2MiB)\nDownloading numpy (4.9MiB)\nDownloading pyarrow (32.6MiB)\nDownloading grpcio-tools (5.4MiB)\nDownloading debugpy (2.4MiB)\nDownloading jsonschema-rs (3.6MiB)\n Downloaded pyzmq\n Downloaded uvloop\n Downloaded pydantic-core\n      Built open-deep-research @ file:///Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA\n Downloaded sqlalchemy\n Downloaded debugpy\n Downloaded jsonschema-rs\n Downloaded numpy\n Downloaded grpcio-tools\n Downloaded lxml\n Downloaded pandas\n Downloaded grpcio\n Downloaded pyarrow\nInstalled 225 packages in 1.61s\nsys.path[0:4]= ['', '/Users/doppler/.local/share/uv/python/cpython-3.12.14-macos-aarch64-none/lib/python312.zip', '/Users/doppler/.local/share/uv/python/cpython-3.12.14-macos-aarch64-none/lib/python3.12', '/Users/doppler/.local/share/uv/python/cpython-3.12-macos-aarch64-none/lib/python3.12/lib-dynload']\ntest.__file__= /Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/test/__init__.py\ntest.__path__= ['/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/test']\ntest.evaluation spec: None\n"
    }
  ]
}
```

### Event 20 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "git status --short; echo \"---venv gitignored?---\"; git check-ignore -v .venv 2>/dev/null || echo \"not ignored\"; echo \"---editable---\"; find .venv -maxdepth 5 \\( -name \"*editable*\" -o -name \"*.pth\" \\) 2>/dev/null | head -20"
  },
  "output": [
    {
      "type": "text",
      "text": "---venv gitignored?---\nnot ignored\n---editable---\n.venv/lib/python3.12/site-packages/__editable___open_deep_research_0_0_16_finder.py\n.venv/lib/python3.12/site-packages/__pycache__/__editable___open_deep_research_0_0_16_finder.cpython-312.pyc\n.venv/lib/python3.12/site-packages/distutils-precedence.pth\n.venv/lib/python3.12/site-packages/_virtualenv.pth\n.venv/lib/python3.12/site-packages/google_cloud_aiplatform-1.133.0-py3.10-nspkg.pth\n.venv/lib/python3.12/site-packages/__editable__.open_deep_research-0.0.16.pth\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "ls .venv/lib/python3.12/site-packages | grep -i \"open.deep\\|editable\" | head; echo \"---\"; for f in .venv/lib/python3.12/site-packages/*.pth; do echo \"== $f\"; cat \"$f\"; done 2>/dev/null | head -60"
  },
  "output": [
    {
      "type": "text",
      "text": "__editable__.open_deep_research-0.0.16.pth\n__editable___open_deep_research_0_0_16_finder.py\nopen_deep_research-0.0.16.dist-info\n---\n== .venv/lib/python3.12/site-packages/__editable__.open_deep_research-0.0.16.pth\nimport __editable___open_deep_research_0_0_16_finder; __editable___open_deep_research_0_0_16_finder.install()== .venv/lib/python3.12/site-packages/_virtualenv.pth\nimport _virtualenv== .venv/lib/python3.12/site-packages/distutils-precedence.pth\nimport os; var = 'SETUPTOOLS_USE_DISTUTILS'; enabled = os.environ.get(var, 'local') == 'local'; enabled and __import__('_distutils_hack').add_shim(); \n== .venv/lib/python3.12/site-packages/google_cloud_aiplatform-1.133.0-py3.10-nspkg.pth\nimport sys, types, os;p = os.path.join(sys._getframe(1).f_locals['sitedir'], *('google',));importlib = __import__('importlib.util');__import__('importlib.machinery');m = sys.modules.setdefault('google', importlib.util.module_from_spec(importlib.machinery.PathFinder.find_spec('google', [os.path.dirname(p)])));m = m or sys.modules.setdefault('google', types.ModuleType('google'));mp = (m or []) and m.__dict__.setdefault('__path__',[]);(p not in mp) and mp.append(p)\nimport sys, types, os;p = os.path.join(sys._getframe(1).f_locals['sitedir'], *('google', 'cloud'));importlib = __import__('importlib.util');__import__('importlib.machinery');m = sys.modules.setdefault('google.cloud', importlib.util.module_from_spec(importlib.machinery.PathFinder.find_spec('google.cloud', [os.path.dirname(p)])));m = m or sys.modules.setdefault('google.cloud', types.ModuleType('google.cloud'));mp = (m or []) and m.__dict__.setdefault('__path__',[]);(p not in mp) and mp.append(p);m and setattr(sys.modules['google'], 'cloud', m)\n"
    }
  ]
}
```

### Event 21 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "sed -n '1,80p' .venv/lib/python3.12/site-packages/__editable___open_deep_research_0_0_16_finder.py"
  },
  "output": [
    {
      "type": "text",
      "text": "from __future__ import annotations\nimport sys\nfrom importlib.machinery import ModuleSpec, PathFinder\nfrom importlib.machinery import all_suffixes as module_suffixes\nfrom importlib.util import spec_from_file_location\nfrom itertools import chain\nfrom pathlib import Path\n\nMAPPING: dict[str, str] = {'open_deep_research': '/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/src/open_deep_research', 'test': '/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/test'}\nNAMESPACES: dict[str, list[str]] = {'open_deep_research': ['/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/src/open_deep_research']}\nPATH_PLACEHOLDER = '__editable__.open_deep_research-0.0.16.finder' + \".__path_hook__\"\n\n\nclass _EditableFinder:  # MetaPathFinder\n    @classmethod\n    def find_spec(cls, fullname: str, path=None, target=None) -> ModuleSpec | None:  # type: ignore\n        # Top-level packages and modules (we know these exist in the FS)\n        if fullname in MAPPING:\n            pkg_path = MAPPING[fullname]\n            return cls._find_spec(fullname, Path(pkg_path))\n\n        # Handle immediate children modules (required for namespaces to work)\n        # To avoid problems with case sensitivity in the file system we delegate\n        # to the importlib.machinery implementation.\n        parent, _, child = fullname.rpartition(\".\")\n        if parent and parent in MAPPING:\n            return PathFinder.find_spec(fullname, path=[MAPPING[parent]])\n\n        # Other levels of nesting should be handled automatically by importlib\n        # using the parent path.\n        return None\n\n    @classmethod\n    def _find_spec(cls, fullname: str, candidate_path: Path) -> ModuleSpec | None:\n        init = candidate_path / \"__init__.py\"\n        candidates = (candidate_path.with_suffix(x) for x in module_suffixes())\n        for candidate in chain([init], candidates):\n            if candidate.exists():\n                return spec_from_file_location(fullname, candidate)\n        return None\n\n\nclass _EditableNamespaceFinder:  # PathEntryFinder\n    @classmethod\n    def _path_hook(cls, path) -> type[_EditableNamespaceFinder]:\n        if path == PATH_PLACEHOLDER:\n            return cls\n        raise ImportError\n\n    @classmethod\n    def _paths(cls, fullname: str) -> list[str]:\n        paths = NAMESPACES[fullname]\n        if not paths and fullname in MAPPING:\n            paths = [MAPPING[fullname]]\n        # Always add placeholder, for 2 reasons:\n        # 1. __path__ cannot be empty for the spec to be considered namespace.\n        # 2. In the case of nested namespaces, we need to force\n        #    import machinery to query _EditableNamespaceFinder again.\n        return [*paths, PATH_PLACEHOLDER]\n\n    @classmethod\n    def find_spec(cls, fullname: str, target=None) -> ModuleSpec | None:  # type: ignore\n        if fullname in NAMESPACES:\n            spec = ModuleSpec(fullname, None, is_package=True)\n            spec.submodule_search_locations = cls._paths(fullname)\n            return spec\n        return None\n\n    @classmethod\n    def find_module(cls, _fullname) -> None:\n        return None\n\n\ndef install():\n    if not any(finder == _EditableFinder for finder in sys.meta_path):\n        sys.meta_path.append(_EditableFinder)\n\n    if not NAMESPACES:\n        return\n\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": ".venv/bin/python - <<'PY'\nimport sys, importlib.util\nprint(sys.path[:5])\nimport test\nprint(\"test:\", test.__file__, list(test.__path__))\nprint(\"test.evaluation:\", importlib.util.find_spec(\"test.evaluation\"))\nimport open_deep_research\nprint(\"odr:\", open_deep_research.__file__, list(open_deep_research.__path__))\nPY"
  },
  "output": [
    {
      "type": "text",
      "text": "['', '/Users/doppler/.local/share/uv/python/cpython-3.12.14-macos-aarch64-none/lib/python312.zip', '/Users/doppler/.local/share/uv/python/cpython-3.12.14-macos-aarch64-none/lib/python3.12', '/Users/doppler/.local/share/uv/python/cpython-3.12-macos-aarch64-none/lib/python3.12/lib-dynload', '/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/.venv/lib/python3.12/site-packages']\ntest: /Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/test/__init__.py ['/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/test']\ntest.evaluation: None\nodr: None ['/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/src/open_deep_research', '__editable__.open_deep_research-0.0.16.finder.__path_hook__']\n"
    }
  ]
}
```

### Event 22 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": ".venv/bin/python - <<'PY'\nimport langsmith, inspect\nprint(\"langsmith\", getattr(langsmith, \"__version__\", \"?\"))\ntry:\n    from langsmith.evaluation import EvaluationResult, EvaluationResults\n    print(\"EvaluationResult:\", EvaluationResult)\n    print(\"fields:\", getattr(EvaluationResult, \"__annotations__\", None))\n    print(\"EvaluationResult dataclass fields:\", [f.name for f in __import__('dataclasses').fields(EvaluationResult)])\nexcept Exception as e:\n    print(\"eval import error:\", e)\nPY"
  },
  "output": [
    {
      "type": "text",
      "text": "langsmith 0.9.2\nEvaluationResult: <class 'langsmith.evaluation.evaluator.EvaluationResult'>\nfields: {'key': 'str', 'score': 'SCORE_TYPE', 'value': 'VALUE_TYPE', 'metadata': 'Optional[dict]', 'comment': 'Optional[str]', 'correction': 'Optional[dict]', 'evaluator_info': 'dict', 'feedback_config': 'Optional[Union[FeedbackConfig, dict]]', 'source_run_id': 'Optional[Union[uuid.UUID, str]]', 'target_run_id': 'Optional[Union[uuid.UUID, str]]', 'extra': 'Optional[dict]'}\neval import error: must be called with a dataclass type or instance\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "grep -rn \"class EvaluationResult\\|score:.*Optional\\|key: str\\|comment:\" .venv/lib/python3.12/site-packages/langsmith/evaluation/_arunner.py .venv/lib/python3.12/site-packages/langsmith/evaluation/__init__.py 2>/dev/null | head -40"
  },
  "output": [
    {
      "type": "text",
      "text": "(no output)"
    }
  ]
}
```

### Event 23 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "sed -n '1,140p' .venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py"
  },
  "output": [
    {
      "type": "text",
      "text": "\"\"\"This module contains the evaluator classes for evaluating runs.\"\"\"\n\nfrom __future__ import annotations\n\nimport asyncio\nimport inspect\nimport logging\nimport uuid\nfrom abc import abstractmethod\nfrom collections.abc import Awaitable, Coroutine, Sequence\nfrom functools import wraps\nfrom typing import (\n    Any,\n    Callable,\n    Literal,\n    Optional,\n    Union,\n    cast,\n)\n\nfrom pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator\nfrom typing_extensions import TypedDict\n\nfrom langsmith import run_helpers as rh\nfrom langsmith import schemas\nfrom langsmith.evaluation._key_extraction import _safe_extract_feedback_keys\nfrom langsmith.schemas import SCORE_TYPE, VALUE_TYPE, Example, Run\n\nlogger = logging.getLogger(__name__)\n\n\ndef _run_async_evaluator_sync(\n    awaitable_factory: Callable[[], Coroutine[Any, Any, Any]],\n    method_name: str,\n    async_method_name: str,\n) -> Any:\n    try:\n        asyncio.get_running_loop()\n    except RuntimeError:\n        return asyncio.run(awaitable_factory())\n    raise RuntimeError(\n        f\"Cannot call `{method_name}` on an async run evaluator from within a \"\n        f\"running event loop. Use `{async_method_name}` instead.\"\n    )\n\n\nclass Category(TypedDict):\n    \"\"\"A category for categorical feedback.\"\"\"\n\n    value: Optional[Union[float, int]]\n    \"\"\"The numeric score/ordinal corresponding to this category.\"\"\"\n    label: str\n    \"\"\"The label for this category.\"\"\"\n\n\nclass FeedbackConfig(TypedDict, total=False):\n    \"\"\"Configuration to define a type of feedback.\n\n    Applied on on the first creation of a `feedback_key`.\n    \"\"\"\n\n    type: Literal[\"continuous\", \"categorical\", \"freeform\"]\n    \"\"\"The type of feedback.\"\"\"\n    min: Optional[Union[float, int]]\n    \"\"\"The minimum permitted value (if continuous type).\"\"\"\n    max: Optional[Union[float, int]]\n    \"\"\"The maximum value permitted value (if continuous type).\"\"\"\n    categories: Optional[list[Union[Category, dict]]]\n\n\nclass EvaluationResult(BaseModel):\n    \"\"\"Evaluation result.\"\"\"\n\n    key: str\n    \"\"\"The aspect, metric name, or label for this evaluation.\"\"\"\n    score: SCORE_TYPE = None\n    \"\"\"The numeric score for this evaluation.\"\"\"\n    value: VALUE_TYPE = None\n    \"\"\"The value for this evaluation, if not numeric.\"\"\"\n    metadata: Optional[dict] = None\n    \"\"\"Arbitrary metadata attached to the evaluation.\"\"\"\n    comment: Optional[str] = None\n    \"\"\"An explanation regarding the evaluation.\"\"\"\n    correction: Optional[dict] = None\n    \"\"\"What the correct value should be, if applicable.\"\"\"\n    evaluator_info: dict = Field(default_factory=dict)\n    \"\"\"Additional information about the evaluator.\"\"\"\n    feedback_config: Optional[Union[FeedbackConfig, dict]] = None\n    \"\"\"The configuration used to generate this feedback.\"\"\"\n    source_run_id: Optional[Union[uuid.UUID, str]] = None\n    \"\"\"The ID of the trace of the evaluator itself.\"\"\"\n    target_run_id: Optional[Union[uuid.UUID, str]] = None\n    \"\"\"The ID of the trace this evaluation is applied to.\n\n    If none provided, the evaluation feedback is applied to the\n    root trace being.\"\"\"\n    extra: Optional[dict] = None\n    \"\"\"Metadata for the evaluator run.\"\"\"\n\n    model_config = ConfigDict(extra=\"forbid\")\n\n    @model_validator(mode=\"after\")\n    def check_value_non_numeric(self) -> EvaluationResult:\n        \"\"\"Warn when numeric values are passed via the `value` field.\"\"\"\n        if self.score is None and isinstance(self.value, (int, float)):\n            logger.warning(\n                \"Numeric values should be provided in the 'score' field, not 'value'.\"\n                f\" Got: {self.value}\"\n            )\n        return self\n\n\nclass EvaluationResults(TypedDict, total=False):\n    \"\"\"Batch evaluation results.\n\n    This makes it easy for your evaluator to return multiple\n    metrics at once.\n    \"\"\"\n\n    results: list[EvaluationResult]\n    \"\"\"The evaluation results.\"\"\"\n\n\nclass RunEvaluator:\n    \"\"\"Evaluator interface class.\"\"\"\n\n    @abstractmethod\n    def evaluate_run(\n        self,\n        run: Run,\n        example: Optional[Example] = None,\n        evaluator_run_id: Optional[uuid.UUID] = None,\n    ) -> Union[EvaluationResult, EvaluationResults]:\n        \"\"\"Evaluate an example.\"\"\"\n\n    async def aevaluate_run(\n        self,\n        run: Run,\n        example: Optional[Example] = None,\n        evaluator_run_id: Optional[uuid.UUID] = None,\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "grep -rn \"SCORE_TYPE\\|VALUE_TYPE\\|def _format_evaluator_result\\|EvaluationResult(\" .venv/lib/python3.12/site-packages/langsmith/evaluation/_arunner.py .venv/lib/python3.12/site-packages/langsmith/evaluation/_runner.py .venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py 2>/dev/null | head -60"
  },
  "output": [
    {
      "type": "text",
      "text": ".venv/lib/python3.12/site-packages/langsmith/evaluation/_arunner.py:1033:                                EvaluationResult(\n.venv/lib/python3.12/site-packages/langsmith/evaluation/_runner.py:1692:                                EvaluationResult(\n.venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py:27:from langsmith.schemas import SCORE_TYPE, VALUE_TYPE, Example, Run\n.venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py:71:class EvaluationResult(BaseModel):\n.venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py:76:    score: SCORE_TYPE = None\n.venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py:78:    value: VALUE_TYPE = None\n.venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py:170:class ComparisonEvaluationResult(BaseModel):\n.venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py:179:    scores: dict[Union[uuid.UUID, str], SCORE_TYPE]\n.venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py:286:            return EvaluationResult(**{\"source_run_id\": source_run_id, **result})\n.venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py:642:            return ComparisonEvaluationResult(\n.venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py:932:def _format_evaluator_result(\n"
    }
  ]
}
```

### Event 24 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "grep -n \"SCORE_TYPE\\|VALUE_TYPE\" .venv/lib/python3.12/site-packages/langsmith/schemas.py | head -20; echo \"---format---\"; sed -n '920,1010p' .venv/lib/python3.12/site-packages/langsmith/evaluation/evaluator.py"
  },
  "output": [
    {
      "type": "text",
      "text": "32:SCORE_TYPE = Union[StrictBool, StrictInt, StrictFloat, None]\n33:VALUE_TYPE = Union[dict, str, StrictBool, StrictInt, StrictFloat, None]\n630:    score: SCORE_TYPE = None\n632:    value: VALUE_TYPE = None\n---format---\n            ) -> _COMPARISON_OUTPUT:\n                (args, kwargs, _) = _prepare_inputs(runs, example)\n                return func(*args, **kwargs)\n\n            wrapper.__name__ = (\n                getattr(func, \"__name__\")\n                if hasattr(func, \"__name__\")\n                else wrapper.__name__\n            )\n            return wrapper, _prepare_inputs  # type: ignore[return-value]\n\n\ndef _format_evaluator_result(\n    result: Union[EvaluationResults, dict, str, int, bool, float, list],\n) -> Union[EvaluationResults, dict]:\n    if isinstance(result, (bool, float, int)):\n        result = {\"score\": result}\n    elif not result:\n        raise ValueError(\n            f\"Expected a non-empty dict, str, bool, int, float, list, \"\n            f\"EvaluationResult, or EvaluationResults. Got {result}\"\n        )\n    elif isinstance(result, list):\n        if not all(isinstance(x, dict) for x in result):\n            raise ValueError(\n                f\"Expected a list of dicts or EvaluationResults. Received {result}.\"\n            )\n        result = {\"results\": result}  # type: ignore[misc]\n    elif isinstance(result, str):\n        result = {\"value\": result}\n    elif isinstance(result, dict):\n        pass\n    else:\n        raise ValueError(\n            f\"Expected a dict, str, bool, int, float, list, EvaluationResult, or \"\n            f\"EvaluationResults. Got {result}\"\n        )\n    return result\n\n\nSUMMARY_EVALUATOR_T = Union[\n    Callable[\n        [Sequence[schemas.Run], Sequence[schemas.Example]],\n        Union[EvaluationResult, EvaluationResults],\n    ],\n    Callable[\n        [list[schemas.Run], list[schemas.Example]],\n        Union[EvaluationResult, EvaluationResults],\n    ],\n]\n\n\ndef _normalize_summary_evaluator(func: Callable) -> SUMMARY_EVALUATOR_T:\n    supported_args = (\"runs\", \"examples\", \"inputs\", \"outputs\", \"reference_outputs\")\n    sig = inspect.signature(func)\n    all_args = [pname for pname, p in sig.parameters.items()]\n    args_with_defaults = [\n        pname\n        for pname, p in sig.parameters.items()\n        if p.default is not inspect.Parameter.empty\n    ]\n    if not all_args or (\n        not all(\n            pname in supported_args or pname in args_with_defaults for pname in all_args\n        )\n        and len([a for a in all_args if a not in args_with_defaults]) != 2\n    ):\n        msg = (\n            f\"Invalid evaluator function. Must have at least one \"\n            f\"argument. Supported arguments are {supported_args}.\"\n        )\n        if all_args:\n            msg += f\" Received arguments {all_args}.\"\n        raise ValueError(msg)\n    # For backwards compatibility we assume custom arg names are Sequence[Run] and\n    # Sequence[Example] types, respectively.\n    elif not all(pname in supported_args for pname in all_args) or all_args == [\n        \"runs\",\n        \"examples\",\n    ]:\n        return func\n    else:\n\n        def wrapper(\n            runs: Sequence[schemas.Run], examples: Sequence[schemas.Example]\n        ) -> Union[EvaluationResult, EvaluationResults]:\n            arg_map = {\n                \"runs\": runs,\n                \"examples\": examples,\n                \"inputs\": [example.inputs for example in examples],\n                \"outputs\": [run.outputs or {} for run in runs],\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "sed -n '1000,1060p' .venv/lib/python3.12/site-packages/langsmith/evaluation/_arunner.py; echo \"---score usage---\"; grep -n \"\\.score is None\\|score is not None\\|feedback.*score\\|create_feedback\" .venv/lib/python3.12/site-packages/langsmith/evaluation/_arunner.py | head -40"
  },
  "output": [
    {
      "type": "text",
      "text": "                \"project_name\": \"evaluators\",\n                \"metadata\": metadata,\n                \"enabled\": \"local\" if not self._upload_results else True,\n                \"client\": self.client,\n            }\n        ):\n            run = current_results[\"run\"]\n            example = current_results[\"example\"]\n            eval_results = current_results[\"evaluation_results\"]\n\n            async def _run_single_evaluator(evaluator: RunEvaluator):\n                evaluator_run_id = uuid.uuid4()\n                try:\n                    evaluator_response = await evaluator.aevaluate_run(  # type: ignore[call-arg]\n                        run=run,\n                        example=self._get_example_with_readers(example),\n                        evaluator_run_id=evaluator_run_id,\n                    )\n                    selected_results = self.client._select_eval_results(\n                        evaluator_response\n                    )\n\n                    if self._upload_results:\n                        self.client._log_evaluation_feedback(\n                            evaluator_response, run=run, _executor=feedback_executor\n                        )\n                    return selected_results\n                except Exception as e:\n                    try:\n                        feedback_keys = evaluator.feedback_keys\n\n                        error_response = EvaluationResults(\n                            results=[\n                                EvaluationResult(\n                                    key=key,\n                                    source_run_id=evaluator_run_id,\n                                    comment=repr(e),\n                                    extra={\"error\": True},\n                                )\n                                for key in feedback_keys\n                            ]\n                        )\n                        selected_results = self.client._select_eval_results(\n                            error_response\n                        )\n                        if self._upload_results:\n                            self.client._log_evaluation_feedback(\n                                error_response, run=run, _executor=feedback_executor\n                            )\n                        return selected_results\n                    except Exception as e2:\n                        logger.debug(f\"Error parsing feedback keys: {e2}\")\n                        pass\n                    logger.error(\n                        f\"Error running evaluator {repr(evaluator)} on\"\n                        f\" run {run.id}: {repr(e)}\",\n                        exc_info=True,\n                    )\n\n            all_results = []\n            for evaluator in evaluators:\n---score usage---\n1115:                                self.client.create_feedback,\n"
    }
  ]
}
```

### Event 25 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "grep -rn \"def _select_eval_results\\|def _log_evaluation_feedback\" .venv/lib/python3.12/site-packages/langsmith/client.py | head"
  },
  "output": [
    {
      "type": "text",
      "text": ".venv/lib/python3.12/site-packages/langsmith/client.py:7355:    def _select_eval_results(\n.venv/lib/python3.12/site-packages/langsmith/client.py:7438:    def _log_evaluation_feedback(\n"
    }
  ]
}
```

#### Tool bash — completed

```json
{
  "input": {
    "command": "grep -n \"_select_eval_results\" .venv/lib/python3.12/site-packages/langsmith/client.py | head"
  },
  "output": [
    {
      "type": "text",
      "text": "7355:    def _select_eval_results(\n7449:        results = self._select_eval_results(evaluator_response)\n"
    }
  ]
}
```

### Event 26 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "sed -n '7355,7475p' .venv/lib/python3.12/site-packages/langsmith/client.py"
  },
  "output": [
    {
      "type": "text",
      "text": "    def _select_eval_results(\n        self,\n        results: Union[\n            ls_evaluator.EvaluationResult, ls_evaluator.EvaluationResults, dict\n        ],\n        *,\n        fn_name: Optional[str] = None,\n    ) -> list[ls_evaluator.EvaluationResult]:\n        from langsmith.evaluation import evaluator as ls_evaluator  # noqa: F811\n\n        def _cast_result(\n            single_result: Union[ls_evaluator.EvaluationResult, dict],\n        ) -> ls_evaluator.EvaluationResult:\n            if isinstance(single_result, dict):\n                merged_result: dict[str, Any] = {**single_result}\n                if \"reasoning\" in merged_result and \"comment\" not in merged_result:\n                    merged_result[\"comment\"] = merged_result[\"reasoning\"]\n                merged_result.pop(\"reasoning\", None)\n                if fn_name is not None and merged_result.get(\"key\") is None:\n                    merged_result[\"key\"] = fn_name\n                return ls_evaluator.EvaluationResult(**merged_result)\n            return single_result\n\n        def _is_eval_results(results: Any) -> TypeGuard[ls_evaluator.EvaluationResults]:\n            return isinstance(results, dict) and \"results\" in results\n\n        if isinstance(results, ls_evaluator.EvaluationResult):\n            results_ = [results]\n        elif _is_eval_results(results):\n            results_ = [_cast_result(r) for r in results[\"results\"]]\n        elif isinstance(results, dict):\n            results_ = [_cast_result(cast(dict, results))]\n        else:\n            raise ValueError(\n                f\"Invalid evaluation results type: {type(results)}.\"\n                \" Must be EvaluationResult, EvaluationResults.\"\n            )\n        return results_\n\n    def evaluate_run(\n        self,\n        run: Union[ls_schemas.Run, ls_schemas.RunBase, str, uuid.UUID],\n        evaluator: ls_evaluator.RunEvaluator,\n        *,\n        source_info: Optional[dict[str, Any]] = None,\n        reference_example: Optional[\n            Union[ls_schemas.Example, str, dict, uuid.UUID]\n        ] = None,\n        load_child_runs: bool = False,\n    ) -> ls_evaluator.EvaluationResult:\n        \"\"\"Evaluate a run.\n\n        Args:\n            run (Union[Run, RunBase, str, UUID]):\n                The run to evaluate.\n            evaluator (RunEvaluator):\n                The evaluator to use.\n            source_info (Optional[Dict[str, Any]]):\n                Additional information about the source of the evaluation to log\n                as feedback metadata.\n            reference_example (Optional[Union[Example, str, dict, UUID]]):\n                The example to use as a reference for the evaluation.\n                If not provided, the run's reference example will be used.\n            load_child_runs (bool, default=False):\n                Whether to load child runs when resolving the run ID.\n\n        Returns:\n            Feedback: The feedback object created by the evaluation.\n        \"\"\"\n        run_ = self._resolve_run_id(run, load_child_runs=load_child_runs)\n        reference_example_ = self._resolve_example_id(reference_example, run_)\n        evaluator_response = evaluator.evaluate_run(\n            run_,\n            example=reference_example_,\n        )\n        results = self._log_evaluation_feedback(\n            evaluator_response,\n            run_,\n            source_info=source_info,\n        )\n        # TODO: Return all results\n        return results[0]\n\n    def _log_evaluation_feedback(\n        self,\n        evaluator_response: Union[\n            ls_evaluator.EvaluationResult, ls_evaluator.EvaluationResults, dict\n        ],\n        run: Optional[ls_schemas.Run] = None,\n        source_info: Optional[dict[str, Any]] = None,\n        project_id: Optional[ID_TYPE] = None,\n        *,\n        _executor: Optional[cf.ThreadPoolExecutor] = None,\n    ) -> list[ls_evaluator.EvaluationResult]:\n        results = self._select_eval_results(evaluator_response)\n\n        def _submit_feedback(**kwargs):\n            if _executor:\n                _executor.submit(self.create_feedback, **kwargs)\n            else:\n                self.create_feedback(**kwargs)\n\n        for res in results:\n            source_info_ = source_info or {}\n            if res.evaluator_info:\n                source_info_ = {**res.evaluator_info, **source_info_}\n            run_id_ = None\n            if res.target_run_id:\n                run_id_ = res.target_run_id\n            elif run is not None:\n                run_id_ = run.id\n            error = res.extra.get(\"error\", None) if res.extra is not None else None\n\n            _submit_feedback(\n                run_id=run_id_,\n                key=res.key,\n                score=res.score,\n                value=res.value,\n                comment=res.comment,\n                correction=res.correction,\n                source_info=source_info_,\n"
    }
  ]
}
```

### Event 27 — OpenCode (plan)

#### Tool bash — completed

````json
{
  "input": {
    "command": "grep -n \"def create_feedback\" .venv/lib/python3.12/site-packages/langsmith/client.py | head; sed -n '2840,2930p' .venv/lib/python3.12/site-packages/langsmith/client.py"
  },
  "output": [
    {
      "type": "text",
      "text": "7534:    def create_feedback(\n7925:    def create_feedback_from_token(\n8227:    def create_feedback_formula(\n8343:    def create_feedback_config(\n\n        Raises:\n            LangsmithAPIError: If there is an error in the API request.\n\n        Returns:\n            None\n\n        !!! note\n\n            The run objects MUST contain the `dotted_order` and `trace_id` fields\n            to be accepted by the API.\n\n        Example:\n            ```python\n            from langsmith import Client\n            import datetime\n            from uuid import uuid4\n\n            client = Client()\n            _session = \"__test_batch_ingest_runs\"\n            trace_id = uuid4()\n            trace_id_2 = uuid4()\n            run_id_2 = uuid4()\n            current_time = datetime.datetime.now(datetime.timezone.utc).strftime(\n                \"%Y%m%dT%H%M%S%fZ\"\n            )\n            later_time = (\n                datetime.datetime.now(datetime.timezone.utc) + timedelta(seconds=1)\n            ).strftime(\"%Y%m%dT%H%M%S%fZ\")\n\n            runs_to_create = [\n                {\n                    \"id\": str(trace_id),\n                    \"session_name\": _session,\n                    \"name\": \"run 1\",\n                    \"run_type\": \"chain\",\n                    \"dotted_order\": f\"{current_time}{str(trace_id)}\",\n                    \"trace_id\": str(trace_id),\n                    \"inputs\": {\"input1\": 1, \"input2\": 2},\n                    \"outputs\": {\"output1\": 3, \"output2\": 4},\n                },\n                {\n                    \"id\": str(trace_id_2),\n                    \"session_name\": _session,\n                    \"name\": \"run 3\",\n                    \"run_type\": \"chain\",\n                    \"dotted_order\": f\"{current_time}{str(trace_id_2)}\",\n                    \"trace_id\": str(trace_id_2),\n                    \"inputs\": {\"input1\": 1, \"input2\": 2},\n                    \"error\": \"error\",\n                },\n                {\n                    \"id\": str(run_id_2),\n                    \"session_name\": _session,\n                    \"name\": \"run 2\",\n                    \"run_type\": \"chain\",\n                    \"dotted_order\": f\"{current_time}{str(trace_id)}.\"\n                    f\"{later_time}{str(run_id_2)}\",\n                    \"trace_id\": str(trace_id),\n                    \"parent_run_id\": str(trace_id),\n                    \"inputs\": {\"input1\": 5, \"input2\": 6},\n                },\n            ]\n            runs_to_update = [\n                {\n                    \"id\": str(run_id_2),\n                    \"dotted_order\": f\"{current_time}{str(trace_id)}.\"\n                    f\"{later_time}{str(run_id_2)}\",\n                    \"trace_id\": str(trace_id),\n                    \"parent_run_id\": str(trace_id),\n                    \"outputs\": {\"output1\": 4, \"output2\": 5},\n                },\n            ]\n\n            client.batch_ingest_runs(create=runs_to_create, update=runs_to_update)\n            ```\n        \"\"\"\n        if not create and not update:\n            return\n        # filter out runs that are not sampled\n        create = self._filter_for_sampling(create or EMPTY_SEQ)\n        update = self._filter_for_sampling(update or EMPTY_SEQ, patch=True)\n        if not create and not update:\n            return\n        # transform and convert to dicts\n        create_dicts = [self._run_transform(run, copy=False) for run in create]\n        update_dicts = [\n            self._run_transform(run, update=True, copy=False) for run in update\n        ]\n        for run in create_dicts:\n            if not run.get(\"trace_id\") or not run.get(\"dotted_order\"):\n"
    }
  ]
}
````

### Event 28 — OpenCode (plan)

#### Tool bash — completed

````json
{
  "input": {
    "command": "sed -n '7534,7670p' .venv/lib/python3.12/site-packages/langsmith/client.py"
  },
  "output": [
    {
      "type": "text",
      "text": "    def create_feedback(\n        self,\n        # TODO: make run_id a kwarg and drop default value for 'key' in breaking release.\n        run_id: Optional[ID_TYPE] = None,\n        key: str = \"unnamed\",\n        *,\n        score: Union[float, int, bool, None] = None,\n        value: Union[float, int, bool, str, dict, None] = None,\n        trace_id: Optional[ID_TYPE] = None,\n        correction: Union[dict, None] = None,\n        comment: Union[str, None] = None,\n        source_info: Optional[dict[str, Any]] = None,\n        feedback_source_type: Union[\n            ls_schemas.FeedbackSourceType, str\n        ] = ls_schemas.FeedbackSourceType.API,\n        source_run_id: Optional[ID_TYPE] = None,\n        feedback_id: Optional[ID_TYPE] = None,\n        feedback_config: Optional[ls_schemas.FeedbackConfig] = None,\n        stop_after_attempt: int = 10,\n        project_id: Optional[ID_TYPE] = None,\n        comparative_experiment_id: Optional[ID_TYPE] = None,\n        feedback_group_id: Optional[ID_TYPE] = None,\n        extra: Optional[dict] = None,\n        error: Optional[bool] = None,\n        session_id: Optional[ID_TYPE] = None,\n        start_time: Optional[datetime.datetime] = None,\n        extend_trace_retention: bool = True,\n        **kwargs: Any,\n    ) -> ls_schemas.Feedback:\n        \"\"\"Create feedback for a run.\n\n        !!! note\n\n            To enable feedback to be batch uploaded in the background you must\n            specify `trace_id`. *We highly encourage this for latency-sensitive environments.*\n\n        Args:\n            key (str):\n                The name of the feedback metric.\n            score (Optional[Union[float, int, bool]]):\n                The score to rate this run on the metric or aspect.\n            value (Optional[Union[float, int, bool, str, dict]]):\n                The display value or non-numeric value for this feedback.\n            run_id (Optional[Union[UUID, str]]):\n                The ID of the run to provide feedback for. At least one of run_id,\n                trace_id, or project_id must be specified.\n            trace_id (Optional[Union[UUID, str]]):\n                The ID of the trace (i.e. root parent run) of the run to provide\n                feedback for (specified by run_id). If run_id and trace_id are the\n                same, only trace_id needs to be specified. **NOTE**: trace_id is\n                required feedback ingestion to be batched and backgrounded.\n            correction (Optional[dict]):\n                The proper ground truth for this run.\n            comment (Optional[str]):\n                A comment about this feedback, such as a justification for the score or\n                chain-of-thought trajectory for an LLM judge.\n            source_info (Optional[Dict[str, Any]]):\n                Information about the source of this feedback.\n            feedback_source_type (Union[FeedbackSourceType, str]):\n                The type of feedback source, such as model (for model-generated feedback)\n                or API.\n            source_run_id (Optional[Union[UUID, str]]):\n                The ID of the run that generated this feedback, if a \"model\" type.\n            feedback_id (Optional[Union[UUID, str]]):\n                The ID of the feedback to create. If not provided, a random UUID will be\n                generated.\n            feedback_config (Optional[FeedbackConfig]):\n                The configuration specifying how to interpret feedback with this key.\n                Examples include continuous (with min/max bounds), categorical,\n                or freeform.\n            stop_after_attempt (int, default=10):\n                The number of times to retry the request before giving up.\n            project_id (Optional[Union[UUID, str]]):\n                The ID of the project (or experiment) to provide feedback on. This is\n                used for creating summary metrics for experiments. Cannot specify\n                run_id or trace_id if project_id is specified, and vice versa.\n            comparative_experiment_id (Optional[Union[UUID, str]]):\n                If this feedback was logged as a part of a comparative experiment, this\n                associates the feedback with that experiment.\n            feedback_group_id (Optional[Union[UUID, str]]):\n                When logging preferences, ranking runs, or other comparative feedback,\n                this is used to group feedback together.\n            extra (Optional[Dict]):\n                Metadata for the feedback.\n            session_id (Optional[Union[UUID, str]]):\n                The session (project) ID of the run this feedback is for. Used to\n                optimize feedback ingestion by avoiding server-side lookups.\n            start_time (Optional[datetime]):\n                The start time of the run this feedback is for. Used to optimize\n                feedback ingestion by avoiding server-side lookups.\n            extend_trace_retention (bool, default=True):\n                If false, create the feedback without extending the trace's retention\n                tier.\n            **kwargs (Any):\n                Additional keyword arguments.\n\n        Returns:\n            Feedback: The created feedback object.\n\n        Example:\n            ```python\n            from langsmith import trace, traceable, Client\n\n\n            @traceable\n            def foo(x):\n                return {\"y\": x * 2}\n\n\n            @traceable\n            def bar(y):\n                return {\"z\": y - 1}\n\n\n            client = Client()\n\n            inputs = {\"x\": 1}\n            with trace(name=\"foobar\", inputs=inputs) as root_run:\n                result = foo(**inputs)\n                result = bar(**result)\n                root_run.outputs = result\n                trace_id = root_run.id\n                child_runs = root_run.child_runs\n\n            # Provide feedback for a trace (a.k.a. a root run)\n            client.create_feedback(\n                key=\"user_feedback\",\n                score=1,\n                trace_id=trace_id,\n            )\n\n            # Provide feedback for a child run\n            foo_run_id = [run for run in child_runs if run.name == \"foo\"][0].id\n            client.create_feedback(\n                key=\"correctness\",\n                score=0,\n                run_id=foo_run_id,\n"
    }
  ]
}
````

### Event 29 — OpenCode (plan)

#### Tool context7_resolve-library-id — completed

```json
{
  "input": {
    "query": "LangSmith evaluator return format EvaluationResult key score comment null score",
    "libraryName": "LangSmith"
  },
  "output": [
    {
      "type": "text",
      "text": "Available Libraries:\n\n- Title: LangSmith\n- Context7-compatible library ID: /websites/langchain_langsmith\n- Description: LangSmith provides tools for developing, debugging, and deploying LLM applications, helping users trace requests, evaluate outputs, test prompts, and manage deployments for building reliable AI systems.\n- Code Snippets: 19529\n- Source Reputation: High\n- Benchmark Score: 70.5\n----------\n- Title: LangSmith\n- Context7-compatible library ID: /langchain-ai/langsmith-docs\n- Description: LangSmith is a platform by LangChain for debugging, testing, evaluating, and monitoring large language model applications.\n- Code Snippets: 2554\n- Source Reputation: High\n- Benchmark Score: 70.01\n----------\n- Title: LangSmith SDK\n- Context7-compatible library ID: /langchain-ai/langsmith-sdk\n- Description: LangSmith Client SDK Implementations\n- Code Snippets: 760\n- Source Reputation: High\n- Benchmark Score: 60.6\n----------\n- Title: LangSmith Cookbook\n- Context7-compatible library ID: /langchain-ai/langsmith-cookbook\n- Description: A comprehensive guide of practical recipes and real-world use cases for mastering LangSmith, a platform for debugging, evaluating, testing, and improving LLM applications.\n- Code Snippets: 1394\n- Source Reputation: High\n- Benchmark Score: 70.57\n----------\n- Title: LangSmith SDK (DeepWiki)\n- Context7-compatible library ID: /websites/deepwiki_langchain-ai_langsmith-sdk\n- Description: LangSmith SDK provides client libraries in Python and JavaScript/TypeScript for debugging, evaluating, and monitoring LLM applications through tracing and dataset management.\n- Code Snippets: 1267\n- Source Reputation: High\n- Benchmark Score: 67"
    }
  ]
}
```

### Event 30 — OpenCode (plan)

#### Tool context7_query-docs — completed

````json
{
  "input": {
    "libraryId": "/langchain-ai/langsmith-docs",
    "query": "Custom evaluator return value contract: EvaluationResult dict key score comment, list of results, and whether score may be null or None",
    "language": "Python"
  },
  "output": [
    {
      "type": "text",
      "text": "### Evaluators > Evaluator outputs\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/evaluation/concepts/index.mdx\n\n#### Evaluator outputs\n\nAn evaluator returns one or more metrics. These should be returned as a dictionary or list of dictionaries of the form:\n\n- `key`: The name of the metric.\n- `score` | `value`: The value of the metric. Use `score` if it's a numerical metric and `value` if it's categorical.\n- `comment` (optional): The reasoning or additional string information justifying the score.\n\n--------------------------------\n\n### How to return multiple scores in one evaluator\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/evaluation/how_to_guides/multiple_scores.mdx\n\nSometimes it is useful for a [custom evaluator function](./custom_evaluator) or [summary evaluator function](./summary) to return multiple metrics.\nFor example, if you have multiple metrics being generated by an LLM judge, you can save time and money by making a single LLM call that generates multiple metrics instead of making multiple LLM calls.\n\nTo return multiple scores using the Python SDK, simply return a list of dictionaries/objects of the following form:\n\n```python\n[\n    # 'key' is the metric name\n    # 'score' is the value of a numerical metric\n    {\"key\": string, \"score\": number},\n    # 'value' is the value of a categorical metric\n    {\"key\": string, \"value\": string},\n    ... # You may log as many as you wish\n]\n```\n\nTo do so with the JS/TS SDK, return an object with a 'results' key and then a list of the above form\n\n```js\n{results: [{ key: string, score: number }, ...]};\n```\n\nEach of these dictionaries can contain any or all of the [feedback fields](/reference/data_formats/feedback_data_format); check out the linked document for more information.\n\n--------------------------------\n\n### Python: Return multiple scores as a list of dictionaries\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/evaluation/how_to_guides/multiple_scores.mdx\n\nReturn a list of dictionaries, each with a 'key' (metric name) and either a 'score' (numerical) or 'value' (categorical). You may log as many as you wish.\n\n```python\n[\n    # 'key' is the metric name\n    # 'score' is the value of a numerical metric\n    {\"key\": string, \"score\": number},\n    # 'value' is the value of a categorical metric\n    {\"key\": string, \"value\": string},\n    ... # You may log as many as you wish\n]\n```\n\n--------------------------------\n\n### Evaluator output\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/evaluation/how_to_guides/custom_evaluator.mdx\n\nCustom evaluators are expected to return one of the following types:\n\nPython and JS/TS\n\n- `dict`: dicts of the form `{\"score\" | \"value\": ..., \"key\": ...}` allow you to customize the metric type (\"score\" for numerical and \"value\" for categorical) and metric name. This if useful if, for example, you want to log an integer as a categorical metric.\n\nPython only\n\n- `int | float | bool`: this is interepreted as an continuous metric that can be averaged, sorted, etc. The function name is used as the name of the metric.\n- `str`: this is intepreted as a categorical metric. The function name is used as the name of the metric.\n- `list[dict]`: return multiple metrics using a single function.\n\n--------------------------------\n\n### Python: Example evaluator returning multiple scores\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/evaluation/how_to_guides/multiple_scores.mdx\n\nRequires `langsmith>=0.2.0`. Replace the evaluation logic with real logic. Returns a list of dictionaries with 'key' and 'score' for precision, recall, and f1.\n\n```python\ndef multiple_scores(outputs: dict, reference_outputs: dict) -> list[dict]:\n    # Replace with real evaluation logic.\n    precision = 0.8\n    recall = 0.9\n    f1 = 0.85\n\n    return [\n        {\"key\": \"precision\", \"score\": precision},\n        {\"key\": \"recall\", \"score\": recall},\n        {\"key\": \"f1\", \"score\": f1},\n    ]\n```"
    }
  ]
}
````

### Event 31 — OpenCode (plan)

#### Tool context7_query-docs — completed

````json
{
  "input": {
    "libraryId": "/langchain-ai/langsmith-docs",
    "query": "Feedback data format: is score optional or nullable? Can feedback be logged with only key and comment and no score/value?",
    "language": "Python"
  },
  "output": [
    {
      "type": "text",
      "text": "### Feedback data format\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/reference/data_formats/feedback_data_format.mdx\n\nFeedback is stored in a simple format with the following fields:\n\n| Field Name               | Type     | Description                                                                                            |\n| ------------------------ | -------- | ------------------------------------------------------------------------------------------------------ |\n| id                       | UUID     | Unique identifier for the record itself                                                                |\n| created_at               | datetime | Timestamp when the record was created                                                                  |\n| modified_at              | datetime | Timestamp when the record was last modified                                                            |\n| session_id               | UUID     | Unique identifier for the experiment or tracing project the run was a part of                          |\n| run_id                   | UUID     | Unique identifier for a specific run within a session                                                  |\n| key                      | string   | A key describing the criteria of the feedback, eg \"correctness\"                                        |\n| score                    | number   | Numerical score associated with the feedback key                                                       |\n| value                    | string   | Reserved for storing a value associated with the score. Useful for categorical feedback.               |\n| comment                  | string   | Any comment or annotation associated with the record. This can be a justification for the score given. |\n| correction               | object   | Reserved for storing correction details, if any                                                        |\n| feedback_source          | object   | Object containing information about the feedback source                                                |\n| feedback_source.type     | string   | The type of source where the feedback originated, eg \"api\", \"app\", \"evaluator\"                         |\n| feedback_source.metadata | object   | Reserved for additional metadata, currently                                                            |\n| feedback_source.user_id  | UUID     | Unique identifier for the user providing feedback                                                      |\n\n--------------------------------\n\n### Python: Return multiple scores as a list of dictionaries\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/evaluation/how_to_guides/multiple_scores.mdx\n\nReturn a list of dictionaries, each with a 'key' (metric name) and either a 'score' (numerical) or 'value' (categorical). You may log as many as you wish.\n\n```python\n[\n    # 'key' is the metric name\n    # 'score' is the value of a numerical metric\n    {\"key\": string, \"score\": number},\n    # 'value' is the value of a categorical metric\n    {\"key\": string, \"value\": string},\n    ... # You may log as many as you wish\n]\n```\n\n--------------------------------\n\n### Evaluators > Evaluator outputs\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/evaluation/concepts/index.mdx\n\n#### Evaluator outputs\n\nAn evaluator returns one or more metrics. These should be returned as a dictionary or list of dictionaries of the form:\n\n- `key`: The name of the metric.\n- `score` | `value`: The value of the metric. Use `score` if it's a numerical metric and `value` if it's categorical.\n- `comment` (optional): The reasoning or additional string information justifying the score.\n\n--------------------------------\n\n### Attach correction feedback\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/prompt_engineering/tutorials/optimize_classifier.mdx\n\nInvokes the classifier with a run_id and attaches correction feedback with key 'correction' and value 'documentation' to indicate the desired classification.\n\n```python\nls_client = Client()\n\nrun_id = uuid.uuid4()\ntopic_classifier(\n    \"fix bug in documentation\",\n    langsmith_extra={\"run_id\": run_id}\n)\n\nls_client.create_feedback(\n    run_id,\n    key=\"correction\",\n    correction=\"documentation\"\n)\n```\n\n--------------------------------\n\n### TypeScript: Create feedback with createFeedback()\n\nSource: https://github.com/langchain-ai/langsmith-docs/blob/main/docs/evaluation/how_to_guides/attach_user_feedback.mdx\n\nDemonstrates logging feedback for a run using client.createFeedback() with a run ID, feedback key, and options including score and comment.\n\n```typescript\nimport { Client } from \"langsmith\";\nconst client = new Client();\n\n// ... Run your application and get the run_id...\n// This information can be the result of a user-facing feedback form\n\nawait client.createFeedback(\n    runId,\n    \"feedback-key\",\n    {\n        score: 1.0,\n        comment: \"comment\",\n    }\n);\n```"
    }
  ]
}
````

### Event 32 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": ".venv/bin/python - <<'PY'\nfrom langsmith.evaluation import EvaluationResult\nfor d in [\n    {\"key\":\"x\",\"score\":None,\"comment\":\"not_evaluable: no_claims\",\"metadata\":{\"status\":\"not_evaluable\"},\"value\":\"not_evaluable\"},\n    {\"key\":\"y\",\"score\":0.5,\"comment\":\"ok\",\"metadata\":{\"status\":\"scored\"}},\n]:\n    r = EvaluationResult(**d)\n    print(r.key, repr(r.score), repr(r.value), r.metadata, r.comment)\nPY"
  },
  "output": [
    {
      "type": "text",
      "text": "x None 'not_evaluable' {'status': 'not_evaluable'} not_evaluable: no_claims\ny 0.5 None {'status': 'scored'} ok\n"
    }
  ]
}
```

### Event 33 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "cat .gitignore; echo \"---status all---\"; git status --short --untracked-files=all | head"
  },
  "output": [
    {
      "type": "text",
      "text": "\n*.egg-info\n*.pyc\n\n# Python\n__pycache__/\n*.py[cod]\n*$py.class\n*.so\n.Python\nbuild/\ndevelop-eggs/\ndist/\ndownloads/\neggs/\n.eggs/\nlib/\nlib64/\nparts/\nsdist/\nvar/\nwheels/\n*.egg-info/\n.installed.cfg\n*.egg\n\n# Virtual environments\nvenv/\nenv/\nENV/\n.env\n\n# IDE specific files\n.idea/\n.vscode/\n*.swp\n*.swo\n.DS_Store\n\n# Jupyter Notebook\n.ipynb_checkpoints\n\n# Testing\n.coverage\nhtmlcov/\n.pytest_cache/\n.tox/\n\n# Logs\n*.log\nlogs/\n\n# Local development\n.env.local\n.env.development.local\n.env.test.local\n.env.production.local\n\n# Dependencies\nnode_modules/\n\n# LangGraph specific\n.langgraph/\n\n# Temporary files\ntmp/\ntemp/\n\n.langgraph_api\n---status all---\n"
    }
  ]
}
```

### Event 34 — OpenCode (plan)

#### Tool bash — completed

```json
{
  "input": {
    "command": "git check-ignore -v .venv/ .venv/lib 2>&1; echo \"exit=$?\"; git config --get core.excludesfile; cat .git/info/exclude 2>/dev/null | tail -20"
  },
  "output": [
    {
      "type": "text",
      "text": ".venv/.gitignore:1:*\t.venv/\n.venv/.gitignore:1:*\t.venv/lib\nexit=0\n# git ls-files --others --exclude-from=.git/info/exclude\n# Lines that start with '#' are comments.\n# For a project mostly in C, the following would be a good set of\n# exclude patterns (uncomment them if you want to use them):\n# *.[oa]\n# *~\n"
    }
  ]
}
```

### Event 35 — OpenCode (plan)

## 执行限制说明

系统 Plan mode 仍强制**只读**，即使你已允许编辑，我也不能落盘。因此下面是最终可执行草案、拟修改差异与验收覆盖清单；**未修改任何受跟踪文件、未写测试/审批、未提交/推送**。检查过程中 `uv run` 自动生成了被 `.venv/.gitignore` 忽略的本地环境，`git status` 无变化。

## 已确认并纳入的设计决定

- 选择 **B 方案**：`test/evaluation/` 核心包 + `test/evaluators.py` 兼容适配器，`test/run_evaluate.py` 不改。
- 接受决定 1、2、3、5、6、8、9。
- 第 3 项补充：CLI 错误写 stderr、非零退出。
- 第 4 项简化：`report_id` 直接使用原报告内容的 SHA-256，不引入调用方自定义 ID。
- 第 7 项：先给打包必要性依据，结论见下。
- LangSmith 契约：见下，`not_evaluable` 映射为 **null score + `value="not_evaluable"` + metadata/comment**，绝不映射为 0。

## 1. 打包配置核实与必要性

现有配置：

- `pyproject.toml`：`[tool.setuptools] packages = ["open_deep_research", "test"]`，`package-dir` 把 `test` 指向仓库根 `test/`。
- README 运行方式：`uv sync`、`uvx --with-editable .`、`python test/run_evaluate.py`；CI 使用 `uv run pytest test/offline`。
- `uv sync` 生成 setuptools **editable finder**：`MAPPING = {'open_deep_research': ..., 'test': ...}`；`test` 的直接子模块通过 `PathFinder.find_spec(..., path=[<test 目录>])` 解析，更深层由父包 `__path__` 自动解析。因此 `test/evaluation/` 在 editable/仓库根运行方式下**无需**加入 `packages` 也可导入。
- 非 editable 安装（`pip install .`/wheel）使用显式 `packages` 列表，会包含 `test` 但不包含 `test/evaluation`；此时 `test.evaluators` 已安装却无法导入 `test.evaluation`，形成不一致。

**结论/建议**：当前支持的 editable、CI、`python test/...` 方式并非硬依赖打包改动；但既然 `test` 已被打包，建议在 `pyproject.toml` 增加 `"test.evaluation"`，避免非 editable 安装断裂。代价是一行变更并需要人工确认依赖文件。若本 PR 不纳入，ADR §9 记录为“条件步骤：仅在支持非 editable 安装时添加；否则明确 evaluation 工具仅支持仓库内 editable 运行”。

## 2. LangSmith 评估返回契约核实

已核对 installed `langsmith 0.9.2` 源码与官方文档：

- 自定义 evaluator 可返回 `dict`、`list[dict]`、`EvaluationResult`、`EvaluationResults`；字段为 `key`、`score`（数值）或 `value`（分类）、可选 `comment`，以及可选的 `metadata`、`correction` 等。
- `langsmith.evaluation.EvaluationResult.score` 类型为 `SCORE_TYPE = Union[StrictBool, StrictInt, StrictFloat, None]`，**允许 `None`**；`create_feedback(score=None)` 也是默认值。
- 官方文档把 `score` 描述为数值、`value` 描述为分类值；因此 null score 在 SDK 类型层面合法，UI/汇总不应把它当作 0。已用本地模型验证 `EvaluationResult(key=..., score=None, value="not_evaluable", metadata=...)` 可正常校验。

**内部 `MetricResult` → LangSmith 兼容结果**

```python
# SCORED
{
    "key": "correctness_score",
    "score": 0.8,
    "comment": "<judge reasoning>",
    "metadata": {"status": "scored"},
}

# NOT_EVALUABLE
{
    "key": "groundedness_score",
    "score": None,
    "value": "not_evaluable",
    "comment": "not_evaluable:no_claims: <detail>",
    "metadata": {"status": "not_evaluable", "reason_code": "no_claims"},
}
```

- `overall_quality` 仍返回 **6 个 dict 的 list**；其余 evaluator 返回单个 dict。这样 `test/run_evaluate.py:2,15` 的现有调用契约不变。
- `not_evaluable` **不得**转换为 `score=0`；null score 使该反馈不参与数值平均，`value`/`metadata`/`comment` 保留状态与原因。
- 每个 evaluator 内部异常时，把它负责的全部 key 以 `not_evaluable` 返回，保证 LangSmith 仍看到所有 metric key；其余 evaluator 继续。
- 兼容字段：保留基线 `key`、`score`、`comment`；新增 `value`/`metadata` 不破坏 LangSmith 契约。

**CLI 行为（拟写入 ADR §3）**

| 情况 | 输出 | 退出码 |
|---|---|---|
| 完成评估，至少一个 metric 为 `scored` | stdout 输出 JSON | 0 |
| 完成评估，但全部 metric 为 `not_evaluable` | stdout 输出 JSON，stderr 提示无可用评分 | 1 |
| 空白 question/report、文件读取失败、参数错误 | stderr `error: <message>`，不调用 judge | 2 |

## 3. 最终文档草案要点

**EVAL-001**：ASR 覆盖 REQ-009 C-001—C-004/M-001 与 REQ-010 C-001—C-003；候选 A/B/C；Choice B；记录 A、C 拒绝理由。

**ADR-001**（`docs/architecture/adr/001-evaluation-module.md`，Proposed）：

- §3：B 方案、核心类型、严格整数校验、失败隔离、SHA-256 `report_id`、CLI 退出码、适配器映射。
- §5：

```python
class MetricStatus(str, Enum):
    SCORED = "scored"
    NOT_EVALUABLE = "not_evaluable"

@dataclass(frozen=True)
class MetricResult:
    metric: str
    status: MetricStatus
    score: float | None
    reason: str
    reason_code: str

@dataclass(frozen=True)
class EvaluationResult:
    report_id: str          # sha256 of the original report text
    metrics: tuple[MetricResult, ...]
    judge_model: str | None

def evaluate_existing_report(
    question: str,
    report: str,
    *,
    reference_answer: str | None = None,
    research_brief: str | None = None,
    evidence: str | None = None,
    judge: Judge | None = None,
) -> EvaluationResult: ...
```

- §6：状态 none；POL-002—POL-006；INV-006/INV-007；确定性边界为评分校验、归一化、输入完整性、claims 比例和异常隔离。
- §9：逐文件步骤（types → validation → judge → metrics → entry → CLI → `test/evaluators.py` 适配器 → `test/prompts.py` 占位符 → README；pyproject 条件步骤）。

**INV-006**：评估结果只能是合法 `scored`（0—1）或 `not_evaluable`（null score），非法评分/缺输入/空 claims/异常不得产生分数。

**INV-007**：评估入口只评估给定报告，不导入或调用 research graph/search，不生成替代报告。

**POL（临时编号）**：

| ID | 触发 | 行为 |
|---|---|---|
| POL-002 | 入口 question/report 空白 | 抛 `EvaluationInputError`；CLI stderr + exit 2；judge 0 次 |
| POL-003 | 缺 reference/brief/evidence | 依赖指标 `not_evaluable`，其余继续 |
| POL-004 | judge 返回非法评分 | 该指标 `not_evaluable`，null score |
| POL-005 | claims 为空 | groundedness `not_evaluable` |
| POL-006 | evaluator/judge 异常 | 该组指标 `not_evaluable`，其余继续 |

**trace-matrix**：REQ-009 → ADR-001/INV-006、`test/evaluation/`、`test/offline/test_evaluator_validity.py`、`out_of_range_score_count`；REQ-010 → ADR-001/INV-007、`test/evaluation/entry.py`、`test/offline/test_report_evaluation_entry.py`、监控 N/A（由 INV-007 结构测试覆盖）。

**structural-constraints §10**：路径 `test/evaluation/`；职责为评估有效性与既有报告评估入口；调用方 `test/evaluators.py`、CLI；可依赖 `test/prompts.py`、`open_deep_research.utils.get_today_str`；禁止依赖 `deep_researcher.py`、research graph、search/provider、导入时构造模型客户端；共享契约 none；无配置开关。

**memory-design §5**：不新增，报告注明 N/A（不改变 graph state）。

## 4. 验收覆盖清单

| Case | 覆盖 | 类型 | 输入/场景 | 预期 | 计划测试位置 |
|---|---|---|---|---|---|
| TC-EVAL-001 | REQ-009 C-001 | normal | 各输入标记 | 各 judge 请求包含对应原文 | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |
| TC-EVAL-002 | REQ-009 C-002 | boundary | rating 1、5 | 0.2、1.0 | `::test_ratings_are_validated` |
| TC-EVAL-003 | REQ-009 C-002 | exception | 0、6、True、`"4"`、4.5、NaN、inf、None | `not_evaluable`、null score | `::test_ratings_are_validated` |
| TC-EVAL-004 | REQ-009 C-003 | exception | 缺 reference/brief/evidence | 依赖指标不可评估，其余已评分 | `::test_missing_input_is_not_evaluable` |
| TC-EVAL-005 | REQ-009 C-004 | boundary | claims=[] | groundedness `not_evaluable` | `::test_groundedness_and_errors` |
| TC-EVAL-006 | REQ-009 C-004 | normal | 4 claims，2 grounded | groundedness=0.5 | `::test_groundedness_and_errors` |
| TC-EVAL-007 | REQ-009 C-004 | exception | 一个 evaluator 抛异常 | 仅该组不可评估，其余评分 | `::test_one_metric_error_does_not_abort_others` |
| TC-EVAL-008 | REQ-009 M-001 | boundary | 全评分扫描 | 越界 score 数为 0 | `::test_ratings_are_validated` |
| TC-EVAL-009 | INV-006 | regression | 无 key/无网络导入；适配器映射 | 导入无副作用；`not_evaluable` 为 null score + value/metadata，基线 key/shape 保持 | `::test_adapter_contract_and_import_is_side_effect_free` |
| TC-EVAL-010 | REQ-010 C-001 | normal | 报告/问题标记；patch graph/search 为失败 | judge 收到原文；graph/search 调用 0；`report_id` 为报告 SHA-256 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research` |
| TC-EVAL-011 | INV-007 | regression | 子进程导入入口 | `open_deep_research.deep_researcher` 不在 `sys.modules` | `::test_entry_does_not_import_research_graph` |
| TC-EVAL-012 | REQ-010 C-002 | exception | 空/纯空白 report 或 question | `EvaluationInputError`；judge 0 次 | `::test_blank_input_rejected` |
| TC-EVAL-013 | REQ-010 C-001 | boundary | 无自定义 ID | `report_id == sha256(report)`，稳定 | `::test_entry_identifies_report` |
| TC-EVAL-014 | REQ-010 C-003 | manual | 按 README 评估文件 | 可读 per-metric 结果 | `docs/review-memo.md` REVIEW-NNN |
| TC-EVAL-015 | REQ-010 C-002 / CLI | exception | CLI 空白输入 | stderr `error:`，exit 2，judge 0 次 | `::test_cli_blank_input_exit_code` |
| TC-EVAL-016 | REQ-010 CLI | boundary | 全部不可评估 / 部分可评估 | exit 1 / exit 0，stdout 为 JSON | `::test_cli_exit_codes` |

**回归**：`uv run pytest test/offline`；`test/evaluators.py` 适配器契约；`test/run_evaluate.py` 导入面不变。

## 5. 拟修改文件（待你切换到可写模式后执行）

| 文件 | 操作 |
|---|---|
| `docs/architecture/evaluation-table.md` | 追加 `EVAL-001` |
| `docs/architecture/adr/001-evaluation-module.md` | 新建，九节完整 |
| `docs/architecture/invariants.md` | 追加 `INV-006`、`INV-007` |
| `docs/architecture/runtime-policy-catalog.md` | §1 增行，§2 增 evaluation 模块 |
| `docs/architecture/trace-matrix.md` | 更新 REQ-009/010 两行 |
| `docs/code-governance/structural-constraints.md` | 追加 §10 evaluation 表 |
| `docs/code-governance/verification-constraints.md` | 追加 §7 evaluation 用例表 |
| `docs/architecture/memory-design.md` | 不修改（N/A） |
| `pyproject.toml` | 条件步骤，待你决定是否纳入 |
| `test/evaluation/*`、`test/evaluators.py`、`test/prompts.py`、`README.md` | 属于 Build/Test Author 后续阶段，本轮不写 |

## 6. 检查结果

| 检查 | 结果 |
|---|---|
| 分支/工作区 | `docs/sa-evaluation`，无受跟踪文件变化 |
| 权限 | Plan 可写目标文档；本轮受 Plan mode 只读限制 |
| 基线代码定位 | PASS（引用见上一轮与 ADR §2 计划） |
| 打包核实 | PASS（editable 下无需强制加入；非 editable 下建议加入） |
| LangSmith 契约核实 | PASS（SDK 0.9.2 类型允许 null score；适配器映射已定） |
| 文档落盘 | NOT_RUN（只读限制） |
| 测试/ruff/requirements 校验 | NOT_RUN（SA 阶段，未写测试/代码） |
| 提交/推送 | N/A（明确禁止） |

## 7. 仍需你决定

1. `pyproject.toml` 是否在本 PR 加入 `"test.evaluation"`：建议加入；当前 editable/CI 流程非硬依赖。
2. CLI 退出码方案（0/1/2）是否按上表固定。
3. POL-002—006 临时编号、INV-007 作为正式 invariant，是否接受集成时统一重编号。

## 8. AI 使用日志建议条目（已按本轮更新）

```yaml
- id: AIU-NNN
  date: "2026-11-13"
  member: DopplerXD
  purpose: >-
    Draft the Phase 1 software-architecture design for the evaluation module for REQ-009 and REQ-010.
  prompt: >-
    Follow AGENTS.md reading order and Prompt.md Phase 1. For REQ-009/REQ-010 (evaluation,
    test/evaluation/), verify role/branch/permissions, analyse test/evaluators.py,
    test/prompts.py and test/run_evaluate.py, map the acceptance criteria, compare 2-3 ADD
    candidates, draft a Proposed ADR, add the module sections, and verify the LangSmith
    evaluator return contract and packaging necessity. Do not write source, tests or approvals.
  requirements: [REQ-009, REQ-010]
  artifacts:
    - docs/architecture/evaluation-table.md
    - docs/architecture/adr/001-evaluation-module.md
    - docs/architecture/invariants.md
    - docs/architecture/runtime-policy-catalog.md
    - docs/architecture/trace-matrix.md
    - docs/code-governance/structural-constraints.md
    - docs/code-governance/verification-constraints.md
  supervision: >-
    The member checked the cited baseline locations, approved option B, confirmed the strict
    rating rules and CLI behaviour, reviewed the LangSmith null-score mapping and packaging
    evidence, and resolved the remaining decisions before SA Review.
  transcript: null
```

请切换到可写模式（或取消 Plan mode 只读限制）。我将按第 5 节写入文档，完成后停在 Gate 1 前，并提交实际 `git diff` 与最终验收覆盖清单。

### Event 40 — User

第7节确认项：1、2、3均接受建议。

Plan模式已能够进行写入，继续工作

> **H-03 Remaining design decisions**
> 确认打包步骤、命令行退出码和临时编号。这是设计方向确认，整体 SA Review 尚待进行。

### Event 46 — model-switched

```json
{
  "time": {
    "created": 1794581549990
  },
  "model": {
    "id": "deepseek-flash",
    "providerID": "deepseek",
    "variant": "high"
  },
  "previous": {
    "id": "deepseek-flash",
    "providerID": "deepseek",
    "variant": "default"
  }
}
```

### Event 50 — User

第7节确认项：1、2、3均接受建议。

Plan模式已能够进行写入，继续工作

### Event 59 — User

第7节确认项：1、2、3均接受建议。

Plan模式已能够进行写入，继续工作

### Event 70 — User

第7节确认项：1、2、3均接受建议。

Plan模式已能够进行写入，继续工作

### Event 71 — OpenCode (plan)

当前仍是 **Plan mode**。系统限制只允许写 `/Users/doppler/.opencode/plan`，**不能修改仓库内的架构文档**；即使权限配置允许，Plan mode harness 仍会阻止落盘。因此我无法继续执行第 5 节的文档写入。

请切换到 **Build agent**（或任何非 Plan 的写入角色），我会立即按已确认方案执行：

- 确认项 1：`pyproject.toml` 加入 `"test.evaluation"`
- 确认项 2：CLI 退出码 `0`（有可用评分）/ `1`（全部 `not_evaluable`）/ `2`（输入或参数错误）
- 确认项 3：接受 `INV-007`，`POL-002—006` 为临时编号，集成时统一
- 写入 `EVAL-001`、`ADR-001`、INV/POL/trace-matrix/structural §10/verification §7
- 不修改 `memory-design.md`（无状态变化）
- 完成后停在 Gate 1 前，提交实际 `git diff` 与验收覆盖清单

目前仓库**没有任何受跟踪文件改动**，也未提交或推送。

### Event 80 — agent-switched

```json
{
  "time": {
    "created": 1794582193869
  },
  "agent": "build",
  "previous": "plan"
}
```

### Event 85 — User

由于内置 Plan 模式禁止写入仓库文档，我明确授权本次使用
Build 角色，将当前会话中已确认的 SA 设计整理到文档。
这是针对文档编辑的临时角色例外，当前阶段仍为 SA。

请先读取 AGENTS.md、Prompt.md、权限文件和当前分支，
复核本会话已确认的 B 方案及后续决定。

只允许修改以下 evaluation 模块文档：
- docs/architecture/evaluation-table.md
- 新建 docs/architecture/adr/<可用编号>-evaluation-module.md
- docs/architecture/invariants.md
- docs/architecture/runtime-policy-catalog.md
- docs/architecture/trace-matrix.md
- docs/code-governance/structural-constraints.md 的模块章节
- docs/code-governance/verification-constraints.md 的模块章节

保留其他模块内容，ADR 状态为 Proposed。
pyproject.toml 的调整只写入 ADR 后续实现步骤。

禁止修改源码、测试代码、依赖配置、权限和审批记录。
禁止提交、推送或进入功能实现。
若有文档编辑权限询问，等待我确认。

完成后给出实际文件差异、验收覆盖和未解决事项。
在聊天中提供真实的 AI 日志建议条目。

> **H-04 Documentation-only role exception**
> 内置 Plan 限制阻止文档写入，人工限定 Build 仅整理七份 SA 文档，保留源码、测试和审批记录边界。

### Event 86 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "git status --short --branch && git branch --show-current && sed -n '1,60p' AGENTS.md >/dev/null && echo \"AGENTS readable\""
  },
  "output": [
    {
      "type": "text",
      "text": "## docs/sa-evaluation\ndocs/sa-evaluation\nAGENTS readable\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "tail -20 docs/architecture/evaluation-table.md; echo \"=====INVARIANTS TAIL=====\"; tail -25 docs/architecture/invariants.md; echo \"=====POLICY TAIL=====\"; tail -20 docs/architecture/runtime-policy-catalog.md"
  },
  "output": [
    {
      "type": "text",
      "text": "- **Decision recorded in:** ADR-NNN\n- **Status:** Open | Decided\n\n**ASR**\n\n| Requirement | Acceptance criteria | Quality attributes at stake |\n|---|---|---|\n| REQ-NNN | C-NNN, M-NNN | e.g. correctness, testability, cost |\n\n**Candidates**\n\n| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |\n|---|---|---|---|---|---|---|\n| A | | | | | Low / Medium / High | Low / Medium / High |\n| B | | | | | | |\n| C (optional) | | | | | | |\n\n**Choice:** <option> — <why it wins>.\n\n**Rejected and why:** <option>: <reason>.\n=====INVARIANTS TAIL=====\n- **Fallback:** at the cap, start no new delegations, end unrun delegations as failed with reason `not_run`, and exit with `budget_exhausted`. A completion request below the coverage threshold is refused, not accepted.\n\n## INV-004 — Every report citation resolves to a retrieved source\n\n- **Statement:** Every citation identifier in a report resolves to exactly one source that was retrieved during the run; a report whose required facts lack resolvable citations is not delivered as complete.\n- **Module:** citations\n- **Source:** none. REQ-006 covers citation format only and lists deterministic citation validation as out of scope.\n- **Status:** Deferred\n- **Enforcing component:** a citation validator at report generation (proposed).\n- **Verification:** offline fixed-source tests for missing, duplicate and malformed identifiers and unsourced facts; monitor `citation_integrity_violation_count == 0`.\n- **Fallback:** correct only format issues that the source list determines; otherwise mark the evidence as missing. Never fabricate a URL or reference.\n\n## INV-005 — Search results are never mistaken for evidence they do not contain\n\n- **Statement:** Every search source is reached through the single tool entry point and returns the same result contract; an unknown provider is rejected at start-up, an invalid result is a failed search, and an empty result is a successful search that carries no evidence.\n- **Module:** search\n- **Source:** REQ-007, REQ-008\n- **Status:** Proposed\n- **Enforcing component:** search configuration validation at graph start; the search adapter called through `utils.get_all_tools()`.\n- **Verification:** `test/offline/test_search_configuration.py`, `test/offline/test_search_fallback.py` with fake providers (normal, empty, timeout, invalid, unknown).\n- **Fallback:** on an eligible error, try only the configured fallback sources in order and record each attempt; when all fail, return an explicit search failure. Never substitute a source that is not configured.\n\n## Adding an Entry\n\nCopy an entry, take the next free `INV-NNN` number, and fill every field. Never reuse a retired number. Add the INV ID to the requirement's row in `trace-matrix.md` and to the ADR's §6. At integration the integrator may renumber entries and updates every reference.\n=====POLICY TAIL=====\n> **Purpose:** What the research agent does at runtime when something goes wrong: exceptions, retries, degradation and failure paths.\n> **Authoritative for:** runtime handling policies. Each policy traces to a requirement or invariant.\n> **Maintained by:** owners of modules with exception, retry, degradation or failure handling write a module section (§2); §1 is integrated from those sections before SA Review. Modules without such handling add nothing.\n> **Last updated:** 2026-11-12\n\n## 1. Policies\n\n| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Module | Source | Test |\n|---|---|---|---|---|---|---|---|---|\n| POL-001 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |\n\n## 2. Module Sections\n\nCopy the example for your module and number policies with the next free `POL-NNN`; numbers are unified at integration.\n\n### <Module> (REQ-NNN, ADR-NNN)\n\n| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |\n|---|---|---|---|---|---|---|---|\n| POL-NNN | e.g. a researcher raises an exception | how deterministic code recognises it | what the system does | retries, limits, fallback, or none | effect on the run outcome (`complete`, `partial`, `failed`, REQ-004) | REQ-NNN / INV-NNN | `test/offline/<file>::<test>` |\n"
    }
  ]
}
```

### Event 99 — OpenCode (build)

#### Tool write — completed

````json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "content": "# ADR-001: Evaluation module — valid metric results and an evaluation-only entry\n\n- **Status:** Proposed\n- **Date:** 2026-11-13\n- **Module:** evaluation\n- **Owner:** DopplerXD\n- **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)\n- **SA Review:** SA-NNN (`docs/review-memo.md`), to be assigned at acceptance\n\n## 1. Architecturally Significant Requirements\n\n| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |\n|---|---|---|\n| REQ-009 | C-001, C-002, C-003, C-004, M-001 | The judge must receive every metric input; scores must come only from a strict integer rating `1..5` or a groundedness ratio over at least one claim; missing inputs, empty claims and evaluator exceptions must not abort the other metrics. REQ-009 is `safety_relevant`, so validation and normalisation are deterministic code. |\n| REQ-010 | C-001, C-002, C-003 | An existing report must be evaluable without compiling or invoking the research graph, calling a search provider or generating a replacement report; blank input must be rejected before any evaluator runs. The entry is therefore a separate component with an import boundary, not a new graph target. |\n\n## 2. Context\n\nThe evaluation code is a set of LangSmith evaluator functions in `test/evaluators.py`; `test/run_evaluate.py` passes them to `Client.aevaluate`. The baseline has these defects:\n\n- `test/evaluators.py` L17-19 constructs `ChatOpenAI(model=\"gpt-4.1\")` at module import. Importing the module therefore has a model-client side effect even when no evaluation runs.\n- `CORRECTNESS_PROMPT` in `test/prompts.py` L95-104 contains no placeholder, so `eval_correctness` at `test/evaluators.py` L199-201 formats the question, report and reference answer into nothing. The judge never sees the inputs its metric is defined over.\n- Ratings declared as integers `1..5` are divided by `5` without validation at `test/evaluators.py` L90-98, L140, L179, L219 and L312. A rating of `0`, `6`, a boolean, a string, a fraction or a non-finite number produces an out-of-range or invalid score.\n- `eval_groundedness` at `test/evaluators.py` L265-270 divides by `len(claims)` and raises `ZeroDivisionError` when the judge extracts no claim.\n- Missing `reference_outputs[\"answer\"]`, `raw_notes` or `research_brief` raises `KeyError` at `test/evaluators.py` L196-198, L239-244 and L286-293; there is no failure isolation, so one broken metric prevents the remaining metrics from being reported.\n- `test/run_evaluate.py` L32-61 compiles and invokes the full research graph for every dataset example; L9-11 also runs `load_dotenv(\"../.env\")` and constructs a LangSmith `Client` at import. There is no entry that scores an already generated report.\n\nThe blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. Offline tests must run without network access, API keys or model calls (`verification-constraints.md` §3), and the baseline LangSmith entry must keep working because it is the benchmark path. The structural constraint that `test/` holds baseline scripts is addressed by keeping evaluation logic in `test/evaluation/` and leaving `test/run_evaluate.py` unchanged; `test/evaluators.py` becomes a thin compatibility adapter.\n\n## 3. Decision\n\nAdopt **option B**: a `test/evaluation/` package containing the evaluation types, validation, judge access, metric evaluation and the evaluation-only entry, plus a compatibility adapter in `test/evaluators.py`.\n\n### 3.1 Package layout\n\n```text\ntest/evaluation/\n  __init__.py           # public exports\n  types.py              # MetricStatus, MetricResult, EvaluationResult, EvaluationInputError\n  validation.py         # strict rating, groundedness ratio, input-presence checks\n  judge.py              # Judge protocol and lazy default judge\n  metrics.py            # metric groups, normalisation, per-group failure isolation\n  entry.py              # evaluate_existing_report(...)\n  evaluate_report.py    # CLI entry point\ntest/evaluators.py      # compatibility adapter only; no evaluation logic\n```\n\n### 3.2 Types and result contract\n\n`MetricStatus` has exactly two values: `scored` and `not_evaluable`. A `MetricResult` states `metric`, `status`, `score`, `reason` and a machine-readable `reason_code`. Its invariant is: `score` is a `float` in `[0, 1]` when and only when `status == \"scored\"`; otherwise `score is None`.\n\n`EvaluationResult` states `report_id`, the tuple of `MetricResult` objects and `judge_model`. `report_id` is the lowercase hexadecimal SHA-256 of the original report text encoded as UTF-8. There is no caller-supplied report id in the first version.\n\n`EvaluationInputError(ValueError)` is raised when the entry's required question or report is blank. It is not a metric result: no evaluator may run before it is raised.\n\n### 3.3 Metric names\n\nThe public metric names preserve the baseline LangSmith keys: `research_depth_score`, `source_quality_score`, `analytical_rigor_score`, `practical_value_score`, `balance_and_objectivity_score`, `writing_quality_score`, `relevance_score`, `structure_and_cohesiveness_score`, `correctness_score`, `groundedness_score` and `completeness_score`. The six overall-quality dimensions are six independent metric results, not one aggregate.\n\n### 3.4 Inputs per metric\n\n- Question and report: all metrics except groundedness; the entry requires both to be non-blank.\n- Reference answer: correctness only.\n- Research brief: completeness only.\n- Evidence (`raw_notes` equivalent): groundedness only.\n\nIf an optional input is missing or blank, only the metrics that require it become `not_evaluable`; the other metrics are still evaluated. If the question or report is missing in the LangSmith adapter, every metric that needs it becomes `not_evaluable` and the adapter does not raise.\n\n### 3.5 Strict rating validation\n\nA judge rating is accepted only when `type(value) is int` and `1 <= value <= 5`. Booleans, floats (including `4.0`), strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and a reason code such as `invalid_rating`. Scores are never clamped, rounded, defaulted or replaced by zero.\n\nGroundedness is the only ratio metric: the judge's claims must be a non-empty list; the score is `grounded_count / total_claims`; an empty list produces `status=\"not_evaluable\"` with reason code `no_claims`. A claim whose `grounded` field is not a boolean makes the metric `not_evaluable` rather than being coerced.\n\n### 3.6 Failure isolation\n\nMetric groups are evaluated independently. A group is one judge call and the metrics it produces: overall quality produces six metrics from one call; each other evaluator produces one metric from one call. An exception in a group makes only that group's metrics `not_evaluable` with a reason code such as `evaluator_error`; the remaining groups still run. The implementation catches `Exception`, never `BaseException`, so interruption and process exit are not swallowed.\n\n### 3.7 Evaluation-only entry\n\n`evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult`:\n\n1. Rejects a blank `question` or `report` with `EvaluationInputError` before any judge call.\n2. Computes `report_id` as the SHA-256 of the supplied report text; the report text is passed to the judge unchanged.\n3. Runs the metric groups against the supplied inputs.\n4. Returns `EvaluationResult`; it never compiles or invokes the research graph, imports `open_deep_research.deep_researcher`, calls a search provider or generates a replacement report.\n\n`Judge` is a protocol with an `invoke(messages, schema)` method. `default_judge()` constructs the baseline judge model lazily on first use; it is injectable for offline tests. Importing `test.evaluation` or `test.evaluators` must not construct a model client or read an API key.\n\n### 3.8 CLI\n\n`python -m test.evaluation.evaluate_report --report <path> --question <text>` accepts optional `--reference-answer`, `--research-brief` and `--evidence`. It prints the result as JSON on stdout. Exit codes are:\n\n| Code | Meaning |\n|---|---|\n| `0` | Evaluation completed and at least one metric is `scored`. |\n| `1` | Evaluation completed but every metric is `not_evaluable`. |\n| `2` | Input, argument or report-file error; the message is written to stderr as `error: ...` and no evaluator runs. |\n\nThe README gains a short section showing the command and how to read the per-metric result (REQ-010 C-003).\n\n### 3.9 LangSmith compatibility adapter\n\n`test/evaluators.py` keeps the six baseline function names and signatures and delegates to `test/evaluation`. It removes the module-level `eval_model` and does not construct a client at import. `overall_quality` still returns a list of six dictionaries; the other evaluators return one dictionary. Each dictionary keeps `key`, `score` and `comment` and adds `status` in `metadata`.\n\nThe conversion is:\n\n```python\n# scored\n{\"key\": \"correctness_score\", \"score\": 0.8, \"comment\": \"<reason>\",\n \"metadata\": {\"status\": \"scored\"}}\n\n# not_evaluable\n{\"key\": \"groundedness_score\", \"score\": None, \"value\": \"not_evaluable\",\n \"comment\": \"not_evaluable:no_claims: <detail>\",\n \"metadata\": {\"status\": \"not_evaluable\", \"reason_code\": \"no_claims\"}}\n```\n\n`score=None` is permitted by the LangSmith `EvaluationResult` score type and by `create_feedback`. `not_evaluable` must never be converted to `0`: a null score is not counted as a numeric score, while `value` and `metadata` keep the status and reason visible. If a whole evaluator group fails before producing any metric, the adapter returns every key that group owns as `not_evaluable`, so LangSmith still sees all metric keys.\n\n## 4. Rejected Options\n\n| Option | Reason for rejection |\n|---|---|\n| A — harden `test/evaluators.py` in place and add a separate entry file | Keeps judge construction, validation, LangSmith serialisation and entry logic in one module; the import side effect and the mixing of adapter and core logic remain, and pure validation is harder to test offline. |\n| C — duplicate the evaluators in a standalone evaluation service and leave the baseline untouched | Two sources of truth for the same metrics; the REQ-009 fixes would not reach the benchmark path; violates the “extend, never replace” rule and doubles maintenance. |\n\nThe full comparison is in EVAL-001.\n\n## 5. Components and Interfaces\n\n| Component | Responsibility | Interface (signature or type) | Called by |\n|---|---|---|---|\n| `test/evaluation/types.py` | Result and error types | `MetricStatus`, `MetricResult`, `EvaluationResult`, `EvaluationInputError` | all evaluation components; adapters |\n| `test/evaluation/validation.py` | Deterministic rating, claim-ratio and input checks | `validate_rating(value) -> float`, `groundedness_ratio(claims) -> float`, `require_text(value) -> bool` | `metrics.py`, `entry.py` |\n| `test/evaluation/judge.py` | Judge boundary; lazy model construction | `Judge.invoke(messages, schema)`, `default_judge() -> Judge` | `metrics.py`, `entry.py` |\n| `test/evaluation/metrics.py` | Run metric groups, normalise and isolate failures | `evaluate_metrics(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> tuple[MetricResult, ...]` | `entry.py`, `test/evaluators.py` |\n| `test/evaluation/entry.py` | Evaluation-only public entry | `evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult` | CLI, callers, `test/evaluators.py` |\n| `test/evaluation/evaluate_report.py` | CLI and exit-code handling | `main(argv=None) -> int`; `python -m test.evaluation.evaluate_report` | humans, scripts |\n| `test/evaluators.py` | Baseline LangSmith adapter | `eval_overall_quality(inputs, outputs)`, `eval_relevance(inputs, outputs)`, `eval_structure(inputs, outputs)`, `eval_correctness(inputs, outputs, reference_outputs)`, `eval_groundedness(inputs, outputs)`, `eval_completeness(inputs, outputs)` | `test/run_evaluate.py` |\n| `test/prompts.py` | Judge templates | `CORRECTNESS_PROMPT` gains `{user_question}`, `{report}`, `{answer}` and `{today}` placeholders | `metrics.py` |\n\n**Shared contracts changed (`structural-constraints.md` §6):** none. The module adds no `state.py` type and no graph state field. The baseline LangSmith evaluator key and return-shape contract is preserved by the adapter; `test/run_evaluate.py` does not change.\n\n## 6. State, Failure Handling and Deterministic Boundary\n\n- **State:** none. The module does not add or change graph state; `memory-design.md` §5 has no evaluation entry.\n- **Runtime policies:** POL-002 to POL-008 (`runtime-policy-catalog.md` §2), covering blank input, missing optional input, invalid rating, empty claims, evaluator exception and CLI exit codes.\n- **Invariants:** INV-006 (valid or `not_evaluable` metric results) and INV-007 (evaluation-only entry does not run research or search).\n- **Deterministic boundary:** the model supplies ratings and claim judgements only. Deterministic code decides whether the rating is a valid integer `1..5`, whether the normalised score is in `[0, 1]`, whether at least one claim exists, whether required inputs are present, whether a metric is `not_evaluable` and whether an exception stays local to its metric group.\n\n## 7. Verification\n\n| Requirement and criterion | Verification |\n|---|---|\n| REQ-009 C-001 | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |\n| REQ-009 C-002 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| REQ-009 C-003 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\n| REQ-009 C-004 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors`, `::test_one_metric_error_does_not_abort_others` |\n| REQ-009 M-001 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| INV-006 | `test/offline/test_evaluator_validity.py` (all cases; no out-of-range score, no score on `not_evaluable`) |\n| REQ-010 C-001 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research`, `::test_entry_identifies_report` |\n| REQ-010 C-002 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected`, `::test_cli_blank_input_exit_code` |\n| REQ-010 C-003 | manual review recorded as `REVIEW-NNN` in `docs/review-memo.md` |\n| INV-007 | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |\n\nThe module's complete case list, including normal, exception, boundary and regression cases, is in `verification-constraints.md` §7.\n\n## 8. Consequences\n\n**Positive.** Every metric either carries a defensible score in `[0, 1]` or an explicit `not_evaluable` result with a reason. Correctness receives the question, report and reference answer. A single broken metric no longer hides the others or crashes a run. Existing reports can be scored without spending research tokens or calling search. Offline tests can inject a fake judge and run without network or keys. The benchmark entry keeps its evaluator names and return shapes.\n\n**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change. `pyproject.toml` needs `test.evaluation` in the packages list for non-editable installs; this is a dependency-file change and needs human confirmation.\n\n**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.\n\n## 9. Implementation Steps\n\nTests for §7 are written by the Test Author after Gate 1; the steps below are the Build work that follows Gate 2.\n\n1. Create `test/evaluation/__init__.py` and export the public types and `evaluate_existing_report`.\n2. Add `test/evaluation/types.py`: `MetricStatus`, `MetricResult`, `EvaluationResult` and `EvaluationInputError`, with the score/status invariant.\n3. Add `test/evaluation/validation.py`: strict `1..5` integer validation, `value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats, strings, `None` and non-finite values.\n4. Add `test/evaluation/judge.py`: the `Judge` protocol and a `default_judge()` that constructs the baseline `ChatOpenAI` only when called. No model construction at import.\n5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score.\n6. Add `test/evaluation/entry.py`: `evaluate_existing_report`, blank-input rejection before the judge, SHA-256 `report_id`, and the no-research/no-search import boundary.\n7. Add `test/evaluation/evaluate_report.py`: the CLI, JSON output and exit codes `0/1/2`; write input errors to stderr as `error: ...`.\n8. In `test/prompts.py`, add `{user_question}`, `{report}`, `{answer}` and `{today}` to `CORRECTNESS_PROMPT`; do not change its rubric wording.\n9. Replace the bodies of the six functions in `test/evaluators.py` with adapter calls; remove the module-level `eval_model`; preserve names, signatures, baseline keys, the six-item list for overall quality and the single-dict shape for the others; add `status` metadata and the null-score/`value=\"not_evaluable\"` mapping.\n10. Add the README section for `python -m test.evaluation.evaluate_report` and the per-metric result (REQ-010 C-003).\n11. Add `\"test.evaluation\"` to `[tool.setuptools] packages` in `pyproject.toml`; this dependency-file change needs the human's confirmation.\n12. Run `uv run ruff check test/evaluation test/evaluators.py test/prompts.py` and `uv run pytest test/offline` after the Test Author's tests exist. Do not modify `test/run_evaluate.py`, `src/` or the tests.\n"
  },
  "output": [
    {
      "type": "text",
      "text": "Created file successfully: docs/architecture/adr/001-evaluation-module.md"
    }
  ]
}
````

### Event 108 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/evaluation-table.md",
    "oldString": "**Choice:** <option> — <why it wins>.\n\n**Rejected and why:** <option>: <reason>.",
    "newString": "**Choice:** <option> — <why it wins>.\n\n**Rejected and why:** <option>: <reason>.\n\n## EVAL-001: How should evaluation produce valid metric results and score an existing report?\n\n- **Module:** evaluation\n- **Owner:** DopplerXD\n- **Decision recorded in:** ADR-001\n- **Status:** Decided\n\n**ASR**\n\n| Requirement | Acceptance criteria | Quality attributes at stake |\n|---|---|---|\n| REQ-009 | C-001, C-002, C-003, C-004, M-001 | Correctness of the score; deterministic validation; failure isolation; offline testability; compatibility with the LangSmith benchmark entry |\n| REQ-010 | C-001, C-002, C-003 | Separation from the research graph and search; input validation before any evaluator; documented use; low operating cost |\n\n**Candidates**\n\n| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |\n|---|---|---|---|---|---|---|\n| A | Harden `test/evaluators.py` in place and add a separate entry file | `test/evaluators.py`, `test/prompts.py`, a new entry script | Smallest file churn; baseline entry untouched; direct reuse of existing functions | Validation, judge construction, LangSmith serialisation and entry logic stay mixed; the import-time model side effect is harder to remove safely; no clean module boundary for pure tests | Low | Medium |\n| B | New `test/evaluation/` core package plus a thin compatibility adapter in `test/evaluators.py` | New `test/evaluation/` package; `test/evaluators.py`; `test/prompts.py`; README; optional `pyproject.toml` package entry | Deterministic validation and entry are separable and testable with a fake judge; judge is constructed lazily; baseline evaluator names and return shapes are preserved; `test/run_evaluate.py` unchanged; matches the blueprint module path | More files and an adapter mapping; a small amount of indirection | Medium | High |\n| C | Duplicate the evaluators in a standalone evaluation service and leave the baseline untouched | New standalone service; existing scripts unchanged | Strong isolation from the benchmark path | Two sources of truth; REQ-009 fixes do not reach the benchmark; duplicated maintenance; violates “extend, never replace” | High | High |\n\n**Choice:** option B — it separates deterministic validation and the evaluation-only entry from the LangSmith adapter, keeps the baseline entry compatible, and allows every REQ-009 and REQ-010 case to run offline with an injected judge. It also places the module at the path assigned by `architecture-blueprint.md` §4.\n\n**Rejected and why:** option A: the core logic remains coupled to the evaluator functions and the import-time model construction, which makes failure isolation and offline tests harder to guarantee. option C: it duplicates metric logic, leaves the benchmark path broken, and creates two sources of truth for the same scores.\n\nThe decision, interfaces and implementation steps are in ADR-001."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/evaluation-table.md (1 replacement)"
    }
  ]
}
```

### Event 117 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/invariants.md",
    "oldString": "## Adding an Entry\n\nCopy an entry, take the next free `INV-NNN` number, and fill every field.",
    "newString": "## INV-006 — Every metric result is valid or explicitly not evaluable\n\n- **Statement:** Every metric result is either `scored` with a score in `[0, 1]` derived from a strict integer judge rating `1..5` or, for groundedness only, from a ratio over at least one extracted claim, or it is `not_evaluable` with a null score and a reason. An invalid rating, missing input, empty claim list or evaluator exception makes only the affected metric `not_evaluable`; it never produces a fabricated score and never aborts the remaining metrics.\n- **Module:** evaluation\n- **Source:** REQ-009\n- **Status:** Proposed\n- **Enforcing component:** `test/evaluation/validation.py`, `test/evaluation/metrics.py` and the compatibility adapter in `test/evaluators.py`.\n- **Verification:** `test/offline/test_evaluator_validity.py`; monitor `out_of_range_score_count == 0`.\n- **Fallback:** return `not_evaluable` with `score=None` and a reason code such as `invalid_rating`, `missing_input`, `no_claims` or `evaluator_error`; continue the other metric groups. Never clamp, round, default or replace a missing score with zero.\n\n## INV-007 — Evaluation-only entry does not perform research or search\n\n- **Statement:** The evaluation-only entry scores exactly the report it is given, using its question and optional reference answer, research brief and evidence. It does not compile or invoke the research graph, call a search provider, generate a replacement report or import the research graph, and it rejects a blank question or report before any evaluator runs.\n- **Module:** evaluation\n- **Source:** REQ-010\n- **Status:** Proposed\n- **Enforcing component:** `test/evaluation/entry.py` and its CLI; the import boundary keeps `open_deep_research.deep_researcher` and search tools out of the entry.\n- **Verification:** `test/offline/test_report_evaluation_entry.py`, including `::test_entry_does_not_import_research_graph`; review of the README procedure for REQ-010 C-003.\n- **Fallback:** raise `EvaluationInputError` (CLI exit `2`) for blank input; never fall back to running research, searching, or generating a report. Report the metric result as `not_evaluable` when an input the metric needs is absent.\n\n## Adding an Entry\n\nCopy an entry, take the next free `INV-NNN` number, and fill every field."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/invariants.md (1 replacement)"
    }
  ]
}
```

### Event 126 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/runtime-policy-catalog.md",
    "oldString": "| POL-NNN | e.g. a researcher raises an exception | how deterministic code recognises it | what the system does | retries, limits, fallback, or none | effect on the run outcome (`complete`, `partial`, `failed`, REQ-004) | REQ-NNN / INV-NNN | `test/offline/<file>::<test>` |",
    "newString": "| POL-NNN | e.g. a researcher raises an exception | how deterministic code recognises it | what the system does | retries, limits, fallback, or none | effect on the run outcome (`complete`, `partial`, `failed`, REQ-004) | REQ-NNN / INV-NNN | `test/offline/<file>::<test>` |\n\n### evaluation (REQ-009, REQ-010, ADR-001)\n\n| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |\n|---|---|---|---|---|---|---|---|\n| POL-002 | The evaluation entry receives a blank question or report | `str.strip()` on both required inputs before any judge call | Raise `EvaluationInputError`; the CLI writes `error: ...` to stderr and exits `2` | None; no evaluator or judge call | N/A (evaluation-only, not a research run) | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |\n| POL-003 | A metric's optional input is absent or blank: reference answer, research brief or evidence | Presence and non-blank check before the metric's judge call | Mark only the dependent metric `not_evaluable`; evaluate the other metrics | None | N/A | REQ-009 C-003 / INV-006 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\n| POL-004 | The judge returns a rating that is not a strict integer `1..5` | `type(value) is int` and range check; booleans, floats, strings, `None` and non-finite values are rejected | Mark that metric `not_evaluable` with `score=None` and `invalid_rating`; do not clamp or default | None; the metric is not retried into a score | N/A | REQ-009 C-002, M-001 / INV-006 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| POL-005 | The judge extracts no claim for groundedness | Non-empty list check before the ratio | Mark groundedness `not_evaluable` with `score=None` and `no_claims` | None | N/A | REQ-009 C-004 / INV-006 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\n| POL-006 | A judge call or evaluator raises an exception | `try/except Exception` around each metric group | Mark only that group's metrics `not_evaluable` with `evaluator_error`; continue the other groups | No module-level retry; provider retries are outside this policy | N/A | REQ-009 C-004 / INV-006 | `test/offline/test_evaluator_validity.py::test_one_metric_error_does_not_abort_others` |\n| POL-007 | The CLI receives an argument or report-file error | Argument parsing and file read before evaluation | Write `error: ...` to stderr; no evaluator runs; exit `2` | None | N/A | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_cli_blank_input_exit_code` |\n| POL-008 | A CLI evaluation completes with every metric `not_evaluable` | Scan the returned metric statuses | Print the JSON result on stdout, notify on stderr and exit `1`; exit `0` when at least one metric is `scored` | None | N/A | REQ-009 / REQ-010 | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/runtime-policy-catalog.md (1 replacement)"
    }
  ]
}
```

### Event 135 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/trace-matrix.md",
    "oldString": "| REQ-009 | Valid evaluator scores | invariant | approved | TBD | TBD | Proposed: `test/evaluation/` | planned: `test/offline/test_evaluator_validity.py` | `out_of_range_score_count` |\n| REQ-010 | Evaluate an existing report | functional | approved | TBD | TBD | Proposed: `test/evaluation/` | planned: `test/offline/test_report_evaluation_entry.py`; review in `docs/review-memo.md` | TBD |",
    "newString": "| REQ-009 | Valid evaluator scores | invariant | approved | Deterministic rating validation, `1..5` normalisation, non-empty claim ratio and per-metric failure isolation; every result is `scored` in `[0, 1]` or `not_evaluable` with a null score | ADR-001 / INV-006 (Proposed) | Proposed: `test/evaluation/` (`validation.py`, `metrics.py`); adapter in `test/evaluators.py` | planned: `test/offline/test_evaluator_validity.py` | `out_of_range_score_count` |\n| REQ-010 | Evaluate an existing report | functional | approved | Evaluation-only entry separated from the research graph and search; SHA-256 report identity; blank input rejected before any evaluator | ADR-001 / INV-007 (Proposed) | Proposed: `test/evaluation/entry.py`; CLI `test/evaluation/evaluate_report.py` | planned: `test/offline/test_report_evaluation_entry.py`; review in `docs/review-memo.md` | N/A (INV-007 structural test) |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/trace-matrix.md (1 replacement)"
    }
  ]
}
```

### Event 144 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "tail -15 docs/code-governance/structural-constraints.md; echo \"=====VERIF TAIL=====\"; tail -18 docs/code-governance/verification-constraints.md"
  },
  "output": [
    {
      "type": "text",
      "text": "\nCopy the example for your module. At integration, check that responsibilities do not overlap, every dependency follows §5 or is listed in blueprint §6, and no two modules write the same state field.\n\n### <Module> (REQ-NNN, ADR-NNN)\n\n| Item | Constraint |\n|---|---|\n| Path | `src/open_deep_research/<module>/` |\n| Responsibility | One sentence; what the module decides or produces |\n| Public interface | Functions and types other code may call |\n| Called from | Nodes or modules that call it, e.g. `supervisor_tools` in `deep_researcher.py` |\n| May depend on | e.g. `state.py`, `configuration.py`, `utils.py` |\n| Must not depend on | e.g. `deep_researcher.py`, other extension modules, model clients in deterministic code |\n| Shared contracts | Types or state fields it reads or writes that other modules also use |\n| Configuration flag | `Configuration` field that switches the behaviour, and its default (§8) |\n=====VERIF TAIL=====\n\n- **Regression:** existing suites to re-run, including `test/offline/test_contracts.py` if a shared contract changes.\n- **Live or human checks:** cases marked `automated: false` in `requirements.yaml`, and where their evidence goes.\n\n## 8. Definition of Done\n\n| # | Condition | Done by |\n|---|---|---|\n| 1 | Every fit-criterion item has an approved test or recorded review, and the tests pass | Test Author (tests), Build (passing), confirmed by Verify |\n| 2 | All prior offline suites pass | Verify |\n| 3 | All active CI gates are green | CI |\n| 4 | Behaviour conforms to the fit criterion, with evidence in `docs/test-reports/` | Verify, confirmed by a human |\n| 5 | `trace-matrix.md` row complete for architecture, code and tests | Module owner |\n| 6 | If a boundary changed: `invariants.md` updated and its test passes | Human, Test Author |\n| 7 | If an architectural decision arose: ADR accepted or `evaluation-table.md` entry recorded | Human |\n| 8 | `docs/ai-use-log.yaml` and `docs/review-memo.md` updated | Human |\n| 9 | Gate 3 passed: two approvals, PR merged | Humans |\n| 10 | `status` in `requirements.yaml` advanced to `verified` | Human |\n"
    }
  ]
}
```

### Event 153 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/structural-constraints.md",
    "oldString": "| Configuration flag | `Configuration` field that switches the behaviour, and its default (§8) |",
    "newString": "| Configuration flag | `Configuration` field that switches the behaviour, and its default (§8) |\n\n### evaluation (REQ-009, REQ-010, ADR-001)\n\n| Item | Constraint |\n|---|---|\n| Path | `test/evaluation/` |\n| Responsibility | Validate and normalise evaluator outputs, produce `scored` or `not_evaluable` metric results, and provide an evaluation-only entry for an existing report. |\n| Public interface | `evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult`; `MetricStatus`, `MetricResult`, `EvaluationResult`, `EvaluationInputError`; CLI `python -m test.evaluation.evaluate_report`. |\n| Called from | The compatibility adapter in `test/evaluators.py` (and therefore `test/run_evaluate.py`), and the CLI. |\n| May depend on | `test/prompts.py`, `open_deep_research.utils.get_today_str`, the Python standard library, and `pydantic`/`langchain_openai` only inside the lazy judge factory. |\n| Must not depend on | `open_deep_research.deep_researcher`, the research graph, search providers or search tools, `test.run_evaluate` import-time state, or any extension module. No model client is constructed at import. |\n| Shared contracts | None: no `state.py` type or graph state field is added. The baseline LangSmith evaluator names, keys and return shapes are preserved by `test/evaluators.py`. |\n| Configuration flag | None: the module is evaluation-only and adds no runtime behaviour flag. |\n\n`test/evaluators.py` is a thin compatibility adapter; evaluation logic lives only in `test/evaluation/`. The `test.evaluation` subpackage is added to `[tool.setuptools] packages` in the same implementation PR so a non-editable install does not omit it."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/structural-constraints.md (1 replacement)"
    }
  ]
}
```

### Event 162 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "- **Live or human checks:** cases marked `automated: false` in `requirements.yaml`, and where their evidence goes.\n\n## 8. Definition of Done",
    "newString": "- **Live or human checks:** cases marked `automated: false` in `requirements.yaml`, and where their evidence goes.\n\n### evaluation (REQ-009, REQ-010, ADR-001)\n\n| Case | Covers | Type | Input | Expected result | Test |\n|---|---|---|---|---|---|\n| TC-EVAL-001 | REQ-009 C-001 | normal | Distinct question, report, reference-answer, research-brief and evidence markers; a fake judge that records requests | Every metric's judge request contains its declared inputs unchanged; correctness receives question, report and reference answer; completeness receives the brief; groundedness receives the evidence | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |\n| TC-EVAL-002 | REQ-009 C-002 | boundary | Ratings `1` and `5` | Scores `0.2` and `1.0`, status `scored` | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| TC-EVAL-003 | REQ-009 C-002 | exception | Ratings `0`, `6`, `True`, `\"4\"`, `4.5`, `NaN`, `inf`, `None` | `not_evaluable`, `score=None`, reason code `invalid_rating`; no clamping or default | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| TC-EVAL-004 | REQ-009 C-003 | exception | Missing reference answer, research brief and evidence, one at a time | Correctness, completeness or groundedness respectively is `not_evaluable`; the other metrics are still `scored` | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\n| TC-EVAL-005 | REQ-009 C-004 | boundary | Judge returns an empty claim list | Groundedness is `not_evaluable` with `score=None`; no `ZeroDivisionError` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\n| TC-EVAL-006 | REQ-009 C-004 | normal | Four claims, two grounded | Groundedness score `0.5` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\n| TC-EVAL-007 | REQ-009 C-004 | exception | One evaluator or judge call raises | Only that group's metrics are `not_evaluable`; the remaining metrics are still evaluated | `test/offline/test_evaluator_validity.py::test_one_metric_error_does_not_abort_others` |\n| TC-EVAL-008 | REQ-009 M-001 | boundary | Sweep of valid and invalid ratings across every metric | `out_of_range_score_count == 0`; every `scored` result is in `[0, 1]`; every invalid result has a null score | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| TC-EVAL-009 | INV-006 | regression | Import `test.evaluators` with no API key and no network; call each adapter with a fake judge | Import has no model-client or network side effect; baseline `key`/return shapes hold; `not_evaluable` maps to null `score`, `value=\"not_evaluable\"` and status metadata | `test/offline/test_evaluator_validity.py::test_adapter_contract_and_import_is_side_effect_free` |\n| TC-EVAL-010 | REQ-010 C-001 | normal | A supplied report and question with markers; research-graph and search entry points patched to fail if called | Judge requests contain the supplied text unchanged; graph and search call counts are zero; `report_id` is the report SHA-256 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research` |\n| TC-EVAL-011 | INV-007 | regression | Import the entry in a subprocess with no research modules preloaded | `open_deep_research.deep_researcher` is absent from `sys.modules` | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |\n| TC-EVAL-012 | REQ-010 C-002 | exception | Empty, whitespace-only and `None` question or report | `EvaluationInputError`; fake judge call count is zero | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |\n| TC-EVAL-013 | REQ-010 C-001 | boundary | Same report submitted twice, and a report differing by one character | `report_id` is stable for the same text and differs for the changed text; it equals the lowercase SHA-256 of the UTF-8 report | `test/offline/test_report_evaluation_entry.py::test_entry_identifies_report` |\n| TC-EVAL-014 | REQ-010 C-003 | human | Reviewer follows the README to evaluate a report file and read the per-metric results | The procedure works without modifying source code; verdict recorded as `REVIEW-NNN` | `docs/review-memo.md` (report evaluation entry review) |\n| TC-EVAL-015 | REQ-010 C-002 / POL-007 | exception | CLI with a blank question or a missing report file | stderr contains `error: ...`; exit code `2`; no judge call | `test/offline/test_report_evaluation_entry.py::test_cli_blank_input_exit_code` |\n| TC-EVAL-016 | POL-008 | boundary | CLI completes with all metrics `not_evaluable`; CLI completes with at least one `scored` metric | Exit code `1` and JSON on stdout in the first case; exit code `0` and JSON in the second | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |\n\n- **Regression:** re-run `uv run pytest test/offline`; the adapter contract in `test/offline/test_evaluator_validity.py`; and the import surface of `test/run_evaluate.py` (the six evaluator names and their call signatures must remain available). No live model or network call is needed for any case above.\n- **Live or human checks:** REQ-010 C-003 is the only `automated: false` criterion in this module; its evidence is the `REVIEW-NNN` record in `docs/review-memo.md`.\n\n## 8. Definition of Done"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

### Event 171 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "git status --short && echo \"---STAT---\" && git diff --stat && echo \"---CHECK---\" && git diff --check"
  },
  "output": [
    {
      "type": "text",
      "text": " M docs/architecture/evaluation-table.md\n M docs/architecture/invariants.md\n M docs/architecture/runtime-policy-catalog.md\n M docs/architecture/trace-matrix.md\n M docs/code-governance/structural-constraints.md\n M docs/code-governance/verification-constraints.md\n?? docs/architecture/adr/001-evaluation-module.md\n---STAT---\n docs/architecture/evaluation-table.md            | 28 ++++++++++++++++++++++++\n docs/architecture/invariants.md                  | 20 +++++++++++++++++\n docs/architecture/runtime-policy-catalog.md      | 12 ++++++++++\n docs/architecture/trace-matrix.md                |  4 ++--\n docs/code-governance/structural-constraints.md   | 15 +++++++++++++\n docs/code-governance/verification-constraints.md | 24 ++++++++++++++++++++\n 6 files changed, 101 insertions(+), 2 deletions(-)\n---CHECK---\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff -- docs/architecture/evaluation-table.md docs/architecture/invariants.md docs/architecture/trace-matrix.md | sed -n '1,240p'"
  },
  "output": [
    {
      "type": "text",
      "text": "diff --git a/docs/architecture/evaluation-table.md b/docs/architecture/evaluation-table.md\nindex 6c02230..68f4236 100644\n--- a/docs/architecture/evaluation-table.md\n+++ b/docs/architecture/evaluation-table.md\n@@ -36,3 +36,31 @@\n **Choice:** <option> — <why it wins>.\n \n **Rejected and why:** <option>: <reason>.\n+\n+## EVAL-001: How should evaluation produce valid metric results and score an existing report?\n+\n+- **Module:** evaluation\n+- **Owner:** DopplerXD\n+- **Decision recorded in:** ADR-001\n+- **Status:** Decided\n+\n+**ASR**\n+\n+| Requirement | Acceptance criteria | Quality attributes at stake |\n+|---|---|---|\n+| REQ-009 | C-001, C-002, C-003, C-004, M-001 | Correctness of the score; deterministic validation; failure isolation; offline testability; compatibility with the LangSmith benchmark entry |\n+| REQ-010 | C-001, C-002, C-003 | Separation from the research graph and search; input validation before any evaluator; documented use; low operating cost |\n+\n+**Candidates**\n+\n+| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |\n+|---|---|---|---|---|---|---|\n+| A | Harden `test/evaluators.py` in place and add a separate entry file | `test/evaluators.py`, `test/prompts.py`, a new entry script | Smallest file churn; baseline entry untouched; direct reuse of existing functions | Validation, judge construction, LangSmith serialisation and entry logic stay mixed; the import-time model side effect is harder to remove safely; no clean module boundary for pure tests | Low | Medium |\n+| B | New `test/evaluation/` core package plus a thin compatibility adapter in `test/evaluators.py` | New `test/evaluation/` package; `test/evaluators.py`; `test/prompts.py`; README; optional `pyproject.toml` package entry | Deterministic validation and entry are separable and testable with a fake judge; judge is constructed lazily; baseline evaluator names and return shapes are preserved; `test/run_evaluate.py` unchanged; matches the blueprint module path | More files and an adapter mapping; a small amount of indirection | Medium | High |\n+| C | Duplicate the evaluators in a standalone evaluation service and leave the baseline untouched | New standalone service; existing scripts unchanged | Strong isolation from the benchmark path | Two sources of truth; REQ-009 fixes do not reach the benchmark; duplicated maintenance; violates “extend, never replace” | High | High |\n+\n+**Choice:** option B — it separates deterministic validation and the evaluation-only entry from the LangSmith adapter, keeps the baseline entry compatible, and allows every REQ-009 and REQ-010 case to run offline with an injected judge. It also places the module at the path assigned by `architecture-blueprint.md` §4.\n+\n+**Rejected and why:** option A: the core logic remains coupled to the evaluator functions and the import-time model construction, which makes failure isolation and offline tests harder to guarantee. option C: it duplicates metric logic, leaves the benchmark path broken, and creates two sources of truth for the same scores.\n+\n+The decision, interfaces and implementation steps are in ADR-001.\ndiff --git a/docs/architecture/invariants.md b/docs/architecture/invariants.md\nindex 7cbc897..2b08540 100644\n--- a/docs/architecture/invariants.md\n+++ b/docs/architecture/invariants.md\n@@ -66,6 +66,26 @@ Every entry uses the same fields:\n - **Verification:** `test/offline/test_search_configuration.py`, `test/offline/test_search_fallback.py` with fake providers (normal, empty, timeout, invalid, unknown).\n - **Fallback:** on an eligible error, try only the configured fallback sources in order and record each attempt; when all fail, return an explicit search failure. Never substitute a source that is not configured.\n \n+## INV-006 — Every metric result is valid or explicitly not evaluable\n+\n+- **Statement:** Every metric result is either `scored` with a score in `[0, 1]` derived from a strict integer judge rating `1..5` or, for groundedness only, from a ratio over at least one extracted claim, or it is `not_evaluable` with a null score and a reason. An invalid rating, missing input, empty claim list or evaluator exception makes only the affected metric `not_evaluable`; it never produces a fabricated score and never aborts the remaining metrics.\n+- **Module:** evaluation\n+- **Source:** REQ-009\n+- **Status:** Proposed\n+- **Enforcing component:** `test/evaluation/validation.py`, `test/evaluation/metrics.py` and the compatibility adapter in `test/evaluators.py`.\n+- **Verification:** `test/offline/test_evaluator_validity.py`; monitor `out_of_range_score_count == 0`.\n+- **Fallback:** return `not_evaluable` with `score=None` and a reason code such as `invalid_rating`, `missing_input`, `no_claims` or `evaluator_error`; continue the other metric groups. Never clamp, round, default or replace a missing score with zero.\n+\n+## INV-007 — Evaluation-only entry does not perform research or search\n+\n+- **Statement:** The evaluation-only entry scores exactly the report it is given, using its question and optional reference answer, research brief and evidence. It does not compile or invoke the research graph, call a search provider, generate a replacement report or import the research graph, and it rejects a blank question or report before any evaluator runs.\n+- **Module:** evaluation\n+- **Source:** REQ-010\n+- **Status:** Proposed\n+- **Enforcing component:** `test/evaluation/entry.py` and its CLI; the import boundary keeps `open_deep_research.deep_researcher` and search tools out of the entry.\n+- **Verification:** `test/offline/test_report_evaluation_entry.py`, including `::test_entry_does_not_import_research_graph`; review of the README procedure for REQ-010 C-003.\n+- **Fallback:** raise `EvaluationInputError` (CLI exit `2`) for blank input; never fall back to running research, searching, or generating a report. Report the metric result as `not_evaluable` when an input the metric needs is absent.\n+\n ## Adding an Entry\n \n Copy an entry, take the next free `INV-NNN` number, and fill every field. Never reuse a retired number. Add the INV ID to the requirement's row in `trace-matrix.md` and to the ADR's §6. At integration the integrator may renumber entries and updates every reference.\ndiff --git a/docs/architecture/trace-matrix.md b/docs/architecture/trace-matrix.md\nindex 85da5ed..10740df 100644\n--- a/docs/architecture/trace-matrix.md\n+++ b/docs/architecture/trace-matrix.md\n@@ -19,8 +19,8 @@ Cell conventions: `TBD` = not decided yet; `Proposed:` = from a document that is\n | REQ-006 | One citation format | invariant | approved | TBD | TBD | Proposed: `citations/` | planned: `test/offline/test_prompt_citation_contract.py`, `test/live/test_report_citations_live.py` | TBD |\n | REQ-007 | Search setup documented and validated | functional | approved | TBD | INV-005 (Proposed) | Proposed: `search/` | planned: `test/offline/test_search_configuration.py`; review in `docs/review-memo.md` | TBD |\n | REQ-008 | Search fallback | functional | approved | TBD | INV-005 (Proposed) | Proposed: `search/` | planned: `test/offline/test_search_fallback.py` | TBD |\n-| REQ-009 | Valid evaluator scores | invariant | approved | TBD | TBD | Proposed: `test/evaluation/` | planned: `test/offline/test_evaluator_validity.py` | `out_of_range_score_count` |\n-| REQ-010 | Evaluate an existing report | functional | approved | TBD | TBD | Proposed: `test/evaluation/` | planned: `test/offline/test_report_evaluation_entry.py`; review in `docs/review-memo.md` | TBD |\n+| REQ-009 | Valid evaluator scores | invariant | approved | Deterministic rating validation, `1..5` normalisation, non-empty claim ratio and per-metric failure isolation; every result is `scored` in `[0, 1]` or `not_evaluable` with a null score | ADR-001 / INV-006 (Proposed) | Proposed: `test/evaluation/` (`validation.py`, `metrics.py`); adapter in `test/evaluators.py` | planned: `test/offline/test_evaluator_validity.py` | `out_of_range_score_count` |\n+| REQ-010 | Evaluate an existing report | functional | approved | Evaluation-only entry separated from the research graph and search; SHA-256 report identity; blank input rejected before any evaluator | ADR-001 / INV-007 (Proposed) | Proposed: `test/evaluation/entry.py`; CLI `test/evaluation/evaluate_report.py` | planned: `test/offline/test_report_evaluation_entry.py`; review in `docs/review-memo.md` | N/A (INV-007 structural test) |\n \n ## Example (Reference Only — VHIS Course Example)\n \n"
    }
  ]
}
```

### Event 184 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff -- docs/architecture/runtime-policy-catalog.md docs/code-governance/structural-constraints.md docs/code-governance/verification-constraints.md | sed -n '1,260p'"
  },
  "output": [
    {
      "type": "text",
      "text": "diff --git a/docs/architecture/runtime-policy-catalog.md b/docs/architecture/runtime-policy-catalog.md\nindex f92a288..a1423a1 100644\n--- a/docs/architecture/runtime-policy-catalog.md\n+++ b/docs/architecture/runtime-policy-catalog.md\n@@ -20,3 +20,15 @@ Copy the example for your module and number policies with the next free `POL-NNN\n | Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |\n |---|---|---|---|---|---|---|---|\n | POL-NNN | e.g. a researcher raises an exception | how deterministic code recognises it | what the system does | retries, limits, fallback, or none | effect on the run outcome (`complete`, `partial`, `failed`, REQ-004) | REQ-NNN / INV-NNN | `test/offline/<file>::<test>` |\n+\n+### evaluation (REQ-009, REQ-010, ADR-001)\n+\n+| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |\n+|---|---|---|---|---|---|---|---|\n+| POL-002 | The evaluation entry receives a blank question or report | `str.strip()` on both required inputs before any judge call | Raise `EvaluationInputError`; the CLI writes `error: ...` to stderr and exits `2` | None; no evaluator or judge call | N/A (evaluation-only, not a research run) | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |\n+| POL-003 | A metric's optional input is absent or blank: reference answer, research brief or evidence | Presence and non-blank check before the metric's judge call | Mark only the dependent metric `not_evaluable`; evaluate the other metrics | None | N/A | REQ-009 C-003 / INV-006 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\n+| POL-004 | The judge returns a rating that is not a strict integer `1..5` | `type(value) is int` and range check; booleans, floats, strings, `None` and non-finite values are rejected | Mark that metric `not_evaluable` with `score=None` and `invalid_rating`; do not clamp or default | None; the metric is not retried into a score | N/A | REQ-009 C-002, M-001 / INV-006 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n+| POL-005 | The judge extracts no claim for groundedness | Non-empty list check before the ratio | Mark groundedness `not_evaluable` with `score=None` and `no_claims` | None | N/A | REQ-009 C-004 / INV-006 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\n+| POL-006 | A judge call or evaluator raises an exception | `try/except Exception` around each metric group | Mark only that group's metrics `not_evaluable` with `evaluator_error`; continue the other groups | No module-level retry; provider retries are outside this policy | N/A | REQ-009 C-004 / INV-006 | `test/offline/test_evaluator_validity.py::test_one_metric_error_does_not_abort_others` |\n+| POL-007 | The CLI receives an argument or report-file error | Argument parsing and file read before evaluation | Write `error: ...` to stderr; no evaluator runs; exit `2` | None | N/A | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_cli_blank_input_exit_code` |\n+| POL-008 | A CLI evaluation completes with every metric `not_evaluable` | Scan the returned metric statuses | Print the JSON result on stdout, notify on stderr and exit `1`; exit `0` when at least one metric is `scored` | None | N/A | REQ-009 / REQ-010 | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |\ndiff --git a/docs/code-governance/structural-constraints.md b/docs/code-governance/structural-constraints.md\nindex 79841a3..e45e75a 100644\n--- a/docs/code-governance/structural-constraints.md\n+++ b/docs/code-governance/structural-constraints.md\n@@ -86,3 +86,18 @@ Copy the example for your module. At integration, check that responsibilities do\n | Must not depend on | e.g. `deep_researcher.py`, other extension modules, model clients in deterministic code |\n | Shared contracts | Types or state fields it reads or writes that other modules also use |\n | Configuration flag | `Configuration` field that switches the behaviour, and its default (§8) |\n+\n+### evaluation (REQ-009, REQ-010, ADR-001)\n+\n+| Item | Constraint |\n+|---|---|\n+| Path | `test/evaluation/` |\n+| Responsibility | Validate and normalise evaluator outputs, produce `scored` or `not_evaluable` metric results, and provide an evaluation-only entry for an existing report. |\n+| Public interface | `evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult`; `MetricStatus`, `MetricResult`, `EvaluationResult`, `EvaluationInputError`; CLI `python -m test.evaluation.evaluate_report`. |\n+| Called from | The compatibility adapter in `test/evaluators.py` (and therefore `test/run_evaluate.py`), and the CLI. |\n+| May depend on | `test/prompts.py`, `open_deep_research.utils.get_today_str`, the Python standard library, and `pydantic`/`langchain_openai` only inside the lazy judge factory. |\n+| Must not depend on | `open_deep_research.deep_researcher`, the research graph, search providers or search tools, `test.run_evaluate` import-time state, or any extension module. No model client is constructed at import. |\n+| Shared contracts | None: no `state.py` type or graph state field is added. The baseline LangSmith evaluator names, keys and return shapes are preserved by `test/evaluators.py`. |\n+| Configuration flag | None: the module is evaluation-only and adds no runtime behaviour flag. |\n+\n+`test/evaluators.py` is a thin compatibility adapter; evaluation logic lives only in `test/evaluation/`. The `test.evaluation` subpackage is added to `[tool.setuptools] packages` in the same implementation PR so a non-editable install does not omit it.\ndiff --git a/docs/code-governance/verification-constraints.md b/docs/code-governance/verification-constraints.md\nindex 6a1ca6a..6f7881b 100644\n--- a/docs/code-governance/verification-constraints.md\n+++ b/docs/code-governance/verification-constraints.md\n@@ -78,6 +78,30 @@ Copy the example for your module. Every acceptance criterion (C-/M-) of the modu\n - **Regression:** existing suites to re-run, including `test/offline/test_contracts.py` if a shared contract changes.\n - **Live or human checks:** cases marked `automated: false` in `requirements.yaml`, and where their evidence goes.\n \n+### evaluation (REQ-009, REQ-010, ADR-001)\n+\n+| Case | Covers | Type | Input | Expected result | Test |\n+|---|---|---|---|---|---|\n+| TC-EVAL-001 | REQ-009 C-001 | normal | Distinct question, report, reference-answer, research-brief and evidence markers; a fake judge that records requests | Every metric's judge request contains its declared inputs unchanged; correctness receives question, report and reference answer; completeness receives the brief; groundedness receives the evidence | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |\n+| TC-EVAL-002 | REQ-009 C-002 | boundary | Ratings `1` and `5` | Scores `0.2` and `1.0`, status `scored` | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n+| TC-EVAL-003 | REQ-009 C-002 | exception | Ratings `0`, `6`, `True`, `\"4\"`, `4.5`, `NaN`, `inf`, `None` | `not_evaluable`, `score=None`, reason code `invalid_rating`; no clamping or default | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n+| TC-EVAL-004 | REQ-009 C-003 | exception | Missing reference answer, research brief and evidence, one at a time | Correctness, completeness or groundedness respectively is `not_evaluable`; the other metrics are still `scored` | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\n+| TC-EVAL-005 | REQ-009 C-004 | boundary | Judge returns an empty claim list | Groundedness is `not_evaluable` with `score=None`; no `ZeroDivisionError` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\n+| TC-EVAL-006 | REQ-009 C-004 | normal | Four claims, two grounded | Groundedness score `0.5` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\n+| TC-EVAL-007 | REQ-009 C-004 | exception | One evaluator or judge call raises | Only that group's metrics are `not_evaluable`; the remaining metrics are still evaluated | `test/offline/test_evaluator_validity.py::test_one_metric_error_does_not_abort_others` |\n+| TC-EVAL-008 | REQ-009 M-001 | boundary | Sweep of valid and invalid ratings across every metric | `out_of_range_score_count == 0`; every `scored` result is in `[0, 1]`; every invalid result has a null score | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n+| TC-EVAL-009 | INV-006 | regression | Import `test.evaluators` with no API key and no network; call each adapter with a fake judge | Import has no model-client or network side effect; baseline `key`/return shapes hold; `not_evaluable` maps to null `score`, `value=\"not_evaluable\"` and status metadata | `test/offline/test_evaluator_validity.py::test_adapter_contract_and_import_is_side_effect_free` |\n+| TC-EVAL-010 | REQ-010 C-001 | normal | A supplied report and question with markers; research-graph and search entry points patched to fail if called | Judge requests contain the supplied text unchanged; graph and search call counts are zero; `report_id` is the report SHA-256 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research` |\n+| TC-EVAL-011 | INV-007 | regression | Import the entry in a subprocess with no research modules preloaded | `open_deep_research.deep_researcher` is absent from `sys.modules` | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |\n+| TC-EVAL-012 | REQ-010 C-002 | exception | Empty, whitespace-only and `None` question or report | `EvaluationInputError`; fake judge call count is zero | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |\n+| TC-EVAL-013 | REQ-010 C-001 | boundary | Same report submitted twice, and a report differing by one character | `report_id` is stable for the same text and differs for the changed text; it equals the lowercase SHA-256 of the UTF-8 report | `test/offline/test_report_evaluation_entry.py::test_entry_identifies_report` |\n+| TC-EVAL-014 | REQ-010 C-003 | human | Reviewer follows the README to evaluate a report file and read the per-metric results | The procedure works without modifying source code; verdict recorded as `REVIEW-NNN` | `docs/review-memo.md` (report evaluation entry review) |\n+| TC-EVAL-015 | REQ-010 C-002 / POL-007 | exception | CLI with a blank question or a missing report file | stderr contains `error: ...`; exit code `2`; no judge call | `test/offline/test_report_evaluation_entry.py::test_cli_blank_input_exit_code` |\n+| TC-EVAL-016 | POL-008 | boundary | CLI completes with all metrics `not_evaluable`; CLI completes with at least one `scored` metric | Exit code `1` and JSON on stdout in the first case; exit code `0` and JSON in the second | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |\n+\n+- **Regression:** re-run `uv run pytest test/offline`; the adapter contract in `test/offline/test_evaluator_validity.py`; and the import surface of `test/run_evaluate.py` (the six evaluator names and their call signatures must remain available). No live model or network call is needed for any case above.\n+- **Live or human checks:** REQ-010 C-003 is the only `automated: false` criterion in this module; its evidence is the `REVIEW-NNN` record in `docs/review-memo.md`.\n+\n ## 8. Definition of Done\n \n | # | Condition | Done by |\n"
    }
  ]
}
```

#### Tool shell — completed

````json
{
  "input": {
    "command": "sed -n '1,260p' docs/architecture/adr/001-evaluation-module.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# ADR-001: Evaluation module — valid metric results and an evaluation-only entry\n\n- **Status:** Proposed\n- **Date:** 2026-11-13\n- **Module:** evaluation\n- **Owner:** DopplerXD\n- **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)\n- **SA Review:** SA-NNN (`docs/review-memo.md`), to be assigned at acceptance\n\n## 1. Architecturally Significant Requirements\n\n| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |\n|---|---|---|\n| REQ-009 | C-001, C-002, C-003, C-004, M-001 | The judge must receive every metric input; scores must come only from a strict integer rating `1..5` or a groundedness ratio over at least one claim; missing inputs, empty claims and evaluator exceptions must not abort the other metrics. REQ-009 is `safety_relevant`, so validation and normalisation are deterministic code. |\n| REQ-010 | C-001, C-002, C-003 | An existing report must be evaluable without compiling or invoking the research graph, calling a search provider or generating a replacement report; blank input must be rejected before any evaluator runs. The entry is therefore a separate component with an import boundary, not a new graph target. |\n\n## 2. Context\n\nThe evaluation code is a set of LangSmith evaluator functions in `test/evaluators.py`; `test/run_evaluate.py` passes them to `Client.aevaluate`. The baseline has these defects:\n\n- `test/evaluators.py` L17-19 constructs `ChatOpenAI(model=\"gpt-4.1\")` at module import. Importing the module therefore has a model-client side effect even when no evaluation runs.\n- `CORRECTNESS_PROMPT` in `test/prompts.py` L95-104 contains no placeholder, so `eval_correctness` at `test/evaluators.py` L199-201 formats the question, report and reference answer into nothing. The judge never sees the inputs its metric is defined over.\n- Ratings declared as integers `1..5` are divided by `5` without validation at `test/evaluators.py` L90-98, L140, L179, L219 and L312. A rating of `0`, `6`, a boolean, a string, a fraction or a non-finite number produces an out-of-range or invalid score.\n- `eval_groundedness` at `test/evaluators.py` L265-270 divides by `len(claims)` and raises `ZeroDivisionError` when the judge extracts no claim.\n- Missing `reference_outputs[\"answer\"]`, `raw_notes` or `research_brief` raises `KeyError` at `test/evaluators.py` L196-198, L239-244 and L286-293; there is no failure isolation, so one broken metric prevents the remaining metrics from being reported.\n- `test/run_evaluate.py` L32-61 compiles and invokes the full research graph for every dataset example; L9-11 also runs `load_dotenv(\"../.env\")` and constructs a LangSmith `Client` at import. There is no entry that scores an already generated report.\n\nThe blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. Offline tests must run without network access, API keys or model calls (`verification-constraints.md` §3), and the baseline LangSmith entry must keep working because it is the benchmark path. The structural constraint that `test/` holds baseline scripts is addressed by keeping evaluation logic in `test/evaluation/` and leaving `test/run_evaluate.py` unchanged; `test/evaluators.py` becomes a thin compatibility adapter.\n\n## 3. Decision\n\nAdopt **option B**: a `test/evaluation/` package containing the evaluation types, validation, judge access, metric evaluation and the evaluation-only entry, plus a compatibility adapter in `test/evaluators.py`.\n\n### 3.1 Package layout\n\n```text\ntest/evaluation/\n  __init__.py           # public exports\n  types.py              # MetricStatus, MetricResult, EvaluationResult, EvaluationInputError\n  validation.py         # strict rating, groundedness ratio, input-presence checks\n  judge.py              # Judge protocol and lazy default judge\n  metrics.py            # metric groups, normalisation, per-group failure isolation\n  entry.py              # evaluate_existing_report(...)\n  evaluate_report.py    # CLI entry point\ntest/evaluators.py      # compatibility adapter only; no evaluation logic\n```\n\n### 3.2 Types and result contract\n\n`MetricStatus` has exactly two values: `scored` and `not_evaluable`. A `MetricResult` states `metric`, `status`, `score`, `reason` and a machine-readable `reason_code`. Its invariant is: `score` is a `float` in `[0, 1]` when and only when `status == \"scored\"`; otherwise `score is None`.\n\n`EvaluationResult` states `report_id`, the tuple of `MetricResult` objects and `judge_model`. `report_id` is the lowercase hexadecimal SHA-256 of the original report text encoded as UTF-8. There is no caller-supplied report id in the first version.\n\n`EvaluationInputError(ValueError)` is raised when the entry's required question or report is blank. It is not a metric result: no evaluator may run before it is raised.\n\n### 3.3 Metric names\n\nThe public metric names preserve the baseline LangSmith keys: `research_depth_score`, `source_quality_score`, `analytical_rigor_score`, `practical_value_score`, `balance_and_objectivity_score`, `writing_quality_score`, `relevance_score`, `structure_and_cohesiveness_score`, `correctness_score`, `groundedness_score` and `completeness_score`. The six overall-quality dimensions are six independent metric results, not one aggregate.\n\n### 3.4 Inputs per metric\n\n- Question and report: all metrics except groundedness; the entry requires both to be non-blank.\n- Reference answer: correctness only.\n- Research brief: completeness only.\n- Evidence (`raw_notes` equivalent): groundedness only.\n\nIf an optional input is missing or blank, only the metrics that require it become `not_evaluable`; the other metrics are still evaluated. If the question or report is missing in the LangSmith adapter, every metric that needs it becomes `not_evaluable` and the adapter does not raise.\n\n### 3.5 Strict rating validation\n\nA judge rating is accepted only when `type(value) is int` and `1 <= value <= 5`. Booleans, floats (including `4.0`), strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and a reason code such as `invalid_rating`. Scores are never clamped, rounded, defaulted or replaced by zero.\n\nGroundedness is the only ratio metric: the judge's claims must be a non-empty list; the score is `grounded_count / total_claims`; an empty list produces `status=\"not_evaluable\"` with reason code `no_claims`. A claim whose `grounded` field is not a boolean makes the metric `not_evaluable` rather than being coerced.\n\n### 3.6 Failure isolation\n\nMetric groups are evaluated independently. A group is one judge call and the metrics it produces: overall quality produces six metrics from one call; each other evaluator produces one metric from one call. An exception in a group makes only that group's metrics `not_evaluable` with a reason code such as `evaluator_error`; the remaining groups still run. The implementation catches `Exception`, never `BaseException`, so interruption and process exit are not swallowed.\n\n### 3.7 Evaluation-only entry\n\n`evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult`:\n\n1. Rejects a blank `question` or `report` with `EvaluationInputError` before any judge call.\n2. Computes `report_id` as the SHA-256 of the supplied report text; the report text is passed to the judge unchanged.\n3. Runs the metric groups against the supplied inputs.\n4. Returns `EvaluationResult`; it never compiles or invokes the research graph, imports `open_deep_research.deep_researcher`, calls a search provider or generates a replacement report.\n\n`Judge` is a protocol with an `invoke(messages, schema)` method. `default_judge()` constructs the baseline judge model lazily on first use; it is injectable for offline tests. Importing `test.evaluation` or `test.evaluators` must not construct a model client or read an API key.\n\n### 3.8 CLI\n\n`python -m test.evaluation.evaluate_report --report <path> --question <text>` accepts optional `--reference-answer`, `--research-brief` and `--evidence`. It prints the result as JSON on stdout. Exit codes are:\n\n| Code | Meaning |\n|---|---|\n| `0` | Evaluation completed and at least one metric is `scored`. |\n| `1` | Evaluation completed but every metric is `not_evaluable`. |\n| `2` | Input, argument or report-file error; the message is written to stderr as `error: ...` and no evaluator runs. |\n\nThe README gains a short section showing the command and how to read the per-metric result (REQ-010 C-003).\n\n### 3.9 LangSmith compatibility adapter\n\n`test/evaluators.py` keeps the six baseline function names and signatures and delegates to `test/evaluation`. It removes the module-level `eval_model` and does not construct a client at import. `overall_quality` still returns a list of six dictionaries; the other evaluators return one dictionary. Each dictionary keeps `key`, `score` and `comment` and adds `status` in `metadata`.\n\nThe conversion is:\n\n```python\n# scored\n{\"key\": \"correctness_score\", \"score\": 0.8, \"comment\": \"<reason>\",\n \"metadata\": {\"status\": \"scored\"}}\n\n# not_evaluable\n{\"key\": \"groundedness_score\", \"score\": None, \"value\": \"not_evaluable\",\n \"comment\": \"not_evaluable:no_claims: <detail>\",\n \"metadata\": {\"status\": \"not_evaluable\", \"reason_code\": \"no_claims\"}}\n```\n\n`score=None` is permitted by the LangSmith `EvaluationResult` score type and by `create_feedback`. `not_evaluable` must never be converted to `0`: a null score is not counted as a numeric score, while `value` and `metadata` keep the status and reason visible. If a whole evaluator group fails before producing any metric, the adapter returns every key that group owns as `not_evaluable`, so LangSmith still sees all metric keys.\n\n## 4. Rejected Options\n\n| Option | Reason for rejection |\n|---|---|\n| A — harden `test/evaluators.py` in place and add a separate entry file | Keeps judge construction, validation, LangSmith serialisation and entry logic in one module; the import side effect and the mixing of adapter and core logic remain, and pure validation is harder to test offline. |\n| C — duplicate the evaluators in a standalone evaluation service and leave the baseline untouched | Two sources of truth for the same metrics; the REQ-009 fixes would not reach the benchmark path; violates the “extend, never replace” rule and doubles maintenance. |\n\nThe full comparison is in EVAL-001.\n\n## 5. Components and Interfaces\n\n| Component | Responsibility | Interface (signature or type) | Called by |\n|---|---|---|---|\n| `test/evaluation/types.py` | Result and error types | `MetricStatus`, `MetricResult`, `EvaluationResult`, `EvaluationInputError` | all evaluation components; adapters |\n| `test/evaluation/validation.py` | Deterministic rating, claim-ratio and input checks | `validate_rating(value) -> float`, `groundedness_ratio(claims) -> float`, `require_text(value) -> bool` | `metrics.py`, `entry.py` |\n| `test/evaluation/judge.py` | Judge boundary; lazy model construction | `Judge.invoke(messages, schema)`, `default_judge() -> Judge` | `metrics.py`, `entry.py` |\n| `test/evaluation/metrics.py` | Run metric groups, normalise and isolate failures | `evaluate_metrics(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> tuple[MetricResult, ...]` | `entry.py`, `test/evaluators.py` |\n| `test/evaluation/entry.py` | Evaluation-only public entry | `evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult` | CLI, callers, `test/evaluators.py` |\n| `test/evaluation/evaluate_report.py` | CLI and exit-code handling | `main(argv=None) -> int`; `python -m test.evaluation.evaluate_report` | humans, scripts |\n| `test/evaluators.py` | Baseline LangSmith adapter | `eval_overall_quality(inputs, outputs)`, `eval_relevance(inputs, outputs)`, `eval_structure(inputs, outputs)`, `eval_correctness(inputs, outputs, reference_outputs)`, `eval_groundedness(inputs, outputs)`, `eval_completeness(inputs, outputs)` | `test/run_evaluate.py` |\n| `test/prompts.py` | Judge templates | `CORRECTNESS_PROMPT` gains `{user_question}`, `{report}`, `{answer}` and `{today}` placeholders | `metrics.py` |\n\n**Shared contracts changed (`structural-constraints.md` §6):** none. The module adds no `state.py` type and no graph state field. The baseline LangSmith evaluator key and return-shape contract is preserved by the adapter; `test/run_evaluate.py` does not change.\n\n## 6. State, Failure Handling and Deterministic Boundary\n\n- **State:** none. The module does not add or change graph state; `memory-design.md` §5 has no evaluation entry.\n- **Runtime policies:** POL-002 to POL-008 (`runtime-policy-catalog.md` §2), covering blank input, missing optional input, invalid rating, empty claims, evaluator exception and CLI exit codes.\n- **Invariants:** INV-006 (valid or `not_evaluable` metric results) and INV-007 (evaluation-only entry does not run research or search).\n- **Deterministic boundary:** the model supplies ratings and claim judgements only. Deterministic code decides whether the rating is a valid integer `1..5`, whether the normalised score is in `[0, 1]`, whether at least one claim exists, whether required inputs are present, whether a metric is `not_evaluable` and whether an exception stays local to its metric group.\n\n## 7. Verification\n\n| Requirement and criterion | Verification |\n|---|---|\n| REQ-009 C-001 | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |\n| REQ-009 C-002 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| REQ-009 C-003 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\n| REQ-009 C-004 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors`, `::test_one_metric_error_does_not_abort_others` |\n| REQ-009 M-001 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| INV-006 | `test/offline/test_evaluator_validity.py` (all cases; no out-of-range score, no score on `not_evaluable`) |\n| REQ-010 C-001 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research`, `::test_entry_identifies_report` |\n| REQ-010 C-002 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected`, `::test_cli_blank_input_exit_code` |\n| REQ-010 C-003 | manual review recorded as `REVIEW-NNN` in `docs/review-memo.md` |\n| INV-007 | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |\n\nThe module's complete case list, including normal, exception, boundary and regression cases, is in `verification-constraints.md` §7.\n\n## 8. Consequences\n\n**Positive.** Every metric either carries a defensible score in `[0, 1]` or an explicit `not_evaluable` result with a reason. Correctness receives the question, report and reference answer. A single broken metric no longer hides the others or crashes a run. Existing reports can be scored without spending research tokens or calling search. Offline tests can inject a fake judge and run without network or keys. The benchmark entry keeps its evaluator names and return shapes.\n\n**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change. `pyproject.toml` needs `test.evaluation` in the packages list for non-editable installs; this is a dependency-file change and needs human confirmation.\n\n**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.\n\n## 9. Implementation Steps\n\nTests for §7 are written by the Test Author after Gate 1; the steps below are the Build work that follows Gate 2.\n\n1. Create `test/evaluation/__init__.py` and export the public types and `evaluate_existing_report`.\n2. Add `test/evaluation/types.py`: `MetricStatus`, `MetricResult`, `EvaluationResult` and `EvaluationInputError`, with the score/status invariant.\n3. Add `test/evaluation/validation.py`: strict `1..5` integer validation, `value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats, strings, `None` and non-finite values.\n4. Add `test/evaluation/judge.py`: the `Judge` protocol and a `default_judge()` that constructs the baseline `ChatOpenAI` only when called. No model construction at import.\n5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score.\n6. Add `test/evaluation/entry.py`: `evaluate_existing_report`, blank-input rejection before the judge, SHA-256 `report_id`, and the no-research/no-search import boundary.\n7. Add `test/evaluation/evaluate_report.py`: the CLI, JSON output and exit codes `0/1/2`; write input errors to stderr as `error: ...`.\n8. In `test/prompts.py`, add `{user_question}`, `{report}`, `{answer}` and `{today}` to `CORRECTNESS_PROMPT`; do not change its rubric wording.\n9. Replace the bodies of the six functions in `test/evaluators.py` with adapter calls; remove the module-level `eval_model`; preserve names, signatures, baseline keys, the six-item list for overall quality and the single-dict shape for the others; add `status` metadata and the null-score/`value=\"not_evaluable\"` mapping.\n10. Add the README section for `python -m test.evaluation.evaluate_report` and the per-metric result (REQ-010 C-003).\n11. Add `\"test.evaluation\"` to `[tool.setuptools] packages` in `pyproject.toml`; this dependency-file change needs the human's confirmation.\n12. Run `uv run ruff check test/evaluation test/evaluators.py test/prompts.py` and `uv run pytest test/offline` after the Test Author's tests exist. Do not modify `test/run_evaluate.py`, `src/` or the tests.\n"
    }
  ]
}
````

### Event 197 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/evaluation-table.md",
    "oldString": "| B | New `test/evaluation/` core package plus a thin compatibility adapter in `test/evaluators.py` | New `test/evaluation/` package; `test/evaluators.py`; `test/prompts.py`; README; optional `pyproject.toml` package entry | Deterministic validation and entry are separable and testable with a fake judge; judge is constructed lazily; baseline evaluator names and return shapes are preserved; `test/run_evaluate.py` unchanged; matches the blueprint module path | More files and an adapter mapping; a small amount of indirection | Medium | High |",
    "newString": "| B | New `test/evaluation/` core package plus a thin compatibility adapter in `test/evaluators.py` | New `test/evaluation/` package; `test/evaluators.py`; `test/prompts.py`; README; `pyproject.toml` package entry | Deterministic validation and entry are separable and testable with a fake judge; judge is constructed lazily; baseline evaluator names and return shapes are preserved; `test/run_evaluate.py` unchanged; matches the blueprint module path | More files and an adapter mapping; a small amount of indirection | Medium | High |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/evaluation-table.md (1 replacement)"
    }
  ]
}
```

### Event 206 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "`MetricStatus` has exactly two values: `scored` and `not_evaluable`. A `MetricResult` states `metric`, `status`, `score`, `reason` and a machine-readable `reason_code`. Its invariant is: `score` is a `float` in `[0, 1]` when and only when `status == \"scored\"`; otherwise `score is None`.\n\n`EvaluationResult` states `report_id`, the tuple of `MetricResult` objects and `judge_model`. `report_id` is the lowercase hexadecimal SHA-256 of the original report text encoded as UTF-8. There is no caller-supplied report id in the first version.",
    "newString": "`MetricStatus` has exactly two values: `scored` and `not_evaluable`. A `MetricResult` states `metric`, `status`, `score`, `reason` and a machine-readable `reason_code`. Its invariant is: `score` is a `float` in `[0, 1]` when and only when `status == \"scored\"`; otherwise `score is None`. Scored results use `judge_rating` or `grounded_ratio`; `not_evaluable` results use `invalid_rating`, `missing_input`, `no_claims`, `invalid_claim` or `evaluator_error`.\n\n`EvaluationResult` states `report_id`, the tuple of `MetricResult` objects and `judge_model`. `report_id` is the lowercase hexadecimal SHA-256 of the original report text encoded as UTF-8. There is no caller-supplied report id in the first version. `judge_model` is the model identifier of the default judge, or `None` when a caller injected a judge."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 213 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "1. Rejects a blank `question` or `report` with `EvaluationInputError` before any judge call.",
    "newString": "1. Rejects a non-string, blank or whitespace-only `question` or `report` with `EvaluationInputError` before any judge call."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 220 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change. `pyproject.toml` needs `test.evaluation` in the packages list for non-editable installs; this is a dependency-file change and needs human confirmation.",
    "newString": "**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change. `pyproject.toml` gains `test.evaluation` in the packages list for non-editable installs; this dependency-file change is accepted and is applied in the implementation PR, not in this SA change."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 227 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "11. Add `\"test.evaluation\"` to `[tool.setuptools] packages` in `pyproject.toml`; this dependency-file change needs the human's confirmation.",
    "newString": "11. Add `\"test.evaluation\"` to `[tool.setuptools] packages` in `pyproject.toml`; the dependency-file change is accepted for the implementation PR and is not made in this SA change."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 234 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/runtime-policy-catalog.md",
    "oldString": "| POL-002 | The evaluation entry receives a blank question or report | `str.strip()` on both required inputs before any judge call | Raise `EvaluationInputError`; the CLI writes `error: ...` to stderr and exits `2` | None; no evaluator or judge call | N/A (evaluation-only, not a research run) | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |",
    "newString": "| POL-002 | The evaluation entry receives a non-string, blank or whitespace-only question or report | Type and `str.strip()` checks on both required inputs before any judge call | Raise `EvaluationInputError`; the CLI writes `error: ...` to stderr and exits `2` | None; no evaluator or judge call | N/A (evaluation-only, not a research run) | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/runtime-policy-catalog.md (1 replacement)"
    }
  ]
}
```

### Event 243 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff --check && echo \"diff-check OK\"; git status --short; echo \"---changed files---\"; git diff --name-only; echo \"---untracked ADR---\"; ls -l docs/architecture/adr/001-evaluation-module.md"
  },
  "output": [
    {
      "type": "text",
      "text": "diff-check OK\n M docs/architecture/evaluation-table.md\n M docs/architecture/invariants.md\n M docs/architecture/runtime-policy-catalog.md\n M docs/architecture/trace-matrix.md\n M docs/code-governance/structural-constraints.md\n M docs/code-governance/verification-constraints.md\n?? docs/architecture/adr/001-evaluation-module.md\n---changed files---\ndocs/architecture/evaluation-table.md\ndocs/architecture/invariants.md\ndocs/architecture/runtime-policy-catalog.md\ndocs/architecture/trace-matrix.md\ndocs/code-governance/structural-constraints.md\ndocs/code-governance/verification-constraints.md\n---untracked ADR---\n-rw-r--r--@ 1 doppler  staff  18943 Nov 13 23:06 docs/architecture/adr/001-evaluation-module.md\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "for id in \"REQ-009 C-001\" \"REQ-009 C-002\" \"REQ-009 C-003\" \"REQ-009 C-004\" \"REQ-009 M-001\" \"REQ-010 C-001\" \"REQ-010 C-002\" \"REQ-010 C-003\" \"INV-006\" \"INV-007\"; do printf '%-16s ' \"$id\"; grep -c \"$id\" docs/code-governance/verification-constraints.md; done; echo \"---structural section---\"; grep -n \"### evaluation\" docs/code-governance/structural-constraints.md docs/code-governance/verification-constraints.md docs/architecture/runtime-policy-catalog.md"
  },
  "output": [
    {
      "type": "text",
      "text": "REQ-009 C-001    1\nREQ-009 C-002    2\nREQ-009 C-003    1\nREQ-009 C-004    3\nREQ-009 M-001    1\nREQ-010 C-001    2\nREQ-010 C-002    2\nREQ-010 C-003    2\nINV-006          1\nINV-007          1\n---structural section---\ndocs/code-governance/structural-constraints.md:90:### evaluation (REQ-009, REQ-010, ADR-001)\ndocs/code-governance/verification-constraints.md:81:### evaluation (REQ-009, REQ-010, ADR-001)\ndocs/architecture/runtime-policy-catalog.md:24:### evaluation (REQ-009, REQ-010, ADR-001)\n"
    }
  ]
}
```

### Event 256 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-002 | REQ-009 C-002 | boundary |",
    "newString": "| TC-EVAL-002 | REQ-009 C-002 / INV-006 | boundary |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-003 | REQ-009 C-002 | exception |",
    "newString": "| TC-EVAL-003 | REQ-009 C-002 / INV-006 | exception |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-004 | REQ-009 C-003 | exception |",
    "newString": "| TC-EVAL-004 | REQ-009 C-003 / INV-006 | exception |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-005 | REQ-009 C-004 | boundary |",
    "newString": "| TC-EVAL-005 | REQ-009 C-004 / INV-006 | boundary |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-007 | REQ-009 C-004 | exception |",
    "newString": "| TC-EVAL-007 | REQ-009 C-004 / INV-006 | exception |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-008 | REQ-009 M-001 | boundary |",
    "newString": "| TC-EVAL-008 | REQ-009 M-001 / INV-006 | boundary |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-010 | REQ-010 C-001 | normal |",
    "newString": "| TC-EVAL-010 | REQ-010 C-001 / INV-007 | normal |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-012 | REQ-010 C-002 | exception |",
    "newString": "| TC-EVAL-012 | REQ-010 C-002 / INV-007 | exception |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-015 | REQ-010 C-002 / POL-007 | exception |",
    "newString": "| TC-EVAL-015 | REQ-010 C-002 / INV-007 / POL-007 | exception |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

### Event 297 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "for id in \"REQ-009 C-001\" \"REQ-009 C-002\" \"REQ-009 C-003\" \"REQ-009 C-004\" \"REQ-009 M-001\" \"REQ-010 C-001\" \"REQ-010 C-002\" \"REQ-010 C-003\" \"INV-006\" \"INV-007\"; do printf '%-16s ' \"$id\"; grep -c \"$id\" docs/code-governance/verification-constraints.md; done; echo \"---diff check---\"; git diff --check && echo OK"
  },
  "output": [
    {
      "type": "text",
      "text": "REQ-009 C-001    1\nREQ-009 C-002    2\nREQ-009 C-003    1\nREQ-009 C-004    3\nREQ-009 M-001    1\nREQ-010 C-001    2\nREQ-010 C-002    2\nREQ-010 C-003    2\nINV-006          7\nINV-007          4\n---diff check---\nOK\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "uv run python scripts/validate_requirements.py"
  },
  "output": [
    {
      "type": "text",
      "text": "PASS: 10 requirements valid\n"
    }
  ]
}
```

### Event 310 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "grep -n \"optional pyproject\\|needs human confirmation\\|TBD\" docs/architecture/adr/001-evaluation-module.md docs/architecture/evaluation-table.md docs/architecture/invariants.md docs/architecture/runtime-policy-catalog.md docs/code-governance/structural-constraints.md docs/code-governance/verification-constraints.md || true; echo \"---ADR sections---\"; grep -n \"^## \" docs/architecture/adr/001-evaluation-module.md"
  },
  "output": [
    {
      "type": "text",
      "text": "docs/architecture/runtime-policy-catalog.md:12:| POL-001 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |\n---ADR sections---\n10:## 1. Architecturally Significant Requirements\n17:## 2. Context\n30:## 3. Decision\n121:## 4. Rejected Options\n130:## 5. Components and Interfaces\n145:## 6. State, Failure Handling and Deterministic Boundary\n152:## 7. Verification\n169:## 8. Consequences\n177:## 9. Implementation Steps\n"
    }
  ]
}
```

#### Tool shell — error

```json
{
  "input": {
    "command": "git diff --stat; echo \"---new ADR lines---\"; wc -l docs/architecture/adr/001-evaluation-module.md; echo \"---no source/test changes---\"; git status --short | grep -E '^( M|\\?\\?) (src|test|pyproject|uv.lock|docs/approvals)' || echo \"none\""
  },
  "output": null,
  "error": {
    "type": "permission.rejected",
    "message": "Permission denied: shell"
  }
}
```

### Event 323 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff --stat"
  },
  "output": [
    {
      "type": "text",
      "text": " docs/architecture/evaluation-table.md            | 28 ++++++++++++++++++++++++\n docs/architecture/invariants.md                  | 20 +++++++++++++++++\n docs/architecture/runtime-policy-catalog.md      | 12 ++++++++++\n docs/architecture/trace-matrix.md                |  4 ++--\n docs/code-governance/structural-constraints.md   | 15 +++++++++++++\n docs/code-governance/verification-constraints.md | 24 ++++++++++++++++++++\n 6 files changed, 101 insertions(+), 2 deletions(-)\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "git status --short"
  },
  "output": [
    {
      "type": "text",
      "text": " M docs/architecture/evaluation-table.md\n M docs/architecture/invariants.md\n M docs/architecture/runtime-policy-catalog.md\n M docs/architecture/trace-matrix.md\n M docs/code-governance/structural-constraints.md\n M docs/code-governance/verification-constraints.md\n?? docs/architecture/adr/001-evaluation-module.md\n"
    }
  ]
}
```

### Event 336 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/evaluation-table.md",
    "oldString": "| B | New `test/evaluation/` core package plus a thin compatibility adapter in `test/evaluators.py` | New `test/evaluation/` package; `test/evaluators.py`; `test/prompts.py`; README; `pyproject.toml` package entry | Deterministic validation and entry are separable and testable with a fake judge; judge is constructed lazily; baseline evaluator names and return shapes are preserved; `test/run_evaluate.py` unchanged; matches the blueprint module path | More files and an adapter mapping; a small amount of indirection | Medium | High |",
    "newString": "| B | New `test/evaluation/` core package plus a thin compatibility adapter in `test/evaluators.py` | New `test/evaluation/` package; `test/evaluators.py`; `test/prompts.py`; README | Deterministic validation and entry are separable and testable with a fake judge; judge is constructed lazily; baseline evaluator names and return shapes are preserved; `test/run_evaluate.py` unchanged; matches the blueprint module path | More files and an adapter mapping; a small amount of indirection | Medium | High |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/evaluation-table.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change. `pyproject.toml` gains `test.evaluation` in the packages list for non-editable installs; this dependency-file change is accepted and is applied in the implementation PR, not in this SA change.",
    "newString": "**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/structural-constraints.md",
    "oldString": "| Configuration flag | None: the module is evaluation-only and adds no runtime behaviour flag. |\n\n`test/evaluators.py` is a thin compatibility adapter; evaluation logic lives only in `test/evaluation/`. The `test.evaluation` subpackage is added to `[tool.setuptools] packages` in the same implementation PR so a non-editable install does not omit it.",
    "newString": "| Configuration flag | None: the module is evaluation-only and adds no runtime behaviour flag. |\n\n`test/evaluators.py` is a thin compatibility adapter; evaluation logic lives only in `test/evaluation/`."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/structural-constraints.md (1 replacement)"
    }
  ]
}
```

### Event 353 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "grep -rn \"pyproject\" docs/architecture/evaluation-table.md docs/architecture/adr/001-evaluation-module.md docs/architecture/invariants.md docs/architecture/runtime-policy-catalog.md docs/architecture/trace-matrix.md docs/code-governance/structural-constraints.md docs/code-governance/verification-constraints.md"
  },
  "output": [
    {
      "type": "text",
      "text": "docs/architecture/adr/001-evaluation-module.md:191:11. Add `\"test.evaluation\"` to `[tool.setuptools] packages` in `pyproject.toml`; the dependency-file change is accepted for the implementation PR and is not made in this SA change.\ndocs/code-governance/structural-constraints.md:20:`[tool.setuptools] packages` in `pyproject.toml` lists `open_deep_research` and `test`. A new extension subpackage is added to that list in the same PR, or a non-editable install omits it.\ndocs/code-governance/structural-constraints.md:67:4. **Dependencies:** declared in `pyproject.toml` with their purpose, locked in `uv.lock`, agreed with the human first.\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff --check && echo OK; uv run python scripts/validate_requirements.py"
  },
  "output": [
    {
      "type": "text",
      "text": "OK\nPASS: 10 requirements valid\n"
    }
  ]
}
```

### Event 366 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "sed -n '160,200p' docs/architecture/adr/001-evaluation-module.md; echo \"---EVAL TAIL---\"; sed -n '38,70p' docs/architecture/evaluation-table.md"
  },
  "output": [
    {
      "type": "text",
      "text": "| REQ-009 M-001 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| INV-006 | `test/offline/test_evaluator_validity.py` (all cases; no out-of-range score, no score on `not_evaluable`) |\n| REQ-010 C-001 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research`, `::test_entry_identifies_report` |\n| REQ-010 C-002 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected`, `::test_cli_blank_input_exit_code` |\n| REQ-010 C-003 | manual review recorded as `REVIEW-NNN` in `docs/review-memo.md` |\n| INV-007 | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |\n\nThe module's complete case list, including normal, exception, boundary and regression cases, is in `verification-constraints.md` §7.\n\n## 8. Consequences\n\n**Positive.** Every metric either carries a defensible score in `[0, 1]` or an explicit `not_evaluable` result with a reason. Correctness receives the question, report and reference answer. A single broken metric no longer hides the others or crashes a run. Existing reports can be scored without spending research tokens or calling search. Offline tests can inject a fake judge and run without network or keys. The benchmark entry keeps its evaluator names and return shapes.\n\n**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change.\n\n**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.\n\n## 9. Implementation Steps\n\nTests for §7 are written by the Test Author after Gate 1; the steps below are the Build work that follows Gate 2.\n\n1. Create `test/evaluation/__init__.py` and export the public types and `evaluate_existing_report`.\n2. Add `test/evaluation/types.py`: `MetricStatus`, `MetricResult`, `EvaluationResult` and `EvaluationInputError`, with the score/status invariant.\n3. Add `test/evaluation/validation.py`: strict `1..5` integer validation, `value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats, strings, `None` and non-finite values.\n4. Add `test/evaluation/judge.py`: the `Judge` protocol and a `default_judge()` that constructs the baseline `ChatOpenAI` only when called. No model construction at import.\n5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score.\n6. Add `test/evaluation/entry.py`: `evaluate_existing_report`, blank-input rejection before the judge, SHA-256 `report_id`, and the no-research/no-search import boundary.\n7. Add `test/evaluation/evaluate_report.py`: the CLI, JSON output and exit codes `0/1/2`; write input errors to stderr as `error: ...`.\n8. In `test/prompts.py`, add `{user_question}`, `{report}`, `{answer}` and `{today}` to `CORRECTNESS_PROMPT`; do not change its rubric wording.\n9. Replace the bodies of the six functions in `test/evaluators.py` with adapter calls; remove the module-level `eval_model`; preserve names, signatures, baseline keys, the six-item list for overall quality and the single-dict shape for the others; add `status` metadata and the null-score/`value=\"not_evaluable\"` mapping.\n10. Add the README section for `python -m test.evaluation.evaluate_report` and the per-metric result (REQ-010 C-003).\n11. Add `\"test.evaluation\"` to `[tool.setuptools] packages` in `pyproject.toml`; the dependency-file change is accepted for the implementation PR and is not made in this SA change.\n12. Run `uv run ruff check test/evaluation test/evaluators.py test/prompts.py` and `uv run pytest test/offline` after the Test Author's tests exist. Do not modify `test/run_evaluate.py`, `src/` or the tests.\n---EVAL TAIL---\n**Rejected and why:** <option>: <reason>.\n\n## EVAL-001: How should evaluation produce valid metric results and score an existing report?\n\n- **Module:** evaluation\n- **Owner:** DopplerXD\n- **Decision recorded in:** ADR-001\n- **Status:** Decided\n\n**ASR**\n\n| Requirement | Acceptance criteria | Quality attributes at stake |\n|---|---|---|\n| REQ-009 | C-001, C-002, C-003, C-004, M-001 | Correctness of the score; deterministic validation; failure isolation; offline testability; compatibility with the LangSmith benchmark entry |\n| REQ-010 | C-001, C-002, C-003 | Separation from the research graph and search; input validation before any evaluator; documented use; low operating cost |\n\n**Candidates**\n\n| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |\n|---|---|---|---|---|---|---|\n| A | Harden `test/evaluators.py` in place and add a separate entry file | `test/evaluators.py`, `test/prompts.py`, a new entry script | Smallest file churn; baseline entry untouched; direct reuse of existing functions | Validation, judge construction, LangSmith serialisation and entry logic stay mixed; the import-time model side effect is harder to remove safely; no clean module boundary for pure tests | Low | Medium |\n| B | New `test/evaluation/` core package plus a thin compatibility adapter in `test/evaluators.py` | New `test/evaluation/` package; `test/evaluators.py`; `test/prompts.py`; README | Deterministic validation and entry are separable and testable with a fake judge; judge is constructed lazily; baseline evaluator names and return shapes are preserved; `test/run_evaluate.py` unchanged; matches the blueprint module path | More files and an adapter mapping; a small amount of indirection | Medium | High |\n| C | Duplicate the evaluators in a standalone evaluation service and leave the baseline untouched | New standalone service; existing scripts unchanged | Strong isolation from the benchmark path | Two sources of truth; REQ-009 fixes do not reach the benchmark; duplicated maintenance; violates “extend, never replace” | High | High |\n\n**Choice:** option B — it separates deterministic validation and the evaluation-only entry from the LangSmith adapter, keeps the baseline entry compatible, and allows every REQ-009 and REQ-010 case to run offline with an injected judge. It also places the module at the path assigned by `architecture-blueprint.md` §4.\n\n**Rejected and why:** option A: the core logic remains coupled to the evaluator functions and the import-time model construction, which makes failure isolation and offline tests harder to guarantee. option C: it duplicates metric logic, leaves the benchmark path broken, and creates two sources of truth for the same scores.\n\nThe decision, interfaces and implementation steps are in ADR-001.\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff --stat; echo \"---\"; git status --short"
  },
  "output": [
    {
      "type": "text",
      "text": " docs/architecture/evaluation-table.md            | 28 ++++++++++++++++++++++++\n docs/architecture/invariants.md                  | 20 +++++++++++++++++\n docs/architecture/runtime-policy-catalog.md      | 12 ++++++++++\n docs/architecture/trace-matrix.md                |  4 ++--\n docs/code-governance/structural-constraints.md   | 15 +++++++++++++\n docs/code-governance/verification-constraints.md | 24 ++++++++++++++++++++\n 6 files changed, 101 insertions(+), 2 deletions(-)\n---\n M docs/architecture/evaluation-table.md\n M docs/architecture/invariants.md\n M docs/architecture/runtime-policy-catalog.md\n M docs/architecture/trace-matrix.md\n M docs/code-governance/structural-constraints.md\n M docs/code-governance/verification-constraints.md\n?? docs/architecture/adr/001-evaluation-module.md\n"
    }
  ]
}
```

### Event 379 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "wc -l docs/architecture/adr/001-evaluation-module.md; sed -n '1,10p' docs/architecture/adr/001-evaluation-module.md"
  },
  "output": [
    {
      "type": "text",
      "text": "     192 docs/architecture/adr/001-evaluation-module.md\n# ADR-001: Evaluation module — valid metric results and an evaluation-only entry\n\n- **Status:** Proposed\n- **Date:** 2026-11-13\n- **Module:** evaluation\n- **Owner:** DopplerXD\n- **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)\n- **SA Review:** SA-NNN (`docs/review-memo.md`), to be assigned at acceptance\n\n## 1. Architecturally Significant Requirements\n"
    }
  ]
}
```

### Event 388 — OpenCode (build)

## 完成情况

已按临时授权的 Build 角色完成 evaluation 模块的 **SA 文档草案**。仅修改/新建以下 7 个文档；未修改源码、测试代码、`pyproject.toml`、权限或审批记录；未提交、未推送、未进入功能实现。ADR 状态保持 **Proposed**。

## 1. 实际文件差异

| 文件 | 状态 | 差异 |
|---|---|---|
| `docs/architecture/evaluation-table.md` | 修改 | 新增 `EVAL-001`：ASR、A/B/C 三方案比较、选择 B、拒绝 A/C 的理由（+28 行） |
| `docs/architecture/adr/001-evaluation-module.md` | 新建 | 192 行；从模板填写全部九节，含组件、接口、状态、严格整数校验、失败隔离、CLI、LangSmith 适配、逐文件实现步骤 |
| `docs/architecture/invariants.md` | 修改 | 新增 `INV-006`（评分有效或 `not_evaluable`）与 `INV-007`（评估入口不触发研究/搜索）（+20 行） |
| `docs/architecture/runtime-policy-catalog.md` | 修改 | §2 新增 evaluation 模块 `POL-002`—`POL-008`（+12 行） |
| `docs/architecture/trace-matrix.md` | 修改 | 更新 REQ-009、REQ-010 两行（+2/−2） |
| `docs/code-governance/structural-constraints.md` | 修改 | §10 新增 evaluation 模块约束表（+15 行） |
| `docs/code-governance/verification-constraints.md` | 修改 | §7 新增 evaluation 用例表 `TC-EVAL-001`—`016`（+24 行） |

`git diff --stat`：6 个已跟踪文件，`101 insertions(+), 2 deletions(-)`；ADR 为新增未跟踪文件。

## 2. 验收覆盖清单

| 需求/准则 | 覆盖用例 |
|---|---|
| REQ-009 C-001 | TC-EVAL-001：各指标 judge 请求包含 question/report/reference/brief/evidence |
| REQ-009 C-002 | TC-EVAL-002（1→0.2、5→1.0）、TC-EVAL-003（0/6/布尔/字符串/4.5/NaN/inf/None → `not_evaluable`, null score） |
| REQ-009 C-003 | TC-EVAL-004：缺 reference/brief/evidence 仅影响依赖指标 |
| REQ-009 C-004 | TC-EVAL-005（空 claims）、006（2/4→0.5）、007（单指标异常隔离） |
| REQ-009 M-001 | TC-EVAL-008：`out_of_range_score_count == 0` |
| INV-006 | TC-EVAL-002—009，重点 TC-009 适配器契约 |
| REQ-010 C-001 | TC-EVAL-010（零 research/search 调用）、TC-EVAL-013（SHA-256 报告标识） |
| REQ-010 C-002 | TC-EVAL-012（空白输入拒绝）、TC-EVAL-015（CLI stderr + exit 2） |
| REQ-010 C-003 | TC-EVAL-014：README 人工检查，证据进 `docs/review-memo.md` 的 `REVIEW-NNN` |
| INV-007 | TC-EVAL-010、011、012、015，重点 TC-011 子进程导入边界 |
| CLI 策略 | TC-EVAL-015（exit 2）、TC-EVAL-016（exit 1/0） |
| 回归 | `uv run pytest test/offline`；`test/evaluators.py` 适配器契约；`test/run_evaluate.py` 六个 evaluator 名称与签名不变 |

## 3. 检查结果

| 检查 | 结果 |
|---|---|
| `git diff --check` | **PASS** |
| `uv run python scripts/validate_requirements.py` | **PASS**：`10 requirements valid` |
| 改动范围核对 | **PASS**：仅上述 7 个文档；无 `src/`、`test/`、`pyproject.toml`、`docs/approvals/` 改动 |
| `uv run pytest test/offline` | **NOT_RUN**：SA 阶段尚未编写测试，`test/offline/` 仅有占位文件 |
| `uv run ruff check` | **NOT_RUN**：本轮无代码改动 |
| 提交/推送 | **N/A**：明确禁止 |

## 4. 未解决事项

1. **SA Review / Gate 1 未执行**：ADR-001 仍为 `Proposed`，`SA-NNN` 待评审后分配。
2. **测试尚未编写**：`TC-EVAL-001`—`016` 由 Test Author 在 Gate 1 后编写，并在 baseline 上确认失败原因。
3. **实现步骤未执行**：ADR §9 的 `test/evaluation/` 实现、`test/prompts.py` 占位符修复、`test/evaluators.py` 适配器、README 与 CLI 均属 Gate 2 之后。
4. **`pyproject.toml` 未改**：按你的要求，仅在 ADR §9 第 11 步记录 `"test.evaluation"` 的打包调整；实际变更留给实现 PR。
5. **POL 编号为临时编号**：`POL-002`—`008` 集成时可能统一重编号。
6. **`structural-constraints.md` §1 措辞**：§1 仍写顶层 `test/` 不放新工作；§10 已明确 `test/evaluation/` 是 evaluation 模块路径，建议集成时由集成者确认这一例外。
7. **LangSmith null-score 的线上表现**：已核对 installed `langsmith 0.9.2` 的 `EvaluationResult`/`SCORE_TYPE` 与官方返回契约，`score=None` 类型合法；但未连接真实 LangSmith 服务验证 UI/汇总展示。设计上明确不把 `not_evaluable` 计为 0。
8. **`test/run_evaluate.py` 导入副作用仍在**：`load_dotenv("../.env")`、`Client()` 位于该基线脚本；本轮按“基准入口兼容”未改动，评估入口通过独立模块避开它。

## 5. AI 使用日志建议条目

```yaml
- id: AIU-NNN
  date: "2026-11-13"
  member: DopplerXD
  purpose: >-
    Draft and write the Phase 1 SA documents for the evaluation module for REQ-009 and REQ-010,
    under a temporary Build-role exception limited to documentation.
  prompt: >-
    Follow AGENTS.md reading order and Prompt.md Phase 1. For REQ-009/REQ-010 (evaluation,
    test/evaluation/), verify role/branch/permissions; analyse test/evaluators.py,
    test/prompts.py and test/run_evaluate.py; map C-001—C-004/M-001 and C-001—C-003; compare
    three ADD candidates; write a Proposed ADR with nine sections; add the evaluation module
    sections to invariants, runtime policies, trace matrix, structural constraints §10 and
    verification constraints §7. Use option B, strict integer ratings, not_evaluable with null
    score, SHA-256 report identity and CLI exit codes 0/1/2. Do not modify source, tests,
    dependency configuration, permissions or approvals.
  requirements: [REQ-009, REQ-010]
  artifacts:
    - docs/architecture/evaluation-table.md
    - docs/architecture/adr/001-evaluation-module.md
    - docs/architecture/invariants.md
    - docs/architecture/runtime-policy-catalog.md
    - docs/architecture/trace-matrix.md
    - docs/code-governance/structural-constraints.md
    - docs/code-governance/verification-constraints.md
  supervision: >-
    The member confirmed option B and decisions 1/2/3, reviewed the strict rating and
    LangSmith null-score mapping, checked the packaging evidence, and will review the ADR and
    module sections before SA Review. The Build role exception applied only to these documents.
  transcript: null
```

### Event 397 — agent-switched

```json
{
  "time": {
    "created": 1794583015836
  },
  "agent": "plan",
  "previous": "build"
}
```

### Event 402 — User

进入本次 SA 草稿提交前的检查。

1. 对照 REQ-009、REQ-010 和仓库模板检查已生成的7个文档，
   检查接口、编号、交叉引用和全部验收项是否一致。
2. 明确评分原始类型必须在Pydantic类型转换前校验，
   并在测试清单补充4.0必须被拒绝。
3. 将结构约束§1与test/evaluation/路径的冲突，
   作为待模块评审确认的问题列出。
4. 区分LangSmith类型兼容性检查和实际线上验证，
   已执行检查应记录依据，尚未执行的保持NOT_RUN。
5. 检查AI日志建议条目，只保留真实发生的人工决定，
   不得写成已完成SA Review或测试验收。

仅检查、修订本模块SA文档，给出最终差异摘要和
待评审问题。暂不提交、推送。

> **H-05 Pre-submission corrections**
> 要求在类型转换前检查评分，补充 4.0 用例，记录路径冲突，并区分类型契约检查与真实线上验证。

### Event 403 — OpenCode (plan)

我回到 Plan mode，只能做只读检查；本轮不会修改仓库文件。下面是逐项核对结果和可直接应用的修订建议。

#### Tool shell — completed

````json
{
  "input": {
    "command": "sed -n '1,30p' docs/code-governance/structural-constraints.md; echo \"=====ADR 3.5 / 5 / 7 / 8=====\"; sed -n '60,120p' docs/architecture/adr/001-evaluation-module.md; sed -n '130,180p' docs/architecture/adr/001-evaluation-module.md"
  },
  "output": [
    {
      "type": "text",
      "text": "# Structural Constraints\n\n> **Purpose:** The rules every member follows when changing code structure, so that parallel work by six people can be merged.\n> **Authoritative for:** source layout, change rules, dependency direction and code-level traceability. *Which* modules exist is decided in `docs/architecture/architecture-blueprint.md` §4; where a specific requirement lands is decided in its ADR.\n> **Maintained by:** humans for §1–§9; each module owner writes their module's section in §10, integrated before SA Review.\n> **Last updated:** 2026-11-12\n\n## 1. Source Layout\n\n| Path | Role | New work goes here? |\n|---|---|---|\n| `src/open_deep_research/` | Baseline implementation: `deep_researcher.py` (graphs and nodes), `state.py`, `configuration.py`, `prompts.py`, `utils.py` | Yes |\n| `src/open_deep_research/<extension>/` | One extension module per architectural element (blueprint §4) | Yes, by its owner |\n| `src/security/` | Supabase JWT and LangGraph auth, loaded through `langgraph.json` | Only with separate review |\n| `test/` | Existing LLM- and API-dependent evaluation scripts | No |\n| `test/offline/` | Deterministic tests: no network, no LLM calls, run in CI | Yes, primary test location |\n| `test/live/` | Tests that call real models or APIs, run on demand | Yes, when a module test case requires it (`verification-constraints.md` §7) |\n| `scripts/` | Project tooling used by CI and humans, e.g. `validate_requirements.py` | Only with human approval |\n\n`[tool.setuptools] packages` in `pyproject.toml` lists `open_deep_research` and `test`. A new extension subpackage is added to that list in the same PR, or a non-editable install omits it.\n\n## 2. Graphs and Nodes\n\n1. **Thin nodes** (accepted 2026-10-13): graph wiring, node names and node signatures stay in `deep_researcher.py`; a node body calls the module that owns its logic and contains no architectural logic of its own.\n2. **Topology:** the three baseline graphs and their nodes (blueprint §3) stay unchanged. Adding or removing a node or edge needs an accepted ADR.\n\n## 3. Tool Assembly\n\n1. Researcher tools have one entry point, `utils.get_all_tools(config)`, which adds core tools (`ResearchComplete`, `think_tool`), then search tools for the configured `SearchAPI` (`utils.get_search_tool`), then MCP tools (`utils.load_mcp_tools`, wrapped by `utils.wrap_mcp_authenticate_tool`; `existing_tool_names` prevents name clashes).\n2. `SearchAPI` values are `tavily`, `openai`, `anthropic` and `none`.\n=====ADR 3.5 / 5 / 7 / 8=====\n### 3.4 Inputs per metric\n\n- Question and report: all metrics except groundedness; the entry requires both to be non-blank.\n- Reference answer: correctness only.\n- Research brief: completeness only.\n- Evidence (`raw_notes` equivalent): groundedness only.\n\nIf an optional input is missing or blank, only the metrics that require it become `not_evaluable`; the other metrics are still evaluated. If the question or report is missing in the LangSmith adapter, every metric that needs it becomes `not_evaluable` and the adapter does not raise.\n\n### 3.5 Strict rating validation\n\nA judge rating is accepted only when `type(value) is int` and `1 <= value <= 5`. Booleans, floats (including `4.0`), strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and a reason code such as `invalid_rating`. Scores are never clamped, rounded, defaulted or replaced by zero.\n\nGroundedness is the only ratio metric: the judge's claims must be a non-empty list; the score is `grounded_count / total_claims`; an empty list produces `status=\"not_evaluable\"` with reason code `no_claims`. A claim whose `grounded` field is not a boolean makes the metric `not_evaluable` rather than being coerced.\n\n### 3.6 Failure isolation\n\nMetric groups are evaluated independently. A group is one judge call and the metrics it produces: overall quality produces six metrics from one call; each other evaluator produces one metric from one call. An exception in a group makes only that group's metrics `not_evaluable` with a reason code such as `evaluator_error`; the remaining groups still run. The implementation catches `Exception`, never `BaseException`, so interruption and process exit are not swallowed.\n\n### 3.7 Evaluation-only entry\n\n`evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult`:\n\n1. Rejects a non-string, blank or whitespace-only `question` or `report` with `EvaluationInputError` before any judge call.\n2. Computes `report_id` as the SHA-256 of the supplied report text; the report text is passed to the judge unchanged.\n3. Runs the metric groups against the supplied inputs.\n4. Returns `EvaluationResult`; it never compiles or invokes the research graph, imports `open_deep_research.deep_researcher`, calls a search provider or generates a replacement report.\n\n`Judge` is a protocol with an `invoke(messages, schema)` method. `default_judge()` constructs the baseline judge model lazily on first use; it is injectable for offline tests. Importing `test.evaluation` or `test.evaluators` must not construct a model client or read an API key.\n\n### 3.8 CLI\n\n`python -m test.evaluation.evaluate_report --report <path> --question <text>` accepts optional `--reference-answer`, `--research-brief` and `--evidence`. It prints the result as JSON on stdout. Exit codes are:\n\n| Code | Meaning |\n|---|---|\n| `0` | Evaluation completed and at least one metric is `scored`. |\n| `1` | Evaluation completed but every metric is `not_evaluable`. |\n| `2` | Input, argument or report-file error; the message is written to stderr as `error: ...` and no evaluator runs. |\n\nThe README gains a short section showing the command and how to read the per-metric result (REQ-010 C-003).\n\n### 3.9 LangSmith compatibility adapter\n\n`test/evaluators.py` keeps the six baseline function names and signatures and delegates to `test/evaluation`. It removes the module-level `eval_model` and does not construct a client at import. `overall_quality` still returns a list of six dictionaries; the other evaluators return one dictionary. Each dictionary keeps `key`, `score` and `comment` and adds `status` in `metadata`.\n\nThe conversion is:\n\n```python\n# scored\n{\"key\": \"correctness_score\", \"score\": 0.8, \"comment\": \"<reason>\",\n \"metadata\": {\"status\": \"scored\"}}\n\n# not_evaluable\n{\"key\": \"groundedness_score\", \"score\": None, \"value\": \"not_evaluable\",\n \"comment\": \"not_evaluable:no_claims: <detail>\",\n \"metadata\": {\"status\": \"not_evaluable\", \"reason_code\": \"no_claims\"}}\n```\n\n`score=None` is permitted by the LangSmith `EvaluationResult` score type and by `create_feedback`. `not_evaluable` must never be converted to `0`: a null score is not counted as a numeric score, while `value` and `metadata` keep the status and reason visible. If a whole evaluator group fails before producing any metric, the adapter returns every key that group owns as `not_evaluable`, so LangSmith still sees all metric keys.\n\n## 5. Components and Interfaces\n\n| Component | Responsibility | Interface (signature or type) | Called by |\n|---|---|---|---|\n| `test/evaluation/types.py` | Result and error types | `MetricStatus`, `MetricResult`, `EvaluationResult`, `EvaluationInputError` | all evaluation components; adapters |\n| `test/evaluation/validation.py` | Deterministic rating, claim-ratio and input checks | `validate_rating(value) -> float`, `groundedness_ratio(claims) -> float`, `require_text(value) -> bool` | `metrics.py`, `entry.py` |\n| `test/evaluation/judge.py` | Judge boundary; lazy model construction | `Judge.invoke(messages, schema)`, `default_judge() -> Judge` | `metrics.py`, `entry.py` |\n| `test/evaluation/metrics.py` | Run metric groups, normalise and isolate failures | `evaluate_metrics(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> tuple[MetricResult, ...]` | `entry.py`, `test/evaluators.py` |\n| `test/evaluation/entry.py` | Evaluation-only public entry | `evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult` | CLI, callers, `test/evaluators.py` |\n| `test/evaluation/evaluate_report.py` | CLI and exit-code handling | `main(argv=None) -> int`; `python -m test.evaluation.evaluate_report` | humans, scripts |\n| `test/evaluators.py` | Baseline LangSmith adapter | `eval_overall_quality(inputs, outputs)`, `eval_relevance(inputs, outputs)`, `eval_structure(inputs, outputs)`, `eval_correctness(inputs, outputs, reference_outputs)`, `eval_groundedness(inputs, outputs)`, `eval_completeness(inputs, outputs)` | `test/run_evaluate.py` |\n| `test/prompts.py` | Judge templates | `CORRECTNESS_PROMPT` gains `{user_question}`, `{report}`, `{answer}` and `{today}` placeholders | `metrics.py` |\n\n**Shared contracts changed (`structural-constraints.md` §6):** none. The module adds no `state.py` type and no graph state field. The baseline LangSmith evaluator key and return-shape contract is preserved by the adapter; `test/run_evaluate.py` does not change.\n\n## 6. State, Failure Handling and Deterministic Boundary\n\n- **State:** none. The module does not add or change graph state; `memory-design.md` §5 has no evaluation entry.\n- **Runtime policies:** POL-002 to POL-008 (`runtime-policy-catalog.md` §2), covering blank input, missing optional input, invalid rating, empty claims, evaluator exception and CLI exit codes.\n- **Invariants:** INV-006 (valid or `not_evaluable` metric results) and INV-007 (evaluation-only entry does not run research or search).\n- **Deterministic boundary:** the model supplies ratings and claim judgements only. Deterministic code decides whether the rating is a valid integer `1..5`, whether the normalised score is in `[0, 1]`, whether at least one claim exists, whether required inputs are present, whether a metric is `not_evaluable` and whether an exception stays local to its metric group.\n\n## 7. Verification\n\n| Requirement and criterion | Verification |\n|---|---|\n| REQ-009 C-001 | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |\n| REQ-009 C-002 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| REQ-009 C-003 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\n| REQ-009 C-004 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors`, `::test_one_metric_error_does_not_abort_others` |\n| REQ-009 M-001 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| INV-006 | `test/offline/test_evaluator_validity.py` (all cases; no out-of-range score, no score on `not_evaluable`) |\n| REQ-010 C-001 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research`, `::test_entry_identifies_report` |\n| REQ-010 C-002 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected`, `::test_cli_blank_input_exit_code` |\n| REQ-010 C-003 | manual review recorded as `REVIEW-NNN` in `docs/review-memo.md` |\n| INV-007 | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |\n\nThe module's complete case list, including normal, exception, boundary and regression cases, is in `verification-constraints.md` §7.\n\n## 8. Consequences\n\n**Positive.** Every metric either carries a defensible score in `[0, 1]` or an explicit `not_evaluable` result with a reason. Correctness receives the question, report and reference answer. A single broken metric no longer hides the others or crashes a run. Existing reports can be scored without spending research tokens or calling search. Offline tests can inject a fake judge and run without network or keys. The benchmark entry keeps its evaluator names and return shapes.\n\n**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change.\n\n**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.\n\n## 9. Implementation Steps\n\nTests for §7 are written by the Test Author after Gate 1; the steps below are the Build work that follows Gate 2.\n\n"
    }
  ]
}
````

#### Tool shell — completed

```json
{
  "input": {
    "command": "grep -n \"TC-EVAL-003\\|4.5\\|4.0\\|NOT_RUN\\|LangSmith\" docs/code-governance/verification-constraints.md docs/architecture/adr/001-evaluation-module.md docs/architecture/evaluation-table.md | sed -n '1,120p'"
  },
  "output": [
    {
      "type": "text",
      "text": "docs/code-governance/verification-constraints.md:52:| Regression | `offline-tests` | `pytest test/offline` | Active; reports `NOT_RUN` while the directory has no tests |\ndocs/code-governance/verification-constraints.md:61:- Verdicts are only `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED` and `N/A`. A skipped test is `NOT_RUN`, never `PASS`.\ndocs/code-governance/verification-constraints.md:62:- No check is reported as passed without execution evidence. A mandatory check that is `FAIL`, `NOT_RUN` or `BLOCKED` keeps the requirement from `verified`.\ndocs/code-governance/verification-constraints.md:87:| TC-EVAL-003 | REQ-009 C-002 / INV-006 | exception | Ratings `0`, `6`, `True`, `\"4\"`, `4.5`, `NaN`, `inf`, `None` | `not_evaluable`, `score=None`, reason code `invalid_rating`; no clamping or default | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\ndocs/architecture/adr/001-evaluation-module.md:19:The evaluation code is a set of LangSmith evaluator functions in `test/evaluators.py`; `test/run_evaluate.py` passes them to `Client.aevaluate`. The baseline has these defects:\ndocs/architecture/adr/001-evaluation-module.md:26:- `test/run_evaluate.py` L32-61 compiles and invokes the full research graph for every dataset example; L9-11 also runs `load_dotenv(\"../.env\")` and constructs a LangSmith `Client` at import. There is no entry that scores an already generated report.\ndocs/architecture/adr/001-evaluation-module.md:28:The blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. Offline tests must run without network access, API keys or model calls (`verification-constraints.md` §3), and the baseline LangSmith entry must keep working because it is the benchmark path. The structural constraint that `test/` holds baseline scripts is addressed by keeping evaluation logic in `test/evaluation/` and leaving `test/run_evaluate.py` unchanged; `test/evaluators.py` becomes a thin compatibility adapter.\ndocs/architecture/adr/001-evaluation-module.md:58:The public metric names preserve the baseline LangSmith keys: `research_depth_score`, `source_quality_score`, `analytical_rigor_score`, `practical_value_score`, `balance_and_objectivity_score`, `writing_quality_score`, `relevance_score`, `structure_and_cohesiveness_score`, `correctness_score`, `groundedness_score` and `completeness_score`. The six overall-quality dimensions are six independent metric results, not one aggregate.\ndocs/architecture/adr/001-evaluation-module.md:67:If an optional input is missing or blank, only the metrics that require it become `not_evaluable`; the other metrics are still evaluated. If the question or report is missing in the LangSmith adapter, every metric that needs it becomes `not_evaluable` and the adapter does not raise.\ndocs/architecture/adr/001-evaluation-module.md:71:A judge rating is accepted only when `type(value) is int` and `1 <= value <= 5`. Booleans, floats (including `4.0`), strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and a reason code such as `invalid_rating`. Scores are never clamped, rounded, defaulted or replaced by zero.\ndocs/architecture/adr/001-evaluation-module.md:102:### 3.9 LangSmith compatibility adapter\ndocs/architecture/adr/001-evaluation-module.md:119:`score=None` is permitted by the LangSmith `EvaluationResult` score type and by `create_feedback`. `not_evaluable` must never be converted to `0`: a null score is not counted as a numeric score, while `value` and `metadata` keep the status and reason visible. If a whole evaluator group fails before producing any metric, the adapter returns every key that group owns as `not_evaluable`, so LangSmith still sees all metric keys.\ndocs/architecture/adr/001-evaluation-module.md:125:| A — harden `test/evaluators.py` in place and add a separate entry file | Keeps judge construction, validation, LangSmith serialisation and entry logic in one module; the import side effect and the mixing of adapter and core logic remain, and pure validation is harder to test offline. |\ndocs/architecture/adr/001-evaluation-module.md:140:| `test/evaluators.py` | Baseline LangSmith adapter | `eval_overall_quality(inputs, outputs)`, `eval_relevance(inputs, outputs)`, `eval_structure(inputs, outputs)`, `eval_correctness(inputs, outputs, reference_outputs)`, `eval_groundedness(inputs, outputs)`, `eval_completeness(inputs, outputs)` | `test/run_evaluate.py` |\ndocs/architecture/adr/001-evaluation-module.md:143:**Shared contracts changed (`structural-constraints.md` §6):** none. The module adds no `state.py` type and no graph state field. The baseline LangSmith evaluator key and return-shape contract is preserved by the adapter; `test/run_evaluate.py` does not change.\ndocs/architecture/adr/001-evaluation-module.md:173:**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change.\ndocs/architecture/adr/001-evaluation-module.md:185:5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score.\ndocs/architecture/evaluation-table.md:51:| REQ-009 | C-001, C-002, C-003, C-004, M-001 | Correctness of the score; deterministic validation; failure isolation; offline testability; compatibility with the LangSmith benchmark entry |\ndocs/architecture/evaluation-table.md:58:| A | Harden `test/evaluators.py` in place and add a separate entry file | `test/evaluators.py`, `test/prompts.py`, a new entry script | Smallest file churn; baseline entry untouched; direct reuse of existing functions | Validation, judge construction, LangSmith serialisation and entry logic stay mixed; the import-time model side effect is harder to remove safely; no clean module boundary for pure tests | Low | Medium |\ndocs/architecture/evaluation-table.md:62:**Choice:** option B — it separates deterministic validation and the evaluation-only entry from the LangSmith adapter, keeps the baseline entry compatible, and allows every REQ-009 and REQ-010 case to run offline with an injected judge. It also places the module at the path assigned by `architecture-blueprint.md` §4.\n"
    }
  ]
}
```

### Event 418 — OpenCode (plan)

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff --check && echo \"diff-check: PASS\"; .venv/bin/python scripts/validate_requirements.py"
  },
  "output": [
    {
      "type": "text",
      "text": "diff-check: PASS\nPASS: 10 requirements valid\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "grep -n \"### evaluation\\|INV-006\\|INV-007\\|POL-00[2-8]\\|TC-EVAL-0\" docs/architecture/runtime-policy-catalog.md docs/architecture/invariants.md docs/code-governance/verification-constraints.md | tail -40"
  },
  "output": [
    {
      "type": "text",
      "text": "docs/architecture/runtime-policy-catalog.md:24:### evaluation (REQ-009, REQ-010, ADR-001)\ndocs/architecture/runtime-policy-catalog.md:28:| POL-002 | The evaluation entry receives a non-string, blank or whitespace-only question or report | Type and `str.strip()` checks on both required inputs before any judge call | Raise `EvaluationInputError`; the CLI writes `error: ...` to stderr and exits `2` | None; no evaluator or judge call | N/A (evaluation-only, not a research run) | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |\ndocs/architecture/runtime-policy-catalog.md:29:| POL-003 | A metric's optional input is absent or blank: reference answer, research brief or evidence | Presence and non-blank check before the metric's judge call | Mark only the dependent metric `not_evaluable`; evaluate the other metrics | None | N/A | REQ-009 C-003 / INV-006 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\ndocs/architecture/runtime-policy-catalog.md:30:| POL-004 | The judge returns a rating that is not a strict integer `1..5` | `type(value) is int` and range check; booleans, floats, strings, `None` and non-finite values are rejected | Mark that metric `not_evaluable` with `score=None` and `invalid_rating`; do not clamp or default | None; the metric is not retried into a score | N/A | REQ-009 C-002, M-001 / INV-006 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\ndocs/architecture/runtime-policy-catalog.md:31:| POL-005 | The judge extracts no claim for groundedness | Non-empty list check before the ratio | Mark groundedness `not_evaluable` with `score=None` and `no_claims` | None | N/A | REQ-009 C-004 / INV-006 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\ndocs/architecture/runtime-policy-catalog.md:32:| POL-006 | A judge call or evaluator raises an exception | `try/except Exception` around each metric group | Mark only that group's metrics `not_evaluable` with `evaluator_error`; continue the other groups | No module-level retry; provider retries are outside this policy | N/A | REQ-009 C-004 / INV-006 | `test/offline/test_evaluator_validity.py::test_one_metric_error_does_not_abort_others` |\ndocs/architecture/runtime-policy-catalog.md:33:| POL-007 | The CLI receives an argument or report-file error | Argument parsing and file read before evaluation | Write `error: ...` to stderr; no evaluator runs; exit `2` | None | N/A | REQ-010 C-002 / INV-007 | `test/offline/test_report_evaluation_entry.py::test_cli_blank_input_exit_code` |\ndocs/architecture/runtime-policy-catalog.md:34:| POL-008 | A CLI evaluation completes with every metric `not_evaluable` | Scan the returned metric statuses | Print the JSON result on stdout, notify on stderr and exit `1`; exit `0` when at least one metric is `scored` | None | N/A | REQ-009 / REQ-010 | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |\ndocs/architecture/invariants.md:69:## INV-006 — Every metric result is valid or explicitly not evaluable\ndocs/architecture/invariants.md:79:## INV-007 — Evaluation-only entry does not perform research or search\ndocs/code-governance/verification-constraints.md:81:### evaluation (REQ-009, REQ-010, ADR-001)\ndocs/code-governance/verification-constraints.md:85:| TC-EVAL-001 | REQ-009 C-001 | normal | Distinct question, report, reference-answer, research-brief and evidence markers; a fake judge that records requests | Every metric's judge request contains its declared inputs unchanged; correctness receives question, report and reference answer; completeness receives the brief; groundedness receives the evidence | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |\ndocs/code-governance/verification-constraints.md:86:| TC-EVAL-002 | REQ-009 C-002 / INV-006 | boundary | Ratings `1` and `5` | Scores `0.2` and `1.0`, status `scored` | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\ndocs/code-governance/verification-constraints.md:87:| TC-EVAL-003 | REQ-009 C-002 / INV-006 | exception | Ratings `0`, `6`, `True`, `\"4\"`, `4.5`, `NaN`, `inf`, `None` | `not_evaluable`, `score=None`, reason code `invalid_rating`; no clamping or default | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\ndocs/code-governance/verification-constraints.md:88:| TC-EVAL-004 | REQ-009 C-003 / INV-006 | exception | Missing reference answer, research brief and evidence, one at a time | Correctness, completeness or groundedness respectively is `not_evaluable`; the other metrics are still `scored` | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\ndocs/code-governance/verification-constraints.md:89:| TC-EVAL-005 | REQ-009 C-004 / INV-006 | boundary | Judge returns an empty claim list | Groundedness is `not_evaluable` with `score=None`; no `ZeroDivisionError` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\ndocs/code-governance/verification-constraints.md:90:| TC-EVAL-006 | REQ-009 C-004 | normal | Four claims, two grounded | Groundedness score `0.5` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\ndocs/code-governance/verification-constraints.md:91:| TC-EVAL-007 | REQ-009 C-004 / INV-006 | exception | One evaluator or judge call raises | Only that group's metrics are `not_evaluable`; the remaining metrics are still evaluated | `test/offline/test_evaluator_validity.py::test_one_metric_error_does_not_abort_others` |\ndocs/code-governance/verification-constraints.md:92:| TC-EVAL-008 | REQ-009 M-001 / INV-006 | boundary | Sweep of valid and invalid ratings across every metric | `out_of_range_score_count == 0`; every `scored` result is in `[0, 1]`; every invalid result has a null score | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\ndocs/code-governance/verification-constraints.md:93:| TC-EVAL-009 | INV-006 | regression | Import `test.evaluators` with no API key and no network; call each adapter with a fake judge | Import has no model-client or network side effect; baseline `key`/return shapes hold; `not_evaluable` maps to null `score`, `value=\"not_evaluable\"` and status metadata | `test/offline/test_evaluator_validity.py::test_adapter_contract_and_import_is_side_effect_free` |\ndocs/code-governance/verification-constraints.md:94:| TC-EVAL-010 | REQ-010 C-001 / INV-007 | normal | A supplied report and question with markers; research-graph and search entry points patched to fail if called | Judge requests contain the supplied text unchanged; graph and search call counts are zero; `report_id` is the report SHA-256 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research` |\ndocs/code-governance/verification-constraints.md:95:| TC-EVAL-011 | INV-007 | regression | Import the entry in a subprocess with no research modules preloaded | `open_deep_research.deep_researcher` is absent from `sys.modules` | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |\ndocs/code-governance/verification-constraints.md:96:| TC-EVAL-012 | REQ-010 C-002 / INV-007 | exception | Empty, whitespace-only and `None` question or report | `EvaluationInputError`; fake judge call count is zero | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |\ndocs/code-governance/verification-constraints.md:97:| TC-EVAL-013 | REQ-010 C-001 | boundary | Same report submitted twice, and a report differing by one character | `report_id` is stable for the same text and differs for the changed text; it equals the lowercase SHA-256 of the UTF-8 report | `test/offline/test_report_evaluation_entry.py::test_entry_identifies_report` |\ndocs/code-governance/verification-constraints.md:98:| TC-EVAL-014 | REQ-010 C-003 | human | Reviewer follows the README to evaluate a report file and read the per-metric results | The procedure works without modifying source code; verdict recorded as `REVIEW-NNN` | `docs/review-memo.md` (report evaluation entry review) |\ndocs/code-governance/verification-constraints.md:99:| TC-EVAL-015 | REQ-010 C-002 / INV-007 / POL-007 | exception | CLI with a blank question or a missing report file | stderr contains `error: ...`; exit code `2`; no judge call | `test/offline/test_report_evaluation_entry.py::test_cli_blank_input_exit_code` |\ndocs/code-governance/verification-constraints.md:100:| TC-EVAL-016 | POL-008 | boundary | CLI completes with all metrics `not_evaluable`; CLI completes with at least one `scored` metric | Exit code `1` and JSON on stdout in the first case; exit code `0` and JSON in the second | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |\n"
    }
  ]
}
```

### Event 431 — OpenCode (plan)

当前仍是 **Plan mode（只读）**，因此本轮已完成只读核对，但**未修改仓库文件**。下面给出核对结论、需要修订的精确位置、最终差异摘要和待评审问题；切换到可写角色后可直接应用。

## 1. 对照检查结论

| 检查项 | 结果 | 说明 |
|---|---|---|
| ADR 九节完整性 | **PASS** | `ADR-001` 含 §1—§9，状态 `Proposed`，`SA-NNN` 未伪造 |
| EVAL 模板字段 | **PASS** | Module、Owner、Decision、Status、ASR、Candidates、Choice、Rejected 齐全 |
| 编号唯一性 | **PASS** | `EVAL-001`、`ADR-001`、`INV-006/007`、`POL-002—008`、`TC-EVAL-001—016` 无冲突 |
| 交叉引用 | **基本 PASS** | ADR/EVAL/INV/POL/TC 互相引用可解析；唯一问题是 `structural-constraints.md` §1 与 `test/evaluation/` 路径冲突，见第 3 节 |
| 验收项覆盖 | **PASS** | REQ-009 C-001—C-004/M-001、REQ-010 C-001—C-003 均有对应用例；C-003 保持人工检查 |
| 接口一致性 | **需修订** | “评分原始类型必须在 Pydantic 转换前校验”尚未写成强制约束；当前 `validate_rating(value)` 可能拿到已被 Pydantic 宽松转换的 `int` |
| LangSmith 验证区分 | **需修订** | 只写了类型兼容结论，未明确区分 SDK 类型检查与实际线上验证 |
| AI 日志措辞 | **需修订** | 现有建议条目含“will review the ADR”等未来动作，不应写成已评审 |

## 2. 必须修订项

### 2.1 评分原始类型必须在 Pydantic 转换前校验

理由：如果 judge 响应 schema 把评分声明为 `int`，Pydantic 默认 lax 模式会把 `4.0`、`"4"` 转成 `4`，后续 `type(value) is int` 会误判为合法。架构上必须让验证函数看到**原始值**。

**建议修改 ADR §3.5 第一段为：**

> The raw judge rating must be validated before any Pydantic or other type conversion. The judge response schema therefore keeps rating fields as raw values (`Any`, or the raw structured tool-call arguments); it must not declare them as `int`, because Pydantic's default lax mode would coerce `4.0` and `"4"` to `4` and hide an invalid rating. `validation.validate_rating(raw_value)` performs the first check: `type(raw_value) is int` and `1 <= raw_value <= 5`. Booleans, floats including `4.0`, strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `value / 5`. An invalid rating produces `status="not_evaluable"`, `score=None` and `reason_code="invalid_rating"`. Scores are never clamped, rounded, defaulted or replaced by zero.

**同步修改：**

- ADR §3.7：`Judge.invoke(...)` 返回原始结构化字段值，评分在构造 `MetricResult` 前经过 `validate_rating`。
- ADR §5：`validation.py` 的 `validate_rating(raw_value) -> float` 明确为“对原始值校验，非法时抛 `InvalidRating`”；`judge.py` 的接口改为返回原始 mapping。
- ADR §9 第 4、5 步：增加“不得把评分字段声明为 `int`；先校验原始值，再构造 `MetricResult`”。
- `INV-006` 的 Statement 增加“on the raw judge value before any Pydantic/type conversion”。
- `POL-004` 的 Detection 增加“raw value before Pydantic conversion；`4.0` 必须拒绝”。
- `verification-constraints.md` 的 `TC-EVAL-003` 输入加入 `4.0`，并补一句：

> `TC-EVAL-003` deliberately includes `4.0` and `"4"`: a lax `int` schema would coerce both to `4`; the test must observe `not_evaluable` with `invalid_rating`.

### 2.2 `structural-constraints.md` §1 与 `test/evaluation/` 路径冲突列为待评审问题

当前 ADR §2 写成“已通过……解决”，但 §1 明确写顶层 `test/` “No”。应改为显式待确认，不静默解决。

**建议：**

- ADR §2 将该句改为：

> The blueprint assigns this module to `test/evaluation/`, but `structural-constraints.md` §1 lists top-level `test/` as “No” for new work. This conflict is recorded as a module-review question in §10 and must be confirmed before SA acceptance; it is not silently resolved here.

- `structural-constraints.md` §10 表格后增加：

> **Module-review question:** §1 lists top-level `test/` as “No” for new work; blueprint §4 assigns this module to `test/evaluation/`. Confirm this exception at module review/integration; §1 is human-owned and is not edited here.

- ADR §8 增加一段 **Open for module review**，复述该问题。
- `EVAL-001` 末尾可加一行 **Open for module review**，保证 ADD 记录也可见。

### 2.3 区分 LangSmith 类型兼容与线上验证

**建议在 ADR §7 表格后增加：**

> **Verification basis and status.** LangSmith compatibility was checked on 2026-11-13 against the installed `langsmith 0.9.2` source (`EvaluationResult.score` accepts `None`) and the official evaluator-output/feedback documentation. This is a type-contract check only; no live `aevaluate`, experiment run or UI check was performed. The live check and all behavioural tests remain `NOT_RUN`; SA Review and Gate 2 are also not performed.

**建议在 `verification-constraints.md` §7 的 “Live or human checks” 增加：**

> **LangSmith live compatibility:** `NOT_RUN`; only the SDK type contract was checked against `langsmith 0.9.2` and the official docs. A live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation.

### 2.4 AI 日志建议条目只保留真实人工决定

现有条目不应写“reviewed / will review the ADR”。建议改为：

```yaml
- id: AIU-NNN
  date: "2026-11-13"
  member: DopplerXD
  purpose: >-
    Draft and write the Phase 1 SA documents for the evaluation module for REQ-009 and REQ-010,
    under a temporary Build-role exception limited to documentation.
  prompt: >-
    Follow AGENTS.md reading order and Prompt.md Phase 1. For REQ-009/REQ-010 (evaluation,
    test/evaluation/), verify role/branch/permissions; analyse test/evaluators.py,
    test/prompts.py and test/run_evaluate.py; map C-001—C-004/M-001 and C-001—C-003; compare
    three ADD candidates; write a Proposed ADR with nine sections; add the evaluation module
    sections to invariants, runtime policies, trace matrix, structural constraints §10 and
    verification constraints §7. Use option B, strict integer ratings validated before
    Pydantic conversion, not_evaluable with null score, SHA-256 report identity and CLI exit
    codes 0/1/2. Do not modify source, tests, dependency configuration, permissions or approvals.
  requirements: [REQ-009, REQ-010]
  artifacts:
    - docs/architecture/evaluation-table.md
    - docs/architecture/adr/001-evaluation-module.md
    - docs/architecture/invariants.md
    - docs/architecture/runtime-policy-catalog.md
    - docs/architecture/trace-matrix.md
    - docs/code-governance/structural-constraints.md
    - docs/code-governance/verification-constraints.md
  supervision: >-
    The member confirmed option B and decisions 1/2/3 (packaging, CLI exit codes,
    INV-007/POL numbering) and requested the pre-Pydantic rating rule and the separation of
    type-level compatibility from live verification. SA Review, test approval and live
    LangSmith verification have not occurred.
  transcript: null
```

## 3. 最终差异摘要

当前实际差异（本轮未新增修改）：

| 文件 | 状态 | 行数 |
|---|---|---|
| `docs/architecture/evaluation-table.md` | 修改 | +28 |
| `docs/architecture/adr/001-evaluation-module.md` | 新建 | 192 |
| `docs/architecture/invariants.md` | 修改 | +20 |
| `docs/architecture/runtime-policy-catalog.md` | 修改 | +12 |
| `docs/architecture/trace-matrix.md` | 修改 | +2/−2 |
| `docs/code-governance/structural-constraints.md` | 修改 | +15 |
| `docs/code-governance/verification-constraints.md` | 修改 | +24 |

待应用修订涉及：ADR §2、§3.5、§3.7、§5、§7、§8、§9；`INV-006`；`POL-004`；`TC-EVAL-003` 与 §7 live bullet；`structural §10`；`EVAL-001` 的 open-review 行。预计新增约 20—30 行、修改若干句，不改变现有编号。

## 4. 待模块评审确认的问题

1. **路径冲突**：`structural-constraints.md` §1 的顶层 `test/` “No” 与蓝图 §4 的 `test/evaluation/` 不一致；需模块评审确认例外，§1 由人类维护，本模块不修改。
2. **原始评分值获取方式**：建议采用“judge 响应保留原始值 + `validate_rating` 手动校验”，而不是依赖 Pydantic 的 `int`/`StrictInt`。需确认该接口选择。
3. **LangSmith 线上行为**：`score=None` 在 SDK 类型层合法，但线上 `aevaluate`/UI 是否接受并正确展示 `not_evaluable` 尚未验证，保持 `NOT_RUN`。
4. **POL 编号**：`POL-002—008` 为模块临时编号，集成时可能统一重编号。
5. **SA Review / Gate 1、测试批准 / Gate 2、实现步骤**均未执行；ADR 仍为 `Proposed`。
6. **`test/run_evaluate.py` 导入副作用**：`load_dotenv("../.env")`、`Client()` 仍在基线入口；本轮按兼容要求未改动，是否需要后续单列技术债待确认。

## 5. 检查结果

| 检查 | 结果 |
|---|---|
| `git diff --check` | **PASS** |
| `.venv/bin/python scripts/validate_requirements.py` | **PASS**：`10 requirements valid` |
| 改动范围 | **PASS**：仅 7 个 evaluation SA 文档；无源码、测试、依赖、权限、审批改动 |
| SA Review / Gate 1 | **NOT_RUN** |
| 测试基线 / Gate 2 | **NOT_RUN** |
| LangSmith 线上验证 | **NOT_RUN**（仅完成 SDK 类型层检查） |
| 提交 / 推送 | **N/A**：未执行 |

若要应用上述修订，请切换到可写角色；当前我无法在 Plan mode 修改仓库文档。

### Event 440 — agent-switched

```json
{
  "time": {
    "created": 1794583352216
  },
  "agent": "build",
  "previous": "plan"
}
```

### Event 445 — User

应用上述修订

> **H-06 Apply the revisions**
> 授权应用上一轮已列出的文档修订，继续保持 SA 阶段。

### Event 446 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "grep -n \"The blueprint\\|A judge rating\\|Judge is a protocol\\|validate_rating\\|Invoke\\|Live or human checks\\|The decision, interfaces\" docs/architecture/adr/001-evaluation-module.md docs/architecture/invariants.md docs/architecture/runtime-policy-catalog.md docs/code-governance/verification-constraints.md docs/code-governance/structural-constraints.md docs/architecture/evaluation-table.md"
  },
  "output": [
    {
      "type": "text",
      "text": "docs/architecture/adr/001-evaluation-module.md:28:The blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. Offline tests must run without network access, API keys or model calls (`verification-constraints.md` §3), and the baseline LangSmith entry must keep working because it is the benchmark path. The structural constraint that `test/` holds baseline scripts is addressed by keeping evaluation logic in `test/evaluation/` and leaving `test/run_evaluate.py` unchanged; `test/evaluators.py` becomes a thin compatibility adapter.\ndocs/architecture/adr/001-evaluation-module.md:71:A judge rating is accepted only when `type(value) is int` and `1 <= value <= 5`. Booleans, floats (including `4.0`), strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and a reason code such as `invalid_rating`. Scores are never clamped, rounded, defaulted or replaced by zero.\ndocs/architecture/adr/001-evaluation-module.md:135:| `test/evaluation/validation.py` | Deterministic rating, claim-ratio and input checks | `validate_rating(value) -> float`, `groundedness_ratio(claims) -> float`, `require_text(value) -> bool` | `metrics.py`, `entry.py` |\ndocs/code-governance/verification-constraints.md:79:- **Live or human checks:** cases marked `automated: false` in `requirements.yaml`, and where their evidence goes.\ndocs/code-governance/verification-constraints.md:103:- **Live or human checks:** REQ-010 C-003 is the only `automated: false` criterion in this module; its evidence is the `REVIEW-NNN` record in `docs/review-memo.md`.\ndocs/architecture/evaluation-table.md:66:The decision, interfaces and implementation steps are in ADR-001.\n"
    }
  ]
}
```

### Event 455 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "grep -n \"Judge\\|metrics.py\\|Add `test/evaluation/judge\\|Add `test/evaluation/metrics\\|Open for module\\|Neutral\" docs/architecture/adr/001-evaluation-module.md | sed -n '1,80p'"
  },
  "output": [
    {
      "type": "text",
      "text": "zsh:1: no such file or directory: test/evaluation/judge|Add\n41:  judge.py              # Judge protocol and lazy default judge\n42:  metrics.py            # metric groups, normalisation, per-group failure isolation\n88:`Judge` is a protocol with an `invoke(messages, schema)` method. `default_judge()` constructs the baseline judge model lazily on first use; it is injectable for offline tests. Importing `test.evaluation` or `test.evaluators` must not construct a model client or read an API key.\n135:| `test/evaluation/validation.py` | Deterministic rating, claim-ratio and input checks | `validate_rating(value) -> float`, `groundedness_ratio(claims) -> float`, `require_text(value) -> bool` | `metrics.py`, `entry.py` |\n136:| `test/evaluation/judge.py` | Judge boundary; lazy model construction | `Judge.invoke(messages, schema)`, `default_judge() -> Judge` | `metrics.py`, `entry.py` |\n137:| `test/evaluation/metrics.py` | Run metric groups, normalise and isolate failures | `evaluate_metrics(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> tuple[MetricResult, ...]` | `entry.py`, `test/evaluators.py` |\n141:| `test/prompts.py` | Judge templates | `CORRECTNESS_PROMPT` gains `{user_question}`, `{report}`, `{answer}` and `{today}` placeholders | `metrics.py` |\n175:**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.\n184:4. Add `test/evaluation/judge.py`: the `Judge` protocol and a `default_judge()` that constructs the baseline `ChatOpenAI` only when called. No model construction at import.\n185:5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score.\n"
    }
  ]
}
```

### Event 464 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "The blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. Offline tests must run without network access, API keys or model calls (`verification-constraints.md` §3), and the baseline LangSmith entry must keep working because it is the benchmark path. The structural constraint that `test/` holds baseline scripts is addressed by keeping evaluation logic in `test/evaluation/` and leaving `test/run_evaluate.py` unchanged; `test/evaluators.py` becomes a thin compatibility adapter.",
    "newString": "The blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. This conflicts with `structural-constraints.md` §1, which lists top-level `test/` as “No” for new work; the conflict is recorded as a module-review question in §10 and must be confirmed before SA acceptance, not silently resolved here. Offline tests must run without network access, API keys or model calls (`verification-constraints.md` §3), and the baseline LangSmith entry must keep working because it is the benchmark path. The design keeps evaluation logic in `test/evaluation/` and leaves `test/run_evaluate.py` unchanged; `test/evaluators.py` becomes a thin compatibility adapter."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 473 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "A judge rating is accepted only when `type(value) is int` and `1 <= value <= 5`. Booleans, floats (including `4.0`), strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and a reason code such as `invalid_rating`. Scores are never clamped, rounded, defaulted or replaced by zero.",
    "newString": "The raw judge rating must be validated before any Pydantic or other type conversion. The judge response schema therefore keeps rating fields as raw values (`Any`, or the raw structured tool-call arguments); it must not declare them as `int`, because Pydantic's default lax mode would coerce `4.0` and `\"4\"` to `4` and hide an invalid rating. `validation.validate_rating(raw_value)` performs the first check: `type(raw_value) is int` and `1 <= raw_value <= 5`. Booleans, floats including `4.0`, strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and `reason_code=\"invalid_rating\"`. Scores are never clamped, rounded, defaulted or replaced by zero."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 480 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "`Judge` is a protocol with an `invoke(messages, schema)` method. `default_judge()` constructs the baseline judge model lazily on first use; it is injectable for offline tests. Importing `test.evaluation` or `test.evaluators` must not construct a model client or read an API key.",
    "newString": "`Judge` is a protocol with `invoke(messages, schema) -> Mapping[str, object]`, returning the raw structured field values so rating values reach `validation.py` before any typed conversion. `default_judge()` constructs the baseline judge model lazily on first use; it is injectable for offline tests. Importing `test.evaluation` or `test.evaluators` must not construct a model client or read an API key."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 487 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "| `test/evaluation/validation.py` | Deterministic rating, claim-ratio and input checks | `validate_rating(value) -> float`, `groundedness_ratio(claims) -> float`, `require_text(value) -> bool` | `metrics.py`, `entry.py` |\n| `test/evaluation/judge.py` | Judge boundary; lazy model construction | `Judge.invoke(messages, schema)`, `default_judge() -> Judge` | `metrics.py`, `entry.py` |",
    "newString": "| `test/evaluation/validation.py` | Deterministic rating, claim-ratio and input checks | `validate_rating(raw_value) -> float` (raises `InvalidRating`), `groundedness_ratio(claims) -> float` (raises `NoClaims`/`InvalidClaim`), `require_text(value) -> bool` | `metrics.py`, `entry.py` |\n| `test/evaluation/judge.py` | Judge boundary; lazy model construction and raw structured output | `Judge.invoke(messages, schema) -> Mapping[str, object]`, `default_judge() -> Judge` | `metrics.py`, `entry.py` |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 494 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "The module's complete case list, including normal, exception, boundary and regression cases, is in `verification-constraints.md` §7.",
    "newString": "**Verification basis and status.** LangSmith compatibility was checked on 2026-11-13 against the installed `langsmith 0.9.2` source (`EvaluationResult.score` accepts `None`) and the official evaluator-output and feedback documentation. This is a type-contract check only; no live `aevaluate` call, experiment run or UI check was performed. The live check and all behavioural tests remain `NOT_RUN`; SA Review and Gate 2 are also not performed.\n\nThe module's complete case list, including normal, exception, boundary and regression cases, is in `verification-constraints.md` §7."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 503 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.",
    "newString": "**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.\n\n**Open for module review.** `structural-constraints.md` §1 lists top-level `test/` as “No” for new work, while `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm the exception at module review and integration; §1 is human-owned and is not edited by this ADR."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 512 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "4. Add `test/evaluation/judge.py`: the `Judge` protocol and a `default_judge()` that constructs the baseline `ChatOpenAI` only when called. No model construction at import.\n5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score.",
    "newString": "4. Add `test/evaluation/judge.py`: the `Judge` protocol that returns raw structured field values, and a `default_judge()` that constructs the baseline `ChatOpenAI` only when called. Do not declare rating fields as `int`; no model construction at import.\n5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Call `validate_rating` on the raw judge value before constructing a `MetricResult`, and map `InvalidRating` to `not_evaluable` with `invalid_rating`. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 521 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/invariants.md",
    "oldString": "- **Statement:** Every metric result is either `scored` with a score in `[0, 1]` derived from a strict integer judge rating `1..5` or, for groundedness only, from a ratio over at least one extracted claim, or it is `not_evaluable` with a null score and a reason. An invalid rating, missing input, empty claim list or evaluator exception makes only the affected metric `not_evaluable`; it never produces a fabricated score and never aborts the remaining metrics.",
    "newString": "- **Statement:** Every metric result is either `scored` with a score in `[0, 1]` derived from a strict integer judge rating `1..5`, validated on the raw judge value before any Pydantic or other type conversion, or, for groundedness only, from a ratio over at least one extracted claim, or it is `not_evaluable` with a null score and a reason. An invalid rating, missing input, empty claim list or evaluator exception makes only the affected metric `not_evaluable`; it never produces a fabricated score and never aborts the remaining metrics."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/invariants.md (1 replacement)"
    }
  ]
}
```

### Event 530 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/runtime-policy-catalog.md",
    "oldString": "| POL-004 | The judge returns a rating that is not a strict integer `1..5` | `type(value) is int` and range check; booleans, floats, strings, `None` and non-finite values are rejected | Mark that metric `not_evaluable` with `score=None` and `invalid_rating`; do not clamp or default | None; the metric is not retried into a score | N/A | REQ-009 C-002, M-001 / INV-006 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |",
    "newString": "| POL-004 | The judge returns a rating that is not a strict integer `1..5` | `type(raw_value) is int` and range check on the raw value before Pydantic or other type conversion; booleans, floats including `4.0`, strings, `None` and non-finite values are rejected | Mark that metric `not_evaluable` with `score=None` and `invalid_rating`; do not clamp or default | None; the metric is not retried into a score | N/A | REQ-009 C-002, M-001 / INV-006 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/runtime-policy-catalog.md (1 replacement)"
    }
  ]
}
```

### Event 539 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "| TC-EVAL-003 | REQ-009 C-002 / INV-006 | exception | Ratings `0`, `6`, `True`, `\"4\"`, `4.5`, `NaN`, `inf`, `None` | `not_evaluable`, `score=None`, reason code `invalid_rating`; no clamping or default | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |",
    "newString": "| TC-EVAL-003 | REQ-009 C-002 / INV-006 | exception | Ratings `0`, `6`, `True`, `\"4\"`, `4.0`, `4.5`, `NaN`, `inf`, `None` | `not_evaluable`, `score=None`, reason code `invalid_rating`; no clamping or default | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "- **Regression:** re-run `uv run pytest test/offline`; the adapter contract in `test/offline/test_evaluator_validity.py`; and the import surface of `test/run_evaluate.py` (the six evaluator names and their call signatures must remain available). No live model or network call is needed for any case above.\n- **Live or human checks:** REQ-010 C-003 is the only `automated: false` criterion in this module; its evidence is the `REVIEW-NNN` record in `docs/review-memo.md`.",
    "newString": "- **Regression:** re-run `uv run pytest test/offline`; the adapter contract in `test/offline/test_evaluator_validity.py`; and the import surface of `test/run_evaluate.py` (the six evaluator names and their call signatures must remain available). No live model or network call is needed for any case above.\n- **Live or human checks:** REQ-010 C-003 is the only `automated: false` criterion in this module; its evidence is the `REVIEW-NNN` record in `docs/review-memo.md`.\n- **LangSmith live compatibility:** `NOT_RUN`; only the SDK type contract was checked against `langsmith 0.9.2` and the official docs. A live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation. `TC-EVAL-003` deliberately includes `4.0` and `\"4\"`: a lax `int` schema would coerce both to `4`; the test must observe `not_evaluable` with `invalid_rating`."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

### Event 552 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "- **LangSmith live compatibility:** `NOT_RUN`; only the SDK type contract was checked against `langsmith 0.9.2` and the official docs. A live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation. `TC-EVAL-003` deliberately includes `4.0` and `\"4\"`: a lax `int` schema would coerce both to `4`; the test must observe `not_evaluable` with `invalid_rating`.",
    "newString": "- **LangSmith live compatibility:** `NOT_RUN`; only the SDK type contract was checked against `langsmith 0.9.2` and the official docs. A live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation.\n- **Raw-rating test note:** `TC-EVAL-003` deliberately includes `4.0` and `\"4\"`: a lax `int` schema would coerce both to `4`; the test must observe `not_evaluable` with `invalid_rating`."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

### Event 561 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/structural-constraints.md",
    "oldString": "`test/evaluators.py` is a thin compatibility adapter; evaluation logic lives only in `test/evaluation/`.",
    "newString": "`test/evaluators.py` is a thin compatibility adapter; evaluation logic lives only in `test/evaluation/`.\n\n**Module-review question:** §1 lists top-level `test/` as “No” for new work; `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm this exception at module review and integration; §1 is human-owned and is not edited here."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/structural-constraints.md (1 replacement)"
    }
  ]
}
```

### Event 570 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/evaluation-table.md",
    "oldString": "The decision, interfaces and implementation steps are in ADR-001.",
    "newString": "The decision, interfaces and implementation steps are in ADR-001.\n\n**Open for module review:** `structural-constraints.md` §1 lists top-level `test/` as not for new work, while `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm the exception at module review and integration."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/evaluation-table.md (1 replacement)"
    }
  ]
}
```

### Event 579 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "sed -n '64,95p' docs/architecture/adr/001-evaluation-module.md; echo \"=====7/8=====\"; sed -n '150,190p' docs/architecture/adr/001-evaluation-module.md"
  },
  "output": [
    {
      "type": "text",
      "text": "- Research brief: completeness only.\n- Evidence (`raw_notes` equivalent): groundedness only.\n\nIf an optional input is missing or blank, only the metrics that require it become `not_evaluable`; the other metrics are still evaluated. If the question or report is missing in the LangSmith adapter, every metric that needs it becomes `not_evaluable` and the adapter does not raise.\n\n### 3.5 Strict rating validation\n\nThe raw judge rating must be validated before any Pydantic or other type conversion. The judge response schema therefore keeps rating fields as raw values (`Any`, or the raw structured tool-call arguments); it must not declare them as `int`, because Pydantic's default lax mode would coerce `4.0` and `\"4\"` to `4` and hide an invalid rating. `validation.validate_rating(raw_value)` performs the first check: `type(raw_value) is int` and `1 <= raw_value <= 5`. Booleans, floats including `4.0`, strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and `reason_code=\"invalid_rating\"`. Scores are never clamped, rounded, defaulted or replaced by zero.\n\nGroundedness is the only ratio metric: the judge's claims must be a non-empty list; the score is `grounded_count / total_claims`; an empty list produces `status=\"not_evaluable\"` with reason code `no_claims`. A claim whose `grounded` field is not a boolean makes the metric `not_evaluable` rather than being coerced.\n\n### 3.6 Failure isolation\n\nMetric groups are evaluated independently. A group is one judge call and the metrics it produces: overall quality produces six metrics from one call; each other evaluator produces one metric from one call. An exception in a group makes only that group's metrics `not_evaluable` with a reason code such as `evaluator_error`; the remaining groups still run. The implementation catches `Exception`, never `BaseException`, so interruption and process exit are not swallowed.\n\n### 3.7 Evaluation-only entry\n\n`evaluate_existing_report(question, report, *, reference_answer=None, research_brief=None, evidence=None, judge=None) -> EvaluationResult`:\n\n1. Rejects a non-string, blank or whitespace-only `question` or `report` with `EvaluationInputError` before any judge call.\n2. Computes `report_id` as the SHA-256 of the supplied report text; the report text is passed to the judge unchanged.\n3. Runs the metric groups against the supplied inputs.\n4. Returns `EvaluationResult`; it never compiles or invokes the research graph, imports `open_deep_research.deep_researcher`, calls a search provider or generates a replacement report.\n\n`Judge` is a protocol with `invoke(messages, schema) -> Mapping[str, object]`, returning the raw structured field values so rating values reach `validation.py` before any typed conversion. `default_judge()` constructs the baseline judge model lazily on first use; it is injectable for offline tests. Importing `test.evaluation` or `test.evaluators` must not construct a model client or read an API key.\n\n### 3.8 CLI\n\n`python -m test.evaluation.evaluate_report --report <path> --question <text>` accepts optional `--reference-answer`, `--research-brief` and `--evidence`. It prints the result as JSON on stdout. Exit codes are:\n\n| Code | Meaning |\n|---|---|\n=====7/8=====\n- **Deterministic boundary:** the model supplies ratings and claim judgements only. Deterministic code decides whether the rating is a valid integer `1..5`, whether the normalised score is in `[0, 1]`, whether at least one claim exists, whether required inputs are present, whether a metric is `not_evaluable` and whether an exception stays local to its metric group.\n\n## 7. Verification\n\n| Requirement and criterion | Verification |\n|---|---|\n| REQ-009 C-001 | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |\n| REQ-009 C-002 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| REQ-009 C-003 | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\n| REQ-009 C-004 | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors`, `::test_one_metric_error_does_not_abort_others` |\n| REQ-009 M-001 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| INV-006 | `test/offline/test_evaluator_validity.py` (all cases; no out-of-range score, no score on `not_evaluable`) |\n| REQ-010 C-001 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research`, `::test_entry_identifies_report` |\n| REQ-010 C-002 | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected`, `::test_cli_blank_input_exit_code` |\n| REQ-010 C-003 | manual review recorded as `REVIEW-NNN` in `docs/review-memo.md` |\n| INV-007 | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |\n\n**Verification basis and status.** LangSmith compatibility was checked on 2026-11-13 against the installed `langsmith 0.9.2` source (`EvaluationResult.score` accepts `None`) and the official evaluator-output and feedback documentation. This is a type-contract check only; no live `aevaluate` call, experiment run or UI check was performed. The live check and all behavioural tests remain `NOT_RUN`; SA Review and Gate 2 are also not performed.\n\nThe module's complete case list, including normal, exception, boundary and regression cases, is in `verification-constraints.md` §7.\n\n## 8. Consequences\n\n**Positive.** Every metric either carries a defensible score in `[0, 1]` or an explicit `not_evaluable` result with a reason. Correctness receives the question, report and reference answer. A single broken metric no longer hides the others or crashes a run. Existing reports can be scored without spending research tokens or calling search. Offline tests can inject a fake judge and run without network or keys. The benchmark entry keeps its evaluator names and return shapes.\n\n**Negative.** A new package and adapter add a small amount of indirection. `not_evaluable` metrics have no numeric score, so they do not contribute to LangSmith numeric averages; the status is carried in `value`, `metadata` and the comment instead. The adapter must keep the baseline key list in sync when metrics are added. `CORRECTNESS_PROMPT` changes, so prompt text is part of the diff even though the rubric wording does not change.\n\n**Neutral.** No graph node, edge, state field or research module changes. `test/run_evaluate.py` is unchanged. The evaluation remains an LLM-judge evaluation: this ADR makes the scores valid and bounded, not necessarily correct in an absolute sense. `test/pairwise_evaluation.py`, `test/supervisor_parallel_evaluation.py` and `test/extract_langsmith_data.py` are outside this decision.\n\n**Open for module review.** `structural-constraints.md` §1 lists top-level `test/` as “No” for new work, while `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm the exception at module review and integration; §1 is human-owned and is not edited by this ADR.\n\n## 9. Implementation Steps\n\nTests for §7 are written by the Test Author after Gate 1; the steps below are the Build work that follows Gate 2.\n\n1. Create `test/evaluation/__init__.py` and export the public types and `evaluate_existing_report`.\n2. Add `test/evaluation/types.py`: `MetricStatus`, `MetricResult`, `EvaluationResult` and `EvaluationInputError`, with the score/status invariant.\n3. Add `test/evaluation/validation.py`: strict `1..5` integer validation, `value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats, strings, `None` and non-finite values.\n4. Add `test/evaluation/judge.py`: the `Judge` protocol that returns raw structured field values, and a `default_judge()` that constructs the baseline `ChatOpenAI` only when called. Do not declare rating fields as `int`; no model construction at import.\n5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Call `validate_rating` on the raw judge value before constructing a `MetricResult`, and map `InvalidRating` to `not_evaluable` with `invalid_rating`. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score.\n6. Add `test/evaluation/entry.py`: `evaluate_existing_report`, blank-input rejection before the judge, SHA-256 `report_id`, and the no-research/no-search import boundary.\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "sed -n '80,112p' docs/code-governance/verification-constraints.md; echo \"=====STRUCT=====\"; tail -8 docs/code-governance/structural-constraints.md; echo \"=====INV=====\"; sed -n '69,76p' docs/architecture/invariants.md"
  },
  "output": [
    {
      "type": "text",
      "text": "\n### evaluation (REQ-009, REQ-010, ADR-001)\n\n| Case | Covers | Type | Input | Expected result | Test |\n|---|---|---|---|---|---|\n| TC-EVAL-001 | REQ-009 C-001 | normal | Distinct question, report, reference-answer, research-brief and evidence markers; a fake judge that records requests | Every metric's judge request contains its declared inputs unchanged; correctness receives question, report and reference answer; completeness receives the brief; groundedness receives the evidence | `test/offline/test_evaluator_validity.py::test_evaluators_receive_their_inputs` |\n| TC-EVAL-002 | REQ-009 C-002 / INV-006 | boundary | Ratings `1` and `5` | Scores `0.2` and `1.0`, status `scored` | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| TC-EVAL-003 | REQ-009 C-002 / INV-006 | exception | Ratings `0`, `6`, `True`, `\"4\"`, `4.0`, `4.5`, `NaN`, `inf`, `None` | `not_evaluable`, `score=None`, reason code `invalid_rating`; no clamping or default | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| TC-EVAL-004 | REQ-009 C-003 / INV-006 | exception | Missing reference answer, research brief and evidence, one at a time | Correctness, completeness or groundedness respectively is `not_evaluable`; the other metrics are still `scored` | `test/offline/test_evaluator_validity.py::test_missing_input_is_not_evaluable` |\n| TC-EVAL-005 | REQ-009 C-004 / INV-006 | boundary | Judge returns an empty claim list | Groundedness is `not_evaluable` with `score=None`; no `ZeroDivisionError` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\n| TC-EVAL-006 | REQ-009 C-004 | normal | Four claims, two grounded | Groundedness score `0.5` | `test/offline/test_evaluator_validity.py::test_groundedness_and_errors` |\n| TC-EVAL-007 | REQ-009 C-004 / INV-006 | exception | One evaluator or judge call raises | Only that group's metrics are `not_evaluable`; the remaining metrics are still evaluated | `test/offline/test_evaluator_validity.py::test_one_metric_error_does_not_abort_others` |\n| TC-EVAL-008 | REQ-009 M-001 / INV-006 | boundary | Sweep of valid and invalid ratings across every metric | `out_of_range_score_count == 0`; every `scored` result is in `[0, 1]`; every invalid result has a null score | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\n| TC-EVAL-009 | INV-006 | regression | Import `test.evaluators` with no API key and no network; call each adapter with a fake judge | Import has no model-client or network side effect; baseline `key`/return shapes hold; `not_evaluable` maps to null `score`, `value=\"not_evaluable\"` and status metadata | `test/offline/test_evaluator_validity.py::test_adapter_contract_and_import_is_side_effect_free` |\n| TC-EVAL-010 | REQ-010 C-001 / INV-007 | normal | A supplied report and question with markers; research-graph and search entry points patched to fail if called | Judge requests contain the supplied text unchanged; graph and search call counts are zero; `report_id` is the report SHA-256 | `test/offline/test_report_evaluation_entry.py::test_entry_scores_supplied_report_without_research` |\n| TC-EVAL-011 | INV-007 | regression | Import the entry in a subprocess with no research modules preloaded | `open_deep_research.deep_researcher` is absent from `sys.modules` | `test/offline/test_report_evaluation_entry.py::test_entry_does_not_import_research_graph` |\n| TC-EVAL-012 | REQ-010 C-002 / INV-007 | exception | Empty, whitespace-only and `None` question or report | `EvaluationInputError`; fake judge call count is zero | `test/offline/test_report_evaluation_entry.py::test_blank_input_rejected` |\n| TC-EVAL-013 | REQ-010 C-001 | boundary | Same report submitted twice, and a report differing by one character | `report_id` is stable for the same text and differs for the changed text; it equals the lowercase SHA-256 of the UTF-8 report | `test/offline/test_report_evaluation_entry.py::test_entry_identifies_report` |\n| TC-EVAL-014 | REQ-010 C-003 | human | Reviewer follows the README to evaluate a report file and read the per-metric results | The procedure works without modifying source code; verdict recorded as `REVIEW-NNN` | `docs/review-memo.md` (report evaluation entry review) |\n| TC-EVAL-015 | REQ-010 C-002 / INV-007 / POL-007 | exception | CLI with a blank question or a missing report file | stderr contains `error: ...`; exit code `2`; no judge call | `test/offline/test_report_evaluation_entry.py::test_cli_blank_input_exit_code` |\n| TC-EVAL-016 | POL-008 | boundary | CLI completes with all metrics `not_evaluable`; CLI completes with at least one `scored` metric | Exit code `1` and JSON on stdout in the first case; exit code `0` and JSON in the second | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |\n\n- **Regression:** re-run `uv run pytest test/offline`; the adapter contract in `test/offline/test_evaluator_validity.py`; and the import surface of `test/run_evaluate.py` (the six evaluator names and their call signatures must remain available). No live model or network call is needed for any case above.\n- **Live or human checks:** REQ-010 C-003 is the only `automated: false` criterion in this module; its evidence is the `REVIEW-NNN` record in `docs/review-memo.md`.\n- **LangSmith live compatibility:** `NOT_RUN`; only the SDK type contract was checked against `langsmith 0.9.2` and the official docs. A live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation.\n- **Raw-rating test note:** `TC-EVAL-003` deliberately includes `4.0` and `\"4\"`: a lax `int` schema would coerce both to `4`; the test must observe `not_evaluable` with `invalid_rating`.\n\n## 8. Definition of Done\n\n| # | Condition | Done by |\n|---|---|---|\n| 1 | Every fit-criterion item has an approved test or recorded review, and the tests pass | Test Author (tests), Build (passing), confirmed by Verify |\n| 2 | All prior offline suites pass | Verify |\n=====STRUCT=====\n| May depend on | `test/prompts.py`, `open_deep_research.utils.get_today_str`, the Python standard library, and `pydantic`/`langchain_openai` only inside the lazy judge factory. |\n| Must not depend on | `open_deep_research.deep_researcher`, the research graph, search providers or search tools, `test.run_evaluate` import-time state, or any extension module. No model client is constructed at import. |\n| Shared contracts | None: no `state.py` type or graph state field is added. The baseline LangSmith evaluator names, keys and return shapes are preserved by `test/evaluators.py`. |\n| Configuration flag | None: the module is evaluation-only and adds no runtime behaviour flag. |\n\n`test/evaluators.py` is a thin compatibility adapter; evaluation logic lives only in `test/evaluation/`.\n\n**Module-review question:** §1 lists top-level `test/` as “No” for new work; `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm this exception at module review and integration; §1 is human-owned and is not edited here.\n=====INV=====\n## INV-006 — Every metric result is valid or explicitly not evaluable\n\n- **Statement:** Every metric result is either `scored` with a score in `[0, 1]` derived from a strict integer judge rating `1..5`, validated on the raw judge value before any Pydantic or other type conversion, or, for groundedness only, from a ratio over at least one extracted claim, or it is `not_evaluable` with a null score and a reason. An invalid rating, missing input, empty claim list or evaluator exception makes only the affected metric `not_evaluable`; it never produces a fabricated score and never aborts the remaining metrics.\n- **Module:** evaluation\n- **Source:** REQ-009\n- **Status:** Proposed\n- **Enforcing component:** `test/evaluation/validation.py`, `test/evaluation/metrics.py` and the compatibility adapter in `test/evaluators.py`.\n- **Verification:** `test/offline/test_evaluator_validity.py`; monitor `out_of_range_score_count == 0`.\n"
    }
  ]
}
```

### Event 592 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/invariants.md",
    "oldString": "- **Statement:** Every metric result is either `scored` with a score in `[0, 1]` derived from a strict integer judge rating `1..5`, validated on the raw judge value before any Pydantic or other type conversion, or, for groundedness only, from a ratio over at least one extracted claim, or it is `not_evaluable` with a null score and a reason. An invalid rating, missing input, empty claim list or evaluator exception makes only the affected metric `not_evaluable`; it never produces a fabricated score and never aborts the remaining metrics.",
    "newString": "- **Statement:** Every metric result is either `scored` with a score in `[0, 1]`, or `not_evaluable` with a null score and a reason. A `scored` result comes only from a strict integer judge rating `1..5`, validated on the raw judge value before any Pydantic or other type conversion, or, for groundedness only, from a ratio over at least one extracted claim. An invalid rating, missing input, empty claim list or evaluator exception makes only the affected metric `not_evaluable`; it never produces a fabricated score and never aborts the remaining metrics."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/invariants.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "A valid rating is normalised as `value / 5`. An invalid rating produces",
    "newString": "A valid rating is normalised as `raw_value / 5`. An invalid rating produces"
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "3. Add `test/evaluation/validation.py`: strict `1..5` integer validation, `value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats, strings, `None` and non-finite values.",
    "newString": "3. Add `test/evaluation/validation.py`: strict `1..5` integer validation on the raw value before any conversion, `raw_value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats including `4.0`, strings, `None` and non-finite values."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

### Event 609 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff --check && echo \"diff-check: PASS\"; .venv/bin/python scripts/validate_requirements.py"
  },
  "output": [
    {
      "type": "text",
      "text": "diff-check: PASS\nPASS: 10 requirements valid\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "grep -rn \"before any Pydantic\\|before Pydantic\\|4\\.0\\|Module-review question\\|Open for module review\\|NOT_RUN\" docs/architecture/adr/001-evaluation-module.md docs/architecture/invariants.md docs/architecture/runtime-policy-catalog.md docs/code-governance/verification-constraints.md docs/code-governance/structural-constraints.md docs/architecture/evaluation-table.md | sed -n '1,80p'"
  },
  "output": [
    {
      "type": "text",
      "text": "docs/architecture/adr/001-evaluation-module.md:71:The raw judge rating must be validated before any Pydantic or other type conversion. The judge response schema therefore keeps rating fields as raw values (`Any`, or the raw structured tool-call arguments); it must not declare them as `int`, because Pydantic's default lax mode would coerce `4.0` and `\"4\"` to `4` and hide an invalid rating. `validation.validate_rating(raw_value)` performs the first check: `type(raw_value) is int` and `1 <= raw_value <= 5`. Booleans, floats including `4.0`, strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `raw_value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and `reason_code=\"invalid_rating\"`. Scores are never clamped, rounded, defaulted or replaced by zero.\ndocs/architecture/adr/001-evaluation-module.md:167:**Verification basis and status.** LangSmith compatibility was checked on 2026-11-13 against the installed `langsmith 0.9.2` source (`EvaluationResult.score` accepts `None`) and the official evaluator-output and feedback documentation. This is a type-contract check only; no live `aevaluate` call, experiment run or UI check was performed. The live check and all behavioural tests remain `NOT_RUN`; SA Review and Gate 2 are also not performed.\ndocs/architecture/adr/001-evaluation-module.md:179:**Open for module review.** `structural-constraints.md` §1 lists top-level `test/` as “No” for new work, while `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm the exception at module review and integration; §1 is human-owned and is not edited by this ADR.\ndocs/architecture/adr/001-evaluation-module.md:187:3. Add `test/evaluation/validation.py`: strict `1..5` integer validation on the raw value before any conversion, `raw_value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats including `4.0`, strings, `None` and non-finite values.\ndocs/architecture/invariants.md:71:- **Statement:** Every metric result is either `scored` with a score in `[0, 1]`, or `not_evaluable` with a null score and a reason. A `scored` result comes only from a strict integer judge rating `1..5`, validated on the raw judge value before any Pydantic or other type conversion, or, for groundedness only, from a ratio over at least one extracted claim. An invalid rating, missing input, empty claim list or evaluator exception makes only the affected metric `not_evaluable`; it never produces a fabricated score and never aborts the remaining metrics.\ndocs/architecture/runtime-policy-catalog.md:30:| POL-004 | The judge returns a rating that is not a strict integer `1..5` | `type(raw_value) is int` and range check on the raw value before Pydantic or other type conversion; booleans, floats including `4.0`, strings, `None` and non-finite values are rejected | Mark that metric `not_evaluable` with `score=None` and `invalid_rating`; do not clamp or default | None; the metric is not retried into a score | N/A | REQ-009 C-002, M-001 / INV-006 | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\ndocs/code-governance/verification-constraints.md:52:| Regression | `offline-tests` | `pytest test/offline` | Active; reports `NOT_RUN` while the directory has no tests |\ndocs/code-governance/verification-constraints.md:61:- Verdicts are only `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED` and `N/A`. A skipped test is `NOT_RUN`, never `PASS`.\ndocs/code-governance/verification-constraints.md:62:- No check is reported as passed without execution evidence. A mandatory check that is `FAIL`, `NOT_RUN` or `BLOCKED` keeps the requirement from `verified`.\ndocs/code-governance/verification-constraints.md:87:| TC-EVAL-003 | REQ-009 C-002 / INV-006 | exception | Ratings `0`, `6`, `True`, `\"4\"`, `4.0`, `4.5`, `NaN`, `inf`, `None` | `not_evaluable`, `score=None`, reason code `invalid_rating`; no clamping or default | `test/offline/test_evaluator_validity.py::test_ratings_are_validated` |\ndocs/code-governance/verification-constraints.md:104:- **LangSmith live compatibility:** `NOT_RUN`; only the SDK type contract was checked against `langsmith 0.9.2` and the official docs. A live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation.\ndocs/code-governance/verification-constraints.md:105:- **Raw-rating test note:** `TC-EVAL-003` deliberately includes `4.0` and `\"4\"`: a lax `int` schema would coerce both to `4`; the test must observe `not_evaluable` with `invalid_rating`.\ndocs/code-governance/structural-constraints.md:105:**Module-review question:** §1 lists top-level `test/` as “No” for new work; `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm this exception at module review and integration; §1 is human-owned and is not edited here.\ndocs/architecture/evaluation-table.md:68:**Open for module review:** `structural-constraints.md` §1 lists top-level `test/` as not for new work, while `architecture-blueprint.md` §4 assigns this module to `test/evaluation/`. Confirm the exception at module review and integration.\n"
    }
  ]
}
```

### Event 622 — OpenCode (build)

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/architecture/adr/001-evaluation-module.md",
    "oldString": "The blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. This conflicts with `structural-constraints.md` §1, which lists top-level `test/` as “No” for new work; the conflict is recorded as a module-review question in §10 and must be confirmed before SA acceptance, not silently resolved here.",
    "newString": "The blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. This conflicts with `structural-constraints.md` §1, which lists top-level `test/` as “No” for new work; the conflict is recorded as a module-review question in `structural-constraints.md` §10 and must be confirmed before SA acceptance, not silently resolved here."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/architecture/adr/001-evaluation-module.md (1 replacement)"
    }
  ]
}
```

#### Tool edit — completed

```json
{
  "input": {
    "path": "/Users/doppler/Documents/cityu/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md",
    "oldString": "- **LangSmith live compatibility:** `NOT_RUN`; only the SDK type contract was checked against `langsmith 0.9.2` and the official docs. A live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation.",
    "newString": "- **LangSmith type-contract check:** `PASS` (2026-11-13) against the installed `langsmith 0.9.2` source (`EvaluationResult.score` accepts `None`) and the official evaluator-output and feedback documentation; this is not a live service test.\n- **LangSmith live compatibility:** `NOT_RUN`; a live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation."
  },
  "output": [
    {
      "type": "text",
      "text": "Edited docs/code-governance/verification-constraints.md (1 replacement)"
    }
  ]
}
```

### Event 635 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff --check && echo \"diff-check: PASS\"; .venv/bin/python scripts/validate_requirements.py; echo \"---STAT---\"; git diff --stat; echo \"---STATUS---\"; git status --short"
  },
  "output": [
    {
      "type": "text",
      "text": "diff-check: PASS\nPASS: 10 requirements valid\n---STAT---\n docs/architecture/evaluation-table.md            | 30 ++++++++++++++++++++++++\n docs/architecture/invariants.md                  | 20 ++++++++++++++++\n docs/architecture/runtime-policy-catalog.md      | 12 ++++++++++\n docs/architecture/trace-matrix.md                |  4 ++--\n docs/code-governance/structural-constraints.md   | 17 ++++++++++++++\n docs/code-governance/verification-constraints.md | 27 +++++++++++++++++++++\n 6 files changed, 108 insertions(+), 2 deletions(-)\n---STATUS---\n M docs/architecture/evaluation-table.md\n M docs/architecture/invariants.md\n M docs/architecture/runtime-policy-catalog.md\n M docs/architecture/trace-matrix.md\n M docs/code-governance/structural-constraints.md\n M docs/code-governance/verification-constraints.md\n?? docs/architecture/adr/001-evaluation-module.md\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "sed -n '180,205p' docs/architecture/adr/001-evaluation-module.md; echo \"=====VERIF TAIL=====\"; sed -n '100,110p' docs/code-governance/verification-constraints.md"
  },
  "output": [
    {
      "type": "text",
      "text": "\n## 9. Implementation Steps\n\nTests for §7 are written by the Test Author after Gate 1; the steps below are the Build work that follows Gate 2.\n\n1. Create `test/evaluation/__init__.py` and export the public types and `evaluate_existing_report`.\n2. Add `test/evaluation/types.py`: `MetricStatus`, `MetricResult`, `EvaluationResult` and `EvaluationInputError`, with the score/status invariant.\n3. Add `test/evaluation/validation.py`: strict `1..5` integer validation on the raw value before any conversion, `raw_value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats including `4.0`, strings, `None` and non-finite values.\n4. Add `test/evaluation/judge.py`: the `Judge` protocol that returns raw structured field values, and a `default_judge()` that constructs the baseline `ChatOpenAI` only when called. Do not declare rating fields as `int`; no model construction at import.\n5. Add `test/evaluation/metrics.py`: the six metric groups, the 11 metric names, per-group `try/except Exception`, deterministic reason codes, and the LangSmith-independent `MetricResult` values. Call `validate_rating` on the raw judge value before constructing a `MetricResult`, and map `InvalidRating` to `not_evaluable` with `invalid_rating`. Keep the existing judge retry behaviour where it applies, but never retry an invalid rating into a score.\n6. Add `test/evaluation/entry.py`: `evaluate_existing_report`, blank-input rejection before the judge, SHA-256 `report_id`, and the no-research/no-search import boundary.\n7. Add `test/evaluation/evaluate_report.py`: the CLI, JSON output and exit codes `0/1/2`; write input errors to stderr as `error: ...`.\n8. In `test/prompts.py`, add `{user_question}`, `{report}`, `{answer}` and `{today}` to `CORRECTNESS_PROMPT`; do not change its rubric wording.\n9. Replace the bodies of the six functions in `test/evaluators.py` with adapter calls; remove the module-level `eval_model`; preserve names, signatures, baseline keys, the six-item list for overall quality and the single-dict shape for the others; add `status` metadata and the null-score/`value=\"not_evaluable\"` mapping.\n10. Add the README section for `python -m test.evaluation.evaluate_report` and the per-metric result (REQ-010 C-003).\n11. Add `\"test.evaluation\"` to `[tool.setuptools] packages` in `pyproject.toml`; the dependency-file change is accepted for the implementation PR and is not made in this SA change.\n12. Run `uv run ruff check test/evaluation test/evaluators.py test/prompts.py` and `uv run pytest test/offline` after the Test Author's tests exist. Do not modify `test/run_evaluate.py`, `src/` or the tests.\n=====VERIF TAIL=====\n| TC-EVAL-016 | POL-008 | boundary | CLI completes with all metrics `not_evaluable`; CLI completes with at least one `scored` metric | Exit code `1` and JSON on stdout in the first case; exit code `0` and JSON in the second | `test/offline/test_report_evaluation_entry.py::test_cli_exit_codes` |\n\n- **Regression:** re-run `uv run pytest test/offline`; the adapter contract in `test/offline/test_evaluator_validity.py`; and the import surface of `test/run_evaluate.py` (the six evaluator names and their call signatures must remain available). No live model or network call is needed for any case above.\n- **Live or human checks:** REQ-010 C-003 is the only `automated: false` criterion in this module; its evidence is the `REVIEW-NNN` record in `docs/review-memo.md`.\n- **LangSmith type-contract check:** `PASS` (2026-11-13) against the installed `langsmith 0.9.2` source (`EvaluationResult.score` accepts `None`) and the official evaluator-output and feedback documentation; this is not a live service test.\n- **LangSmith live compatibility:** `NOT_RUN`; a live `aevaluate` run with a `not_evaluable` result and UI rendering must be executed after implementation.\n- **Raw-rating test note:** `TC-EVAL-003` deliberately includes `4.0` and `\"4\"`: a lax `int` schema would coerce both to `4`; the test must observe `not_evaluable` with `invalid_rating`.\n\n## 8. Definition of Done\n\n| # | Condition | Done by |\n"
    }
  ]
}
```

### Event 648 — OpenCode (build)

#### Tool shell — completed

```json
{
  "input": {
    "command": "grep -rn \"validate_rating(value)\\|value / 5\\|type(value) is int\\|optional pyproject\\|needs human confirmation\" docs/architecture/adr/001-evaluation-module.md docs/architecture/invariants.md docs/architecture/runtime-policy-catalog.md docs/code-governance/verification-constraints.md docs/code-governance/structural-constraints.md docs/architecture/evaluation-table.md || true; echo \"---ADR lines---\"; wc -l docs/architecture/adr/001-evaluation-module.md"
  },
  "output": [
    {
      "type": "text",
      "text": "docs/architecture/adr/001-evaluation-module.md:71:The raw judge rating must be validated before any Pydantic or other type conversion. The judge response schema therefore keeps rating fields as raw values (`Any`, or the raw structured tool-call arguments); it must not declare them as `int`, because Pydantic's default lax mode would coerce `4.0` and `\"4\"` to `4` and hide an invalid rating. `validation.validate_rating(raw_value)` performs the first check: `type(raw_value) is int` and `1 <= raw_value <= 5`. Booleans, floats including `4.0`, strings, fractions, `None`, `NaN` and infinities are invalid. A valid rating is normalised as `raw_value / 5`. An invalid rating produces `status=\"not_evaluable\"`, `score=None` and `reason_code=\"invalid_rating\"`. Scores are never clamped, rounded, defaulted or replaced by zero.\ndocs/architecture/adr/001-evaluation-module.md:187:3. Add `test/evaluation/validation.py`: strict `1..5` integer validation on the raw value before any conversion, `raw_value / 5` normalisation, non-empty claim ratio and required-text checks. Reject booleans, floats including `4.0`, strings, `None` and non-finite values.\n---ADR lines---\n     196 docs/architecture/adr/001-evaluation-module.md\n"
    }
  ]
}
```

#### Tool shell — completed

```json
{
  "input": {
    "command": "git diff -- docs/architecture/adr/001-evaluation-module.md | head -5; echo \"(new file is untracked; use diff --no-index if needed)\"; sed -n '26,32p' docs/architecture/adr/001-evaluation-module.md"
  },
  "output": [
    {
      "type": "text",
      "text": "(new file is untracked; use diff --no-index if needed)\n- `test/run_evaluate.py` L32-61 compiles and invokes the full research graph for every dataset example; L9-11 also runs `load_dotenv(\"../.env\")` and constructs a LangSmith `Client` at import. There is no entry that scores an already generated report.\n\nThe blueprint (`architecture-blueprint.md` §4) assigns REQ-009 and REQ-010 to the `evaluation` module at `test/evaluation/`. This conflicts with `structural-constraints.md` §1, which lists top-level `test/` as “No” for new work; the conflict is recorded as a module-review question in `structural-constraints.md` §10 and must be confirmed before SA acceptance, not silently resolved here. Offline tests must run without network access, API keys or model calls (`verification-constraints.md` §3), and the baseline LangSmith entry must keep working because it is the benchmark path. The design keeps evaluation logic in `test/evaluation/` and leaves `test/run_evaluate.py` unchanged; `test/evaluators.py` becomes a thin compatibility adapter.\n\n## 3. Decision\n\nAdopt **option B**: a `test/evaluation/` package containing the evaluation types, validation, judge access, metric evaluation and the evaluation-only entry, plus a compatibility adapter in `test/evaluators.py`.\n"
    }
  ]
}
```

### Event 661 — OpenCode (build)

已应用上一轮列出的修订。仅修改 evaluation 模块的 SA 文档；未改源码、测试、`pyproject.toml`、权限或审批记录；未提交、未推送。

## 1. 实际文件差异

| 文件 | 状态 | 差异摘要 |
|---|---|---|
| `docs/architecture/evaluation-table.md` | 修改 | `EVAL-001` 增加 **Open for module review**，记录 `test/` 路径冲突（+30 行） |
| `docs/architecture/adr/001-evaluation-module.md` | 新建 | 196 行；新增原始评分值校验、LangSmith 类型/线上验证区分、路径冲突待评审项 |
| `docs/architecture/invariants.md` | 修改 | `INV-006` 明确评分在 Pydantic/类型转换前对原始值校验（+20 行） |
| `docs/architecture/runtime-policy-catalog.md` | 修改 | `POL-004` 改为对 `raw_value` 校验，显式拒绝 `4.0`（+12 行） |
| `docs/architecture/trace-matrix.md` | 修改 | REQ-009/010 两行保持与 ADR-001、INV-006/007 一致（+2/−2） |
| `docs/code-governance/structural-constraints.md` | 修改 | §10 增加 **Module-review question**，明确 §1 路径冲突待确认（+17 行） |
| `docs/code-governance/verification-constraints.md` | 修改 | `TC-EVAL-003` 加入 `4.0`；增加原始值测试说明、LangSmith 类型检查 PASS 与线上 NOT_RUN（+27 行） |

`git diff --stat`：6 个已跟踪文件，`108 insertions(+), 2 deletions(-)`；ADR 为新增未跟踪文件。

## 2. 本轮修订要点

### 2.1 原始评分类型先于 Pydantic 转换

已在以下位置明确：

- **ADR §3.5**：评分字段保持原始值（`Any` 或 raw structured arguments），不得声明为 `int`；`validate_rating(raw_value)` 先执行 `type(raw_value) is int` 与 `1..5` 范围检查。
- **ADR §3.7 / §5**：`Judge.invoke(...) -> Mapping[str, object]` 返回原始结构化字段值；`validate_rating(raw_value)` 非法时抛 `InvalidRating`。
- **ADR §9 第 3—5 步**：先校验原始值，再构造 `MetricResult`；`InvalidRating` 映射为 `not_evaluable` + `invalid_rating`。
- **INV-006**：评分结果必须来自“在 Pydantic 或其他类型转换前校验的原始 judge 值”。
- **POL-004**：检测对象改为 `raw_value`，显式说明 `4.0` 会被拒绝。
- **TC-EVAL-003**：输入加入 `4.0`，并增加说明：宽松 `int` schema 会把 `4.0` 和 `"4"` 转成 `4`，测试必须观察到 `not_evaluable`。

### 2.2 路径冲突列为待模块评审问题

已在四处记录，不再写成“已解决”：

- ADR §2：明确 `structural-constraints.md` §1 的顶层 `test/` “No” 与蓝图 §4 的 `test/evaluation/` 冲突。
- ADR §8：新增 **Open for module review**。
- `structural-constraints.md` §10：新增 **Module-review question**，说明 §1 由人类维护、本模块不修改。
- `EVAL-001`：新增 **Open for module review**。

### 2.3 LangSmith 类型兼容与实际线上验证分离

- **ADR §7**：记录已执行检查的依据——`langsmith 0.9.2` 源码中 `EvaluationResult.score` 接受 `None`，以及官方 evaluator output/feedback 文档；明确这不是线上验证。
- **`verification-constraints.md` §7**：
  - `LangSmith type-contract check`: **PASS**（2026-11-13，SDK 类型层）；
  - `LangSmith live compatibility`: **NOT_RUN**（未执行真实 `aevaluate`/实验/UI 检查）。

### 2.4 AI 日志建议条目

未写入 `docs/ai-use-log.yaml`（人类维护）。建议条目见第 5 节，只保留真实发生的决定，不声称已完成 SA Review 或测试验收。

## 3. 验收覆盖复核

| 需求/准则 | 覆盖用例 | 状态 |
|---|---|---|
| REQ-009 C-001 | TC-EVAL-001 | 已覆盖 |
| REQ-009 C-002 | TC-EVAL-002、TC-EVAL-003（含 `4.0`） | 已覆盖 |
| REQ-009 C-003 | TC-EVAL-004 | 已覆盖 |
| REQ-009 C-004 | TC-EVAL-005、006、007 | 已覆盖 |
| REQ-009 M-001 | TC-EVAL-008 | 已覆盖 |
| INV-006 | TC-EVAL-002—009 | 已覆盖 |
| REQ-010 C-001 | TC-EVAL-010、013 | 已覆盖 |
| REQ-010 C-002 | TC-EVAL-012、015 | 已覆盖 |
| REQ-010 C-003 | TC-EVAL-014（人工） | 已覆盖 |
| INV-007 | TC-EVAL-010、011、012、015 | 已覆盖 |
| CLI 退出码 | TC-EVAL-015、016 | 已覆盖 |
| 回归 | `pytest test/offline`；适配器契约；`test/run_evaluate.py` 导入面 | 已列入 |

## 4. 检查结果

| 检查 | 结果 |
|---|---|
| `git diff --check` | **PASS** |
| `.venv/bin/python scripts/validate_requirements.py` | **PASS**：`10 requirements valid` |
| 改动范围 | **PASS**：仅 7 个 evaluation SA 文档；无源码、测试、依赖、权限、审批改动 |
| SA Review / Gate 1 | **NOT_RUN** |
| 测试基线 / Gate 2 | **NOT_RUN** |
| LangSmith SDK 类型检查 | **PASS**（`langsmith 0.9.2` 源码与官方文档） |
| LangSmith 线上验证 | **NOT_RUN** |
| 提交 / 推送 | **N/A**：未执行 |

## 5. AI 使用日志建议条目

```yaml
- id: AIU-NNN
  date: "2026-11-13"
  member: DopplerXD
  purpose: >-
    Draft and write the Phase 1 SA documents for the evaluation module for REQ-009 and REQ-010,
    under a temporary Build-role exception limited to documentation.
  prompt: >-
    Follow AGENTS.md reading order and Prompt.md Phase 1. For REQ-009/REQ-010 (evaluation,
    test/evaluation/), verify role/branch/permissions; analyse test/evaluators.py,
    test/prompts.py and test/run_evaluate.py; map C-001—C-004/M-001 and C-001—C-003; compare
    three ADD candidates; write a Proposed ADR with nine sections; add the evaluation module
    sections to invariants, runtime policies, trace matrix, structural constraints §10 and
    verification constraints §7. Use option B, strict integer ratings validated before
    Pydantic conversion, not_evaluable with null score, SHA-256 report identity and CLI exit
    codes 0/1/2. Do not modify source, tests, dependency configuration, permissions or approvals.
  requirements: [REQ-009, REQ-010]
  artifacts:
    - docs/architecture/evaluation-table.md
    - docs/architecture/adr/001-evaluation-module.md
    - docs/architecture/invariants.md
    - docs/architecture/runtime-policy-catalog.md
    - docs/architecture/trace-matrix.md
    - docs/code-governance/structural-constraints.md
    - docs/code-governance/verification-constraints.md
  supervision: >-
    The member confirmed option B and decisions 1/2/3 (packaging, CLI exit codes,
    INV-007/POL numbering) and requested the pre-Pydantic rating rule and the separation of
    type-level compatibility from live verification. SA Review, test approval and live
    LangSmith verification have not occurred.
  transcript: null
```

## 6. 待模块评审确认的问题

1. `structural-constraints.md` §1 的顶层 `test/` “No” 与蓝图 §4 的 `test/evaluation/` 冲突；需模块评审确认例外。
2. 原始评分值的获取方式：建议采用“保留原始结构化字段值 + 手动校验”，而非依赖 Pydantic `int`/`StrictInt`；需确认接口选择。
3. LangSmith 线上 `aevaluate`/UI 对 `score=None`、`value="not_evaluable"` 的实际表现仍为 `NOT_RUN`。
4. `POL-002—008` 为模块临时编号，集成时可能统一重编号。
5. ADR 仍为 `Proposed`；SA Review、测试批准、实现步骤均未执行。
6. `test/run_evaluate.py` 的导入副作用（`load_dotenv("../.env")`、`Client()`）仍保留，是否单列技术债待确认。
