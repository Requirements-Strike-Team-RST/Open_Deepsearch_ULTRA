# AIU-010 — REQ-008 Search Fallback Architecture

- Date: 2026-11-17
- Member: sszfot
- Session: ses_e2bdd7ea1fferC4tLbkCJeovtC
- Scope: REQ-008 ADD Iterations 1–2, EVAL-002/ADR-002, integration, consistency repair, evidence
- Source: OpenCode session history (parts from the first REQ-008 message onward)
- Note: Sanitized at export time (emails, API keys, bearer tokens and local home paths replaced). Tool payloads truncated; transient step/patch parts omitted.
- Status: Draft; human redaction review before publication.

## Message 162 — USER

You are assisting with the Software Architecture (SA) phase of the Open_Deepsearch_ULTRA project.

I am responsible for **REQ-008: Search shall fall back to configured alternative sources on failure**.

This is an architecture analysis task, not an implementation task.

**Important restrictions:**
- Read and analyze the existing repository only.
- Do not modify, create, or delete any files.
- Do not implement code or tests.
- Do not commit or push.
- Stop after presenting your analysis and wait for human approval.

## 1. Read the project requirements and architecture rules

Read the relevant sections of:

- `docs/req/requirements.yaml`
- `AGENTS.md`
- `Prompt.md`
- `docs/architecture/evaluation-table.md`
- `docs/architecture/trace-matrix.md`
- `docs/architecture/invariants.md`
- `docs/architecture/runtime-policy-catalog.md`
- `docs/code-governance/structural-constraints.md`
- `docs/code-governance/verification-constraints.md`
- `docs/architecture/adr/001-search-configuration-validation.md`

Identify the exact requirements, acceptance criteria, dependencies, and constraints for REQ-008.

Do not assume that the proposed REQ-007 architecture has been approved.

## 2. Analyze the existing search execution path

Inspect the actual implementation, especially:

- `src/open_deep_research/configuration.py`
- `src/open_deep_research/utils.py`
- `src/open_deep_research/deep_researcher.py`

Verify the paths against the actual repository layout.

Explain:

1. How `search_api` is resolved.
2. How Tavily search tools are constructed and invoked.
3. How MCP search tools are loaded.
4. How `get_all_tools` assembles the researcher's tools.
5. How `execute_tool_safely` handles exceptions.
6. How the researcher receives search results or failures.
7. How native OpenAI and Anthropic search differ from Tavily and MCP execution.

For every important finding, provide the exact file, function, and line range.

Do not invent interfaces that do not currently exist.

## 3. Extract architecturally significant requirements

Derive provisional ASR-008 identifiers from REQ-008 C-001 through C-005.

Include:

- Ordered fallback execution.
- Eligible versus ineligible errors.
- Empty results as successful searches.
- Explicit all-sources-failed reporting.
- Consistent result handling.
- Compatibility with REQ-007.
- Offline testability.
- Preservation of existing behavior when no fallback is configured.

Clearly distinguish explicit requirement statements from proposed derived architectural constraints.

## 4. Compare three candidate architectures

Evaluate at least these options:

**Option A — Researcher-level fallback**

The researcher orchestrates sequential search attempts directly.

**Option B — Dedicated fallback coordinator**

A separate search execution component coordinates ordered Tavily/MCP sources and exposes a consistent search-tool interface to the researcher.

**Option C — Tool-wrapper fallback**

An adapter wraps the primary search tool and attempts configured fallback tools on eligible failures.

For each option, analyze:

- Satisfaction of C-001 through C-005.
- Module cohesion and coupling.
- Changes to existing interfaces.
- Error classification and propagation.
- Result normalization.
- Interaction with MCP loading.
- Compatibility with REQ-007.
- Offline testability.
- Risks and implementation complexity.

Provide a comparison matrix and a reasoned recommendation, but do not select or finalize an ADR without human approval.

## 5. Identify unresolved decisions

List any decisions that require team agreement, especially:

- Fallback configuration representation and precedence.
- Eligible error classification.
- Handling of unavailable MCP fallback sources.
- Representation of all-sources-failed errors.
- Relationship between REQ-007 runtime capability checks and REQ-008 fallback.
- Whether a dedicated coordinator or a wrapper provides the cleaner module boundary.

Do not expand scope to native model search fallback, parallel searches, cost-based selection, or new provider integrations.

## 6. Output format

Return your analysis in this order:

1. Verified current implementation.
2. REQ-008 requirement and acceptance-criteria mapping.
3. Provisional ASR-008 list.
4. Three candidate architectures.
5. ADD evaluation matrix.
6. Recommended architecture and rationale.
7. Open questions for human/team decision.
8. Proposed document changes (filenames only).

**Do not edit any files. Stop after reporting your findings.**

---

## Message 163 — ASSISTANT

I'll read REQ-008 requirements and the governance docs, then verify the actual search execution paths. I'm in read-only plan mode.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"REQ-008\" -A 90 docs/req/requirements.yaml | head -120"}
output: 137:        - Errors of individual search or MCP tool calls inside researcher_tools (REQ-008)
138-        - Token-limit recovery inside compress_research (REQ-005)
139-        - Exit decision of the research loop (REQ-003)
140-        - legacy/multi_agent.py, which was removed in commit a4d557a
141-        - Automatic retry or re-planning of failed tasks
142-    fit_criterion:
143-      summary: >-
144-        Under injected researcher failures every delegation ends with a result, no failure ends
145-        the research phase, completed siblings are kept, no task is still running after the
146-        join, and no failure text appears among the findings.
147-      checks:
148-        - id: C-001
149-          description: >-
150-            Given one delegation whose researcher raises RuntimeError, when supervisor_tools
151-            runs, then it routes back to the supervisor rather than END and the task result is
152-            failed with category runtime and the original error message.
153-          verification: test/offline/test_failure_propagation.py::test_child_exception_becomes_failed_result
154-          automated: true
155-        - id: C-002
156-          description: >-
157-            Given two delegations where one researcher returns a finding and the other raises,
158-            when supervisor_tools runs, then the finding is kept in the tool messages and
159-            raw_notes and only the other task is failed.
160-          verification: test/offline

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && git log --oneline -3 && git branch --show-current"}
output: daf6947 Merge pull request #17 from Requirements-Strike-Team-RST/chore/governance-and-sa-templates
8177e4b Merge pull request #9 from Requirements-Strike-Team-RST/dependabot/uv/langchain-groq-1.1.3
e228829 Merge pull request #6 from Requirements-Strike-Team-RST/dependabot/github_actions/actions/checkout-7
docs/sa-search-fallback


---

## Message 164 — ASSISTANT

That was REQ-002. Let me read the actual REQ-008 block.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '/  - id: REQ-008/,/  - id: REQ-009/p' docs/req/requirements.yaml"}
output:   - id: REQ-008
    title: Search shall fall back to configured alternative sources on failure
    type: functional
    problem: >-
      A failed search is never retried with another source. An exception from Tavily
      (utils.py L138-170) reaches execute_tool_safely (deep_researcher.py L427-432), which hands
      the researcher model the text "Error executing tool: ..." and nothing else. Upstream #250
      asks for fallback to another API. Only Tavily and MCP tools run as client-side tools; the
      OpenAI and Anthropic searches run inside the model call and cannot be invoked as a
      substitute after a failure.
    statement: >-
      The system shall accept an ordered list of fallback search sources, each being Tavily or a
      configured MCP search tool. When a search fails with an eligible error, namely a timeout,
      a connection failure, a rate limit, a provider server error or a rejected credential, the
      system shall try the next source in order until one succeeds, and shall use a successful
      result the same way whichever source returned it. A search that returns no hits is a
      success and shall not trigger fallback, and an ineligible error shall be returned without
      fallback. When every source fails, the researcher shall receive an explicit search failure
      that lists each source tried and its error and that cannot be mistaken for an empty
      result.
    owner: sszfot
    priority: should
    priority_rationale: >-
      Fallback

---

## Message 165 — ASSISTANT

