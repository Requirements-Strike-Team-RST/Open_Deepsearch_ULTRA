"""Main LangGraph implementation for the Deep Research agent."""

import asyncio
from typing import Literal

from langchain.chat_models import init_chat_model
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
    filter_messages,
    get_buffer_string,
)
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph
from langgraph.types import Command

from open_deep_research.configuration import (
    Configuration,
)
from open_deep_research.context.recovery import (
    CompressionFailed,
    compress_with_recovery,
)
from open_deep_research.delivery.execution import run_delegations
from open_deep_research.delivery.outcome import (
    assess_research,
    finish_outcome,
    render_limitations,
)
from open_deep_research.orchestration.contracts import (
    BUDGET_TOOL_MESSAGE,
    DELEGATION_TOOL_NAME,
    THINK_TOOL_NAME,
    build_task_result,
    build_task_specs,
    extract_urls,
    render_notes,
    render_result_message,
    render_task_brief,
)
from open_deep_research.orchestration.termination import select_exit
from open_deep_research.prompts import (
    clarify_with_user_instructions,
    compress_research_simple_human_message,
    compress_research_system_prompt,
    final_report_generation_prompt,
    lead_researcher_prompt,
    lead_researcher_task_contract_prompt,
    research_system_prompt,
    task_findings_instruction,
    transform_messages_into_research_topic_prompt,
)
from open_deep_research.search.fallback import apply_search_fallback
from open_deep_research.search.validation import (
    load_search_config,
    require_search_tools,
)
from open_deep_research.state import (
    AgentInputState,
    AgentState,
    ClarifyWithUser,
    ConductResearch,
    ConductResearchTask,
    ResearchComplete,
    ResearcherOutputState,
    ResearcherState,
    ResearchQuestion,
    SupervisorState,
    TaskResult,
    TaskSpec,
    unanswered_questions,
)
from open_deep_research.utils import (
    anthropic_websearch_called,
    get_all_tools,
    get_api_key_for_model,
    get_model_token_limit,
    get_notes_from_tool_calls,
    get_today_str,
    is_token_limit_exceeded,
    openai_websearch_called,
    remove_up_to_last_ai_message,
    think_tool,
)

# Initialize a configurable model that we will use throughout the agent
configurable_model = init_chat_model(
    configurable_fields=("model", "max_tokens", "api_key"),
)

# Baseline text of a compression that did not succeed.
COMPRESSION_PLACEHOLDER = "Error synthesizing research report: Maximum retries exceeded"
# The tool a supervisor calls to request the end of research (REQ-003).
COMPLETE_TOOL_NAME = "ResearchComplete"
NOT_RUN_REASON = "the research loop reached its iteration cap before this task could run"


def _override(value: list) -> dict:
    """Return an ``override_reducer`` update that replaces a list field."""
    return {"type": "override", "value": value}


def _message_text(message) -> str:
    """Return a message's text, joining the text parts of block content."""
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    parts = []
    for block in content or []:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, dict) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))
    return "\n".join(parts)

async def clarify_with_user(state: AgentState, config: RunnableConfig) -> Command[Literal["write_research_brief", "__end__"]]:
    """Analyze user messages and ask clarifying questions if the research scope is unclear.
    
    This function determines whether the user's request needs clarification before proceeding
    with research. If clarification is disabled or not needed, it proceeds directly to research.
    
    Args:
        state: Current agent state containing user messages
        config: Runtime configuration with model settings and preferences
        
    Returns:
        Command to either end with a clarifying question or proceed to research brief
    """
    # Step 0: Validate the search configuration before any model call (REQ-007,
    # ADR-006 §3.4, INV-005): an invalid setting, or a run whose tools hold no
    # search tool, stops here instead of starting research without search.
    configurable = load_search_config(config)
    require_search_tools(await get_all_tools(config), configurable.search_api)

    # Step 1: Check if clarification is enabled in configuration
    if not configurable.allow_clarification:
        # Skip clarification step and proceed directly to research
        return Command(goto="write_research_brief")
    
    # Step 2: Prepare the model for structured clarification analysis
    messages = state["messages"]
    model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }
    
    # Configure model with structured output and retry logic
    clarification_model = (
        configurable_model
        .with_structured_output(ClarifyWithUser)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(model_config)
    )
    
    # Step 3: Analyze whether clarification is needed
    prompt_content = clarify_with_user_instructions.format(
        messages=get_buffer_string(messages), 
        date=get_today_str()
    )
    response = await clarification_model.ainvoke([HumanMessage(content=prompt_content)])
    
    # Step 4: Route based on clarification analysis
    if response.need_clarification:
        # End with clarifying question for user
        return Command(
            goto=END, 
            update={"messages": [AIMessage(content=response.question)]}
        )
    else:
        # Proceed to research with verification message
        return Command(
            goto="write_research_brief", 
            update={"messages": [AIMessage(content=response.verification)]}
        )


