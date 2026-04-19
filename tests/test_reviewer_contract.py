"""Tests for ReviewerAgent result contracts."""

import asyncio
from unittest.mock import Mock

from src.agents.reviewer_agent import ReviewerAgent


class TestReviewerContract:
    """Ensure ReviewerAgent returns stable result structures."""

    def test_reviewer_success_contract_for_single_file(self, tmp_path):
        """Reviewing one Python file should not claim file changes."""
        target_file = tmp_path / "example.py"
        target_file.write_text(
            '"""Docstring"""\n\ndef example():\n    return 1\n',
            encoding="utf-8",
        )

        agent = ReviewerAgent(ai_client=Mock(), config_manager=None)
        result = asyncio.run(
            agent.execute(str(target_file), "review this file for code quality")
        )

        assert result.success is True
        assert result.created_files == []
        assert result.modified_files == []
        assert result.errors == []
        assert result.warnings == []
        assert result.output_data["target"] == str(target_file)
        assert result.output_data["task_type"] == "code_review"

    def test_reviewer_failure_contract_for_missing_target(self):
        """Missing review targets should fail without claiming file changes."""
        agent = ReviewerAgent(ai_client=Mock(), config_manager=None)

        result = asyncio.run(
            agent.execute("/tmp/definitely-missing-review-target.py", "review this file")
        )

        assert result.success is False
        assert result.created_files == []
        assert result.modified_files == []
        assert result.warnings == []
        assert result.errors == [
            "Target not found: /tmp/definitely-missing-review-target.py"
        ]
        assert result.output_data["task_type"] == "code_review"
