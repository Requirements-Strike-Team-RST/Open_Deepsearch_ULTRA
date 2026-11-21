"""REQ-006: live reports cite by number, each with exactly one Sources entry.

Covers TC-CIT-05 (``verification-constraints.md`` §7, citations; REQ-006 C-004).
The case is ``automated: false``: a human chooses the live configuration
(``test/live/conftest.py``) and judges the sample, and the runs that needed
truncated findings are reported apart (ADR-003 §3.3). The evidence goes to
``docs/test-reports/REQ-006.md``.

The report is the text the graph produces, without the limitations section that
a partial run appends, because that section is not part of the cited body.
"""

import re

import pytest
from conftest import live_settings, run_config, run_query

BASELINE_QUERIES = (
    "Which regulation governs battery recycling in the EU and when was it replaced?",
    "How many battery recycling plants opened in the EU in 2024, and what share of batteries is recycled?",
)
INLINE_CITATION = re.compile(r"\[(\d+)\](?!\()")
SOURCES_ENTRY = re.compile(r"^\s*\[(\d+)\]\s+\S", re.MULTILINE)
SOURCES_HEADING = re.compile(r"^#{1,6}\s*Sources\s*$", re.MULTILINE | re.IGNORECASE)
LIMITATIONS_HEADING = re.compile(
    r"^#{1,6}\s*Limitations\s*$", re.MULTILINE | re.IGNORECASE
)

pytestmark = pytest.mark.live


def report_body(text: str) -> str:
    """Return the report without the limitations section the node appends to a partial run."""
    match = LIMITATIONS_HEADING.search(text)
    return text[: match.start()] if match else text


def citation_numbers(text: str) -> tuple[set[int], set[int]]:
    """Return the numbers cited inline and the numbers listed in the Sources section."""
    body = report_body(text)
    heading = SOURCES_HEADING.search(body)
    cited = {
        int(number)
        for number in INLINE_CITATION.findall(
            body[: heading.start()] if heading else body
        )
    }
    listed = {
        int(number)
        for number in SOURCES_ENTRY.findall(body[heading.start() :] if heading else "")
    }
    return cited, listed


def test_reports_use_numbered_citations():
    """TC-CIT-05 / C-004: every inline [n] has exactly one matching ### Sources entry."""
    settings = live_settings()
    runs = [run_query(query, run_config(settings)) for query in BASELINE_QUERIES]

    truncated = [
        index
        for index, state in enumerate(runs)
        if state.get("research_outcome") == "partial"
    ]
    complete = [
        (index, state) for index, state in enumerate(runs) if index not in truncated
    ]
    problems = []
    # The runs that needed truncated findings are reported apart (ADR-003 §3.3).
    for index, state in complete:
        report = state.get("final_report") or ""
        cited, listed = citation_numbers(report)
        if not cited:
            continue
        missing = sorted(cited - listed)
        if missing:
            problems.append(f"run {index} cites {missing} without a Sources entry")
        if duplicates_of_sources(report):
            problems.append(
                f"run {index} lists {sorted(duplicates_of_sources(report))} more than once"
            )

    assert not problems, f"{problems}; partial runs reported separately: {truncated}"


def duplicates_of_sources(text: str) -> set[int]:
    """Return the numbers that more than one Sources entry claims."""
    body = report_body(text)
    heading = SOURCES_HEADING.search(body)
    if not heading:
        return set()
    seen: dict[int, int] = {}
    for number in SOURCES_ENTRY.findall(body[heading.start() :]):
        seen[int(number)] = seen.get(int(number), 0) + 1
    return {number for number, count in seen.items() if count > 1}