async def write_research_brief(state: AgentState, config: RunnableConfig) -> Command[Literal["research_supervisor"]]:
    """Transform user messages into a structured research brief and initialize supervisor.
    
    This function analyzes the user's messages and generates a focused research brief
    that will guide the research supervisor. It also sets up the initial supervisor
    context with appropriate prompts and instructions.
    
    Args:
        state: Current agent state containing user messages
        config: Runtime configuration with model settings
        
    Returns:
        Command to proceed to research supervisor with initialized context
    """
    # Step 1: Set up the research model for structured output
    configurable = Configuration.from_runnable_config(config)
    research_model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }
    
    # Configure model for structured research question generation
    research_model = (
        configurable_model
        .with_structured_output(ResearchQuestion)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(research_model_config)
    )
    
    # Step 2: Generate structured research brief from user messages
    prompt_content = transform_messages_into_research_topic_prompt.format(
        messages=get_buffer_string(state.get("messages", [])),
        date=get_today_str()
    )
    response = await research_model.ainvoke([HumanMessage(content=prompt_content)])
    
    # Step 3: Initialize supervisor with research brief and instructions
    # (REQ-001, ADR-001 §9 step 4: the flag-on variant explains typed delegations)
    supervisor_prompt = (
        lead_researcher_task_contract_prompt
        if configurable.task_contract_enabled
        else lead_researcher_prompt
    )
    supervisor_system_prompt = supervisor_prompt.format(
        date=get_today_str(),
        max_concurrent_research_units=configurable.max_concurrent_research_units,
        max_researcher_iterations=configurable.max_researcher_iterations
    )
    
    update = {
        "research_brief": response.research_brief,
        "supervisor_messages": {
            "type": "override",
            "value": [
                SystemMessage(content=supervisor_system_prompt),
                HumanMessage(content=response.research_brief)
            ]
        }
    }
    if configurable.task_contract_enabled:
        # REQ-001, REQ-003, ADR-001 §9 step 5: every run starts with an empty loop
        # result, so a thread's earlier run cannot end or fill this one.
        update.update({
            "task_results": _override([]),
            "exit_reason": None,
            "exit_detail": "",
        })
    return Command(goto="research_supervisor", update=update)


async def supervisor(state: SupervisorState, config: RunnableConfig) -> Command[Literal["supervisor_tools", "__end__"]]:
    """Lead research supervisor that plans research strategy and delegates to researchers.
    
    The supervisor analyzes the research brief and decides how to break down the research
    into manageable tasks. It can use think_tool for strategic planning, ConductResearch
    to delegate tasks to sub-researchers, or ResearchComplete when satisfied with findings.
    
    Args:
        state: Current supervisor state with messages and research context
        config: Runtime configuration with model settings
        
    Returns:
        Command to proceed to supervisor_tools for tool execution
    """
    # Step 1: Configure the supervisor model with available tools
    configurable = Configuration.from_runnable_config(config)
    research_model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }
    
    # Available tools: research delegation, completion signaling, and strategic thinking.
    # REQ-001, ADR-001 §3.1: with the task contract on, the delegation tool is the
    # typed ConductResearchTask, whose schema title stays ConductResearch.
    delegation_tool = (
        ConductResearchTask if configurable.task_contract_enabled else ConductResearch
    )
    lead_researcher_tools = [delegation_tool, ResearchComplete, think_tool]
    
    # Configure model with tools, retry logic, and model settings
    research_model = (
        configurable_model
        .bind_tools(lead_researcher_tools)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(research_model_config)
    )
    
    # Step 2: Generate supervisor response based on current context
    supervisor_messages = state.get("supervisor_messages", [])
    try:
        response = await research_model.ainvoke(supervisor_messages)
    except Exception as exc:
        if not configurable.task_contract_enabled:
            raise
        # REQ-003, ADR-001 §3.4 step 5, POL-011: after its retries a failing
        # supervisor ends the loop with the reason select_exit returns.
        return _supervisor_failure_exit(state, configurable, exc)
    
    # Step 3: Update state and proceed to tool execution
    return Command(
        goto="supervisor_tools",
        update={
            "supervisor_messages": [response],
            "research_iterations": state.get("research_iterations", 0) + 1
        }
    )

def _next_task_number(results) -> int:
    """Return the number of the run's next task id; ids are T1, T2, ... per run (ADR-001 §3.1)."""
    numbers = [
        int(str(result.task_id)[1:])
        for result in results
        if str(getattr(result, "task_id", "")).startswith("T")
        and str(result.task_id)[1:].isdigit()
    ]
    return max(numbers, default=0) + 1


def _exit_detail(reason: str, results: list, configurable: Configuration) -> str:
    """Return the short reason of an exit other than ``covered`` (ADR-001 §3.4 step 7)."""
    if reason == "covered":
        return ""
    if reason == "budget_exhausted":
        detail = (
            "the research loop reached its iteration cap "
            f"(max_researcher_iterations={configurable.max_researcher_iterations})"
        )
    elif reason == "stalled":
        detail = "two supervisor turns in a row added no answered required question"
    else:
        detail = "the supervisor failed"
    missing = unanswered_questions(results)
    if missing:
        detail += "; unanswered required questions: " + "; ".join(missing)
    return detail


def _loop_exit_update(results: list, reason: str, detail: str, stalled_turns: int) -> dict:
    """Return the fields every loop exit writes (ADR-001 §3.4 step 7).

    ``notes`` are replaced by the counted findings of the complete and partial
    tasks of the whole run, so no summary or failure text reaches them
    (REQ-002 C-007, INV-002).
    """
    return {
        "exit_reason": reason,
        "exit_detail": detail,
        "notes": _override(render_notes(results)),
        "stalled_turns": stalled_turns,
    }