Now let me verify the actual search-execution paths in source, plus the governance docs and the REQ-007 ADR.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"def tavily_search\\|async def tavily_search_async\\|AsyncTavilyClient\\|def get_search_tool\\|async def get_all_tools\\|async def load_mcp_tools\\|def get_config_value\" src/open_deep_research/utils.py"}
output: 30:from tavily import AsyncTavilyClient
44:async def tavily_search(
138:async def tavily_search_async(
158:    tavily_client = AsyncTavilyClient(api_key=get_tavily_api_key(config))
449:async def load_mcp_tools(
531:async def get_search_tool(search_api: SearchAPI):
569:async def get_all_tools(config: RunnableConfig):
881:def get_config_value(value):


[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"def execute_tool_safely\\|async def researcher_tools\\|async def researcher\\b\\|def researcher(\" src/open_deep_research/deep_researcher.py"}
output: 365:async def researcher(state: ResearcherState, config: RunnableConfig) -> Command[Literal["researcher_tools"]]:
427:async def execute_tool_safely(tool, args, config):
435:async def researcher_tools(state: ResearcherState, config: RunnableConfig) -> Command[Literal["researcher", "compress_research"]]:


---

## Message 166 — ASSISTANT

I already have most of this code from prior reading. Let me re-confirm the exact line ranges for Tavily execution, execute_tool_safely, and the researcher_tools tool dispatch.

[tool: read | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/src/open_deep_research/utils.py", "offset": 138, "limit": 36}
output: <path>[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/src/open_deep_research/utils.py</path>
<type>file</type>
<content>
138: async def tavily_search_async(
139:     search_queries,
140:     max_results: int = 5,
141:     topic: Literal["general", "news", "finance"] = "general",
142:     include_raw_content: bool = True,
143:     config: RunnableConfig = None
144: ):
145:     """Execute multiple Tavily search queries asynchronously.
146:
147:     Args:
148:         search_queries: List of search query strings to execute
149:         max_results: Maximum number of results per query
150:         topic: Topic category for filtering results
151:         include_raw_content: Whether to include full webpage content
152:         config: Runtime configuration for API key access
153:
154:     Returns:
155:         List of search result dictionaries from Tavily API
156:     """
157:     # Initialize the Tavily client with API key from config
158:     tavily_client = AsyncTavilyClient(api_key=get_tavily_api_key(config))
159:
160:     # Create search tasks for parallel execution
161:     search_tasks = [
162:         tavily_client.search(
163:             query,
164:             max_results=max_results,
165:             include_raw_content=include_raw_content,
166:             topic=topic
167:         )
168:         for query in search_queries
169:     ]
170:
171:     # Execute all search queries in parallel and return results
172:     search_results = await asynci

[tool: read | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/src/open_deep_research/deep_researcher.py", "offset": 427, "limit": 84}
output: <path>[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/src/open_deep_research/deep_researcher.py</path>
<type>file</type>
<content>
427: async def execute_tool_safely(tool, args, config):
428:     """Safely execute a tool with error handling."""
429:     try:
430:         return await tool.ainvoke(args, config)
431:     except Exception as e:
432:         return f"Error executing tool: {str(e)}"
433:
434:
435: async def researcher_tools(state: ResearcherState, config: RunnableConfig) -> Command[Literal["researcher", "compress_research"]]:
436:     """Execute tools called by the researcher, including search tools and strategic thinking.
437:
438:     This function handles various types of researcher tool calls:
439:     1. think_tool - Strategic reflection that continues the research conversation
440:     2. Search tools (tavily_search, web_search) - Information gathering
441:     3. MCP tools - External tool integrations
442:     4. ResearchComplete - Signals completion of individual research task
443:
444:     Args:
445:         state: Current researcher state with messages and iteration count
446:         config: Runtime configuration with research limits and tool settings
447:
448:     Returns:
449:         Command to either continue research loop or proceed to compression
450:     """
451:     # Step 1: Extract current state and check early exit conditions
452:     configurable = Configuration.from_runnable_config(config)
453:     researcher_messages = stat

---

## Message 167 — ASSISTANT

Now let me read the key governance docs for REQ-008 constraints: trace-matrix, invariants INV-005, runtime policy, structural constraints §3/§10, and verification constraints §7.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"REQ-008\" docs/architecture/trace-matrix.md docs/architecture/evaluation-table.md docs/architecture/invariants.md docs/architecture/runtime-policy-catalog.md docs/code-governance/structural-constraints.md docs/code-governance/verification-constraints.md 2>/dev/null"}
output: docs/architecture/trace-matrix.md:21:| REQ-008 | Search fallback | functional | approved | TBD | INV-005 (Proposed) | Proposed: `search/` | planned: `test/offline/test_search_fallback.py` | TBD |
docs/architecture/invariants.md:63:- **Source:** REQ-007, REQ-008


[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '1,40p' docs/architecture/evaluation-table.md | head -40; echo \"=== EVAL entries ===\"; grep -n \"^## EVAL\" docs/architecture/evaluation-table.md"}
output: # Evaluation Table

> **Purpose:** ADD results: for each architectural question, 2–3 candidate solutions compared on pros, cons, complexity and testability, and the choice made.
> **Authoritative for:** option comparisons. The decision itself is recorded in the ADR named in the entry.
> **Maintained by:** each module owner adds the entries for their module; entries are integrated before SA Review (`Prompt.md` §4).
> **Last updated:** 2026-11-12

## How to Add an Entry

1. Copy the example below, take the next free `EVAL-NNN` number and keep the same fields.
2. **ASR:** list the requirements and the acceptance criteria (C-/M- IDs from `docs/req/requirements.yaml`) that shape the decision.
3. **Candidates:** describe 2–3 options; rate complexity and offline testability as Low, Medium or High.
4. **Choice:** name the chosen option and why it wins, say why each other option was rejected, then write the ADR.

## EVAL-NNN: <Question being decided>

- **Module:** <module from `architecture-blueprint.md` §4>
- **Owner:** <name>
- **Decision recorded in:** ADR-NNN
- **Status:** Open | Decided

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-NNN | C-NNN, M-NNN | e.g. correctness, testability, cost |

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | | | | | Low / Medium / High | Low / Medium / High |
| B | | | | | | |
| C (optional) | | | | | | |

---

## Message 168 — ASSISTANT

Note: this branch is `docs/sa-search-fallback` at merge `daf6947`, which is **before** the REQ-007 SA commits — so `evaluation-table.md` has no EVAL-001, the trace matrix shows REQ-007/REQ-008 rows as `TBD`, and ADR-001 does not exist here. Let me confirm the ADR-001 status and INV-005/runtime policy content visible on this branch.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && ls docs/architecture/adr/; echo \"=== INV-005 ===\"; sed -n '/^## INV-005/,/^## Adding/p' docs/architecture/invariants.md; echo \"=== runtime policy ===\"; cat docs/architecture/runtime-policy-catalog.md"}
output: 000-template.md
=== INV-005 ===
## INV-005 — Search results are never mistaken for evidence they do not contain

- **Statement:** Every search source is reached through the single tool entry point and returns the same result contract; an unknown provider is rejected at start-up, an invalid result is a failed search, and an empty result is a successful search that carries no evidence.
- **Module:** search
- **Source:** REQ-007, REQ-008
- **Status:** Proposed
- **Enforcing component:** search configuration validation at graph start; the search adapter called through `utils.get_all_tools()`.
- **Verification:** `test/offline/test_search_configuration.py`, `test/offline/test_search_fallback.py` with fake providers (normal, empty, timeout, invalid, unknown).
- **Fallback:** on an eligible error, try only the configured fallback sources in order and record each attempt; when all fail, return an explicit search failure. Never substitute a source that is not configured.

## Adding an Entry
=== runtime policy ===
# Runtime Policy Catalog

> **Purpose:** What the research agent does at runtime when something goes wrong: exceptions, retries, degradation and failure paths.
> **Authoritative for:** runtime handling policies. Each policy traces to a requirement or invariant.
> **Maintained by:** owners of modules with exception, retry, degradation or failure handling write a module section (§2); §1 is integrated from those sections before SA Review. Modules without such handling add nothin

---

## Message 169 — ASSISTANT

Important context: this branch (`docs/sa-search-fallback`, merge `daf6947`) predates the REQ-007 SA work on `docs/sa-search-provider`. ADR-001 does not exist here, EVAL-001 is absent, and REQ-008's trace row is `TBD`. Let me confirm structural §3/§5/§10 and verification §7 for the search module, and check how MCP wraps errors.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '/^## 3. Tool Assembly/,/^## 4/p' docs/code-governance/structural-constraints.md; echo \"=== §10 search? ===\"; grep -n \"### search\\|### <Module>\\|^### \" docs/code-governance/structural-constraints.md"}
output: ## 3. Tool Assembly

1. Researcher tools have one entry point, `utils.get_all_tools(config)`, which adds core tools (`ResearchComplete`, `think_tool`), then search tools for the configured `SearchAPI` (`utils.get_search_tool`), then MCP tools (`utils.load_mcp_tools`, wrapped by `utils.wrap_mcp_authenticate_tool`; `existing_tool_names` prevents name clashes).
2. `SearchAPI` values are `tavily`, `openai`, `anthropic` and `none`.
3. The supervisor's tools (`ConductResearch`, `ResearchComplete`, `think_tool`) are bound directly in the `supervisor` node.

A new researcher tool is implemented in `utils.py` or the owning extension module and registered through `get_all_tools()`; no node assembles its own tool set.

## 4. Models and API Keys
=== §10 search? ===
77:### <Module> (REQ-NNN, ADR-NNN)


[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"### search\\|^### \\|TC-0\" docs/code-governance/verification-constraints.md | head; echo \"=== wrap_mcp_authenticate_tool ===\"; sed -n '385,447p' src/open_deep_research/utils.py"}
output: 70:### <Module> (REQ-NNN, ADR-NNN)
74:| TC-001 | REQ-NNN C-NNN | normal | | | `test/offline/<file>::<test>` |
75:| TC-002 | INV-NNN | exception | | | |
76:| TC-003 | REQ-NNN M-NNN | boundary | | | |
=== wrap_mcp_authenticate_tool ===
def wrap_mcp_authenticate_tool(tool: StructuredTool) -> StructuredTool:
    """Wrap MCP tool with comprehensive authentication and error handling.

    Args:
        tool: The MCP structured tool to wrap

    Returns:
        Enhanced tool with authentication error handling
    """
    original_coroutine = tool.coroutine

    async def authentication_wrapper(**kwargs):
        """Enhanced coroutine with MCP error handling and user-friendly messages."""

        def _find_mcp_error_in_exception_chain(exc: BaseException) -> McpError | None:
            """Recursively search for MCP errors in exception chains."""
            if isinstance(exc, McpError):
                return exc

            # Handle ExceptionGroup (Python 3.11+) by checking attributes
            if hasattr(exc, 'exceptions'):
                for sub_exception in exc.exceptions:
                    if found_error := _find_mcp_error_in_exception_chain(sub_exception):
                        return found_error
            return None

        try:
            # Execute the original tool functionality
            return await original_coroutine(**kwargs)

        except BaseException as original_error:
            # Search for

---

## Message 170 — ASSISTANT

I now have complete evidence. Let me confirm how `tavily_search` returns empty results and the exact line range for the search tool construction/dispatch by name.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"No valid search results\\|return formatted_output\\|def tavily_search(\" src/open_deep_research/utils.py; echo \"=== get_search_tool range ===\"; sed -n '531,567p' src/open_deep_research/utils.py | head -5"}
output: 44:async def tavily_search(
127:        return "No valid search results found. Please try different search queries or use a different search API."
136:    return formatted_output
=== get_search_tool range ===
async def get_search_tool(search_api: SearchAPI):
    """Configure and return search tools based on the specified API provider.

    Args:
        search_api: The search API provider to use (Anthropic, OpenAI, Tavily, or None)


---

## Message 171 — ASSISTANT

I have all evidence needed. Note I'm on `docs/sa-search-fallback` (`daf6947`), which predates the REQ-007 SA commits, so ADR-001/EVAL-001 are not present on this branch. Here is the read-only analysis.

---

# REQ-008 Architecture Analysis — Search Fallback on Failure

## 1. Verified current implementation

Branch `docs/sa-search-fallback`, HEAD `daf6947` (this branch predates the REQ-007 SA work; `docs/architecture/adr/` has only `000-template.md`, the evaluation table has no numbered entry, and the REQ-008 trace row is `TBD`).

**1.1 How `search_api` is resolved.** `Configuration.search_api` is a `SearchAPI` enum field with default `tavily` (`src/open_deep_research/configuration.py:78-93`). `from_runnable_config` reads each field from `SEARCH_API` env first, then `configurable`, dropping `None` (`configuration.py:236-247`). Pydantic rejects an invalid enum value during construction. `get_all_tools` later re-wraps with `SearchAPI(get_config_value(configurable.search_api))` (`utils.py:583`, `881-890`).

**1.2 Tavily construction and invocation.** `tavily_search` is a `@tool` (`utils.py:43-136`); it calls `tavily_search_async` (`utils.py:138-173`), which builds `AsyncTavilyClient(api_key=...)` (`:158`) and runs `client.search(...)` per query via `asyncio.gather` (`:172`). Exceptions from the client propagate out of `tavily_search_async`; client-side raw results are summarised; an empty result returns the literal string "No valid search results found..." (`utils.py:127`) — i.e. empty-is-not-error at the tool boundary.

**1.3 MCP loading.** `load_mcp_tools` (`utils.py:449-524`) validates config (`:470-479`), fetches tokens if `auth_required` (`:465-468`), sets up `MultiServerMCPClient` (`:500-501`), filters by declared tools/name clashes (`:506-524`), and wraps each with `wrap_mcp_authenticate_tool` (`utils.py:385-447`). Critically, **all failures collapse to `[]`**: config invalid (`:478-479`), `get_tools()` exception (`:502-504`). The wrapper re-raises non-MCP errors and converts MCP auth-interaction (`-32003`) to `ToolException` (`:440`).

**1.4 `get_all_tools` assembly.** `utils.py:569-597`: starts `[tool(ResearchComplete), think_tool]` (`:579`), extends with `get_search_tool(search_api)` (`:584`), computes `existing_tool_names`, extends with `load_mcp_tools` (`:594-595`). `get_search_tool` (`utils.py:531-567`) returns native **dict definitions** for anthropic/openai (`:540-550`), the `tavily_search` tool object for tavily (`:552-560`, with `metadata["name"]="web_search"`), else `[]`.

**1.5 `execute_tool_safely`.** `deep_researcher.py:427-432`: `await tool.ainvoke(args, config)` inside `try`; on any `Exception` returns the **string** `"Error executing tool: {e}"`. It never re-raises, never classifies, never retries.

**1.6 How the researcher receives results/failures.** `researcher_tools` (`deep_researcher.py:435-509`) reloads tools (`:467`), builds `tools_by_name` keyed by `.name` or `.get("name","web_search")` (`:468-471`), executes all tool calls in parallel through `execute_tool_safely` (`:474-479`), and wraps each observation into a `ToolMessage` (`:482-489`). The only difference between success and failure is the message content string; the model cannot distinguish an empty result from a swallowed exception beyond text.

**1.7 Native vs Tavily/MCP execution.** Native OpenAI/Anthropic search runs **inside the model call** via tool definitions bound in `researcher` (`deep_researcher.py:406-411`); it is detected post-hoc (`openai_websearch_called`/`anthropic_websearch_called`, `deep_researcher.py:458-461`; `utils.py:607-658`). Tavily and MCP run as **client-side tools** invoked in `researcher_tools`. Native search therefore cannot be invoked as a fallback substitute — consistent with REQ-008 `out_of_scope`.

## 2. REQ-008 requirement and acceptance-criteria mapping

Requirement: `depends_on: [REQ-007]`, `priority: should`, `status: approved`, `safety_relevant: false` (`requirements.yaml` REQ-008 block).

| Item | Statement (from requirements.yaml) | In scope? |
|---|---|---|
| C-001 | Primary times out + working fallback → primary tried once, fallback tried next, its result returned | yes |
| C-002 | Three sources, first two eligible-fail → tried in order, third result returned | yes |
| C-003 | Every source eligible-fails → researcher gets explicit failure naming each source + error, no fabricated result | yes |
| C-004 | Primary returns no hits without error → empty result returned, no fallback | yes |
| C-005 | Primary rejects query as malformed (ineligible) → error returned, no fallback | yes |

Constraints stated in the requirement: sources are **Tavily or a configured MCP search tool** only; eligible errors = timeout, connection failure, rate limit, provider server error, rejected credential; successful result used identically regardless of source; empty ≠ failure; all-failed must be explicit and unmistakable for empty. Out of scope: native OpenAI/Anthropic fallback, new providers, parallel search, cost selection, credential recovery, supervisor delegation/termination.

Remaining under-specified (the requirement's `notes` says "classification of eligible errors is to be agreed in the design review").

## 3. Provisional ASR-008 list

Explicit (traceable to the requirement):
- **ASR-008-01** — Ordered fallback over a configured list of Tavily/MCP sources (C-001, C-002).
- **ASR-008-02** — Eligible vs ineligible error classification gates fallback (C-001, C-002, C-005).
- **ASR-008-03** — Empty result is success and suppresses fallback (C-004).
- **ASR-008-04** — All-sources-failed produces an explicit, non-fabricated failure listing each source and error (C-003).
- **ASR-008-05** — A successful result is handled identically regardless of which source produced it.

Derived architectural constraints (proposed, not in the requirement text):
- **ASR-008-06** — Fallback operates only on client-side tools (Tavily/MCP); native search is excluded (restates out_of_scope as a design invariant).
- **ASR-008-07** — Offline testability: classification and ordering must be exercisable with fake tools and injected errors, no network/keys.
- **ASR-008-08** — Preservation: when no fallback is configured, behaviour is unchanged (single-source, current error path).
- **ASR-008-09** — Compatibility with REQ-007: fallback must not depend on the *unapproved* REQ-007 design; it must work whether or not REQ-007 validation is later accepted, and should reuse its module boundary if accepted.
- **ASR-008-10** — MCP sources that are unavailable at load time must be handled deterministically (this is exactly the area REQ-007 leaves open in U-1).

## 4. Three candidate architectures

**Option A — Researcher-level fallback.** `researcher_tools` (or `execute_tool_safely`) loops over the configured sources when a search tool raises. Touches `deep_researcher.py:427-509` and needs source selection logic inside the node.

**Option B — Dedicated fallback coordinator.** A new `search/` component runs the ordered attempt loop over constructed Tavily/MCP source callables, classifies errors, normalises results, and returns either a result or an aggregate failure. The researcher (or `get_all_tools`) calls it through one stable search entry; tool assembly changes so the coordinator receives the ordered sources and its result is what the researcher sees.

**Option C — Tool-wrapper fallback.** A wrapper around the primary search tool that, on eligible failure, invokes configured fallback tools in order, returning the first success or the aggregate error. Reuses `get_all_tools` assembly; the wrapper is registered as the single search tool.

## 5. ADD evaluation matrix

| Dimension | A — Researcher-level | B — Coordinator | C — Tool-wrapper |
|---|---|---|---|
| C-001 (ordered, primary once) | ⚠️ possible, but ordering logic lands in the node (thin-node rule §2.1 risk) | ✅ coordinator owns the loop; order explicit | ✅ wrapper loops in order |
| C-002 (ordered 3 sources) | ⚠️ same node burden | ✅ natural | ✅ natural |
| C-003 (explicit all-failed) | ⚠️ node must build the aggregate string | ✅ single place builds aggregate | ✅ wrapper builds aggregate |
| C-004 (empty = success) | ⚠️ must special-case empty in node | ✅ coordinator treats empty as success | ✅ wrapper treats empty as success |
| C-005 (ineligible, no fallback) | ⚠️ classification in node | ✅ coordinator classifies | ✅ wrapper classifies |
| Cohesion / coupling | ❌ search logic in orchestration node | ✅ one module, one responsibility (`search/`) | ⚠️ wrapper holds routing + assembly coupling |
| Interface changes | ❌ changes node internals; mixes concerns | ✅ new module interface; nodes stay thin | ⚠️ changes what the "search tool" is; assembly affected |
| Error classification & propagation | ⚠️ inside node, hard to reuse | ✅ centralised, testable | ✅ centralised but tied to tool contract |
| Result normalisation | ⚠️ node-dependent | ✅ explicit normalisation type | ⚠️ wrapper must mimic tool result shape |
| MCP loading interaction | ⚠️ node must reach MCP tools | ✅ coordinator receives sources; MCP stays via assembly | ⚠️ wrapper must know fallback tool identities from assembly |
| Compatibility with REQ-007 (unapproved) | ⚠️ entangles with node validation | ✅ same `search/` module; orthogonal to validation | ⚠️ overlaps tool-assembly territory (REQ-007 rejected Option C region) |
| Offline testability | ⚠️ tests invoke graph/node | ✅ pure coordinator with fake sources | ✅ wrapper with fake tools, but tool-shape coupling |
| Risks / complexity | Medium risk (node bloat) | Low–Medium complexity, cleanest | Medium (tool contract coupling, assembly changes) |

## 6. Recommended architecture and rationale

**Recommend Option B — dedicated fallback coordinator in the `search/` module.** Rationale grounded in the code:
- The only failure surface for client-side searches is `execute_tool_safely` (`deep_researcher.py:427-432`), which currently collapses everything to a string; classification and ordering belong in a dedicated, offline-testable component, not in the node (thin-node rule, `structural-constraints.md` §2.1).
- A coordinator keeps the `search/` module cohesive ("search configuration validation, fallback", blueprint §4) and avoids coupling fallback to tool-assembly (which is exactly the region REQ-007's rejected Option C occupied).
- Empty-is-success is easiest to express at a single normalisation point (C-004), and the all-failed aggregate (C-003) is built in one place.

This is a **proposal pending human approval**, not a finalized ADR. Option A is rejected for placing search routing in the orchestration node and for testability; Option C is a credible alternative but couples fallback to the tool object contract and to `get_all_tools` assembly, risking interference with REQ-007 and harder result normalisation.

Caveat: the actual "tool called by name" dispatch (`tools_by_name`, `deep_researcher.py:468-471`) means whichever option is chosen, the researcher must still address a single search entry the model can call; the coordinator would present one search tool whose identity is stable regardless of which source ultimately answered.

## 7. Open questions for human/team decision

1. **Fallback configuration representation & precedence** — a new ordered field (e.g. list of Tavily/MCP tool names) on `Configuration`/`MCPConfig`; how it interacts with `search_api` (primary) and `structural-constraints.md` §8 (config field with `x_oap_ui_config`, baseline default unchanged until verified).
2. **Eligible error classification** — the concrete types/signals for timeout, connection failure, rate limit, server error, rejected credential, given that Tavily client exceptions are raw and MCP errors are wrapped as `ToolException` (`utils.py:440`).
3. **Unavailable MCP fallback sources** — behaviour when a configured MCP fallback cannot load (ties directly to REQ-007 U-1); is an unloadable MCP source "tried and failed" or "not attempted"?
4. **All-failed error representation** — the exact message shape that satisfies C-003 and cannot be mistaken for the empty-result string (`utils.py:127`).
5. **REQ-007 relationship** — whether REQ-008 reuses the (still-unapproved) REQ-007 validator/capability module; REQ-008 must not assume ADR-001 is accepted.
6. **Coordinator vs wrapper boundary** — confirm B over C, and where the coordinator is invoked (inside `execute_tool_safely` replacement vs. as the assembled search tool).
7. **Single-source preservation** — confirm ASR-008-08: with no fallback list, reuse today's exact error path.

Excluded by scope (do not expand): native model search fallback, parallel searches, cost-based selection, new provider integrations, credential recovery.

## 8. Proposed document changes (filenames only — not edited)

- `docs/architecture/evaluation-table.md` (new EVAL entry for REQ-008)
- `docs/architecture/adr/00N-search-fallback.md` (new ADR; number per current branch's adr/ contents — on this branch only `000-template.md` exists, so next free is `001`)
- `docs/architecture/invariants.md` (INV-005 search-result contract, already sources REQ-008 — refine, keep Proposed)
- `docs/architecture/runtime-policy-catalog.md` (fallback policy entry, proposed)
- `docs/architecture/trace-matrix.md` (fill REQ-008 row)
- `docs/code-governance/structural-constraints.md` (§10 search module section — coordinate with REQ-007's module section)
- `docs/code-governance/verification-constraints.md` (§7 search test cases for C-001…C-005)

Not touched: source, tests, `requirements.yaml`, README, AI logs, transcripts.

**Stopping here for human approval. No files were modified.** One branch note for your decision: this work is on `docs/sa-search-fallback` at `daf6947`, which does **not** contain the REQ-007 SA artifacts (ADR-001/EVAL-001). If the REQ-007 SA work is merged later, the search-module sections and INV-005/POL numbering (REQ-007 planned `POL-002`) will need reconciliation at integration — please confirm which branch base this REQ-008 work should target.

---

## Message 172 — USER

You are assisting with the Software Architecture phase of Open_Deepsearch_ULTRA.

I own REQ-007 and REQ-008. REQ-008 depends on REQ-007.

Current branch: `docs/sa-search-fallback`.

The REQ-007 architecture artifacts have now been merged into this branch, including:

- `docs/architecture/adr/001-search-configuration-validation.md`
- `docs/architecture/evaluation-table.md` (EVAL-001)
- `docs/architecture/invariants.md`
- `docs/architecture/runtime-policy-catalog.md`
- `docs/architecture/trace-matrix.md`
- `docs/code-governance/structural-constraints.md`
- `docs/code-governance/verification-constraints.md`

Your task is **REQ-008 ADD Iteration 1: Search Fallback Architecture**.

This is a read-only architecture design task.

Do not create, edit, or delete files. Do not implement code, write tests, commit, or push.

## 1. Establish the architecture baseline

Read the actual REQ-007 ADR-001, EVAL-001, relevant invariants, runtime policies, structural constraints, and verification constraints.

Identify:

- Approved requirements versus proposed architecture decisions.
- The REQ-007 static validation boundary.
- The REQ-007 runtime MCP availability policy.
- The proposed search capability predicate.
- The proposed MCP load-result interface.
- Open decisions U-1 through U-5, as actually documented.

Do not assume that any Proposed decision has been approved.

## 2. Analyze REQ-008 against REQ-007

Read the full REQ-008 requirement and acceptance criteria C-001 through C-005.

Explain exactly how ordered fallback would interact with:

- `Configuration.from_runnable_config`
- `get_search_tool`
- `get_all_tools`
- `load_mcp_tools`
- `wrap_mcp_authenticate_tool`
- `execute_tool_safely`
- `researcher_tools`

Identify any conflicts between REQ-007's fail-fast behavior and REQ-008's fallback behavior.

## 3. Derive ASR-008

Create a proposed ASR list with explicit traceability to REQ-008 and its acceptance criteria.

Separate:

A. Requirements explicitly stated in REQ-008.

B. Derived architectural constraints that require team approval.

Focus on ordering, eligible errors, empty-result semantics, all-failed reporting, result compatibility, offline testability, and preservation of existing behavior.

## 4. Evaluate three ADD alternatives

A. Researcher-level fallback.

B. Dedicated fallback coordinator.

C. Search tool wrapper.

For each alternative, evaluate:

- Functional correctness.
- REQ-008 C-001 through C-005.
- Compatibility with REQ-007.
- Module boundaries.
- Interface stability.
- Error classification.
- MCP availability and failure handling.
- Search result representation.
- Offline testability.
- Implementation complexity and risks.

Use the evaluation-table.md template and existing EVAL-001 style.

## 5. Investigate critical design details

Pay special attention to:

1. How the fallback coordinator would be exposed as a tool without breaking tool-name dispatch.
2. Whether Tavily and MCP search tools have compatible input schemas.
3. How to distinguish empty success from tool errors.
4. How to classify errors before `execute_tool_safely` converts them to strings.
5. How a configured but unavailable MCP fallback should be represented.
6. How to avoid bypassing REQ-007 validation.
7. How fallback configuration should be represented without changing default behavior.
8. How an all-sources-failed error reaches the researcher unambiguously.

For each issue, propose a concrete solution and identify any remaining uncertainty.

## 6. Recommend an architecture

Recommend one alternative, but clearly mark it as **Proposed**.

Explain why the alternatives are less suitable.

List all unresolved decisions that require human or team review.

## 7. Output

Return:

1. Verified REQ-007 architecture baseline.
2. REQ-008 requirements and ASR mapping.
3. ADD alternatives and evaluation matrix.
4. Recommended architecture with component responsibilities.
5. REQ-007/REQ-008 integration analysis.
6. Open decisions and risks.
7. Proposed EVAL-002 content.
8. Proposed ADR-002 outline.
9. Proposed document changes.

Do not edit any files.

Stop after producing the report and wait for human review.

---

## Message 173 — ASSISTANT

I'll verify the state of this branch to see whether the REQ-007 artifacts are actually present as claimed.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && git log --oneline -5 && echo \"---branch---\" && git branch --show-current && echo \"---adr---\" && ls docs/architecture/adr/ && echo \"---eval entries---\" && grep -n \"^## EVAL\" docs/architecture/evaluation-table.md"}
output: fa18c98 Merge remote-tracking branch 'origin/docs/sa-search-provider' into docs/sa-search-fallback  Lines starting with '#' will be ignored, and an empty message aborts
7544a7c docs: clean up REQ-007 AI evidence formatting
8db87b8 docs(ai): record REQ-007 architecture refinement evidence
67bc289 docs(sa): refine REQ-007 search configuration architecture
11be0fb docs(ai): fix REQ-007 transcript naming and redaction
---branch---
docs/sa-search-fallback
---adr---
000-template.md
001-search-configuration-validation.md
---eval entries---
15:## EVAL-NNN: <Question being decided>
40:## EVAL-001: Where search configuration is validated before research


[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -c \"POL-002\" docs/architecture/runtime-policy-catalog.md; echo \"---U ids in ADR---\"; grep -oE \"U-[1-5] \\([^)]*\\)\" docs/architecture/adr/001-search-configuration-validation.md 2>/dev/null | sort -u; echo \"---tc count---\"; awk '/^### search \\(REQ-007/{f=1} f' docs/code-governance/verification-constraints.md 2>/dev/null | grep -cE \"^\\| TC-[0-9]{3} \""}
output: 1
---U ids in ADR---
U-1 (open)
U-2 (open, wording)
U-3 (open)
U-4 (open)
U-5 (open)
---tc count---
26


---

## Message 174 — ASSISTANT

The REQ-007 artifacts are present as claimed. Let me read the merged ADR-001 and EVAL-001 in full to establish the accurate baseline.

[tool: read | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/001-search-configuration-validation.md"}
output: <path>[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/001-search-configuration-validation.md</path>
<type>file</type>
<content>
1: # ADR-001: Validate Search Configuration with a Pure Validator Before Research
2:
3: - **Status:** Proposed
4: - **Date:** 2026-11-13
5: - **Module:** search
6: - **Owner:** sszfot
7: - **Evaluation:** EVAL-001 (`docs/architecture/evaluation-table.md`)
8: - **SA Review:** pending (no `SA-NNN` recorded)
9:
10: > This decision is *Proposed*. It is not approved until SA Review accepts it (`Prompt.md` §4, Gate 1). Everything below describes intended behaviour; none of it is implemented yet. Decisions still open for the team are listed in §12.
11:
12: ## 1. Architecturally Significant Requirements
13:
14: | Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
15: |---|---|---|
16: | REQ-007 | C-001, C-002, C-003, C-004, C-005 | The decision must reject invalid search configurations *before any model or search call*, which fixes where validation runs in the graph and whether it may use a model or network. |
17: | REQ-007 | ASR-007-01 to ASR-007-09 (below) | These sub-drivers fix purity, module boundary, provider/model rules, MCP static-vs-runtime split and documentation consistency. |
18:
19: Architectural drivers (ASR), provisional IDs used consistently across EVAL-001, this ADR and the module sections:
20:
21: | ID | Statement |
22: |---|---|
23: | ASR-007-01 | Every entry path into the

---

## Message 175 — ASSISTANT

Now let me read EVAL-001, the search module sections, and LOCATE the actual current source (the branch merge may have changed utils.py). Let me verify source line numbers against this branch's HEAD.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '/^## EVAL-001/,/^$/p' docs/architecture/evaluation-table.md | head -40; echo \"=== structural search section ===\"; sed -n '/^### search (REQ-007/,/REQ-008 (search fallback)/p' docs/code-governance/structural-constraints.md"}
output: ## EVAL-001: Where search configuration is validated before research

=== structural search section ===
### search (REQ-007, ADR-001)

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/search/` |
| Responsibility | Resolve and validate a search configuration on each run before a model/search call, decide whether a run has search capability, and classify the MCP load outcome, without model calls or implicit process-environment access during static validation; apply the runtime MCP stop-and-error policy (Proposed, pending SA Review). |
| Public interface | `resolve_search_api(raw_configurable, environ: Mapping) -> SearchAPI` (pure; caller passes the environment snapshot); `resolve_configuration(raw_configurable, environ) -> Configuration` (builds from validated effective inputs, §7.2); `validate_search_configuration(search_api, research_model, mcp) -> None` (raises a domain error); `classify_mcp(mcp: MCPConfig \| None) -> MCPStatus`; `model_provider(model: str) -> str`; `load_mcp_result(config, existing_tool_names) -> McpLoadResult` (MCP load distinction, §8.1a; U-5); `has_search_capability(evidence: SearchEvidence) -> bool` (evaluated after binding, step 4) |
| Called from | `clarify_with_user` (public boundary: effective configuration resolution and static validation only — no tool assembly, MCP loading or native binding) and `researcher` (subgraph boundary, which runs the §8.0 order: validate → assemble → bind → capability → invoke) in `deep_researcher.py` |
|

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"def tavily_search\\|async def tavily_search_async\\|def get_search_tool\\|async def get_all_tools\\|async def load_mcp_tools\\|def wrap_mcp_authenticate_tool\\|def execute_tool_safely\\|async def researcher_tools\\|async def researcher\\b\" src/open_deep_research/utils.py src/open_deep_research/deep_researcher.py"}
output: src/open_deep_research/utils.py:44:async def tavily_search(
src/open_deep_research/utils.py:138:async def tavily_search_async(
src/open_deep_research/utils.py:385:def wrap_mcp_authenticate_tool(tool: StructuredTool) -> StructuredTool:
src/open_deep_research/utils.py:449:async def load_mcp_tools(
src/open_deep_research/utils.py:531:async def get_search_tool(search_api: SearchAPI):
src/open_deep_research/utils.py:569:async def get_all_tools(config: RunnableConfig):
src/open_deep_research/deep_researcher.py:365:async def researcher(state: ResearcherState, config: RunnableConfig) -> Command[Literal["researcher_tools"]]:
src/open_deep_research/deep_researcher.py:427:async def execute_tool_safely(tool, args, config):
src/open_deep_research/deep_researcher.py:435:async def researcher_tools(state: ResearcherState, config: RunnableConfig) -> Command[Literal["researcher", "compress_research"]]:


---

## Message 176 — ASSISTANT

Source line numbers are unchanged from my earlier reads (verified). Let me quickly read EVAL-001 candidates and the verification §7 REQ-007 section header to match style and confirm POL/test numbering, plus check the trace-matrix REQ-008 row and runtime policy.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '40,75p' docs/architecture/evaluation-table.md; echo \"=== trace REQ-007/008 ===\"; grep -nE \"REQ-00[78] \" docs/architecture/trace-matrix.md; echo \"=== POL rows ===\"; grep -nE \"POL-0\" docs/architecture/runtime-policy-catalog.md"}
output: ## EVAL-001: Where search configuration is validated before research

- **Module:** search
- **Owner:** sszfot
- **Decision recorded in:** ADR-001
- **Status:** Open (provisional selection of B; awaiting SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-007 | C-001, C-002, C-003, C-004, C-005 | correctness (fail before model/search calls), testability, modularity, behaviour preservation |

Architectural drivers (provisional IDs, see ADR-001 §1): ASR-007-01 validate on every path to a model/search call; ASR-007-02 native provider ↔ `research_model`; ASR-007-03 static MCP capability versus runtime availability; ASR-007-04 unsupported provider lists the supported set (including via `SEARCH_API`); ASR-007-05 pure and offline-testable; ASR-007-06 preserve valid behaviour and topology; ASR-007-07 documentation consistency; ASR-007-08 a statically declared but unusable MCP must not silently produce a no-search run; ASR-007-09 an explicit search-capability predicate replaces the tool-count check.

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Validate at the top of the research graph entry node | `deep_researcher.py` (`clarify_with_user`) | Small; runs early | Violates the thin-node rule (`structural-constraints.md` §2.1); correctness depends on placement before the `allow_clarification` return; no reusable, unit-testable interfac

---

## Message 177 — ASSISTANT

I now have the complete, verified baseline. Two specifics I must check for the fallback design: the Tavily tool's input schema and how `tools_by_name` keys the search tool (relevant to tool-name dispatch), and the exact empty-result return string.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '43,60p' src/open_deep_research/utils.py; echo \"=== empty string ===\"; sed -n '125,136p' src/open_deep_research/utils.py; echo \"=== tools_by_name ===\"; sed -n '466,479p' src/open_deep_research/deep_researcher.py"}
output: @tool(description=TAVILY_SEARCH_DESCRIPTION)
async def tavily_search(
    queries: List[str],
    max_results: Annotated[int, InjectedToolArg] = 5,
    topic: Annotated[Literal["general", "news", "finance"], InjectedToolArg] = "general",
    config: RunnableConfig = None
) -> str:
    """Fetch and summarize search results from Tavily search API.

    Args:
        queries: List of search queries to execute
        max_results: Maximum number of results to return per query
        topic: Topic filter for search results (general, news, or finance)
        config: Runtime configuration for API keys and model settings

    Returns:
        Formatted string containing summarized search results
    """
=== empty string ===
    # Step 7: Format the final output
    if not summarized_results:
        return "No valid search results found. Please try different search queries or use a different search API."

    formatted_output = "Search results: \n\n"
    for i, (url, result) in enumerate(summarized_results.items()):
        formatted_output += f"\n\n--- SOURCE {i+1}: {result['title']} ---\n"
        formatted_output += f"URL: {url}\n\n"
        formatted_output += f"SUMMARY:\n{result['content']}\n\n"
        formatted_output += "\n\n" + "-" * 80 + "\n"

    return formatted_output
=== tools_by_name ===
    # Step 2: Handle other tool calls (search, MCP tools, etc.)
    tools = await get_all_tools(config)
    tools_by_name = {
        tool.name if hasattr(tool, "name") else t

---

## Message 178 — ASSISTANT

I have everything needed. Here is the REQ-008 ADD Iteration 1 report — read-only; no files changed.

---

# REQ-008 ADD Iteration 1 — Search Fallback Architecture (read-only)

Branch `docs/sa-search-fallback`, HEAD `fa18c98` (REQ-007 merged from `docs/sa-search-provider`). All source line numbers below re-verified against this HEAD.

## 1. Verified REQ-007 architecture baseline

**Approved vs Proposed.** REQ-007 is `status: approved` (requirements.yaml). But **every architecture artifact is Proposed**: ADR-001 §header "Status: Proposed", EVAL-001 "Open", INV-005 "Proposed", POL-002 "Proposed", `SA Review: pending (no SA-NNN recorded)`. Nothing in the REQ-007 design is approved architecture. REQ-008 must not assume any of it holds.

| Element | What the docs actually say | Status |
|---|---|---|
| Static validation boundary | `search` module called at `clarify_with_user` (public) and `researcher` (subgraph); ADR-001 §3, §10 | Proposed |
| `resolve_search_api(raw_configurable, environ)` | Pure; raw env snapshot; env precedence; omitted/None→tavily; rejects invalid (ADR-001 §7.2) | Proposed |
| Config-resolution boundary | Build `Configuration` from validated inputs (Option 1) or additive `environ=` factory (Option 2) — implementation dependency (ADR-001 §7.2) | Proposed |
| Runtime MCP availability policy | `POL-002`: declared MCP that yields no usable tool **stops the affected research with an error**; no substitution (ADR-001 §9) | Proposed; U-1 open |
| Capability predicate | `has_search_capability(SearchEvidence)`; native requires `native_bound`; MCP requires `LOADED` + ≥1 tool; Tavily requires `tavily_search` present (ADR-001 §8.3) | Proposed; U-4 open |
| MCP load-result interface | Two options (U-5): Option A adapter owns load; **Option B `utils.load_mcp_tools` returns `McpLoadResult(status, tools)`** with `LOADED/ZERO_USABLE_TOOLS/AUTH_MISSING/LOAD_FAILED` (ADR-001 §8.1a) | Proposed; depends on code change not yet implemented |
| Execution order | §8.0 six steps: validate → assemble → bind → capability → invoke → optional post-response (ADR-001 §8.0) | Proposed |

**Open decisions U-1…U-5 (as documented):**
- **U-1** Adopt stop-and-error MCP policy under REQ-007 now vs defer to REQ-002/REQ-004; placement in `researcher`.
- **U-2** "start-up" → per-run wording; confirm INV-005.
- **U-3** Strict prefix vs LangChain-compatible provider inference.
- **U-4** Replace dead `len(tools)==0` with `has_search_capability`.
- **U-5** MCP adapter (Option A) vs `load_mcp_tools` return-contract refactor (Option B).

**REQ-007 trace row:** `TC-001–TC-025` (26 IDs in body incl. TC-026 in verification; trace header says TC-001–TC-025 — minor pre-existing inconsistency, noted but not part of this task).

## 2. REQ-008 vs the actual code path

REQ-008: `depends_on: [REQ-007]`, `priority: should`, `status: approved`, `safety_relevant: false`; sources = Tavily or configured MCP tool; eligible errors = timeout, connection failure, rate limit, provider server error, rejected credential; empty = success; all-failed = explicit list; notes: "classification of eligible errors is to be agreed in the design review."

How fallback interacts with each function (verified lines):

- **`Configuration.from_runnable_config`** (`configuration.py:236-247`) — reads env-then-configurable per field, drops `None`; rejects invalid enum. A fallback list would be a **new** field; adding it changes the configuration surface and must preserve env precedence and default-off behaviour.
- **`get_search_tool`** (`utils.py:531-567`) — returns native **dicts** for openai/anthropic, the `tavily_search` tool object for tavily (`metadata["name"]="web_search"`), `[]` for none/unknown. Fallback must only ever draw from Tavily/MCP (native excluded).
- **`get_all_tools`** (`utils.py:569-597`) — core tools + search tool + MCP tools; dedups by `existing_tool_names`. Any fallback source must be in this assembled set for `researcher_tools` to dispatch it.
- **`load_mcp_tools`** (`utils.py:449-524`) — collapses all failures to `[]`; wraps tools via `wrap_mcp_authenticate_tool`. A "configured but unavailable MCP fallback" is indistinguishable from "not configured" today (same U-5 gap REQ-007 has).
- **`wrap_mcp_authenticate_tool`** (`utils.py:385-447`) — re-raises non-MCP errors unchanged; converts MCP `-32003` to `ToolException`. So MCP failures surface as arbitrary exceptions or `ToolException`, not a typed "connection/rate-limit" error.
- **`execute_tool_safely`** (`deep_researcher.py:427-432`) — catches **all** exceptions and returns the **string** `"Error executing tool: {e}"`. This is where error identity is destroyed *before* the researcher sees anything; classification for C-002/C-005 must happen **above or before** this.
- **`researcher_tools`** (`deep_researcher.py:435-509`) — reloads tools (`:467`), keys `tools_by_name` by `tool.name` or `.get("name","web_search")` (`:468-471`), runs all calls in parallel via `execute_tool_safely` (`:474-479`), wraps each in a `ToolMessage` content string (`:482-489`). The model cannot distinguish error vs empty except by text; the empty string is `"No valid search results found..."` (`utils.py:127`).

**Tavily input schema:** `tavily_search(queries: List[str], max_results, topic, config)` (`utils.py:43-49`) returns a formatted **string**. MCP tools are `StructuredTool` objects with server-defined schemas — **not guaranteed compatible** with Tavily's `queries` arg.

**REQ-007 fail-fast vs REQ-008 fallback — the core tension:**
- REQ-007 §9/POL-002 says a declared-but-unusable MCP **stops the affected research** (no substitution).
- REQ-008 says an **eligible search error** should fall over to the next configured source.
- Conflict surface: is an MCP **load** failure (REQ-007 stop) the same event as an MCP **search** failure (REQ-008 fallback)? The docs currently draw the line at load-time (stop) vs invocation-time (fallback), but REQ-008 C-001 is about a search *timing out*, not a source failing to load. **This boundary must be reconciled explicitly** (see §6, D-1). Also REQ-008 explicitly excludes "recovery from invalid credentials", which overlaps POL-002's `AUTH_MISSING` stop — so an `AUTH_MISSING` MCP fallback source is *not* a fallback trigger.

## 3. Requirements and ASR mapping

**A. Explicitly stated in REQ-008 (traceable, not derived):**

| ASR | Statement | Criteria |
|---|---|---|
| ASR-008-01 | Ordered fallback over a configured list of Tavily/MCP sources; next source tried in order until one succeeds | C-001, C-002 |
| ASR-008-02 | Eligible errors (timeout, connection failure, rate limit, provider server error, rejected credential) trigger fallback; ineligible errors return without fallback | C-001, C-002, C-005 |
| ASR-008-03 | A search returning no hits is a success and does not trigger fallback | C-004 |
| ASR-008-04 | When every source fails, the researcher receives an explicit failure listing each source and its error, not mistakable for empty | C-003 |
| ASR-008-05 | A successful result is used identically regardless of which source produced it | statement |

**B. Derived architectural constraints (require team approval):**

| ASR | Statement | Rationale |
|---|---|---|
| ASR-008-06 | Fallback operates only on client-side sources (Tavily/MCP); native model search excluded | restates out_of_scope as a design invariant |
| ASR-008-07 | Error classification and ordering are deterministic and offline-testable with fake tools/injected errors | verification-constraints §3 |
| ASR-008-08 | With no fallback configured, behaviour is unchanged (today's single-source error path) | preservation; structural-constraints §5 "extend, never replace" |
| ASR-008-09 | Fallback must not depend on unapproved REQ-007 decisions; if it reuses the `search` module it works whether or not ADR-001 is accepted | REQ-008 must stand even if U-1…U-5 never land as written |
| ASR-008-10 | A configured-but-unloadable MCP fallback is represented deterministically (tried-and-failed vs not-attempted) | U-5 makes load outcome unrecoverable today |
| ASR-008-11 | The coordinator exposes one stable search entry the model can call, without breaking `tools_by_name` dispatch | `deep_researcher.py:468-471` keys by tool name |

## 4. Three ADD alternatives and evaluation matrix

**A. Researcher-level fallback.** `execute_tool_safely`/`researcher_tools` loops over sources on exception.
**B. Dedicated fallback coordinator** (`search/`): pure ordering/classification/normalisation of Tavily+MCP source callables.
**C. Search tool wrapper.** A `web_search`-named wrapper that tries configured fallback tools on eligible failure.

| Dimension | A — Researcher-level | B — Coordinator | C — Tool-wrapper |
|---|---|---|---|
| C-001 ordered, primary once | ⚠️ node holds loop (thin-node risk §2.1) | ✅ | ✅ |
| C-002 ordered 3 sources | ⚠️ node burden | ✅ | ✅ |
| C-003 explicit all-failed | ⚠️ node builds aggregate | ✅ one place | ✅ one place |
| C-004 empty=success | ⚠️ must special-case `utils.py:127` string | ✅ normalised centrally | ✅ but string-shape coupling |
| C-005 ineligible no-fallback | ⚠️ classification in node | ✅ | ✅ |
| REQ-007 compatibility | ❌ entangles with node validation; POL-002 stop vs fallback mixed | ✅ same module, orthogonal; can assert "REQ-008 does not override POL-002 load-stop" | ⚠️ sits in assembly region REQ-007 rejected as Option C |
| Module boundaries | ❌ logic in orchestration | ✅ `search/` cohesive | ⚠️ wrapper couples routing+assembly |
| Interface stability | ❌ changes node internals | ✅ new module; nodes thin | ⚠️ changes what "the search tool" is |
| Error classification | ⚠️ after `execute_tool_safely` already stringified | ✅ before stringification | ✅ inside wrapper |
| MCP availability/failure | ⚠️ node reaches MCP tools | ✅ receives sources via assembly; consumes `McpLoadResult` | ⚠️ wrapper must know fallback tool identities |
| Result representation | ⚠️ node-dependent strings | ✅ explicit normalisation | ⚠️ must mimic tool return shape |
| Offline testability | ⚠️ invoke node/graph | ✅ pure, fake source callables | ✅ fake tools, tool-shape coupling |
| Complexity / risk | Medium (node bloat) | Low–Medium, cleanest | Medium (contract coupling) |

## 5. Critical design details — concrete proposals

1. **Expose coordinator as a tool without breaking `tools_by_name`.** Register the coordinator as the single search tool under a **stable name** (e.g. keep `tavily_search`'s effective dispatch name `web_search`, or a dedicated `web_search` name) and ensure `get_all_tools` includes it so `tools_by_name` (`deep_researcher.py:468-471`) resolves the model's call. The coordinator's user-facing schema must match what the model was shown. *Uncertainty:* whether to keep `web_search` (metadata alias of `tavily_search`, §8.3 note) or introduce an explicit coordinator tool name — affects REQ-007 capability predicate and README.
2. **Tavily vs MCP input compatibility.** Tavily takes `queries: List[str]`, `max_results`, `topic`. MCP tools expose server-defined args and may not accept `queries`. Proposal: the coordinator owns a **normalised search request** (queries list) and per-source **adapters** translate to each source's schema; sources whose schema cannot be adapted are rejected at config/validation time, not at call time. *Uncertainty:* exact MCP schema negotiation; some MCP "search" tools may loop.

3. **Empty success vs tool error.** Today empty = a specific return string (`utils.py:127`), and errors = `"Error executing tool: ..."`. Proposal: the coordinator returns a **typed result** (e.g. `SearchOutcome(found: bool, content: str)` or a small dataclass) so C-004 is decided on the actual result, not string sniffing. Avoid parsing the existing strings. *Uncertainty:* whether MCP empties look like empty strings or empty lists.
4. **Classify errors before `execute_tool_safely`.** Classification must run where the exception type is intact — inside the coordinator's attempt loop, around `await source.ainvoke(...)`, **before** `execute_tool_safely` (`deep_researcher.py:427-432`) flattens to a string. Proposal: coordinator catches the raw exception and maps to `eligible/ineligible`; only its final typed result (or aggregate failure) flows back through the node.
5. **Configured-but-unavailable MCP fallback.** Today `load_mcp_tools` returns `[]` for load failure, so the coordinator cannot tell "unavailable" from "not configured". Proposal: depend on `McpLoadResult` (REQ-007 U-5) — an unavailable fallback source is recorded as **tried-and-failed with the load error** (so C-003 lists it) or **excluded as not-attempted**; team must pick (ASR-008-10). *Uncertainty:* this creates a hard dependency on the U-5 code change; if U-5 is deferred, fallback cannot honestly distinguish the case.
6. **Avoid bypassing REQ-007 validation.** The coordinator lives inside the same `search/` module and is invoked **after** the §8.0 validation steps; it must not re-implement validation. Fallback source list itself should be validated statically (each entry names a real Tavily/MCP source). *Uncertainty:* whether fallback-list validation is REQ-007's job or REQ-008's.
7. **Fallback config without changing default behaviour.** A new opt-in field (e.g. ordered `search_fallback` list) with default empty = today's behaviour exactly (ASR-008-08), `x_oap_ui_config` metadata per structural-constraints §8, baseline default until verified. *Uncertainty:* field placement (`Configuration` vs `MCPConfig`) and precedence vs `search_api`.
8. **All-failed error reaching the researcher unambiguously.** Return one `ToolMessage` whose content is a structured, unmistakable failure (e.g. `Search failed: all sources exhausted` + per-source reasons), distinct from the empty string at `utils.py:127`. Proposal: define a marker prefix the researcher prompt can recognise, and/or a typed outcome the node renders consistently. *Uncertainty:* whether the model-facing text or a structured field is the contract C-003 tests.

## 6. Recommended architecture (Proposed)

**Recommend Option B — dedicated fallback coordinator in the `search/` module.**

Rationale:
- The only failure surface for client-side search is `execute_tool_safely` (`deep_researcher.py:427-432`), which destroys error identity; classification must live **above** it in a dedicated, offline-testable component, not in the node (thin-node rule §2.1).
- Keeps `search/` cohesive ("validation, fallback", blueprint §4) and avoids the assembly-coupling that REQ-007 already rejected (Option C region, ADR-001 §4).
- Empty-vs-error (C-004) and all-failed aggregation (C-003) are single-point concerns best expressed once.
- Compatible with REQ-007: coordinator consumes `McpLoadResult` + assembled tools as values, never re-validates, and does **not** override POL-002's load-time stop unless the team decides the reconcile boundary (§2, D-1).

**Why not A:** puts routing in the orchestration node, hard to test, entangles with REQ-007 validation, and classifies after error identity is lost.
**Why not C (rejected as primary):** couples fallback to the tool-object contract and `get_all_tools` assembly, reproduces the shape REQ-007 rejected for validation, and makes result normalisation awkward; it remains a viable *thin wrapper around the coordinator* but not the core.

**Component responsibilities (Proposed):**
- `search/fallback.py` (new) — ordered attempt loop over normalised sources; error classification; result normalisation; aggregate failure. Pure over injected source callables.
- `search/sources.py` or adapter in coordinator — per-source schema adapters (Tavily, MCP) → normalised search request.
- Integration: invoked from `researcher_tools` (or a replacement for the `execute_tool_safely` search branch) via the single assembled search tool; reads `McpLoadResult` from `get_all_tools` assembly.

## 7. Open decisions and risks

- **D-1** REQ-007 POL-002 load-time **stop** vs REQ-008 invocation-time **fallback**: are they the same failure or different? (Conflict: ADR-001 §9 says "no substitution".)
- **D-2** Fallback configuration field: name, placement (`Configuration` vs `MCPConfig`), precedence vs `search_api`, default-off.
- **D-3** Eligible error classification: concrete signals for Tavily raw exceptions and MCP `ToolException`/`-32003` (`utils.py:440`).
- **D-4** Unavailable MCP fallback source: tried-and-failed vs not-attempted (depends on U-5/`McpLoadResult`).
- **D-5** Hard dependency on REQ-007 U-5: without the structured loader, D-4 and the "MCP unavailable" branch cannot be honest.
- **D-6** Coordinator vs wrapper as the exposed search tool; exact tool name and schema visible to the model.
- **D-7** All-failed representation contract (marker string vs typed field) that C-003 tests against.
- **D-8** Whether REQ-008 fallback supersedes / defers to the `AUTH_MISSING` stop (REQ-008 excludes credential recovery).
- **Risk:** adding a `Configuration` field touches a shared contract (`structural-constraints.md` §6) → owner approval.
- **Risk:** native search excluded means fallback only helps Tavily/MCP configurations; must be documented.

## 8. Proposed EVAL-002 content (not written)

- **Title:** "Where ordered search fallback is executed on failure"
- Module: search · Owner: sszfot · Decision recorded in: ADR-002 · Status: Open
- ASR: REQ-008 C-001…C-005; ASR-008-01…08-11
- Candidates: A (researcher-level), B (coordinator), C (tool-wrapper) with the matrix in §4.
- Choice: **Proposed B**; rejected A (node bloat, late classification) and C (assembly/contract coupling, overlaps REQ-007 rejected region).
- Note: dependency on REQ-007 `McpLoadResult` (U-5) and the POL-002 boundary (D-1).

## 9. Proposed ADR-002 outline (not written)

Header (Status: Proposed; Module: search; Evaluation: EVAL-002; SA Review pending) · §1 ASRs (REQ-008 + ASR-008-*) · §2 Context (execute_tool_safely stringification, load_mcp_tools `[]` collapse, empty string at `utils.py:127`, native excluded) · §3 Decision (coordinator in `search/`, single exposed search tool, typed outcomes, config field default-off) · §4 Rejected (A, C) · §5 Components/Interfaces (`search/fallback.py`, source adapters, `FallbackResult`/`SearchOutcome`, consumes `McpLoadResult`) · §6 State none / runtime policy (fallback policy + POL-002 boundary) / INV-005 / deterministic boundary · §7 Error classification rules · §8 Result normalisation & empty semantics · §9 Integration with REQ-007 (does not override validation; consumes capability/load evidence) · §10 Implementation steps · §11 Verification (TC map to C-001…C-005) · §12 Risks/open decisions D-1…D-8, rollback.

## 10. Proposed document changes (filenames only — not edited)

- `docs/architecture/evaluation-table.md` — add EVAL-002.
- `docs/architecture/adr/002-search-fallback.md` — new ADR.
- `docs/architecture/invariants.md` — refine INV-005 (already sources REQ-007, REQ-008; keep Proposed).
- `docs/architecture/runtime-policy-catalog.md` — add fallback policy (next free `POL-NNN`; `POL-001` placeholder, `POL-002` taken) and reconcile with POL-002.
- `docs/architecture/trace-matrix.md` — fill REQ-008 row.
- `docs/code-governance/structural-constraints.md` — extend §10 search module with fallback interface.
- `docs/code-governance/verification-constraints.md` — add §7 search fallback cases (C-001…C-005).

Not touched: source, tests, requirements, README, AI logs, transcripts.

---

**Stopping here for human review. No files were modified.**

One thing needs your decision before any future drafting: **D-1** (REQ-007 load-time stop vs REQ-008 invocation-time fallback) is the crux conflict — should the fallback coordinator treat a declared-but-unloadable MCP as an eligible fallback failure, or must it still honour POL-002's stop? And **D-5**: REQ-008's honest MCP-unavailable handling depends on the still-unapproved U-5 loader change — do you want REQ-008 designed to depend on it, or to degrade gracefully if U-5 is deferred?

---

## Message 179 — USER

Continue REQ-008 Software Architecture analysis with **ADD Iteration 2 — Decision Resolution**.

Current branch: `docs/sa-search-fallback`.

Use the actual repository and the existing ADD Iteration 1 analysis as evidence.

This remains a **read-only design task**. Do not modify files, implement code, create tests, commit, or push.

## 1. Refine the proposed architecture

Use Option B (Dedicated Fallback Coordinator) as the preferred candidate, but keep it Proposed.

Define concrete responsibilities and interfaces for:

- Search request normalization.
- Tavily and MCP source adapters.
- Ordered fallback coordination.
- Eligible/ineligible error classification.
- Successful, empty, and failed search outcomes.
- Integration with existing tool assembly and dispatch.

Do not assume that all MCP search tools accept Tavily's input schema.

## 2. Resolve the REQ-007 / REQ-008 interaction

Evaluate the following proposed policy:

- REQ-007 validates configuration before model/search calls.
- REQ-007 checks whether usable search capability exists.
- An unavailable fallback MCP source does not necessarily stop the run if other usable search sources remain.
- REQ-008 handles eligible failures during search execution.
- No available search capability produces an explicit error.
- Missing authentication configuration is not automatically repaired.
- A rejected credential during a search invocation is eligible for fallback, as explicitly required by REQ-008.

Compare this policy with existing ADR-001 §9 and POL-002.

Identify precisely which statements would need amendment and which decisions still require team approval.

Do not silently overwrite the existing REQ-007 proposal.

## 3. Specify the runtime contracts

Propose typed interfaces or equivalent contracts for:

- SearchRequest.
- SearchSource.
- SearchOutcome.
- SearchAttemptFailure.
- AllSourcesFailed.
- ErrorClassification.
- MCP load-result integration.

For each, explain required fields, ownership, and failure semantics.

Distinguish a source that could not be loaded from a source whose invocation failed.

Specify how results are rendered into ToolMessage without being mistaken for empty results.

## 4. Refine error classification

Map the explicitly eligible categories:

- Timeout.
- Connection failure.
- Rate limit.
- Provider server error.
- Rejected credential.

Also cover ineligible failures, including malformed queries.

Explain how classification works for Tavily and MCP without relying solely on error-message substring matching.

Identify cases where the underlying exception type or structured error code is insufficient and require a documented policy.

## 5. Complete the ADD comparison

Compare Options A, B, and C across all REQ-008 acceptance criteria and quality attributes.

Pay special attention to whether Option C can serve as a thin tool-facing adapter over Option B, rather than being a competing implementation of the fallback algorithm.

Do not conflate the rejected REQ-007 validation-in-tool-assembly alternative with REQ-008's tool-facing fallback adapter; they solve different architectural problems.

## 6. Revisit the open decisions

For D-1 through D-8, provide:

- Exact decision statement.
- Recommended option.
- Alternative options.
- Consequences.
- Dependencies on REQ-007 U-1 through U-5.
- Whether team approval is required.

Do not treat these decisions as approved.

## 7. Prepare the drafting plan

Produce:

1. Refined architecture diagram in Mermaid.
2. Interface contract table.
3. Error classification matrix.
4. Complete ADD comparison matrix.
5. Proposed EVAL-002 decision text.
6. Proposed ADR-002 section-by-section content outline.
7. Exact changes required to existing shared architecture documents.
8. Proposed verification cases, clearly marked Planned and Not Executed.
9. Unresolved questions to post in the team discussion.

Stop after presenting the analysis and wait for human review.

---

## Message 180 — ASSISTANT

I'll verify the current state and the specifics needed for the refined design before drafting.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && git log --oneline -1 && sed -n '/^## 9. Runtime MCP Failure/,/^## 10/p' docs/architecture/adr/001-search-configuration-validation.md"}
output: fa18c98 Merge remote-tracking branch 'origin/docs/sa-search-provider' into docs/sa-search-fallback  Lines starting with '#' will be ignored, and an empty message aborts
## 9. Runtime MCP Failure — Proposed Stop-and-Error Policy (U-1, open)

When a declared MCP is the effective search source (typically `search_api=none` with `MCP_DECLARED`), distinguish these outcomes. None of them is a fallback: the design never substitutes another source (that is REQ-008, out of scope).

| Outcome | Detection (via the §8.1a adapter/refactor; not available today) | Proposed behaviour |
|---|---|---|
| Connection or loading failure | `McpLoadResult.status == LOAD_FAILED` (the `get_tools()` exception branch, today `utils.py:502-504`) | Stop the affected research; raise an explicit error naming `mcp_config.url` and "connection failed". |
| Loaded, zero usable declared search tools | `McpLoadResult.status == ZERO_USABLE_TOOLS` (empty after the declared-name/name-conflict filter, today `utils.py:506-524`) | Stop; raise an explicit error that the declared MCP tools are not available. |
| Missing required authentication | `McpLoadResult.status == AUTH_MISSING` (`auth_required=True`, no token, today `utils.py:475-479`) | Stop; raise an explicit error that the MCP server requires authentication. |
| Loaded and usable, tool returns no hits | `McpLoadResult.status == LOADED`; the tool runs and returns zero results | Success with no evidence; not an error and no stop (belongs to INV-005 / REQ-008). |

Th

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '1,40p' src/open_deep_research/state.py; echo \"=== ToolException import ===\"; grep -n \"ToolException\\|from tavily\\|import time\\|asyncio\" src/open_deep_research/utils.py | head"}
output: """Graph state definitions and data structures for the Deep Research agent."""

import operator
from typing import Annotated, Optional

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


###################
# Structured Outputs
###################
class ConductResearch(BaseModel):
    """Call this tool to conduct research on a specific topic."""
    research_topic: str = Field(
        description="The topic to research. Should be a single topic, and should be described in high detail (at least a paragraph).",
    )

class ResearchComplete(BaseModel):
    """Call this tool to indicate that the research is complete."""

class Summary(BaseModel):
    """Research summary with key findings."""

    summary: str
    key_excerpts: str

class ClarifyWithUser(BaseModel):
    """Model for user clarification requests."""

    need_clarification: bool = Field(
        description="Whether the user needs to be asked a clarifying question.",
    )
    question: str = Field(
        description="A question to ask the user to clarify the report scope",
    )
    verification: str = Field(
        description="Verify message that we will start research after the user has provided the necessary information.",
=== ToolException import ===
3:import asyncio
24:    ToolException,
30:from tavily import AsyncTavilyClient
110:    summaries = await asyncio.gathe

---

## Message 181 — ASSISTANT

Let me confirm the Tavily exception types available and how `asyncio.TimeoutError`/`ToolException` surface, plus the researcher_tools dispatch name so I can specify the tool-facing adapter precisely.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && uv run python - <<'PY'\nimport tavily, inspect\nprint(\"tavily version:\", getattr(tavily, \"__version__\", \"?\"))\ntry:\n    from tavily import AsyncTavilyClient\n    src = inspect.getsource(AsyncTavilyClient)\n    print(\"has UsageLimitExceeded:\", \"UsageLimitExceeded\" in src or \"429\" in src)\nexcept Exception as e:\n    print(\"err\", e)\ntry:\n    import tavily.exceptions as ex\n    print([n for n in dir(ex) if not n.startswith(\"_\")])\nexcept Exception as e:\n    print(\"no tavily.exceptions:\", e)\nPY"}
output: Uninstalled 1 package in 3ms
Installed 1 package in 3ms
tavily version: ?
has UsageLimitExceeded: True
no tavily.exceptions: No module named 'tavily.exceptions'


---

## Message 182 — ASSISTANT

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && uv run python - <<'PY'\nimport inspect\nfrom tavily import AsyncTavilyClient\nsrc = inspect.getsource(AsyncTavilyClient)\nfor kw in [\"UsageLimitExceeded\",\"InvalidAPIKeyError\",\"ForbiddenError\",\"raise \",\"status_code\",\"429\",\"432\",\"433\",\"status\"]:\n    print(kw, \"->\", src.count(kw))\nimport tavily\nprint(\"module attrs:\", [n for n in dir(tavily) if \"Error\" in n or \"Limit\" in n])\nPY"}
output: UsageLimitExceeded -> 4
InvalidAPIKeyError -> 4
ForbiddenError -> 4
raise  -> 25
status_code -> 20
429 -> 4
432 -> 4
433 -> 4
status -> 24
module attrs: ['BadRequestError', 'InvalidAPIKeyError', 'MissingAPIKeyError', 'UsageLimitExceededError']


---

## Message 183 — ASSISTANT

Tavily exposes typed exceptions (`BadRequestError`, `InvalidAPIKeyError`, `MissingAPIKeyError`, `UsageLimitExceededError`, `ForbiddenError`) — this matters for classification without substring matching. Let me confirm their base classes and that `MissingAPIKeyError`/`ForbiddenError` are importable.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && uv run python - <<'PY'\nimport tavily\nnames = [n for n in dir(tavily) if n.endswith(\"Error\")]\nfor n in names:\n    cls = getattr(tavily, n)\n    print(n, \"-> bases:\", [b.__name__ for b in cls.__mro__[1:4]])\ntry:\n    from tavily.errors import UsageLimitExceeded\n    print(\"tavily.errors import OK\")\nexcept Exception as e:\n    print(\"tavily.errors:\", e)\nPY"}
output: BadRequestError -> bases: ['Exception', 'BaseException', 'object']
InvalidAPIKeyError -> bases: ['Exception', 'BaseException', 'object']
MissingAPIKeyError -> bases: ['Exception', 'BaseException', 'object']
UsageLimitExceededError -> bases: ['Exception', 'BaseException', 'object']
tavily.errors: cannot import name 'UsageLimitExceeded' from 'tavily.errors' ([LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/.venv/lib/python3.12/site-packages/tavily/errors.py)


---

## Message 184 — ASSISTANT

Good — Tavily typed errors exist but don't share a common `TavilyError` base and `ForbiddenError` isn't top-level. Documentation of the exact import path is a policy decision I'll flag. Let me check the MCP client's error surface and `McpError` code availability (already imported in utils).

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && uv run python - <<'PY'\nfrom mcp import McpError\nimport mcp\nprint(\"McpError MRO:\", [c.__name__ for c in McpError.__mro__[:4]])\ntry:\n    from mcp.types import ErrorData\n    print(\"ErrorData fields:\", getattr(ErrorData, \"model_fields\", {}).keys())\nexcept Exception as e:\n    print(\"ErrorData:\", e)\nPY"}
output: McpError MRO: ['McpError', 'Exception', 'BaseException', 'object']
ErrorData fields: dict_keys(['code', 'message', 'data'])


---

## Message 185 — ASSISTANT

I have all the evidence needed (Tavily typed errors, `McpError.code`, no shared base class, `execute_tool_safely` stringification at `deep_researcher.py:427-432`, empty string at `utils.py:127`, `load_mcp_tools` `[]` collapse). Here is the read-only design report.

---

# REQ-008 ADD Iteration 2 — Decision Resolution (read-only)

Branch `docs/sa-search-fallback`, HEAD `fa18c98`. Nothing modified. Option B remains **Proposed**.

## 1. Refined architecture — Option B components & interfaces

**Responsibilities (Proposed):**

| Component | Responsibility |
|---|---|
| `search/request.py` | `SearchRequest` — normalised, provider-agnostic search intent (queries, limits, topic). |
| `search/adapters/` | Per-source adapters: translate `SearchRequest` → each source's native schema and map native results/exceptions back to `SearchOutcome`/`SearchAttemptFailure`. Tavily and MCP have **different** input schemas; adapters are not interchangeable. |
| `search/fallback.py` | `FallbackCoordinator` — ordered attempt loop, classification, aggregation. Pure over injected `SearchSource`s. |
| `search/errors.py` | `ErrorClassification`, `SearchAttemptFailure`, `AllSourcesFailed`. |
| Integration | One tool-facing entry (see §5) exposing the coordinator as the single search tool; consumes `McpLoadResult` from assembly. |

**Key rule (explicit):** MCP search tools do **not** accept Tavily's `queries: List[str]` arg. Each adapter declares the capability to build a call from a `SearchRequest`; a source that cannot be adapted is rejected at configuration time, not at call time.

## 2. REQ-007 / REQ-008 interaction — comparison and precise amendments

**Proposed policy (to evaluate):**
1. REQ-007 validates config before model/search calls.
2. REQ-007 checks usable search capability exists.
3. An unavailable fallback MCP source does **not** necessarily stop the run if other usable sources remain.
4. REQ-008 handles eligible failures during execution.
5. No available search capability → explicit error.
6. Missing auth config is not auto-repaired.
7. Rejected credential during invocation is eligible for fallback (REQ-008 explicit).

**Comparison with ADR-001 §9 / POL-002:** ADR §9 says for `MCP_DECLARED` sources — `LOAD_FAILED`/`ZERO_USABLE_TOOLS`/`AUTH_MISSING` → **"Stop the affected research; no source substitution."** The proposed policy **narrows** that: an MCP source that is the *only* usable source and cannot load still stops; but if it is one of several configured fallback sources, its load failure becomes a per-source failure inside the coordinator, not a run stop.

| Statement to amend | Where | Nature of amendment (needs team approval) |
|---|---|---|
| "None of them is a fallback: the design never substitutes another source" | ADR-001 §9 intro | Restrict to *primary/single-source* case; allow fallback sources per REQ-008 |
| `LOAD_FAILED` → "Stop the affected research" | ADR-001 §9 row 1 | Add "…unless a configured fallback remains; then record as a failed source" |
| `ZERO_USABLE_TOOLS` → "Stop" | ADR-001 §9 row 2 | Same conditional |
| `AUTH_MISSING` → "Stop" | ADR-001 §9 row 3 | Keep as **configuration error** (D-8); not a runtime fallback trigger, since REQ-008 excludes credential recovery — *but* distinguish missing-auth-config (rule 6, stop) from credential-rejected-at-invocation (rule 7, fallback-eligible) |
| POL-002 "Behaviour: stop … no source substitution" | runtime-policy-catalog POL-002 | Add the multi-source clause and a companion fallback policy (new POL-NNN) |
| capability predicate `has_search_capability` | ADR-001 §8.3 | Must count **usable configured fallback sources** as satisfying "search capability" (rule 3), not only the primary source |
| "no available search capability → explicit error" | ADR-001 §8.3, §9 | Already consistent; keep, and make it the aggregate-failure path |

**Conflict explicitly resolved:** the crux (prior D-1) is split into two distinct events — **(a) source unavailable at load** (REQ-007 concern; fatal only if no other usable source) vs **(b) source invocation failed with an eligible error** (REQ-008 concern; fallback). AUTH: missing *configuration* (a, fatal, rule 6) vs rejected *credential at invocation* (b, fallback, rule 7).

**Do not silently overwrite:** ADR-001 §9 stays Proposed as-is until the team approves these amendments; REQ-008's ADR-002 records the interaction as a *proposed* dependent decision.

## 3. Runtime contracts (typed interfaces, Proposed)

| Contract | Required fields | Ownership | Failure semantics |
|---|---|---|---|
| `SearchRequest` | `queries: list[str]`; `max_results: int`; `topic: str` | Coordinator builds once | Immutable input to all sources |
| `SearchSource` (protocol) | `name: str`; `async invoke(req) -> SearchOutcome`; `load_status: McpLoadStatus \| None` | Adapter per source | Raises typed `SearchAttemptFailure` on eligible/ineligible failure |
| `SearchOutcome` | `found: bool`; `content: str`; `source_name: str` | Adapter returns | `found=False` = empty success (C-004), **not** failure |
| `SearchAttemptFailure` | `source_name`; `classification: ErrorClassification`; `detail: str` | Coordinator per attempt | Captured, not raised past the loop |
| `ErrorClassification` | enum `ELIGIBLE` / `INELIGIBLE`; `category` (timeout/connection/rate_limit/server_error/credential_rejected/malformed/other) | `search/errors.py` | Decides whether to continue |
| `AllSourcesFailed` | `failures: list[SearchAttemptFailure]` | Coordinator when loop exhausts | Rendered to researcher as explicit failure (never empty) |
| `McpLoadResult` (from REQ-007 §8.1a) | `status: McpLoadStatus`; `tools` | Orchestration/loader | "could not be loaded" ≠ "invocation failed": a non-`LOADED` source is recorded as a `SearchAttemptFailure` with `category=load_failed` before any invocation |

**Loaded vs invocation-failed distinction:** `load_status != LOADED` → failure recorded at *assembly*, source never invoked. `LOADED` then `invoke` raises → failure recorded from the invocation. Both feed `AllSourcesFailed` but carry different categories.

**ToolMessage rendering:** the coordinator returns a `SearchOutcome` (success) or an `AllSourcesFailed` aggregate. Integration renders:
- success → existing formatted string (unchanged);
- empty → the existing empty marker string (`utils.py:127`) so it stays "empty success";
- all-failed → a **distinct** marker, e.g. `Search failed: all sources exhausted` + one line per `source_name: category: detail`, guaranteed never equal to the empty marker. (Contract for C-003; exact marker is D-7.)

## 4. Error classification (Tavily + MCP, typed first)

Verified: Tavily exposes `BadRequestError`, `InvalidAPIKeyError`, `MissingAPIKeyError`, `UsageLimitExceededError`, plus `ForbiddenError` (not top-level); they have **no shared base**. MCP `McpError` carries `ErrorData{code, message, data}`.

| Category | Tavily | MCP | Eligible? |
|---|---|---|---|
| Timeout | `asyncio.TimeoutError` / client timeout | tool-call timeout | eligible |
| Connection failure | client connection error (`aiohttp`/transport) | `McpError` connection / transport error | eligible |
| Rate limit | `UsageLimitExceededError`, HTTP 429/432/433 | `McpError` code rate-limit (if surfaced) | eligible |
| Provider server error | HTTP 5xx (client raises generic) | `McpError` 5xx | eligible |
| Rejected credential | `InvalidAPIKeyError`, `ForbiddenError` (401/403) | MCP auth error (note: wrapper maps `-32003` to `ToolException`, `utils.py:440`) | eligible (rule 7) |
| Malformed query | `BadRequestError` (400) | `McpError` invalid-params | **ineligible** (C-005) |
| Missing auth *config* | n/a | `AUTH_MISSING` (pre-invocation) | **ineligible/stop** (rule 6, D-8) |

**Without substring matching:** classify by **exception class** where typed (Tavily typed errors, `McpError.code`) and by HTTP `status_code` attribute when present. **Substring matching is a fallback only where typed info is absent**, and must be documented as such.

**Where types are insufficient (require documented policy):**
- Tavily connection/5xx often raise a generic client exception without a stable class → rely on `status_code` attr or a bounded allow-list; document the fallback substring rule.
- `wrap_mcp_authenticate_tool` converts `-32003` to `ToolException` (`utils.py:440`), losing the code → classification must run on the **original** exception inside the adapter (before the wrapper) or the wrapper must preserve the code.
- `execute_tool_safely` (`deep_researcher.py:427-432`) flattens everything to a string → classification must occur **inside the coordinator**, never after this function.
- Tavily `MissingAPIKeyError` at construction is a config error, not an invocation error → ineligible/stop.

## 5. Completed ADD comparison (A / B / C)

**Reframing C:** Option C is **not** a competing fallback algorithm. It is a **thin tool-facing adapter** that exposes Option B's coordinator as the single `web_search`-named tool so `tools_by_name` dispatch (`deep_researcher.py:468-471`) still resolves the model's call. C-over-B is therefore **complementary**, and the genuine competing alternatives are **A (fallback in researcher)** vs **B (fallback in coordinator, exposed via the thin C adapter)**.

| Criterion | A — researcher-level | B — coordinator | C — thin adapter over B |
|---|---|---|---|
| C-001 ordered/primary-once | ⚠️ | ✅ | ✅ (delegates to B) |
| C-002 3 sources ordered | ⚠️ | ✅ | ✅ |
| C-003 explicit all-failed | ⚠️ | ✅ | ✅ |
| C-004 empty=success | ⚠️ | ✅ | ✅ |
| C-005 ineligible no-fallback | ⚠️ | ✅ | ✅ |
| Core classification location | node (post-stringify) | coordinator (typed) | n/a (B does it) |
| Tool-name dispatch stability | n/a | needs adapter | ✅ adapter is the mechanism |
| Module boundary | ❌ orchestration | ✅ `search/` | ✅ thin |
| Testability | ⚠️ | ✅ pure | ✅ thin |
| Complexity | Medium | Medium | Low (adapter) |

**Note (do not conflate):** REQ-007's rejected "validation in tool assembly" (ADR-001 §4 Option C) is a *different* problem (validation timing). REQ-008's C-adapter is *result routing*, not validation; it does not re-introduce REQ-007's rejected design.

**Recommendation (Proposed):** adopt **B as the fallback algorithm**, exposed through a **thin C adapter** as the single model-facing search tool. A is rejected (node bloat, late classification).

## 6. Open decisions D-1…D-8 (all unapproved)

| ID | Decision statement | Recommended | Alternatives | Consequences | REQ-007 dependency | Approval |
|---|---|---|---|---|---|---|
| D-1 | Load-time unavailability vs invocation-time failure boundary | Split: load→REQ-007 (fatal only if no other usable source); invocation→REQ-008 fallback | Treat all load failures as fallback-eligible | Changes POL-002 scope | U-1, U-5 | **Yes** |
| D-2 | Fallback config field name/placement/precedence/default | New opt-in ordered field default empty; `search_api` remains primary | Reuse `search_api` only; put on `MCPConfig` | Shared contract (§6) | none | **Yes** |
| D-3 | Eligible error classification signals | Typed classes + status code; substring only as documented fallback | Substring-only (rejected) | Taxonomy stability | none | **Yes** |
| D-4 | Unavailable MCP fallback: tried-and-failed vs not-attempted | Tried-and-failed, category `load_failed`, listed in C-003 | Exclude silently | C-003 completeness | **U-5** | **Yes** |
| D-5 | Hard dependency on structured `McpLoadResult` | Design depends on it; degrade to "unavailable" if U-5 deferred | Independent loader probing | Honesty of D-4 | U-5 | **Yes** |
| D-6 | Coordinator vs wrapper as exposed tool | B algorithm behind thin C adapter, stable name | B as tool directly | Dispatch/schema | U-4 (capability) | **Yes** |
| D-7 | All-failed representation | Distinct marker/typed field, never equals empty marker | Reuse generic error string | C-003 testability | INV-005 | **Yes** |
| D-8 | Missing auth config vs rejected credential | Missing config = stop (rule 6); rejected at invocation = fallback (rule 7) | Both fallback / both stop | Scope vs REQ-008 exclusion | POL-002 | **Yes** |

None approved; all recorded as Proposed in ADR-002 when drafted.

## 7. Drafting plan

### 7.1 Mermaid architecture

```mermaid
flowchart TD
  CFG[Configuration incl. ordered fallback list] --> VAL[REQ-007 static validation]
  VAL --> ASM[get_all_tools assembly]
  ASM --> MLOAD[MCP load -> McpLoadResult]
  MLOAD --> CAP{usable source exists?}
  CAP -- no --> ERR[explicit no-search error]
  CAP -- yes --> BIND[bind native + search tool]
  BIND --> MODEL[researcher model]
  MODEL --> TOOL[tool-facing adapter C: web_search]
  TOOL --> COORD[FallbackCoordinator B]
  COORD --> AD_T[Tavily adapter]
  COORD --> AD_M[MCP adapter]
  AD_T --> CLS[ErrorClassification]
  AD_M --> CLS
  CLS -- eligible & sources left --> COORD
  CLS -- ineligible --> OUT[return failure to model]
  CLS -- success/empty --> OUT
  CLS -- exhausted --> ALL[AllSourcesFailed -> distinct marker]
```

### 7.2 Interface contract table
As §3 (SearchRequest, SearchSource, SearchOutcome, SearchAttemptFailure, AllSourcesFailed, ErrorClassification, McpLoadResult bridge).

### 7.3 Error classification matrix
As §4.

### 7.4 Complete ADD comparison matrix
As §5 (A / B / C-as-adapter).

### 7.5 Proposed EVAL-002 decision text
- Module: search · Owner: sszfot · Decision recorded in ADR-002 · Status: **Open**
- ASR: REQ-008 C-001…C-005; ASR-008-01…08-11 (from Iteration 1)
- Candidates: A (researcher-level), B (coordinator), C (thin adapter over B, complementary)
- **Choice (Proposed):** B algorithm behind thin C adapter — typed classification before stringification, single module, offline-testable, preserves tool-name dispatch.
- Rejected: A (node bloat, post-stringify classification). Note C is not rejected but *combined* with B; REQ-007's Option-C rejection is a different concern (validation timing).

### 7.6 ADR-002 section-by-section outline
- §1 ASRs (REQ-008 + ASR-008-*) · §2 Context (`execute_tool_safely` stringification, `load_mcp_tools` `[]`, empty marker, native excluded, Tavily/MCP schema mismatch) · §3 Decision (B behind thin C adapter; typed contracts) · §4 Rejected (A; clarify C is complementary, distinct from REQ-007 §4) · §5 Components/Interfaces (§3 contracts) · §6 State none / runtime policy (new fallback POL + POL-002 amendment proposal) / INV-005 / deterministic boundary · §7 Error classification (§4) · §8 Result rendering (success/empty/all-failed) · §9 REQ-007 interaction (§2 amendments) · §10 Implementation steps · §11 Verification (case map) · §12 Risks/open D-1…D-8, rollback.

### 7.7 Exact changes to existing shared documents (planned, not made)
- `evaluation-table.md`: add EVAL-002.
- `adr/002-search-fallback.md`: new.
- `invariants.md`: refine INV-005 (REQ-008 empty/all-failed semantics) — keep Proposed.
- `runtime-policy-catalog.md`: add fallback policy at next free `POL-NNN` (POL-001 placeholder, POL-002 taken); propose conditional amendment to POL-002 (D-1/D-8).
- `trace-matrix.md`: fill REQ-008 row (ADR-002, POL, tests).
- `structural-constraints.md` §10 search: add fallback interface + adapter dependency direction.
- `verification-constraints.md` §7: add REQ-008 cases.

### 7.8 Proposed verification cases (Planned / Not Executed)
All **Planned — Not Executed**:

| TC | Covers | Case |
|---|---|---|
| TC-801 | C-001 | primary timeout → fallback result |
| TC-802 | C-002 | 3 sources, first two eligible-fail, third result |
| TC-803 | C-003 | all fail → aggregate lists each source+error, ≠ empty marker |
| TC-804 | C-004 | empty result → success, no fallback |
| TC-805 | C-005 | malformed query (ineligible) → returned, no fallback |
| TC-806 | D-3/D-4 | typed classification for Tavily/MCP without substring |
| TC-807 | D-4/D-5 | configured-but-unloadable MCP fallback recorded `load_failed`, listed |
| TC-808 | D-7 | all-failed marker distinct from empty marker |
| TC-809 | ASR-008-08 | no fallback configured → unchanged behaviour |
| TC-810 | D-8 | missing auth config → stop; rejected credential at invocation → fallback |

### 7.9 Unresolved questions for team discussion
- D-1 split (load vs invocation) — accept the POL-002 narrowing?
- D-2 field representation/precedence/default.
- D-3 typed-vs-substring policy and the Tavily generic-error gap.
- D-4/D-5 dependency on U-5; degrade behaviour if deferred.
- D-6 exposed tool name/schema (and effect on REQ-007 capability predicate).
- D-7 all-failed contract (string marker vs typed field) that C-003 tests.
- D-8 missing-auth vs rejected-credential boundary.
- Whether REQ-008 can be *verified* while U-5 remains open (likely partially blocked for D-4/D-5 cases).

---

**No files were modified.** Stopping for human review.

Two points need your steer before any drafting: (1) the **D-1** split — do you accept narrowing ADR-001 §9/POL-002 so an unloadable *fallback* MCP source is recorded rather than stopping the run, while a lone unusable source still stops? (2) **D-5** — should REQ-008 be documented as depending on the still-open REQ-007 U-5 loader change (honest for D-4 but couples the two requirements), or designed to degrade to "source unavailable" if U-5 is deferred?

---

## Message 186 — USER

Continue REQ-008 Software Architecture work.

Current branch: `docs/sa-search-fallback`.

Task: Draft EVAL-002 and ADR-002 based on ADD Iterations 1 and 2, incorporating the human review decisions below.

You may edit only:

- `docs/architecture/evaluation-table.md`
- `docs/architecture/adr/002-search-fallback.md`

Do not modify implementation code, tests, requirements, ADR-001, runtime policies, invariants, trace matrix, governance constraints, AI logs, or transcripts.

Do not commit or push.

## 1. Architecture selection

Use the following Proposed architecture:

- Option B: Dedicated Fallback Coordinator owns the fallback algorithm.
- A thin tool-facing adapter exposes the coordinator through a stable model-callable search tool.
- Per-source adapters translate normalized search requests to Tavily/MCP tool schemas.
- Error classification happens before exceptions are converted to strings.
- Successful and empty search outcomes are distinguished from errors.
- All eligible failures are aggregated with source-specific diagnostics.

Evaluate A, B, and C fairly, noting that a thin C-style adapter may complement B.

## 2. REQ-007 dependency

Document REQ-008's dependency on REQ-007 U-5 or an equivalent structured MCP load-result contract.

Do not silently degrade an unavailable MCP source to an empty tool list.

For D-1, propose a conditional revision of POL-002 allowing a failed fallback MCP source to be recorded without terminating the run when other validated, usable sources remain.

Keep this revision explicitly Pending Team Approval.

Do not edit ADR-001 or POL-002.

## 3. Failure semantics

Distinguish:

- Eligible invocation failure: attempt the next configured source.
- Ineligible invocation failure: terminate fallback immediately.
- Empty successful result: return success without fallback.
- All eligible sources exhausted: return AllSourcesFailed with every attempted source and its error.
- Source unavailable during loading: preserve a distinct load-stage diagnostic; behavior remains subject to D-1 approval.
- Missing required authentication configuration: configuration failure.
- Credential rejected during invocation: eligible fallback error, without automatic credential recovery.

Do not treat every error as AllSourcesFailed.

## 4. Error classification

Use explicit exception types, structured error codes, or documented status metadata.

Do not assume MCP errors always carry HTTP status codes.

Do not use generic error-message substring matching as an automatic fallback mechanism.

Unclassifiable errors should default to ineligible pending an explicit policy decision.

## 5. Interface contracts

Specify proposed interfaces for:

- SearchRequest
- SearchSource
- SearchOutcome
- SearchAttemptFailure
- SearchTerminatedFailure
- AllSourcesFailed
- ErrorClassification
- MCP load-result integration

Explain ownership, call boundaries, and model-facing rendering.

Treat interfaces as architectural proposals, not implemented code.

## 6. Traceability and verification

Map REQ-008 C-001 through C-005 to planned verification cases.

Inspect the existing verification-constraints numbering convention before proposing test IDs.

Do not claim that any tests have been written or executed.

## 7. Documentation requirements

For EVAL-002:

- Follow the actual EVAL-001 format.
- Compare alternatives and justify the provisional choice.
- Status: Open.
- Owner: sszfot.
- Reference ADR-002.

For ADR-002:

- Follow the actual ADR-001 and ADR template conventions.
- Status: Proposed.
- SA Review: Pending.
- Include context, ASRs, decision, alternatives, interfaces, execution flow, error policy, REQ-007 integration, risks, verification plan, and rollback.
- Explicitly list D-1 through D-8 as unresolved or conditionally recommended.
- Do not claim team approval.

## 8. Final validation

After editing, inspect the diff and report:

1. Files modified.
2. EVAL-002 summary.
3. ADR-002 summary.
4. Remaining open decisions.
5. Cross-document inconsistencies.
6. Any assumptions requiring confirmation.

Stop without committing or pushing.

---

## Message 187 — ASSISTANT

I'll verify the exact EVAL-001/ADR-001 format and the verification-constraints numbering before drafting.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '36,73p' docs/architecture/evaluation-table.md"}
output: **Choice:** <option> — <why it wins>.

**Rejected and why:** <option>: <reason>.

## EVAL-001: Where search configuration is validated before research

- **Module:** search
- **Owner:** sszfot
- **Decision recorded in:** ADR-001
- **Status:** Open (provisional selection of B; awaiting SA Review)

**ASR**

| Requirement | Acceptance criteria | Quality attributes at stake |
|---|---|---|
| REQ-007 | C-001, C-002, C-003, C-004, C-005 | correctness (fail before model/search calls), testability, modularity, behaviour preservation |

Architectural drivers (provisional IDs, see ADR-001 §1): ASR-007-01 validate on every path to a model/search call; ASR-007-02 native provider ↔ `research_model`; ASR-007-03 static MCP capability versus runtime availability; ASR-007-04 unsupported provider lists the supported set (including via `SEARCH_API`); ASR-007-05 pure and offline-testable; ASR-007-06 preserve valid behaviour and topology; ASR-007-07 documentation consistency; ASR-007-08 a statically declared but unusable MCP must not silently produce a no-search run; ASR-007-09 an explicit search-capability predicate replaces the tool-count check.

**Candidates**

| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |
|---|---|---|---|---|---|---|
| A | Validate at the top of the research graph entry node | `deep_researcher.py` (`clarify_with_user`) | Small; runs early | Violates the thin-node rule (`structural-constraints.md` §2.1); correctness depends on plac

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && awk '/^### search \\(REQ-007/{f=1} f' docs/code-governance/verification-constraints.md | grep -oE \"^\\| TC-[0-9]{3} \" | grep -oE \"TC-[0-9]{3}\" | sort | tail -5; echo \"=== last TC overall ===\"; grep -oE \"TC-[0-9]{3}\" docs/code-governance/verification-constraints.md | sort -u | tail -3"}
output: TC-022
TC-023
TC-024
TC-025
TC-026
=== last TC overall ===
TC-024
TC-025
TC-026


---

## Message 188 — ASSISTANT

REQ-007 uses TC-001–TC-026. To avoid collision, REQ-008 tests should start at TC-027 (the module example rows at lines 74-76 use TC-001/002/003 as placeholders only). Let me confirm the ADR template and ADR-001 §header/§13 conventions.

[tool: read | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/000-template.md"}
output: <path>[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/000-template.md</path>
<type>file</type>
<content>
1: # ADR-NNN: <Decision Title>
2:
3: > Copy this file to `NNN-<short-slug>.md` with the next free number (`001`, `002`, ...) and fill every section. Never reuse a number; a replaced decision is marked *Superseded* and links to its successor.
4:
5: - **Status:** Proposed | Accepted | Superseded by ADR-NNN | Rejected
6: - **Date:** YYYY-MM-DD
7: - **Module:** <module>
8: - **Owner:** <name>
9: - **Evaluation:** EVAL-NNN (`docs/architecture/evaluation-table.md`)
10: - **SA Review:** SA-NNN (`docs/review-memo.md`), at acceptance
11:
12: ## 1. Architecturally Significant Requirements
13:
14: | Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |
15: |---|---|---|
16: | REQ-NNN | C-NNN, M-NNN | |
17:
18: ## 2. Context
19:
20: The problem, the forces and constraints, and the baseline behaviour being changed (file and line).
21:
22: ## 3. Decision
23:
24: The chosen option, stated so that a coding agent can implement it without guessing.
25:
26: ## 4. Rejected Options
27:
28: | Option | Reason for rejection |
29: |---|---|
30: | | |
31:
32: The full comparison is in EVAL-NNN.
33:
34: ## 5. Components and Interfaces
35:
36: | Component | Responsibility | Interface (signature or type) | Called by |
37: |---|---|---|---|
38: | | | | |
39:
40: Shared contracts changed (`structural-constraints.md` §6): none | list

---

## Message 189 — ASSISTANT

Now I'll append EVAL-002 to the evaluation table (following EVAL-001 format exactly), then create ADR-002.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && tail -5 docs/architecture/evaluation-table.md; echo \"=== line count ===\"; wc -l docs/architecture/evaluation-table.md"}
output: - `structural-constraints.md` §2 (thin nodes) and §5 (dependency direction).

**Choice:** B — the only option that validates before every model/search call on all paths while keeping validation pure, single-responsibility, offline-testable and inside the `search/` module boundary (provisional; pending SA Review).

**Rejected and why:** A — breaks the thin-node rule and is placement-fragile. C — validates too late (after the clarification and brief model calls) and couples validation to tool assembly and REQ-008.
=== line count ===
      79 docs/architecture/evaluation-table.md


---

## Message 190 — ASSISTANT

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && cat >> docs/architecture/evaluation-table.md <<'EOF'\n\n## EVAL-002: Where ordered search fallback is executed on failure\n\n- **Module:** search\n- **Owner:** sszfot\n- **Decision recorded in:** ADR-002\n- **Status:** Open (provisional selection of B with a thin C-style tool adapter; awaiting SA Review)\n\n**ASR**\n\n| Requirement | Acceptance criteria | Quality attributes at stake |\n|---|---|---|\n| REQ-008 | C-001, C-002, C-003, C-004, C-005 | correctness (ordered fallback, explicit failure), testability, modularity, behaviour preservation |\n\nArchitectural drivers (provisional IDs, see ADR-002 §1): ASR-008-01 ordered fallback over Tavily/MCP sources; ASR-008-02 eligible-vs-ineligible classification gates fallback; ASR-008-03 empty result is success and suppresses fallback; ASR-008-04 all-sources-failed is explicit and lists each source; ASR-008-05 a success is used identically regardless of source; ASR-008-06 fallback operates only on client-side sources (native excluded); ASR-008-07 error classification is deterministic and offline-testable; ASR-008-08 with no fallback configured, behaviour is unchanged; ASR-008-09 fallback does not depend on unapproved REQ-007 decisions; ASR-008-10 a configured-but-unloadable MCP source is represented deterministically; ASR-008-11 the fallback path exposes one stable model-callable search tool.\n\n**Candidates**\n\n| Option | Summary | Components touched | Pros | Cons | Complexity | Offline testability |\n|---|---|---|---|---|---|---|\n| A | Researcher-level fallback: `execute_tool_safely`/`researcher_tools` loops over sources on exception | `deep_researcher.py` (`execute_tool_safely`, `researcher_tools`) | Small change in one node | Puts the fallback loop and classification in the orchestration node, violating the thin-node rule (`structural-constraints.md` §2.1); classification happens after `execute_tool_safely` has flattened the exception to a string (`deep_re
output: appended
**Choice:** B with a thin C-style tool adapter — the coordinator owns the fallback algorithm and classifies typed errors before they are stringified, while a thin adapter exposes it as one stable model-callable search tool (provisional; pending SA Review).

**Rejected and why:** A — puts fallback and classification in the orchestration node and classifies after the exception is already a string. C as a standalone — it only routes results; it does not decide ordering, classification or aggregation, so it complements B rather than replacing it.


---

## Message 191 — ASSISTANT

Now create ADR-002 following the template and ADR-001 conventions.

[tool: write | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "content": "# ADR-002: Ordered Search Fallback Through a Dedicated Coordinator\n\n- **Status:** Proposed\n- **Date:** 2026-11-13\n- **Module:** search\n- **Owner:** sszfot\n- **Evaluation:** EVAL-002 (`docs/architecture/evaluation-table.md`)\n- **SA Review:** pending (no `SA-NNN` recorded)\n\n> This decision is *Proposed*. It is not approved until SA Review accepts it (`Prompt.md` §4, Gate 1). Nothing below is implemented. Decisions still open for the team are listed in §12. REQ-008 depends on REQ-007, which is itself still Proposed (ADR-001); this ADR does not assume ADR-001 has been approved.\n\n## 1. Architecturally Significant Requirements\n\n| Requirement | Acceptance criteria that shape this decision | Why they matter architecturally |\n|---|---|---|\n| REQ-008 | C-001, C-002, C-003, C-004, C-005 | Ordered fallback, eligible-vs-ineligible gating, empty-is-success and an explicit all-failed failure fix where the loop, the classification and the aggregation live, and what the researcher receives. |\n| REQ-007 (dependency) | U-5 / structured MCP load result | Distinguishing a source that could not be loaded from one that returned nothing needs the structured load result; without it the load-stage outcome is unrecoverable. |\n\nArchitectural drivers (ASR), provisional IDs used consistently across EVAL-002, this ADR and the module section:\n\n| ID | Statement |\n|---|---|\n| ASR-008-01 | The system tries a configured ordered list of Tavily/MCP sources, next source on eligible failure, until one succeeds (C-001, C-002). |\n| ASR-008-02 | Eligible errors (timeout, connection failure, rate limit, provider server error, rejected credential) trigger fallback; ineligible errors return without fallback (C-001, C-002, C-005). |\n| ASR-008-03 | A search that returns no hits is a success and does not trigger fallback (C-004). |\n| ASR-008-04 | When every source fails, the
output: Wrote file successfully.

---

## Message 192 — ASSISTANT

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && git diff --check && echo \"DIFF_CHECK_CLEAN\"; echo \"=== status ===\"; git status --short; echo \"=== stat ===\"; git diff --stat; echo \"=== EVAL-002 present ===\"; grep -c \"^## EVAL-002\" docs/architecture/evaluation-table.md; echo \"=== ADR-002 sections ===\"; grep -nE \"^## |^# ADR\" docs/architecture/adr/002-search-fallback.md | head -20"}
output: DIFF_CHECK_CLEAN
=== status ===
 M docs/architecture/evaluation-table.md
?? docs/architecture/adr/002-search-fallback.md
=== stat ===
 docs/architecture/evaluation-table.md | 42 +++++++++++++++++++++++++++++++++++
 1 file changed, 42 insertions(+)
=== EVAL-002 present ===
1
=== ADR-002 sections ===
1:# ADR-002: Ordered Search Fallback Through a Dedicated Coordinator
12:## 1. Architecturally Significant Requirements
35:## 2. Context
48:## 3. Decision
61:## 4. Rejected Options
70:## 5. Components and Interfaces
95:## 6. State, Failure Handling and Deterministic Boundary
116:## 7. Error Classification
136:## 8. Integration with REQ-007
147:## 9. Consequences, Risks, Assumptions, Unresolved Decisions and Rollback
167:## 10. Implementation Steps
181:## 11. Verification
199:## 12. Modules and Documents to Update at Integration


---

## Message 193 — ASSISTANT

Both files are in place. Let me confirm ADR-002 is counted (untracked) and the ADR template sections are all present, and verify no other files changed.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && echo \"=== all changed/untracked ===\"; git status --porcelain; echo \"=== ADR-002 line count ===\"; wc -l docs/architecture/adr/002-search-fallback.md; echo \"=== status field ===\"; head -10 docs/architecture/adr/002-search-fallback.md"}
output: === all changed/untracked ===
 M docs/architecture/evaluation-table.md
?? docs/architecture/adr/002-search-fallback.md
=== ADR-002 line count ===
     201 docs/architecture/adr/002-search-fallback.md
=== status field ===
# ADR-002: Ordered Search Fallback Through a Dedicated Coordinator

- **Status:** Proposed
- **Date:** 2026-11-13
- **Module:** search
- **Owner:** sszfot
- **Evaluation:** EVAL-002 (`docs/architecture/evaluation-table.md`)
- **SA Review:** pending (no `SA-NNN` recorded)

> This decision is *Proposed*. It is not approved until SA Review accepts it (`Prompt.md` §4, Gate 1). Nothing below is implemented. Decisions still open for the team are listed in §12. REQ-008 depends on REQ-007, which is itself still Proposed (ADR-001); this ADR does not assume ADR-001 has been approved.


---

## Message 194 — ASSISTANT

Only the two permitted files changed. Reporting results.

## 1. Files modified
- `docs/architecture/evaluation-table.md` (modified — appended EVAL-002; EVAL-001 untouched)
- `docs/architecture/adr/002-search-fallback.md` (new)

No other files touched (no ADR-001, POL-002, invariants, trace matrix, governance constraints, code, tests, requirements, AI logs, transcripts).

## 2. EVAL-002 summary
Follows EVAL-001's exact format: Module `search` · Owner `sszfot` · Decision in ADR-002 · **Status Open**. ASR table (REQ-008 C-001–C-005) plus ASR-008-01…08-11. Candidates A (researcher-level), B (coordinator), C (thin adapter over B). Choice: **B with a thin C-style adapter** (provisional). Includes an explicit "Option C is not a competing algorithm" clarification distinguishing it from REQ-007's rejected validation-in-tool-assembly option, an MCP load-result dependency note (U-5), and file:line evidence.

## 3. ADR-002 summary
Follows template + ADR-001 conventions, **Status Proposed**, **SA Review pending**, 12 sections: ASRs; Context (execute_tool_safely stringification, tools_by_name dispatch, empty marker `utils.py:127`, Tavily/MCP schema mismatch, `-32003` rewrite, `load_mcp_tools` `[]`); Decision (coordinator + thin tool adapter, classify before stringification); Rejected (A; C-standalone, with the REQ-007 distinction); Components/Interfaces (SearchRequest, SearchSource, SearchOutcome, SearchAttemptFailure, SearchTerminatedFailure, AllSourcesFailed, ErrorClassification, MCP load-result integration) with ownership/call-boundary/rendering notes; State/Failure (the explicit failure-semantics table separating eligible/ineligible/empty/exhausted/load-stage/auth-config/credential-rejected); Error Classification matrix (typed Tavily exceptions + MCP `McpError.code` + status metadata; unclassifiable → ineligible; no generic substring matching); REQ-007 integration (load vs invocation split, **POL-002 conditional revision Pending Team Approval**, ADR-001/POL-002 not edited); Risks; D-1…D-8 all Open/conditional; Implementation steps; Verification (planned, not executed); Integration/rollback.

## 4. Remaining open decisions
- **D-1** (Open, conditionally recommended): load-vs-invocation split + POL-002 narrowing for multi-source fallback.
- **D-2** fallback config field (name/placement/precedence/default empty).
- **D-3** typed classification policy incl. Tavily generic-error gap; unclassifiable → ineligible.
- **D-4** unloadable MCP fallback recorded `load_failed` vs excluded.
- **D-5** dependency on REQ-007 U-5 structured load result (no silent degradation).
- **D-6** coordinator-behind-thin-adapter + stable tool name.
- **D-7** all-failed rendering distinct from empty marker.
- **D-8** missing-auth-config (stop) vs rejected-credential-at-invocation (fallback).

All are marked unapproved; none claimed.

## 5. Cross-document inconsistencies (noted, not edited)
- ADR-002 §11 reports test IDs as `TC-…` are *planned* and points to `verification-constraints.md` §7, which does **not** yet contain them (that file was out of this task's scope). The trace-matrix REQ-008 row remains `TBD`. Both are expected until the module-section task.
- REQ-008's `verification` field in `requirements.yaml` names `test_search_fallback.py::test_*` — ADR-002 uses those exact names for the five criteria, consistent.
- ADR-001 §9 / POL-002 still state unconditional "stop"; ADR-002 documents the **proposed** conditional revision without editing them, so the two documents currently differ by design — flagged as D-1, pending approval.
- ADR-001 trace row cites "TC-001–TC-025" while the body has 26 IDs; pre-existing, unrelated to this task.

## 6. Assumptions requiring confirmation
- Test-ID numbering continues **after TC-026** to avoid the REQ-007 collision (planned, to be finalized in `verification-constraints.md`).
- The exposed search tool keeps a base name compatible with `tools_by_name` (exact name is D-6).
- `execute_tool_safely` is excluded from the classification path; classification runs inside the coordinator.
- Fallback list contains only Tavily and configured MCP sources; native search excluded.

`git diff --check`: **CLEAN**. Nothing committed or pushed. Stopping for human review.

---

## Message 195 — USER

Perform a focused consistency repair of REQ-008 EVAL-002 and ADR-002.

Current branch: `docs/sa-search-fallback`.

Edit only:
- `docs/architecture/evaluation-table.md`
- `docs/architecture/adr/002-search-fallback.md`

Do not modify other files. Do not commit or push.

Required corrections:

1. Replace ASR-008-09 in both documents. REQ-008 explicitly depends on REQ-007, especially U-5. State that this dependency must be tracked and that unapproved REQ-007 decisions cannot be treated as implemented guarantees.

2. Correct the FallbackCoordinator.run return contract to include:
   - SearchOutcome
   - SearchTerminatedFailure
   - AllSourcesFailed

3. Correct ADR-002 §11 so it does not claim that REQ-008 verification cases already exist in verification-constraints.md. Mark them Planned / Not Implemented / Not Executed.

4. Verify the ADR creation date. Use 2026-11-17 unless repository conventions require another date.

5. Clarify how an empty fallback configuration preserves existing single-source behavior. Distinguish architectural intent from verified implementation behavior.

6. Add a stage distinction (load vs invoke) to SearchAttemptFailure or an equivalent failure record. Explain how an unavailable MCP source is represented without falsely claiming that its search tool was invoked.

7. Ensure D-1 and D-5 remain explicitly pending team approval. Do not change ADR-001 or POL-002.

8. Check that the EVAL-002 and ADR-002 terminology, interfaces, ASR identifiers, and cross-references agree.

After editing, run read-only validation commands including `git diff --check` and `git status --short`.

Report the exact corrections and remaining unresolved decisions.

Do not expand the scope or start implementation.

---

## Message 196 — ASSISTANT

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"ASR-008-09\\|SearchTerminatedFailure\\|AllSourcesFailed\\|FallbackCoordinator\\|Date:\\|2026-11-13\\|Planned\\|not executed\\|not been written\\|§11\" docs/architecture/adr/002-search-fallback.md docs/architecture/evaluation-table.md"}
output: docs/architecture/adr/002-search-fallback.md:4:- **Date:** 2026-11-13
docs/architecture/adr/002-search-fallback.md:31:| ASR-008-09 | Fallback does not depend on unapproved REQ-007 decisions; it must behave correctly whether or not ADR-001 is accepted. |
docs/architecture/adr/002-search-fallback.md:54:3. **Coordinate in order.** `FallbackCoordinator` iterates the configured sources in order, **classifying each failure before any exception becomes a string** (`execute_tool_safely` is never in the classification path).
docs/architecture/adr/002-search-fallback.md:55:4. **Distinguish outcomes.** A success returns its result; an empty result is a success; an ineligible failure terminates fallback immediately and is returned; only when every eligible source is exhausted is `AllSourcesFailed` produced.
docs/architecture/adr/002-search-fallback.md:78:| `search/fallback.py` (new) | Ordered attempt loop, classification, result normalisation, all-failed aggregation. Pure over injected `SearchSource`s. | `class FallbackCoordinator: async def run(req: SearchRequest, sources: Sequence[SearchSource]) -> SearchOutcome \| AllSourcesFailed` | Tool-facing adapter |
docs/architecture/adr/002-search-fallback.md:79:| `search/errors.py` (new) | Typed outcomes and classification. | `SearchOutcome(found: bool, content: str, source_name: str)`; `SearchAttemptFailure(source_name: str, classification: ErrorClassification, detail: str)`; `SearchTerminatedFailure(failure: SearchAttemptFailure)`; `AllSourc

---

## Message 197 — ASSISTANT

Now I'll apply the corrections. **Correction 1** — ASR-008-09 in both files.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "oldString": "| ASR-008-09 | Fallback does not depend on unapproved REQ-007 decisions; it must behave correctly whether or not ADR-001 is accepted. |", "newString": "| ASR-008-09 | REQ-008 explicitly depends on REQ-007 (especially U-5, the structured MCP load result); that dependency must be tracked, and unapproved REQ-007 decisions must not be treated as implemented guarantees. |"}
output: Edit applied successfully.

---

## Message 198 — ASSISTANT

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/evaluation-table.md", "oldString": "ASR-008-08 with no fallback configured, behaviour is unchanged; ASR-008-09 fallback does not depend on unapproved REQ-007 decisions; ASR-008-10 a configured-but-unloadable MCP source is represented deterministically; ASR-008-11 the fallback path exposes one stable model-callable search tool.", "newString": "ASR-008-08 with no fallback configured, behaviour is unchanged; ASR-008-09 REQ-008 explicitly depends on REQ-007 (especially U-5), the dependency is tracked and unapproved REQ-007 decisions are not treated as implemented guarantees; ASR-008-10 a configured-but-unloadable MCP source is represented deterministically; ASR-008-11 the fallback path exposes one stable model-callable search tool."}
output: Edit applied successfully.

---

## Message 199 — ASSISTANT

**Correction 2** — FallbackCoordinator.run return contract to include all three.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "oldString": "| `search/fallback.py` (new) | Ordered attempt loop, classification, result normalisation, all-failed aggregation. Pure over injected `SearchSource`s. | `class FallbackCoordinator: async def run(req: SearchRequest, sources: Sequence[SearchSource]) -> SearchOutcome \\| AllSourcesFailed` | Tool-facing adapter |", "newString": "| `search/fallback.py` (new) | Ordered attempt loop, classification, result normalisation, all-failed aggregation. Pure over injected `SearchSource`s. | `class FallbackCoordinator: async def run(req: SearchRequest, sources: Sequence[SearchSource]) -> SearchOutcome \\| SearchTerminatedFailure \\| AllSourcesFailed` | Tool-facing adapter |"}
output: Edit applied successfully.

---

## Message 200 — ASSISTANT

**Correction 3** — §11 not claiming cases exist.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "oldString": "Cases are listed in the `search` module section of `verification-constraints.md` §7 and are **planned, not executed**. IDs continue after REQ-007's `TC-026` to avoid collision (module example rows TC-001…TC-003 are placeholders, not real cases).", "newString": "The cases below are **Planned / Not Implemented / Not Executed**. They do **not** yet exist in `verification-constraints.md` §7 or in any test file; this ADR only proposes them. IDs are proposed to continue after REQ-007's `TC-026` to avoid collision (the module example rows TC-001…TC-003 are placeholders, not real cases)."}
output: Edit applied successfully.

---

## Message 201 — ASSISTANT

**Correction 4** — date.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "oldString": "- **Date:** 2026-11-13", "newString": "- **Date:** 2026-11-17"}
output: Edit applied successfully.

---

## Message 202 — ASSISTANT

**Correction 5** — empty-config preservation: architectural intent vs verified behavior. Let me read the ASR-008-08 and decision area.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"ASR-008-08\\|no fallback configured\\|default empty\\|opt-in\\|baseline behaviour preserved\" docs/architecture/adr/002-search-fallback.md"}
output: 30:| ASR-008-08 | With no fallback configured, behaviour is unchanged (today's single-source error path). |
157:- **D-2 (Open):** Fallback configuration field — name, placement (`Configuration` vs `MCPConfig`), precedence vs `search_api`, default empty (opt-in). Recommended default empty; requires shared-contract approval.
165:- **Rollback:** remove the fallback coordinator, adapters and tool adapter, and the configuration field; with the field default empty, baseline behaviour is restored.
174:4. Add the ordered fallback configuration field (D-2), default empty, with `x_oap_ui_config` metadata; baseline behaviour preserved when empty.
194:| ASR-008-08 | no fallback configured → unchanged behaviour | `::test_no_fallback_configuration_preserved` |


---

## Message 203 — ASSISTANT

Let me find the Decision section point 5 area to add the empty-config clarification.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '48,60p' docs/architecture/adr/002-search-fallback.md"}
output: ## 3. Decision

Adopt a **dedicated fallback coordinator** in the `search` module that owns the fallback algorithm, exposed to the researcher through a **thin tool-facing adapter**:

1. **Normalise the request.** One `SearchRequest` (queries, limits, topic) is the provider-agnostic input.
2. **Adapt per source.** Each Tavily/MCP source has an adapter that translates a `SearchRequest` into that source's native schema and maps native results and exceptions back to the typed contracts. Sources are not assumed schema-compatible.
3. **Coordinate in order.** `FallbackCoordinator` iterates the configured sources in order, **classifying each failure before any exception becomes a string** (`execute_tool_safely` is never in the classification path).
4. **Distinguish outcomes.** A success returns its result; an empty result is a success; an ineligible failure terminates fallback immediately and is returned; only when every eligible source is exhausted is `AllSourcesFailed` produced.
5. **Expose as one tool.** A thin adapter registers the coordinator as the single model-callable search tool under a stable name, so `tools_by_name` dispatch (`deep_researcher.py:468-471`) is unchanged.
6. **Consume the structured MCP load result.** The coordinator receives availability from the MCP load result rather than inferring it from an empty tool list.

Do not change the graph topology or state. Do not substitute native model search. Keep REQ-007 validation separate (this ADR does not perform or rep

---

## Message 204 — ASSISTANT

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "oldString": "Do not change the graph topology or state. Do not substitute native model search. Keep REQ-007 validation separate (this ADR does not perform or replace configuration validation). The MCP load-result contract is a dependency (see §2, §9, and REQ-007 U-5).", "newString": "Do not change the graph topology or state. Do not substitute native model search. Keep REQ-007 validation separate (this ADR does not perform or replace configuration validation). The MCP load-result contract is a dependency (see §2, §9, and REQ-007 U-5).\n\n**Empty fallback configuration (intent vs evidence).** The architectural *intent* is that an empty (or absent) fallback list preserves today's single-source behaviour exactly: one search source, and on failure the current error path through `execute_tool_safely` (`deep_researcher.py:427-432`) is unchanged (ASR-008-08). This is **architectural intent only, not verified behaviour**: it is not yet implemented, and it must be confirmed by the planned regression case `::test_no_fallback_configuration_preserved` (§11) before it can be claimed. Until that case runs and passes, no statement here should be read as proving backward compatibility."}
output: Edit applied successfully.

---

## Message 205 — ASSISTANT

**Correction 6** — add stage distinction (load vs invoke) to `SearchAttemptFailure`. Update the interface and the contract-details explanation.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "oldString": "| `search/errors.py` (new) | Typed outcomes and classification. | `SearchOutcome(found: bool, content: str, source_name: str)`; `SearchAttemptFailure(source_name: str, classification: ErrorClassification, detail: str)`; `SearchTerminatedFailure(failure: SearchAttemptFailure)`; `AllSourcesFailed(failures: list[SearchAttemptFailure])`; `ErrorClassification(eligible: bool, category: str)` | Coordinator |", "newString": "| `search/errors.py` (new) | Typed outcomes and classification. | `SearchOutcome(found: bool, content: str, source_name: str)`; `SearchAttemptFailure(source_name: str, stage: FailureStage, classification: ErrorClassification, detail: str)` where `FailureStage ∈ {LOAD, INVOKE}`; `SearchTerminatedFailure(failure: SearchAttemptFailure)`; `AllSourcesFailed(failures: list[SearchAttemptFailure])`; `ErrorClassification(eligible: bool, category: str)` | Coordinator |"}
output: Edit applied successfully.

---

## Message 206 — ASSISTANT

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "oldString": "- `SearchAttemptFailure` — recorded per attempted source; `classification` decides whether to continue.", "newString": "- `SearchAttemptFailure` — recorded per attempted source; `classification` decides whether to continue. Its `stage` field distinguishes a **load-stage** failure (`LOAD`) from an **invocation-stage** failure (`INVOKE`). A source unavailable at load time is recorded with `stage=LOAD` and its `detail` naming the load cause; this explicitly records that the source's search tool was **never invoked**, so it must not be presented as an invocation error. An invocation error is recorded with `stage=INVOKE` after `invoke` actually raised. Both stages still appear in `AllSourcesFailed`, tagged by `stage`, so the aggregate never falsely claims an unavailable source was called."}
output: Edit applied successfully.

---

## Message 207 — ASSISTANT

Also update the failure-semantics table row for load stage to reference the `stage=LOAD` record precisely.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"Source unavailable during loading\" docs/architecture/adr/002-search-fallback.md"}
output: 112:| Source unavailable during loading | Preserve a distinct load-stage diagnostic (`category=load_failed`); the run-terminating decision is **subject to D-1 approval**. |


---

## Message 208 — ASSISTANT

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "oldString": "| Source unavailable during loading | Preserve a distinct load-stage diagnostic (`category=load_failed`); the run-terminating decision is **subject to D-1 approval**. |", "newString": "| Source unavailable during loading | Record `SearchAttemptFailure(stage=LOAD, category=load_failed)` naming the load cause; the source's search tool was never invoked. The run-terminating decision is **subject to D-1 approval**. |"}
output: Edit applied successfully.

---

## Message 209 — ASSISTANT

**Correction 7** — confirm D-1 and D-5 remain pending approval (already worded as Open; verify). Then **Correction 8** — cross-reference consistency between EVAL-002 and ADR-002.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"D-1 \\|D-5 \\|D-1 (\\|D-5 (\" docs/architecture/adr/002-search-fallback.md"}
output: 112:| Source unavailable during loading | Record `SearchAttemptFailure(stage=LOAD, category=load_failed)` naming the load cause; the source's search tool was never invoked. The run-terminating decision is **subject to D-1 approval**. |
158:- **D-1 (Open; conditionally recommended):** Split load-stage (REQ-007) from invocation-stage (REQ-008) failures; narrow POL-002 so an unloadable fallback MCP source is recorded, not run-terminating, when other usable sources remain. Requires team approval.
162:- **D-5 (Open):** Hard dependency on REQ-007 U-5 structured load result (or equivalent); no silent degradation to an empty tool list. Requires approval of the dependency.


---

## Message 210 — ASSISTANT

D-1 and D-5 already say "Open"/"Requires approval". Good. Now check cross-document agreement of ASR-008-09 text, and verify the EVAL-002 candidate/interfaces terminology matches ADR-002.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && echo \"=== ASR-008-09 EVAL vs ADR ===\"; grep -n \"ASR-008-09\" docs/architecture/evaluation-table.md docs/architecture/adr/002-search-fallback.md; echo \"=== return contract ===\"; grep -n \"SearchOutcome \\\\\\\\| SearchTerminatedFailure\\|SearchTerminatedFailure \\\\\\\\| AllSourcesFailed\" docs/architecture/adr/002-search-fallback.md | head"}
output: === ASR-008-09 EVAL vs ADR ===
docs/architecture/evaluation-table.md:94:Architectural drivers (provisional IDs, see ADR-002 §1): ASR-008-01 ordered fallback over Tavily/MCP sources; ASR-008-02 eligible-vs-ineligible classification gates fallback; ASR-008-03 empty result is success and suppresses fallback; ASR-008-04 all-sources-failed is explicit and lists each source; ASR-008-05 a success is used identically regardless of source; ASR-008-06 fallback operates only on client-side sources (native excluded); ASR-008-07 error classification is deterministic and offline-testable; ASR-008-08 with no fallback configured, behaviour is unchanged; ASR-008-09 REQ-008 explicitly depends on REQ-007 (especially U-5), the dependency is tracked and unapproved REQ-007 decisions are not treated as implemented guarantees; ASR-008-10 a configured-but-unloadable MCP source is represented deterministically; ASR-008-11 the fallback path exposes one stable model-callable search tool.
docs/architecture/adr/002-search-fallback.md:31:| ASR-008-09 | REQ-008 explicitly depends on REQ-007 (especially U-5, the structured MCP load result); that dependency must be tracked, and unapproved REQ-007 decisions must not be treated as implemented guarantees. |
=== return contract ===
80:| `search/fallback.py` (new) | Ordered attempt loop, classification, result normalisation, all-failed aggregation. Pure over injected `SearchSource`s. | `class FallbackCoordinator: async def run(req: SearchRequest, sources: Sequence

---

## Message 211 — ASSISTANT

EVAL-002 and ADR-002 agree on ASR-008-09 and interface terminology. Let me also confirm the "Source unavailable" stage distinction is consistent with the SearchSource `load_status` note, and that the EVAL-002 MCP note aligns. Then run validation.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"load_status\\|U-5\\|no silent\\|degrade\" docs/architecture/evaluation-table.md | tail -5; echo \"=== diag ===\"; grep -n \"load_failed\\|stage=LOAD\\|never invoked\" docs/architecture/adr/002-search-fallback.md"}
output: 65:**MCP runtime note (affects all options).** The split between static declaration and runtime availability is the same for every option; only the placement of the runtime stop-and-error check differs (Option B places it in `researcher` after assembly). The current `load_mcp_tools` returns a single `[]` for connection failure, zero usable tools, and missing authentication (`utils.py:470-504`), so none of these options can distinguish the runtime outcomes without an adapter or a return-contract change (ADR-001 §8.1a, U-5). This is an implementation dependency of the accepted direction, not a property of the existing code.
94:Architectural drivers (provisional IDs, see ADR-002 §1): ASR-008-01 ordered fallback over Tavily/MCP sources; ASR-008-02 eligible-vs-ineligible classification gates fallback; ASR-008-03 empty result is success and suppresses fallback; ASR-008-04 all-sources-failed is explicit and lists each source; ASR-008-05 a success is used identically regardless of source; ASR-008-06 fallback operates only on client-side sources (native excluded); ASR-008-07 error classification is deterministic and offline-testable; ASR-008-08 with no fallback configured, behaviour is unchanged; ASR-008-09 REQ-008 explicitly depends on REQ-007 (especially U-5), the dependency is tracked and unapproved REQ-007 decisions are not treated as implemented guarantees; ASR-008-10 a configured-but-unloadable MCP source is represented deterministically; ASR-008-11 the fallback path exposes one

---

## Message 212 — ASSISTANT

All corrections applied and cross-consistent. Now run validation and confirm only the two permitted files changed.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && git diff --check && echo \"DIFF_CHECK_CLEAN\"; echo \"=== status --short ===\"; git status --short; echo \"=== stat ===\"; git diff --stat; echo \"=== date ===\"; grep -n \"Date:\" docs/architecture/adr/002-search-fallback.md"}
output: DIFF_CHECK_CLEAN
=== status --short ===
 M docs/architecture/evaluation-table.md
?? docs/architecture/adr/002-search-fallback.md
=== stat ===
 docs/architecture/evaluation-table.md | 42 +++++++++++++++++++++++++++++++++++
 1 file changed, 42 insertions(+)
=== date ===
4:- **Date:** 2026-11-17


---

## Message 213 — ASSISTANT

All eight corrections are applied to only the two permitted files. (ADR-002 is untracked from the prior step, so `git diff --stat` counts only the tracked EVAL table; both are confirmed present.)

## Exact corrections made

1. **ASR-008-09 replaced (both files).** Now: "REQ-008 explicitly depends on REQ-007 (especially U-5, the structured MCP load result); that dependency must be tracked, and unapproved REQ-007 decisions must not be treated as implemented guarantees." EVAL-002 driver list and ADR-002 §1 row agree.
2. **`FallbackCoordinator.run` return contract** (§5) now: `-> SearchOutcome | SearchTerminatedFailure | AllSourcesFailed`.
3. **ADR §11** no longer implies existing cases: now states cases are **Planned / Not Implemented / Not Executed**, do **not** yet exist in `verification-constraints.md` §7 or any test file, IDs proposed after `TC-026`.
4. **Date** changed `2026-11-13` → **`2026-11-17`**.
5. **Empty-config clarification added** to §3 Decision: architectural intent vs verified behaviour — intent is single-source preservation; not implemented and must be confirmed by planned `::test_no_fallback_configuration_preserved` before being claimed.
6. **Stage distinction added:** `SearchAttemptFailure(..., stage: FailureStage ∈ {LOAD, INVOKE}, ...)`; explained that a load-stage failure records the source was **never invoked**, and `AllSourcesFailed` tags each entry by stage so it never falsely claims an unavailable source was called. Failure-semantics table row updated to `stage=LOAD, category=load_failed`.
7. **D-1 and D-5 remain Open / "Requires team approval."** ADR-001 and POL-002 not edited (only referenced as a pending conditional revision).
8. **Cross-reference check:** ASR-008-09, interface names (`SearchRequest`, `SearchSource`, `SearchOutcome`, `SearchAttemptFailure`, `SearchTerminatedFailure`, `AllSourcesFailed`, `ErrorClassification`), and the U-5 dependency note agree between EVAL-002 and ADR-002.

## Remaining unresolved decisions
- D-1 load-vs-invocation split / POL-002 narrowing — **Pending team approval**.
- D-2 fallback config field representation/precedence/default.
- D-3 typed classification policy (Tavily generic-error gap; unclassifiable→ineligible).
- D-4 unloadable MCP source recorded vs excluded (now carries `stage=LOAD`; final policy pending).
- D-5 dependency on REQ-007 U-5 — **Pending team approval**.
- D-6 coordinator-behind-thin-adapter + stable tool name.
- D-7 all-failed rendering distinct from empty marker.
- D-8 missing-auth-config vs rejected-credential boundary.

## Validation
- `git diff --check`: **CLEAN**
- `git status --short`: only `M docs/architecture/evaluation-table.md` and `?? docs/architecture/adr/002-search-fallback.md`
- No other files modified; nothing committed or pushed. Scope not expanded.

---

## Message 214 — USER

Continue REQ-008 Software Architecture documentation integration.

Current branch: `docs/sa-search-fallback`.

EVAL-002 and ADR-002 have been drafted and consistency-repaired.

Task: Integrate the proposed REQ-008 architecture into the existing shared architecture and code-governance documents.

Read the actual current repository files before making changes.

You may edit only:

- `docs/architecture/invariants.md`
- `docs/architecture/runtime-policy-catalog.md`
- `docs/architecture/trace-matrix.md`
- `docs/code-governance/structural-constraints.md`
- `docs/code-governance/verification-constraints.md`

Do not edit EVAL-002 or ADR-002 in this task. Report any inconsistencies requiring changes to them instead.

Do not modify source code, tests, requirements, ADR-001, AI logs, or transcripts.

Do not commit or push.

## 1. Invariants

Inspect the existing INV-005 and all other search-related invariants.

Preserve the required fields:

- statement
- source requirement ID
- enforcing component
- verification method
- operational fallback

Do not silently change the meaning of an existing REQ-007 invariant.

Add REQ-008-specific invariants only where they express non-negotiable behavior, including:

- No fallback after an empty successful result.
- No fallback after an ineligible error.
- Configured source order must be preserved.
- All eligible sources exhausted must produce an explicit failure.

Use the next available invariant IDs after inspecting the file.

Mark new invariants Proposed.

## 2. Runtime policy

Add a proposed REQ-008 runtime fallback policy using the next available POL identifier.

Specify:

- Trigger conditions.
- Eligible and ineligible failures.
- Ordered retry behavior.
- Empty-result semantics.
- All-failed reporting.
- Load-stage vs invocation-stage distinction.
- Missing authentication configuration vs rejected credential at invocation.

Do not silently amend POL-002.

Record the proposed multi-source exception to POL-002 as Pending Team Approval, cross-referencing ADR-002 D-1 and REQ-007 U-1.

## 3. Trace matrix

Update the REQ-008 row to reference:

- ADR-002
- EVAL-002
- New REQ-008 invariants
- Proposed runtime policy
- Relevant module constraints
- Planned verification cases

Preserve the REQ-007 row and other requirements.

If the REQ-007 test range is inconsistent with actual case IDs, report it rather than changing unrelated records.

## 4. Structural constraints

Extend the existing search module section, preserving REQ-007's responsibilities.

Specify proposed REQ-008 components:

- SearchRequest
- SearchSource adapters
- FallbackCoordinator
- ErrorClassification and failure types
- Thin tool-facing adapter

Document the dependency direction and the prohibition on implementing the fallback algorithm inside orchestration nodes.

Record shared-contract approval dependencies for Configuration and MCP load results.

## 5. Verification constraints

Inspect the existing TC numbering and formatting.

Add planned REQ-008 test cases beginning at the next unused TC ID after REQ-007.

At minimum cover:

- C-001 primary timeout followed by successful fallback.
- C-002 ordered three-source fallback.
- C-003 explicit aggregate when all eligible sources fail.
- C-004 empty success suppresses fallback.
- C-005 malformed query suppresses fallback.
- Typed error classification.
- MCP load-stage failure diagnostics.
- No-fallback configuration backward compatibility.
- Rejected credential at invocation versus missing auth configuration.
- Stable tool-name dispatch and source adapter schema mapping.

All cases must be marked Planned / Not Implemented / Not Executed.

Do not write or execute tests.

## 6. Consistency checks

Verify:

- REQ-008 C-001 through C-005 all have traceability.
- Invariant IDs are unique.
- Runtime policy IDs are unique.
- TC IDs are unique.
- No Proposed decision is described as Accepted.
- REQ-007 documents are not overwritten.
- ADR-002 and shared documents use consistent interface names.
- D-1 through D-8 remain appropriately open.

Run:

- `git diff --check`
- `git status --short`
- Relevant read-only grep or validation commands.

## 7. Final report

Return:

1. Exact files changed.
2. New invariant IDs.
3. New runtime policy ID.
4. TC ID range and coverage.
5. Updated traceability summary.
6. Cross-document inconsistencies.
7. Decisions requiring team approval.
8. Git status and validation results.

Stop without committing or pushing.

---

## Message 215 — ASSISTANT

I'm now in build mode with the five files permitted. Let me read the current state of each before editing.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"^## INV-\" docs/architecture/invariants.md; echo \"=== runtime policy POL ids ===\"; grep -nE \"POL-[0-9]{3}\" docs/architecture/runtime-policy-catalog.md; echo \"=== TC ids overall ===\"; grep -oE \"TC-[0-9]{3}\" docs/code-governance/verification-constraints.md | sort -u | tr '\\n' ' '; echo; echo \"=== trace rows ===\"; grep -nE \"^\\| REQ-00[78] \" docs/architecture/trace-matrix.md"}
output: 19:## INV-001 — Compression never drops the newest context
29:## INV-002 — No failure is reported as complete research
39:## INV-003 — Research is bounded and every exit has one reason
49:## INV-004 — Every report citation resolves to a retrieved source
59:## INV-005 — Search results are never mistaken for evidence they do not contain
=== runtime policy POL ids ===
12:| POL-001 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
30:| POL-002 | A declared MCP is the effective search source (`search_api=none` with `MCP_DECLARED`) and cannot provide a usable search tool at runtime | `McpLoadResult.status` is `LOAD_FAILED` (connection/loading failure), `ZERO_USABLE_TOOLS` (loaded but none match), or `AUTH_MISSING` (required token unresolvable). Requires the ADR-001 §8.1a adapter/refactor (U-5); not available in the current `load_mcp_tools` | Stop the affected research and raise an explicit error naming the cause (and `mcp_config.url`); no source substitution | None | Research for the affected task fails explicitly; no silent no-search run; a `LOADED` tool that returns no hits is not this policy and remains a success | REQ-007 / INV-005 (Proposed) | planned: `test/offline/test_search_configuration.py` (TC-016, TC-017, TC-018, TC-024) |
=== TC ids overall ===
TC-001 TC-002 TC-003 TC-004 TC-005 TC-006 TC-007 TC-008 TC-009 TC-010 TC-011 TC-012 TC-013 TC-014 TC-015 TC-016 TC-017 TC-018 TC-019 TC-020 TC-021 TC-022 TC-023 TC-024 TC-025 TC-026
=== trace rows ===
20:| REQ-007 | Search setu

---

## Message 216 — ASSISTANT

Facts confirmed: INV-001..005 exist (next INV-006), POL-001 placeholder + POL-002 used (next POL-003), TC-001..TC-026 used (next TC-027). Note REQ-007 trace row says "TC-001–TC-025" but body has TC-026 — I'll report this, not fix it. Let me read the relevant sections.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '59,71p' docs/architecture/invariants.md"}
output: ## INV-005 — Search results are never mistaken for evidence they do not contain

- **Statement:** On every run, before any model or search call, a search configuration that names an unsupported provider, pairs a native provider with a `research_model` of another provider, or leaves no search and no valid MCP declaration is rejected. A statically declared MCP that cannot provide a usable search tool at runtime fails that research explicitly, while a search that returns no results is a successful search that carries no evidence.
- **Module:** search
- **Source:** REQ-007, REQ-008
- **Status:** Proposed
- **Enforcing component:** the pure search-configuration validator and search-capability predicate in `search/`, called from `clarify_with_user` and `researcher` (ADR-001, Proposed); the runtime MCP failure policy `POL-002` (Proposed; ADR-001 §9, U-1). The search adapter is reached through `utils.get_all_tools()`.
- **Verification:** `test/offline/test_search_configuration.py`, `test/offline/test_search_fallback.py` with fake providers (normal, empty, timeout, invalid, unknown); see ADR-001 §11 and `verification-constraints.md` §7.
- **Fallback:** on an eligible error, try only the configured fallback sources in order and record each attempt; when all fail, return an explicit search failure. Never substitute a source that is not configured. (Fallback behaviour itself is REQ-008 and out of REQ-007 scope.)

## Adding an Entry

Copy an entry, take the next free `INV-NNN` number, and

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '14,32p' docs/architecture/runtime-policy-catalog.md"}
output: ## 2. Module Sections

Copy the example for your module and number policies with the next free `POL-NNN`; numbers are unified at integration.

### <Module> (REQ-NNN, ADR-NNN)

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |
|---|---|---|---|---|---|---|---|
| POL-NNN | e.g. a researcher raises an exception | how deterministic code recognises it | what the system does | retries, limits, fallback, or none | effect on the run outcome (`complete`, `partial`, `failed`, REQ-004) | REQ-NNN / INV-NNN | `test/offline/<file>::<test>` |

### search (REQ-007, ADR-001) — proposed, awaiting approval

The entries below are **proposed** and are not approved until SA Review and the human decide them (ADR-001 §9, U-1). They introduce no fallback behaviour; fallback belongs to REQ-008 and is out of scope. Implementation **depends** on the MCP load adapter or refactor in ADR-001 §8.1a (U-5): the current `load_mcp_tools` returns an empty list for every failure, so the three failure states are not distinguishable today.

| Policy ID | Trigger | Detection | Behaviour | Retry / degradation | Outcome effect | Source | Test |
|---|---|---|---|---|---|---|---|
| POL-002 | A declared MCP is the effective search source (`search_api=none` with `MCP_DECLARED`) and cannot provide a usable search tool at runtime | `McpLoadResult.status` is `LOAD_FAILED` (connection/loading failure), `ZERO_USABLE_TOOLS` (loaded but none match), or `AUTH_MISSING` (required

---

## Message 217 — ASSISTANT

Now the verification-constraints search section tail and structural constraints search section.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '110,118p' docs/code-governance/verification-constraints.md"}
output: | TC-024 | U-5, §8.1a | exception | MCP load fed each branch (Option A: adapter owns the load; Option B: refactored `load_mcp_tools`): missing `url`/`tools`, missing auth token, `get_tools()` raise, successful load with 0 matching tools, successful load with tools | Returns distinct `LOAD_FAILED` / `AUTH_MISSING` / `ZERO_USABLE_TOOLS` / `LOADED` (four states not collapsed to `[]`); a fake MCP client (`get_tools`) is used, no network | `::test_mcp_load_result_distinguishes_states` |
| TC-025 | U-3, §8.2 | normal/boundary | Native binding: fake model records definitions passed to `bind_tools`; "configured" (definition produced) vs "bound" (`native_bound`) vs "executed" (fake response with/without `anthropic_websearch_called`/`openai_websearch_called` metadata) | Predicate uses `native_bound` (available only after binding); execution availability is observed only post-response and does not gate capability; a successful bind is not treated as proof of remote execution | `::test_native_configured_bound_executed` |
| TC-026 | Correction B, §7.2, §8.0 | normal/exception | Env `SEARCH_API` set with a conflicting `configurable.search_api`; a resolver snapshot plus construction from validated effective inputs; a fake model recording call count | The constructed `Configuration` reflects the resolver's effective value (env precedence preserved), no `os.environ` mutation occurs, and the capability predicate is only evaluated after `bind_tools` (step 4). Zero model/search calls before vali

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '90,103p' docs/code-governance/structural-constraints.md"}
output: ### search (REQ-007, ADR-001)

| Item | Constraint |
|---|---|
| Path | `src/open_deep_research/search/` |
| Responsibility | Resolve and validate a search configuration on each run before a model/search call, decide whether a run has search capability, and classify the MCP load outcome, without model calls or implicit process-environment access during static validation; apply the runtime MCP stop-and-error policy (Proposed, pending SA Review). |
| Public interface | `resolve_search_api(raw_configurable, environ: Mapping) -> SearchAPI` (pure; caller passes the environment snapshot); `resolve_configuration(raw_configurable, environ) -> Configuration` (builds from validated effective inputs, §7.2); `validate_search_configuration(search_api, research_model, mcp) -> None` (raises a domain error); `classify_mcp(mcp: MCPConfig \| None) -> MCPStatus`; `model_provider(model: str) -> str`; `load_mcp_result(config, existing_tool_names) -> McpLoadResult` (MCP load distinction, §8.1a; U-5); `has_search_capability(evidence: SearchEvidence) -> bool` (evaluated after binding, step 4) |
| Called from | `clarify_with_user` (public boundary: effective configuration resolution and static validation only — no tool assembly, MCP loading or native binding) and `researcher` (subgraph boundary, which runs the §8.0 order: validate → assemble → bind → capability → invoke) in `deep_researcher.py` |
| May depend on | `configuration.py` (`Configuration`, `SearchAPI`, `MCPConfig`); an explicit environment

---

## Message 218 — ASSISTANT

I have all context. Now making the edits. **§1 Invariants** — add INV-006..009 after INV-005 (before "Adding an Entry").

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/invariants.md", "oldString": "- **Fallback:** on an eligible error, try only the configured fallback sources in order and record each attempt; when all fail, return an explicit search failure. Never substitute a source that is not configured. (Fallback behaviour itself is REQ-008 and out of REQ-007 scope.)\n\n## Adding an Entry", "newString": "- **Fallback:** on an eligible error, try only the configured fallback sources in order and record each attempt; when all fail, return an explicit search failure. Never substitute a source that is not configured. (Fallback behaviour itself is REQ-008 and out of REQ-007 scope.)\n\n## INV-006 — No fallback after an empty successful result\n\n- **Statement:** A search that returns no hits without error is a successful search and terminates the fallback sequence; no further source is tried.\n- **Module:** search\n- **Source:** REQ-008 (C-004)\n- **Status:** Proposed\n- **Enforcing component:** the fallback coordinator (`search/`, ADR-002): an empty `SearchOutcome` (`found=False`) is a success and stops the attempt loop.\n- **Verification:** `test/offline/test_search_fallback.py` — planned case for C-004 (empty result suppresses fallback); see ADR-002 §11 and `verification-constraints.md` §7.\n- **Fallback:** return the empty success to the researcher as no evidence; do not advance to the next configured source.\n\n## INV-007 — No fallback after an ineligible error\n\n- **Statement:** An ineligible search error (for example a malformed query) is returned without trying any further source; fallback advances only on an eligible error.\n- **Module:** search\n- **Source:** REQ-008 (C-005)\n- **Status:** Proposed\n- **Enforcing component:** the error classification in the fallback coordinator (`search/`, ADR-002): an ineligible `SearchTerminatedFailure` ends the loop immediately.\n- **Verification:** `test/offline/test_search_fallback.py` — planned case for C-005
output: Edit applied successfully.

---

## Message 219 — ASSISTANT

**§2 Runtime policy** — add POL-003 (next free), plus the pending multi-source exception note. Add after the POL-002 row.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/runtime-policy-catalog.md", "oldString": "| POL-002 | A declared MCP is the effective search source (`search_api=none` with `MCP_DECLARED`) and cannot provide a usable search tool at runtime | `McpLoadResult.status` is `LOAD_FAILED` (connection/loading failure), `ZERO_USABLE_TOOLS` (loaded but none match), or `AUTH_MISSING` (required token unresolvable). Requires the ADR-001 §8.1a adapter/refactor (U-5); not available in the current `load_mcp_tools` | Stop the affected research and raise an explicit error naming the cause (and `mcp_config.url`); no source substitution | None | Research for the affected task fails explicitly; no silent no-search run; a `LOADED` tool that returns no hits is not this policy and remains a success | REQ-007 / INV-005 (Proposed) | planned: `test/offline/test_search_configuration.py` (TC-016, TC-017, TC-018, TC-024) |", "newString": "| POL-002 | A declared MCP is the effective search source (`search_api=none` with `MCP_DECLARED`) and cannot provide a usable search tool at runtime | `McpLoadResult.status` is `LOAD_FAILED` (connection/loading failure), `ZERO_USABLE_TOOLS` (loaded but none match), or `AUTH_MISSING` (required token unresolvable). Requires the ADR-001 §8.1a adapter/refactor (U-5); not available in the current `load_mcp_tools` | Stop the affected research and raise an explicit error naming the cause (and `mcp_config.url`); no source substitution | None | Research for the affected task fails explicitly; no silent no-search run; a `LOADED` tool that returns no hits is not this policy and remains a success | REQ-007 / INV-005 (Proposed) | planned: `test/offline/test_search_configuration.py` (TC-016, TC-017, TC-018, TC-024) |\n\n### search (REQ-008, ADR-002) — proposed, awaiting approval\n\nThe policy below is **proposed** and not approved until SA Review (ADR-002, EVAL-002). It introduces no change to native model search (out of scope) and does not amend POL
output: Edit applied successfully.

---

## Message 220 — ASSISTANT

**§3 Trace matrix** — update REQ-008 row.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/trace-matrix.md", "oldString": "| REQ-008 | Search fallback | functional | approved | TBD | INV-005 (Proposed) | Proposed: `search/` | planned: `test/offline/test_search_fallback.py` | TBD |", "newString": "| REQ-008 | Search fallback | functional | approved | Ordered fallback over configured Tavily/MCP sources on eligible failures; empty result = success (no fallback); ineligible error stops fallback; all-exhausted yields an explicit aggregate distinct from empty; load-stage vs invocation-stage distinguished; depends on REQ-007 U-5 for the structured load result | INV-005 (Proposed); INV-006, INV-007, INV-008, INV-009 (Proposed); ADR-002 (Proposed); EVAL-002 (Open); POL-003 (Proposed) | Proposed: `search/` fallback coordinator (`SearchRequest`, `SearchSource` adapters, `FallbackCoordinator`, error/failure types, thin tool-facing adapter) | planned: `test/offline/test_search_fallback.py` (TC-027 onward, ADR-002 §11) | TBD |"}
output: Edit applied successfully.

---

## Message 221 — ASSISTANT

**§4 Structural constraints** — extend the search module section with REQ-008 components.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/code-governance/structural-constraints.md", "oldString": "REQ-008 (search fallback) will also live in this module and is designed separately; this section covers REQ-007 only. Two call sites are intentional: `clarify_with_user` is the public boundary, and `researcher` is required because the researcher subgraph is compiled and directly invokable (ADR-001 §2.2, §10). `supervisor` binds no search tool and `researcher_tools` is reached only after `researcher` validated, so neither needs a check.", "newString": "REQ-008 (search fallback) will also live in this module and is designed separately; this section covers REQ-007 only. Two call sites are intentional: `clarify_with_user` is the public boundary, and `researcher` is required because the researcher subgraph is compiled and directly invokable (ADR-001 §2.2, §10). `supervisor` binds no search tool and `researcher_tools` is reached only after `researcher` validated, so neither needs a check.\n\n### search — REQ-008 fallback (REQ-008, ADR-002) — Proposed\n\nThe REQ-007 responsibilities above are unchanged. REQ-008 adds the following components to the same `search/` module (not yet implemented; Proposed, pending SA Review).\n\n| Item | Constraint |\n|---|---|\n| Path | `src/open_deep_research/search/` (same module as REQ-007) |\n| Responsibility | Execute an ordered fallback over configured client-side search sources on eligible failures, classify errors before they are stringified, distinguish empty success from failure, and aggregate an explicit all-sources-failed result. |\n| Public interface | `SearchRequest(queries, max_results, topic)`; `SearchSource` adapters (`name`, `async invoke(SearchRequest) -> SearchOutcome`, `load_status`); `FallbackCoordinator.run(req, sources) -> SearchOutcome \\| SearchTerminatedFailure \\| AllSourcesFailed`; `SearchAttemptFailure(source_name, stage ∈ {LOAD, INVOKE}, classification, detail)`, `SearchTerminatedFailure`, `AllSo
output: Edit applied successfully.

---

## Message 222 — ASSISTANT

**§5 Verification constraints** — add REQ-008 cases TC-027..TC-036 after TC-026 row block, before the regression notes. I'll insert them within the search module section, but mark them as REQ-008. Let me append after TC-026 and add a sub-note.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md", "oldString": "| TC-026 | Correction B, §7.2, §8.0 | normal/exception | Env `SEARCH_API` set with a conflicting `configurable.search_api`; a resolver snapshot plus construction from validated effective inputs; a fake model recording call count | The constructed `Configuration` reflects the resolver's effective value (env precedence preserved), no `os.environ` mutation occurs, and the capability predicate is only evaluated after `bind_tools` (step 4). Zero model/search calls before validation | `::test_config_resolution_snapshot_and_order` |\n\n- **Regression:** `uv run pytest test/offline`; no shared contract changes, so `test/offline/test_contracts.py` is unaffected. TC-021 is the default-configuration regression.", "newString": "| TC-026 | Correction B, §7.2, §8.0 | normal/exception | Env `SEARCH_API` set with a conflicting `configurable.search_api`; a resolver snapshot plus construction from validated effective inputs; a fake model recording call count | The constructed `Configuration` reflects the resolver's effective value (env precedence preserved), no `os.environ` mutation occurs, and the capability predicate is only evaluated after `bind_tools` (step 4). Zero model/search calls before validation | `::test_config_resolution_snapshot_and_order` |\n\n**REQ-008 fallback (ADR-002) — Planned / Not Implemented / Not Executed.** The cases below are proposed only; no test file exists yet. They continue after TC-026 and are recorded in ADR-002 §11.\n\n| Case | Covers | Type | Input | Expected result | Test |\n|---|---|---|---|---|---|\n| TC-027 | REQ-008 C-001 | exception | Primary source times out; a working fallback is configured | Primary tried once, fallback tried next, fallback result returned | `test/offline/test_search_fallback.py::test_primary_failure_uses_fallback` |\n| TC-028 | REQ-008 C-002 | exception | Three sources; first two fail with eligible erro
output: Edit applied successfully.

---

## Message 223 — ASSISTANT

Let me verify uniqueness and consistency, and check the TC-033 requirement-req mapping and closing note.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && echo \"=== INV ids ===\"; grep -n \"^## INV-\" docs/architecture/invariants.md; echo \"=== POL ids ===\"; grep -oE \"POL-[0-9]{3}\" docs/architecture/runtime-policy-catalog.md | sort | uniq -c; echo \"=== TC unique count ===\"; grep -oE \"^\\| TC-[0-9]{3} \" docs/code-governance/verification-constraints.md | grep -oE \"TC-[0-9]{3}\" | sort | uniq -d; echo \"dups above (none=ok)\"; grep -cE \"^\\| TC-[0-9]{3} \" docs/code-governance/verification-constraints.md; echo \"=== REQ-008 cases present ===\"; grep -oE \"TC-0(2[7-9]|3[0-6])\" docs/code-governance/verification-constraints.md | sort -u | tr '\\n' ' '"}
output: === INV ids ===
19:## INV-001 — Compression never drops the newest context
29:## INV-002 — No failure is reported as complete research
39:## INV-003 — Research is bounded and every exit has one reason
49:## INV-004 — Every report citation resolves to a retrieved source
59:## INV-005 — Search results are never mistaken for evidence they do not contain
69:## INV-006 — No fallback after an empty successful result
79:## INV-007 — No fallback after an ineligible error
89:## INV-008 — Configured source order is preserved
99:## INV-009 — Exhausting all eligible sources produces an explicit failure
=== POL ids ===
   1 POL-001
   7 POL-002
   1 POL-003
=== TC unique count ===
TC-001
TC-002
TC-003
dups above (none=ok)
39
=== REQ-008 cases present ===
TC-027 TC-028 TC-029 TC-030 TC-031 TC-032 TC-033 TC-034 TC-035 TC-036

---

## Message 224 — ASSISTANT

The only "duplicates" are TC-001/002/003 from the template example rows (lines 74-76), which are placeholders — pre-existing, not real cases. Genuine cases TC-004…TC-036 are unique (39 table rows = 3 template + 36 real). POL-002 count 7 is because the string "POL-002" appears in the cross-reference note, not 7 policy rows — let me verify POL rows are unique.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && echo \"=== POL row-starts (unique check) ===\"; grep -oE \"^\\| POL-[0-9]{3} \" docs/architecture/runtime-policy-catalog.md | grep -oE \"POL-[0-9]{3}\" | sort | uniq -c; echo \"=== INV field completeness (each needs Statement/Module/Source/Status/Enforcing/Verification/Fallback) ===\"; for n in 006 007 008 009; do c=$(awk \"/^## INV-$n/{f=1;next} /^## /{f=0} f\" docs/architecture/invariants.md | grep -cE \"^- \\*\\*(Statement|Module|Source|Status|Enforcing component|Verification|Fallback):\\*\\*\"); echo \"INV-$n fields: $c/7\"; done"}
output: === POL row-starts (unique check) ===
   1 POL-001
   1 POL-002
   1 POL-003
=== INV field completeness (each needs Statement/Module/Source/Status/Enforcing/Verification/Fallback) ===
INV-006 fields: 7/7
INV-007 fields: 7/7
INV-008 fields: 7/7
INV-009 fields: 7/7


---

## Message 225 — ASSISTANT

All unique and complete. Now check cross-document interface-name consistency with ADR-002 and that C-001…C-005 all trace, then run final validation.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && echo \"=== interface names ADR-002 vs structural/verif ===\"; for t in SearchRequest SearchSource FallbackCoordinator SearchOutcome SearchTerminatedFailure AllSourcesFailed SearchAttemptFailure ErrorClassification; do a=$(grep -c \"$t\" docs/architecture/adr/002-search-fallback.md); s=$(grep -c \"$t\" docs/code-governance/structural-constraints.md); v=$(grep -c \"$t\" docs/code-governance/verification-constraints.md); echo \"$t  ADR=$a struct=$s verif=$v\"; done"}
output: === interface names ADR-002 vs structural/verif ===
SearchRequest  ADR=6 struct=1 verif=1
SearchSource  ADR=3 struct=1 verif=0
FallbackCoordinator  ADR=2 struct=1 verif=0
SearchOutcome  ADR=6 struct=1 verif=0
SearchTerminatedFailure  ADR=5 struct=1 verif=0
AllSourcesFailed  ADR=10 struct=1 verif=1
SearchAttemptFailure  ADR=3 struct=1 verif=1
ErrorClassification  ADR=2 struct=1 verif=0


[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && echo \"=== C-001..C-005 trace in verification ===\"; for c in C-001 C-002 C-003 C-004 C-005; do echo \"$c: $(grep -c \"REQ-008 $c\" docs/code-governance/verification-constraints.md) in verif; $(grep -c \"$c\" docs/architecture/trace-matrix.md) in trace\"; done; echo \"=== 'Accepted'/'approved' claims for Proposed? ===\"; grep -niE \"INV-006|INV-007|INV-008|INV-009|POL-003|ADR-002\" docs/architecture/invariants.md docs/architecture/runtime-policy-catalog.md docs/architecture/trace-matrix.md | grep -iE \"accepted\" || echo \"no false Accepted\""}
output: === C-001..C-005 trace in verification ===
C-001: 1 in verif; 1 in trace
C-002: 1 in verif; 0 in trace
C-003: 1 in verif; 0 in trace
C-004: 1 in verif; 0 in trace
C-005: 1 in verif; 1 in trace
=== 'Accepted'/'approved' claims for Proposed? ===
no false Accepted


---

## Message 226 — ASSISTANT

C-002/C-003/C-004 show "0 in trace" only because the trace row groups them descriptively rather than as literal "C-002" strings. Let me verify the trace row covers all criteria conceptually, then run final validation.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -n \"REQ-008\" docs/architecture/trace-matrix.md | head -1"}
output: 21:| REQ-008 | Search fallback | functional | approved | Ordered fallback over configured Tavily/MCP sources on eligible failures; empty result = success (no fallback); ineligible error stops fallback; all-exhausted yields an explicit aggregate distinct from empty; load-stage vs invocation-stage distinguished; depends on REQ-007 U-5 for the structured load result | INV-005 (Proposed); INV-006, INV-007, INV-008, INV-009 (Proposed); ADR-002 (Proposed); EVAL-002 (Open); POL-003 (Proposed) | Proposed: `search/` fallback coordinator (`SearchRequest`, `SearchSource` adapters, `FallbackCoordinator`, error/failure types, thin tool-facing adapter) | planned: `test/offline/test_search_fallback.py` (TC-027 onward, ADR-002 §11) | TBD |


[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && git diff --check && echo \"DIFF_CHECK_CLEAN\"; echo \"=== status --short ===\"; git status --short; echo \"=== stat ===\"; git diff --stat"}
output: DIFF_CHECK_CLEAN
=== status --short ===
 M docs/architecture/evaluation-table.md
 M docs/architecture/invariants.md
 M docs/architecture/runtime-policy-catalog.md
 M docs/architecture/trace-matrix.md
 M docs/code-governance/structural-constraints.md
 M docs/code-governance/verification-constraints.md
?? docs/architecture/adr/002-search-fallback.md
=== stat ===
 docs/architecture/evaluation-table.md            | 42 ++++++++++++++++++++++++
 docs/architecture/invariants.md                  | 40 ++++++++++++++++++++++
 docs/architecture/runtime-policy-catalog.md      | 10 ++++++
 docs/architecture/trace-matrix.md                |  2 +-
 docs/code-governance/structural-constraints.md   | 17 ++++++++++
 docs/code-governance/verification-constraints.md | 15 +++++++++
 6 files changed, 125 insertions(+), 1 deletion(-)


---

## Message 227 — ASSISTANT

All edits are complete and consistent. Note EVAL-002 (`evaluation-table.md`) and ADR-002 appear in `git status` only because they were drafted in the previous task and are not yet committed; I did not modify them in this task.

## 1. Files changed (this task)

- `docs/architecture/invariants.md` — added INV-006…INV-009
- `docs/architecture/runtime-policy-catalog.md` — added POL-003 + pending POL-002 exception note
- `docs/architecture/trace-matrix.md` — updated REQ-008 row
- `docs/code-governance/structural-constraints.md` — added REQ-008 fallback subsection to the search module
- `docs/code-governance/verification-constraints.md` — added TC-027…TC-036

Not modified in this task: EVAL-002 / ADR-002 (drafted previously; only reported on), source, tests, requirements, ADR-001, AI logs, transcripts.

## 2. New invariant IDs

- **INV-006** — No fallback after an empty successful result (C-004)
- **INV-007** — No fallback after an ineligible error (C-005)
- **INV-008** — Configured source order is preserved (C-001, C-002)
- **INV-009** — Exhausting all eligible sources produces an explicit failure (C-003)

All marked **Proposed**; each has all 7 fields (Statement, Module, Source, Status, Enforcing component, Verification, Fallback); INV-005 unchanged in meaning.

## 3. New runtime policy ID

- **POL-003** (next free after POL-001 placeholder and POL-002). Covers triggers, eligible/ineligible failures, ordered retry, empty semantics, all-failed reporting, load-vs-invoke stage, missing-auth-config vs rejected-credential.
- Added a **"Proposed exception to POL-002 — Pending Team Approval"** note cross-referencing ADR-002 D-1 and REQ-007 U-1/U-5. POL-002 itself was not amended.

## 4. TC ID range and coverage

- **TC-027 … TC-036** (continues after REQ-007's TC-026), all marked **Planned / Not Implemented / Not Executed**.
- Coverage: C-001 (TC-027), C-002 (TC-028), C-003 (TC-029), C-004 (TC-030), C-005 (TC-031), typed classification (TC-032), MCP load-stage diagnostics (TC-033), no-fallback backward compatibility (TC-034), rejected-credential vs missing-auth-config (TC-035), stable tool dispatch + adapter schema mapping (TC-036).

## 5. Updated traceability summary

REQ-008 row now references ADR-002 (Proposed), EVAL-002 (Open), INV-005 + INV-006…INV-009 (Proposed), POL-003 (Proposed), the `search/` fallback coordinator components, and planned `test_search_fallback.py` TC-027 onward. REQ-007 and all other requirement rows preserved unchanged.

## 6. Cross-document inconsistencies

- **REQ-007 trace row says "TC-001–TC-025"** but the verification body has TC-001…TC-026 (TC-026 exists). This is a pre-existing, unrelated-record inconsistency — **reported, not changed**, per your instruction. It should be corrected to TC-001–TC-026 in a separate REQ-007 maintenance edit.
- **ADR-002 §11 / EVAL-002** describe the REQ-008 cases as planned; those cases now exist in `verification-constraints.md` §7 (TC-027…TC-036) as planned entries. No wording conflict, but ADR-002 §11 could later add a pointer to the assigned TC IDs — a change to ADR-002, out of this task's allowed scope (reported).
- Interface names (`SearchRequest`, `SearchSource`, `FallbackCoordinator`, `SearchOutcome`, `SearchTerminatedFailure`, `AllSourcesFailed`, `SearchAttemptFailure`, `ErrorClassification`) are used consistently across ADR-002, structural constraints and verification constraints.
- No Proposed item is described as Accepted/approved anywhere.

## 7. Decisions requiring team approval

- **D-1** — load-vs-invocation split and the POL-002 multi-source exception (Pending).
- **D-2** — fallback configuration field name/placement/precedence/default.
- **D-3** — typed classification policy (Tavily generic-error gap; unclassifiable → ineligible).
- **D-4** — unloadable MCP fallback recorded (now `stage=LOAD`) vs excluded.
- **D-5** — dependency on REQ-007 U-5 structured load result (Pending).
- **D-6** — coordinator-behind-thin-adapter + stable tool name.
- **D-7** — all-failed rendering distinct from the empty marker.
- **D-8** — missing-auth-config vs rejected-credential boundary.

## 8. Validation

- `git diff --check`: **CLEAN**
- Unique IDs: INV-001…INV-009 (9 unique, 4 new); POL rows `POL-001`/`POL-002`/`POL-003` each exactly once; TC table rows: only template placeholders TC-001/002/003 duplicate (pre-existing example rows), real cases TC-004…TC-036 unique.
- No false "Accepted" claims for any Proposed item.
- Nothing committed or pushed. Scope not expanded.

---

## Message 228 — USER

Perform the final cross-document consistency repair for REQ-008 Software Architecture.

Current branch: `docs/sa-search-fallback`.

Read the actual current repository documents before editing.

You may edit only:

- `docs/architecture/adr/002-search-fallback.md`
- `docs/architecture/trace-matrix.md`
- `docs/code-governance/verification-constraints.md`

Do not modify any other file.

Do not implement code or tests. Do not commit or push.

## 1. Update ADR-002 §11

The planned verification cases TC-027 through TC-036 now exist as documentation entries in `docs/code-governance/verification-constraints.md` §7.

Replace any outdated statement claiming these cases are absent from that document.

Clearly distinguish:

- Planned test cases documented.
- Test implementation not created.
- Tests not executed.

Ensure ADR-002's verification table and the TC-027–TC-036 definitions are consistent.

## 2. Review TC-033

Distinguish two verification responsibilities:

A. Recording a structured MCP load-stage failure, including `stage=LOAD`, without falsely claiming that a search invocation occurred.

B. Deciding whether another usable search source permits continuation after an MCP fallback source fails to load.

A is a proposed diagnostic contract.

B depends on ADR-002 D-1/D-4 and REQ-007 U-1/U-5 and must remain conditional on team approval.

Do not silently approve the POL-002 exception.

Preserve unique TC identifiers. If splitting TC-033 requires another case, use the next unused TC ID and update all relevant references within the permitted files.

## 3. Review the REQ-008 trace matrix

Verify that C-001 through C-005 map explicitly to TC-027 through TC-031.

If the table structure permits, make the acceptance-criterion mapping explicit in the REQ-008 row without changing unrelated requirements.

Report the pre-existing REQ-007 TC-001–TC-025 versus TC-026 mismatch. Do not change the REQ-007 row.

## 4. Review regression requirements

Preserve the existing REQ-007 regression note.

Add a separate REQ-008 regression note explaining that:

- A new fallback configuration field is proposed.
- The MCP load-result contract may change, depending on REQ-007 U-5.
- Shared-contract compatibility must be tested if these changes are approved.
- TC-034 covers the no-fallback behavior-preservation requirement.
- No regression tests have been implemented or executed for REQ-008.

Do not claim existing contract tests are unaffected.

## 5. Review invariant and policy interactions

Read INV-005, INV-006 through INV-009, POL-002, and POL-003 without editing them.

Identify any remaining conflicts between:

- Ordered fallback without skipping sources.
- A configured MCP source that cannot load.
- The existing POL-002 stop behavior.
- The proposed conditional continuation policy.

Report unresolved conflicts for team review instead of silently resolving them.

## 6. Validation

Run:

- `git diff --check`
- `git status --short`
- Cross-reference checks for ADR-002 and TC-027 onward.
- Duplicate TC-ID checks excluding template example rows.

Because ADR-002 is currently untracked, ensure its contents are also inspected for whitespace and consistency.

Return:

1. Exact changes made.
2. Updated test coverage.
3. Remaining cross-document conflicts.
4. Decisions pending team approval.
5. Git status.
6. Whether the documentation is ready for AI evidence logging and SA Review submission.

Stop without committing or pushing.

---

## Message 229 — ASSISTANT

I'll read the current ADR-002 §11, TC-027..036, the trace row, and the invariants/policies before editing.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '/^## 11. Verification/,/^## 12/p' docs/architecture/adr/002-search-fallback.md"}
output: ## 11. Verification

The cases below are **Planned / Not Implemented / Not Executed**. They do **not** yet exist in `verification-constraints.md` §7 or in any test file; this ADR only proposes them. IDs are proposed to continue after REQ-007's `TC-026` to avoid collision (the module example rows TC-001…TC-003 are placeholders, not real cases).

| Criterion | Planned case | Test name (planned) |
|---|---|---|
| C-001 | primary timeout → next source's result returned | `test/offline/test_search_fallback.py::test_primary_failure_uses_fallback` |
| C-002 | three sources, first two eligible-fail → third result | `::test_fallbacks_follow_configured_order` |
| C-003 | all eligible fail → `AllSourcesFailed` lists each source and error | `::test_all_sources_fail_explicitly` |
| C-004 | primary empty result → success, no fallback | `::test_empty_result_does_not_trigger_fallback` |
| C-005 | malformed query (ineligible) → terminated, no fallback | `::test_ineligible_error_does_not_trigger_fallback` |
| ASR-008-10 / D-4 | configured-but-unloadable MCP → `load_failed` diagnostic, listed | `::test_unloadable_mcp_source_recorded` |
| D-7 | all-failed rendering distinct from empty marker | `::test_all_failed_distinct_from_empty` |
| ASR-008-08 | no fallback configured → unchanged behaviour | `::test_no_fallback_configuration_preserved` |
| D-8 | missing auth config = failure; rejected credential at invocation = fallback | `::test_auth_boundary_classification` |

The exact `TC-NNN` assignment

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -nE \"TC-03[3-7]|TC-036|REQ-008 fallback \\(ADR-002\\)\" docs/code-governance/verification-constraints.md"}
output: 114:**REQ-008 fallback (ADR-002) — Planned / Not Implemented / Not Executed.** The cases below are proposed only; no test file exists yet. They continue after TC-026 and are recorded in ADR-002 §11.
124:| TC-033 | REQ-008 §6.1, INV-006..009 (load stage) | exception | Declared MCP fallback source unavailable at load time while other usable sources remain | `SearchAttemptFailure(stage=LOAD)` recorded; aggregate shows the source was never invoked; behaviour subject to D-1 | `test/offline/test_search_fallback.py::test_mcp_load_stage_failure_recorded` |
125:| TC-034 | REQ-008 ASR-008-08 | regression | No fallback list configured | Single-source baseline behaviour preserved (intent; must be confirmed by this case) | `test/offline/test_search_fallback.py::test_no_fallback_configuration_preserved` |
126:| TC-035 | REQ-008 D-8 | exception | (a) missing auth configuration; (b) credential rejected at invocation | (a) configuration failure, not retried; (b) eligible fallback, no automatic recovery | `test/offline/test_search_fallback.py::test_auth_boundary_classification` |
127:| TC-036 | REQ-008 ASR-008-11, §5 (schema mapping) | normal | Tavily and MCP sources with different input schemas; model calls the search tool by its stable name | Tool name resolves via `tools_by_name`; each adapter maps `SearchRequest` to its source schema; result handled identically | `test/offline/test_search_fallback.py::test_tool_dispatch_and_adapter_schema` |


---

## Message 230 — ASSISTANT

Now let me see the full REQ-008 TC block (TC-027..036) and the regression notes to edit precisely.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '114,132p' docs/code-governance/verification-constraints.md"}
output: **REQ-008 fallback (ADR-002) — Planned / Not Implemented / Not Executed.** The cases below are proposed only; no test file exists yet. They continue after TC-026 and are recorded in ADR-002 §11.

| Case | Covers | Type | Input | Expected result | Test |
|---|---|---|---|---|---|
| TC-027 | REQ-008 C-001 | exception | Primary source times out; a working fallback is configured | Primary tried once, fallback tried next, fallback result returned | `test/offline/test_search_fallback.py::test_primary_failure_uses_fallback` |
| TC-028 | REQ-008 C-002 | exception | Three sources; first two fail with eligible errors | Tried in configured order; third source's result returned | `test/offline/test_search_fallback.py::test_fallbacks_follow_configured_order` |
| TC-029 | REQ-008 C-003 | exception | Every source fails with eligible errors | `AllSourcesFailed` lists each attempted source and error; not equal to the empty marker; no fabricated result | `test/offline/test_search_fallback.py::test_all_sources_fail_explicitly` |
| TC-030 | REQ-008 C-004 | normal | Primary returns no hits without error | Empty success returned; no fallback tried | `test/offline/test_search_fallback.py::test_empty_result_does_not_trigger_fallback` |
| TC-031 | REQ-008 C-005 | exception | Primary rejects the query as malformed (ineligible) | Error returned; no fallback tried | `test/offline/test_search_fallback.py::test_ineligible_error_does_not_trigger_fallback` |
| TC-032 | REQ-008 §7 (typed classification) | ex

---

## Message 231 — ASSISTANT

Now I'll make the edits. **§1 ADR-002 §11** — replace the "do not yet exist" statement and align the table with TC-027..TC-036 (including the TC-033 split).

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/adr/002-search-fallback.md", "oldString": "The cases below are **Planned / Not Implemented / Not Executed**. They do **not** yet exist in `verification-constraints.md` §7 or in any test file; this ADR only proposes them. IDs are proposed to continue after REQ-007's `TC-026` to avoid collision (the module example rows TC-001…TC-003 are placeholders, not real cases).\n\n| Criterion | Planned case | Test name (planned) |\n|---|---|---|\n| C-001 | primary timeout → next source's result returned | `test/offline/test_search_fallback.py::test_primary_failure_uses_fallback` |\n| C-002 | three sources, first two eligible-fail → third result | `::test_fallbacks_follow_configured_order` |\n| C-003 | all eligible fail → `AllSourcesFailed` lists each source and error | `::test_all_sources_fail_explicitly` |\n| C-004 | primary empty result → success, no fallback | `::test_empty_result_does_not_trigger_fallback` |\n| C-005 | malformed query (ineligible) → terminated, no fallback | `::test_ineligible_error_does_not_trigger_fallback` |\n| ASR-008-10 / D-4 | configured-but-unloadable MCP → `load_failed` diagnostic, listed | `::test_unloadable_mcp_source_recorded` |\n| D-7 | all-failed rendering distinct from empty marker | `::test_all_failed_distinct_from_empty` |\n| ASR-008-08 | no fallback configured → unchanged behaviour | `::test_no_fallback_configuration_preserved` |\n| D-8 | missing auth config = failure; rejected credential at invocation = fallback | `::test_auth_boundary_classification` |\n\nThe exact `TC-NNN` assignments are proposed in the `verification-constraints.md` §7 module section; this ADR does not claim they exist.", "newString": "Status of these cases, stated precisely:\n\n- **Planned test cases are documented** as entries in `verification-constraints.md` §7 (`REQ-008 fallback (ADR-002)`), as `TC-027` through `TC-037`.\n- **Test implementation is not created:** no `test/offline/test_search_f
output: Edit applied successfully.

---

## Message 232 — ASSISTANT

**§2 TC-033 split** — split into TC-033 (A: diagnostic contract) and TC-037 (B: continuation decision, conditional). Update verification-constraints and add TC-037.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md", "oldString": "| TC-033 | REQ-008 §6.1, INV-006..009 (load stage) | exception | Declared MCP fallback source unavailable at load time while other usable sources remain | `SearchAttemptFailure(stage=LOAD)` recorded; aggregate shows the source was never invoked; behaviour subject to D-1 | `test/offline/test_search_fallback.py::test_mcp_load_stage_failure_recorded` |", "newString": "| TC-033 | REQ-008 §6.1, INV-006..009 (load-stage diagnostic contract) | exception | Declared MCP fallback source unavailable at load time | `SearchAttemptFailure(stage=LOAD)` recorded with the load cause; the aggregate shows the source was **never invoked** (not represented as an invocation failure). This is the proposed diagnostic contract only; it does not decide continuation | `test/offline/test_search_fallback.py::test_mcp_load_stage_failure_recorded` |"}
output: Edit applied successfully.

---

## Message 233 — ASSISTANT

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md", "oldString": "| TC-036 | REQ-008 ASR-008-11, §5 (schema mapping) | normal | Tavily and MCP sources with different input schemas; model calls the search tool by its stable name | Tool name resolves via `tools_by_name`; each adapter maps `SearchRequest` to its source schema; result handled identically | `test/offline/test_search_fallback.py::test_tool_dispatch_and_adapter_schema` |", "newString": "| TC-036 | REQ-008 ASR-008-11, §5 (schema mapping) | normal | Tavily and MCP sources with different input schemas; model calls the search tool by its stable name | Tool name resolves via `tools_by_name`; each adapter maps `SearchRequest` to its source schema; result handled identically | `test/offline/test_search_fallback.py::test_tool_dispatch_and_adapter_schema` |\n| TC-037 | REQ-008 D-1/D-4, ASR-008-08 (conditional continuation) | exception | A declared MCP fallback source fails at load while other validated, usable sources remain | **Conditional on team approval (ADR-002 D-1/D-4; REQ-007 U-1/U-5):** if the proposed multi-source exception is approved, fallback continues and records the `stage=LOAD` failure; if it is not approved, POL-002 stop behaviour stands and the run terminates. The case records the decision, it does not presuppose approval | `test/offline/test_search_fallback.py::test_load_failure_continuation_decision` |"}
output: Edit applied successfully.

---

## Message 234 — ASSISTANT

Now update the intro line and add REQ-008 regression notes (§4). Let me update the section opener, the regression block, and the closing notes.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md", "oldString": "**REQ-008 fallback (ADR-002) — Planned / Not Implemented / Not Executed.** The cases below are proposed only; no test file exists yet. They continue after TC-026 and are recorded in ADR-002 §11.", "newString": "**REQ-008 fallback (ADR-002) — Planned / Not Implemented / Not Executed.** The cases below are documented plans only: no `test/offline/test_search_fallback.py` exists and none of these cases has run. They continue after TC-026 and are recorded in ADR-002 §11."}
output: Edit applied successfully.

---

## Message 235 — ASSISTANT

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/code-governance/verification-constraints.md", "oldString": "- **Regression:** `uv run pytest test/offline`; no shared contract changes, so `test/offline/test_contracts.py` is unaffected. TC-021 is the default-configuration regression.", "newString": "- **REQ-007 regression:** `uv run pytest test/offline`; no shared contract changes, so `test/offline/test_contracts.py` is unaffected. TC-021 is the default-configuration regression.\n- **REQ-008 regression (planned, not implemented):** REQ-008 proposes a new fallback configuration field (default empty) and, depending on REQ-007 U-5, may change the `utils.load_mcp_tools` return contract. If either is approved, shared-contract compatibility must be tested (including `test/offline/test_contracts.py`); it cannot be assumed unaffected. TC-034 (`::test_no_fallback_configuration_preserved`) covers the no-fallback behaviour-preservation requirement. No regression tests have been implemented or executed for REQ-008."}
output: Edit applied successfully.

---

## Message 236 — ASSISTANT

**§3 Trace matrix** — make C-001..C-005 → TC-027..TC-031 explicit in the REQ-008 row. REQ-007 row untouched.

[tool: edit | status=completed]
input: {"filePath": "[LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA/docs/architecture/trace-matrix.md", "oldString": "| REQ-008 | Search fallback | functional | approved | Ordered fallback over configured Tavily/MCP sources on eligible failures; empty result = success (no fallback); ineligible error stops fallback; all-exhausted yields an explicit aggregate distinct from empty; load-stage vs invocation-stage distinguished; depends on REQ-007 U-5 for the structured load result | INV-005 (Proposed); INV-006, INV-007, INV-008, INV-009 (Proposed); ADR-002 (Proposed); EVAL-002 (Open); POL-003 (Proposed) | Proposed: `search/` fallback coordinator (`SearchRequest`, `SearchSource` adapters, `FallbackCoordinator`, error/failure types, thin tool-facing adapter) | planned: `test/offline/test_search_fallback.py` (TC-027 onward, ADR-002 §11) | TBD |", "newString": "| REQ-008 | Search fallback | functional | approved | Ordered fallback over configured Tavily/MCP sources on eligible failures; empty result = success (no fallback); ineligible error stops fallback; all-exhausted yields an explicit aggregate distinct from empty; load-stage vs invocation-stage distinguished; depends on REQ-007 U-5 for the structured load result | INV-005 (Proposed); INV-006, INV-007, INV-008, INV-009 (Proposed); ADR-002 (Proposed); EVAL-002 (Open); POL-003 (Proposed) | Proposed: `search/` fallback coordinator (`SearchRequest`, `SearchSource` adapters, `FallbackCoordinator`, error/failure types, thin tool-facing adapter) | planned: `test/offline/test_search_fallback.py` — C-001→TC-027, C-002→TC-028, C-003→TC-029, C-004→TC-030, C-005→TC-031; TC-032–TC-037 (ADR-002 §11) | TBD |"}
output: Edit applied successfully.

---

## Message 237 — ASSISTANT

Now inspect invariants/policies for conflicts (§5) and run all validations.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && echo \"=== TC uniqueness (table rows, excluding template example lines 74-76) ===\"; grep -nE \"^\\| TC-[0-9]{3} \" docs/code-governance/verification-constraints.md | awk -F: '$1>76' | grep -oE \"TC-[0-9]{3}\" | sort | uniq -d; echo \"(dups above; empty=ok)\"; echo \"total real TC rows:\"; grep -nE \"^\\| TC-[0-9]{3} \" docs/code-governance/verification-constraints.md | awk -F: '$1>76' | wc -l; echo \"TC-037 present:\"; grep -c \"TC-037\" docs/code-governance/verification-constraints.md docs/architecture/adr/002-search-fallback.md docs/architecture/trace-matrix.md"}
output: === TC uniqueness (table rows, excluding template example lines 74-76) ===
TC-018
(dups above; empty=ok)
total real TC rows:
      37
TC-037 present:
docs/code-governance/verification-constraints.md:1
docs/architecture/adr/002-search-fallback.md:2
docs/architecture/trace-matrix.md:1


[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && printf '%s\\n' \"whitespace check (all tracked + untracked ADR-002):\"; git diff --check && echo \"TRACKED_CLEAN\"; grep -nE \" +$\" docs/architecture/adr/002-search-fallback.md && echo \"ADR trailing-ws FOUND\" || echo \"ADR no trailing whitespace\""}
output: whitespace check (all tracked + untracked ADR-002):
TRACKED_CLEAN
ADR no trailing whitespace


---

## Message 238 — ASSISTANT

TC-018 appears twice as a table row — but TC-018 is a REQ-007 case; likely one is the placeholder-example line that shifted past my line filter. Let me check precisely.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -nE \"^\\| TC-018 \" docs/code-governance/verification-constraints.md"}
output: 104:| TC-018 | ASR-007-08, U-5 | exception | Declared MCP, `auth_required=True`, no token at runtime | Adapter status `AUTH_MISSING` (distinct from `LOAD_FAILED` and `ZERO_USABLE_TOOLS`): research stops with explicit auth error | `::test_mcp_missing_auth_stops` |


---

## Message 239 — ASSISTANT

Only one TC-018 row exists; the "duplicate" was a false positive from my `awk -F:` filter cutting on the colon inside `::test`. Let me redo the uniqueness check robustly, excluding the three template example lines explicitly.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && grep -nE \"^\\| TC-[0-9]{3} \" docs/code-governance/verification-constraints.md | grep -vE \"REQ-NNN|INV-NNN|<file>\" | sed -E 's/^[0-9]+:\\| (TC-[0-9]{3}) .*/\\1/' | sort | uniq -d; echo \"^^ duplicates (empty=ok)\"; echo \"real TC count:\"; grep -nE \"^\\| TC-[0-9]{3} \" docs/code-governance/verification-constraints.md | grep -vE \"REQ-NNN|INV-NNN|<file>\" | wc -l"}
output: ^^ duplicates (empty=ok)
real TC count:
      37


---

## Message 240 — ASSISTANT

37 real TC rows, all unique (TC-001..TC-037; the 3 template placeholders excluded by their `REQ-NNN`/`INV-NNN` markers). Now inspect the invariant/policy interaction for unresolved conflicts (§5) and run final validation.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && echo \"=== INV-008 (order) vs POL-002 (stop) tension ===\"; sed -n '/^## INV-008/,/^## INV-009/p' docs/architecture/invariants.md | grep -iE \"order|skip|load\"; echo \"--- POL-003 exception note ---\"; grep -n \"Proposed exception to POL-002\" docs/architecture/runtime-policy-catalog.md"}
output: === INV-008 (order) vs POL-002 (stop) tension ===
## INV-008 — Configured source order is preserved
- **Statement:** When an eligible failure triggers fallback, the configured fallback sources are tried in their configured order, and no source is skipped or reordered.
- **Enforcing component:** the ordered attempt loop in the fallback coordinator (`search/`, ADR-002).
- **Verification:** `test/offline/test_search_fallback.py` — planned cases for C-001 and C-002 (ordered fallback); see ADR-002 §11 and `verification-constraints.md` §7.
- **Fallback:** never reorder or skip; if the configured order cannot be followed, the run receives an explicit failure rather than a silently different order.
--- POL-003 exception note ---
40:**Proposed exception to POL-002 — Pending Team Approval.** POL-002 currently stops the run unconditionally when a declared MCP cannot provide a usable tool. The proposed REQ-008 policy narrows this only for a **fallback** MCP source: when a declared fallback source fails at **load** stage and other validated, usable sources remain, the load failure is recorded and fallback continues instead of terminating the run; when no usable source remains, the run stops as POL-002 describes. This amendment is **not applied** to POL-002 here; it requires team approval (ADR-002 D-1; related REQ-007 U-1 and U-5). Until approved, POL-002 stands as written.


[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && git diff --check && echo \"DIFF_CHECK_CLEAN\"; echo \"=== status --short ===\"; git status --short"}
output: DIFF_CHECK_CLEAN
=== status --short ===
 M docs/architecture/evaluation-table.md
 M docs/architecture/invariants.md
 M docs/architecture/runtime-policy-catalog.md
 M docs/architecture/trace-matrix.md
 M docs/code-governance/structural-constraints.md
 M docs/code-governance/verification-constraints.md
?? docs/architecture/adr/002-search-fallback.md


---

## Message 241 — ASSISTANT

All edits complete. Let me verify ADR-002 §11 renders correctly and confirm the REQ-007 row is untouched, then produce the report.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && sed -n '/^## 11. Verification/,/^## 12/p' docs/architecture/adr/002-search-fallback.md | head -20; echo \"=== REQ-007 row unchanged? ===\"; git diff docs/architecture/trace-matrix.md | grep -c \"+.*REQ-007\\|-.*REQ-007\""}
output: ## 11. Verification

Status of these cases, stated precisely:

- **Planned test cases are documented** as entries in `verification-constraints.md` §7 (`REQ-008 fallback (ADR-002)`), as `TC-027` through `TC-037`.
- **Test implementation is not created:** no `test/offline/test_search_fallback.py` exists yet.
- **Tests are not executed:** none of these cases has been run; there is no pass/fail evidence.

IDs continue after REQ-007's `TC-026` to avoid collision (the module example rows TC-001…TC-003 are placeholders, not real cases).

| Criterion | Verification case | Test name (planned) |
|---|---|---|
| C-001 | TC-027 | `test/offline/test_search_fallback.py::test_primary_failure_uses_fallback` |
| C-002 | TC-028 | `::test_fallbacks_follow_configured_order` |
| C-003 | TC-029 | `::test_all_sources_fail_explicitly` |
| C-004 | TC-030 | `::test_empty_result_does_not_trigger_fallback` |
| C-005 | TC-031 | `::test_ineligible_error_does_not_trigger_fallback` |
| Typed classification (§7) | TC-032 | `::test_error_classification_typed` |
| Load-stage diagnostic contract (§6.1, ASR-008-10) | TC-033 | `::test_mcp_load_stage_failure_recorded` |
| Conditional continuation after load failure (D-1/D-4, ASR-008-08) | TC-037 | `::test_load_failure_continuation_decision` |
=== REQ-007 row unchanged? ===
1


---

## Message 242 — ASSISTANT

The trace diff still contains a REQ-007 change — let me verify it's only the untouched row context, not a modification.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && git diff docs/architecture/trace-matrix.md | grep -E \"^[+-].*REQ-00[78]\""}
output: -| REQ-008 | Search fallback | functional | approved | TBD | INV-005 (Proposed) | Proposed: `search/` | planned: `test/offline/test_search_fallback.py` | TBD |
+| REQ-008 | Search fallback | functional | approved | Ordered fallback over configured Tavily/MCP sources on eligible failures; empty result = success (no fallback); ineligible error stops fallback; all-exhausted yields an explicit aggregate distinct from empty; load-stage vs invocation-stage distinguished; depends on REQ-007 U-5 for the structured load result | INV-005 (Proposed); INV-006, INV-007, INV-008, INV-009 (Proposed); ADR-002 (Proposed); EVAL-002 (Open); POL-003 (Proposed) | Proposed: `search/` fallback coordinator (`SearchRequest`, `SearchSource` adapters, `FallbackCoordinator`, error/failure types, thin tool-facing adapter) | planned: `test/offline/test_search_fallback.py` — C-001→TC-027, C-002→TC-028, C-003→TC-029, C-004→TC-030, C-005→TC-031; TC-032–TC-037 (ADR-002 §11) | TBD |


---

## Message 243 — ASSISTANT

Confirmed: only the REQ-008 row changed (the earlier count of 1 was the pre-existing REQ-008 line matching my regex, not REQ-007). REQ-007 row is untouched.

## 1. Exact changes made

**`docs/architecture/adr/002-search-fallback.md` (§11 only):**
- Replaced the outdated "they do not yet exist in verification-constraints.md" sentence with an explicit three-state statement: **Planned test cases are documented** (TC-027–TC-037 in §7), **test implementation not created** (no `test_search_fallback.py`), **tests not executed**.
- Rewrote the verification table to map each criterion to its documented TC ID (C-001→TC-027 … C-005→TC-031), added TC-037 for the conditional-continuation decision, and aligned all test names with §7.

**`docs/code-governance/verification-constraints.md`:**
- Tightened the section opener to "documented plans only; no test file exists; none has run."
- **Split TC-033** into: **TC-033** = load-stage diagnostic contract (A: records `stage=LOAD`, source never invoked, no continuation decision) and new **TC-037** = conditional continuation after a load failure (B: explicitly conditional on D-1/D-4/U-1/U-5, does not presuppose approval).
- Replaced the single regression note with a **REQ-007 regression** note (unchanged content) plus a separate **REQ-008 regression** note: new fallback config field proposed, MCP load-result contract may change (U-5), shared-contract compatibility must be tested if approved, TC-034 covers no-fallback preservation, and none of it is implemented/executed.

**`docs/architecture/trace-matrix.md` (REQ-008 row only):**
- Made the criterion→case mapping explicit: `C-001→TC-027, C-002→TC-028, C-003→TC-029, C-004→TC-030, C-005→TC-031; TC-032–TC-037`.

No other files changed. ADR-002 was inspected for trailing whitespace (none).

## 2. Updated test coverage

- Documented planned cases now **TC-027 … TC-037** (11 cases), all Planned / Not Implemented / Not Executed.
- LC-001→TC-027, C-002→TC-028, C-003→TC-029, C-004→TC-030, C-005→TC-031; typed classification TC-032; load-stage diagnostic TC-033; no-fallback regression TC-034; auth boundary TC-035; tool dispatch/schema TC-036; **conditional continuation TC-037 (new)**.
- All 37 real TC rows (TC-001…TC-037) are unique.

## 3. Remaining cross-document conflicts

- **INV-008 vs POL-002:** INV-008 forbids skipping a configured source; POL-002 terminates the run when a declared MCP cannot load. If the MCP fallback source cannot load and POL-002 stops the run, the remaining ordered sources are effectively not tried — a tension with INV-008's intent. This is exactly what the proposed POL-002 exception (POL-003 note) and TC-037 address, but it remains **unresolved pending D-1/D-4 approval**; the documents do not silently resolve it.
- **REQ-007 trace row** states "TC-001–TC-025" while the body has TC-001…TC-026. Pre-existing; **reported, not changed** (REQ-007 row left untouched per instruction).
- ADR-002 §11 and the trace row now both reference TC-027–TC-037 consistently; no naming conflict remains.

## 4. Decisions pending team approval

- **D-1 / D-4** — load-vs-invocation split and the conditional POL-002 multi-source exception (TC-037 remains conditional; POL-002 not amended).
- **D-2** — fallback configuration field (name/placement/precedence/default).
- **D-3** — typed classification policy and unclassifiable→ineligible default.
- **D-5** — dependency on REQ-007 U-5 structured load result.
- **D-6** — coordinator behind thin tool adapter + stable tool name.
- **D-7** — all-failed rendering distinct from the empty marker.
- **D-8** — missing-auth-config vs rejected-credential boundary.

## 5. Git status

```
 M docs/architecture/evaluation-table.md
 M docs/architecture/invariants.md
 M docs/architecture/runtime-policy-catalog.md
 M docs/architecture/trace-matrix.md
 M docs/code-governance/structural-constraints.md
 M docs/code-governance/verification-constraints.md
?? docs/architecture/adr/002-search-fallback.md
```
`git diff --check`: **CLEAN**. (The other listed files were edited in the prior integration task; this task modified only ADR-002, trace-matrix, and verification-constraints.)

## 6. Ready for AI evidence logging and SA Review submission?

**Not yet.** Internal consistency of EVAL-002 / ADR-002 / shared documents is now sound, but before SA Review submission:
- Decisions D-1…D-8 must be presented for team decision; several (D-1, D-4, D-5) gate POL-002 wording and the TC-037 expectation.
- The pre-existing REQ-007 trace-row TC range mismatch (TC-025 vs TC-026) should be corrected in a REQ-007 maintenance edit (out of this task's scope).
- AI-use logging (`docs/ai-use-log.yaml`) and the SA review record (`docs/review-memo.md`, `SA-NNN`) still need to be drafted/applied by humans — not done here.
- Nothing has been committed or pushed.

Stopping without committing or pushing.

---

## Message 244 — USER

Prepare the REQ-008 AI-use evidence and pre-commit audit.

Current branch: `docs/sa-search-fallback`.

Read the repository's actual `docs/ai-use-log.yaml` format, transcript naming conventions, and existing REQ-007 evidence records before making changes.

First, identify the current OpenCode session ID and determine whether the full REQ-008 design conversation is contained in one session or multiple sessions.

Do not invent session IDs, transcript content, tool outputs, approval records, or timestamps.

## 1. Evidence preparation

Identify all relevant REQ-008 OpenCode interactions, including:

- ADD Iteration 1.
- ADD Iteration 2.
- EVAL-002 and ADR-002 drafting.
- Consistency repair.
- Shared architecture document integration.
- Final consistency review.

Determine which interactions can be exported from the available OpenCode session history.

If any sessions are unavailable, report the gap explicitly.

## 2. Transcript export

Export the actual OpenCode session evidence using the supported OpenCode export mechanism.

Preserve:

- User prompts.
- Assistant responses.
- Tool calls and relevant tool outputs.
- Document edits.
- Validation commands and their results.

Inspect the export for credentials, tokens, private keys, and sensitive environment values.

Do not silently remove evidence needed to understand the architecture decisions.

Use a sanitized repository transcript with clearly documented redactions.

## 3. AI-use log

Create the next available AI-use entry using the repository's existing YAML schema.

Include:

- Actual date.
- Member: sszfot.
- REQ-008 purpose.
- AI-assisted tasks.
- Files affected.
- Human review and corrections.
- Actual repository-relative transcript path.
- Status of architecture approval.

Do not claim that tests ran, source code was implemented, or SA Review was approved.

## 4. Pre-commit audit

Check:

- `git status --short`
- `git diff --check`
- `git diff --stat`
- All REQ-008 document references.
- Unique INV, POL, and TC identifiers.
- No credentials in committed evidence.
- No implementation or test code changes.
- ADR-002 remains Proposed.
- EVAL-002 remains Open.
- D-1 through D-8 remain pending.

Also report the existing REQ-007 trace-row TC range mismatch without changing unrelated REQ-007 content.

## 5. Scope

You may edit only:

- `docs/ai-use-log.yaml`
- REQ-008 transcript evidence files under the repository's existing transcript directory.

Do not modify architecture documents, requirements, implementation, tests, or review records.

Do not commit, push, or create a PR.

Stop and report the evidence paths, AI-use entry ID, redaction summary, validation results, and any unresolved issues requiring human attention.

---

## Message 245 — ASSISTANT

I'm now in build mode. Let me first inspect the actual evidence infrastructure before creating anything.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && ls -la transcripts/ && echo \"=== ai-use tail ===\" && tail -40 docs/ai-use-log.yaml"}
output: total 1896
drwxr-xr-x   6 sft  staff     192 17 11 18:18 .
drwxr-xr-x  31 sft  staff     992 17 11 18:06 ..
-rw-r--r--   1 sft  staff   84529 17 11 18:18 60725623-ChensihanLIU-AIU009.md
-rw-r--r--   1 sft  staff  881135 17 11 18:18 60725623-ChensihanLIU.md
-rw-r--r--   1 sft  staff       0 13 11 16:47 61061690_ZHANG Kaidi.md
-rw-r--r--   1 sft  staff       0 13 11 16:47 student-id_name.md
=== ai-use tail ===
      architectures. The initial documents were reviewed against
      REQ-007 and the source code. Subsequent refinements are
      recorded in AIU-009. The architecture remains Proposed
      pending SA Review.
    transcript: transcripts/60725623-ChensihanLIU.md


      - id: AIU-009
        date: "2026-11-16"
        member: sszfot
        purpose: >-
          Review and refine the proposed REQ-007 software architecture,
          including configuration validation, MCP runtime handling,
          module boundaries, and verification coverage.
        prompt: >-
          Audit and refine ADR-001 and the related REQ-007 architecture
          artifacts against the existing implementation and acceptance
          criteria. Correct environment precedence and configuration
          snapshot handling, clarify MCP loading responsibilities,
          strengthen the search capability predicate, and expand the
          verification matrix. Keep all unresolved decisions open and
          make no implementation or test changes.
        requirements: [ REQ-007 ]
        artif

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && which opencode 2>/dev/null; opencode --version 2>/dev/null; echo \"---session dirs---\"; ls -d ~/.local/share/opencode/* 2>/dev/null; ls -d ~/.config/opencode 2>/dev/null"}
output: /opt/homebrew/bin/opencode
1.19.0
---session dirs---
[LOCAL_HOME]/.local/share/opencode/log
[LOCAL_HOME]/.local/share/opencode/opencode.db
[LOCAL_HOME]/.local/share/opencode/opencode.db-shm
[LOCAL_HOME]/.local/share/opencode/opencode.db-wal
[LOCAL_HOME]/.local/share/opencode/repos
[LOCAL_HOME]/.local/share/opencode/snapshot
[LOCAL_HOME]/.local/share/opencode/tool-output
[LOCAL_HOME]/.config/opencode


---

## Message 246 — ASSISTANT

There's an existing transcript naming pattern `<studentid>-<Name>.md` and `-AIU009.md`. Let me understand how those were produced and identify the current session. Let me check the DB/session mechanism and the existing transcript format.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && head -50 transcripts/60725623-ChensihanLIU.md; echo \"=== AIU009 transcript head ===\"; head -30 transcripts/60725623-ChensihanLIU-AIU009.md"}
output: # REQ-007 — Full OpenCode Agent Transcript

- Session ID: ses_e2bdd7ea1fferC4tLbkCJeovtC
- Total messages: 68
- Source: Original OpenCode JSON export
- Note: This document contains unredacted tool inputs and outputs.

---

## Message 1 — USER

### Part 1 — text

```text
I am responsible for the approved REQ-007, associated with upstream Issue #250.

My working branch is docs/sa-search-provider.

We are now performing the first iteration of Attribute-Driven Design (ADD).

Please read the complete REQ-007 from docs/req/requirements.yaml, AGENTS.md, the architecture templates, and the existing search-related source code.

Analyze these proposed architectural drivers:

- ASR-007-01: Validate search configuration before any research or search call.
- ASR-007-02: Enforce compatibility between native search providers and research models.
- ASR-007-03: Correctly account for MCP tools when determining whether research has search capability.
- ASR-007-04: Keep search configuration documentation consistent with actual system behavior.

These ASR identifiers are provisional. Validate and revise them based on repository evidence.

Compare three candidate designs:

A. Validation directly inside the existing research graph entry point.

B. A centralized search configuration validator called before research starts.

C. A configuration validation layer integrated with existing search tool assembly.

For each design, evaluate:
1. Satisfaction of REQ-007 C-001 through C-005.
2. Modularity, cohe

[tool: bash | status=completed]
input: {"command": "opencode --help 2>&1 | head -40; echo \"=== export help ===\"; opencode export --help 2>&1 | head -20"}
output: ⠀                                ▄
█▀▀█ █▀▀█ █▀▀█ █▀▀▄ █▀▀▀ █▀▀█ █▀▀█ █▀▀█
█  █ █  █ █▀▀▀ █  █ █    █  █ █  █ █▀▀▀
▀▀▀▀ █▀▀▀ ▀▀▀▀ ▀  ▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀ ▀▀▀▀

Commands:
  opencode completion          generate shell completion script
  opencode acp                 start ACP (Agent Client Protocol) server
  opencode mcp                 manage MCP (Model Context Protocol) servers
  opencode [project]           start opencode tui                                          [default]
  opencode attach <url>        attach to a running opencode server
  opencode run [message..]     run opencode with a message
  opencode debug               debugging and troubleshooting tools
  opencode providers           manage AI providers and credentials                   [aliases: auth]
  opencode agent               manage agents
  opencode upgrade [target]    upgrade opencode to the latest or a specific version
  opencode uninstall           uninstall opencode and remove all related files
  opencode serve               starts a headless opencode server
  opencode web                 start opencode server and open web interface
  opencode models [provider]   list all available models
  opencode stats               show token usage and cost statistics
  opencode export [sessionID]  export session data as JSON
  opencode import <file>       import session data from JSON file or URL
  opencode github              manage GitHub agent
  opencode pr <number>         fetch and checkout a GitHub PR bran

---

## Message 247 — ASSISTANT

`opencode export` with `--sanitize` exists. I need the current session ID. Let me list sessions to find the active REQ-008 one.

[tool: bash | status=completed]
input: {"command": "opencode session --help 2>&1 | head -25"}
output: opencode session

manage sessions

Commands:
  opencode session list                list sessions
  opencode session delete <sessionID>  delete a session

Options:
  -h, --help        show help                                                              [boolean]
  -v, --version     show version number                                                    [boolean]
      --print-logs  print logs to stderr                                                   [boolean]
      --log-level   log level                   [string] [choices: "DEBUG", "INFO", "WARN", "ERROR"]
      --pure        run without external plugins                                           [boolean]

[tool: bash | status=completed]
input: {"command": "opencode db --help 2>&1 | head -30"}
output: opencode db

database tools

Commands:
  opencode db [query]     open an interactive sqlite3 shell or run a query                 [default]
  opencode db path        print the database path

Positionals:
  query  SQL query to execute                                                               [string]

Options:
  -h, --help        show help                                                              [boolean]
  -v, --version     show version number                                                    [boolean]
      --print-logs  print logs to stderr                                                   [boolean]
      --log-level   log level                   [string] [choices: "DEBUG", "INFO", "WARN", "ERROR"]
      --pure        run without external plugins                                           [boolean]
      --format      Output format                 [string] [choices: "json", "tsv"] [default: "tsv"]

---

## Message 248 — ASSISTANT

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode session list 2>&1 | head -40"}
output: Session ID                      Title                         Updated
─────────────────────────────────────────────────────────────────────
ses_e2bdd7ea1fferC4tLbkCJeovtC  REQ-007 search config ADD 分析  6:45 PM


---

## Message 249 — ASSISTANT

Only one session is listed — `ses_e2bdd7ea1fferC4tLbkCJeovtC`, the REQ-007 session. My current REQ-008 conversation appears to be within this same session (session titles can be stale) or the current session isn't yet persisted in this list. Let me query the DB directly to confirm whether the REQ-008 conversation is stored and under which session.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode db \"SELECT name FROM sqlite_master WHERE type='table'\" 2>&1 | head -40"}
output: name
workspace
data_migration
account_state
account
control_account
credential
event_sequence
event
permission
project_directory
project
message
part
session_context_epoch
session_input
session_message
session
todo
session_share
migration


---

## Message 250 — ASSISTANT

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode db \"SELECT sessionID, COUNT(*) c FROM session_message GROUP BY sessionID\" 2>&1 | head; echo \"=== sessions table ===\"; opencode db \"SELECT id, title, datetime(time_updated/1000,'unixepoch') upd FROM session ORDER BY time_updated DESC LIMIT 10\" 2>&1 | head"}
output: [91m[1mError: [0mUnexpected error

no such column: sessionID
=== sessions table ===
id	title	upd
ses_e2bdd7ea1fferC4tLbkCJeovtC	REQ-007 search config ADD 分析	2026-11-17 10:46:08
ses_ec67f09c0ffePMKa3NOej7kIcg	CS5351 Phase 2 verification and fixes	2026-10-14 13:16:33
ses_ec6c39762ffeutkbYb2EPl3GTd	CS5351 Phase 2 audit summary	2026-10-14 08:14:48
ses_ecc32f699ffekcdRV1Hr4nR5bI	CS5351 Phase 2 verification run	2026-10-13 15:20:43
ses_ecf51936fffeCBHnplzPJeOVhI	CS5351 Phase 2 verification and fixes	2026-10-13 05:39:46
ses_ecfb95a67ffeZJZmGiMIi3neeG	CS5351 Phase 2 verification script update	2026-10-12 15:04:12
ses_ed0b26a2fffeq9IaVLQtjOnv5W	Phase 2 V1 ReAct loop unification	2026-10-12 13:14:35
ses_ed0bb7a7cffe3YJiwEdVydrEir	CS5351 Assessment 2 Phase 2 audit and ReAct plan	2026-10-12 08:42:00
ses_f36e62282ffeVAk4zobXQSIUnI	V10 demo.py verification checklist	2026-09-23 02:48:04


---

## Message 251 — ASSISTANT

The current session is `ses_e2bdd7ea1fferC4tLbkCJeovtC` (updated today 10:46 UTC). Its title is stale ("REQ-007 search config ADD"). Let me confirm the REQ-008 messages are in this session and find their range.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode db \"SELECT name FROM pragma_table_info('session_message')\" 2>&1 | head; echo \"=== session_message columns of message? ===\"; opencode db \"SELECT name FROM pragma_table_info('message')\" 2>&1 | head -20"}
output: name
id
session_id
type
seq
time_created
time_updated
data
=== session_message columns of message? ===
name
id
session_id
time_created
time_updated
data


---

## Message 252 — ASSISTANT

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode db \"SELECT session_id, COUNT(*) FROM session_message GROUP BY session_id ORDER BY COUNT(*) DESC LIMIT 5\" 2>&1 | head; echo \"=== count for current session ===\"; opencode db \"SELECT COUNT(*) FROM session_message WHERE session_id='ses_e2bdd7ea1fferC4tLbkCJeovtC'\" 2>&1"}
output: === count for current session ===
COUNT(*)
0


---

## Message 253 — ASSISTANT

The `session_message` table is empty — the live conversation is buffered in `part`/`event`, not yet finalized into `session_message` (this session is still active). Let me check the `part` table for the current session's content.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode db \"SELECT name FROM pragma_table_info('part')\" 2>&1 | head -20; echo \"=== part counts by session ===\"; opencode db \"SELECT session_id, COUNT(*) FROM part GROUP BY session_id ORDER BY COUNT(*) DESC LIMIT 5\" 2>&1 | head"}
output: name
id
message_id
session_id
time_created
time_updated
data
=== part counts by session ===
session_id	COUNT(*)
ses_e2bdd7ea1fferC4tLbkCJeovtC	1014
ses_f3cb1504effepz8tASXxhcXZpN	960
ses_ecfb95a67ffeZJZmGiMIi3neeG	606
ses_ecf51936fffeCBHnplzPJeOVhI	585
ses_ecc32f699ffekcdRV1Hr4nR5bI	580


---

## Message 254 — ASSISTANT

The current session (`ses_e2bdd7ea1fferC4tLbkCJeovtC`) has 1014 parts — it contains the full conversation including REQ-008. This is the same session as REQ-007's earlier work; it's one continuous session. Let me confirm the REQ-008 prompts are present and locate their start.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode db \"SELECT COUNT(*) FROM part WHERE session_id='ses_e2bdd7ea1fferC4tLbkCJeovtC' AND data LIKE '%REQ-008%'\" 2>&1; echo \"=== first req-008 text part ===\"; opencode db \"SELECT id, substr(data,1,120) FROM part WHERE session_id='ses_e2bdd7ea1fferC4tLbkCJeovtC' AND data LIKE '%REQ-008: Search shall fall back%' ORDER BY time_created LIMIT 1\" 2>&1"}
output: COUNT(*)
136
=== first req-008 text part ===
id	substr(data,1,120)
prt_1e8f9ff6f001T2O51Hh1492PeA	{"type":"text","text":"You are assisting with the Software Architecture (SA) phase of the Open_Deepsearch_ULTRA project.


---

## Message 255 — ASSISTANT

Confirmed: the REQ-008 design conversation is contained in the **same single session** `ses_e2bdd7ea1fferC4tLbkCJeovtC`, starting at part `prt_1e8f9ff6f001T2O51Hh1492PeA`. Now let me use the official export with `--sanitize`.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && mkdir -p /tmp/req008_export && opencode export ses_e2bdd7ea1fferC4tLbkCJeovtC --sanitize > /tmp/req008_export/full.json 2>/tmp/req008_export/err.log; echo \"exit=$?\"; ls -la /tmp/req008_export/; echo \"=== err ===\"; cat /tmp/req008_export/err.log | head"}
output: exit=0
total 1568
drwxr-xr-x@  4 sft   wheel     128 17 11 18:47 .
drwxrwxrwt  16 root  wheel     512 17 11 18:47 ..
-rw-r--r--@  1 sft   wheel      50 17 11 18:47 err.log
-rw-r--r--@  1 sft   wheel  796661 17 11 18:47 full.json
=== err ===
Exporting session: ses_e2bdd7ea1fferC4tLbkCJeovtC


---

## Message 256 — ASSISTANT

Export succeeded (796KB sanitized JSON). Let me verify the sanitize worked and inspect structure + check for leaked secrets.

[tool: bash | status=completed]
input: {"command": "cd /tmp/req008_export && uv run --no-project python - <<'PY'\nimport json\nd=json.load(open(\"full.json\"))\nprint(\"top keys:\", list(d.keys()) if isinstance(d,dict) else type(d))\nmsgs = d.get(\"messages\") if isinstance(d,dict) else d\nprint(\"message count:\", len(msgs))\nif msgs:\n    print(\"first msg keys:\", list(msgs[0].keys()))\n    print(\"roles:\", {m.get(\"role\") or m.get(\"info\",{}).get(\"role\") for m in msgs})\nPY"}
output: top keys: ['info', 'messages']
message count: 255
first msg keys: ['info', 'parts']
roles: {'assistant', 'user'}


[tool: bash | status=completed]
input: {"command": "cd /tmp/req008_export && grep -oE \"sk-[A-Za-z0-9]{10,}|tvly-[A-Za-z0-9]{10,}|1354422486@qq\\.com|Bearer [A-Za-z0-9._-]{10,}|AKIA[0-9A-Z]{12,}\" full.json | sort | uniq -c | head"}
output: (no output)

---

## Message 257 — ASSISTANT

Sanitized export has 255 messages, no leaked keys/emails found. Let me check whether the sanitize redacted the previously-seen email, and inspect how much of this is REQ-007 vs REQ-008 (to scope the REQ-008 transcript). Since the whole session is one, I'll extract from the first REQ-008 user message onward.

[tool: bash | status=completed]
input: {"command": "cd /tmp/req008_export && uv run --no-project python - <<'PY'\nimport json\nd=json.load(open(\"full.json\"))\nmsgs=d[\"messages\"]\ndef txt(m):\n    out=[]\n    for p in m.get(\"parts\",[]):\n        if p.get(\"type\")==\"text\": out.append(p.get(\"text\",\"\"))\n    return \"\\n\".join(out)\n# find first REQ-008 assistant-side prompt\nstart=None\nfor i,m in enumerate(msgs):\n    t=txt(m)\n    if \"REQ-008: Search shall fall back\" in t or (\"REQ-008\" in t and \"fall back to configured\" in t):\n        start=i; break\nprint(\"first REQ-008 msg index:\", start, \"role:\", msgs[start][\"info\"][\"role\"] if start is not None else None)\nprint(\"total:\", len(msgs))\n# count req-008 mentions per side after start\nif start is not None:\n    print(\"msgs from start:\", len(msgs)-start)\nPY"}
output: first REQ-008 msg index: None role: None
total: 255


---

## Message 258 — ASSISTANT

The sanitized export may have redacted or truncated long text. Let me inspect an actual message's text content to understand the sanitized format.

[tool: bash | status=completed]
input: {"command": "cd /tmp/req008_export && uv run --no-project python - <<'PY'\nimport json\nd=json.load(open(\"full.json\"))\nmsgs=d[\"messages\"]\nfor i in [0,1]:\n    m=msgs[i]\n    print(f\"--- msg {i} role={m['info'].get('role')} parts={len(m.get('parts',[]))} ---\")\n    for p in m.get(\"parts\",[])[:3]:\n        print(\"  type:\", p.get(\"type\"), \"| keys:\", list(p.keys()))\n        if p.get(\"type\")==\"text\":\n            print(\"  text[:200]:\", repr(p.get(\"text\",\"\")[:200]))\nPY"}
output: --- msg 0 role=user parts=1 ---
  type: text | keys: ['type', 'text', 'id', 'sessionID', 'messageID']
  text[:200]: '[redacted:text:prt_1d4228172001q3ONEdHBR5ojYr]'
--- msg 1 role=assistant parts=5 ---
  type: step-start | keys: ['snapshot', 'type', 'id', 'sessionID', 'messageID']
  type: text | keys: ['type', 'text', 'time', 'id', 'sessionID', 'messageID']
  text[:200]: '[redacted:text:prt_1d4228f9c001XPN1JbM1WzL3m2]'
  type: tool | keys: ['type', 'tool', 'callID', 'state', 'id', 'sessionID', 'messageID']


---

## Message 259 — ASSISTANT

The `--sanitize` flag over-redacts **all** text (including user prompts and assistant reasoning), making the transcript useless for understanding architecture decisions. That violates the task's requirement to preserve evidence. I'll produce the transcript from the DB parts directly, then apply targeted redaction (secrets only), matching the existing REQ-007 transcript style.

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode db \"SELECT id FROM part WHERE session_id='ses_e2bdd7ea1fferC4tLbkCJeovtC' AND data LIKE '%REQ-008: Search shall fall back%' ORDER BY time_created LIMIT 1\" 2>&1; echo \"=== which message holds it ===\"; opencode db \"SELECT message_id, time_created FROM part WHERE id='prt_1e8f9ff6f001T2O51Hh1492PeA'\" 2>&1"}
output: id
prt_1e8f9ff6f001T2O51Hh1492PeA
=== which message holds it ===
message_id	time_created
msg_1e8f9ff6900122nw97Ycz1h9Z1	1794910060401


---

## Message 260 — ASSISTANT

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode db \"SELECT message_id, type, time_created FROM part WHERE session_id='ses_e2bdd7ea1fferC4tLbkCJeovtC' AND time_created >= 1794910060401 ORDER BY time_created\" --format json 2>/tmp/req008_export/q.err > /tmp/req008_export/req008_parts.json; echo \"exit=$?\"; uv run --no-project python -c \"import json;d=json.load(open('/tmp/req008_export/req008_parts.json'));print('parts:',len(d))\""}
output: exit=1
Traceback (most recent call last):
  File "<string>", line 1, in <module>
  File "/opt/homebrew/Cellar/python@3.12/3.12.14/Frameworks/Python.framework/Versions/3.12/lib/python3.12/json/__init__.py", line 293, in load
    return loads(fp.read(),
           ^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.12/3.12.14/Frameworks/Python.framework/Versions/3.12/lib/python3.12/json/__init__.py", line 346, in loads
    return _default_decoder.decode(s)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.12/3.12.14/Frameworks/Python.framework/Versions/3.12/lib/python3.12/json/decoder.py", line 338, in decode
    obj, end = self.raw_decode(s, idx=_w(s, 0).end())
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/opt/homebrew/Cellar/python@3.12/3.12.14/Frameworks/Python.framework/Versions/3.12/lib/python3.12/json/decoder.py", line 356, in raw_decode
    raise JSONDecodeError("Expecting value", s, err.value) from None
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)


---

## Message 261 — ASSISTANT

[tool: bash | status=completed]
input: {"command": "cat /tmp/req008_export/q.err | head; echo \"=== try tsv ===\"; cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && opencode db \"SELECT COUNT(*) FROM part WHERE session_id='ses_e2bdd7ea1fferC4tLbkCJeovtC' AND time_created >= 1794910060401\" 2>&1"}
output: [91m[1mError: [0mUnexpected error

no such column: type
=== try tsv ===
COUNT(*)
395


---

## Message 262 — ASSISTANT

395 parts from the REQ-008 start onward. I'll query parts with full data via a script and render the transcript, applying targeted redaction. Let me write an extraction script using the sqlite DB directly (via the opencode db query interface, outputting the JSON `data` column).

[tool: bash | status=completed]
input: {"command": "cd [LOCAL_HOME]/Documents/Open_Deepsearch_ULTRA && dbfile=$(opencode db path 2>/dev/null); echo \"db: $dbfile\"; ls -la \"$dbfile\" 2>&1"}
output: db: [LOCAL_HOME]/.local/share/opencode/opencode.db
-rw-r--r--@ 1 sft  staff  65515520 17 11 18:49 [LOCAL_HOME]/.local/share/opencode/opencode.db


---

## Message 263 — ASSISTANT

I'll read the DB directly with a Python script (the WAL is live; opening read-only avoids disturbing the running session). This extracts parts for the REQ-008 range.

[tool: write | status=completed]
input: {"content": "import json, sqlite3, sys, re\n\nDB = \"[LOCAL_HOME]/.local/share/opencode/opencode.db\"\nSID = \"ses_e2bdd7ea1fferC4tLbkCJeovtC\"\nSTART_MSG = \"msg_1e8f9ff6900122nw97Ycz1h9Z1\"  # first REQ-008 user message\n\ncon = sqlite3.connect(f\"file:{DB}?mode=ro\", uri=True)\ncur = con.cursor()\n\n# Order messages by their first part time_created; find start index\nrows = cur.execute(\n    \"SELECT id, time_created FROM message WHERE session_id=? ORDER BY time_created\", (SID,)\n).fetchall()\nstart_idx = None\nfor i, (mid, _t) in enumerate(rows):\n    if mid == START_MSG:\n        start_idx = i\n        break\nif start_idx is None:\n    print(\"START_MSG not found\", file=sys.stderr)\n    sys.exit(2)\n\nmsgs = rows[start_idx:]\nprint(f\"total msgs in session: {len(rows)}  req008 msgs: {len(msgs)}\", file=sys.stderr)\n\ndef get_parts(mid):\n    recs = cur.execute(\n        \"SELECT id, time_created, data FROM part WHERE message_id=? ORDER BY time_created\",\n        (mid,),\n    ).fetchall()\n    out = []\n    for pid, tc, data in recs:\n        try:\n            out.append((pid, tc, json.loads(data)))\n        except Exception:\n            pass\n    return out\n\n# Build message list\nexport = []\nfor idx, (mid, mt) in enumerate(msgs, start=start_idx + 1):\n    info = cur.execute(\"SELECT data FROM message WHERE id=?\", (mid,)).fetchone()\n    try:\n        info_d = json.loads(info[0]) if info else {}\n    except Exception:\n        info_d = {}\n    role = info_d.get(\"role\", \"?\")\n    export.append({\"index\": idx, \"role\": role, \"parts\": get_parts(mid)})\n\njson.dump(export, open(\"/tmp/req008_export/req008_msgs.json\", \"w\"), ensure_ascii=False)\nprint(\"wrote req008_msgs.json\", file=sys.stderr)\n", "filePath": "/tmp/req008_export/extract.py"}
output: Wrote file successfully.

---

## Message 264 — ASSISTANT

[tool: bash | status=running]
input: {"command": "cd /tmp/req008_export && python3 extract.py 2>&1 | tail; ls -la req008_msgs.json 2>&1"}

---
