# MCP and Tool Manifest

> **Purpose:** The tools coding agents may use, per role. Anything not listed is denied.
> **Authoritative for:** the tool list. Tiers and command rules are in `docs/architecture/permission-model.md`; the enforcing configuration is `.opencode/permissions.jsonc`.
> **Maintained by:** humans.
> **Last updated:** 2026-11-11

## Tools

| Tool | Plan | Test Author | Build | Verify |
|---|---|---|---|---|
| `read` | allow, except secrets | allow, except secrets | allow, except secrets | allow, except secrets |
| `edit` (`write`, `edit`, `apply_patch`) | allow; deny on code and tests | allow on tests and docs; deny on other code | allow; deny on `test/offline/`, `test/live/` | allow; deny on code and tests |
| `glob`, `grep`, `list`, `lsp`, `question`, `todowrite` | allow | allow | allow | allow |
| `bash` | see `permission-model.md` §4 | see `permission-model.md` §4 | see `permission-model.md` §4 | see `permission-model.md` §4 |
| `task` | `explore` only | `explore` only | `explore` only | `explore` only |
| `webfetch`, `websearch`, approved MCP servers (below) | allow | allow | allow | allow |
| Other MCP tools, `skill`, external directories | ask | ask | ask | ask |

Edits to governance documents and dependency files ask for every role (`permission-model.md` §3). All roles are denied edits to `.opencode/*`, `opencode.json*` and `docs/approvals/*`, and every access to `.env*` except `.env.example`.

## MCP Servers, Plugins, Skills, Sub-Agents

To add one, a human records it here, configures it under `mcp` in `.opencode/permissions.jsonc` and allows its tools (`<name>_*`) for the roles that need it.

| Name | Endpoint | Roles | Access | Purpose | Added |
|---|---|---|---|---|---|
| `context7` | `https://mcp.context7.com/mcp` (remote) | All roles | Read-only | Current library and framework documentation | 2026-11-11 |
