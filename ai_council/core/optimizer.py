"""
Token Optimizer for AI Council - Manages token counting and smart context compression
"""

import tiktoken
from typing import List, Dict, Any, Optional


class TokenOptimizer:
    """Handles token counting and context optimization"""
    
    def __init__(self, default_model: str = "gpt-3.5-turbo"):
        # We use gpt-3.5-turbo encoding as a safe default for most OpenAI-compatible models
        try:
            self.encoding = tiktoken.encoding_for_model(default_model)
        except Exception:
            self.encoding = tiktoken.get_encoding("cl100k_base")
            
    def count_tokens(self, text: str) -> int:
        """Count tokens in a string"""
        if not text:
            return 0
        return len(self.encoding.encode(text))
    
    def truncate_to_limit(self, text: str, max_tokens: int) -> str:
        """Truncate text to stay within token limit"""
        tokens = self.encoding.encode(text)
        if len(tokens) <= max_tokens:
            return text
        return self.encoding.decode(tokens[:max_tokens])
    
    def optimize_context(self, responses: Dict[str, str], max_tokens_per_agent: int = 1000) -> str:
        """
        Compress previous responses into a optimized context string.
        Removes fluff and ensures each agent's contribution is within limits.
        """
        optimized_parts = []
        for agent, content in responses.items():
            # Basic cleanup (remove excessive newlines and spaces)
            cleaned = " ".join(content.split())
            
            # Truncate if still too long
            shortened = self.truncate_to_limit(cleaned, max_tokens_per_agent)
            
            optimized_parts.append(f"### {agent}:\n{shortened}")
            
        return "\n\n".join(optimized_parts)

    def should_summarize(self, all_responses: List[Dict[str, Any]], threshold: int = 4000) -> bool:
        """Check if total tokens exceed a threshold, suggesting a summary is needed"""
        total_text = "".join([r.get('content', '') for r in all_responses])
        return self.count_tokens(total_text) > threshold
