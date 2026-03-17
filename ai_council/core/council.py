"""
Council Coordinator - Manages AI agents and coordinates discussions
"""

import asyncio
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from ..providers.base import BaseProvider, Message, ProviderResponse
from ..core.config import Config


@dataclass
class Agent:
    """Represents an AI agent with a specific role"""
    name: str
    role: str
    provider: BaseProvider
    system_prompt: str
    temperature: float = 0.7
    responses: List[str] = field(default_factory=list)
    
    def add_response(self, content: str):
        """Add a response to the agent's history"""
        self.responses.append(content)
    
    def get_last_response(self) -> Optional[str]:
        """Get the most recent response"""
        return self.responses[-1] if self.responses else None


@dataclass
class CouncilSession:
    """Represents a council discussion session"""
    query: str
    agents: List[Agent]
    rounds: int = 0
    all_responses: List[Dict[str, str]] = field(default_factory=list)
    final_synthesis: Optional[str] = None


class CouncilCoordinator:
    """Coordinates the AI council discussion"""
    
    def __init__(self, config: Config):
        self.config = config
        self.providers: Dict[str, BaseProvider] = {}
        self.agents: Dict[str, Agent] = {}
        self._initialize_providers()
        self._initialize_agents()
    
    def _initialize_providers(self):
        """Initialize all configured providers"""
        from ..providers.api_providers import (
            OpenRouterProvider,
            GroqProvider,
            CerebrasProvider,
            MistralProvider,
            GeminiProvider,
        )
        from ..providers.cli_providers import (
            GeminiCLIProvider,
            CodexCLIProvider,
            QwenCLIProvider,
            KiloCLIProvider,
        )
        
        # API Providers
        api_configs = self.config.get_enabled_api_providers()
        
        if "openrouter" in api_configs:
            self.providers["openrouter"] = OpenRouterProvider(api_configs["openrouter"])
        if "groq" in api_configs:
            self.providers["groq"] = GroqProvider(api_configs["groq"])
        if "cerebras" in api_configs:
            self.providers["cerebras"] = CerebrasProvider(api_configs["cerebras"])
        if "mistral" in api_configs:
            self.providers["mistral"] = MistralProvider(api_configs["mistral"])
        if "gemini" in api_configs:
            self.providers["gemini"] = GeminiProvider(api_configs["gemini"])
        
        # CLI Providers
        cli_configs = self.config.get_enabled_cli_providers()
        
        if "gemini_cli" in cli_configs:
            self.providers["gemini_cli"] = GeminiCLIProvider(cli_configs["gemini_cli"])
        if "codex_cli" in cli_configs:
            self.providers["codex_cli"] = CodexCLIProvider(cli_configs["codex_cli"])
        if "qwen_cli" in cli_configs:
            self.providers["qwen_cli"] = QwenCLIProvider(cli_configs["qwen_cli"])
        if "kilo_cli" in cli_configs:
            self.providers["kilo_cli"] = KiloCLIProvider(cli_configs["kilo_cli"])
    
    def _initialize_agents(self):
        """Initialize agents based on configuration"""
        agent_roles = self.config.get_agent_roles()
        
        for role_name, role_config in agent_roles.items():
            provider_name = role_config.get("provider", "openrouter")
            
            if provider_name not in self.providers:
                continue
            
            agent = Agent(
                name=role_name,
                role=role_name.capitalize(),
                provider=self.providers[provider_name],
                system_prompt=role_config.get("system_prompt", ""),
                temperature=role_config.get("temperature", 0.7),
            )
            self.agents[role_name] = agent
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent names"""
        return list(self.agents.keys())
    
    async def query_agents(
        self,
        query: str,
        agent_names: Optional[List[str]] = None,
        context: Optional[str] = None,
    ) -> List[ProviderResponse]:
        """Query multiple agents in parallel"""
        
        if agent_names is None:
            agent_names = self.config.get_council_settings().get(
                "default_agents", ["architect", "critic", "optimizer"]
            )
        
        # Filter to available agents
        agents_to_query = [
            self.agents[name] for name in agent_names if name in self.agents
        ]
        
        if not agents_to_query:
            return []
        
        # Create messages
        messages = [Message(role="user", content=query)]
        if context:
            messages.insert(0, Message(role="user", content=f"Context: {context}"))
        
        # Query all agents in parallel
        tasks = [
            self._query_single_agent(agent, messages)
            for agent in agents_to_query
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process responses
        results = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                results.append(ProviderResponse(
                    provider_name=agents_to_query[i].name,
                    content="",
                    model="",
                    latency_ms=0,
                    success=False,
                    error=str(response),
                ))
            else:
                results.append(response)
                # Store response in agent history
                agents_to_query[i].add_response(response.content)
        
        return results
    
    async def _query_single_agent(
        self,
        agent: Agent,
        messages: List[Message],
    ) -> ProviderResponse:
        """Query a single agent"""
        return await agent.provider.chat(
            messages=messages,
            system_prompt=agent.system_prompt,
            temperature=agent.temperature,
            max_tokens=2000,
        )
    
    async def run_debate(
        self,
        query: str,
        rounds: int = 2,
        agent_names: Optional[List[str]] = None,
    ) -> CouncilSession:
        """Run a multi-round debate between agents"""
        
        if agent_names is None:
            agent_names = self.config.get_council_settings().get(
                "default_agents", ["architect", "critic", "optimizer"]
            )
        
        agents_to_use = [
            self.agents[name] for name in agent_names if name in self.agents
        ]
        
        session = CouncilSession(query=query, agents=agents_to_use)
        context = query
        
        for round_num in range(rounds):
            session.rounds = round_num + 1
            
            # Query all agents
            responses = await self.query_agents(
                query=query,
                agent_names=agent_names,
                context=context if round_num > 0 else None,
            )
            
            # Collect responses
            round_responses = {}
            for resp in responses:
                if resp.success:
                    round_responses[resp.provider_name] = resp.content
                    session.all_responses.append({
                        "round": round_num + 1,
                        "agent": resp.provider_name,
                        "content": resp.content,
                    })
            
            # Build context for next round (agents see each other's responses)
            if round_num < rounds - 1:
                context = self._build_debate_context(round_responses, round_num + 1)
        
        # Run synthesis
        synthesis = await self._synthesize(session)
        session.final_synthesis = synthesis
        
        return session
    
    def _build_debate_context(
        self,
        responses: Dict[str, str],
        round_num: int,
    ) -> str:
        """Build context from previous round responses"""
        context = f"Previous responses from Round {round_num}:\n\n"
        for agent, response in responses.items():
            # Increase limit to 2000 characters to provide more context
            context += f"{agent}: {response[:2000]}\n\n"
        context += "Please review these responses and provide your perspective."
        return context
    
    async def _synthesize(self, session: CouncilSession) -> str:
        """Synthesize all responses into a final recommendation"""
        
        moderator = self.agents.get("moderator")
        if not moderator:
            # If no moderator, use first available agent
            if session.agents:
                moderator = session.agents[0]
            else:
                return self._simple_synthesis(session)
        
        # Build synthesis prompt
        synthesis_prompt = self._build_synthesis_prompt(session)
        
        messages = [Message(role="user", content=synthesis_prompt)]
        
        response = await moderator.provider.chat(
            messages=messages,
            system_prompt=moderator.system_prompt,
            temperature=0.5,
            max_tokens=4000, # Increased max tokens for synthesis
        )
        
        if response.success:
            return response.content
        
        return self._simple_synthesis(session)
    
    def _build_synthesis_prompt(self, session: CouncilSession) -> str:
        """Build prompt for synthesis"""
        prompt = "Based on the following discussion, provide a final recommendation:\n\n"
        prompt += f"Original Query: {session.query}\n\n"
        
        # Include more content from responses for synthesis
        for i, resp in enumerate(session.all_responses):
            prompt += f"{resp['agent']} (Round {resp['round']}):\n{resp['content'][:1500]}\n\n"
        
        prompt += "\nPlease synthesize these perspectives into a coherent final recommendation."
        return prompt
    
    def _simple_synthesis(self, session: CouncilSession) -> str:
        """Simple synthesis without moderator"""
        synthesis = "## Council Summary\n\n"
        synthesis += f"Query: {session.query}\n\n"
        synthesis += f"Agents consulted: {', '.join(a.name for a in session.agents)}\n\n"
        
        # Group by round
        by_round = {}
        for resp in session.all_responses:
            round_num = resp["round"]
            if round_num not in by_round:
                by_round[round_num] = []
            by_round[round_num].append(resp)
        
        for round_num, responses in sorted(by_round.items()):
            synthesis += f"### Round {round_num}\n"
            for resp in responses:
                synthesis += f"**{resp['agent']}**: {resp['content'][:200]}...\n"
            synthesis += "\n"
        
        return synthesis
