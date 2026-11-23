"""Build task specifications and task results from the model's output.

REQ-001, ADR-001 (INV-006, POL-006 to POL-009). Every decision here is made by
deterministic code: the model proposes a delegation and a findings block, and
this module decides whether they satisfy the task contract, which findings count
and what the task status is. No function in this module calls a model.

The functions are called from the existing graph nodes: ``supervisor_tools``
(``build_task_specs``, ``render_task_brief``, ``render_result_message``,
``render_notes``), ``researcher_tools`` (``extract_urls``) and
``compress_research`` (``build_task_result``).
"""

import json
import re
from typing import Any, Mapping, Sequence

from langchain_core.messages import ToolMessage

from open_deep_research.configuration import Configuration
from open_deep_research.state import (
    Finding,
    Source,
    TaskResult,
    TaskSpec,
    normalize_question,
)

FINDINGS_OPEN = "<task_findings>"
FINDINGS_CLOSE = "</task_findings>"
SOURCES_HEADING = "### Sources"
DELEGATION_TOOL_NAME = "ConductResearch"
THINK_TOOL_NAME = "think_tool"
BUDGET_TOOL_MESSAGE = (
    "Tool-call budget used up for this research task: the call was not run."
)
# Prefix ``execute_tool_safely`` puts in front of a failed tool call.
FAILED_TOOL_PREFIX = "Error executing tool:"
MAX_REQUIRED_QUESTIONS = 5

_URL_PATTERN = re.compile(r"https?://[^\s<>\"'()\[\]]+")
_SOURCE_ENTRY_PATTERN = re.compile(r"^\s*\[(\d+)\]\s*(.*?)\s*:\s*(\S+)\s*$")


def _text_of(message: Any) -> str:
    """Return a message's text, joining the text parts of block content (ADR-001 §3.2)."""
    content = getattr(message, "content", message)
    if isinstance(content, str):
        return content
    parts: list[str] = []
    for block in content or []:
        if isinstance(block, str):
            parts.append(block)
        elif isinstance(block, Mapping) and block.get("type") == "text":
            parts.append(str(block.get("text", "")))
    return "\n".join(parts)


def _tool_call_id(tool_call: Any) -> str:
    """Return a tool call's id, accepting the dict and the attribute shape."""
    if isinstance(tool_call, Mapping):
        return str(tool_call.get("id", ""))
    return str(getattr(tool_call, "id", ""))


def _tool_call_args(tool_call: Any) -> Mapping[str, Any]:
    """Return a tool call's arguments as a mapping."""
    args = (
        tool_call.get("args")
        if isinstance(tool_call, Mapping)
        else getattr(tool_call, "args", None)
    )
    return args if isinstance(args, Mapping) else {}


def _delegation_calls(calls: Sequence[Any]) -> list[Any]:
    """Keep only the calls that delegate research."""
    return [
        call
        for call in calls
        if (
            call.get("name")
            if isinstance(call, Mapping)
            else getattr(call, "name", None)
        )
        == DELEGATION_TOOL_NAME
    ]


def _clean_questions(raw: Any) -> list[str] | None:
    """Return the de-duplicated required questions, or ``None`` when the value is invalid.

    ADR-001 §3.1: duplicates are removed after ``normalize_question`` and the
    first spelling is kept; a non-string question or more than five distinct
    questions makes the delegation invalid.
    """
    if raw is None:
        return []
    if not isinstance(raw, list | tuple):
        return None
    questions: list[str] = []
    seen: set[str] = set()
    for question in raw:
        if not isinstance(question, str):
            return None
        if not question.strip():
            continue
        key = normalize_question(question)
        if key in seen:
            continue
        seen.add(key)
        questions.append(question.strip())
    if len(questions) > MAX_REQUIRED_QUESTIONS:
        return None
    return questions


