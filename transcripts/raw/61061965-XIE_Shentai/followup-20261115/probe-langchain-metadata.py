#!/usr/bin/env python3
"""Offline adapter experiment with locked langchain-openai and mocked HTTP only."""

import os

os.environ["LANGSMITH_TRACING"] = "false"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

import asyncio
import importlib.metadata
import json
from pathlib import Path
import socket

import httpx
from langchain_openai import ChatOpenAI


ROOT = Path(__file__).resolve().parent


def reject_network(*args, **kwargs):
    raise RuntimeError("Offline adapter probe forbids socket connections")


socket.socket.connect = reject_network
socket.socket.connect_ex = reject_network


async def main():
    rows = []
    labels = ["forced-length", "short-control"]
    if (ROOT / "gateway-tool-control.response.json").is_file():
        labels.append("tool-control")
    for label in labels:
        response = json.loads((ROOT / ("gateway-" + label + ".response.json")).read_text())
        requests = []

        def respond(request):
            assert request.url.host == "offline.invalid"
            requests.append({"host": request.url.host, "method": request.method})
            return httpx.Response(200, json=response)

        async with httpx.AsyncClient(transport=httpx.MockTransport(respond)) as client:
            model = ChatOpenAI(model="CS5351/DeepSeek-V4-Flash", api_key="unused-offline",
                               base_url="https://offline.invalid/v1", max_retries=0,
                               http_async_client=client)
            msg = await model.ainvoke("offline synthetic probe", config={"callbacks": []})
        expected = response["choices"][0]["finish_reason"]
        assert msg.response_metadata.get("finish_reason") == expected
        row = {"fixture": label, "api_finish_reason": expected,
               "message_finish_reason": msg.response_metadata.get("finish_reason"),
               "content_preserved": msg.content == (response["choices"][0]["message"].get("content") or ""),
               "parsed_tool_calls": [{"name": t["name"], "args": t["args"]} for t in msg.tool_calls],
               "usage_metadata": msg.usage_metadata,
               "mock_http_requests": requests, "real_socket_connections": 0}
        rows.append(row)
        print(json.dumps(row), flush=True)
    result = {"scope": "real pinned ChatOpenAI adapter; captured gateway JSON; HTTP mocked; no real model request",
              "versions": {name: importlib.metadata.version(name) for name in ("langchain-openai", "langchain-core", "openai")},
              "observations": rows, "verdict": "PASS finish_reason survives into AIMessage.response_metadata"}
    (ROOT / "truncation-langchain-results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    asyncio.run(main())