def _supervisor_failure_exit(
    state: SupervisorState, configurable: Configuration, error: Exception
) -> Command[Literal["__end__"]]:
    """End the loop after a supervisor model failure (REQ-003, ADR-001 §3.4 step 5, POL-011)."""
    results = list(state.get("task_results", []) or [])
    cap_reached = (
        state.get("research_iterations", 0) > configurable.max_researcher_iterations
    )
    reason, stalled_turns = select_exit(
        results,
        results,
        stalled_turns=state.get("stalled_turns", 0) or 0,
        turn_is_eligible=False,
        cap_reached=cap_reached,
        supervisor_error=True,
        threshold=configurable.coverage_threshold,
    )
    if reason == "failed":
        detail = f"the supervisor model failed: {error}"
    else:
        detail = _exit_detail(reason, results, configurable)
        if reason != "covered":
            detail += f"; then the supervisor model failed: {error}"
    return Command(
        goto=END, update=_loop_exit_update(results, reason, detail, stalled_turns)
    )


async def _task_contract_turn(
    state: SupervisorState, config: RunnableConfig, configurable: Configuration
) -> Command[Literal["supervisor", "__end__"]]:
    """Handle one supervisor turn with the task contract on (REQ-001 to REQ-003, ADR-001 §3.4).

    Steps 1-7 of ADR-001 §3.4: reflections as in the baseline; delegations
    become task specifications, and invalid ones are rejected; at the iteration
    cap the accepted specs end ``not_run``, otherwise ``run_delegations`` runs
    them (ADR-002); every delegation gets one ``ToolMessage``; ``select_exit``
    alone decides whether the loop ends.
    """
    supervisor_messages = state.get("supervisor_messages", [])
    tool_calls = list(supervisor_messages[-1].tool_calls or [])
    before = list(state.get("task_results", []) or [])
    tool_messages = []

    # Step 1: reflections, and the delegations as task specifications
    for tool_call in tool_calls:
        if tool_call["name"] == THINK_TOOL_NAME:
            tool_messages.append(ToolMessage(
                content=f"Reflection recorded: {tool_call['args']['reflection']}",
                name=THINK_TOOL_NAME,
                tool_call_id=tool_call["id"]
            ))
    delegations = [call for call in tool_calls if call["name"] == DELEGATION_TOOL_NAME]
    specs, rejections = build_task_specs(
        tool_calls, _next_task_number(before), configurable
    )
    rejected = {message.tool_call_id: message for message in rejections}
    accepted = [
        spec for call, spec in zip(delegations, specs) if call["id"] not in rejected
    ]

    # Step 2: at the cap nothing runs; otherwise every accepted spec runs and joins
    cap_reached = (
        state.get("research_iterations", 0) > configurable.max_researcher_iterations
    )
    raw_notes: list[str] = []
    if cap_reached:
        ran = [TaskResult.failed(spec, "not_run", NOT_RUN_REASON) for spec in accepted]
    else:
        async def run_one(spec: TaskSpec):
            # The researcher runs with the run's configuration, as in the baseline.
            return await researcher_subgraph.ainvoke({
                "researcher_messages": [HumanMessage(content=render_task_brief(spec))],
                "research_topic": spec.research_topic,
                "task_spec": spec,
            }, config)

        ran, raw_notes = await run_delegations(
            accepted,
            run_one,
            max_concurrent=configurable.max_concurrent_research_units,
            research_model=configurable.research_model,
        )
    ran_by_task = {result.task_id: result for result in ran}

    # Step 3: exactly one result and one ToolMessage per delegation, in call order
    step_results = []
    for call, spec in zip(delegations, specs):
        if call["id"] in rejected:
            error = rejected[call["id"]]
            step_results.append(
                TaskResult.failed(spec, "invalid_result", _message_text(error))
            )
            tool_messages.append(error)
            continue
        result = ran_by_task[spec.task_id]
        step_results.append(result)
        tool_messages.append(ToolMessage(
            content=render_result_message(result),
            name=DELEGATION_TOOL_NAME,
            tool_call_id=call["id"]
        ))

    # Step 4: one exit decision; only a turn with nothing but think_tool calls
    # leaves the stall counter as it is
    after = before + step_results
    turn_is_eligible = not tool_calls or any(
        call["name"] != THINK_TOOL_NAME for call in tool_calls
    )
    reason, stalled_turns = select_exit(
        before,
        after,
        stalled_turns=state.get("stalled_turns", 0) or 0,
        turn_is_eligible=turn_is_eligible,
        cap_reached=cap_reached,
        supervisor_error=False,
        threshold=configurable.coverage_threshold,
    )
    # The turn's results are appended to the run's list by ``override_reducer``.
    update = {"task_results": step_results, "stalled_turns": stalled_turns}
    if raw_notes:
        update["raw_notes"] = ["\n".join(raw_notes)]
    if reason is not None:
        update["supervisor_messages"] = tool_messages
        update.update(_loop_exit_update(
            after, reason, _exit_detail(reason, after, configurable), stalled_turns
        ))
        return Command(goto=END, update=update)

    # Step 6: a completion request, or a turn without tool calls, below the
    # threshold is refused and the supervisor is told what is still missing
    missing = unanswered_questions(after)
    refusal = (
        "The research is not complete yet. Unanswered required questions: "
        + "; ".join(missing)
        if missing
        else "The research is not complete yet: no required question has been "
        "delegated. Delegate research tasks with must_answer questions first."
    )
    for call in tool_calls:
        if call["name"] == COMPLETE_TOOL_NAME:
            tool_messages.append(ToolMessage(
                content=refusal, name=COMPLETE_TOOL_NAME, tool_call_id=call["id"]
            ))
    if not tool_calls:
        tool_messages.append(HumanMessage(content=refusal))
    update["supervisor_messages"] = tool_messages
    return Command(goto="supervisor", update=update)


