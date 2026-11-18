# Risk List

> **Purpose:** The risks and assumptions behind the architectural decisions, and the observation that should make the team re-evaluate a decision.
> **Authoritative for:** design risks. Decisions are in `docs/architecture/adr/`, option comparisons in `evaluation-table.md`. Defects go to `docs/bug-diary.md`, technical debt to `docs/debt-register.md`.
> **Maintained by:** each module owner adds the risks of their module; reviewed at every SA Review.
> **Last updated:** 2026-11-18

Likelihood and impact are High, Medium or Low. All risks are *Open* until evidence closes them; a closed risk keeps its number and states the evidence.

| Risk ID | Module | Source | Risk | Likelihood / Impact | Mitigation | Re-evaluate when |
|---|---|---|---|---|---|---|
| RISK-001 | delivery | REQ-004, ADR-003 | The report model silently leaves out a finding it was given, and the run is still `complete`. Only findings cut by the system are detected. | Medium / High | The report prompt asks for all findings; truncation is detected and reported. Checking the report body is INV-004 (Deferred). | A live run omits a finding while the outcome is `complete`. |
| RISK-002 | delivery | REQ-002, ADR-002 | Queued delegations run instead of being rejected, so turns with many delegations cost more tokens and time and may hit rate limits. | High / Low | Peak concurrency stays at `max_concurrent_research_units`; the per-task tool-call budget limits each task. | Live runs show queued tasks dominating cost, or providers reject the load. |
| RISK-003 | orchestration | REQ-001, ADR-001 | The model often writes a malformed findings block, so useful research ends `invalid_result`. | Medium / High | The block format is short and shown in the prompt; failures are visible in `task_results`. | More than a few tasks per live run end `invalid_result`. |
| RISK-004 | orchestration | REQ-001, ADR-001 | A retrieved URL does not prove that the source supports the claim. | Medium / Medium | Status, coverage and `notes` use counted findings only; the limitations section names partial tasks. | A requirement asks for fact-level checking, or INV-004 is taken up. |
| RISK-005 | orchestration | REQ-001, ADR-001 | The tool-call budget (calls, not model turns) is tighter than the baseline, so researchers search less. | Medium / Medium | The budget equals `max_react_tool_calls` and is configurable. | Live coverage drops compared with the baseline. |
| RISK-006 | context | REQ-005, ADR-004 | The preamble and instruction cannot be found from message types, for example if a message is inserted before the topic. | Low / High | Turns are paired by tool-call id; tests cover odd histories. | A new message type or node changes the researcher history. |
| RISK-007 | context | REQ-005, ADR-004 | A provider reports a token-limit error in a form `is_token_limit_exceeded` does not recognise, so the request is retried unchanged and fails as `runtime`. | Medium / Medium | Classification uses `compression_model`; the failure is still explicit. | A live token-limit error ends as `runtime`. |
| RISK-008 | context | REQ-005, ADR-004 | Even after removing every older turn, the preamble, the newest turn and the instruction do not fit. | Low / Medium | The task fails explicitly as `token_limit`. | This happens in live runs; then evaluate splitting the largest tool result. |
| RISK-009 | search | REQ-007, ADR-006 | The fail-closed provider allowlist rejects native-search combinations that might work (Azure OpenAI, Bedrock, OpenRouter), or a LangChain upgrade changes how `init_chat_model` infers providers. | Medium / Low | Clear error naming `research_model`; the provider rules are pinned by tests. | A user needs one of these combinations (verify it, then add it to the allowlist in ADR-006), or the provider tests fail after an upgrade. |
| RISK-010 | orchestration, search | REQ-001, ADR-001, ADR-006 | With `task_contract_enabled`, native OpenAI and Anthropic search cannot be used, because their URLs do not come back as tool messages. | High / Low | The validator rejects the combination with a clear message. | Native search results become readable as tool output. |
| RISK-011 | evaluation | REQ-009, ADR-007 | `not_evaluable` metrics have no number, so they drop out of LangSmith averages and the average can look better than it is. | Medium / Low | The status and reason are in each metric's comment. | Reports compare runs only by averages. |
| RISK-012 | context | REQ-005, EVAL-004 | There is no input-token check before a call; every token-limit case costs one rejected call. | Medium / Low | Recovery after the error is correct and bounded. | Compression often fails with `token_limit`, or a tokenizer is available without a new dependency (EVAL-004 option C). |
| RISK-013 | orchestration | REQ-002 C-007, ADR-001 | `notes` hold only counted findings (claims and sources), so the report writer gets less context than the baseline compressed text and reports may become shorter. | Medium / Medium | Findings keep their claims and sources; the full summary still guides the supervisor. | Live reports are clearly thinner than the baseline; then propose a change to REQ-002 C-007. |
| RISK-014 | search | REQ-008, ADR-008 | MCP tools often raise errors without a type or HTTP status, so they are classified `other` and do not fall back. | Medium / Medium | Classification follows `__cause__` to `httpx` errors; the error still reaches the researcher. | Live MCP failures that should have fallen back are seen; then add their error types to the table in ADR-008 §3.4. |

## Adding a Risk

Add one row with the next free `RISK-NNN` number. Name the risk in the ADR's §8 (Consequences).
