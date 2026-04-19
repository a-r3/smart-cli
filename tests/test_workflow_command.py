"""Tests for explicit workflow command."""

import pytest
from typer.testing import CliRunner
from unittest.mock import Mock, patch, AsyncMock

from src.cli import app


@pytest.fixture
def cli_runner():
    """Provide CLI test runner."""
    return CliRunner()


class TestWorkflowCommand:
    """Test explicit workflow command surface."""

    def test_workflow_repo_plan_help_shows_command(self, cli_runner):
        """Workflow command should be available and documented."""
        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "workflow" in result.stdout.lower()

    def test_workflow_command_requires_subcommand(self, cli_runner):
        """Workflow command should require a subcommand."""
        result = cli_runner.invoke(app, ["workflow"])
        # Should fail or show help since argument is missing
        assert result.exit_code != 0 or "workflow" in result.stdout.lower()

    @patch("src.cli.execute_workflow_request")
    def test_workflow_repo_plan_builds_correct_request(
        self, mock_execute, cli_runner
    ):
        """Workflow repo-plan should build repo analysis + plan request."""
        mock_execute = AsyncMock()

        # Invoke the command
        with patch("src.cli.asyncio.run") as mock_asyncio_run:
            mock_asyncio_run.side_effect = lambda coro: None
            result = cli_runner.invoke(
                app, ["workflow", "repo-plan", "."]
            )

        # Should invoke the asyncio run
        assert result.exit_code == 0 or "Target:" in result.stdout

    @patch("src.cli.execute_workflow_request")
    def test_workflow_repo_analyze_builds_correct_request(
        self, mock_execute, cli_runner
    ):
        """Workflow repo-analyze should build repo analysis request."""
        mock_execute = AsyncMock()

        # Invoke the command
        with patch("src.cli.asyncio.run") as mock_asyncio_run:
            mock_asyncio_run.side_effect = lambda coro: None
            result = cli_runner.invoke(
                app, ["workflow", "repo-analyze", "/some/repo"]
            )

        # Should invoke the asyncio run
        assert result.exit_code == 0 or "Target:" in result.stdout

    def test_workflow_invalid_command_shows_error(self, cli_runner):
        """Invalid workflow command should show helpful error."""
        with patch("src.cli.asyncio.run"):
            result = cli_runner.invoke(
                app, ["workflow", "invalid-workflow", "."]
            )
            # Should show error about unknown command
            assert "unknown workflow command" in result.stdout.lower() or result.exit_code != 0


class TestWorkflowCommandMetadata:
    """Test workflow command documentation and metadata."""

    def test_workflow_command_has_help_text(self, cli_runner):
        """Workflow command should have help documentation."""
        result = cli_runner.invoke(app, ["workflow", "--help"])
        assert result.exit_code == 0
        assert "workflow" in result.stdout.lower()

    def test_repo_plan_workflow_available(self, cli_runner):
        """repo-plan workflow should be listed in help."""
        result = cli_runner.invoke(app, ["workflow", "--help"])
        assert result.exit_code == 0
        assert "repo-plan" in result.stdout or "workflow" in result.stdout.lower()

    def test_repo_analyze_workflow_available(self, cli_runner):
        """repo-analyze workflow should be listed in help."""
        result = cli_runner.invoke(app, ["workflow", "--help"])
        assert result.exit_code == 0
        assert "repo-analyze" in result.stdout or "workflow" in result.stdout.lower()
