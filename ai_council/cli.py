#!/usr/bin/env python3
"""
AI Council CLI - Main Entry Point

A multi-agent AI system for collaborative problem solving.
"""

import asyncio
import sys
import warnings
from pathlib import Path

import click

# Silence annoying background warnings during subprocess/async operations
warnings.filterwarnings("ignore", category=ResourceWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_council.core.config import Config
from ai_council.core.council import CouncilCoordinator
from ai_council.ui.tui import CouncilTUI


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """AI Council CLI - Multi-agent AI system for collaborative problem solving."""
    pass


@cli.command()
@click.option(
    "-q", "--query",
    prompt="Your question",
    help="The question to ask the council",
)
@click.option(
    "--agents", "-a",
    multiple=True,
    help="Specific agents to use",
)
@click.option(
    "--profile", "-p",
    help="Preset profile (code, security, research, strategy, full)",
)
@click.option(
    "--debate", "-d",
    is_flag=True,
    help="Enable debate mode (multiple rounds)",
)
@click.option(
    "--rounds", "-r",
    default=2,
    help="Number of debate rounds (default: 2)",
)
@click.option(
    "--simple", "-s",
    is_flag=True,
    help="Simple mode without TUI",
)
@click.option(
    "--config", "-c",
    type=Path,
    default=None,
    help="Path to config file (default: config.json)",
)
def ask(query, agents, profile, debate, rounds, simple, config):
    """Ask the AI council a question."""
    
    # Load configuration
    config_path = config or Path(__file__).parent.parent / "config.json"
    cfg = Config(config_path)
    cfg.load()
    
    if not cfg.is_configured():
        click.echo(
            click.style(
                "Error: No providers configured. Please edit config.json with your API keys.",
                fg="red",
            )
        )
        sys.exit(1)
    
    # Initialize coordinator
    coordinator = CouncilCoordinator(cfg)
    available_agents = coordinator.get_available_agents()
    
    if not available_agents:
        click.echo(
            click.style(
                "Error: No agents available. Check your configuration.",
                fg="red",
            )
        )
        sys.exit(1)
    
    # Parse agent selection
    agent_list = list(agents) if agents else None
    
    # Run the council
    if simple:
        run_simple_mode(coordinator, query, agent_list, profile, debate, rounds)
    else:
        run_tui_mode(coordinator, query, agent_list, profile, debate, rounds)


def run_simple_mode(coordinator, query, agents, profile, debate, rounds):
    """Run in simple text mode"""
    console = CouncilTUI()
    console.show_welcome()
    
    # Run session
    if debate:
        click.echo(click.style("\n🎭 Starting debate mode...\n", fg="yellow"))
    else:
        click.echo(click.style("\n🤖 Querying agents...\n", fg="green"))
        
    session = asyncio.run(coordinator.run_debate(
        query, 
        rounds=rounds if debate else 1, 
        agent_names=agents,
        profile=profile
    ))
    
    # Print all responses
    for resp in session.all_responses:
        console.print_response(
            type('obj', (object,), {
                'provider_name': resp['agent'],
                'model': resp.get('model', 'auto'),
                'content': resp['content'],
                'success': True,
                'error': None,
            })()
        )
    
    # Print synthesis
    if session.final_synthesis:
        console.print_synthesis(session.final_synthesis)


def run_tui_mode(coordinator, query, agents, profile, debate, rounds):
    """Run with Rich TUI"""
    console = CouncilTUI()
    console.show_welcome()
    
    # Run session (even if 1 round to trigger storage)
    if debate:
        click.echo(click.style("\n🎭 Starting debate mode...\n", fg="yellow"))
    else:
        click.echo(click.style("\n🚀 Initializing Rich Council Session...\n", fg="cyan"))
        
    session = asyncio.run(coordinator.run_debate(
        query=query, 
        rounds=rounds if debate else 1, 
        agent_names=agents,
        profile=profile
    ))
    
    # Show live updating results
    asyncio.run(console.run_live_session(session))


@cli.command()
@click.option(
    "--config", "-c",
    type=Path,
    default=None,
    help="Path to config file",
)
def setup(config):
    """Interactive setup wizard for configuration."""
    
    config_path = config or Path(__file__).parent.parent / "config.json"
    
    click.echo(click.style("\n🔧 AI Council Setup Wizard\n", fg="cyan", bold=True))
    click.echo(f"Config file: {config_path}\n")
    
    # Check if config exists
    if config_path.exists():
        click.echo(click.style("✓ Config file exists", fg="green"))
    else:
        click.echo(click.style("✗ Config file not found", fg="red"))
        click.echo("Creating from template...\n")
        
        # Copy from example
        example_path = Path(__file__).parent.parent / "config.example.json"
        if example_path.exists():
            import shutil
            shutil.copy(example_path, config_path)
            click.echo(click.style("✓ Config created from template", fg="green"))
        else:
            click.echo(click.style("✗ Template not found", fg="red"))
            sys.exit(1)
    
    # Load and check configuration
    cfg = Config(config_path)
    cfg.load()
    
    api_providers = cfg.get_enabled_api_providers()
    cli_providers = cfg.get_enabled_cli_providers()
    
    click.echo(f"\n📊 Configuration Summary:")
    click.echo(f"  API Providers enabled: {len(api_providers)}")
    click.echo(f"  CLI Providers enabled: {len(cli_providers)}")
    
    if api_providers:
        click.echo("\n  API Providers:")
        for name in api_providers:
            has_key = bool(api_providers[name].get("api_key"))
            status = "✓" if has_key else "✗"
            click.echo(f"    {status} {name}")
    
    if cli_providers:
        click.echo("\n  CLI Providers:")
        for name in cli_providers:
            click.echo(f"    • {name} ({cli_providers[name].get('command', name)})")
    
    click.echo("\n💡 Tip: Set API keys via environment variables or edit config.json")
    click.echo("   Environment variables: OPENROUTER_API_KEY, GROQ_API_KEY, etc.\n")


@cli.command()
def agents():
    """List available agents and their roles."""
    
    cfg = Config()
    cfg.load()
    
    coordinator = CouncilCoordinator(cfg)
    
    click.echo(click.style("\n🤖 Available Agents\n", fg="cyan", bold=True))
    
    for name, agent in coordinator.agents.items():
        click.echo(f"\n  {click.style(name.upper(), fg='yellow', bold=True)}")
        click.echo(f"  Provider: {agent.provider.name}")
        click.echo(f"  Temperature: {agent.temperature}")
        click.echo(f"  Role: {agent.role}")


@cli.command()
@click.option(
    "--query", "-q",
    default="What is the best practice for error handling in Python?",
    help="Test query",
)
def test(query):
    """Run a quick test to verify configuration."""
    
    click.echo(click.style("\n🧪 Running AI Council Test\n", fg="cyan", bold=True))
    
    cfg = Config()
    cfg.load()
    
    if not cfg.is_configured():
        click.echo(click.style("✗ No providers configured", fg="red"))
        sys.exit(1)
    
    click.echo(click.style("✓ Configuration loaded", fg="green"))
    
    coordinator = CouncilCoordinator(cfg)
    available = coordinator.get_available_agents()
    
    if not available:
        click.echo(click.style("✗ No agents available", fg="red"))
        sys.exit(1)
    
    click.echo(click.style(f"✓ {len(available)} agents available: {', '.join(available)}", fg="green"))
    
    # Run a quick query
    click.echo(f"\n📝 Test query: {query}\n")
    
    try:
        # Test all available agents
        responses = asyncio.run(coordinator.query_agents(query, agent_names=available))
        
        success_count = sum(1 for r in responses if r.success)
        click.echo(click.style(f"✓ {success_count}/{len(responses)} responses received", fg="green" if success_count == len(responses) else "yellow"))
        
        for resp in responses:
            if resp.success:
                click.echo(f"\n  {click.style('✓', fg='green')} {resp.provider_name}:")
                click.echo(f"    {resp.content[:100].replace('\n', ' ')}...")
            else:
                click.echo(f"\n  {click.style('✗', fg='red')} {resp.provider_name}: {resp.error}")
        
        if success_count > 0:
            click.echo(click.style("\n✓ Test completed!\n", fg="green", bold=True))
        else:
            click.echo(click.style("\n✗ All agents failed!\n", fg="red", bold=True))
            sys.exit(1)
    
    except Exception as e:
        click.echo(click.style(f"✗ Test failed: {e}\n", fg="red"))
        sys.exit(1)


@cli.command()
@click.option("--limit", "-l", default=10, help="Number of sessions to show")
def history(limit):
    """View session history"""
    from .core.config import Config
    from .core.council import CouncilCoordinator
    
    config = Config()
    coordinator = CouncilCoordinator(config)
    
    sessions = coordinator.storage.get_history(limit)
    
    if not sessions:
        click.echo("No session history found.")
        return
    
    click.echo("\n📜 AI Council Session History\n")
    
    from rich.table import Table
    from rich.console import Console
    
    table = Table(title="Recent Sessions")
    table.add_column("ID", style="cyan")
    table.add_column("Date", style="green")
    table.add_column("Query", style="white", overflow="fold")
    table.add_column("Rounds", style="magenta")
    table.add_column("Cost (USD)", style="yellow")
    
    for s in sessions:
        table.add_row(
            s["id"],
            s["timestamp"],
            s["query"][:50] + "..." if len(s["query"]) > 50 else s["query"],
            str(s["rounds"]),
            f"${s.get('total_cost', 0):.4f}"
        )
    
    Console().print(table)
    click.echo("\nUse 'view <id>' to see details (coming soon)\n")


@cli.command()
@click.argument("session_id")
def view(session_id):
    """View details of a specific session"""
    from .core.config import Config
    from .core.council import CouncilCoordinator
    
    config = Config()
    coordinator = CouncilCoordinator(config)
    
    session = coordinator.storage.get_session_details(session_id)
    
    if not session:
        click.echo(f"Session {session_id} not found.")
        return
    
    from rich.console import Console
    from rich.panel import Panel
    from rich.markdown import Markdown
    
    console = Console()
    
    console.print(Panel(
        f"[bold]Query:[/] {session['query']}\n[bold]Total Cost:[/] ${session.get('total_cost', 0):.4f}", 
        title=f"Session {session_id}"
    ))
    
    if session["final_synthesis"]:
        console.print(Panel(Markdown(session["final_synthesis"]), title="Final Synthesis", border_style="green"))
    
    for resp in session["responses"]:
        console.print(Panel(
            resp["content"], 
            title=f"Agent: {resp['agent_name']} (Round {resp['round']})",
            subtitle=f"Model: {resp['model']} | Latency: {resp['latency_ms']:.0f}ms"
        ))


@cli.command()
@click.argument("session_id")
@click.option("--output", "-o", default=None, help="Output file path")
def export(session_id, output):
    """Export a session to a Markdown file"""
    from .core.config import Config
    from .core.council import CouncilCoordinator
    from datetime import datetime
    
    config = Config()
    coordinator = CouncilCoordinator(config)
    
    session = coordinator.storage.get_session_details(session_id)
    
    if not session:
        click.echo(f"Session {session_id} not found.")
        return
    
    # Create export directory
    export_dir = Path("exports")
    export_dir.mkdir(exist_ok=True)
    
    if not output:
        # Generate default filename
        safe_query = "".join([c if c.isalnum() else "_" for c in session["query"][:30]])
        output = export_dir / f"session_{session_id}_{safe_query}.md"
    else:
        output = Path(output)
    
    # Build Markdown content
    md = f"# AI Council Session Report\n\n"
    md += f"**Session ID:** `{session_id}`  \n"
    md += f"**Date:** {session['timestamp']}  \n"
    md += f"**Rounds:** {session['rounds']}  \n\n"
    
    md += f"## ❓ Original Query\n\n>{session['query']}\n\n"
    
    if session["final_synthesis"]:
        md += f"## 🎯 Final Recommendation\n\n{session['final_synthesis']}\n\n"
    
    md += "## 🎭 Agent Perspectives\n\n"
    
    # Group by agent
    responses_by_agent = {}
    for resp in session["responses"]:
        name = resp["agent_name"]
        if name not in responses_by_agent:
            responses_by_agent[name] = []
        responses_by_agent[name].append(resp)
    
    for agent_name, resps in responses_by_agent.items():
        md += f"### 👤 Agent: {agent_name}\n"
        for r in resps:
            md += f"**Round {r['round']}** (Model: `{r['model']}`)\n\n"
            md += f"{r['content']}\n\n"
        md += "---\n\n"
    
    md += "---\n*Generated by AI Council CLI*"
    
    # Write to file
    with open(output, "w") as f:
        f.write(md)
    
    click.echo(click.style(f"\n✅ Session {session_id} exported to: {output}\n", fg="green", bold=True))


@cli.command()
@click.option("--port", "-p", default=8000, help="Port to run the dashboard on")
@click.option("--no-browser", is_flag=True, help="Don't open browser automatically")
def dashboard(port, no_browser):
    """Launch the Web Dashboard to visualize session history"""
    import uvicorn
    import webbrowser
    import threading
    import time
    
    click.echo(click.style(f"\n🚀 Launching AI Council Dashboard on http://localhost:{port}\n", fg="cyan", bold=True))
    
    def open_browser():
        time.sleep(1.5) # Wait for server to start
        if not no_browser:
            webbrowser.open(f"http://localhost:{port}")
            
    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run server
    try:
        uvicorn.run("ai_council.ui.dashboard.app:app", host="127.0.0.1", port=port, log_level="error")
    except KeyboardInterrupt:
        click.echo("\n👋 Dashboard stopped.")


if __name__ == "__main__":
    cli()
