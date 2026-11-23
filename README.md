# Open Deep Research ULTRA

Open Deep Research ULTRA is the Requirements Strike Team's CS5351 fork of [Open Deep Research](https://github.com/langchain-ai/open_deep_research) ([GitHub repository](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA)). A supervisor delegates research, researchers gather and compress evidence, and a report writer synthesizes the findings. This fork makes it easier to tell what was researched, why the run stopped, and whether the result is complete.

## Project organization

```text
Open_Deepsearch_ULTRA/
├── README.md                                  # Project overview, setup, tests, and blocking gates
├── AGENTS.md                                  # Coding-agent entry point and governance map (D3)
├── architecture-blueprint.md                  # System-level architecture blueprint (D2.1)
├── Prompt.md                                  # Static coding-agent startup workflow prompt (D9)
├── Report.md                                  # Process summary report and member reflections (D6)
├── langgraph.json                             # LangGraph server and auth entry configuration
├── pyproject.toml / uv.lock                   # Python 3.12 dependencies and Ruff/pytest config
├── .opencode/                                 # Machine-readable role permissions & behavioral rules (D3)
├── .agent/rules.md                            # Project covenant entry point (D3)
├── .github/workflows/ci.yml                   # Blocking CI gates (D4/D7)
├── prompts/prompt_v1.0.yaml                   # Versioned runtime research prompts
├── scripts/validate_requirements.py           # Requirements schema and ID validator
├── docs/
│   ├── req/                                   # Machine-readable requirements.yaml & req-schema.json (D1)
│   ├── architecture/                          # ADRs (001–008), invariants, trace matrix, policies, risks (D2)
│   ├── code-governance/                       # Structural, verification, and MCP tool constraints (D3/D4)
│   ├── build-reports/                         # Implementation build and live test reports
│   ├── ai-use-log.yaml                        # Auditable AI-use log (D1)
│   ├── review-memo.md                         # PR and SA review records (D4)
│   ├── debt-register.md                       # Technical debt register (D4)
│   └── bug-diary.md                           # Significant bug diary (D4)
├── src/
│   ├── open_deep_research/                    # Research graph and extension modules (D8)
│   │   ├── orchestration/                     # REQ-001, REQ-003 (task contracts & termination)
│   │   ├── delivery/                          # REQ-002, REQ-004 (failure isolation & run outcome)
│   │   ├── context/                           # REQ-005 (turn-aware compression recovery)
│   │   ├── citations/                         # REQ-006 (shared citation format contract)
│   │   └── search/                            # REQ-007, REQ-008 (search validation & fallback)
│   └── security/auth.py                       # Upstream LangGraph server auth middleware
├── test/
│   ├── offline/                               # Deterministic offline tests (172 cases, no API keys) (D4/D8)
│   ├── live/                                  # Opt-in live API tests (D8)
│   └── evaluation/                            # REQ-009, REQ-010 standalone report evaluation module
└── transcripts/                               # Annotated student agent-session transcripts (D5)
```

## What we improved

- **Typed tasks and coverage-based completion (REQ-001, REQ-003).** Research tasks have required questions and a tool-call budget. The program checks whether findings cite sources retrieved by the task and uses those findings to measure coverage. A model's request to stop is not proof that research is complete.
- **Failure isolation and explicit outcomes (REQ-002, REQ-004).** Delegations queue when the concurrency limit is reached. One researcher can fail without discarding successful sibling results. Runs distinguish `complete`, `partial`, and `failed`; a run with no validated findings skips report generation.
- **Context recovery and consistent citations (REQ-005, REQ-006).** Compression recovery removes the oldest whole turns first, keeping tool results with their calls and preserving the newest turn. Compression and report prompts share one numbered citation format.
- **Early search validation and ordered fallback (REQ-007, REQ-008).** Invalid search setups are rejected before the first model or search call. Eligible tool failures can try configured alternatives in order. A successful search with no results does not trigger fallback.
- **Reliable evaluation (REQ-009, REQ-010).** An invalid or unavailable metric is reported as `not_evaluable`, not turned into a zero. An existing report can be scored without running the research graph again.

## Quickstart

