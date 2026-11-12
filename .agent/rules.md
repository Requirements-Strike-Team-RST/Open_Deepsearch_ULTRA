# Agent Rules

> **HUMAN-ONLY FILE — agents must not modify it.**
> **Purpose:** Entry point for tools that look for rules under `.agent/`. It defines no rules of its own.
> **Last updated:** 2026-11-11

The canonical rules for every coding agent are in **`.opencode/rules.md`** (R1–R8). Read them, then follow the reading order in `AGENTS.md` §2.

| Need | Document |
|---|---|
| Project context, environment, Git and PR rules, document authority | `AGENTS.md` |
| Workflow and human gates | `Prompt.md` |
| Behaviour rules | `.opencode/rules.md` |
| Paths, tools and approval delegation | `docs/architecture/permission-model.md` |
| Code structure and change rules | `docs/code-governance/structural-constraints.md` |
| Verification and Definition of Done | `docs/code-governance/verification-constraints.md` |
| Requirements | `docs/req/requirements.yaml` |

If this file ever disagrees with `.opencode/rules.md`, the latter wins; report the difference to a human (`.opencode/rules.md` R7).
