"""Context module: token-limit recovery during research compression.

Implements REQ-005, ADR-004, INV-001, POL-012 to POL-014. ``trimming.py`` splits
a history into whole turns and removes the oldest one; ``recovery.py`` retries a
compression call, freeing context from the oldest end on a token-limit error and
reporting an unreducible history as a typed failure instead of placeholder text.
Trimming code never calls a model.
"""
