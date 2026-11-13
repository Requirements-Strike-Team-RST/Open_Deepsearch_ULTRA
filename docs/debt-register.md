# Technical Debt Register

> **Purpose:** Known technical debt, its impact and the plan to pay it.
> **Maintained by:** humans; agents propose entries in their reports.
> **Last updated:** 2026-11-11

## Entry Template

| ID | Area | Description | Impact | Category | Action | Status |
|---|---|---|---|---|---|---|

Category: code, test, documentation, tooling or architecture. Status: open, planned, paid.

## Register

| ID | Area | Description | Impact | Category | Action | Status |
|---|---|---|---|---|---|---|
| DEBT-001 | `src/security/auth.py` | 7 `ruff check` violations (D100, D103, D202, I001) in the baseline | Path excluded from the static-analysis gate | code | Fix under its own review (auth changes need separate review), then add the path to the gate | open |
| DEBT-002 | `test/*.py` evaluation scripts | 11 `ruff check` violations (T201, I001, F541) in `run_evaluate.py`, `extract_langsmith_data.py`, `supervisor_parallel_evaluation.py` | Paths excluded from the static-analysis gate | test | Fix when REQ-009 or REQ-010 touches these scripts | open |
| DEBT-003 | `src/open_deep_research/` | 5 baseline files are not `ruff format`-clean | Formatting is applied to new files and changed lines only | code | Reformat in one dedicated `chore/` PR when no feature branch is open | open |
| DEBT-004 | mypy | `mypy src/open_deep_research` fails on import resolution without configuration | Type checking cannot be gated | tooling | Add mypy configuration, then add it to the static-analysis gate | open |
