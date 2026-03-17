#!/usr/bin/env python3
"""
AI Council CLI - Main Entry Point

A multi-agent AI system for collaborative problem solving.
"""

import asyncio
import sys
from pathlib import Path

import click

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
    help="Specific agents to use (default: architect, critic, optimizer)",
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
def ask(query, agents, debate, rounds, simple, config):
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
        run_simple_mode(coordinator, query, agent_list, debate, rounds)
    else:
        run_tui_mode(coordinator, query, agent_list, debate, rounds)


def run_simple_mode(coordinator, query, agents, debate, rounds):
    """Run in simple text mode"""
    console = CouncilTUI()
    console.show_welcome()
    
    # Show available agents
    agent_list = list(coordinator.agents.values())
    console.show_agents(agent_list)
    
    # Print query
    console.print_query(query)
    
    if debate:
        # Run debate mode
        click.echo(click.style("\n🎭 Starting debate mode...\n", fg="yellow"))
        session = asyncio.run(coordinator.run_debate(query, rounds=rounds, agent_names=agents))
        
        # Print all responses
        for resp in session.all_responses:
            console.print_response(
                type('obj', (object,), {
                    'provider_name': resp['agent'],
                    'model': 'auto',
                    'content': resp['content'],
                    'success': True,
                    'error': None,
                })()
            )
        
        # Print synthesis
        if session.final_synthesis:
            console.print_synthesis(session.final_synthesis)
    else:
        # Single query mode
        click.echo(click.style("\n🤖 Querying agents...\n", fg="green"))
        responses = asyncio.run(coordinator.query_agents(query, agent_names=agents))
        
        for resp in responses:
            console.print_response(resp)


def run_tui_mode(coordinator, query, agents, debate, rounds):
    """Run with Rich TUI"""
    console = CouncilTUI()
    console.show_welcome()
    
    # Show available agents
    agent_list = list(coordinator.agents.values())
    console.show_agents(agent_list)
    
    # Print query
    console.print_query(query)
    
    if debate:
        # Run debate mode
        click.echo(click.style("\n🎭 Starting debate mode...\n", fg="yellow"))
        session = asyncio.run(coordinator.run_debate(query, rounds=rounds, agent_names=agents))
        
        # Print synthesis
        if session.final_synthesis:
            console.print_synthesis(session.final_synthesis)
    else:
        # Single query mode
        click.echo(click.style("\n🤖 Querying agents...\n", fg="green"))
        responses = asyncio.run(coordinator.query_agents(query, agent_names=agents))
        
        for resp in responses:
            console.print_response(resp)


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


if __name__ == "__main__":
    cli()
