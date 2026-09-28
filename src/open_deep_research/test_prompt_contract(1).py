from open_deep_research.prompts import (
    compress_research_system_prompt,
    final_report_generation_prompt,
)

FORMAT_A = "**List of All Relevant Sources"
FORMAT_B = "### Sources"


def test_compression_prompt_can_be_loaded():
    assert isinstance(compress_research_system_prompt, str)
    assert len(compress_research_system_prompt) > 0

def test_compression_prompt_has_consistent_sources_contract():
    prompt = compress_research_system_prompt

    has_format_a = FORMAT_A in prompt
    has_format_b = FORMAT_B in prompt

    # Issue #232: the original bug was *unconstrained* mixing of two
    # Sources-section formats, which made the model's output non-deterministic.
    # The fix may either (a) keep only one format, or (b) allow both but
    # explicitly require the model to pick one and not mix them.
    if has_format_a and has_format_b:
        mixing_is_constrained = any(
            marker in prompt
            for marker in (
                "do not mix",
                "single, consistent citation style",
                "single consistent citation style",
            )
        )
        assert mixing_is_constrained, (
            "Issue #232 reproduced: "
            "compress_research_system_prompt contains competing "
            "Sources-section format instructions without a constraint "
            "forcing the model to pick one.\n"
            f"Format A present: {has_format_a}\n"
            f"Format B present: {has_format_b}"
        )
    else:
        # Only one format is present — no conflict possible.
        assert has_format_a or has_format_b, (
            "compress_research_system_prompt must define at least one "
            "Sources-section format."
        )

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

def test_cross_prompt_citation_format_consistency():
    """Issue #232: 压缩阶段与最终报告阶段的引用契约必须一致。

    原 issue 的症状是两处 prompt 对 Sources 格式给出冲突指令。
    修复方向可以是单格式，也可以是带互斥约束的双格式；
    关键要求是：两个 prompt 必须声明同一套契约。
    """
    compression_prompt = compress_research_system_prompt
    final_prompt = final_report_generation_prompt

    # 两个 prompt 必须都声明"选定一种风格、不得混用"的约束。
    for name, prompt in (
        ("compress_research_system_prompt", compression_prompt),
        ("final_report_generation_prompt", final_prompt),
    ):
        assert "single, consistent citation style" in prompt, (
            f"{name} 缺少单一引用风格的约束，"
            "无法保证跨 prompt 一致性。"
        )
        assert "do not mix" in prompt, (
            f"{name} 未禁止混用两种引用风格，"
            "Issue #232 可能复现。"
        )

    # 两个 prompt 必须提供同一组可选风格：编号 + inline。
    for name, prompt in (
        ("compress_research_system_prompt", compression_prompt),
        ("final_report_generation_prompt", final_prompt),
    ):
        assert "Style A (numbered)" in prompt, (
            f"{name} 缺少编号引用风格的定义。"
        )
        assert "Style B (inline links)" in prompt, (
            f"{name} 缺少 inline 引用风格的定义。"
        )

    # 两个 prompt 必须都要求正文引用与 ### Sources 列表精确匹配。
    for name, prompt in (
        ("compress_research_system_prompt", compression_prompt),
        ("final_report_generation_prompt", final_prompt),
    ):
        assert "### Sources" in prompt, (
            f"{name} 缺少 ### Sources 段落要求。"
        )
        assert "match exactly" in prompt, (
            f"{name} 未要求正文引用与 Sources 列表精确匹配。"
        )