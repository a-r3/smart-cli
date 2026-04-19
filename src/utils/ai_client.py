"""Legacy AI client compatibility layer for older tests."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

import aiohttp

from .config import ConfigManager


@dataclass
class ChatMessage:
    """Legacy chat message structure."""

    role: str
    content: str
    timestamp: Optional[datetime] = None


@dataclass
class AIResponse:
    """Legacy AI response structure."""

    content: str
    model: str
    usage: Dict[str, Any]
    timestamp: Optional[datetime] = None
    cost_estimate: float = 0.0


class OpenRouterClient:
    """Compatibility wrapper around the older chat-style client API."""

    def __init__(self, config: Optional[ConfigManager] = None):
        if config is None:
            try:
                from . import config as config_module
            except ImportError:
                import config as config_module
            config = config_module.ConfigManager()
        self.config = config
        self.api_key = self.config.get_config("openrouter_api_key")
        self.base_url = "https://openrouter.ai/api/v1"
        self.fallback_models = self.config.get_config(
            "fallback_models",
            ["anthropic/claude-3-sonnet-20240229"],
        )
        self.max_retries = self.config.get_config("max_retries", 3)
        self.timeout = self.config.get_config("timeout", 30)
        self.temperature = self.config.get_config("temperature", 0.7)
        self.max_tokens = self.config.get_config("max_tokens", 4000)
        self.session: Optional[aiohttp.ClientSession] = None

        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.request_count = 0

    async def __aenter__(self) -> "OpenRouterClient":
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close_session()

    async def initialize(self) -> None:
        """Initialize the HTTP session lazily."""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=self.timeout)
            self.session = aiohttp.ClientSession(timeout=timeout)

    async def close_session(self) -> None:
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def generate_response(self, messages: List[ChatMessage]) -> AIResponse:
        """Generate a response using fallback model handling."""
        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        last_error: Optional[Exception] = None
        for model in self.fallback_models:
            try:
                response_data = await self._make_request(messages, model)
                parsed = self._parse_response(response_data, model)
                self.request_count += 1
                self.total_tokens_used += parsed.usage.get("total_tokens", 0)
                self.total_cost += parsed.cost_estimate
                return parsed
            except Exception as exc:  # pragma: no cover - validated by tests
                last_error = exc

        raise Exception(f"All AI models failed: {last_error}")

    async def _make_request(
        self, messages: List[ChatMessage], model: str
    ) -> Dict[str, Any]:
        """Perform one HTTP request with retry on rate limit."""
        await self.initialize()
        payload = {
            "model": model,
            "messages": [{"role": msg.role, "content": msg.content} for msg in messages],
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        for attempt in range(self.max_retries):
            try:
                request_ctx = self.session.post(
                    f"{self.base_url}/chat/completions",
                    json=payload,
                    headers=headers,
                )
                if hasattr(request_ctx, "__await__"):
                    request_ctx = await request_ctx

                async with request_ctx as response:
                    if response.status == 200:
                        return await response.json()

                    if response.status == 401:
                        raise ValueError("Invalid API key")

                    if response.status == 429:
                        if attempt == self.max_retries - 1:
                            raise ValueError("Rate limited")
                        await asyncio.sleep(attempt + 1)
                        continue

                    error_body = await response.json()
                    raise ValueError(str(error_body))
            except asyncio.TimeoutError:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(attempt + 1)

        raise ValueError("Request failed")

    def _parse_response(self, response_data: Dict[str, Any], model: str) -> AIResponse:
        """Parse API responses into the legacy response type."""
        if "error" in response_data:
            error = response_data["error"]
            message = (
                error.get("message")
                if isinstance(error, dict)
                else str(error)
            )
            raise ValueError(f"API error: {message}")

        choices = response_data.get("choices", [])
        if not choices:
            raise ValueError("No response choices in API response")

        content = choices[0].get("message", {}).get("content", "")
        usage = response_data.get("usage", {})
        return AIResponse(
            content=content,
            model=model,
            usage=usage,
            timestamp=datetime.now(),
            cost_estimate=self._estimate_cost(usage, model),
        )

    def _estimate_cost(self, usage: Dict[str, Any], model: str) -> float:
        """Estimate cost using a tiny model-rate table."""
        total_tokens = usage.get("total_tokens", 0)
        rates = {
            "anthropic/claude-3-sonnet-20240229": 0.000003,
            "openai/gpt-4-turbo": 0.00001,
            "google/gemini-pro": 0.0000015,
        }
        rate = rates.get(model, 0.000002)
        return total_tokens * rate

    def get_usage_stats(self) -> Dict[str, Any]:
        """Return aggregated usage statistics."""
        average = (
            self.total_tokens_used / self.request_count
            if self.request_count
            else 0
        )
        return {
            "total_requests": self.request_count,
            "total_tokens": self.total_tokens_used,
            "estimated_cost": self.total_cost,
            "average_tokens_per_request": average,
        }

    def reset_usage_stats(self) -> None:
        """Reset usage accounting."""
        self.total_tokens_used = 0
        self.total_cost = 0.0
        self.request_count = 0


class MultiLLMClient:
    """Minimal multi-provider compatibility wrapper."""

    def __init__(self, config: Optional[ConfigManager] = None):
        self.config = config or ConfigManager()
        self.openrouter_client: Optional[OpenRouterClient] = None

    async def get_client(self, provider: str) -> OpenRouterClient:
        """Return or create the requested provider client."""
        if provider != "openrouter":
            raise ValueError(f"Unsupported AI provider: {provider}")
        if not self.openrouter_client:
            self.openrouter_client = OpenRouterClient(self.config)
        return self.openrouter_client

    async def generate_response(
        self, messages: List[ChatMessage], provider: str = "openrouter"
    ) -> AIResponse:
        """Generate a response through the selected provider."""
        client = await self.get_client(provider)
        return await client.generate_response(messages)

    async def close_all_sessions(self) -> None:
        """Close all cached provider sessions."""
        if self.openrouter_client:
            await self.openrouter_client.close_session()
