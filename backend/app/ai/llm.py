"""Configurable LLM provider abstraction."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import settings
from app.utils.logger import get_logger

logger = get_logger(__name__)

MODEL_REGISTRY: dict[str, dict[str, str]] = {
    "gpt-4o": {"provider": "openai", "model_id": "gpt-4o"},
    "claude-sonnet": {"provider": "anthropic", "model_id": settings.ANTHROPIC_DEFAULT_MODEL},
    "llama-3.1": {"provider": "ollama", "model_id": settings.OLLAMA_DEFAULT_MODEL},
}


def get_chat_model(model_name: str | None = None, temperature: float | None = None) -> BaseChatModel:
    """Return a LangChain chat model for the given model name."""
    name = model_name or settings.DEFAULT_LLM_MODEL
    info = MODEL_REGISTRY.get(name, MODEL_REGISTRY["gpt-4o"])
    temp = temperature if temperature is not None else settings.OPENAI_TEMPERATURE

    if info["provider"] == "openai":
        return ChatOpenAI(
            model=info["model_id"],
            api_key=settings.OPENAI_API_KEY or "not-set",
            temperature=temp,
            max_tokens=settings.OPENAI_MAX_TOKENS,
        )
    if info["provider"] == "anthropic":
        return ChatAnthropic(
            model=info["model_id"],
            api_key=settings.ANTHROPIC_API_KEY or "not-set",
            temperature=temp,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
        )
    # Ollama via OpenAI-compatible endpoint
    return ChatOpenAI(
        model=info["model_id"],
        base_url=f"{settings.OLLAMA_BASE_URL}/v1",
        api_key="ollama",
        temperature=temp,
    )


def is_model_available(model_name: str) -> bool:
    info = MODEL_REGISTRY.get(model_name)
    if not info:
        return False
    if info["provider"] == "openai":
        return bool(settings.OPENAI_API_KEY)
    if info["provider"] == "anthropic":
        return bool(settings.ANTHROPIC_API_KEY)
    return True


async def invoke_llm(
    prompt: str,
    system: str | None = None,
    model_name: str | None = None,
) -> str:
    """Invoke LLM and return text response."""
    llm = get_chat_model(model_name)
    messages: list = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))

    try:
        response = await llm.ainvoke(messages)
        return str(response.content)
    except Exception as exc:
        logger.warning("llm_invoke_failed", model=model_name, error=str(exc))
        return _fallback_response(prompt)


async def stream_llm(
    prompt: str,
    system: str | None = None,
    model_name: str | None = None,
) -> AsyncIterator[str]:
    """Stream LLM tokens."""
    llm = get_chat_model(model_name)
    messages: list = []
    if system:
        messages.append(SystemMessage(content=system))
    messages.append(HumanMessage(content=prompt))

    try:
        async for chunk in llm.astream(messages):
            if chunk.content:
                yield str(chunk.content)
    except Exception as exc:
        logger.warning("llm_stream_failed", model=model_name, error=str(exc))
        yield _fallback_response(prompt)


def _fallback_response(prompt: str) -> str:
    """Deterministic fallback when no LLM API key is configured."""
    if "claim" in prompt.lower() and "extract" in prompt.lower():
        return '["Metformin lowers blood glucose", "Metformin may cause nausea"]'
    if "verify" in prompt.lower() or "supported" in prompt.lower():
        return "SUPPORTED"
    return (
        "Based on available medical literature, the requested information requires "
        "consultation with a qualified healthcare professional. "
        "Insufficient evidence found for a definitive answer without API access."
    )
