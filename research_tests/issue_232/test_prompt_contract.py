from open_deep_research.prompts import compress_research_system_prompt


FORMAT_A = "**List of All Relevant Sources"
FORMAT_B = "### Sources"


def test_compression_prompt_can_be_loaded():
    assert isinstance(compress_research_system_prompt, str)
    assert len(compress_research_system_prompt) > 0


def test_compression_prompt_has_single_sources_contract():
    prompt = compress_research_system_prompt

    has_format_a = FORMAT_A in prompt
    has_format_b = FORMAT_B in prompt

    assert not (
        has_format_a and has_format_b
    ), (
        "Issue #232 reproduced: "
        "compress_research_system_prompt contains competing "
        "Sources-section format instructions.\n"
        f"Format A present: {has_format_a}\n"
        f"Format B present: {has_format_b}"
    )