def build_task_specs(
    calls: Sequence[Any],
    first_index: int,
    config: Configuration,
) -> tuple[list[TaskSpec], list[ToolMessage]]:
    """Turn the delegation calls of one supervisor turn into task specifications.

    REQ-001, ADR-001 §3.1, POL-006. Task ids are ``T<first_index>``, ``T<first_index + 1>``,
    ... in delegation order. An invalid delegation (blank topic, non-string
    question, more than five distinct questions) still gets a spec, so that the
    delegation is not dropped, but the spec has no required questions, adds
    nothing to coverage and is never run; its error ``ToolMessage`` is returned
    in the second list, in delegation order.
    """
    specs: list[TaskSpec] = []
    errors: list[ToolMessage] = []
    for offset, call in enumerate(_delegation_calls(calls)):
        task_id = f"T{first_index + offset}"
        call_id = _tool_call_id(call)
        args = _tool_call_args(call)
        topic = args.get("research_topic")
        scope = args.get("scope", "")
        questions = _clean_questions(args.get("must_answer"))
        problem = None
        if not isinstance(topic, str) or not topic.strip():
            problem = "the delegation has a blank research_topic"
        elif questions is None:
            problem = (
                "must_answer must be a list of strings with at most "
                f"{MAX_REQUIRED_QUESTIONS} distinct questions"
            )
        elif not questions:
            questions = [" ".join(topic.split())]
        elif len(questions) == 1 and normalize_question(
            questions[0]
        ) == normalize_question(topic):
            # ADR-001 §3.1: the topic itself is the default question; a single
            # question equal to the topic is the same question and gets the
            # topic's spelling.
            questions = [" ".join(topic.split())]

        if problem is not None:
            spec = TaskSpec.model_construct(
                task_id=task_id,
                research_topic=topic if isinstance(topic, str) else "",
                scope=scope if isinstance(scope, str) else "",
                must_answer=[],
                max_tool_calls=config.max_react_tool_calls,
            )
            errors.append(
                ToolMessage(
                    content=f"Rejected delegation: {problem}. The task was not run.",
                    name=DELEGATION_TOOL_NAME,
                    tool_call_id=call_id,
                )
            )
            specs.append(spec)
            continue

        specs.append(
            TaskSpec(
                task_id=task_id,
                research_topic=topic,
                scope=scope if isinstance(scope, str) else "",
                must_answer=questions,
                max_tool_calls=config.max_react_tool_calls,
            )
        )
    return specs, errors


def render_task_brief(spec: TaskSpec) -> str:
    """Render the first message a researcher receives for ``spec`` (ADR-001 §3.1)."""
    lines = [
        f"Research task {spec.task_id}",
        "",
        "Topic:",
        spec.research_topic,
        "",
        "Scope:",
        spec.scope if spec.scope.strip() else "(not specified)",
        "",
        "Required questions (every one must be answered with sourced findings):",
    ]
    lines.extend(
        f"{index}. {question}" for index, question in enumerate(spec.must_answer, 1)
    )
    lines.extend(
        [
            "",
            f"Tool-call budget: at most {spec.max_tool_calls} tool calls.",
            "",
            "Report each finding in the task findings block described in your "
            "compression instructions, and cite only URLs your own tool calls "
            "returned.",
        ]
    )
    return "\n".join(lines)


def extract_urls(tool_messages: Sequence[Any]) -> list[str]:
    """Return every http(s) URL a successful tool message returned, in order of first use.

    REQ-001, ADR-001 §3.2: reflection messages, budget messages and failed calls
    are skipped, so a URL that only appears in error text is never "retrieved".
    URLs are compared as exact strings.
    """
    urls: list[str] = []
    seen: set[str] = set()
    for message in tool_messages or []:
        name = getattr(message, "name", None)
        if name == THINK_TOOL_NAME:
            continue
        text = _text_of(message)
        if text.startswith(BUDGET_TOOL_MESSAGE) or text.startswith(FAILED_TOOL_PREFIX):
            continue
        for url in _URL_PATTERN.findall(text):
            url = url.rstrip(".,;:")
            if url not in seen:
                seen.add(url)
                urls.append(url)
    return urls


def _single_findings_block(text: str) -> str | None:
    """Return the body of the one findings block in ``text``, or ``None``.

    ADR-001 §3.3 rule 1: exactly one complete block is allowed.
    """
    if text.count(FINDINGS_OPEN) != 1 or text.count(FINDINGS_CLOSE) != 1:
        return None
    start = text.index(FINDINGS_OPEN) + len(FINDINGS_OPEN)
    end = text.index(FINDINGS_CLOSE)
    if end < start:
        return None
    return text[start:end]


def parse_sources(text: str) -> dict[int, Source]:
    """Read the ``### Sources`` list of a findings block text into ``{n: Source}``."""
    sources: dict[int, Source] = {}
    if SOURCES_HEADING not in text:
        return sources
    listing = text.split(SOURCES_HEADING, 1)[1]
    for line in listing.splitlines():
        match = _SOURCE_ENTRY_PATTERN.match(line)
        if not match:
            continue
        number = int(match.group(1))
        sources.setdefault(number, Source(title=match.group(2), url=match.group(3)))
    return sources


def _parse_findings(text: str, allowed: set[str]) -> list[dict[str, Any]] | None:
    """Parse the findings block, or return ``None`` when it breaks the contract."""
    body = _single_findings_block(text)
    if body is None:
        return None
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return None
    if not isinstance(payload, dict) or not isinstance(payload.get("findings"), list):
        return None
    parsed: list[dict[str, Any]] = []
    for item in payload["findings"]:
        if not isinstance(item, dict):
            return None
        claim = item.get("claim")
        answers = item.get("answers")
        numbers = item.get("sources")
        if not isinstance(claim, str) or not claim.strip():
            return None
        if not isinstance(answers, list) or not answers:
            return None
        if not isinstance(numbers, list):
            return None
        # ADR-001 §3.3 step 2: a finding without a source does not count, which
        # is decided after parsing so that the others still can.
        if any(not isinstance(n, int) or isinstance(n, bool) for n in numbers):
            return None
        keys = []
        for question in answers:
            if (
                not isinstance(question, str)
                or normalize_question(question) not in allowed
            ):
                return None
            keys.append(normalize_question(question))
        parsed.append({"claim": claim, "answers": keys, "sources": numbers})
    return parsed


