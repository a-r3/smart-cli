"""Main CLI entry point for Smart CLI."""

import asyncio
import os
import sys

import typer
from rich.console import Console

# Add src directory to Python path for imports
current_dir = os.path.dirname(__file__)
sys.path.insert(0, current_dir)

# Import branding utilities
try:
    from .utils.branding import display_welcome_banner, format_section_header
except ImportError:
    from utils.branding import display_welcome_banner, format_section_header

try:
    from .utils.config import ConfigManager
except ImportError:
    from utils.config import ConfigManager

# Import new modular Smart CLI
try:
    from .smart_cli import SmartCLI
except ImportError:
    from smart_cli import SmartCLI

# Initialize console for rich output
console = Console()

# Create main Typer app for interactive mode only
app = typer.Typer(
    name="smart",
    help="Smart CLI - Interactive AI-powered development assistant.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
)


@app.command("config")
def config_command(
    action: str = typer.Argument(..., help="Configuration action (github-token, api-key, show)"),
    value: str = typer.Argument("", help="Configuration value"),
):
    """🔧 Configure Smart CLI settings"""
    console.print(format_section_header("Smart CLI Configuration", "🔧"))
    config_manager = ConfigManager()

    if action == "github-token":
        if not value:
            console.print("❌ [red]GitHub token tələb olunur: smart config github-token ghp_...[/red]")
            return

        if not (value.startswith("ghp_") or value.startswith("github_pat_")):
            console.print("⚠️ [yellow]GitHub token 'ghp_' və ya 'github_pat_' ilə başlamalıdır[/yellow]")

        config_manager.set_config("github_token", value, secure=True)
        console.print("✅ [green]GitHub token uğurla yadda saxlanıldı![/green]")
        console.print("💡 [blue]GitHub integrasiyası indi işləyəcək[/blue]")

    elif action == "api-key":
        if not value:
            console.print("❌ [red]API key tələb olunur: smart config api-key sk-or-...[/red]")
            return

        if not value.startswith("sk-or-"):
            console.print("⚠️ [yellow]OpenRouter API key 'sk-or-' ilə başlamalıdır[/yellow]")

        config_manager.set_config("openrouter_api_key", value, secure=True)
        console.print("✅ [green]API key uğurla yadda saxlanıldı![/green]")

    elif action == "show":
        from rich.table import Table

        config = config_manager.get_all_config()
        table = Table(title="📊 Smart CLI Konfiqurasiyası")
        table.add_column("Parametr", style="cyan")
        table.add_column("Dəyər", style="white")
        table.add_column("Status", style="yellow")

        # Show important settings (hide sensitive values)
        settings = [
            ("API Key", "***" + str(config.get("openrouter_api_key", "Yoxdur"))[-4:] if config.get("openrouter_api_key") else "Təyin edilməyib", "✅" if config.get("openrouter_api_key") else "❌"),
            ("GitHub Token", "***" + str(config.get("github_token", "Yoxdur"))[-4:] if config.get("github_token") else "Təyin edilməyib", "✅" if config.get("github_token") else "⚠️"),
            ("Default Model", config.get("default_model", "anthropic/claude-3-sonnet-20240229"), "✅"),
            ("Max Tokens", str(config.get("max_tokens", 4000)), "✅"),
        ]

        for param, value, status in settings:
            table.add_row(param, str(value), status)

        console.print(table)

    else:
        console.print(f"❌ [red]Naməlum əmr: {action}[/red]")
        console.print("💡 Mövcud əmrlər: github-token, api-key, show")

@app.command("version")
def version_command():
    """Show Smart CLI version information."""
    show_version()


def show_version():
    """Show Smart CLI version information."""
    from rich.table import Table

    table = Table(title="Smart CLI Version Info")
    table.add_column("Field", style="bold blue")
    table.add_column("Value", style="green")

    table.add_row("Version", "1.0.0")
    table.add_row("Description", "Interactive AI Assistant")
    table.add_row(
        "Python Version",
        f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
    )

    console.print(table)


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-v", help="Show version info"),
    debug: bool = typer.Option(False, "--debug", help="Enable debug mode"),
):
    """Run Smart CLI or start the interactive assistant."""
    if version:
        show_version()
        return

    if ctx.invoked_subcommand is None:
        display_welcome_banner(console, compact=False)
        asyncio.run(start_interactive_cli(debug=debug))

async def start_interactive_cli(debug: bool = False):
    """Start the interactive Smart CLI session."""
    try:
        smart_cli = SmartCLI(debug=debug)
        await smart_cli.start()
    except KeyboardInterrupt:
        console.print("\\n👋 [yellow]Goodbye![/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Error starting Smart CLI: {e}[/red]")

if __name__ == "__main__":
    app()
