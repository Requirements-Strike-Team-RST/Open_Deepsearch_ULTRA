"""Graph state definitions and data structures for the Deep Research agent."""

import operator
from typing import Annotated, Literal, Optional

from langchain_core.messages import MessageLikeRepresentation
from langgraph.graph import MessagesState
from pydantic import BaseModel, Field, model_validator
from typing_extensions import TypedDict


###################
# Structured Outputs
###################
class ConductResearch(BaseModel):
    """Call this tool to conduct research on a specific topic."""
    research_topic: str = Field(
        description="The topic to research. Should be a single topic, and should be described in high detail (at least a paragraph).",
    )

class ConductResearchTask(BaseModel):
    """Delegate research as a typed task: a topic, the questions it must answer and its scope.

    REQ-001, ADR-001 §3.1, INV-006. Bound by the supervisor only when
    ``Configuration.task_contract_enabled`` is on; its schema title stays
    ``ConductResearch`` so the model still sees a tool of that name.
    """
    research_topic: str = Field(
        description="The topic to research. Should be a single topic, and should be described in high detail (at least a paragraph).",
    )
    must_answer: list[str] = Field(
        default_factory=list,
        description="The questions this task must answer, one per entry. Each question must be answerable with sourced findings.",
    )
    scope: str = Field(
        default="",
        description="What is inside this task and what is outside it, so parallel tasks do not overlap.",
    )

    model_config = {"title": "ConductResearch"}

class ResearchComplete(BaseModel):
    """Call this tool to indicate that the research is complete."""

class Summary(BaseModel):
    """Research summary with key findings."""
    
    summary: str
    key_excerpts: str

class ClarifyWithUser(BaseModel):
    """Model for user clarification requests."""
    
    need_clarification: bool = Field(
        description="Whether the user needs to be asked a clarifying question.",
    )
    question: str = Field(
        description="A question to ask the user to clarify the report scope",
    )
    verification: str = Field(
        description="Verify message that we will start research after the user has provided the necessary information.",
    )

class ResearchQuestion(BaseModel):
    """Research question and brief for guiding research."""
    
    research_brief: str = Field(
        description="A research question that will be used to guide the research.",
    )


###################
# Task Contract
###################
# Shared contract types of REQ-001 (ADR-001 §5, INV-006). They live here so that
# every module can read them without importing another extension module
# (structural-constraints.md §5, §6).

TaskStatus = Literal["complete", "partial", "failed"]
ExitReason = Literal["covered", "budget_exhausted", "stalled", "failed"]
ResearchOutcome = Literal["complete", "partial", "failed"]
FailureCategory = Literal[
    "unanswered", "invalid_result", "runtime", "token_limit", "not_run"
]

_MAX_REQUIRED_QUESTIONS = 5


def normalize_question(text: str) -> str:
    """Return the comparison form of a question: whitespace collapsed, case folded.

    REQ-001, ADR-001 §3.1: two questions are the same when their normal forms are
    equal, so ``"  How   many "`` and ``"how many"`` match.
    """
    if not isinstance(text, str):
        raise TypeError("a question must be a string")
    return " ".join(text.split()).casefold()


class TaskSpec(BaseModel):
    """One delegated research task: id, topic, scope, required questions and budget.

    REQ-001, ADR-001 §3.1. A spec with a blank topic or without 1-5 questions
    (counted after ``normalize_question``) cannot be constructed.
    """

    task_id: str
    research_topic: str
    scope: str = ""
    must_answer: list[str] = Field(default_factory=list)
    max_tool_calls: int = Field(default=0, ge=1)

    @model_validator(mode="after")
    def _check_spec(self) -> "TaskSpec":
        if not self.research_topic.strip():
            raise ValueError("a task specification needs a non-blank research_topic")
        for question in self.must_answer:
            if not isinstance(question, str) or not question.strip():
                raise ValueError("every required question must be a non-blank string")
        distinct = {normalize_question(question) for question in self.must_answer}
        if not 1 <= len(distinct) <= _MAX_REQUIRED_QUESTIONS:
            raise ValueError(
                f"a task specification needs 1-{_MAX_REQUIRED_QUESTIONS} distinct "
                "required questions"
            )
        return self


class Source(BaseModel):
    """A URL cited by a finding, with the title the search tool returned."""

    title: str
    url: str


class Finding(BaseModel):
    """One claim, the questions it answers and at least one supporting source."""

    claim: str
    answers: list[str]
    sources: list[Source] = Field(min_length=1)


