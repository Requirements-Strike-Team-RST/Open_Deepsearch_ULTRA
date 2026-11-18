#!/usr/bin/env python3
"""Bounded SA experiment: baseline functions with fakes; optional CityU-only probe.

This is external design evidence, not a product acceptance suite. No repository
module is imported or changed, no research tool is executed, and no Claude API
or provider discovery is used. Credentials are read from the inherited runtime
environment only and never written to artifacts.
"""

import argparse
import ast
import asyncio
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
from types import SimpleNamespace
from typing import Literal
import urllib.error
import urllib.parse
import urllib.request


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "sa-centay-2026-11-14/src/open_deep_research/deep_researcher.py"
MODEL = "CS5351/DeepSeek-V4-Flash"


class Message:
    def __init__(self, content="", **kwargs):
        self.content = content
        self.__dict__.update(kwargs)


class Command:
    @classmethod
    def __class_getitem__(cls, item):
        return cls

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class FakeModel:
    def __init__(self, content, finish_reason):
        self.calls = 0
        self.response = Message(content, response_metadata={"finish_reason": finish_reason}, tool_calls=[])

    def with_config(self, *args, **kwargs):
        return self

    async def ainvoke(self, *args, **kwargs):
        self.calls += 1
        return self.response


async def offline():
    source = SOURCE.read_bytes()
    tree = ast.parse(source, filename=str(SOURCE))
    names = {"compress_research", "final_report_generation", "supervisor_tools"}
    functions = [n for n in tree.body if isinstance(n, ast.AsyncFunctionDef) and n.name in names]
    assert {n.name for n in functions} == names
    cfg = SimpleNamespace(compression_model="fake", compression_model_max_tokens=32,
                          research_model="fake", final_report_model="fake",
                          final_report_model_max_tokens=32, max_researcher_iterations=3,
                          max_concurrent_research_units=1)
    namespace = dict(
        ResearcherState=dict, AgentState=dict, SupervisorState=dict, RunnableConfig=dict,
        Command=Command, Literal=Literal, END="__end__",
        Configuration=SimpleNamespace(from_runnable_config=lambda config: cfg),
        get_api_key_for_model=lambda *args: "unused-no-network",
        get_today_str=lambda: "2026-11-15",
        compress_research_simple_human_message="Summarize.",
        compress_research_system_prompt="Summarize at {date}.",
        final_report_generation_prompt="{research_brief} {messages} {findings} {date}",
        HumanMessage=Message, SystemMessage=Message, AIMessage=Message, ToolMessage=Message,
        asyncio=asyncio,
        filter_messages=lambda msgs, **kwargs: msgs,
        get_buffer_string=lambda msgs: " ".join(m.content for m in msgs),
        get_notes_from_tool_calls=lambda msgs: [],
        is_token_limit_exceeded=lambda *args: False,
    )
    exec(compile(ast.Module(body=functions, type_ignores=[]), str(SOURCE), "exec"), namespace)
    rows = []
    for name in ("compress_research", "final_report_generation"):
        sidecar = {"schema_version": 1, "findings": [{"claim": "demo", "answers": ["Q1"], "source_numbers": [1]}]}
        content = '<task_findings_v1>\n```json\n' + json.dumps(sidecar) + '\n```\n</task_findings_v1>\n### Sources\n[1] Demo: https://example.org' if name == "compress_research" else "# Report\nA valid-looking report.\n"
        if name == "compress_research":
            assert json.loads(content.split('```json\n')[1].split('\n```')[0]) == sidecar
        results = {}
        for reason in ("stop", "length"):
            model = FakeModel(content, reason)
            namespace["configurable_model"] = model
            state = {"researcher_messages": [Message("evidence")]} if name == "compress_research" else {"notes": ["verified finding"], "messages": [], "research_brief": "demo"}
            result = await namespace[name](state, {})
            text_key = "compressed_research" if name == "compress_research" else "final_report"
            results[reason] = result[text_key]
            preserved_in_message = any(getattr(m, "response_metadata", {}).get("finish_reason") == reason for m in result.get("messages", []))
            rows.append({"function": name, "finish_reason_in": reason,
                         "model_calls": model.calls, "returned_text": result[text_key],
                         "metadata_in_returned_message": preserved_in_message,
                         "finish_reason_in_result_fields": "finish_reason" in result,
                         "observation": "returned without truncation rejection"})
        assert results["stop"] == results["length"]
    for reason in ("stop", "length"):
        msg = Message("", response_metadata={"finish_reason": reason}, tool_calls=[])
        result = await namespace["supervisor_tools"]({"supervisor_messages": [msg], "research_iterations": 1}, {})
        assert result.goto == "__end__"
        rows.append({"function": "supervisor_tools", "finish_reason_in": reason,
                     "tool_calls": [], "goto": result.goto,
                     "observation": "no-tool exit does not distinguish length from stop"})
    class FakeChild:
        def __init__(self):
            self.calls = 0

        async def ainvoke(self, *args, **kwargs):
            self.calls += 1
            return {"compressed_research": "synthetic child summary", "raw_notes": []}

    for reason in ("stop", "length"):
        child = FakeChild()
        namespace["researcher_subgraph"] = child
        msg = Message("", response_metadata={"finish_reason": reason},
                      tool_calls=[{"id": "synthetic-call", "name": "ConductResearch", "args": {"research_topic": "synthetic topic"}}])
        result = await namespace["supervisor_tools"]({"supervisor_messages": [msg], "research_iterations": 1}, {})
        assert child.calls == 1 and result.goto == "supervisor"
        rows.append({"function": "supervisor_tools", "finish_reason_in": reason,
                     "tool_calls": ["ConductResearch"], "fake_child_starts": child.calls,
                     "goto": result.goto, "observation": "well-shaped intent dispatched despite length marker; child mocked, no network"})
    result = {"kind": "offline source-function experiment", "at_utc": datetime.now(timezone.utc).isoformat(),
              "source": str(SOURCE), "source_sha256": hashlib.sha256(source).hexdigest(),
              "functions": {n.name: {"start": n.lineno, "end": n.end_lineno} for n in functions},
              "scope": "actual extracted function bodies with fake model/messages/config; not full graph or Proposed implementation",
              "verdict": "CONFIRMED baseline ignores finish_reason on these paths", "observations": rows}
    (ROOT / "truncation-offline-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"offline": result["verdict"], "cases": len(rows), "source_sha256": result["source_sha256"]}))


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


def live(tool_only=False):
    base = os.environ.get("CITYUCS_LLM_BASE_URL", "")
    key = os.environ.get("CITYUCS_LLM_API_KEY", "")
    endpoint = urllib.parse.urlparse(base)
    if endpoint.scheme != "https" or endpoint.hostname != "llm.cs.cityu.edu.hk" or endpoint.path.rstrip("/") != "/v1" or endpoint.username or endpoint.password or endpoint.query or endpoint.fragment:
        raise SystemExit("BLOCKED: exact approved CityU endpoint not available")
    if not key:
        raise SystemExit("BLOCKED: inherited CityU credential unavailable")
    url = base.rstrip("/") + "/chat/completions"
    probes = [
        ("forced-length", 32, "Write 200 numbered English sentences about counting. Start immediately with sentence 1 and keep writing; no preamble."),
        ("short-control", 256, "Reply with exactly the word OK and nothing else.")]
    if tool_only:
        probes = [("tool-control", 128, "Call metadata_probe with value OK. Do not write any other output.")]
    rows = []
    opener = urllib.request.build_opener(NoRedirect())
    for label, limit, prompt in probes:
        body = {"model": MODEL, "messages": [{"role": "user", "content": prompt}],
                "max_tokens": limit, "stream": False, "temperature": 0}
        if tool_only:
            body["tools"] = [{"type": "function", "function": {
                "name": "metadata_probe", "description": "Return a synthetic test value; never executed.",
                "parameters": {"type": "object", "properties": {"value": {"type": "string"}},
                               "required": ["value"], "additionalProperties": False}}}]
            body["tool_choice"] = {"type": "function", "function": {"name": "metadata_probe"}}
        req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                     headers={"Authorization": "Bearer " + key,
                                              "Content-Type": "application/json"}, method="POST")
        started = datetime.now(timezone.utc).isoformat()
        try:
            with opener.open(req, timeout=40) as response:
                raw = response.read(2_000_000)
            parsed = json.loads(raw)
            # Prompt and output are synthetic, but still prevent credential echoes.
            sanitized = json.dumps(parsed, ensure_ascii=False).replace(key, "<redacted>")
            raw_path = ROOT / ("gateway-" + label + ".response.json")
            raw_path.write_text(sanitized + "\n")
            choices = parsed.get("choices", [])
            first = choices[0] if choices else {}
            message = first.get("message", {})
            row = {"probe": label, "started_utc": started, "host": endpoint.hostname,
                   "requested_model": MODEL, "max_tokens": limit,
                   "returned_model": parsed.get("model"), "finish_reason": first.get("finish_reason"),
                   "choice_fields": sorted(first), "message_fields": sorted(message),
                   "content_chars": len(message.get("content") or ""),
                   "tool_intents_returned": len(message.get("tool_calls") or []),
                   "usage": parsed.get("usage"), "raw_file": raw_path.name, "verdict": "RESPONSE"}
        except urllib.error.HTTPError as error:
            row = {"probe": label, "started_utc": started, "host": endpoint.hostname,
                   "max_tokens": limit, "verdict": "HTTP_ERROR", "status": error.code}
        except Exception as error:
            row = {"probe": label, "started_utc": started, "host": endpoint.hostname,
                   "max_tokens": limit, "verdict": "ERROR", "exception_type": type(error).__name__}
        rows.append(row)
        print(json.dumps(row, ensure_ascii=False), flush=True)
    target = "truncation-gateway-tool-results.json" if tool_only else "truncation-gateway-results.json"
    (ROOT / target).write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--live-tools", action="store_true")
    args = parser.parse_args()
    ROOT.mkdir(parents=True, exist_ok=True)
    asyncio.run(offline())
    if args.live or args.live_tools:
        live(tool_only=args.live_tools)
