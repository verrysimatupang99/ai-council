"""
API-based AI Providers
"""

import asyncio
import time
from typing import AsyncIterator, List, Optional

import httpx

from .base import BaseProvider, Message, ProviderResponse


class OpenAICompatibleProvider(BaseProvider):
    """Base class for OpenAI-compatible API providers"""
    
    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.api_key = config.get("api_key", "")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
    
    async def chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResponse:
        """Send chat request to OpenAI-compatible API"""
        start_time = time.time()
        
        if not self.api_key:
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model=self.model,
                latency_ms=0,
                success=False,
                error="API key not configured",
            )
        
        try:
            formatted_messages = self._format_messages(messages, system_prompt)
            
            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
                "stream": False,
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                )
                response.raise_for_status()
                data = response.json()
                
                content = data["choices"][0]["message"]["content"]
                latency = (time.time() - start_time) * 1000
                
                return ProviderResponse(
                    provider_name=self.name,
                    content=content,
                    model=self.model,
                    latency_ms=latency,
                    success=True,
                    raw_response=data,
                )
        
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model=self.model,
                latency_ms=latency,
                success=False,
                error=str(e),
            )
    
    async def chat_stream(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream chat response"""
        if not self.api_key:
            yield ""
            return
        
        try:
            formatted_messages = self._format_messages(messages, system_prompt)
            
            payload = {
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
                "stream": True,
            }
            
            if max_tokens:
                payload["max_tokens"] = max_tokens
            
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json=payload,
                ) as response:
                    response.raise_for_status()
                    async for line in response.aiter_lines():
                        if line.startswith("data: "):
                            data = line[6:]
                            if data == "[DONE]":
                                break
                            try:
                                import json
                                parsed = json.loads(data)
                                delta = parsed["choices"][0]["delta"].get("content", "")
                                if delta:
                                    yield delta
                            except:
                                continue
        except Exception:
            pass
    
    def _format_messages(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
    ) -> List[dict]:
        """Format messages for API"""
        result = []
        if system_prompt:
            result.append({"role": "system", "content": system_prompt})
        for msg in messages:
            result.append({"role": msg.role, "content": msg.content})
        return result


class OpenRouterProvider(OpenAICompatibleProvider):
    """OpenRouter API provider"""
    
    def __init__(self, config: dict):
        super().__init__("openrouter", config)
        self.base_url = config.get("base_url", "https://openrouter.ai/api/v1")
        self.headers["HTTP-Referer"] = "https://github.com/ai-council"
        self.headers["X-Title"] = "AI Council CLI"


class GroqProvider(OpenAICompatibleProvider):
    """Groq API provider"""
    
    def __init__(self, config: dict):
        super().__init__("groq", config)
        self.base_url = config.get("base_url", "https://api.groq.com/openai/v1")


class CerebrasProvider(OpenAICompatibleProvider):
    """Cerebras API provider"""
    
    def __init__(self, config: dict):
        super().__init__("cerebras", config)
        self.base_url = config.get("base_url", "https://api.cerebras.ai/v1")


class MistralProvider(OpenAICompatibleProvider):
    """Mistral AI provider"""
    
    def __init__(self, config: dict):
        super().__init__("mistral", config)
        self.base_url = config.get("base_url", "https://api.mistral.ai/v1")


class GeminiProvider(BaseProvider):
    """Google Gemini API provider using official SDK"""
    
    def __init__(self, config: dict):
        super().__init__("gemini", config)
        self.api_key = config.get("api_key", "")
        self.model_name = config.get("model", "gemini-2.0-flash")
        
        # Initialize the library
        if self.api_key:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel(self.model_name)
        else:
            self.model = None
    
    async def chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResponse:
        """Send chat request to Gemini API"""
        start_time = time.time()
        
        if not self.api_key or not self.model:
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model=self.model_name,
                latency_ms=0,
                success=False,
                error="API key not configured",
            )
        
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                import google.generativeai as genai
            
            # Format messages for Gemini SDK
            gemini_messages = []
            for msg in messages:
                role = "user" if msg.role == "user" else "model"
                gemini_messages.append({"role": role, "parts": [msg.content]})
            
            # Create config
            generation_config = genai.types.GenerationConfig(
                temperature=temperature,
                max_output_tokens=max_tokens,
            )
            
            # System prompt is passed to GenerativeModel constructor or via chat start
            # For simplicity, we'll use start_chat if system_prompt is handled via message
            # But the best way is to set it in the model constructor
            if system_prompt:
                model_with_system = genai.GenerativeModel(
                    self.model_name,
                    system_instruction=system_prompt
                )
            else:
                model_with_system = self.model
                
            # Run in executor since SDK is synchronous/blocking for some parts
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model_with_system.generate_content(
                    gemini_messages,
                    generation_config=generation_config
                )
            )
            
            content = response.text
            latency = (time.time() - start_time) * 1000
            
            # Extract usage if available
            usage = {}
            try:
                if hasattr(response, "usage_metadata"):
                    # UsageMetadata in newer SDK might not have to_dict() or have different structure
                    meta = response.usage_metadata
                    usage = {
                        "prompt_token_count": getattr(meta, "prompt_token_count", 0),
                        "candidates_token_count": getattr(meta, "candidates_token_count", 0),
                        "total_token_count": getattr(meta, "total_token_count", 0),
                    }
            except:
                pass
            
            return ProviderResponse(
                provider_name=self.name,
                content=content,
                model=self.model_name,
                latency_ms=latency,
                success=True,
                raw_response={"usage": usage},
            )
        
        except Exception as e:
            latency = (time.time() - start_time) * 1000
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model=self.model_name,
                latency_ms=latency,
                success=False,
                error=str(e),
            )
    
    async def chat_stream(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream chat response"""
        # SDK supports streaming but implementing here for consistency
        response = await self.chat(messages, system_prompt, temperature, max_tokens)
        if response.success:
            yield response.content
