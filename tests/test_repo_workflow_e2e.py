"""End-to-end workflow test with fixture repository."""

import asyncio
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, AsyncMock, patch
import pytest

from src.core.intelligent_request_classifier import (
    IntelligentRequestClassifier,
    RequestType,
)
from src.core.enhanced_request_router import EnhancedRequestRouter
from src.agents.orchestrator import SmartCLIOrchestrator
from src.agents.analyzer_agent import AnalyzerAgent
from src.agents.architect_agent import ArchitectAgent
from src.agents.modifier_agent import ModifierAgent
from src.agents.tester_agent import TesterAgent
from src.agents.reviewer_agent import ReviewerAgent


class TestRepoWorkflowE2E:
    """Test complete workflow from classifier through orchestrator."""

    @pytest.fixture
    def fixture_repo_path(self):
        """Provide path to fixture repository."""
        repo_path = Path(__file__).parent / "fixtures" / "sample_repo"
        assert repo_path.exists(), f"Fixture repo not found at {repo_path}"
        return repo_path

    def test_classifier_recognizes_repo_analysis_request(self):
        """Classifier should recognize repo analysis request."""
        classifier = IntelligentRequestClassifier()
        request = "analyze this repository and give me an implementation plan"
        result = classifier.classify_request(request)

        # Should be classified as ANALYSIS or DEVELOPMENT type
        assert result.request_type in [RequestType.ANALYSIS, RequestType.DEVELOPMENT]
        # Confidence should be reasonable
        assert result.confidence > 0.3

    def test_classifier_detects_golden_path_request(self):
        """Classifier should mark analysis+planning as high-confidence."""
        classifier = IntelligentRequestClassifier()
        request = "analyze this repository and give me an implementation plan"
        result = classifier.classify_request(request)

        # Should detect repo + analyze + plan pattern
        assert result.confidence > 0.2
        suggested = result.suggested_action.lower()
        # Should suggest workflow-oriented action
        assert (
            "workflow" in suggested
            or "plan" in suggested
            or "analyze" in suggested
            or "repo" in suggested
        )

    def test_orchestrator_builds_workflow_summary(self):
        """Orchestrator should build stable workflow summary."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        plan = {
            "workflow_type": "repo_understand_plan",
            "title": "Repository Analysis",
            "pipeline": ["analyzer", "architect"],
            "estimated_cost": 0.025,
        }

        summary = orchestrator.build_workflow_summary(plan)

        assert summary["workflow_type"] == "repo_understand_plan"
        assert "analyzer" in summary["stages"]
        assert "architect" in summary["stages"]
        assert summary["estimated_cost"] == 0.025
        assert len(summary["summary_lines"]) >= 3

    def test_orchestrator_infers_repo_understand_plan_workflow(self):
        """Orchestrator should infer repo_understand_plan workflow type."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        request = "analyze this repository and give me an implementation plan"
        workflow_type = orchestrator._infer_workflow_type(request)

        assert workflow_type == "repo_understand_plan"

    def test_orchestrator_infers_repo_understand_workflow(self):
        """Orchestrator should infer repo_understand workflow type."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        request = "analyze this repository"
        workflow_type = orchestrator._infer_workflow_type(request)

        assert workflow_type == "repo_understand"

    def test_analyzer_agent_with_fixture_repo(self, fixture_repo_path):
        """AnalyzerAgent should report structure without file changes."""
        agent = AnalyzerAgent(ai_client=Mock(), config_manager=None)
        result = asyncio.run(
            agent._basic_analysis_fallback(
                str(fixture_repo_path), "analyze this repository"
            )
        )

        assert result.success is True
        assert result.created_files == []
        assert result.modified_files == []
        # Should have meaningful output data
        assert len(result.output_data) > 0
        # Should detect files or components
        assert (
            "file_count" in result.output_data
            or "total_files" in result.output_data
            or "component_count" in result.output_data
        )

    def test_architect_agent_with_fixture_repo(self, fixture_repo_path):
        """ArchitectAgent should design structure without file changes."""
        agent = ArchitectAgent(ai_client=Mock(), config_manager=None)
        result = asyncio.run(
            agent._basic_architecture_fallback(
                str(fixture_repo_path), "design architecture"
            )
        )

        assert result.success is True
        assert result.created_files == []
        assert result.modified_files == []
        assert "component_count" in result.output_data
        assert "dependency_count" in result.output_data

    def test_tester_agent_with_fixture_repo(self, fixture_repo_path):
        """TesterAgent should validate Python files without changes."""
        agent = TesterAgent(ai_client=Mock(), config_manager=None)
        test_file = fixture_repo_path / "tests" / "test_calculator.py"

        result = asyncio.run(
            agent._basic_testing_fallback(
                str(test_file), "validate test file"
            )
        )

        assert result.success is True
        assert result.created_files == []
        assert result.modified_files == []
        assert result.output_data.get("syntax_valid") is True

    def test_reviewer_agent_with_fixture_repo(self, fixture_repo_path):
        """ReviewerAgent should review code without file changes."""
        agent = ReviewerAgent(ai_client=Mock(), config_manager=None)
        src_file = fixture_repo_path / "src" / "calculator.py"

        result = asyncio.run(
            agent.execute(str(src_file), "review this code")
        )

        assert result.success is True
        assert result.created_files == []
        assert result.modified_files == []
        assert result.output_data.get("target") == str(src_file)

    def test_workflow_summary_end_to_end(self, fixture_repo_path):
        """Build complete workflow summary with fixture repo context."""
        orchestrator = SmartCLIOrchestrator(
            ai_client=Mock(), config_manager=None
        )

        # Simulate classification
        user_request = "analyze this repository and give me an implementation plan"
        workflow_type = orchestrator._infer_workflow_type(user_request)

        # Build plan
        plan = {
            "workflow_type": workflow_type,
            "title": "Repository Analysis Plan",
            "pipeline": ["analyzer", "architect", "tester", "reviewer"],
            "estimated_cost": 0.15,
        }

        summary = orchestrator.build_workflow_summary(plan)

        # Validate summary structure
        assert summary["workflow_type"] == "repo_understand_plan"
        assert len(summary["stages"]) == 4
        assert all(
            stage in ["analyzer", "architect", "tester", "reviewer"]
            for stage in summary["stages"]
        )
        assert summary["estimated_cost"] == 0.15
        assert len(summary["summary_lines"]) >= 3

        # All summary lines should be present and meaningful
        assert any("Workflow:" in line for line in summary["summary_lines"])
        assert any("Pipeline:" in line for line in summary["summary_lines"])
        assert any("Estimated cost:" in line for line in summary["summary_lines"])

    def test_artifact_manifest_structure(self, fixture_repo_path):
        """Artifact manifests should follow stable structure."""
        agent = AnalyzerAgent(ai_client=Mock(), config_manager=None)
        result = asyncio.run(
            agent._basic_analysis_fallback(
                str(fixture_repo_path), "analyze"
            )
        )

        # Manifest fields must always be present
        assert hasattr(result, "created_files")
        assert hasattr(result, "modified_files")
        assert hasattr(result, "errors")
        assert hasattr(result, "warnings")
        assert hasattr(result, "output_data")

        # Must be list-like or empty
        assert isinstance(result.created_files, (list, tuple)) or result.created_files is None
        assert isinstance(result.modified_files, (list, tuple)) or result.modified_files is None
        assert isinstance(result.errors, (list, tuple)) or result.errors is None
        assert isinstance(result.warnings, (list, tuple)) or result.warnings is None

        # output_data must be dict-like
        assert isinstance(result.output_data, dict)

    def test_orchestrator_workflow_records_real_modifier_change(self, tmp_path, monkeypatch):
        """Full workflow should record a real file modification during modifier phase."""
        monkeypatch.chdir(tmp_path)

        target_file = tmp_path / "app.py"
        original = "def greet():\n    return 'hello'\n"
        updated = "def greet():\n    return 'hello world'\n"
        target_file.write_text(original, encoding="utf-8")

        ai_client = Mock()
        ai_client.generate_response = AsyncMock(
            return_value=SimpleNamespace(content=updated)
        )
        orchestrator = SmartCLIOrchestrator(ai_client=ai_client, config_manager=None)

        modifier_agent = ModifierAgent(ai_client=ai_client, config_manager=None)

        async def delegate_stub(agent_type, target, description, action=""):
            if agent_type == "modifier":
                return await modifier_agent.execute(
                    str(target_file), "update greet return value"
                )

            return SimpleNamespace(
                success=True,
                created_files=[],
                modified_files=[],
                warnings=[],
                errors=[],
                output_data={"agent_type": agent_type},
            )

        orchestrator.delegate_to_agent = delegate_stub

        plan = {
            "workflow_type": "repo_implementation",
            "pipeline": ["analyzer", "architect", "modifier", "tester", "reviewer"],
            "complexity": "medium",
            "risk": "medium",
            "workflow_summary": {
                "workflow_type": "repo_implementation",
                "title": "Implementation Workflow",
                "stages": ["analyzer", "architect", "modifier", "tester", "reviewer"],
                "estimated_cost": 0.05,
                "summary_lines": [
                    "Workflow: repo_implementation",
                    "Pipeline: analyzer -> architect -> modifier -> tester -> reviewer",
                    "Estimated cost: $0.050",
                ],
            },
        }

        success = asyncio.run(
            orchestrator._execute_smart_pipeline(plan, "update greet implementation")
        )

        assert success is True
        assert target_file.read_text(encoding="utf-8") == updated

        modifier_results = [
            entry
            for entry in orchestrator.execution_logger.execution_log["agent_results"]
            if entry["agent_type"] == "modifier"
        ]
        assert len(modifier_results) == 1
        assert modifier_results[0]["modified_files"] == [str(target_file)]
        assert modifier_results[0]["created_files"] == []

        implementation_artifacts = orchestrator.artifacts["implementation"]
        assert str(target_file) in implementation_artifacts
        assert any(
            artifact.endswith("artifacts/implementation/phase_manifest.json")
            for artifact in implementation_artifacts
        )
