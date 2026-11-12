# AGENTS.md — Global Development Guidelines

> **Purpose:** Entry point for every coding agent: project context, reading order, document authority, environment, collaboration rules.
> **Authoritative for:** environment, coding practices, Git and PR rules, feedback format, and the document map below.
> **Maintained by:** humans. Agents propose changes; see `docs/architecture/permission-model.md` §3.
> **Last updated:** 2026-11-11

## 1. Project Overview

This project improves [LangChain AI / Open Deep Research](https://github.com/langchain-ai/open_deep_research), a LangGraph agent that uses large language models, search tools and MCP servers to research a question and write a report. The team improves it through bug fixes, features, behaviour-preserving refactoring and necessary structural changes, each driven by a requirement in `docs/req/requirements.yaml`.

Two kinds of agent appear in this repository and must not be confused:

| Term | Meaning | Governed by |
|---|---|---|
| **Coding agent** | The Plan, Test Author, Build and Verify roles that change this repository | this file, `Prompt.md`, `.opencode/rules.md`, `docs/architecture/permission-model.md` |
| **Research agent** | The runtime `supervisor` and `researcher` inside Open Deep Research, i.e. the product being improved | `docs/architecture/architecture-blueprint.md`, `docs/architecture/invariants.md`, `docs/architecture/runtime-policy-catalog.md` |

## 2. Reading Order

1. **Always:** `README.md` → this file → `Prompt.md` → `.opencode/rules.md`.
2. **For the task at hand:** `docs/req/requirements.yaml` (the assigned requirement) → `docs/architecture/architecture-blueprint.md` → `docs/architecture/invariants.md` → `docs/code-governance/structural-constraints.md` → the ADRs for the requirement.
3. **Before writing anything:** `docs/architecture/permission-model.md` and `docs/code-governance/verification-constraints.md`.
4. **During tests and implementation:** the accepted ADR, the module's sections in `structural-constraints.md` §10 and `verification-constraints.md` §7, and the approval record for the requirement ID (RID).

## 3. Document Map and Authority

Each concern has exactly one authoritative document. Other documents refer to it instead of repeating it.

| Concern | Authoritative document | Maintained by |
|---|---|---|
| Requirements, priorities, owners, fit criteria | `docs/req/requirements.yaml`, validated against `docs/req/req-schema.json` | humans |
| Task workflow, phases, human gates | `Prompt.md` | humans |
| Always-on agent behaviour rules | `.opencode/rules.md` (`.agent/rules.md` only points to it) | humans |
| Roles, readable and writable paths, tools, approval delegation | `docs/architecture/permission-model.md`, enforced through `.opencode/permissions.jsonc` | humans |
| Architecture, module list, deterministic boundaries | `docs/architecture/architecture-blueprint.md` and `docs/architecture/adr/` | module owners (ADRs), integrated before SA Review |
| Invariants | `docs/architecture/invariants.md` | module owners, integrated before SA Review |
| Requirement traceability | `docs/architecture/trace-matrix.md` | module owners |
| State and memory design | `docs/architecture/memory-design.md` | module owners, integrated before SA Review |
| Runtime exception, degradation and failure policies | `docs/architecture/runtime-policy-catalog.md` | module owners, integrated before SA Review |
| ADD: candidate solutions and their comparison | `docs/architecture/evaluation-table.md` | module owners |
| Code structure and change rules | `docs/code-governance/structural-constraints.md` | humans; module owners add their module sections |
| Verification layers, test conventions, CI gates, Definition of Done | `docs/code-governance/verification-constraints.md` | humans; module owners add their module sections |
| Tools available to coding agents | `docs/code-governance/mcp-tool-manifest.md` | humans |
| AI-use record | `docs/ai-use-log.yaml` | humans |
| PR review record | `docs/review-memo.md` | reviewers |
| Significant bugs | `docs/bug-diary.md` | humans |
| Technical debt | `docs/debt-register.md` | humans |
| CI gates | `.github/workflows/ci.yml` | humans |
| Annotated agent transcripts | `transcripts/` | each student |

Precedence when documents disagree: the authoritative document for the concern wins; `requirements.yaml` wins over design, invariants and ADRs on *what* the system must do; the blueprint wins on architecture until an ADR changes it. Report every significant conflict to a human even when precedence resolves it (`.opencode/rules.md` R7).

A referenced document that does not exist yet (for example `docs/approvals/`, `docs/build-reports/`, `docs/test-reports/`) may only be created by the role allowed to write it in the permission model, and only after telling the human which document and why.

## 4. Development Environment

- **Python:** 3.12, pinned in `.python-version`. CI and LangGraph deployment use the same version.
- **Dependencies:** `uv` with `pyproject.toml` and `uv.lock`; run project commands with `uv run`. Development tools come from the `dev` extra (`uv sync --extra dev`).
- **New dependencies:** prefer existing ones (for HTTP use `httpx`). Adding a third-party dependency needs a stated reason and the human's agreement beforehand.
- **Secrets:** API keys and credentials live in `.env`, never in the repository; examples go in `.env.example`.
- **Lint and types:** Ruff, configured in `pyproject.toml`; mypy is optional.
- **Tests:** pytest, following `docs/code-governance/verification-constraints.md`.

Do not change the Python version, the dependency manager or project configuration without human authorisation.

## 5. Coding and Commenting Practices

- **Clarity first:** code should be correct, readable and maintainable; use abstractions and patterns only where they reduce complexity.
- **Modularity:** high cohesion, low coupling; reuse existing modules instead of duplicating them. Module boundaries are in `structural-constraints.md`.
- **Style:** PEP 8, the Ruff configuration in `pyproject.toml` and `.editorconfig` (UTF-8, LF line endings, 4-space indentation for Python and TOML, 2 spaces elsewhere; `.gitattributes` enforces LF in Git); type annotations on new public code.
- **Comments:** explain intent, non-obvious behaviour and constraints, not what the code already says. Public functions and new modules get docstrings that name the RID they implement (`structural-constraints.md` §9).
- **Exceptions:** handle expected errors explicitly; never swallow an error silently or catch broadly to hide a failure.
- **Scope:** change only what the task needs. Do not reformat or refactor untouched code; `ruff check` must pass and `ruff format` applies to new files and changed lines only.

## 6. Global Constraints

- Follow the workflow and human gates in `Prompt.md` for the current role; do not mix roles or skip steps.
- Stay within the assigned RID and its approved scope; do not expand it.
- Do not bypass permission or approval gates, and do not edit governance documents, tests or thresholds to make a check pass.
- Report documentation conflicts, insufficient permissions and acceptance criteria that cannot be met, and wait for a human decision.

This file does not grant permissions; `permission-model.md` does.

## 7. Git and Team Collaboration

### 7.1 Branches

- One independent improvement per branch; keep its code, tests and documentation together and keep unrelated work apart.
- Branch names are English, lowercase, hyphenated, with a conventional prefix: `feat/`, `fix/`, `refactor/`, `docs/`, `test/`, `chore/` (for example `fix/research-failure-handling`).
- Never commit directly to `main` unless a human explicitly authorises it.
- Never force-push or otherwise overwrite remote history. `git reset` and `git rebase` are for local commits that have not been pushed; a coding agent runs them, and `git push`, only when the human confirms.

### 7.2 Commits and Pull Requests

- Commit messages in English, Conventional Commits style (`feat: add citation validation`).
- One PR per improvement. Title and description in English, stating the change, the RIDs and the verification actually performed with its results.
- A PR merges into `main` only with **approval from at least two other team members** and all active CI gates green. Do not bypass required reviews.
- Address review comments with new commits on the same branch; do not close and recreate the PR.
- Coding agents may assist with reviews; the human reviewer remains responsible for the decision.

## 8. Feedback to the User

Report only work actually performed. As applicable:

- **Completed work:** what changed, and which files.
- **Verification:** which checks ran and their verdicts (`PASS / FAIL / NOT_RUN / BLOCKED / N/A`); name every check that was not run or failed.
- **Traceability:** whether affected documents and the `trace-matrix.md` row were updated.
- **Outstanding issues:** outdated documents, unresolved conflicts, incomplete traceability, pending work.

Do not claim to have checked areas outside the task, and do not guess completion status.
