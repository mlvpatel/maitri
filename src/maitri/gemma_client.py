"""Shared Gemma 4 client over the Hugging Face router with retry and audit hooks."""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from .config import get_settings


@dataclass
class GemmaResponse:
    call_id: str
    model: str
    content: str
    tool_calls: list[dict[str, Any]]
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_usd: float
    latency_ms: int
    raw: dict[str, Any] = field(repr=False)


class GemmaError(RuntimeError):
    pass


class GemmaClient:
    def __init__(self, audit_sink: Callable[[dict[str, Any]], None] | None = None) -> None:
        self._settings = get_settings()
        self._audit_sink = audit_sink
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if self._settings.provider == "hf":
            headers["Authorization"] = f"Bearer {self._settings.hf_token}"
            self._endpoint = self._settings.router_url
        else:
            self._endpoint = self._settings.ollama_base_url
        self._http = httpx.Client(
            timeout=httpx.Timeout(60.0, read=300.0),
            headers=headers,
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "GemmaClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def chat(
        self,
        messages: Sequence[dict[str, Any]],
        *,
        model: str | None = None,
        agent: str = "unknown",
        temperature: float = 0.2,
        max_tokens: int = 1024,
        tools: list[dict[str, Any]] | None = None,
        response_format: dict[str, Any] | None = None,
    ) -> GemmaResponse:
        if self._settings.provider == "ollama":
            # Override hosted model ids with the locally available ollama ones.
            if model is None or model == self._settings.reasoning_model:
                primary = self._settings.ollama_reasoning_model
                fallback = self._settings.ollama_light_model
            elif model == self._settings.light_model:
                primary = self._settings.ollama_light_model
                fallback = self._settings.ollama_reasoning_model
            else:
                primary = model
                fallback = self._settings.ollama_light_model
            return self._call(
                primary,
                list(messages),
                agent=agent,
                temperature=temperature,
                max_tokens=max_tokens,
                tools=None,  # ollama chat completion does not standardize tools
                response_format=response_format,
            )
        primary = model or self._settings.reasoning_model
        fallback = (
            self._settings.reasoning_fallback
            if primary == self._settings.reasoning_model
            else self._settings.light_fallback
        )
        for attempt_model in (primary, fallback):
            try:
                return self._call(
                    attempt_model,
                    list(messages),
                    agent=agent,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    tools=tools,
                    response_format=response_format,
                )
            except GemmaError:
                if attempt_model == fallback:
                    raise
                continue
        raise GemmaError("unreachable")

    @retry(
        retry=retry_if_exception_type(httpx.HTTPError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        reraise=True,
    )
    def _post(self, payload: dict[str, Any]) -> httpx.Response:
        return self._http.post(self._endpoint, json=payload)

    def _call(
        self,
        model: str,
        messages: list[dict[str, Any]],
        *,
        agent: str,
        temperature: float,
        max_tokens: int,
        tools: list[dict[str, Any]] | None,
        response_format: dict[str, Any] | None,
    ) -> GemmaResponse:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        if response_format:
            payload["response_format"] = response_format

        call_id = str(uuid.uuid4())
        started = time.perf_counter()
        response = self._post(payload)
        latency_ms = int((time.perf_counter() - started) * 1000)

        if response.status_code >= 400:
            raise GemmaError(f"router returned {response.status_code}: {response.text[:400]}")
        body = response.json()
        choice = (body.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        usage = body.get("usage") or {}
        out = GemmaResponse(
            call_id=call_id,
            model=model,
            content=message.get("content") or "",
            tool_calls=list(message.get("tool_calls") or []),
            prompt_tokens=int(usage.get("prompt_tokens") or 0),
            completion_tokens=int(usage.get("completion_tokens") or 0),
            estimated_cost_usd=float(usage.get("estimated_cost") or 0.0),
            latency_ms=latency_ms,
            raw=body,
        )
        if self._audit_sink is not None:
            self._audit_sink(
                {
                    "call_id": out.call_id,
                    "agent": agent,
                    "model": model,
                    "messages": messages,
                    "tool_calls": out.tool_calls,
                    "prompt_tokens": out.prompt_tokens,
                    "completion_tokens": out.completion_tokens,
                    "cost_usd": out.estimated_cost_usd,
                    "latency_ms": out.latency_ms,
                    "response_excerpt": out.content[:1200],
                }
            )
        return out


def _smoke() -> None:
    with GemmaClient() as client:
        s = client.chat(
            messages=[{"role": "user", "content": "Reply with one word: OK"}],
            agent="smoke",
            max_tokens=8,
        )
        print(json.dumps({"model": s.model, "content": s.content, "latency_ms": s.latency_ms}))


if __name__ == "__main__":
    import sys

    if "--smoke" in sys.argv:
        _smoke()