class TaskResult(BaseModel):
    """What a researcher returns for one task (REQ-001, ADR-001 §3.3, §5).

    ``complete`` carries findings and no failure category; ``partial`` and
    ``failed`` name a category and a reason; ``failed`` carries no findings.
    """

    task_id: str
    status: TaskStatus
    must_answer: list[str] = Field(default_factory=list)
    findings: list[Finding] = Field(default_factory=list)
    summary: str = ""
    tool_calls: int = 0
    failure_category: Optional[FailureCategory] = None
    reason: str = ""

    @classmethod
    def failed(
        cls,
        spec: TaskSpec,
        category: FailureCategory,
        reason: str,
        tool_calls: int = 0,
    ) -> "TaskResult":
        """Build a failed result for ``spec`` with no findings and no summary."""
        return cls(
            task_id=spec.task_id,
            status="failed",
            must_answer=list(spec.must_answer),
            findings=[],
            summary="",
            tool_calls=tool_calls,
            failure_category=category,
            reason=reason,
        )


def answered_questions(results) -> list[str]:
    """Return the distinct questions at least one counted finding answers, in first-seen order.

    REQ-003, ADR-001 §3.4: a question counts when any task result holds a counted
    finding for it, whichever task produced that finding. ``findings`` of a
    ``TaskResult`` hold counted findings only, each with at least one source;
    the task status and the model's text are never read.
    """
    answered: list[str] = []
    seen: set[str] = set()
    for result in results or []:
        for finding in getattr(result, "findings", None) or []:
            if not getattr(finding, "sources", None):
                continue
            for question in getattr(finding, "answers", None) or []:
                key = normalize_question(question)
                if key not in seen:
                    seen.add(key)
                    answered.append(question)
    return answered


def unanswered_questions(results) -> list[str]:
    """Return, in spec order, the required questions no counted finding answered.

    REQ-003, ADR-001 §5. A question answered by any task in ``results`` is
    answered for every task.
    """
    covered = {normalize_question(question) for question in answered_questions(results)}
    missing: list[str] = []
    seen: set[str] = set()
    for result in results or []:
        for question in getattr(result, "must_answer", None) or []:
            key = normalize_question(question)
            if key in covered or key in seen:
                continue
            seen.add(key)
            missing.append(question)
    return missing


###################
# State Definitions
###################

def override_reducer(current_value, new_value):
    """Reducer function that allows overriding values in state."""
    if isinstance(new_value, dict) and new_value.get("type") == "override":
        return new_value.get("value", new_value)
    else:
        return operator.add(current_value, new_value)
    
class AgentInputState(MessagesState):
    """InputState is only 'messages'."""

class AgentState(MessagesState):
    """Main agent state containing messages and research data."""
    
    supervisor_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    research_brief: Optional[str]
    raw_notes: Annotated[list[str], override_reducer] = []
    notes: Annotated[list[str], override_reducer] = []
    final_report: str
    # REQ-001/REQ-003 (orchestration), copied from the supervisor subgraph; REQ-004 (delivery).
    task_results: Annotated[list[TaskResult], override_reducer] = []
    exit_reason: Optional[ExitReason] = None
    exit_detail: str = ""
    research_outcome: Optional[ResearchOutcome] = None
    outcome_detail: str = ""
    failed_tasks: Annotated[list[TaskResult], override_reducer] = []

class SupervisorState(TypedDict):
    """State for the supervisor that manages research tasks."""
    
    supervisor_messages: Annotated[list[MessageLikeRepresentation], override_reducer]
    research_brief: str
    notes: Annotated[list[str], override_reducer] = []
    research_iterations: int = 0
    raw_notes: Annotated[list[str], override_reducer] = []
    task_results: Annotated[list[TaskResult], override_reducer] = []
    exit_reason: Optional[ExitReason] = None
    exit_detail: str = ""
    stalled_turns: int = 0

class ResearcherState(TypedDict):
    """State for individual researchers conducting research."""
    
    researcher_messages: Annotated[list[MessageLikeRepresentation], operator.add]
    tool_call_iterations: int = 0
    research_topic: str
    compressed_research: str
    raw_notes: Annotated[list[str], override_reducer] = []
    task_spec: Optional[TaskSpec] = None
    retrieved_urls: Annotated[list[str], operator.add] = []
    tool_calls_spent: int = 0

class ResearcherOutputState(BaseModel):
    """Output state from individual researchers."""
    
    compressed_research: str
    raw_notes: Annotated[list[str], override_reducer] = []
    task_result: Optional[TaskResult] = None