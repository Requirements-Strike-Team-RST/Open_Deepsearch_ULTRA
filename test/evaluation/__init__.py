"""Evaluation package: valid metric results and an evaluation-only entry.

REQ-009, REQ-010, ADR-007. ``metrics`` holds the result type, the deterministic
validation and the metric groups; ``entry`` scores an existing report without
running research or search. Neither module imports the research graph.
"""
