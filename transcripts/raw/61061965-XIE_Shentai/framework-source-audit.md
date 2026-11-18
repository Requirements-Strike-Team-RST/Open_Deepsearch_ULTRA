# Framework source inspection supporting the proposal

This is static source/documentation evidence, not an executed runtime test.

- uv.lock pins LangGraph 1.2.9, langgraph-checkpoint 4.1.1 and langchain-core 1.4.8.
- Baseline state.py override_reducer appends ordinary lists and consumes explicit override envelopes. Child channel values, rather than the envelopes themselves, cross the compiled subgraph output boundary; main must already be cleared before append.
- The official LangGraph subgraph guide describes default checkpointer=None as per-invocation state with within-call resume; checkpointer=True accumulates state per thread. Source: https://docs.langchain.com/oss/python/langgraph/use-subgraphs#per-invocation-default (read 2026-11-14). The project has not executed ORC-039 yet.
- A read-only assistant inspected locked langchain-core config.py: set_config_context, ensure_config and merge_configs, plus RunnableBinding._merge_configs and the library's coroutine-context helper. Ambient configurable data is inherited, so omitting the private receipt from a local with_config call alone is insufficient. The proposal uses set_config_context(safe_config) and Python3.12 asyncio.create_task(..., context=clean_context), then awaits completion. Exact tool behavior remains for the later fake-model tests.

No existing model client, permissions, dependency lock or project code was modified by this inspection.