You need Python 3.12, [uv](https://docs.astral.sh/uv/), and credentials for your chosen model and search providers. The default research workflow uses [DeepSeek Flash](https://api-docs.deepseek.com/) and Tavily search.

```bash
git clone https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA.git
cd Open_Deepsearch_ULTRA
uv sync --locked
```

If you do not already have a `.env` file, copy `.env.example` to `.env`. For the default research workflow, set `DEEPSEEK_API_KEY` and `TAVILY_API_KEY`. The separate report evaluation command still uses `OPENAI_API_KEY`. Keep credentials out of Git. Then start the development server:

```bash
uv run langgraph dev --allow-blocking
```

Open [LangGraph Studio](https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024), select **Deep Researcher**, and submit a question in `messages`. For example: “Which regulation governs battery recycling in the EU?” The local [API documentation](http://127.0.0.1:2024/docs) is also available while the server is running.

## Enable the improved research workflow

Set these values in `.env` and restart the development server, or use the corresponding settings in Studio:

```dotenv
SEARCH_API=tavily
TASK_CONTRACT_ENABLED=true
CONTEXT_TRIMMING=true
COVERAGE_THRESHOLD=0.8
```

`task_contract_enabled` and `context_trimming` default to `false`; `search_fallback` defaults to an empty list. Early search validation and the shared citation format apply without a flag. Environment variables take precedence over per-run settings in Studio.

With `task_contract_enabled` on, inspect these fields in the final state:

- `task_results`: individual task outcomes and their validated findings.
- `exit_reason` and `exit_detail`: why the research loop stopped. Possible reasons include `covered`, `budget_exhausted`, `stalled`, and `failed`.
- `research_outcome`, `outcome_detail`, and `failed_tasks`: the result of the run and the details needed to interpret it. A partial report includes a limitations section. A failed run returns no report.

`context_trimming` handles context-limit errors during compression. It does not prevent a model from running out of **output** tokens while writing the required findings block. If long tasks return `invalid_result` and the compression response is visibly cut off, try a higher `COMPRESSION_MODEL_MAX_TOKENS` within your provider's limits. A local trial succeeded at `32768` where `8192` truncated the response; this is a configuration-specific mitigation, not a guarantee. See [RISK-003](docs/architecture/risk-list.md).

## Model and search configuration

The four model settings in [`configuration.py`](src/open_deep_research/configuration.py) default to `deepseek:deepseek-flash`. Override them in Studio or with these environment variables:

- `SUMMARIZATION_MODEL`: summarizes retrieved web pages.
- `RESEARCH_MODEL`: handles planning and research.
- `COMPRESSION_MODEL`: consolidates research findings.
- `FINAL_REPORT_MODEL`: writes the final report.

DeepSeek Flash uses non-thinking mode in the research workflow so the current client can handle multi-turn tool calls.

Select models that support the structured output or tool calling used by their stage. Each researcher decides when to search using the tools available to it. Choose a search provider with `SEARCH_API` or `search_api`:

- **`tavily` (default):** uses the `tavily_search` tool. Set `TAVILY_API_KEY` and credentials for the configured models, including the webpage summarizer.
- **`openai` or `anthropic`:** uses native search inside a compatible model call. `research_model` must match the selected provider, and its API key is required (`OPENAI_API_KEY` or `ANTHROPIC_API_KEY`). Native search is not supported with `task_contract_enabled`, because the task contract needs tool results to check retrieved URLs.
- **`none`:** disables built-in search. Configure at least one usable MCP search tool; otherwise the run is rejected.

### MCP search and fallback

Set `mcp_config` in the assistant configuration. `url` is the server's base URL; the agent appends `/mcp` and connects over streamable HTTP. `tools` lists the exact tool names to expose. Do not put credentials in the URL or commit them to the repository.

```json
{
  "search_api": "tavily",
  "mcp_config": {
    "url": "https://search.example.org",
    "tools": ["self_hosted_search"],
    "auth_required": false
  },
  "search_fallback": ["self_hosted_search"]
}
```

In this example, an eligible Tavily error, such as a timeout or rate limit, can fall back to `self_hosted_search`. Each fallback entry must be `tavily` or a name listed in `mcp_config.tools`. An MCP fallback tool must take exactly one required string argument. For MCP-to-Tavily fallback, list both the MCP tool and `tavily` in `search_fallback`. The equivalent environment setting is comma-separated (`SEARCH_FALLBACK=self_hosted_search,tavily`). If no configured source succeeds after an eligible failure, the error lists the failed attempts.

## Score an existing report

The evaluation command reads a report file and scores it with `gpt-4.1`. Set `OPENAI_API_KEY` in the shell before running it. It does not need a search key or start a new research run.

```bash
uv run python -m test.evaluation.entry \
  --question "Which regulation governs battery recycling?" \
  --report path/to/report.md
```

Optional inputs are text, not file paths: `--reference-answer` for correctness, `--research-brief` for completeness, and `--evidence` for groundedness. The JSON result contains a report ID and the status, score, and reason for each metric. A `not_evaluable` metric has a `null` score. Exit code `0` means the command produced results; `2` indicates an input error, such as a blank question or an unreadable report.

The existing benchmark runner, [`test/run_evaluate.py`](test/run_evaluate.py), is separate: it runs the research graph for each dataset example and can incur model and search costs. Upstream leaderboard results are not results for this fork.

## Prompts, verification, and contributions

Runtime research prompts are maintained in [`prompts/prompt_v1.0.yaml`](prompts/prompt_v1.0.yaml). Edit the YAML rather than adding a second copy in the Python loader. Evaluation prompts in [`test/prompts.py`](test/prompts.py) are separate. Restart the local process after changing the YAML.

```bash
uv sync --locked --extra dev
uv run python scripts/validate_requirements.py
uv run ruff check src/open_deep_research test/offline scripts
uv run pytest test/offline -q
```

Offline tests use fake models and tools and do not need API keys. The final revision of [the implementation PR](https://github.com/Requirements-Strike-Team-RST/Open_Deepsearch_ULTRA/pull/24) passed 172 offline cases in CI. This does not establish live acceptance. To run the opt-in live cases, make provider credentials available to the test process and select a search-capable configuration:

```bash
export OPEN_DEEP_RESEARCH_LIVE_SEARCH_API=tavily
export OPEN_DEEP_RESEARCH_LIVE_RESEARCH_MODEL=deepseek:deepseek-flash
uv run pytest test/live -v
```

To run the full pytest suite (offline and live tests together, with provider credentials set):

```bash
uv run pytest test/offline test/live -v
```

### Blocking gates and branch protection

The repository enforces branch protection on `main` (pull requests required, at least two teammate approvals, and passing CI checks) together with the six course blocking gates defined in [`docs/code-governance/verification-constraints.md`](docs/code-governance/verification-constraints.md) §5 and [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

| Gate | Mechanism | What it checks |
|---|---|---|
| **Schema gate** | CI (`requirements-schema`) | Validates `docs/req/requirements.yaml` against `docs/req/req-schema.json` and checks unique/resolvable IDs. |
| **Static analysis gate** | CI (`static-analysis`) | Runs `ruff check` on `src/open_deep_research`, `test/offline`, and `scripts` (with `mypy` available locally via `uv run mypy src/open_deep_research`). |
| **Regression gate** | CI (`offline-tests`) | Runs the full deterministic offline suite (`uv run pytest test/offline -q`, 172 cases); any regression blocks merge. |
| **AI-use log gate** | CI (`ai-use-log`) | Runs `.github/check_ai_use_log.py` on pull requests to validate `docs/ai-use-log.yaml` and enforce explicit PR declarations (`AI use: yes/no` and new `AIU-NNN` IDs). |
| **Test approval gate** | Workflow & PR review (`Prompt.md` §6) | Separates Test Author and Build roles via `.opencode/permissions.jsonc` and requires human review of test cases before merging implementation changes. |
| **Semantic evaluation gate** | Live evaluation (`test/live/`, `test/evaluation/entry.py`) | Evaluates prompt or model changes against live research queries and report-scoring metrics when credentials are available. |

Pull requests declare `AI use: yes` or `AI use: no`. For `yes`, add a new entry to [`docs/ai-use-log.yaml`](docs/ai-use-log.yaml) and list its ID in the PR description, for example `AI-use log: AIU-028` (use the actual new ID). The CI check validates the declaration and log; it cannot infer AI use from the diff. Follow the [PR template](.github/pull_request_template.md) and the [project workflow](Prompt.md).

For the engineering process and team contributions, see the [project report](Report.md). For implementation details, start with the [architecture blueprint](architecture-blueprint.md) and [traceability matrix](docs/architecture/trace-matrix.md).

## Credits and license

Built on [LangChain AI's Open Deep Research](https://github.com/langchain-ai/open_deep_research). This fork retains the [MIT license](LICENSE).
