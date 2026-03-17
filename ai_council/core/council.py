"""
Council Coordinator - Manages AI agents and coordinates discussions
"""

import asyncio
import uuid
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from ..providers.base import BaseProvider, Message, ProviderResponse
from ..core.config import Config
from ..core.storage import StorageManager
from ..core.optimizer import TokenOptimizer
from ..core.tools import ToolManager


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
    id: str
    query: str
    agents: List[Agent]
    rounds: int = 0
    all_responses: List[Dict[str, Any]] = field(default_factory=list)
    final_synthesis: Optional[str] = None


class CouncilCoordinator:
    """Coordinates the AI council discussion"""
    
    def __init__(self, config: Config):
        self.config = config
        self.providers: Dict[str, BaseProvider] = {}
        self.agents: Dict[str, Agent] = {}
        self.storage = StorageManager()
        self.optimizer = TokenOptimizer()
        self.tools = ToolManager()
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
        """Initialize agents based on configuration with real-time context"""
        agent_roles = self.config.get_agent_roles()
        tool_prompt = self.tools.get_tool_prompt()
        from datetime import datetime
        current_date = datetime.now().strftime("%B %d, %Y")
        
        for role_name, role_config in agent_roles.items():
            provider_name = role_config.get("provider", "openrouter")
            
            if provider_name not in self.providers:
                continue
            
            # Base prompt with mandatory real-time context
            system_prompt = f"CURRENT DATE: {current_date}\n"
            system_prompt += role_config.get("system_prompt", "")
            
            # Inject tool instructions for relevant roles
            if role_name in ["architect", "coder", "researcher", "reviewer"]:
                system_prompt += "\n\n" + tool_prompt
                
            agent = Agent(
                name=role_name,
                role=role_name.capitalize(),
                provider=self.providers[provider_name],
                system_prompt=system_prompt,
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
        profile: Optional[str] = None,
    ) -> CouncilSession:
        """Run a multi-round debate between agents with profile support"""
        
        session_id = str(uuid.uuid4())[:8]
        
        # Resolve agent names from profile or default
        if not agent_names:
            settings = self.config.get_council_settings()
            if profile and "profiles" in settings and profile in settings["profiles"]:
                agent_names = settings["profiles"][profile]
            else:
                agent_names = settings.get("default_agents", ["architect", "critic", "optimizer"])
        
        agents_to_use = [
            self.agents[name] for name in agent_names if name in self.agents
        ]
        
        session = CouncilSession(id=session_id, query=query, agents=agents_to_use)
        context = query
        
        for round_num in range(rounds):
            session.rounds = round_num + 1
            
            # Query all agents
            responses = await self.query_agents(
                query=query,
                agent_names=agent_names,
                context=context if round_num > 0 else None,
            )
            
            # Collect responses and check for tool usage
            round_responses = {}
            for resp in responses:
                if resp.success:
                    # Check if agent wants to use tools
                    tool_output = self._handle_tool_calls(resp.content)
                    content_with_tools = resp.content
                    if tool_output:
                        content_with_tools += f"\n\n[SYSTEM: Tool Output]\n{tool_output}"
                    
                    round_responses[resp.provider_name] = content_with_tools
                    session.all_responses.append({
                        "round": round_num + 1,
                        "agent": resp.provider_name,
                        "content": content_with_tools,
                        "provider": resp.provider_name,
                        "model": resp.model,
                        "latency_ms": resp.latency_ms,
                        "tokens": self.optimizer.count_tokens(content_with_tools)
                    })
            
            # Build optimized context for next round
            if round_num < rounds - 1:
                context = self._build_debate_context(round_responses, round_num + 1)
        
        # Run synthesis
        synthesis = await self._synthesize(session)
        session.final_synthesis = synthesis
        
        # Calculate total cost
        total_cost = 0
        for resp in session.all_responses:
            tokens = resp.get('tokens', 0)
            # Estimate prompt tokens as roughly 1.5x of the query + context
            prompt_est = self.optimizer.count_tokens(query) + 500 
            total_cost += self.optimizer.estimate_cost(resp.get('model', ''), prompt_est, tokens)

        # Save to persistent storage
        try:
            self.storage.save_session(
                session_id=session.id,
                query=session.query,
                rounds=session.rounds,
                agents=[a.name for a in session.agents],
                all_responses=session.all_responses,
                final_synthesis=session.final_synthesis,
                total_cost=total_cost
            )
        except Exception:
            pass
            
        return session
    
    def _handle_tool_calls(self, content: str) -> str:
        """Parse response for tool calls and execute them"""
        outputs = []
        
        # Match [READ_FILE: path]
        read_matches = re.findall(r"\[READ_FILE:\s*(.*?)\]", content)
        for path in read_matches:
            outputs.append(f"--- Content of {path} ---\n{self.tools.read_file(path.strip())}")
            
        # Match [LIST_FILES: path]
        list_matches = re.findall(r"\[LIST_FILES:\s*(.*?)\]", content)
        for path in list_matches:
            files = self.tools.list_files(path.strip())
            outputs.append(f"--- Files in {path} ---\n" + "\n".join(files))

        # Match [SEARCH: query]
        search_matches = re.findall(r"\[SEARCH:\s*(.*?)\]", content)
        for query in search_matches:
            outputs.append(f"--- Web Search Results ---\n{self.tools.web_search(query.strip())}")

        # Match [EXECUTE: code]
        execute_matches = re.findall(r"\[EXECUTE:\s*(.*?)\]", content, re.DOTALL)
        for code in execute_matches:
            outputs.append(f"--- Code Execution Output ---\n{self.tools.execute_python(code.strip())}")
            
        return "\n\n".join(outputs) if outputs else ""

    def _build_debate_context(
        self,
        responses: Dict[str, str],
        round_num: int,
    ) -> str:
        """Build optimized context from previous round responses with interactive debate instructions"""
        context = f"DEBATE ROUND {round_num + 1} - INTERACTIVE PROTOCOL:\n"
        context += "Here are the initial perspectives from other specialized agents in the council.\n"
        context += "YOUR TASK: \n"
        context += "1. Analyze the responses below through your specific role's lens.\n"
        context += "2. Identify any logical flaws, hallucinations, or missing pieces in their arguments.\n"
        context += "3. Support or challenge their claims with evidence.\n"
        context += "4. Refine your own stance based on this collective intelligence.\n\n"
        
        # Use optimizer to ensure we don't blow the context window
        context += self.optimizer.optimize_context(responses, max_tokens_per_agent=1000)
        
        return context
    
    async def _synthesize(self, session: CouncilSession) -> str:
        """Synthesize all responses into a final recommendation"""
        
        moderator = self.agents.get("moderator")
        if not moderator:
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
            max_tokens=4000,
        )
        
        if response.success:
            return response.content
        
        return self._simple_synthesis(session)
    
    def _build_synthesis_prompt(self, session: CouncilSession) -> str:
        """Build prompt for synthesis with token awareness"""
        prompt = "Based on the following discussion, provide a final recommendation:\n\n"
        prompt += f"Original Query: {session.query}\n\n"
        
        # Use optimizer-style logic to include relevant parts of all responses
        for resp in session.all_responses:
            # Limit each response to ~800 tokens for synthesis
            content = self.optimizer.truncate_to_limit(resp['content'], 800)
            prompt += f"{resp['agent']} (Round {resp['round']}):\n{content}\n\n"
        
        prompt += "\nPlease synthesize these perspectives into a coherent final recommendation."
        return prompt
    
    def _simple_synthesis(self, session: CouncilSession) -> str:
        """Simple synthesis fallback"""
        synthesis = "## Council Summary\n\n"
        synthesis += f"Query: {session.query}\n\n"
        
        by_round = {}
        for resp in session.all_responses:
            round_num = resp["round"]
            if round_num not in by_round:
                by_round[round_num] = []
            by_round[round_num].append(resp)
        
        for round_num, responses in sorted(by_round.items()):
            synthesis += f"### Round {round_num}\n"
            for resp in responses:
                synthesis += f"**{resp['agent']}**: {resp['content'][:300]}...\n"
            synthesis += "\n"
        
        return synthesis
