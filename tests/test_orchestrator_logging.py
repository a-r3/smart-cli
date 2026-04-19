"""Tests for orchestrator execution logging integration."""

from unittest.mock import Mock
from pathlib import Path
import pytest

from src.agents.orchestrator import SmartCLIOrchestrator
from src.core.execution_logger import ExecutionLogger


class TestOrchestratorLogging:
    """Test that orchestrator generates execution logs."""

    def test_orchestrator_initializes_with_logger(self):
        """Orchestrator should initialize with ExecutionLogger."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        assert orchestrator.execution_logger is not None
        assert isinstance(orchestrator.execution_logger, ExecutionLogger)

    def test_orchestrator_accepts_custom_logger(self):
        """Orchestrator should accept custom ExecutionLogger."""
        custom_logger = ExecutionLogger(session_id="custom_123")
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(),
            config_manager=None,
            execution_logger=custom_logger,
        )

        assert orchestrator.execution_logger == custom_logger
        assert orchestrator.execution_logger.session_id == "custom_123"

    def test_orchestrator_logger_records_artifacts(self):
        """Orchestrator should record final artifacts in log."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        # Manually set some artifacts
        orchestrator.artifacts = {
            "analyzer": ["/tmp/analysis.json"],
            "architect": ["/tmp/plan.md"],
        }

        # Record artifacts
        orchestrator.execution_logger.record_artifacts(orchestrator.artifacts)

        # Verify they're in the log
        logged_artifacts = orchestrator.execution_logger.execution_log["artifacts"]
        assert logged_artifacts["analyzer"] == ["/tmp/analysis.json"]
        assert logged_artifacts["architect"] == ["/tmp/plan.md"]

    def test_orchestrator_logger_records_errors(self):
        """Orchestrator should record errors in log."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        # Record an error
        orchestrator.execution_logger.record_error("Test agent failed")
        
        # Verify error is recorded
        assert "Test agent failed" in orchestrator.execution_logger.execution_log["errors"]

    def test_orchestrator_logger_records_workflow_type(self):
        """Orchestrator should record workflow type."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        # Record workflow type
        orchestrator.execution_logger.record_workflow_type("repo_understand_plan")
        
        # Verify workflow type is recorded
        assert orchestrator.execution_logger.execution_log["workflow_type"] == "repo_understand_plan"

    def test_orchestrator_logger_record_orchestrator_summary(self):
        """Orchestrator should record summary."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        summary = {
            "workflow_type": "repo_analyze",
            "title": "Analysis",
            "stages": ["analyzer"],
            "estimated_cost": 0.05,
        }
        
        # Record summary
        orchestrator.execution_logger.record_orchestrator_summary(summary)
        
        # Verify summary is recorded
        logged_summary = orchestrator.execution_logger.execution_log["orchestrator_summary"]
        assert logged_summary["workflow_type"] == "repo_analyze"
        assert logged_summary["estimated_cost"] == 0.05

    def test_orchestrator_logger_can_be_finalized(self):
        """Orchestrator logger should be finalizable."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        # Finalize logger
        orchestrator.execution_logger.finalize(success=True)
        
        # Verify finalization
        assert orchestrator.execution_logger.execution_log["completion_status"] == "success"
        assert orchestrator.execution_logger.execution_log["execution_time"] > 0

    def test_orchestrator_logger_can_save_logs(self, tmp_path):
        """Orchestrator logger should save logs to disk."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        # Record some data
        orchestrator.execution_logger.record_workflow_type("test_workflow")
        orchestrator.execution_logger.finalize(success=True)
        
        # Save to disk
        log_path = orchestrator.execution_logger.save_to_disk(str(tmp_path))
        
        # Verify file exists
        assert log_path.exists()
        assert "execution_" in log_path.name
        assert log_path.suffix == ".json"

    def test_orchestrator_has_active_agents_map(self):
        """Orchestrator should have active agents map for logging."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        # Should have agent mappings
        assert "analyzer" in orchestrator.active_agents
        assert "architect" in orchestrator.active_agents
        assert "tester" in orchestrator.active_agents
        assert "reviewer" in orchestrator.active_agents
        
        # Should have display names
        assert "Analyzer" in orchestrator.active_agents["analyzer"]
        assert "Architect" in orchestrator.active_agents["architect"]