def build_task_result(
    spec: TaskSpec,
    text: str,
    retrieved_urls: Sequence[str],
    tool_calls: int,
) -> TaskResult:
    """Derive the task result from the compression text and the retrieved URLs.

    REQ-001, ADR-001 §3.3, INV-006, POL-007, POL-008. The model never decides the
    status: a finding counts only when it cites at least one source and every one
    of its URLs was returned by a tool call of this task; the status follows from
    the counted findings.
    """

    def invalid(reason: str) -> TaskResult:
        return TaskResult.failed(spec, "invalid_result", reason, tool_calls=tool_calls)

    if not isinstance(text, str):
        return invalid("the compression output is not text")

    allowed = {normalize_question(question) for question in spec.must_answer}
    parsed = _parse_findings(text, allowed)
    if parsed is None:
        return invalid(
            "the compression text does not hold exactly one valid task findings block"
        )
    source_list = parse_sources(text)
    retrieved = set(retrieved_urls or [])

    counted: list[Finding] = []
    answered: set[str] = set()
    for item in parsed:
        if not item["sources"]:
            # ADR-001 §3.3 step 2: a finding without a source does not count.
            continue
        try:
            sources = [source_list[number] for number in item["sources"]]
        except KeyError:
            return invalid(
                "a finding cites a source number that is not in the Sources list"
            )
        if not all(source.url in retrieved for source in sources):
            continue
        display_answers = [
            question
            for question in spec.must_answer
            if normalize_question(question) in item["answers"]
        ]
        counted.append(
            Finding(claim=item["claim"], answers=display_answers, sources=sources)
        )
        answered.update(item["answers"])

    required = [normalize_question(question) for question in spec.must_answer]
    missing = [
        question
        for question, key in zip(spec.must_answer, required)
        if key not in answered
    ]
    body = _single_findings_block(text) or ""
    summary = (
        text.replace(body, "").replace(FINDINGS_OPEN, "").replace(FINDINGS_CLOSE, "")
    )
    if SOURCES_HEADING in summary:
        summary = summary.split(SOURCES_HEADING, 1)[0]
    summary = "\n".join(line for line in summary.splitlines() if line.strip())

    if not missing:
        status = "complete"
        category = None
        reason = ""
    elif answered:
        status = "partial"
        category = "unanswered"
        reason = "Unanswered questions: " + "; ".join(missing)
    else:
        return TaskResult.failed(
            spec,
            "unanswered",
            "No sourced finding answers any required question"
            + (f": {'; '.join(missing)}" if missing else ""),
            tool_calls=tool_calls,
        )

    return TaskResult(
        task_id=spec.task_id,
        status=status,
        must_answer=list(spec.must_answer),
        findings=counted,
        summary=summary,
        tool_calls=tool_calls,
        failure_category=category,
        reason=reason,
    )


def render_result_message(result: TaskResult) -> str:
    """Render the ``ToolMessage`` the supervisor receives for one task result."""
    lines = [f"Task {result.task_id}: {result.status}"]
    if result.reason:
        lines.append(f"Reason: {result.reason}")
    if result.must_answer:
        lines.append("Required questions: " + "; ".join(result.must_answer))
    if result.summary:
        lines.extend(["", result.summary])
    return "\n".join(lines)


def render_notes(results: Sequence[TaskResult]) -> list[str]:
    """Render ``notes`` from the counted findings of complete and partial tasks only.

    REQ-002 C-007, ADR-001 §3.4 step 7, INV-002: neither the free-text summary nor
    any failure text enters ``notes``. Source numbers restart at 1 in each entry.
    """
    notes: list[str] = []
    for result in results or []:
        if getattr(result, "status", None) not in ("complete", "partial"):
            continue
        numbers: dict[str, int] = {}
        entries: list[Source] = []
        lines = [f"Task {result.task_id}:"]
        for finding in getattr(result, "findings", None) or []:
            marks = []
            for source in finding.sources:
                if source.url not in numbers:
                    entries.append(source)
                    numbers[source.url] = len(entries)
                marks.append(f"[{numbers[source.url]}]")
            lines.append(f"- {finding.claim} {''.join(marks)}")
        if not entries:
            continue
        lines.append(SOURCES_HEADING)
        for number, source in enumerate(entries, 1):
            lines.append(f"[{number}] {source.title}: {source.url}")
        notes.append("\n".join(lines))
    return notes
