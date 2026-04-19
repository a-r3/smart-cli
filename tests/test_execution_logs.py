"""Tests for structured execution logging."""

import json
import time
from pathlib import Path
from unittest.mock import patch
import pytest

from src.core.execution_logger import ExecutionLogger


class TestExecutionLogger:
    """Test structured execution log creation and persistence."""

    def test_execution_logger_initialization(self):
        """Logger should initialize with stable structure."""
        logger = ExecutionLogger()

        assert logger.session_id is not None
        assert len(logger.session_id) > 0
        assert logger.execution_log["session_id"] == logger.session_id
        assert logger.execution_log["workflow_type"] is None
        assert logger.execution_log["original_request"] is None
        assert logger.execution_log["completion_status"] == "pending"

    def test_execution_logger_custom_session_id(self):
        """Logger should accept custom session ID."""
        session_id = "test_session_123"
        logger = ExecutionLogger(session_id=session_id)

        assert logger.session_id == session_id
        assert logger.execution_log["session_id"] == session_id

    def test_record_classification(self):
        """Logger should record classifier results."""
        logger = ExecutionLogger()
        request_text = "analyze this repository"

        logger.record_classification(
            request_type="analysis",
            confidence=0.85,
            reasoning=["Contains repo keyword", "Contains analyze keyword"],
            original_request=request_text,
        )

        assert logger.execution_log["original_request"] == request_text
        assert logger.execution_log["classifier_result"]["request_type"] == "analysis"
        assert logger.execution_log["classifier_result"]["confidence"] == 0.85
        assert len(logger.execution_log["classifier_result"]["reasoning"]) == 2

    def test_record_workflow_type(self):
        """Logger should record workflow type."""
        logger = ExecutionLogger()
        logger.record_workflow_type("repo_understand_plan")

        assert logger.execution_log["workflow_type"] == "repo_understand_plan"

    def test_record_orchestrator_summary(self):
        """Logger should record orchestrator summary."""
        logger = ExecutionLogger()
        summary = {
            "workflow_type": "repo_understand_plan",
            "title": "Repository Analysis",
            "stages": ["analyzer", "architect"],
            "estimated_cost": 0.05,
        }

        logger.record_orchestrator_summary(summary)

        assert logger.execution_log["orchestrator_summary"]["workflow_type"] == "repo_understand_plan"
        assert logger.execution_log["orchestrator_summary"]["estimated_cost"] == 0.05

    def test_record_agent_execution_success(self):
        """Logger should record successful agent execution."""
        logger = ExecutionLogger()

        logger.record_agent_execution(
            agent_name="🔍 Code Analyzer Agent",
            agent_type="analyzer",
            success=True,
            created_files=[],
            modified_files=[],
            errors=[],
            warnings=[],
            execution_time=0.5,
            output_data={"total_files": 3},
        )

        assert len(logger.execution_log["agent_results"]) == 1
        result = logger.execution_log["agent_results"][0]
        assert result["agent_type"] == "analyzer"
        assert result["success"] is True
        assert result["created_files"] == []
        assert result["output_data"]["total_files"] == 3

    def test_record_agent_execution_with_files(self):
        """Logger should record agent execution with created/modified files."""
        logger = ExecutionLogger()

        logger.record_agent_execution(
            agent_name="🔧 Code Modifier Agent",
            agent_type="modifier",
            success=True,
            created_files=["new_feature.py"],
            modified_files=["config.yaml"],
            errors=[],
            warnings=["Check imports"],
            execution_time=1.2,
            output_data={"lines_changed": 150},
        )

        result = logger.execution_log["agent_results"][0]
        assert result["created_files"] == ["new_feature.py"]
        assert result["modified_files"] == ["config.yaml"]
        assert len(result["warnings"]) == 1
        assert result["warnings"][0] == "Check imports"

    def test_record_artifacts(self):
        """Logger should record final artifacts."""
        logger = ExecutionLogger()
        artifacts = {
            "analyzer": ["/path/to/analysis.json"],
            "architect": ["/path/to/plan.md"],
        }

        logger.record_artifacts(artifacts)

        assert logger.execution_log["artifacts"]["analyzer"] == ["/path/to/analysis.json"]
        assert logger.execution_log["artifacts"]["architect"] == ["/path/to/plan.md"]

    def test_record_warnings_and_errors(self):
        """Logger should accumulate warnings and errors."""
        logger = ExecutionLogger()

        logger.record_warning("First warning")
        logger.record_error("First error")
        logger.record_warning("Second warning")
        logger.record_error("Second error")

        assert logger.execution_log["warnings"] == ["First warning", "Second warning"]
        assert logger.execution_log["errors"] == ["First error", "Second error"]

    def test_record_duplicate_warnings_ignored(self):
        """Logger should not duplicate identical warnings."""
        logger = ExecutionLogger()

        logger.record_warning("Same warning")
        logger.record_warning("Same warning")
        logger.record_warning("Different warning")

        assert len(logger.execution_log["warnings"]) == 2
        assert logger.execution_log["warnings"][0] == "Same warning"

    def test_finalize_success(self):
        """Logger should finalize with success status."""
        logger = ExecutionLogger()
        logger.finalize(success=True)

        assert logger.execution_log["completion_status"] == "success"
        assert logger.execution_log["execution_time"] > 0

    def test_finalize_failure(self):
        """Logger should finalize with failed status."""
        logger = ExecutionLogger()
        logger.finalize(success=False)

        assert logger.execution_log["completion_status"] == "failed"

    def test_save_to_disk_creates_directory(self, tmp_path):
        """Logger should create artifacts/session directory if needed."""
        logger = ExecutionLogger()
        logger.finalize(success=True)

        log_path = logger.save_to_disk(str(tmp_path))

        assert log_path.exists()
        assert log_path.parent.name == "session"
        assert "execution_" in log_path.name

    def test_saved_log_is_valid_json(self, tmp_path):
        """Saved log should be valid JSON."""
        logger = ExecutionLogger(session_id="test_log_123")
        logger.record_workflow_type("repo_understand")
        logger.finalize(success=True)

        log_path = logger.save_to_disk(str(tmp_path))

        # Read and parse the saved log
        with open(log_path, "r") as f:
            saved_log = json.load(f)

        assert saved_log["session_id"] == "test_log_123"
        assert saved_log["workflow_type"] == "repo_understand"
        assert saved_log["completion_status"] == "success"

    def test_get_log_dict(self):
        """Logger should return complete log dictionary."""
        logger = ExecutionLogger()
        logger.record_workflow_type("repo_analyze")
        logger.record_warning("test warning")
        logger.finalize(success=True)

        log_dict = logger.get_log_dict()

        assert log_dict["session_id"] == logger.session_id
        assert log_dict["workflow_type"] == "repo_analyze"
        assert len(log_dict["warnings"]) == 1

    def test_get_latest_log_returns_most_recent(self, tmp_path):
        """get_latest_log should return the most recent log."""
        # Create first log
        logger1 = ExecutionLogger(session_id="log_1")
        logger1.finalize(success=True)
        path1 = logger1.save_to_disk(str(tmp_path))

        # Wait a bit and create second log
        time.sleep(0.1)
        logger2 = ExecutionLogger(session_id="log_2")
        logger2.finalize(success=True)
        path2 = logger2.save_to_disk(str(tmp_path))

        # Latest should be the second one
        latest = ExecutionLogger.get_latest_log(str(tmp_path))
        assert latest == path2

    def test_load_log_from_disk(self, tmp_path):
        """Should be able to load a saved log from disk."""
        logger = ExecutionLogger(session_id="load_test")
        logger.record_workflow_type("repo_understand_plan")
        logger.record_warning("Test warning")
        logger.finalize(success=True)

        log_path = logger.save_to_disk(str(tmp_path))

        # Load the log
        loaded_log = ExecutionLogger.load_log(log_path)

        assert loaded_log["session_id"] == "load_test"
        assert loaded_log["workflow_type"] == "repo_understand_plan"
        assert loaded_log["warnings"] == ["Test warning"]
        assert loaded_log["completion_status"] == "success"

    def test_complete_workflow_logging(self, tmp_path):
        """Test complete workflow logging scenario."""
        logger = ExecutionLogger()

        # Record classification
        logger.record_classification(
            request_type="development",
            confidence=0.80,
            reasoning=["repo keyword found", "plan keyword found"],
            original_request="analyze this repository and give me a plan",
        )

        # Record workflow type
        logger.record_workflow_type("repo_understand_plan")

        # Record orchestrator summary
        logger.record_orchestrator_summary({
            "workflow_type": "repo_understand_plan",
            "title": "Repository Analysis and Planning",
            "stages": ["analyzer", "architect"],
            "estimated_cost": 0.05,
        })

        # Record agent executions
        logger.record_agent_execution(
            agent_name="🔍 Code Analyzer Agent",
            agent_type="analyzer",
            success=True,
            created_files=[],
            modified_files=[],
            errors=[],
            warnings=[],
            execution_time=0.3,
            output_data={"total_files": 5, "directories": 2},
        )

        logger.record_agent_execution(
            agent_name="🏗️ System Architect Agent",
            agent_type="architect",
            success=True,
            created_files=["architecture_plan.md"],
            modified_files=[],
            errors=[],
            warnings=[],
            execution_time=0.5,
            output_data={"components": 3},
        )

        # Record artifacts
        logger.record_artifacts({
            "analyzer": ["/tmp/analysis.json"],
            "architect": ["/tmp/architecture_plan.md"],
        })

        logger.finalize(success=True)

        # Save and verify
        log_path = logger.save_to_disk(str(tmp_path))
        assert log_path.exists()

        loaded_log = ExecutionLogger.load_log(log_path)
        assert loaded_log["completion_status"] == "success"
        assert len(loaded_log["agent_results"]) == 2
        assert loaded_log["agent_results"][0]["agent_type"] == "analyzer"
        assert loaded_log["agent_results"][1]["agent_type"] == "architect"
        assert loaded_log["agent_results"][1]["created_files"] == ["architecture_plan.md"]
