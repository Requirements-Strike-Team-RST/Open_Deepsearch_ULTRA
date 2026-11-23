"""Delivery module: fail-isolated fan-out and join, run outcome and limitations.

Implements REQ-002 and REQ-004, ADR-002 and ADR-003, INV-002 and INV-007.
``execution.py`` runs the delegated tasks of one supervisor turn so that one
failure fails one task; ``outcome.py`` decides whether the run was complete,
partial or failed and writes the limitations section.
"""
