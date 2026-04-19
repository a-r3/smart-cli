"""Tests for report/document file creation contracts in analysis agents."""

import asyncio
import os
from pathlib import Path
from unittest.mock import Mock

from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.architect_agent import ArchitectAgent
from src.agents.tester_agent import TesterAgent as SmartTesterAgent


class TestAgentReportContracts:
    """Ensure agent helper methods return real created files."""

    def test_analyzer_report_helper_returns_existing_file(self, tmp_path):
        """Analyzer report helper should return a path that exists on disk."""
        agent = AnalyzerAgent(ai_client=Mock(), config_manager=None)
        insights = {
            "recommendations": ["Refactor routing"],
            "quick_wins": ["Remove dead code"],
            "next_steps": ["Review report"],
        }

        previous_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            report_path = asyncio.run(
                agent._create_analysis_report(insights, "src/example.py")
            )
        finally:
            os.chdir(previous_cwd)

        assert report_path is not None
        created_file = tmp_path / report_path
        assert created_file.exists()
        assert created_file.read_text(encoding="utf-8").startswith("# Code Analysis Report")

    def test_architect_documentation_helper_returns_existing_files(self, tmp_path):
        """Architect documentation helper should return created files that exist."""
        agent = ArchitectAgent(ai_client=Mock(), config_manager=None)
        architecture_design = {
            "components": [{"name": "API", "purpose": "Serve requests"}],
            "technology_stack": {"backend": ["Python"]},
            "design_patterns": [{"name": "Factory", "usage": "Object creation"}],
            "security_architecture": {"auth": "Token-based"},
        }
        implementation_plan = {"phases": ["Design", "Build", "Test"]}

        previous_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            created_files = asyncio.run(
                agent._create_architecture_documentation(
                    architecture_design,
                    implementation_plan,
                    "smart-cli",
                )
            )
        finally:
            os.chdir(previous_cwd)

        assert len(created_files) == 2
        for file_path in created_files:
            assert (tmp_path / file_path).exists()

    def test_tester_report_helper_returns_existing_file(self, tmp_path):
        """Tester report helper should return a path that exists on disk."""
        agent = SmartTesterAgent(ai_client=Mock(), config_manager=None)
        test_strategy = {"types": ["unit_testing"]}
        test_results = {
            "executed_tests": [{"name": "test_example", "return_code": 0}],
            "passed_tests": 1,
            "failed_tests": 0,
            "issues_found": [],
            "next_steps": ["Ship it"],
        }

        previous_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            report_path = asyncio.run(
                agent._create_testing_report(
                    test_strategy,
                    test_results,
                    "src/example.py",
                )
            )
        finally:
            os.chdir(previous_cwd)

        assert report_path is not None
        created_file = tmp_path / report_path
        assert created_file.exists()
        assert created_file.read_text(encoding="utf-8").startswith("# Comprehensive Testing Report")
