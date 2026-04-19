"""Smart CLI Command Handler - Handles special commands and operations."""

import os
import subprocess
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()


class CommandHandler:
    """Handles Smart CLI special commands and operations."""

    def __init__(self, config_manager=None):
        # Accept either a config manager or a legacy SmartCLI instance.
        self.smart_cli = None
        if config_manager is not None and hasattr(config_manager, "config"):
            self.smart_cli = config_manager
            self.config_manager = getattr(config_manager, "config", None)
        else:
            self.config_manager = config_manager
        self.available_commands = {
            "help": "Show available commands",
            "exit": "Exit Smart CLI",
            "quit": "Exit Smart CLI",
            "clear": "Clear screen",
            "version": "Show version information",
            "config": "Configuration management",
            "setup": "Initial setup wizard",
        }

    async def handle_command(self, command: str) -> bool:
        """Handle special commands. Returns False if should exit."""
        parts = command[1:].split(" ", 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""

        if cmd in ["exit", "quit"]:
            return False

        elif cmd == "help":
            await self.display_help()

        elif cmd == "clear":
            os.system("clear" if os.name == "posix" else "cls")

        elif cmd == "version":
            self._display_version_info()

        elif cmd == "config":
            await self.handle_config(args)

        elif cmd == "setup":
            await self.handle_setup()

        else:
            console.print(f"❌ [red]Unknown command: {cmd}[/red]")
            console.print("💡 Type '/help' to see available commands")

        return True

    def _display_version_info(self):
        """Display version information with full ASCII logo."""
        try:
            # Load full ASCII logo
            icon_path = os.path.join(
                os.path.dirname(__file__), "../../smart_full_icon_pack"
            )
            ascii_file = os.path.join(icon_path, "smart_simple_ascii.txt")

            if os.path.exists(ascii_file):
                with open(ascii_file, "r", encoding="utf-8") as f:
                    ascii_logo = f.read()

                version_info = f"""[bold cyan]{ascii_logo}[/bold cyan]

[bold green]Smart CLI v6.0.0[/bold green] • [dim]Enterprise AI Platform[/dim]
[yellow]50+ AI models • Multi-agent system • GitHub integration[/yellow]

[dim]© 2025 Smart CLI Project • MIT License[/dim]"""
            else:
                version_info = "[bold green]Smart CLI v6.0.0[/bold green]\n[white]Enterprise AI Platform[/white]\n[yellow]50+ AI models • Multi-agent system • Azerbaijani support[/yellow]"

            version_panel = Panel(
                version_info,
                title="[bold blue]📋 Version Information[/bold blue]",
                border_style="blue",
                padding=(1, 2),
            )

            console.print(version_panel)

        except Exception as e:
            console.print(f"❌ [red]Failed to load version info: {str(e)}[/red]")

    async def display_help(self):
        """Display help information."""
        console.print("🔧 [bold blue]Smart CLI Commands:[/bold blue]\n")

        # Basic commands
        console.print("📋 [bold green]Basic Commands:[/bold green]")
        for cmd, desc in self.available_commands.items():
            console.print(f"  /{cmd:<10} - {desc}")

        console.print("\n📁 [bold green]File Operations:[/bold green]")
        console.print("  'filename.py oxu'    - Read and analyze file")
        console.print("  'read full file.py'  - Read complete file")
        console.print("  'fix filename.py'    - Fix issues in file")
        console.print("  'improve code.js'    - Improve code quality")

        console.print("\n🤖 [bold green]AI Commands:[/bold green]")
        console.print("  'analyze project'    - Analyze project structure")
        console.print("  'review my code'     - Get code review")
        console.print("  'optimize hello.py'  - Optimize code performance")

        console.print(
            "\n💡 [dim]Tip: Smart CLI understands natural language - just ask![/dim]"
        )

    async def handle_config(self, args: str):
        """Handle configuration commands."""
        if not self.config_manager:
            console.print("❌ [red]Configuration manager not available[/red]")
            return

        if not args:
            self._show_config_help()
            return

        parts = args.split(" ", 1)
        action = parts[0].lower()
        value = parts[1] if len(parts) > 1 else ""

        if action == "show":
            await self._show_config()
        elif action == "api-key":
            await self._set_api_key(value)
        elif action == "github-token":
            await self._set_github_token(value)
        elif action == "model":
            await self._set_model(value)
        elif action == "models":
            await self._show_available_models()
        elif action == "reset":
            await self._reset_config()
        else:
            self._show_config_help()

    def _show_config_help(self):
        """Show configuration help."""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Əmr", style="cyan", width=25)
        table.add_column("Təsvir", style="white")

        commands = [
            ("/config show", "Cari konfiqurasiyani göstər"),
            ("/config api-key <key>", "OpenRouter API key təyin et"),
            ("/config github-token <token>", "GitHub token təyin et"),
            ("/config model <model>", "Default AI modeli dəyiş"),
            ("/config models", "Mövcud AI modellərini göstər"),
            ("/config reset", "Konfiqurasiyani sıfırla"),
        ]

        for cmd, desc in commands:
            table.add_row(cmd, desc)

        console.print(
            Panel(table, title="⚙️ Konfiqurasiya Əmrləri", border_style="blue")
        )

    async def _show_config(self):
        """Show current configuration."""
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Parametr", style="cyan", width=20)
        table.add_column("Dəyər", style="white")
        table.add_column("Status", style="yellow", width=10)

        # Get current config
        config = self.config_manager.get_all_config()

        # Show important settings (hide sensitive values)
        settings = [
            (
                "API Key",
                (
                    "***" + str(config.get("openrouter_api_key", "Yoxdur"))[-4:]
                    if config.get("openrouter_api_key")
                    else "Təyin edilməyib"
                ),
                "✅" if config.get("openrouter_api_key") else "❌",
            ),
            (
                "GitHub Token",
                (
                    "***" + str(config.get("github_token", "Yoxdur"))[-4:]
                    if config.get("github_token")
                    else "Təyin edilməyib"
                ),
                "✅" if config.get("github_token") else "⚠️",
            ),
            (
                "Default Model",
                config.get("default_model", "anthropic/claude-3-sonnet-20240229"),
                "✅",
            ),
            ("Max Tokens", str(config.get("max_tokens", 4000)), "✅"),
            ("Temperature", str(config.get("temperature", 0.7)), "✅"),
            ("Log Level", config.get("log_level", "INFO"), "✅"),
        ]

        for param, value, status in settings:
            table.add_row(param, str(value), status)

        console.print(
            Panel(table, title="📊 Smart CLI Konfiqurasiyası", border_style="green")
        )

        # Show config file location
        config_dir = Path.home() / ".smart-cli"
        console.print(f"\n📁 [dim]Konfiqurasiya faylları: {config_dir}[/dim]")

    async def _set_api_key(self, api_key: str):
        """Set OpenRouter API key."""
        if not api_key:
            console.print("❌ [red]API key daxil edin: /config api-key sk-or-...[/red]")
            return

        # Validate API key format
        if not api_key.startswith("sk-or-"):
            console.print("⚠️ [yellow]API key 'sk-or-' ilə başlamalıdır[/yellow]")

        self.config_manager.set_config("openrouter_api_key", api_key, secure=True)
        console.print("✅ [green]API key uğurla yadda saxlanıldı![/green]")
        console.print(
            "💡 [blue]Yenidən başlatmaq lazım deyil - dərhal işləyəcək[/blue]"
        )

    async def _set_github_token(self, token: str):
        """Set GitHub token."""
        if not token:
            console.print(
                "❌ [red]GitHub token daxil edin: /config github-token ghp_...[/red]"
            )
            console.print(
                "💡 [blue]GitHub token almaq üçün: Settings → Developer settings → Personal access tokens[/blue]"
            )
            return

        # Validate token format
        if not (token.startswith("ghp_") or token.startswith("github_pat_")):
            console.print(
                "⚠️ [yellow]GitHub token 'ghp_' və ya 'github_pat_' ilə başlamalıdır[/yellow]"
            )

        self.config_manager.set_config("github_token", token, secure=True)
        console.print("✅ [green]GitHub token uğurla yadda saxlanıldı![/green]")
        console.print("💡 [blue]GitHub inteqrasiyası indi işləyəcək[/blue]")

    async def _set_model(self, model: str):
        """Set default AI model."""
        if not model:
            console.print(
                "❌ [red]Model adı daxil edin: /config model anthropic/claude-3-sonnet-20240229[/red]"
            )
            console.print(
                "💡 [blue]Mövcud modelləri görmək üçün: /config models[/blue]"
            )
            return

        # List of popular models for validation
        popular_models = [
            "anthropic/claude-3-sonnet-20240229",
            "anthropic/claude-3-haiku-20240307",
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo",
            "google/gemini-pro",
            "meta-llama/llama-3-70b-instruct",
            "mistralai/mistral-large",
        ]

        if model not in popular_models:
            console.print(
                f"⚠️ [yellow]Model '{model}' tanınmır, amma yenə də təyin ediləcək[/yellow]"
            )

        self.config_manager.set_config("default_model", model)
        console.print(f"✅ [green]Default model '{model}' olaraq təyin edildi![/green]")

    async def _show_available_models(self):
        """Show available AI models."""
        table = Table(show_header=True, header_style="bold blue")
        table.add_column("Model", style="cyan", width=35)
        table.add_column("Provider", style="green", width=12)
        table.add_column("Xüsusiyyət", style="white")

        models = [
            (
                "anthropic/claude-3-sonnet-20240229",
                "Anthropic",
                "Ən yaxşı balans (tövsiyə)",
            ),
            ("anthropic/claude-3-haiku-20240307", "Anthropic", "Sürətli və qənaətli"),
            ("openai/gpt-4-turbo", "OpenAI", "Güclü reasoning"),
            ("openai/gpt-3.5-turbo", "OpenAI", "Sürətli və ucuz"),
            ("google/gemini-pro", "Google", "Multimodal dəstək"),
            ("meta-llama/llama-3-70b-instruct", "Meta", "Open source"),
            ("mistralai/mistral-large", "Mistral", "Avropa modeli"),
            ("cohere/command-r-plus", "Cohere", "RAG optimallaşdırılmış"),
        ]

        for model, provider, feature in models:
            table.add_row(model, provider, feature)

        console.print(Panel(table, title="🤖 Mövcud AI Modelləri", border_style="blue"))
        console.print("💡 [blue]Model dəyişmək üçün: /config model <model_name>[/blue]")

    async def _reset_config(self):
        """Reset configuration."""
        console.print(
            "⚠️ [yellow]Konfiqurasiyani sıfırlamaq istədiyinizə əminsiniz? (y/n)[/yellow]"
        )
        # Bu real tətbiqdə input alınacaq
        console.print(
            "💡 [blue]Təhlükəsizlik üçün manual olaraq silin: ~/.smart-cli/[/blue]"
        )

    async def handle_setup(self):
        """Handle initial setup wizard."""
        console.print("🚀 [bold blue]Smart CLI İlkin Quraşdırma[/bold blue]\n")

        # Check current configuration
        config = self.config_manager.get_all_config() if self.config_manager else {}

        setup_table = Table(show_header=True, header_style="bold green")
        setup_table.add_column("Addım", style="cyan", width=5)
        setup_table.add_column("Təsvir", style="white", width=40)
        setup_table.add_column("Status", style="yellow", width=10)

        steps = [
            (
                "1",
                "OpenRouter API key",
                "✅" if config.get("openrouter_api_key") else "❌",
            ),
            (
                "2",
                "GitHub Token (isteğe bağlı)",
                "✅" if config.get("github_token") else "⚠️",
            ),
            ("3", "Default AI modeli", "✅" if config.get("default_model") else "❌"),
        ]

        for step, desc, status in steps:
            setup_table.add_row(step, desc, status)

        console.print(
            Panel(setup_table, title="📋 Quraşdırma Addımları", border_style="green")
        )

        console.print("\n📝 [bold]Quraşdırma Komandaları:[/bold]")
        console.print(
            "• [cyan]/config api-key sk-or-your-key-here[/cyan] - OpenRouter API key"
        )
        console.print(
            "• [cyan]/config github-token ghp_your-token[/cyan] - GitHub token"
        )
        console.print(
            "• [cyan]/config model anthropic/claude-3-sonnet-20240229[/cyan] - AI model"
        )
        console.print("\n💡 [blue]Ətraflı məlumat: /config show[/blue]")
