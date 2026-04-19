"""Focused tests for public versus experimental mode surface."""

import asyncio
from unittest.mock import Mock

from src.core.enhanced_request_router import EnhancedRequestRouter
from src.core.mode_manager import ModeManager, SmartMode


def make_router():
    """Create a lightweight enhanced router for mode-surface tests."""
    smart_cli = Mock()
    smart_cli.orchestrator = Mock()
    smart_cli.handlers = {}
    smart_cli.command_handler = Mock()
    smart_cli.debug = False
    smart_cli.config = {}
    return EnhancedRequestRouter(smart_cli)


class TestModeSurface:
    """Test the public and experimental mode boundaries."""

    def test_public_and_experimental_modes_are_split(self):
        """Only smart, code, and analysis should be public."""
        manager = ModeManager()

        assert [mode.value for mode in manager.get_public_modes()] == [
            "smart",
            "code",
            "analysis",
        ]
        assert [mode.value for mode in manager.get_experimental_modes()] == [
            "architect",
            "learning",
            "fast",
            "orchestrator",
        ]

    def test_parse_mode_string_defaults_to_smart(self):
        """Unknown mode strings should safely default to smart."""
        assert ModeManager.parse_mode_string("code") == SmartMode.CODE
        assert ModeManager.parse_mode_string("invalid-mode") == SmartMode.SMART

    def test_architecture_suggestions_do_not_promote_experimental_mode(self):
        """Auto-suggestions should stay inside the public surface."""
        manager = ModeManager()

        suggestion = asyncio.run(
            manager.suggest_mode_switch("design the system architecture", {})
        )

        assert suggestion is None

    def test_mode_command_lists_stable_and_experimental_sections(self, capsys):
        """The /mode command should expose stable and experimental sections separately."""
        router = make_router()

        asyncio.run(router._handle_mode_command([]))
        captured = capsys.readouterr()

        assert "Stable mode" in captured.out
        assert "Experimental mode" in captured.out
        assert "smart" in captured.out
        assert "architect" in captured.out
