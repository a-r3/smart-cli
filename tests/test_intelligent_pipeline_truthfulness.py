"""Tests for truthful intelligent pipeline execution."""

import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock, Mock, patch

from src.agents.base_agent import AgentReport
from src.agents.orchestrator import SmartCLIOrchestrator


class TestIntelligentPipelineTruthfulness:
    """Keep intelligent pipeline output aligned with real execution."""

    def test_phase_key_for_agent(self):
        """Agent types should map to stable artifact phase keys."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)

        assert orchestrator._phase_key_for_agent("analyzer") == "analysis"
        assert orchestrator._phase_key_for_agent("reviewer") == "review"
        assert orchestrator._phase_key_for_agent("custom") == "custom"

    def test_intelligent_pipeline_records_real_artifacts(self):
        """Intelligent pipeline should persist artifacts from actual agent results."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)
        phase = SimpleNamespace(
            phase_number=1,
            execution_mode=SimpleNamespace(value="sequential"),
            agents=["analyzer"],
        )
        result = AgentReport(
            success=True,
            agent_name="Analyzer Agent",
            task_description="Analyze repository",
            execution_time=0.1,
            created_files=["reports/analysis.txt"],
            modified_files=[],
            errors=[],
            warnings=[],
            output_data={},
            next_recommendations=[],
        )
        orchestrator._execute_agent_with_progress = AsyncMock(return_value=result)
        orchestrator._generate_phase_artifacts = Mock()

        with patch("src.agents.orchestrator.console.print"):
            results = asyncio.run(
                orchestrator._execute_intelligent_pipeline(
                    [phase],
                    "review this repository",
                    "medium",
                    "medium",
                )
            )

        assert results == [result]
        orchestrator._generate_phase_artifacts.assert_called_once_with(
            "analyzer",
            "analysis",
            result,
        )
