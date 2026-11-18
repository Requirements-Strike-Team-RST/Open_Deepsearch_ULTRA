# Historical baseline query reference (not a new run)

Source: local `docs/orchestration/trace_run.py`, lines 43–45, preserved under the course project workspace. These queries were recovered by read-only source inspection on 2026-11-14; the script was NOT executed. The measurements in old notes are historical claims, not re-verified evidence.

1. `simple`: 用三句话介绍 LangGraph 的 Command 对象
2. `compare3`: 比较 LangGraph、AutoGen、CrewAI 三个框架在多 agent 编排(任务拆分、并行执行、终止条件)上的差异,每个框架各给两条优点和两条缺点

Historical setup: school router, SEARCH_API=none, MAX_RESEARCHER_ITERATIONS=3, MAX_REACT_TOOL_CALLS=3. Current REQ-001 needs retrieved-source-backed findings; a no-search setup cannot demonstrate sourced completion. Search draft also rejects none without valid MCP. Therefore live C-006 requires human agreement on a valid source-capable improved configuration, with query text fixed and every configuration difference from historical baseline recorded. Do not claim an apples-to-apples provider/search comparison or replace the queries with arbitrary examples.
