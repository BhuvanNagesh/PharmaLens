"""Agent 4: produce prioritized corrective actions for identified gaps."""

from __future__ import annotations

import json
import logging
from typing import Any, Mapping

from langchain_core.prompts import ChatPromptTemplate

from app.agents.llm_config import LLMInvocationError, invoke_structured
from app.agents.schemas import CorrectiveActionOutput


logger = logging.getLogger(__name__)

_ACTION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a pharmaceutical quality corrective-action recommender. "
            "For every identified gap, formulate a specific, auditable remediation action. "
            "Use immediate for critical product-quality or sterility risks, short_term for "
            "major mandatory-control omissions, and long_term for minor wording or formatting "
            "improvements. Do not recommend actions unrelated to the supplied gaps. "
            "Include a concise regulatory reference when one is present in the gap.",
        ),
        (
            "human",
            "Regulatory template sections:\n{template_sections}\n\n"
            "Identified compliance gaps:\n{gaps}",
        ),
    ]
)


def corrective_action_recommender_node(state: Mapping[str, Any]) -> dict[str, object]:
    """Populate ``corrective_actions`` and ``summary`` from structured gap findings."""
    if state.get("error"):
        return {"error": str(state["error"])}

    gaps = state.get("gaps", [])
    if not gaps:
        return {
            "corrective_actions": [],
            "summary": "No compliance gaps were identified by the gap analyzer.",
        }

    try:
        result = invoke_structured(
            _ACTION_PROMPT,
            CorrectiveActionOutput,
            {
                "template_sections": json.dumps(
                    state.get("template_sections", []),
                    ensure_ascii=False,
                    default=str,
                ),
                "gaps": json.dumps(gaps, ensure_ascii=False, default=str),
            },
        )
    except LLMInvocationError:
        logger.exception("Corrective action recommender agent failed.")
        return {
            "error": "Corrective action recommender agent failed to produce structured output."
        }

    return {
        "corrective_actions": [action.model_dump() for action in result.actions],
        "summary": result.summary,
    }
