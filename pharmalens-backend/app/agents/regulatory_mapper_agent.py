"""Agent 2: map extracted document sections to regulatory requirements."""

from __future__ import annotations

import json
import logging
from typing import Any, Mapping

from langchain_core.prompts import ChatPromptTemplate

from app.agents.llm_config import LLMInvocationError, invoke_structured
from app.agents.schemas import RegulatoryMappingOutput


logger = logging.getLogger(__name__)

_MAPPER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a pharmaceutical regulatory framework mapper. "
            "Map every required template section to the best matching extracted document "
            "section. Use null when no section covers the requirement. "
            "Assess confidence as high, medium, low, or none. "
            "Do not treat similar wording as sufficient when the required content is absent. "
            "Return one mapping for every template section in its supplied order.",
        ),
        (
            "human",
            "Required regulatory template sections:\n{template_sections}\n\n"
            "Extracted document sections:\n{parsed_sections}",
        ),
    ]
)


def regulatory_mapper_node(state: Mapping[str, Any]) -> dict[str, object]:
    """Populate ``section_mappings`` by comparing template and parsed sections."""
    if state.get("error"):
        return {"error": str(state["error"])}

    template_sections = state.get("template_sections", [])
    parsed_sections = state.get("parsed_sections", [])
    if not template_sections:
        return {"section_mappings": []}

    try:
        result = invoke_structured(
            _MAPPER_PROMPT,
            RegulatoryMappingOutput,
            {
                "template_sections": json.dumps(
                    template_sections,
                    ensure_ascii=False,
                    default=str,
                ),
                "parsed_sections": json.dumps(
                    parsed_sections,
                    ensure_ascii=False,
                    default=str,
                ),
            },
        )
    except LLMInvocationError:
        logger.exception("Regulatory mapper agent failed.")
        return {"error": "Regulatory mapper agent failed to produce structured output."}

    return {"section_mappings": [mapping.model_dump() for mapping in result.mappings]}
