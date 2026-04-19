"""Tests for non-AI fallback result contracts."""

import asyncio
from unittest.mock import Mock

from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.architect_agent import ArchitectAgent
from src.agents.tester_agent import TesterAgent as SmartTesterAgent


class TestBasicFallbackContracts:
    """Keep fallback execution contracts stable and truthful."""

    def test_analyzer_basic_fallback_for_file(self, tmp_path):
        """Analyzer fallback should report file metadata without file changes."""
        target_file = tmp_path / "sample.py"
        target_file.write_text("print('hello')\n", encoding="utf-8")

        agent = AnalyzerAgent(ai_client=Mock(), config_manager=None)
        result = asyncio.run(
            agent._basic_analysis_fallback(
                str(target_file),
                "analyze this file",
            )
        )

        assert result.success is True
        assert result.created_files == []
        assert result.modified_files == []
        assert result.errors == []
        assert result.output_data["file_type"] == ".py"
        assert result.output_data["line_count"] == 2

    def test_architect_basic_fallback_for_directory(self, tmp_path):
        """Architect fallback should expose structure data without file changes."""
        target_file = tmp_path / "module.py"
        target_file.write_text("def run():\n    return True\n", encoding="utf-8")

        agent = ArchitectAgent(ai_client=Mock(), config_manager=None)
        result = asyncio.run(
            agent._basic_architecture_fallback(
                str(tmp_path),
                "design architecture for this repository",
            )
        )

        assert result.success is True
        assert result.created_files == []
        assert result.modified_files == []
        assert result.errors == []
        assert "component_count" in result.output_data
        assert "dependency_count" in result.output_data

    def test_tester_basic_fallback_marks_valid_python(self, tmp_path):
        """Tester fallback should report syntax validation through output_data."""
        target_file = tmp_path / "valid.py"
        target_file.write_text("def ok():\n    return 1\n", encoding="utf-8")

        agent = SmartTesterAgent(ai_client=Mock(), config_manager=None)
        result = asyncio.run(
            agent._basic_testing_fallback(
                str(target_file),
                "test this file",
            )
        )

        assert result.success is True
        assert result.created_files == []
        assert result.modified_files == []
        assert result.errors == []
        assert result.output_data["syntax_valid"] is True

    def test_tester_basic_fallback_marks_invalid_python(self, tmp_path):
        """Tester fallback should fail truthfully on invalid syntax."""
        target_file = tmp_path / "invalid.py"
        target_file.write_text("def broken(\n    return 1\n", encoding="utf-8")

        agent = SmartTesterAgent(ai_client=Mock(), config_manager=None)
        result = asyncio.run(
            agent._basic_testing_fallback(
                str(target_file),
                "test this file",
            )
        )

        assert result.success is False
        assert result.created_files == []
        assert result.modified_files == []
        assert result.output_data["syntax_valid"] is False
        assert len(result.errors) == 1
