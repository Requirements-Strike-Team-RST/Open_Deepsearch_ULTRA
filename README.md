# 🔬 Open Deep Research

<img width="1388" height="298" alt="full_diagram" src="https://github.com/user-attachments/assets/12a2371b-8be2-4219-9b48-90503eb43c69" />

Deep research has broken out as one of the most popular agent applications. This is a simple, configurable, fully open source deep research agent that works across many model providers, search tools, and MCP servers. It's performance is on par with many popular deep research agents ([see Deep Research Bench leaderboard](https://huggingface.co/spaces/Ayanami0730/DeepResearch-Leaderboard)).

<img width="817" height="666" alt="Screenshot 2025-07-13 at 11 21 12 PM" src="https://github.com/user-attachments/assets/052f2ed3-c664-4a4f-8ec2-074349dcaa3f" />

### 🔥 Recent Updates

**August 14, 2025**: See our free course [here](https://academy.langchain.com/courses/deep-research-with-langgraph) (and course repo [here](https://github.com/langchain-ai/deep_research_from_scratch)) on building open deep research.

**August 7, 2025**: Added GPT-5 and updated the Deep Research Bench evaluation w/ GPT-5 results.

**August 2, 2025**: Achieved #6 ranking on the [Deep Research Bench Leaderboard](https://huggingface.co/spaces/Ayanami0730/DeepResearch-Leaderboard) with an overall score of 0.4344. 

**July 30, 2025**: Read about the evolution from our original implementations to the current version in our [blog post](https://rlancemartin.github.io/2025/07/30/bitter_lesson/).

**July 16, 2025**: Read more in our [blog](https://blog.langchain.com/open-deep-research/) and watch our [video](https://www.youtube.com/watch?v=agGiWUpxkhg) for a quick overview.

### 🚀 Quickstart

1. Clone the repository and activate a virtual environment:
```bash
git clone https://github.com/langchain-ai/open_deep_research.git
cd open_deep_research
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

2. Install dependencies:
```bash
uv sync
# or
uv pip install -r pyproject.toml
```

3. Set up your `.env` file to customize the environment variables (for model selection, search tools, and other configuration settings):
```bash
cp .env.example .env
```

4. Launch agent with the LangGraph server locally:

```bash
# Install dependencies and start the LangGraph server
uvx --refresh --from "langgraph-cli[inmem]" --with-editable . --python 3.12 langgraph dev --allow-blocking
```

This will open the LangGraph Studio UI in your browser.

```
- 🚀 API: http://127.0.0.1:2024
- 🎨 Studio UI: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024
- 📚 API Docs: http://127.0.0.1:2024/docs
```

Ask a question in the `messages` input field and click `Submit`. Select different configuration in the "Manage Assistants" tab.

### ⚙️ Configurations

#### LLM :brain:

Open Deep Research supports a wide range of LLM providers via the [init_chat_model() API](https://python.langchain.com/docs/how_to/chat_models_universal_init/). It uses LLMs for a few different tasks. See the below model fields in the [configuration.py](https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/configuration.py) file for more details. This can be accessed via the LangGraph Studio UI. 

- **Summarization** (default: `openai:gpt-4.1-mini`): Summarizes search API results
- **Research** (default: `openai:gpt-4.1`): Power the search agent
- **Compression** (default: `openai:gpt-4.1`): Compresses research findings
- **Final Report Model** (default: `openai:gpt-4.1`): Write the final report

> Note: the selected model will need to support [structured outputs](https://python.langchain.com/docs/integrations/chat/) and [tool calling](https://python.langchain.com/docs/how_to/tool_calling/).

> Note: For OpenRouter: Follow [this guide](https://github.com/langchain-ai/open_deep_research/issues/75#issuecomment-2811472408) and for local models via Ollama  see [setup instructions](https://github.com/langchain-ai/open_deep_research/issues/65#issuecomment-2743586318).

#### Search API :mag:

Open Deep Research supports a wide range of search tools. By default it uses the [Tavily](https://www.tavily.com/) search API. Has full MCP compatibility and work native web search for Anthropic and OpenAI. See the `search_api` and `mcp_config` fields in the [configuration.py](https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/configuration.py) file for more details. This can be accessed via the LangGraph Studio UI. 

The research model decides when to search: each researcher gets the configured search tool and calls it as often as its tool budget allows. Set `search_api` in the configuration (or `SEARCH_API` in `.env`, which takes precedence) to one of:

| `search_api` | What it uses | Research models it accepts | Key needed |
|---|---|---|---|
| `tavily` (default) | The Tavily search tool `tavily_search` | any | `TAVILY_API_KEY`, plus the key of the `summarization_model` |
| `openai` | OpenAI's native web search inside the model call | OpenAI models only: `openai:...`, or a bare name starting with `gpt-`, `o1`, `o3`, `chatgpt` or `text-davinci` | `OPENAI_API_KEY` |
| `anthropic` | Anthropic's native web search inside the model call | Anthropic models only: `anthropic:...`, or a bare name starting with `claude` | `ANTHROPIC_API_KEY` |
| `none` | Only the tools of an MCP search server (`mcp_config`) | any | whatever the MCP server needs |

The configuration is checked when a run starts, before any model or search call, and an invalid one stops the run with an error that names the setting to change: an unknown `search_api`, native search with a research model of another provider (Azure OpenAI, Bedrock, OpenRouter and unrecognised names are rejected too, because their native search is not verified), `search_api: none` without a usable `mcp_config`, `task_contract_enabled` with native search (native search returns no tool results whose URLs could be checked), or an unknown `search_fallback` entry. A run whose tools contain no search tool at all, for example because the MCP server returned none of the listed tools, also stops with a "no search tool is available" error.

**Custom or self-hosted search (MCP).** Set `search_api` to `none` (or keep a provider and add MCP tools next to it) and configure `mcp_config`:

```json
{"url": "https://search.example.org", "tools": ["self_hosted_search"], "auth_required": false}
```

`url` is the server's base URL (the agent connects to `<url>/mcp` over streamable HTTP), `tools` lists the tool names the researchers may use, and `auth_required: true` exchanges the Open Agent Platform user token for an MCP access token. `mcp_prompt` can tell the researchers how to use the tools.

**Search fallback.** `search_fallback` (or `SEARCH_FALLBACK`, comma-separated) lists the sources to try, in order, when a search call fails. Each entry is `tavily` or the name of a tool listed in `mcp_config.tools`; native search cannot be a fallback, and the empty list (the default) keeps the behaviour without fallback. For example, with `search_api: tavily`, `mcp_config.tools: ["self_hosted_search"]` and `search_fallback: ["self_hosted_search"]`, a Tavily call that times out is retried once on `self_hosted_search`. Only failures that another source could avoid fall back: timeouts, connection errors, rate limits (HTTP 429), server errors (HTTP 5xx) and rejected credentials (HTTP 401/403). A malformed query (HTTP 400), a missing API key and any other error are returned as they are, and an empty result is a result, not a failure. When every source fails, the researcher receives one `All search sources failed: ...` message that lists each source with its error. An MCP tool can be a fallback only if it takes exactly one required string argument (the query); a listed tool that did not load, or has another shape, is reported as `not available`.

#### Other 

See the fields in the [configuration.py](https://github.com/langchain-ai/open_deep_research/blob/main/src/open_deep_research/configuration.py) for various other settings to customize the behavior of Open Deep Research. 

### 📊 Evaluation

Open Deep Research is configured for evaluation with [Deep Research Bench](https://huggingface.co/spaces/Ayanami0730/DeepResearch-Leaderboard). This benchmark has 100 PhD-level research tasks (50 English, 50 Chinese), crafted by domain experts across 22 fields (e.g., Science & Tech, Business & Finance) to mirror real-world deep-research needs. It has 2 evaluation metrics, but the leaderboard is based on the RACE score. This uses LLM-as-a-judge (Gemini) to evaluate research reports against a golden set of reports compiled by experts across a set of metrics.

#### Usage

> Warning: Running across the 100 examples can cost ~$20-$100 depending on the model selection.

The dataset is available on [LangSmith via this link](https://smith.langchain.com/public/c5e7a6ad-fdba-478c-88e6-3a388459ce8b/d). To kick off evaluation, run the following command:

```bash
# Run comprehensive evaluation on LangSmith datasets
python test/run_evaluate.py
```

This will provide a link to a LangSmith experiment, which will have a name `YOUR_EXPERIMENT_NAME`. Once this is done, extract the results to a JSONL file that can be submitted to the Deep Research Bench.

```bash
python test/extract_langsmith_data.py --project-name "YOUR_EXPERIMENT_NAME" --model-name "you-model-name" --dataset-name "deep_research_bench"
```

This creates `test/expt_results/deep_research_bench_model-name.jsonl` with the required format. Move the generated JSONL file to a local clone of the Deep Research Bench repository and follow their [Quick Start guide](https://github.com/Ayanami0730/deep_research_bench?tab=readme-ov-file#quick-start) for evaluation submission.

#### Scoring an existing report

A report that already exists can be scored without running research or search, so
evaluating a report costs one judge call per metric group and no research budget:

```bash
uv run python -m test.evaluation.entry \
  --question "Which regulation governs battery recycling?" \
  --report path/to/report.md \
  [--reference-answer "text of the reference answer"] \
  [--research-brief "text of the research brief"] \
  [--evidence "text of the raw notes"]
```

`--report` is a file path; the optional inputs are passed as text. The judge
is the baseline `openai:gpt-4.1` model, so `OPENAI_API_KEY` must be set.

The command prints one JSON object on standard output:

```json
{"report_id": "<sha256 of the report text>",
 "metrics": [{"metric": "relevance_score", "status": "scored", "score": 0.8, "reason": "..."}]}
```

`report_id` names exactly the report that was scored. Each metric is either
`scored`, with a score between 0 and 1, or `not_evaluable`, with `score: null`
and a `reason`: a judge rating outside 1-5, a groundedness answer with no claim,
or a missing input (the reference answer for `correctness_score`, the research
brief for `completeness_score`, the evidence for `groundedness_score`). A
`not_evaluable` metric never stops the others, and scores are never clamped or
defaulted to zero.

Exit codes: `0` when the report was scored, `2` when the question or the report
is blank or cannot be read (no judge call is made in that case). The same
functions back the LangSmith evaluators in `test/evaluators.py`, so an experiment
and a single scored report use one set of rules.


#### Results 

| Name | Commit | Summarization | Research | Compression | Total Cost | Total Tokens | RACE Score | Experiment |
|------|--------|---------------|----------|-------------|------------|--------------|------------|------------|
| GPT-5 | [ca3951d](https://github.com/langchain-ai/open_deep_research/pull/168/commits) | openai:gpt-4.1-mini | openai:gpt-5 | openai:gpt-4.1 |  | 204,640,896 | 0.4943 | [Link](https://smith.langchain.com/o/ebbaf2eb-769b-4505-aca2-d11de10372a4/datasets/6e4766ca-613c-4bda-8bde-f64f0422bbf3/compare?selectedSessions=4d5941c8-69ce-4f3d-8b3e-e3c99dfbd4cc&baseline=undefined) |
| Defaults | [6532a41](https://github.com/langchain-ai/open_deep_research/commit/6532a4176a93cc9bb2102b3d825dcefa560c85d9) | openai:gpt-4.1-mini | openai:gpt-4.1 | openai:gpt-4.1 | $45.98 | 58,015,332 | 0.4309 | [Link](https://smith.langchain.com/o/ebbaf2eb-769b-4505-aca2-d11de10372a4/datasets/6e4766ca-6[…]ons=cf4355d7-6347-47e2-a774-484f290e79bc&baseline=undefined) |
| Claude Sonnet 4 | [f877ea9](https://github.com/langchain-ai/open_deep_research/pull/163/commits/f877ea93641680879c420ea991e998b47aab9bcc) | openai:gpt-4.1-mini | anthropic:claude-sonnet-4-20250514 | openai:gpt-4.1 | $187.09 | 138,917,050 | 0.4401 | [Link](https://smith.langchain.com/o/ebbaf2eb-769b-4505-aca2-d11de10372a4/datasets/6e4766ca-6[…]ons=04f6002d-6080-4759-bcf5-9a52e57449ea&baseline=undefined) |
| Deep Research Bench Submission | [c0a160b](https://github.com/langchain-ai/open_deep_research/commit/c0a160b57a9b5ecd4b8217c3811a14d8eff97f72) | openai:gpt-4.1-nano | openai:gpt-4.1 | openai:gpt-4.1 | $87.83 | 207,005,549 | 0.4344 | [Link](https://smith.langchain.com/o/ebbaf2eb-769b-4505-aca2-d11de10372a4/datasets/6e4766ca-6[…]ons=e6647f74-ad2f-4cb9-887e-acb38b5f73c0&baseline=undefined) |

### 🚀 Deployments and Usage

#### LangGraph Studio

Follow the [quickstart](#-quickstart) to start LangGraph server locally and test the agent out on LangGraph Studio.

#### Hosted deployment
 
You can easily deploy to [LangGraph Platform](https://langchain-ai.github.io/langgraph/concepts/#deployment-options). 

#### Open Agent Platform

Open Agent Platform (OAP) is a UI from which non-technical users can build and configure their own agents. OAP is great for allowing users to configure the Deep Researcher with different MCP tools and search APIs that are best suited to their needs and the problems that they want to solve.

We've deployed Open Deep Research to our public demo instance of OAP. All you need to do is add your API Keys, and you can test out the Deep Researcher for yourself! Try it out [here](https://oap.langchain.com)

You can also deploy your own instance of OAP, and make your own custom agents (like Deep Researcher) available on it to your users.
1. [Deploy Open Agent Platform](https://docs.oap.langchain.com/quickstart)
2. [Add Deep Researcher to OAP](https://docs.oap.langchain.com/setup/agents)

### Legacy Implementations 🏛️

The upstream `src/legacy/` implementations (`graph.py`, `multi_agent.py`) were removed from this fork in commit `a4d557a`. See the [upstream repository](https://github.com/langchain-ai/open_deep_research) for them.