async def supervisor_tools(state: SupervisorState, config: RunnableConfig) -> Command[Literal["supervisor", "__end__"]]:
    """Execute tools called by the supervisor, including research delegation and strategic thinking.
    
    This function handles three types of supervisor tool calls:
    1. think_tool - Strategic reflection that continues the conversation
    2. ConductResearch - Delegates research tasks to sub-researchers
    3. ResearchComplete - Signals completion of research phase
    
    Args:
        state: Current supervisor state with messages and iteration count
        config: Runtime configuration with research limits and model settings
        
    Returns:
        Command to either continue supervision loop or end research phase
    """
    # Step 1: Extract current state and check exit conditions
    configurable = Configuration.from_runnable_config(config)
    if configurable.task_contract_enabled:
        # REQ-001 to REQ-003, ADR-001 §3.4: a typed task turn; only select_exit
        # ends the loop.
        return await _task_contract_turn(state, config, configurable)
    supervisor_messages = state.get("supervisor_messages", [])
    research_iterations = state.get("research_iterations", 0)
    most_recent_message = supervisor_messages[-1]
    
    # Define exit criteria for research phase
    exceeded_allowed_iterations = research_iterations > configurable.max_researcher_iterations
    no_tool_calls = not most_recent_message.tool_calls
    research_complete_tool_call = any(
        tool_call["name"] == "ResearchComplete" 
        for tool_call in most_recent_message.tool_calls
    )
    
    # Exit if any termination condition is met
    if exceeded_allowed_iterations or no_tool_calls or research_complete_tool_call:
        return Command(
            goto=END,
            update={
                "notes": get_notes_from_tool_calls(supervisor_messages),
                "research_brief": state.get("research_brief", "")
            }
        )
    
    # Step 2: Process all tool calls together (both think_tool and ConductResearch)
    all_tool_messages = []
    update_payload = {"supervisor_messages": []}
    
    # Handle think_tool calls (strategic reflection)
    think_tool_calls = [
        tool_call for tool_call in most_recent_message.tool_calls 
        if tool_call["name"] == "think_tool"
    ]
    
    for tool_call in think_tool_calls:
        reflection_content = tool_call["args"]["reflection"]
        all_tool_messages.append(ToolMessage(
            content=f"Reflection recorded: {reflection_content}",
            name="think_tool",
            tool_call_id=tool_call["id"]
        ))
    
    # Handle ConductResearch calls (research delegation)
    conduct_research_calls = [
        tool_call for tool_call in most_recent_message.tool_calls 
        if tool_call["name"] == "ConductResearch"
    ]
    
    if conduct_research_calls:
        try:
            # Limit concurrent research units to prevent resource exhaustion
            allowed_conduct_research_calls = conduct_research_calls[:configurable.max_concurrent_research_units]
            overflow_conduct_research_calls = conduct_research_calls[configurable.max_concurrent_research_units:]
            
            # Execute research tasks in parallel
            research_tasks = [
                researcher_subgraph.ainvoke({
                    "researcher_messages": [
                        HumanMessage(content=tool_call["args"]["research_topic"])
                    ],
                    "research_topic": tool_call["args"]["research_topic"]
                }, config) 
                for tool_call in allowed_conduct_research_calls
            ]
            
            tool_results = await asyncio.gather(*research_tasks)
            
            # Create tool messages with research results
            for observation, tool_call in zip(tool_results, allowed_conduct_research_calls):
                all_tool_messages.append(ToolMessage(
                    content=observation.get("compressed_research", "Error synthesizing research report: Maximum retries exceeded"),
                    name=tool_call["name"],
                    tool_call_id=tool_call["id"]
                ))
            
            # Handle overflow research calls with error messages
            for overflow_call in overflow_conduct_research_calls:
                all_tool_messages.append(ToolMessage(
                    content=f"Error: Did not run this research as you have already exceeded the maximum number of concurrent research units. Please try again with {configurable.max_concurrent_research_units} or fewer research units.",
                    name="ConductResearch",
                    tool_call_id=overflow_call["id"]
                ))
            
            # Aggregate raw notes from all research results
            raw_notes_concat = "\n".join([
                "\n".join(observation.get("raw_notes", [])) 
                for observation in tool_results
            ])
            
            if raw_notes_concat:
                update_payload["raw_notes"] = [raw_notes_concat]
                
        except Exception as e:
            # Handle research execution errors
            if is_token_limit_exceeded(e, configurable.research_model) or True:
                # Token limit exceeded or other error - end research phase
                return Command(
                    goto=END,
                    update={
                        "notes": get_notes_from_tool_calls(supervisor_messages),
                        "research_brief": state.get("research_brief", "")
                    }
                )
    
    # Step 3: Return command with all tool results
    update_payload["supervisor_messages"] = all_tool_messages
    return Command(
        goto="supervisor",
        update=update_payload
    ) 

# Supervisor Subgraph Construction
# Creates the supervisor workflow that manages research delegation and coordination
supervisor_builder = StateGraph(SupervisorState, config_schema=Configuration)

# Add supervisor nodes for research management
supervisor_builder.add_node("supervisor", supervisor)           # Main supervisor logic
supervisor_builder.add_node("supervisor_tools", supervisor_tools)  # Tool execution handler

