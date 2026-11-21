"""REQ-006: the research prompts state one consistent citation format.

Covers TC-CIT-01 to TC-CIT-04 (``verification-constraints.md`` §7, citations) and
INV-008, each case once as its table row defines it. The interface is
``citations/contract.py`` and the assembled prompt strings of ``prompts.py``
(ADR-005 §3, §5). No model is called and no network is used.
"""

import re
import string

BASELINE_REPORT_PLACEHOLDERS = {"research_brief", "messages", "findings", "date"}


def citation_block(prompt: str) -> str:
    """Return the text between the `<Citation Rules>` tags."""
    match = re.search(r"<Citation Rules>(.*?)</Citation Rules>", prompt, re.DOTALL)
    assert match, "the prompt carries one <Citation Rules> block"
    return match.group(1)


def placeholders(template: str) -> set[str]:
    """Return the named format fields of a template."""
    return {name for _, name, _, _ in string.Formatter().parse(template) if name}


###################
# The compression prompt (TC-CIT-01)
###################
def test_compression_prompt_has_single_sources_format():
    """TC-CIT-01 / C-001; INV-008: one rules block with `### Sources`, no competing label or link format."""
    from open_deep_research.prompts import compress_research_system_prompt

    prompt = compress_research_system_prompt

    assert prompt.count("<Citation Rules>") == 1
    block = citation_block(prompt)
    assert "### Sources" in block
    assert "[n] Title: URL" in block
    assert "List of All Relevant Sources" not in prompt
    assert "[Title](URL)" not in prompt
    assert "**List of Queries and Tool Calls Made**" in prompt, (
        "the rest of the output format stays"
    )
    assert "Sources section" in prompt, (
        "the rules block points at the mandatory Sources section"
    )


###################
# The report prompt (TC-CIT-02)
###################
def test_report_prompt_has_single_citation_format():
    """TC-CIT-02 / C-002; INV-008: numbered citations, no `[Title](URL)` and one renumbering instruction."""
    from open_deep_research.prompts import final_report_generation_prompt

    prompt = final_report_generation_prompt

    assert prompt.count("<Citation Rules>") == 1
    assert "### Sources" in citation_block(prompt)
    assert "[Title](URL)" not in prompt
    assert "numbered" in prompt.lower() or "[n]" in prompt
    renumbering = re.findall(r"renumber", prompt, re.IGNORECASE)
    assert len(renumbering) == 1, (
        "the instruction to renumber across findings appears once"
    )


###################
# One format for both prompts (TC-CIT-03)
###################
def test_prompts_share_citation_format():
    """TC-CIT-03 / C-003; INV-008: the text between the `<Citation Rules>` tags is identical."""
    from open_deep_research.prompts import (
        compress_research_system_prompt,
        final_report_generation_prompt,
    )

    assert citation_block(compress_research_system_prompt) == citation_block(
        final_report_generation_prompt
    )


###################
# Assembling the prompts (TC-CIT-04)
###################
def test_assembled_prompts_format_without_leftover_placeholders():
    """TC-CIT-04 / ADR-005 §3: both prompts format with their runtime placeholders and leave none behind."""
    from open_deep_research.prompts import (
        compress_research_system_prompt,
        final_report_generation_prompt,
    )

    assert placeholders(compress_research_system_prompt) == {"date"}
    assert placeholders(final_report_generation_prompt) == BASELINE_REPORT_PLACEHOLDERS

    for prompt, values in (
        (compress_research_system_prompt, {"date": "Fri Nov 20, 2026"}),
        (
            final_report_generation_prompt,
            {
                "research_brief": "battery recycling",
                "messages": "user: battery recycling",
                "findings": "Task T1: topic",
                "date": "Fri Nov 20, 2026",
            },
        ),
    ):
        text = prompt.format(**values)
        assert not re.search(r"\{[a-z_]+\}", text), "no `{name}` placeholder is left"
        assert "<Citation Rules>" in text and "### Sources" in text


###################
# The shared constants (ADR-005 §5)
###################
def test_citation_constants_hold_no_braces():
    """ADR-005 §3: the constants contain no `{` or `}`, so `.format()` cannot break them."""
    from open_deep_research.citations import contract

    for constant in (contract.CITATION_RULES_BLOCK, contract.SOURCES_SECTION_POINTER):
        assert "{" not in constant and "}" not in constant
    if hasattr(contract, "RENUMBER_ACROSS_FINDINGS_INSTRUCTION"):
        instruction = contract.RENUMBER_ACROSS_FINDINGS_INSTRUCTION
        assert "{" not in instruction and "}" not in instruction
