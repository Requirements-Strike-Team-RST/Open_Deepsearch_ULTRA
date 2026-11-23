"""Expose the shared citation rules for the research prompts (REQ-006, INV-008)."""

from open_deep_research._prompt_loader import get_template

CITATION_RULES_BLOCK = get_template("citation_rules_block")
SOURCES_SECTION_POINTER = get_template("sources_section_pointer")
RENUMBER_ACROSS_FINDINGS_INSTRUCTION = get_template(
    "renumber_across_findings_instruction"
)
