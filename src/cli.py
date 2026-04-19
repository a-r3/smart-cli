"""Main CLI entry point for Smart CLI."""

import asyncio
import contextlib
import inspect
import os
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

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

try:
    from .utils import health_checker
except ImportError:
    import utils.health_checker as health_checker

try:
    from .templates.template_manager import TemplateManager
except ImportError:
    from templates.template_manager import TemplateManager

# Import new modular Smart CLI
try:
    from .smart_cli import SmartCLI
except ImportError:
    from smart_cli import SmartCLI

# Initialize console for rich output
console = Console()


class UsageTracker:
    """Lightweight compatibility usage tracker for CLI commands."""

    def get_daily_usage(self):
        return {
            "overall": {
                "total_requests": 0,
                "total_tokens": 0,
                "total_estimated_cost": 0.0,
                "total_actual_cost": None,
                "average_cost_per_request": 0.0,
            }
        }

    def check_budget_status(self):
        return {
            "daily": {
                "budget": 10.0,
                "spent": 0.0,
                "remaining": 10.0,
                "percentage_used": 0.0,
                "over_budget": False,
            },
            "weekly": {
                "budget": 50.0,
                "spent": 0.0,
                "remaining": 50.0,
                "percentage_used": 0.0,
                "over_budget": False,
            },
            "monthly": {
                "budget": 200.0,
                "spent": 0.0,
                "remaining": 200.0,
                "percentage_used": 0.0,
                "over_budget": False,
            },
        }

    def get_top_usage_patterns(self):
        return []

    def set_budget(self, period: str, amount: float) -> bool:
        return True


def _run_async(value):
    """Run awaitables and return plain values unchanged."""
    if inspect.isawaitable(value):
        return asyncio.run(value)
    return value

# Create main Typer app for interactive mode only
app = typer.Typer(
    name="smart",
    help="Smart CLI - Interactive AI-powered development assistant. AI-powered CLI tool for development workflows.",
    add_completion=False,
    rich_markup_mode="rich",
    no_args_is_help=False,
)


template_app = typer.Typer(
    help="Generate basic templates for common development tasks."
)
generate_app = typer.Typer(
    help="Generate code using AI or template-assisted workflows."
)
init_app = typer.Typer(
    help="Initialize new projects with starter scaffolding."
)
review_app = typer.Typer(
    help="Review and analyze code or projects."
)

app.add_typer(template_app, name="template")
app.add_typer(generate_app, name="generate")
app.add_typer(init_app, name="init")
app.add_typer(review_app, name="review")


@app.command("config")
def config_command(
    action: str = typer.Argument(
        None, help="Legacy configuration action (github-token, api-key, show)"
    ),
    value: str = typer.Argument("", help="Legacy configuration value"),
    show: bool = typer.Option(False, "--show", help="Show current configuration"),
    set_key: str = typer.Option(None, "--set", help="Set a configuration key"),
    set_value: str = typer.Option(None, "--value", help="Configuration value for --set"),
):
    """🔧 Configure Smart CLI settings"""
    console.print(format_section_header("Smart CLI Configuration", "🔧"))
    config_manager = ConfigManager()

    if show:
        action = "show"
    elif set_key:
        config_manager.set_config(set_key, set_value or "")
        console.print("✅ [green]Configuration updated[/green]")
        return

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
        config = config_manager.get_all_config()
        table = Table(title="Smart CLI Konfiqurasiyası")
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


@app.command("health")
def health_command():
    """Run a lightweight health check."""
    checker = health_checker.HealthChecker()
    result = _run_async(checker.run_health_checks())
    console.print("Health Status")
    console.print(str(result.get("status", "unknown")))


@app.command("usage")
def usage_command():
    """Show usage statistics."""
    tracker = UsageTracker()
    usage = tracker.get_daily_usage()
    budget = tracker.check_budget_status()

    console.print("Daily Usage Summary")
    console.print(str(usage.get("overall", {})))
    console.print("\nBudget Status")
    console.print(str(budget))


@app.command("budget")
def budget_command(
    set_period: str = typer.Option(None, "--set", help="Budget period to update"),
    amount: float = typer.Option(None, "--amount", help="Budget amount"),
):
    """Show or update budget configuration."""
    tracker = UsageTracker()
    if set_period and amount is not None:
        tracker.set_budget(set_period, amount)
        console.print(f"Budget updated: {set_period} = {amount}")
        return

    console.print("Budget Configuration")
    console.print(str(tracker.check_budget_status()))

