"""The citation format of the research prompts, as text only.

REQ-006, ADR-005 §3, INV-008. The three constants contain no ``{`` or ``}``, so
the ``.format(...)`` calls on the assembled prompts cannot break them.
``prompts.py`` inserts ``CITATION_RULES_BLOCK`` into both prompts,
``SOURCES_SECTION_POINTER`` into the compression prompt and
``RENUMBER_ACROSS_FINDINGS_INSTRUCTION`` into the report prompt, once each.
"""

CITATION_RULES_BLOCK = """<Citation Rules>
- Assign each unique URL a single citation number as an inline marker in your text, e.g. [1].
- End with a section headed ### Sources that lists every cited source, one per line, as [n] Title: URL.
- Number sources sequentially without gaps (1,2,3,4...) in the final list.
- Example format:
  [1] Source Title: URL
  [2] Source Title: URL
</Citation Rules>"""

SOURCES_SECTION_POINTER = (
    "End with the Sources section specified in the Citation Rules below."
)

RENUMBER_ACROSS_FINDINGS_INSTRUCTION = (
    "The findings above come from several researchers that each numbered their "
    "sources from 1. Renumber all citations into one sequence so that each URL "
    "has exactly one number in the report, and list every cited URL once in the "
    "Sources section."
)
