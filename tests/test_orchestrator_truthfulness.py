"""Tests for factual orchestrator status and meta-learning output."""

import asyncio
import json
import os
from unittest.mock import AsyncMock, Mock, patch

from src.agents.base_agent import AgentReport
from src.agents.orchestrator import SmartCLIOrchestrator


class TestOrchestratorTruthfulness:
    """Keep orchestrator output aligned with real behavior."""

    def test_execute_agent_with_progress_uses_factual_status_line(self):
        """Agent execution should print a simple delegation status only."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)
        expected_result = AgentReport(
            success=True,
            agent_name="Analyzer Agent",
            task_description="Analyze repo",
            execution_time=0.1,
            created_files=[],
            modified_files=[],
            errors=[],
            warnings=[],
            output_data={},
            next_recommendations=[],
        )
        orchestrator.delegate_to_agent = AsyncMock(return_value=expected_result)

        with patch("src.agents.orchestrator.console.print") as mock_print:
            result = asyncio.run(
                orchestrator._execute_agent_with_progress(
                    "analyzer",
                    "review this repository",
                    "medium",
                    "analysis",
                )
            )

        assert result is expected_result
        rendered = [call.args[0] for call in mock_print.call_args_list]
        assert rendered == ["   Status: delegating to analyzer agent"]

    def test_record_meta_learning_manifest_writes_only_manifest(self, tmp_path):
        """Meta-learning should persist a truthful manifest instead of fake output files."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)

        previous_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            orchestrator._record_meta_learning_manifest()
        finally:
            os.chdir(previous_cwd)

        manifest_path = tmp_path / "artifacts" / "metalearning" / "phase_manifest.json"
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["agent"] == "metalearning"
        assert manifest["created_files"] == []
        assert manifest["modified_files"] == []
        assert "post-run learning step" in manifest["notes"][1]

        assert orchestrator.artifacts["metalearning"] == [
            "artifacts/metalearning/phase_manifest.json"
        ]
