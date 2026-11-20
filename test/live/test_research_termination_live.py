"""REQ-003: the baseline queries end covered on a search-capable configuration.

Covers TC-ORC-13 (``verification-constraints.md`` §7, orchestration; REQ-003
C-006). The case is ``automated: false``: the team's earlier baseline ran with
search disabled, so a human chooses the configuration (``test/live/conftest.py``)
and interprets the result. The evidence goes to ``docs/test-reports/REQ-003.md``.

The expectation is REQ-003 C-006: at least one of the two baseline queries exits
``covered`` and at most one reaches the iteration cap. Each run is one streamed
graph execution over the real model and the chosen search source.
"""

import pytest
from conftest import live_settings, run_config

BASELINE_QUERIES = (
    "Which regulation governs battery recycling in the EU and when was it replaced?",
    "How many battery recycling plants opened in the EU in 2024, and what share of batteries is recycled?",
)

pytestmark = pytest.mark.live


def test_baseline_queries_exit_reasons():
    """TC-ORC-13 / C-006: at least one baseline query exits covered and at most one hits the cap."""
    settings = live_settings()
    from open_deep_research.deep_researcher import deep_researcher

    states = []
    for query in BASELINE_QUERIES:
        final_state = {}
        for chunk in deep_researcher.stream(
            {"messages": [("user", query)]},
            run_config(settings),
            stream_mode="values",
        ):
            final_state = chunk
        states.append(final_state)

    exit_reasons = [state.get("exit_reason") for state in states]
    outcomes = [state.get("research_outcome") for state in states]
    details = [state.get("exit_detail") for state in states]
    # The evidence for the test report is the reason, the outcome and the detail of each run.
    evidence = f"exit reasons {exit_reasons}; outcomes {outcomes}; details {details}"

    assert all(
        reason in {"covered", "budget_exhausted", "stalled", "failed"}
        for reason in exit_reasons
    ), f"every run states one exit reason; {evidence}"
    covered = sum(1 for reason in exit_reasons if reason == "covered")
    at_cap = sum(1 for reason in exit_reasons if reason == "budget_exhausted")
    assert covered >= 1, (
        f"at least one run must exit covered (baseline was zero); {evidence}"
    )
    assert at_cap <= 1, (
        f"at most one run may reach the cap (baseline was two); {evidence}"
    )