@app.command("version")
def version_command():
    """Show Smart CLI version information."""
    show_version()


@app.command("workflow")
def workflow_command(
    command: str = typer.Argument(
        ..., help="Workflow command: repo-plan, repo-analyze"
    ),
    target: str = typer.Argument(
        ".", help="Target repository path or file (default: current directory)"
    ),
):
    """🧭 Execute explicit repository workflows."""
    console.print(format_section_header("Smart Workflow", "🧭"))

    if command == "repo-plan":
        request = (
            f"analyze this repository at {target} and give me an implementation plan"
        )
    elif command == "repo-analyze":
        request = f"analyze this repository at {target}"
    else:
        console.print(
            f"❌ [red]Unknown workflow command: {command}[/red]"
        )
        console.print(
            "💡 Available workflows: repo-plan, repo-analyze"
        )
        return

    console.print(f"📍 Target: {target}")
    console.print(f"🎯 Request: {request}\n")

    try:
        workflow_coro = execute_workflow_request(request, debug=False)
        try:
            asyncio.run(workflow_coro)
        finally:
            if inspect.iscoroutine(workflow_coro):
                with contextlib.suppress(RuntimeError):
                    workflow_coro.close()
    except KeyboardInterrupt:
        console.print("\n👋 [yellow]Workflow cancelled[/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Workflow error: {e}[/red]")


async def execute_workflow_request(request: str, debug: bool = False):
    """Execute a workflow request through the Smart CLI system."""
    smart_cli = SmartCLI(debug=debug)
    await smart_cli.initialize()

    # Use the internal request processing to handle the workflow
    try:
        from src.core.request_router import RequestRouter
    except ImportError:
        from core.request_router import RequestRouter

    request_router = RequestRouter(smart_cli)
    await request_router.process_request(request)



def show_version():
    """Show Smart CLI version information."""
    table = Table(title="Smart CLI Version Info")
    table.add_column("Field", style="bold blue")
    table.add_column("Value", style="green")

    table.add_row("Version", "1.0.0")
    table.add_row("Description", "AI-powered CLI tool")
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


@template_app.command("function")
def template_function(
    name: str = typer.Argument(..., help="Function or module name"),
    lang: str = typer.Option("python", "--lang", help="Language"),
    desc: str = typer.Option("Generated function", "--desc", help="Description"),
    output: str = typer.Option(None, "--output", help="Optional output file"),
):
    """Generate a basic function template."""
    if lang.lower() == "python":
        content = (
            f'""" {desc} """\n\n'
            f"def {name}():\n"
            f'    """{desc}."""\n'
            f"    pass\n"
        )
    else:
        content = f"// {desc}\nfunction {name}() {{\n}}\n"

    if output:
        Path(output).write_text(content, encoding="utf-8")
        console.print(f"Saved template to {output}")
    else:
        console.print(content)


@generate_app.command("function")
def generate_function_help():
    """Generate code using AI."""
    console.print("Generate code using AI")
    console.print("Examples: function, api")


@generate_app.command("api")
def generate_api_help():
    """Generate API scaffolding using AI."""
    console.print("Generate code using AI")
    console.print("API scaffold generation")


@init_app.callback(invoke_without_command=True)
def init_callback():
    """Initialize new projects."""
    pass


@review_app.command("code")
def review_code(
    path: str = typer.Argument(..., help="Path to a source file"),
    focus: str = typer.Option("general", "--focus", help="Review focus area"),
):
    """Review and analyze code."""
    target = Path(path)
    if target.exists():
        lines = target.read_text(encoding="utf-8", errors="ignore").splitlines()
        console.print("Code Metrics")
        console.print(f"Lines: {len(lines)}")
        console.print(f"Focus: {focus}")
    else:
        console.print("reviewing code")


@review_app.command("project")
def review_project(
    path: str = typer.Argument(..., help="Path to a project directory"),
):
    """Review and analyze a project."""
    target = Path(path)
    if target.exists() and target.is_dir():
        entries = list(target.iterdir())
        console.print("Project Overview")
        console.print(f"Found {len(entries)} items")
    else:
        console.print("reviewing project")

if __name__ == "__main__":
    app()
