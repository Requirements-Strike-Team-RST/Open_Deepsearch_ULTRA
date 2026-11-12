# Coding-Agent Permission Model

> **Purpose:** What each coding-agent role may read, write and run, what needs the human's confirmation, and how a task receives its permissions.
> **Authoritative for:** roles, paths, tools and approval delegation. Behaviour rules are in `.opencode/rules.md`; the workflow is in `Prompt.md`.
> **Maintained by:** humans.
> **Last updated:** 2026-11-12

## 1. Principles

Every action falls into one of three tiers:

| Tier | Effect | Used for |
|---|---|---|
| **Allow** | Runs without asking | Routine work of the role: reading, searching, editing, running checks, committing, read-only web and documentation lookups (`webfetch`, `websearch`, Context7) |
| **Ask** | The human confirms each time | Legitimate but risky actions: pushing, rewriting local history, changing dependencies, raw network commands (`curl`, `wget`), unapproved MCP tools, deleting files, editing governance documents |
| **Deny** | Never runs, even if the human confirms | Reading secrets, changing permissions or approval records, force-pushing, `sudo`, and edits that break role separation |

The configuration controls tool access; it does not isolate the process. Anything an agent changes appears in the PR diff, and review is the final control.

## 2. Roles

| Role | Job | Edits | Commands without asking (§4) |
|---|---|---|---|
| **Plan** | Software architecture: EVAL entries, ADRs, module sections | SA documents (§3) and other documentation; never source, tests or `scripts/` | Read-only, checks, Git add and commit |
| **Test Author** | Tests that fail on the baseline | `test/offline/`, `test/live/` and documentation; never source, `scripts/` or other code under `test/` | Read-only, checks, `ruff format` on tests, Git add, commit and switch |
| **Build** | Implementation that makes the approved tests pass | Source, `scripts/`, evaluation code under `test/` and documentation, within the approval record (§5); never `test/offline/` or `test/live/` | Read-only, checks, `ruff format` on `src/`, Git add, commit and switch |
| **Verify** | Independent verification | Documentation, including its reports in `docs/test-reports/`; never source, tests or `scripts/` | Read-only, checks, Git add and commit |

Test Author and Build never edit each other's files, so an implementation cannot pass by changing its tests. Edits to governance documents and dependency files ask for every role; edits to SA documents ask for every role except Plan (§3). All roles may read the whole repository except secrets, search with `glob`, `grep`, `list` and `lsp`, and delegate searches to the read-only `explore` sub-agent.

## 3. Path Ownership

**SA documents:** `docs/architecture/*` except `permission-model.md`, plus `docs/code-governance/structural-constraints.md` and `verification-constraints.md`. Plan writes them freely during software architecture; Test Author, Build and Verify edit them only when the human confirms, so implementation cannot change the architecture silently. The ADR template `adr/000-template.md` is not edited by agents.

**Governance documents (human-owned):** `AGENTS.md`, `Prompt.md`, `.agent/*`, `.github/*`, `docs/req/*`, `docs/architecture/permission-model.md`, `docs/code-governance/mcp-tool-manifest.md`, `docs/ai-use-log.yaml`, `docs/review-memo.md`, `docs/bug-diary.md`, `docs/debt-register.md`. **Dependency files:** `pyproject.toml`, `uv.lock`. Agents edit these only when the human confirms; the change still goes through PR review.

**Never editable by agents:** `.opencode/*`, `opencode.json*` and `docs/approvals/*`, so that no agent can widen its own permissions or forge an approval.

**Secrets:** `.env*` (except `.env.example`) and `.git/*` are never read, through the read tool or through a command.

## 4. Commands

Rules for the `bash` tool. A command matching none of the rows asks the human.

| Commands | Plan | Test Author | Build | Verify |
|---|---|---|---|---|
| Read-only: `ls`, `pwd`, `cat`, `head`, `tail`, `wc`, `rg`, `grep`, `find`, `tree` | allow | allow | allow | allow |
| Read-only Git: `status`, `diff`, `log`, `show`, `branch`, `blame` | allow | allow | allow | allow |
| Checks: `uv sync`, `uv run pytest`, `uv run ruff check`, `uv run mypy`, `uv run python scripts/validate_requirements.py` | allow | allow | allow | allow |
| `git add`, `git commit` | allow | allow | allow | allow |
| `uv run ruff format` | ask | allow on `test/offline`, `test/live`; ask elsewhere | allow on `src`; ask elsewhere | ask |
| `git switch` | ask | allow | allow | ask |
| `git push`, `git reset`, `git rebase`, `git checkout`, `git stash` | ask | ask | ask | ask |
| `uv add`, `uv remove`, `pip install`, `curl`, `wget`, `rm`, `sed -i`, shell redirection `>` | ask | ask | ask | ask |
| Force-push (`push --force`, `push -f`), `sudo`, anything touching `.env*`, `.opencode/`, `opencode.json` or `docs/approvals/` | deny | deny | deny | deny |

Ask and deny rules match anywhere in the command, so `git commit -m x && git push` asks and `x && git push --force` is denied.

**Other tools:** `question`, `todowrite`, `webfetch`, `websearch` and the tools of approved MCP servers are allowed; other MCP tools, skills and directories outside the repository ask; sub-agents other than `explore` are denied. `curl` and `wget` ask because, unlike the read-only web tools, they can send data out. MCP servers are approved in `docs/code-governance/mcp-tool-manifest.md` and configured in `.opencode/permissions.jsonc`.

## 5. Approval and Permission Delegation

`docs/approvals/<task-id>.md` is written by the human only and records two gates (`Prompt.md` §4, §6):

| Gate | Recorded fields |
|---|---|
| Gate 1 — SA Review | SA review record (`SA-NNN` in `docs/review-memo.md`), accepted ADRs, approver, date |
| Gate 2 — Tests | Approved test commit, approver, date |

Build implements the accepted ADR, starting from the approved test commit; the PR review compares the diff with the ADR's components and implementation steps. An architecture change needs a new SA Review (`Prompt.md` §10), and a change to an approved test invalidates Gate 2. No configuration change or session restart is needed for either gate.

## 6. Configuration and Acceptance

**Configuration.** `.opencode/permissions.jsonc` holds the rules. It defines the `plan`, `test-author`, `build` and `verify` agents and the read-only `explore` sub-agent, configures the approved MCP servers, makes `plan` the default agent, and denies everything to agents it does not define. OpenCode does not load a file named `permissions.jsonc`; `.opencode/opencode.jsonc` is a symlink to it, so edit only `permissions.jsonc` and keep the symlink. On Windows, clone with `core.symlinks=true`.

**Merging.** A member's global OpenCode configuration and plugins merge with the project configuration. Work only in the `plan`, `test-author`, `build` and `verify` agents and do not start OpenCode with `--auto`, which approves every *ask*.

**Acceptance.** On OpenCode 2.2.7 (2026-11-12), `opencode debug config` showed that `.opencode/opencode.jsonc` is loaded, and the rules resolved by `opencode debug agents` were evaluated against 83 cases covering every tier for every role: reads and secret reads, SA-document, governance, source and test edits per role, the Test Author and Build separation, web, Context7 and unapproved MCP tools, permission and approval tampering through the edit tool and the shell, routine commands, push, reset, rebase, dependency and network commands, force-push, chained commands, sub-agents and undefined agents. Result: **PASS, 83/83**. OpenCode resolves the `bash` key to the action `shell` and `task` to `subagent`.
