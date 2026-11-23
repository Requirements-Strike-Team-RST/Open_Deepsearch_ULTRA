"""Citations module: the one citation format shared by the research prompts.

Implements REQ-006, ADR-005, INV-008. This module holds text only; ``prompts.py``
inserts the constants into both prompt templates once, at module load, so the
compression prompt and the final report prompt cannot drift apart again.
"""