# Define supervisor workflow edges
supervisor_builder.add_edge(START, "supervisor")  # Entry point to supervisor

# Compile supervisor subgraph for use in main workflow
supervisor_subgraph = supervisor_builder.compile()

async def researcher(state: ResearcherState, config: RunnableConfig) -> Command[Literal["researcher_tools"]]:
    """Individual researcher that conducts focused research on specific topics.
    
    This researcher is given a specific research topic by the supervisor and uses
    available tools (search, think_tool, MCP tools) to gather comprehensive information.
    It can use think_tool for strategic planning between searches.
    
    Args:
        state: Current researcher state with messages and topic context
        config: Runtime configuration with model settings and tool availability
        
    Returns:
        Command to proceed to researcher_tools for tool execution
    """
    # Step 1: Load configuration and validate tool availability (REQ-007,
    # ADR-006 §3.4, INV-005): an invalid search configuration, or tools without
    # any search tool, stop the researcher before its model call.
    configurable = load_search_config(config)
    researcher_messages = state.get("researcher_messages", [])
    
    # Get all available research tools (search, MCP, think_tool)
    tools = await get_all_tools(config)
    require_search_tools(tools, configurable.search_api)
    
    # Step 2: Configure the researcher model with tools
    research_model_config = {
        "model": configurable.research_model,
        "max_tokens": configurable.research_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.research_model, config),
        "tags": ["langsmith:nostream"]
    }
    
    # Prepare system prompt with MCP context if available
    researcher_prompt = research_system_prompt.format(
        mcp_prompt=configurable.mcp_prompt or "", 
        date=get_today_str()
    )
    
    # Configure model with tools, retry logic, and settings
    research_model = (
        configurable_model
        .bind_tools(tools)
        .with_retry(stop_after_attempt=configurable.max_structured_output_retries)
        .with_config(research_model_config)
    )
    
    # Step 3: Generate researcher response with system context
    messages = [SystemMessage(content=researcher_prompt)] + researcher_messages
    response = await research_model.ainvoke(messages)
    
    # Step 4: Update state and proceed to tool execution
    return Command(
        goto="researcher_tools",
        update={
            "researcher_messages": [response],
            "tool_call_iterations": state.get("tool_call_iterations", 0) + 1
        }
    )

# Tool Execution Helper Function
async def execute_tool_safely(tool, args, config):
    """Safely execute a tool with error handling."""
    try:
        return await tool.ainvoke(args, config)
    except Exception as e:
        return f"Error executing tool: {str(e)}"


async def researcher_tools(state: ResearcherState, config: RunnableConfig) -> Command[Literal["researcher", "compress_research"]]:
    """Execute tools called by the researcher, including search tools and strategic thinking.
    
    This function handles various types of researcher tool calls:
    1. think_tool - Strategic reflection that continues the research conversation
    2. Search tools (tavily_search, web_search) - Information gathering
    3. MCP tools - External tool integrations
    4. ResearchComplete - Signals completion of individual research task
    
    Args:
        state: Current researcher state with messages and iteration count
        config: Runtime configuration with research limits and tool settings
        
    Returns:
        Command to either continue research loop or proceed to compression
    """
    # Step 1: Extract current state and check early exit conditions
    configurable = Configuration.from_runnable_config(config)
    researcher_messages = state.get("researcher_messages", [])
    most_recent_message = researcher_messages[-1]
    
    # Early exit if no tool calls were made (including native web search)
    has_tool_calls = bool(most_recent_message.tool_calls)
    has_native_search = (
        openai_websearch_called(most_recent_message) or 
        anthropic_websearch_called(most_recent_message)
    )
    
    if not has_tool_calls and not has_native_search:
        return Command(goto="compress_research")
    
    # Step 2: Handle other tool calls (search, MCP tools, etc.)
    tools = await get_all_tools(config)
    # REQ-008, ADR-008 §3.2: the configured search tools fall back to the next
    # source; with an empty search_fallback the tools are returned unchanged.
    tools = apply_search_fallback(tools, configurable)
    tools_by_name = {
        tool.name if hasattr(tool, "name") else tool.get("name", "web_search"): tool 
        for tool in tools
    }
    
    # Execute all tool calls in parallel
    tool_calls = most_recent_message.tool_calls
    # REQ-001, ADR-001 §3.2, POL-009: with the task contract a task runs at most
    # its tool-call budget; the calls beyond it, in the model's order, are not run.
    task_spec = state.get("task_spec") if configurable.task_contract_enabled else None
    tool_calls_spent = state.get("tool_calls_spent", 0) or 0
    calls_to_run = tool_calls
    if task_spec is not None:
        calls_to_run = tool_calls[:max(0, task_spec.max_tool_calls - tool_calls_spent)]
    tool_execution_tasks = [
        execute_tool_safely(tools_by_name[tool_call["name"]], tool_call["args"], config) 
        for tool_call in calls_to_run
    ]
    observations = await asyncio.gather(*tool_execution_tasks)
    
    # Create tool messages from execution results
    tool_outputs = [
        ToolMessage(
            content=observation,
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        ) 
        for observation, tool_call in zip(observations, calls_to_run)
    ]
    tool_outputs.extend(
        ToolMessage(
            content=BUDGET_TOOL_MESSAGE,
            name=tool_call["name"],
            tool_call_id=tool_call["id"]
        )
        for tool_call in tool_calls[len(calls_to_run):]
    )
    update = {"researcher_messages": tool_outputs}
    budget_used_up = False
    if task_spec is not None:
        # Every executed call counts, a failed one too; the URLs of successful
        # tool results are what a finding may cite (ADR-001 §3.2).
        tool_calls_spent += len(calls_to_run)
        update["tool_calls_spent"] = tool_calls_spent
        update["retrieved_urls"] = extract_urls(tool_outputs)
        budget_used_up = tool_calls_spent >= task_spec.max_tool_calls
    
    # Step 3: Check late exit conditions (after processing tools)
    exceeded_iterations = state.get("tool_call_iterations", 0) >= configurable.max_react_tool_calls
    research_complete_called = any(
        tool_call["name"] == "ResearchComplete" 
        for tool_call in most_recent_message.tool_calls
    )
    
    if exceeded_iterations or research_complete_called or budget_used_up:
        # End research and proceed to compression
        return Command(
            goto="compress_research",
            update=update
        )
    
    # Continue research loop with tool results
    return Command(
        goto="researcher",
        update=update
    )

