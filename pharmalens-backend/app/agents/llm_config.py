"""LangChain model construction and structured-output fallback handling."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import TypeVar

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel

from app.core.config import settings


logger = logging.getLogger(__name__)
OutputModel = TypeVar("OutputModel", bound=BaseModel)


class LLMConfigurationError(RuntimeError):
    """Indicate that no configured LangChain model can be constructed."""


class LLMInvocationError(RuntimeError):
    """Indicate that all configured models failed a structured invocation."""


def _build_google_llm() -> BaseChatModel:
    """Build the configured Gemini Flash model lazily."""
    if not settings.google_api_key.strip():
        raise LLMConfigurationError("GOOGLE_API_KEY is not configured.")
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI
    except ImportError as error:
        raise LLMConfigurationError(
            "langchain-google-genai is required for the Google LLM provider."
        ) from error
    return ChatGoogleGenerativeAI(
        model="gemini-1.5-flash",
        google_api_key=settings.google_api_key,
        temperature=0,
    )


def _build_openai_llm() -> BaseChatModel:
    """Build the configured GPT-4o-mini fallback model lazily."""
    if not settings.openai_api_key.strip():
        raise LLMConfigurationError("OPENAI_API_KEY is not configured.")
    try:
        from langchain_openai import ChatOpenAI
    except ImportError as error:
        raise LLMConfigurationError(
            "langchain-openai is required for the OpenAI LLM provider."
        ) from error
    return ChatOpenAI(
        model="gpt-4o-mini",
        api_key=settings.openai_api_key,
        temperature=0,
    )


def _provider_order() -> tuple[str, str]:
    """Return the configured provider followed by its supported fallback."""
    provider = settings.llm_provider.strip().lower()
    if provider == "google":
        return ("google", "openai")
    if provider == "openai":
        return ("openai", "google")
    raise LLMConfigurationError("LLM_PROVIDER must be either 'google' or 'openai'.")


@lru_cache(maxsize=1)
def get_llm_candidates() -> tuple[BaseChatModel, ...]:
    """Construct all configured models in primary-then-fallback order."""
    builders = {
        "google": _build_google_llm,
        "openai": _build_openai_llm,
    }
    candidates: list[BaseChatModel] = []
    for provider in _provider_order():
        try:
            candidates.append(builders[provider]())
        except LLMConfigurationError as error:
            logger.info("Skipping unavailable %s LLM provider: %s", provider, error)
    if not candidates:
        raise LLMConfigurationError(
            "No configured LLM provider is available. Configure GOOGLE_API_KEY "
            "or OPENAI_API_KEY."
        )
    return tuple(candidates)


def get_llm() -> BaseChatModel:
    """Return the primary available model for callers that need one model."""
    return get_llm_candidates()[0]


def invoke_structured(
    prompt: ChatPromptTemplate,
    output_model: type[OutputModel],
    variables: dict[str, object],
) -> OutputModel:
    """Invoke a structured chain and retry with the configured fallback model."""
    invocation_errors: list[str] = []
    try:
        llm_candidates = get_llm_candidates()
    except LLMConfigurationError as error:
        raise LLMInvocationError(str(error)) from error

    for llm in llm_candidates:
        for attempt in range(1, settings.llm_max_attempts + 1):
            try:
                structured_llm = llm.with_structured_output(output_model)
                result = (prompt | structured_llm).invoke(variables)
                if isinstance(result, output_model):
                    return result
                return output_model.model_validate(result)
            except Exception as error:
                invocation_errors.append(
                    f"{type(llm).__name__}:{type(error).__name__}:attempt={attempt}"
                )
                logger.warning(
                    "Structured LLM invocation failed for %s on attempt %d/%d.",
                    type(llm).__name__,
                    attempt,
                    settings.llm_max_attempts,
                    exc_info=True,
                )
    providers = ", ".join(invocation_errors) or "none"
    raise LLMInvocationError(
        f"All configured LLM providers failed during structured invocation: {providers}."
    )
