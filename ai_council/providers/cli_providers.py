"""
CLI-based AI Providers
Wraps existing CLI tools (gemini, codex, qwen, kilo)
"""

import asyncio
import time
from typing import AsyncIterator, List, Optional

from .base import BaseProvider, Message, ProviderResponse


class BaseCLIProvider(BaseProvider):
    """Base class for CLI-based providers"""
    
    def __init__(self, name: str, config: dict):
        super().__init__(name, config)
        self.command = config.get("command", name)
        self.description = config.get("description", "")
    
    async def _run_cli(
        self,
        prompt: str,
        timeout: int = 60,
    ) -> tuple[str, int]:
        """
        Run CLI command using 4-Tier Invocation Strategy.
        Optimized for automation based on community benchmarks.
        """
        # Define tool-specific patterns (Tier 1)
        tool_patterns = {
            'kilo_cli': [['kilo', 'run', prompt]],
            'qwen_cli': [['qwen', '-p', prompt], ['qwen', prompt]],
            'gemini_cli': [['gemini', '-p', prompt], ['gemini', prompt]],
            'codex_cli': [['codex', 'exec', prompt], ['codex', prompt]],
        }

        # Strategy 1 & 2: Try specific patterns or direct arguments
        commands_to_try = tool_patterns.get(self.name, [[self.command, prompt]])
        
        for cmd_args in commands_to_try:
            process = None
            try:
                process = await asyncio.create_subprocess_exec(
                    *cmd_args,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(),
                    timeout=timeout,
                )
                
                if process.returncode == 0 and stdout:
                    return stdout.decode(), 0
            except Exception:
                if process:
                    try:
                        process.kill()
                        await process.wait() # Properly wait for cleanup
                    except: pass
                continue

        # Tier 3: Fallback to stdin pipe
        process = None
        try:
            process = await asyncio.create_subprocess_exec(
                self.command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            stdout, stderr = await asyncio.wait_for(
                process.communicate(input=prompt.encode()),
                timeout=timeout,
            )
            
            if process.returncode == 0:
                return stdout.decode(), 0
        except Exception:
            if process:
                try:
                    process.kill()
                    await process.wait() # Properly wait for cleanup
                except: pass

        # Tier 4: File-based input (Last resort for very long prompts)
        import tempfile
        try:
            with tempfile.NamedTemporaryFile(mode='w+', suffix='.txt', delete=True) as tf:
                tf.write(prompt)
                tf.flush()
                process = await asyncio.create_subprocess_exec(
                    self.command,
                    tf.name,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=timeout)
                if process.returncode == 0:
                    return stdout.decode(), 0
        except:
            pass

        return "", -3 # All tiers failed


class GeminiCLIProvider(BaseCLIProvider):
    """Gemini CLI provider (Google One AI Pro)"""
    
    def __init__(self, config: dict):
        super().__init__("gemini_cli", config)
    
    async def chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResponse:
        """Send query to Gemini CLI"""
        start_time = time.time()
        
        # Build prompt
        prompt = ""
        if system_prompt:
            prompt = f"{system_prompt}\n\n"
        
        for msg in messages:
            if msg.role == "user":
                prompt += f"{msg.content}\n"
        
        stdout, returncode = await self._run_cli(prompt)
        latency = (time.time() - start_time) * 1000
        
        if returncode == 0:
            return ProviderResponse(
                provider_name=self.name,
                content=stdout.strip(),
                model="gemini-cli",
                latency_ms=latency,
                success=True,
            )
        elif returncode == -1:
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model="gemini-cli",
                latency_ms=latency,
                success=False,
                error="CLI command timed out",
            )
        elif returncode == -2:
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model="gemini-cli",
                latency_ms=latency,
                success=False,
                error=f"Command '{self.command}' not found",
            )
        else:
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model="gemini-cli",
                latency_ms=latency,
                success=False,
                error=f"CLI error (code: {returncode})",
            )
    
    async def chat_stream(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream not supported for CLI, returns full response"""
        response = await self.chat(messages, system_prompt, temperature, max_tokens)
        if response.success:
            for chunk in response.content.split("\n"):
                yield chunk + "\n"


class CodexCLIProvider(BaseCLIProvider):
    """Codex CLI provider (ChatGPT free)"""
    
    def __init__(self, config: dict):
        super().__init__("codex_cli", config)
    
    async def chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResponse:
        """Send query to Codex CLI"""
        start_time = time.time()
        
        prompt = ""
        if system_prompt:
            prompt = f"{system_prompt}\n\n"
        
        for msg in messages:
            if msg.role == "user":
                prompt += f"{msg.content}\n"
        
        stdout, returncode = await self._run_cli(prompt)
        latency = (time.time() - start_time) * 1000
        
        if returncode == 0:
            return ProviderResponse(
                provider_name=self.name,
                content=stdout.strip(),
                model="codex-cli",
                latency_ms=latency,
                success=True,
            )
        else:
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model="codex-cli",
                latency_ms=latency,
                success=False,
                error=f"Codex CLI error (code: {returncode})",
            )
    
    async def chat_stream(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream not supported for CLI"""
        response = await self.chat(messages, system_prompt, temperature, max_tokens)
        if response.success:
            yield response.content


class QwenCLIProvider(BaseCLIProvider):
    """Qwen CLI provider (free tier)"""
    
    def __init__(self, config: dict):
        super().__init__("qwen_cli", config)
    
    async def chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResponse:
        """Send query to Qwen CLI"""
        start_time = time.time()
        
        prompt = ""
        if system_prompt:
            prompt = f"{system_prompt}\n\n"
        
        for msg in messages:
            if msg.role == "user":
                prompt += f"{msg.content}\n"
        
        stdout, returncode = await self._run_cli(prompt)
        latency = (time.time() - start_time) * 1000
        
        if returncode == 0:
            return ProviderResponse(
                provider_name=self.name,
                content=stdout.strip(),
                model="qwen-cli",
                latency_ms=latency,
                success=True,
            )
        else:
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model="qwen-cli",
                latency_ms=latency,
                success=False,
                error=f"Qwen CLI error (code: {returncode})",
            )
    
    async def chat_stream(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream not supported for CLI"""
        response = await self.chat(messages, system_prompt, temperature, max_tokens)
        if response.success:
            yield response.content


class KiloCLIProvider(BaseCLIProvider):
    """Kilo CLI provider (free tier)"""
    
    def __init__(self, config: dict):
        super().__init__("kilo_cli", config)
    
    async def chat(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> ProviderResponse:
        """Send query to Kilo CLI"""
        start_time = time.time()
        
        prompt = ""
        if system_prompt:
            prompt = f"{system_prompt}\n\n"
        
        for msg in messages:
            if msg.role == "user":
                prompt += f"{msg.content}\n"
        
        stdout, returncode = await self._run_cli(prompt)
        latency = (time.time() - start_time) * 1000
        
        if returncode == 0:
            return ProviderResponse(
                provider_name=self.name,
                content=stdout.strip(),
                model="kilo-cli",
                latency_ms=latency,
                success=True,
            )
        else:
            return ProviderResponse(
                provider_name=self.name,
                content="",
                model="kilo-cli",
                latency_ms=latency,
                success=False,
                error=f"Kilo CLI error (code: {returncode})",
            )
    
    async def chat_stream(
        self,
        messages: List[Message],
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
    ) -> AsyncIterator[str]:
        """Stream not supported for CLI"""
        response = await self.chat(messages, system_prompt, temperature, max_tokens)
        if response.success:
            yield response.content