async def compress_research(state: ResearcherState, config: RunnableConfig):
    """Compress and synthesize research findings into a concise, structured summary.
    
    This function takes all the research findings, tool outputs, and AI messages from
    a researcher's work and distills them into a clean, comprehensive summary while
    preserving all important information and findings.
    
    Args:
        state: Current researcher state with accumulated research messages
        config: Runtime configuration with compression model settings
        
    Returns:
        Dictionary containing compressed research summary and raw notes
    """
    # Step 1: Configure the compression model
    configurable = Configuration.from_runnable_config(config)
    synthesizer_model = configurable_model.with_config({
        "model": configurable.compression_model,
        "max_tokens": configurable.compression_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.compression_model, config),
        "tags": ["langsmith:nostream"]
    })
    
    # Step 2: Prepare messages for compression
    researcher_messages = state.get("researcher_messages", [])
    task_spec = state.get("task_spec") if configurable.task_contract_enabled else None
    
    # Add instruction to switch from research mode to compression mode
    compression_instruction = compress_research_simple_human_message
    if task_spec is not None:
        # REQ-001, ADR-001 §3.3: the final instruction asks for one findings block.
        compression_instruction += "\n\n" + task_findings_instruction.format(
            must_answer="\n".join(f"- {question}" for question in task_spec.must_answer)
        )
    researcher_messages.append(HumanMessage(content=compression_instruction))
    
    if configurable.context_trimming:
        # REQ-005, ADR-004 §3: on a token-limit error the oldest whole turns are
        # removed; a history that cannot be reduced is an explicit failure.
        try:
            summary = await compress_with_recovery(
                synthesizer_model,
                compress_research_system_prompt.format(date=get_today_str()),
                researcher_messages,
                configurable.compression_model,
            )
        except CompressionFailed as failure:
            return _compression_failed(state, task_spec, failure, researcher_messages)
        return _compression_output(state, task_spec, summary, researcher_messages)
    
    # Step 3: Attempt compression with retry logic for token limit issues
    synthesis_attempts = 0
    max_attempts = 3
    
    while synthesis_attempts < max_attempts:
        try:
            # Create system prompt focused on compression task
            compression_prompt = compress_research_system_prompt.format(date=get_today_str())
            messages = [SystemMessage(content=compression_prompt)] + researcher_messages
            
            # Execute compression
            response = await synthesizer_model.ainvoke(messages)
            
            # Extract raw notes from all tool and AI messages
            raw_notes_content = "\n".join([
                str(message.content) 
                for message in filter_messages(researcher_messages, include_types=["tool", "ai"])
            ])
            
            if task_spec is not None:
                return _compression_output(
                    state, task_spec, _message_text(response), researcher_messages
                )
            
            # Return successful compression result
            return {
                "compressed_research": str(response.content),
                "raw_notes": [raw_notes_content]
            }
            
        except Exception as e:
            synthesis_attempts += 1
            
            # Handle token limit exceeded by removing older messages
            if is_token_limit_exceeded(e, configurable.research_model):
                researcher_messages = remove_up_to_last_ai_message(researcher_messages)
                continue
            
            # For other errors, continue retrying
            continue
    
    # Step 4: Return error result if all attempts failed
    if task_spec is not None:
        # ADR-001 §3.3: the placeholder has no findings block, so the task
        # becomes failed/invalid_result instead of passing placeholder text on.
        return _compression_output(
            state, task_spec, COMPRESSION_PLACEHOLDER, researcher_messages
        )
    raw_notes_content = "\n".join([
        str(message.content) 
        for message in filter_messages(researcher_messages, include_types=["tool", "ai"])
    ])
    
    return {
        "compressed_research": "Error synthesizing research report: Maximum retries exceeded",
        "raw_notes": [raw_notes_content]
    }

def _raw_notes(messages) -> str:
    """Return the tool and AI text of a research history, as the baseline raw notes."""
    return "\n".join([
        str(message.content)
        for message in filter_messages(messages, include_types=["tool", "ai"])
    ])


