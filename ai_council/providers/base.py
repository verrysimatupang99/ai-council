"""
Base provider interface for all AI providers
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import AsyncIterator, List, Optional


@dataclass
class Message:
    """Represents a chat message"""
    role: str  # "system", "user", or "assistant"
    content: str


@dataclass
class ProviderResponse:
    """Standardized response from any provider"""
    provider_name: str
    content: str
    model: str
    latency_ms: float
    success: bool
    error: Optional[str] = None
    raw_response: Optional[dict] = None


class BaseProvider(ABC):
    """Abstract base class for all AI providers"""
    
    def __init__(self, name: str, config: dict):
        self.name = name
        self.config = config
        self.enabled = config.get("enabled", False)
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResponse:
        """Send a chat request and get response"""
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream chat response token by token"""
        pass
    
    def is_available(self) -> bool:
        """Check if provider is available (configured and healthy)"""
        return self.enabled
    
    def get_model(self) -> str:
        """Get the default model name"""
        return self.config.get("model", "default")
    
    def _create_messages(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
    ) -> List[Message]:
        """Create message list with optional system prompt"""
        result = []
        if system_prompt:
            result.append(Message(role="system", content=system_prompt))
        result.extend(messages)
        return result
