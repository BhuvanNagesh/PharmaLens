"""Phase 3 compliance graph state and sequential LangGraph orchestration."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from typing import Any, TypedDict, cast

from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph

from app.agents.corrective_action_agent import (
    corrective_action_recommender_node as run_corrective_action_agent,
)
from app.agents.document_parser_agent import document_parser_node as run_document_parser_agent
from app.agents.gap_analyzer_agent import gap_analyzer_node as run_gap_analyzer_agent
from app.agents.regulatory_mapper_agent import regulatory_mapper_node as run_regulatory_mapper_agent
from app.services.scoring import (
    ComplianceScoringError,
    calculate_score_breakdown,
)


class ComplianceState(TypedDict):
    """State passed between the four compliance-analysis stages."""

    document_id: str
    template_id: str
    document_text: str
    template_sections: list[dict]
    parsed_sections: list[dict]
    section_mappings: list[dict]
    gaps: list[dict]
    corrective_actions: list[dict]
    compliance_score: float
    summary: str
    error: str | None


_STRING_FIELDS = ("document_id", "template_id", "document_text", "summary")
_LIST_FIELDS = (
    "template_sections",
    "parsed_sections",
    "section_mappings",
    "gaps",
    "corrective_actions",
)


def create_initial_state(
    document_id: str,
    template_id: str,
    document_text: str,
    template_sections: list[dict],
) -> ComplianceState:
    """Create a fully initialized state for a new compliance analysis."""
    return {
        "document_id": document_id,
        "template_id": template_id,
        "document_text": document_text,
        "template_sections": template_sections,
        "parsed_sections": [],
        "section_mappings": [],
        "gaps": [],
        "corrective_actions": [],
        "compliance_score": 0.0,
        "summary": "",
        "error": None,
    }


def _with_validation_error(state: dict[str, object], message: str) -> None:
    """Record the first state error without hiding an earlier pipeline failure."""
    if state.get("error") is None:
        state["error"] = message


def _validate_state(state: ComplianceState) -> ComplianceState:
    """Validate the shared state shape while preserving every pipeline value."""
    state_copy: dict[str, object] = dict(state)
    for field_name in _STRING_FIELDS:
        field_value = state_copy.get(field_name)
        if not isinstance(field_value, str):
            _with_validation_error(
                state_copy,
                f"Compliance state field '{field_name}' must be text.",
            )
    for field_name in _LIST_FIELDS:
        if not isinstance(state_copy.get(field_name), list):
            _with_validation_error(
                state_copy,
                f"Compliance state field '{field_name}' must be a list.",
            )
    score = state_copy.get("compliance_score")
    if not isinstance(score, (int, float)) or isinstance(score, bool):
        _with_validation_error(
            state_copy,
            "Compliance state field 'compliance_score' must be numeric.",
        )
    else:
        state_copy["compliance_score"] = float(score)
    error = state_copy.get("error")
    if error is not None and not isinstance(error, str):
        _with_validation_error(state_copy, "Compliance state field 'error' must be text or null.")
    return cast(ComplianceState, state_copy)


def _run_agent_node(
    state: ComplianceState,
    agent: Callable[[Mapping[str, Any]], dict[str, object]],
) -> ComplianceState:
    """Validate state, run one agent, and merge its partial state update."""
    validated_state = _validate_state(state)
    if validated_state.get("error"):
        return validated_state
    updated_state: dict[str, object] = dict(validated_state)
    updated_state.update(agent(validated_state))
    return _validate_state(cast(ComplianceState, updated_state))


def document_parser_node(state: ComplianceState) -> ComplianceState:
    """Run Agent 1 and merge its parsed sections into graph state."""
    return _run_agent_node(state, run_document_parser_agent)


def regulatory_mapper_node(state: ComplianceState) -> ComplianceState:
    """Run Agent 2 and merge its section mappings into graph state."""
    return _run_agent_node(state, run_regulatory_mapper_agent)


def gap_analyzer_node(state: ComplianceState) -> ComplianceState:
    """Run Agent 3 and merge its classified gaps into graph state."""
    return _run_agent_node(state, run_gap_analyzer_agent)


def corrective_action_recommender_node(state: ComplianceState) -> ComplianceState:
    """Run Agent 4 and merge its recommendations into graph state."""
    return _run_agent_node(state, run_corrective_action_agent)


def compliance_score_node(state: ComplianceState) -> ComplianceState:
    """Calculate and store the deterministic weighted compliance score."""
    validated_state = _validate_state(state)
    if validated_state.get("error"):
        return validated_state
    try:
        score_breakdown = calculate_score_breakdown(validated_state["gaps"])
    except ComplianceScoringError as error:
        updated_state = dict(validated_state)
        updated_state["error"] = str(error)
        return _validate_state(cast(ComplianceState, updated_state))

    updated_state = dict(validated_state)
    updated_state["compliance_score"] = score_breakdown.score
    return _validate_state(cast(ComplianceState, updated_state))


def build_compliance_graph() -> CompiledStateGraph:
    """Compile the sequential compliance graph from START to END."""
    graph = StateGraph(ComplianceState)
    graph.add_node("document_parser", document_parser_node)
    graph.add_node("regulatory_mapper", regulatory_mapper_node)
    graph.add_node("gap_analyzer", gap_analyzer_node)
    graph.add_node("corrective_action_recommender", corrective_action_recommender_node)
    graph.add_node("score_compliance", compliance_score_node)
    graph.add_edge(START, "document_parser")
    graph.add_edge("document_parser", "regulatory_mapper")
    graph.add_edge("regulatory_mapper", "gap_analyzer")
    graph.add_edge("gap_analyzer", "corrective_action_recommender")
    graph.add_edge("corrective_action_recommender", "score_compliance")
    graph.add_edge("score_compliance", END)
    return graph.compile()


compliance_graph = build_compliance_graph()