def _compression_output(state: ResearcherState, task_spec, summary: str, messages) -> dict:
    """Return the researcher output for a compression text (REQ-001, ADR-001 §3.3).

    With the task contract the status is decided by ``build_task_result`` from
    the findings block and the URLs this task's tools returned, and the output
    summary is the text without the findings block.
    """
    if task_spec is None:
        return {"compressed_research": summary, "raw_notes": [_raw_notes(messages)]}
    task_result = build_task_result(
        task_spec,
        summary,
        state.get("retrieved_urls", []) or [],
        state.get("tool_calls_spent", 0) or 0,
    )
    return {
        "compressed_research": task_result.summary,
        "raw_notes": [_raw_notes(messages)],
        "task_result": task_result,
    }


def _compression_failed(
    state: ResearcherState, task_spec, failure: CompressionFailed, messages
) -> dict:
    """Map a compression that could not finish (REQ-005 C-004, ADR-004 §3).

    With the task contract the task ends ``failed`` with the failure's category
    and no summary; without it there is no task result, so the baseline
    placeholder is returned.
    """
    if task_spec is None:
        return {
            "compressed_research": COMPRESSION_PLACEHOLDER,
            "raw_notes": [_raw_notes(messages)],
        }
    return {
        "compressed_research": "",
        "raw_notes": [_raw_notes(messages)],
        "task_result": TaskResult.failed(
            task_spec,
            failure.category,
            failure.reason,
            tool_calls=state.get("tool_calls_spent", 0) or 0,
        ),
    }

# Researcher Subgraph Construction
# Creates individual researcher workflow for conducting focused research on specific topics
researcher_builder = StateGraph(
    ResearcherState, 
    output=ResearcherOutputState, 
    config_schema=Configuration
)

# Add researcher nodes for research execution and compression
researcher_builder.add_node("researcher", researcher)                 # Main researcher logic
researcher_builder.add_node("researcher_tools", researcher_tools)     # Tool execution handler
researcher_builder.add_node("compress_research", compress_research)   # Research compression

# Define researcher workflow edges
researcher_builder.add_edge(START, "researcher")           # Entry point to researcher
researcher_builder.add_edge("compress_research", END)      # Exit point after compression

# Compile researcher subgraph for parallel execution by supervisor
researcher_subgraph = researcher_builder.compile()

async def check_research_outcome(
    state: AgentState, config: RunnableConfig
) -> Command[Literal["final_report_generation", "__end__"]]:
    """Decide before the report whether the report model may run (REQ-004, ADR-003 §3.1, §3.2).

    A run without any validated finding, or whose research loop exited
    ``failed``, ends here with outcome ``failed`` and an empty report, so the
    report model is never called (POL-015). Any other run goes on to
    ``final_report_generation`` with ``failed_tasks`` written; the provisional
    outcome is not stored. With ``task_contract_enabled`` off the node only
    forwards.
    """
    configurable = Configuration.from_runnable_config(config)
    if not configurable.task_contract_enabled:
        return Command(goto="final_report_generation")

    decision = assess_research(
        list(state.get("task_results", []) or []),
        state.get("exit_reason"),
        state.get("exit_detail", "") or "",
    )
    failed_tasks = _override(decision.failed_tasks)
    if decision.report_allowed:
        return Command(
            goto="final_report_generation", update={"failed_tasks": failed_tasks}
        )
    return Command(
        goto=END,
        update={
            "research_outcome": decision.outcome,
            "outcome_detail": decision.detail,
            "failed_tasks": failed_tasks,
            "final_report": "",
            "notes": _override([]),
        },
    )


async def _flag_on_report(
    state: AgentState, config: RunnableConfig, configurable: Configuration
) -> dict:
    """Write the report and decide the final outcome (REQ-004, ADR-003 §3.3, POL-016, POL-017).

    The baseline retry loop stays, but an error never becomes report text: it
    goes to ``outcome_detail`` and the report is empty. Findings cut to fit the
    model make the run ``partial``, and a ``partial`` report gets the
    limitations section written by code.
    """
    results = list(state.get("task_results", []) or [])
    decision = assess_research(
        results, state.get("exit_reason"), state.get("exit_detail", "") or ""
    )
    cleared_state = {"notes": _override([])}
    if not decision.report_allowed:
        return {
            "final_report": "",
            "research_outcome": decision.outcome,
            "outcome_detail": decision.detail,
            **cleared_state,
        }

    findings = "\n".join(state.get("notes", []) or [])
    writer_model_config = {
        "model": configurable.final_report_model,
        "max_tokens": configurable.final_report_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.final_report_model, config),
        "tags": ["langsmith:nostream"]
    }
    max_retries = 3
    current_retry = 0
    findings_token_limit = None
    findings_truncated = False
    report = None
    report_error = None
    while current_retry <= max_retries:
        try:
            final_report_prompt = final_report_generation_prompt.format(
                research_brief=state.get("research_brief", ""),
                messages=get_buffer_string(state.get("messages", [])),
                findings=findings,
                date=get_today_str()
            )
            response = await configurable_model.with_config(writer_model_config).ainvoke([
                HumanMessage(content=final_report_prompt)
            ])
            report = _message_text(response)
            break
        except Exception as e:
            if not is_token_limit_exceeded(e, configurable.final_report_model):
                report_error = f"Error generating final report: {e}"
                break
            current_retry += 1
            if current_retry == 1:
                model_token_limit = get_model_token_limit(configurable.final_report_model)
                if not model_token_limit:
                    report_error = (
                        "Error generating final report: Token limit exceeded, however, "
                        "we could not determine the model's maximum context length. "
                        f"{e}"
                    )
                    break
                findings_token_limit = model_token_limit * 4
            else:
                findings_token_limit = int(findings_token_limit * 0.9)
            findings = findings[:findings_token_limit]
            findings_truncated = True
    if report is None and report_error is None:
        report_error = "Error generating final report: Maximum retries exceeded"

    outcome, detail = finish_outcome(
        decision, report_error=report_error, findings_truncated=findings_truncated
    )
    if report_error is not None:
        # No message is added: the error text appears only in outcome_detail.
        return {
            "final_report": "",
            "research_outcome": outcome,
            "outcome_detail": detail,
            **cleared_state,
        }
    if outcome == "partial":
        limitations = render_limitations(results, findings_truncated)
        if limitations:
            report = f"{report}\n\n{limitations}"
    return {
        "final_report": report,
        "messages": [AIMessage(content=report)],
        "research_outcome": outcome,
        "outcome_detail": detail,
        **cleared_state,
    }


