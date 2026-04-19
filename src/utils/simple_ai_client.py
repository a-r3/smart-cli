"""Simple AI Client with provider-aware request handling."""

import asyncio
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import aiohttp


@dataclass
class Message:
    """Simple message structure."""

    role: str
    content: str


@dataclass
class AIResponse:
    """Simple AI response."""

    content: str
    model: str
    usage: dict


class SimpleOpenRouterClient:
    """Minimal AI client with OpenRouter and Anthropic support."""

    def __init__(self, config_manager=None):
        if config_manager is None:
            try:
                from .config import ConfigManager
            except ImportError:
                from config import ConfigManager
            config_manager = ConfigManager()
        self.config = config_manager
        self.provider = "openrouter"
        self.api_key = config_manager.get_config("openrouter_api_key")
        self.base_url = "https://openrouter.ai/api/v1"
        self.session = None
        self.last_request_time = 0
        self.rate_limit_delay = 1.0  # Minimum delay between requests
        self.max_retries = 3

        # Dynamic model selection
        self.current_model = config_manager.get_config(
            "default_model", "anthropic/claude-3-sonnet-20240229"
        )
        
        # Support direct Anthropic API if no OpenRouter key
        if not self.api_key:
            self.api_key = config_manager.get_config("anthropic_api_key")
            if self.api_key:
                self.provider = "anthropic"
                self.base_url = "https://api.anthropic.com/v1"
                self.current_model = "claude-3-sonnet-20240229"

        # Intelligent caching system
        self.cache_enabled = config_manager.get_config("ai_cache_enabled", True)
        self.cache = None
        if self.cache_enabled:
            self._initialize_cache()

    def _initialize_cache(self):
        """Initialize AI response cache."""
        try:
            from ..core.ai_cache import get_ai_cache

            self.cache = get_ai_cache()
            # Start background cleanup if event loop is available
            if hasattr(self.cache, '_start_background_cleanup'):
                self.cache._start_background_cleanup()
        except (ImportError, RuntimeError):
            self.cache_enabled = False
            self.cache = None

    def set_model(self, model_name: str):
        """Set the current model for subsequent requests."""
        self.current_model = model_name

    def get_current_model(self) -> str:
        """Get the currently selected model."""
        return self.current_model

    def _normalize_model_name(self, model: str) -> str:
        """Normalize provider-prefixed model names for direct provider APIs."""
        if self.provider == "anthropic" and "/" in model:
            provider_name, normalized_model = model.split("/", 1)
            if provider_name == "anthropic":
                return normalized_model
        return model

    def _create_cache_context(
        self, model: str, messages: List[Message]
    ) -> Dict[str, Any]:
        """Create context for cache key generation."""
        return {
            "model": model,
            "message_count": len(messages),
            "has_system_message": any(msg.role == "system" for msg in messages),
            "total_length": sum(len(msg.content) for msg in messages),
        }

    def _build_request_data(
        self, selected_model: str, messages: List[Message]
    ) -> Dict[str, Any]:
        """Build provider-specific request payload."""
        normalized_model = self._normalize_model_name(selected_model)

        if self.provider == "anthropic":
            system_messages = [
                msg.content for msg in messages if msg.role == "system"
            ]
            chat_messages = [
                {"role": msg.role, "content": msg.content}
                for msg in messages
                if msg.role != "system"
            ]
            data = {
                "model": normalized_model,
                "messages": chat_messages,
                "max_tokens": 4000,
            }
            if system_messages:
                data["system"] = "\n".join(system_messages)
            return data

        return {
            "model": normalized_model,
            "messages": [
                {"role": msg.role, "content": msg.content} for msg in messages
            ],
            "temperature": 0.7,
            "max_tokens": 4000,
        }

    def _build_headers(self) -> Dict[str, str]:
        """Build provider-specific request headers."""
        if self.provider == "anthropic":
            return {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            }

        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://smart-cli.dev",
            "X-Title": "Smart CLI",
        }

    def _get_endpoint_path(self) -> str:
        """Return the provider-specific API path."""
        if self.provider == "anthropic":
            return "/messages"
        return "/chat/completions"

    def _parse_response(
        self, result: Dict[str, Any], selected_model: str
    ) -> AIResponse:
        """Parse provider-specific responses into a common shape."""
        if self.provider == "anthropic":
            content_blocks = result.get("content", [])
            text_parts = [
                block.get("text", "")
                for block in content_blocks
                if block.get("type") == "text"
            ]
            usage = result.get("usage", {})
            return AIResponse(
                content="".join(text_parts),
                model=result.get("model", self._normalize_model_name(selected_model)),
                usage=usage,
            )

        content = (
            result.get("choices", [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        return AIResponse(
            content=content,
            model=result.get("model", selected_model),
            usage=result.get("usage", {}),
        )

    async def initialize(self):
        """Initialize HTTP session."""
        if not self.session:
            self.session = aiohttp.ClientSession()

    async def close_session(self):
        """Close HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None

    async def generate_response(self, user_input: str, model: str = None) -> AIResponse:
        """Generate AI response with intelligent caching, retry logic and rate limiting."""

        if not self.api_key:
            raise ValueError("OpenRouter API key not configured")

        await self.initialize()

        # Prepare model and messages first for caching
        selected_model = model or self.current_model

        # Prepare messages with identity context
        messages = [
            Message(
                role="system",
                content="You are Smart CLI - Smart Multi-Agent Development Assistant. You have intelligent multi-agent orchestration, cost-effective model selection, smart budget management, and superior development assistance. Always respond as Smart CLI with awareness of your advanced features.",
            ),
            Message(role="user", content=user_input),
        ]

        # Try cache first if enabled
        if self.cache_enabled and self.cache:
            try:
                cache_context = self._create_cache_context(selected_model, messages)
                cached_response = await self.cache.get(user_input, cache_context)

                if cached_response:
                    return AIResponse(
                        content=cached_response,
                        model=selected_model,
                        usage={"cached": True, "tokens": 0},
                    )
            except Exception:
                # Cache errors shouldn't break the flow
                pass

        # Rate limiting
        current_time = time.time()
        if current_time - self.last_request_time < self.rate_limit_delay:
            await asyncio.sleep(
                self.rate_limit_delay - (current_time - self.last_request_time)
            )

        self.last_request_time = time.time()

        data = self._build_request_data(selected_model, messages)
        headers = self._build_headers()
        endpoint_path = self._get_endpoint_path()

        # Retry logic
        last_exception = None
        for attempt in range(self.max_retries):
            try:
                timeout = aiohttp.ClientTimeout(
                    total=60
                )  # 60 second timeout for implementations
                async with self.session.post(
                    f"{self.base_url}{endpoint_path}",
                    json=data,
                    headers=headers,
                    timeout=timeout,
                ) as response:

                    if response.status == 200:
                        result = await response.json()
                        parsed_response = self._parse_response(result, selected_model)
                        content = parsed_response.content
                        model_used = parsed_response.model
                        usage = parsed_response.usage

                        # Cache the response if enabled
                        if self.cache_enabled and self.cache and content:
                            try:
                                cache_context = self._create_cache_context(
                                    selected_model, messages
                                )
                                cache_metadata = {
                                    "model": model_used,
                                    "usage": usage,
                                    "response_length": len(content),
                                }
                                await self.cache.set(
                                    user_input, content, cache_context, cache_metadata
                                )
                            except Exception:
                                # Cache errors shouldn't break the flow
                                pass

                        return parsed_response
                    elif response.status == 429:  # Rate limit
                        retry_after = int(response.headers.get("retry-after", 5))
                        await asyncio.sleep(retry_after)
                        continue
                    elif response.status >= 500:  # Server error, retry
                        error_text = await response.text()
                        last_exception = Exception(
                            f"Server error {response.status}: {error_text}"
                        )
                        await asyncio.sleep(2**attempt)  # Exponential backoff
                        continue
                    else:
                        error_text = await response.text()
                        raise Exception(
                            f"{self.provider.title()} API error {response.status}: {error_text}"
                        )

            except asyncio.TimeoutError:
                last_exception = Exception("Request timeout")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                continue
            except Exception as e:
                last_exception = e
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2**attempt)
                continue

        raise Exception(
            f"AI request failed after {self.max_retries} attempts: {str(last_exception)}"
        )


# Backward compatibility
OpenRouterClient = SimpleOpenRouterClient
AIClient = SimpleOpenRouterClient
