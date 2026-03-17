"""
Rich TUI Interface for AI Council
"""

import asyncio
from typing import Optional

from rich import box
from rich.console import Console
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.spinner import Spinner
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text
from rich.markdown import Markdown

from ..core.council import CouncilSession, Agent
from ..providers.base import ProviderResponse


class CouncilTUI:
    """Rich TUI for AI Council"""
    
    def __init__(self):
        self.console = Console()
        self.layout = Layout()
        self._current_status = "Initializing..."
        self._responses = []
        self._session: Optional[CouncilSession] = None
    
    def create_layout(self) -> Layout:
        """Create the main layout"""
        self.layout = Layout()
        
        self.layout.split(
            Layout(name="header", size=3),
            Layout(name="body"),
            Layout(name="footer", size=3),
        )
        
        self.layout["body"].split_row(
            Layout(name="left", ratio=2),
            Layout(name="right", ratio=3),
        )
        
        self.layout["left"].split(
            Layout(name="status", size=5),
            Layout(name="responses"),
        )
        
        self.layout["right"].split(
            Layout(name="synthesis"),
        )
        
        return self.layout
    
    def update_header(self, title: str = "AI Council CLI"):
        """Update header panel"""
        header = Panel(
            Text(title, justify="center", style="bold cyan"),
            border_style="blue",
        )
        self.layout["header"].update(header)
    
    def update_footer(self, status: str = ""):
        """Update footer panel"""
        footer_text = f"AI Council | {status}" if status else "AI Council"
        footer = Panel(
            Text(footer_text, justify="right", style="dim"),
            border_style="blue",
        )
        self.layout["footer"].update(footer)
    
    def update_status(self, status: str, spinner: bool = True):
        """Update status panel"""
        if spinner:
            content = Spinner("dots", text=status, style="green")
        else:
            content = Text(status, style="green")
        
        self.layout["status"].update(Panel(content, title="Status", border_style="green"))
    
    def update_responses(self, responses: list):
        """Update responses panel"""
        content = ""
        for resp in responses:
            agent_style = {
                "architect": "bold blue",
                "critic": "bold red",
                "optimizer": "bold green",
                "researcher": "bold yellow",
                "generalist": "bold magenta",
                "moderator": "bold cyan",
            }.get(resp.get("agent", ""), "bold white")
            
            content += f"[{agent_style}]{resp.get('agent', 'Unknown')}[/]\n"
            content += f"{resp.get('content', '')[:3000]}\n\n"
            content += "─" * 50 + "\n"
        
        self.layout["responses"].update(
            Panel(
                content,
                title="Agent Responses",
                border_style="blue",
            )
        )
    
    def update_synthesis(self, synthesis: str):
        """Update synthesis panel"""
        self.layout["synthesis"].update(
            Panel(
                Markdown(synthesis),
                title="Final Synthesis",
                border_style="cyan",
            )
        )
    
    def make_agents_table(self, agents: list) -> Table:
        """Create a table of available agents"""
        table = Table(title="Available Agents", box=box.ROUNDED)
        table.add_column("Agent", style="cyan")
        table.add_column("Provider", style="green")
        table.add_column("Status", style="yellow")
        
        for agent in agents:
            table.add_row(
                agent.name,
                agent.provider.name,
                "[green]Ready[/]" if agent.provider.is_available() else "[red]Unavailable[/]",
            )
        
        return table
    
    def show_welcome(self):
        """Show welcome screen"""
        self.console.clear()
        self.console.print(
            Panel(
                Text(
                    """
 █████╗ ██╗██████╗ ██████╗ ██╗   ██╗████████╗███████╗
██╔══██╗██║██╔══██╗██╔══██╗╚██╗ ██╔╝╚══██╔══╝██╔════╝
███████║██║██████╔╝██████╔╝ ╚████╔╝    ██║   █████╗  
██╔══██║██║██╔══██╗██╔══██╗  ╚██╔╝     ██║   ██╔══╝  
██║  ██║██║██║  ██║██████╔╝   ██║      ██║   ███████╗
╚═╝  ╚═╝╚═╝╚═╝  ╚═╝╚═════╝    ╚═╝      ╚═╝   ╚══════╝
                    Council CLI
""",
                    justify="center",
                    style="bold cyan",
                ),
                border_style="blue",
            )
        )
    
    def show_agents(self, agents: list):
        """Show available agents"""
        table = self.make_agents_table(agents)
        self.console.print(table)
    
    def print_query(self, query: str):
        """Print user query"""
        self.console.print(
            Panel(
                Markdown(f"**Query:** {query}"),
                border_style="yellow",
                title="Your Question",
            )
        )
    
    def print_response(self, response: ProviderResponse):
        """Print a single agent response"""
        if response.success:
            self.console.print(
                Panel(
                    Markdown(f"**{response.provider_name}** ({response.model})\n\n{response.content}"),
                    border_style="green",
                    title=f"✓ {response.provider_name}",
                )
            )
        else:
            self.console.print(
                Panel(
                    f"**{response.provider_name}** failed: {response.error}",
                    border_style="red",
                    title=f"✗ {response.provider_name}",
                )
            )
    
    def print_synthesis(self, synthesis: str):
        """Print final synthesis"""
        self.console.print(
            Panel(
                Markdown(synthesis),
                border_style="cyan",
                title="🎯 Final Synthesis",
            )
        )
    
    async def run_live_session(self, session: CouncilSession):
        """Run a live updating session"""
        self.create_layout()
        self.update_header("AI Council - Live Session")
        
        with Live(self.layout, console=self.console, refresh_per_second=4) as live:
            # Initial display
            self.update_status("Starting council discussion...")
            self.update_footer(f"Query: {session.query[:50]}...")
            
            # Simulate live updates (in real implementation, this would stream)
            for i in range(len(session.all_responses)):
                self.update_status(f"Processing response {i + 1}/{len(session.all_responses)}...")
                
                # Update responses
                current_responses = []
                for j in range(i + 1):
                    resp = session.all_responses[j]
                    current_responses.append({
                        "agent": resp["agent"],
                        "content": resp["content"],
                    })
                
                self.update_responses(current_responses)
                await asyncio.sleep(0.5)
            
            # Show synthesis
            self.update_status("Synthesizing final recommendation...", spinner=False)
            if session.final_synthesis:
                self.update_synthesis(session.final_synthesis)
            
            self.update_footer("Session complete")
            await asyncio.sleep(2)