async def final_report_generation(state: AgentState, config: RunnableConfig):
    """Generate the final comprehensive research report with retry logic for token limits.
    
    This function takes all collected research findings and synthesizes them into a 
    well-structured, comprehensive final report using the configured report generation model.
    
    Args:
        state: Agent state containing research findings and context
        config: Runtime configuration with model settings and API keys
        
    Returns:
        Dictionary containing the final report and cleared state
    """
    configurable = Configuration.from_runnable_config(config)
    if configurable.task_contract_enabled:
        # REQ-004, ADR-003 §3.3: the report also decides the run outcome.
        return await _flag_on_report(state, config, configurable)
    
    # Step 1: Extract research findings and prepare state cleanup
    notes = state.get("notes", [])
    cleared_state = {"notes": {"type": "override", "value": []}}
    findings = "\n".join(notes)
    
    # Step 2: Configure the final report generation model
    configurable = Configuration.from_runnable_config(config)
    writer_model_config = {
        "model": configurable.final_report_model,
        "max_tokens": configurable.final_report_model_max_tokens,
        "api_key": get_api_key_for_model(configurable.final_report_model, config),
        "tags": ["langsmith:nostream"]
    }
    
    # Step 3: Attempt report generation with token limit retry logic
    max_retries = 3
    current_retry = 0
    findings_token_limit = None
    
    while current_retry <= max_retries:
        try:
            # Create comprehensive prompt with all research context
            final_report_prompt = final_report_generation_prompt.format(
                research_brief=state.get("research_brief", ""),
                messages=get_buffer_string(state.get("messages", [])),
                findings=findings,
                date=get_today_str()
            )
            
            # Generate the final report
            final_report = await configurable_model.with_config(writer_model_config).ainvoke([
                HumanMessage(content=final_report_prompt)
            ])
            
            # Return successful report generation
            return {
                "final_report": final_report.content, 
                "messages": [final_report],
                **cleared_state
            }
            
        except Exception as e:
            # Handle token limit exceeded errors with progressive truncation
            if is_token_limit_exceeded(e, configurable.final_report_model):
                current_retry += 1
                
                if current_retry == 1:
                    # First retry: determine initial truncation limit
                    model_token_limit = get_model_token_limit(configurable.final_report_model)
                    if not model_token_limit:
                        return {
                            "final_report": f"Error generating final report: Token limit exceeded, however, we could not determine the model's maximum context length. Please update the model map in deep_researcher/utils.py with this information. {e}",
                            "messages": [AIMessage(content="Report generation failed due to token limits")],
                            **cleared_state
                        }
                    # Use 4x token limit as character approximation for truncation
                    findings_token_limit = model_token_limit * 4
                else:
                    # Subsequent retries: reduce by 10% each time
                    findings_token_limit = int(findings_token_limit * 0.9)
                
                # Truncate findings and retry
                findings = findings[:findings_token_limit]
                continue
            else:
                # Non-token-limit error: return error immediately
                return {
                    "final_report": f"Error generating final report: {e}",
                    "messages": [AIMessage(content="Report generation failed due to an error")],
                    **cleared_state
                }
    
    # Step 4: Return failure result if all retries exhausted
    return {
        "final_report": "Error generating final report: Maximum retries exceeded",
        "messages": [AIMessage(content="Report generation failed after maximum retries")],
        **cleared_state
    }

# Main Deep Researcher Graph Construction
# Creates the complete deep research workflow from user input to final report
deep_researcher_builder = StateGraph(
    AgentState, 
    input=AgentInputState, 
    config_schema=Configuration
)

# Add main workflow nodes for the complete research process
deep_researcher_builder.add_node("clarify_with_user", clarify_with_user)           # User clarification phase
deep_researcher_builder.add_node("write_research_brief", write_research_brief)     # Research planning phase
deep_researcher_builder.add_node("research_supervisor", supervisor_subgraph)       # Research execution phase
deep_researcher_builder.add_node("check_research_outcome", check_research_outcome) # Outcome before the report
deep_researcher_builder.add_node("final_report_generation", final_report_generation)  # Report generation phase

# Define main workflow edges for sequential execution
deep_researcher_builder.add_edge(START, "clarify_with_user")                       # Entry point
deep_researcher_builder.add_edge("research_supervisor", "check_research_outcome")  # Research to outcome check
# check_research_outcome routes to final_report_generation or END with Command.
deep_researcher_builder.add_edge("final_report_generation", END)                   # Final exit point

# Compile the complete deep researcher workflow
deep_researcher = deep_researcher_builder.compile()