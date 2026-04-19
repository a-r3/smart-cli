"""Tests for ModifierAgent created/modified file reporting."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock

from src.agents.modifier_agent import ModifierAgent


class TestModifierContract:
    """Ensure ModifierAgent reports file changes consistently."""

    def test_fix_code_errors_separates_created_and_modified_files(self, tmp_path):
        """Fix flow should report new fixed files separately from edited originals."""
        target_file = tmp_path / "broken.py"
        target_file.write_text("def broken()\n    return 1\n", encoding="utf-8")

        ai_client = Mock()
        ai_client.generate_response = AsyncMock(
            return_value=SimpleNamespace(content="def broken():\n    return 1\n")
        )
        agent = ModifierAgent(ai_client=ai_client, config_manager=None)

        success, created_files, modified_files, errors = asyncio.run(
            agent._fix_code_errors(str(target_file), "fix syntax errors in broken.py")
        )

        assert success is True
        assert errors == []
        assert created_files == [str(target_file).replace(".py", "_fixed.py")]
        assert modified_files == [str(target_file)]

    def test_execute_reports_modified_files_for_fix_tasks(self, tmp_path):
        """Top-level execute should preserve modified file reporting for fix tasks."""
        target_file = tmp_path / "broken.py"
        target_file.write_text("def broken()\n    return 1\n", encoding="utf-8")

        ai_client = Mock()
        ai_client.generate_response = AsyncMock(
            return_value=SimpleNamespace(content="def broken():\n    return 1\n")
        )
        agent = ModifierAgent(ai_client=ai_client, config_manager=None)

        result = asyncio.run(
            agent.execute(str(target_file), "fix syntax errors in broken.py")
        )

        assert result.success is True
        assert result.created_files == [str(target_file).replace(".py", "_fixed.py")]
        assert result.modified_files == [str(target_file)]
