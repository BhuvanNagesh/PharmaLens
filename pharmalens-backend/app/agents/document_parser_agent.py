"""Agent 1: extract logical sections from normalized document text."""

from __future__ import annotations

import logging
from typing import Any, Mapping

from langchain_core.prompts import ChatPromptTemplate

from app.agents.llm_config import LLMInvocationError, invoke_structured
from app.agents.schemas import DocumentParserOutput


logger = logging.getLogger(__name__)
MAX_DOCUMENT_CONTEXT_CHARS = 100_000

_PARSER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a pharmaceutical quality-document section extractor. "
            "Split the supplied document into distinct logical sections in reading order. "
            "Preserve the source wording and do not invent requirements. "
            "Use meaningful titles such as Purpose, Scope, Responsibilities, Procedure, "
            "Deviation Handling, and Record Retention when the document supports them. "
            "Return an empty sections list when the document contains no usable text.",
        ),
        (
            "human",
            "Extract the logical sections from this document text:\n\n{document_text}",
        ),
    ]
)


def document_parser_node(state: Mapping[str, Any]) -> dict[str, object]:
    """Populate ``parsed_sections`` with structured sections from document text."""
    if state.get("error"):
        return {"error": str(state["error"])}

    document_text = str(state.get("document_text", ""))
    if not document_text.strip():
        return {"parsed_sections": []}

    try:
        result = invoke_structured(
            _PARSER_PROMPT,
            DocumentParserOutput,
            {"document_text": document_text[:MAX_DOCUMENT_CONTEXT_CHARS]},
        )
    except LLMInvocationError as error:
        logger.exception("Document parser agent failed.")
        return {"error": "Document parser agent failed to produce structured output."}

    return {"parsed_sections": [section.model_dump() for section in result.sections]}
