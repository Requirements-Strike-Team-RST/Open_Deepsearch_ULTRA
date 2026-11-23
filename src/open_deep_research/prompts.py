"""Expose the Deep Research prompt templates loaded from the versioned YAML catalog."""

from open_deep_research._prompt_loader import get_template
from open_deep_research.citations.contract import (
    CITATION_RULES_BLOCK,
    RENUMBER_ACROSS_FINDINGS_INSTRUCTION,
    SOURCES_SECTION_POINTER,
)

clarify_with_user_instructions = get_template("clarify_with_user_instructions")
transform_messages_into_research_topic_prompt = get_template(
    "transform_messages_into_research_topic_prompt"
)
lead_researcher_prompt = get_template("lead_researcher_prompt")
research_system_prompt = get_template("research_system_prompt")
compress_research_simple_human_message = get_template(
    "compress_research_simple_human_message"
)
task_findings_instruction = get_template("task_findings_instruction")
task_contract_delegation_note = get_template("task_contract_delegation_note")
summarize_webpage_prompt = get_template("summarize_webpage_prompt")
task_brief = get_template("task_brief")
task_brief_unspecified_scope = get_template("task_brief_unspecified_scope")
completion_refusal_with_missing_questions = get_template(
    "completion_refusal_with_missing_questions"
)
completion_refusal_without_questions = get_template(
    "completion_refusal_without_questions"
)

compress_research_system_prompt = (
    get_template("compress_research_system_prompt")
    .replace("{citation_rules}", CITATION_RULES_BLOCK)
    .replace("{sources_section_pointer}", SOURCES_SECTION_POINTER)
)
final_report_generation_prompt = (
    get_template("final_report_generation_prompt")
    .replace("{citation_rules}", CITATION_RULES_BLOCK)
    .replace(
        "{renumber_across_findings_instruction}", RENUMBER_ACROSS_FINDINGS_INSTRUCTION
    )
)
lead_researcher_task_contract_prompt = lead_researcher_prompt.replace(
    "</Hard Limits>", task_contract_delegation_note + "\n</Hard Limits>", 1
)
