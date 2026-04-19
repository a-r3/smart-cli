"""Tests for the current Smart CLI command surface."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

from src.cli import app
from src.smart_cli import SmartCLI


class TestMainCLI:
    """Test the supported Smart CLI commands."""

    def test_cli_help(self, cli_runner):
        """Help output should reflect the current CLI contract."""
        result = cli_runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Smart CLI" in result.stdout
        assert "Interactive AI-powered development assistant" in result.stdout
        assert "config" in result.stdout
        assert "version" in result.stdout

    def test_version_option(self, cli_runner):
        """The global version flag should render version information."""
        result = cli_runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "Version" in result.stdout
        assert "1.0.0" in result.stdout

    def test_version_command(self, cli_runner):
        """The explicit version command should work."""
        result = cli_runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "Version" in result.stdout
        assert "1.0.0" in result.stdout

    def test_config_show_command(self, cli_runner):
        """Config show should render the configuration table."""
        mock_config = Mock()
        mock_config.get_all_config.return_value = {
            "openrouter_api_key": "sk-or-test1234",
            "github_token": "ghp_test1234",
            "default_model": "test-model",
            "max_tokens": 2048,
        }

        with patch("src.cli.ConfigManager", return_value=mock_config):
            result = cli_runner.invoke(app, ["config", "show"])

        assert result.exit_code == 0
        assert "Konfiquras" in result.stdout
        assert "test-model" in result.stdout
        mock_config.get_all_config.assert_called_once()

    def test_config_api_key_command(self, cli_runner):
        """Config api-key should write the secure config value."""
        mock_config = Mock()

        with patch("src.cli.ConfigManager", return_value=mock_config):
            result = cli_runner.invoke(app, ["config", "api-key", "sk-or-test-key"])

        assert result.exit_code == 0
        mock_config.set_config.assert_called_once_with(
            "openrouter_api_key", "sk-or-test-key", secure=True
        )

    def test_invalid_command(self, cli_runner):
        """Unknown commands should fail."""
        result = cli_runner.invoke(app, ["invalid-command"])

        assert result.exit_code != 0


class TestInteractiveStartup:
    """Test startup behavior when no explicit subcommand is provided."""

    def test_no_args_starts_interactive_cli(self, cli_runner):
        """Running without arguments should enter the interactive flow."""
        with patch("src.cli.display_welcome_banner") as mock_banner:
            with patch("src.cli.start_interactive_cli", new=AsyncMock()) as mock_start:
                result = cli_runner.invoke(app, [])

        assert result.exit_code == 0
        mock_banner.assert_called_once()
        mock_start.assert_awaited_once_with(debug=False)


class TestSmartCLIStartupGuards:
    """Test startup safeguards for the interactive assistant."""

    def test_start_requires_ai_configuration(self):
        """Interactive startup should stop early when no AI client is available."""
        smart_cli = SmartCLI(debug=False)
        smart_cli.initialize = AsyncMock(return_value=True)
        smart_cli.ai_client = None
        smart_cli.session_manager = Mock()

        with patch("src.smart_cli.console.print") as mock_print:
            asyncio.run(smart_cli.start())

        smart_cli.session_manager.start_session.assert_not_called()
        rendered = " ".join(str(call.args[0]) for call in mock_print.call_args_list)
        assert "No AI provider is configured." in rendered

    def test_start_stops_when_initialize_fails(self):
        """Startup should stop before opening a session if initialization fails."""
        smart_cli = SmartCLI(debug=False)
        smart_cli.initialize = AsyncMock(return_value=False)
        smart_cli.session_manager = Mock()
        smart_cli.interactive_loop = AsyncMock()

        asyncio.run(smart_cli.start())

        smart_cli.session_manager.start_session.assert_not_called()
        smart_cli.interactive_loop.assert_not_awaited()

    def test_start_runs_session_and_loop_when_ai_client_exists(self):
        """Startup should open a session and enter the interactive loop."""
        smart_cli = SmartCLI(debug=False)
        smart_cli.initialize = AsyncMock(return_value=True)
        smart_cli.ai_client = Mock()
        smart_cli.session_manager = Mock()
        smart_cli.session_manager.start_session = AsyncMock()
        smart_cli.interactive_loop = AsyncMock()

        asyncio.run(smart_cli.start())

        smart_cli.session_manager.start_session.assert_awaited_once()
        smart_cli.interactive_loop.assert_awaited_once()

    def test_shutdown_closes_resources(self):
        """Shutdown should close the AI session and end the active session."""
        smart_cli = SmartCLI(debug=False)
        smart_cli.session_manager = Mock()
        smart_cli.session_manager.session_active = True
        smart_cli.session_manager.end_session = AsyncMock()
        smart_cli.ai_client = Mock()
        smart_cli.ai_client.close_session = AsyncMock()

        asyncio.run(smart_cli.shutdown())

        smart_cli.session_manager.end_session.assert_awaited_once()
        smart_cli.ai_client.close_session.assert_awaited_once()
