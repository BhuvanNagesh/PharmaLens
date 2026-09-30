"""Agent 3: identify and classify regulatory compliance gaps."""

from __future__ import annotations

import json
import logging
from typing import Any, Mapping

from langchain_core.prompts import ChatPromptTemplate

from app.agents.llm_config import LLMInvocationError, invoke_structured
from app.agents.schemas import GapAnalysisOutput


logger = logging.getLogger(__name__)

_GAP_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a pharmaceutical compliance gap analyzer and risk classifier. "
            "Review each regulatory mapping against the extracted document content. "
            "Detect missing requirements, incomplete procedures, objective-criteria omissions, "
            "ambiguous wording, and direct non-compliance. "
            "Use critical for a direct regulatory violation that could risk product quality, "
            "major for a mandatory omission or missing quality-unit control, and minor for a "
            "limited ambiguity or documentation shortfall. "
            "Use only missing, incomplete, or non_compliant as gap_type. "
            "Quote a concise supporting excerpt when one exists and never invent an excerpt.",
        ),
        (
            "human",
            "Regulatory template sections:\n{template_sections}\n\n"
            "Extracted document sections:\n{parsed_sections}\n\n"
            "Section mappings:\n{section_mappings}",
        ),
    ]
)


def gap_analyzer_node(state: Mapping[str, Any]) -> dict[str, object]:
    """Populate ``gaps`` with severity-classified structured findings."""
    if state.get("error"):
        return {"error": str(state["error"])}

    try:
        result = invoke_structured(
            _GAP_PROMPT,
            GapAnalysisOutput,
            {
                "template_sections": json.dumps(
                    state.get("template_sections", []),
                    ensure_ascii=False,
                    default=str,
                ),
                "parsed_sections": json.dumps(
                    state.get("parsed_sections", []),
                    ensure_ascii=False,
                    default=str,
                ),
                "section_mappings": json.dumps(
                    state.get("section_mappings", []),
                    ensure_ascii=False,
                    default=str,
                ),
            },
        )
    except LLMInvocationError:
        logger.exception("Gap analyzer agent failed.")
        return {"error": "Gap analyzer agent failed to produce structured output."}

    return {"gaps": [gap.model_dump() for gap in result.gaps]}
