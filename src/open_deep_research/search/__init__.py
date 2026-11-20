"""Search module: configuration validation and ordered search fallback.

Implements REQ-007 (ADR-006, INV-005) and REQ-008 (ADR-008, INV-010).
``validation.py`` rejects an invalid search configuration, or a run without any
search tool, before the first model or search call; ``fallback.py`` wraps the
search tools so that a failed call tries the configured fallback sources in
order.
"""
