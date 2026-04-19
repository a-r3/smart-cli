"""Tests for standardized workflow metadata in orchestrator plans."""

from types import SimpleNamespace
from unittest.mock import Mock
from unittest.mock import patch

from src.agents.orchestrator import SmartCLIOrchestrator


class TestWorkflowSummary:
    """Ensure the orchestrator exposes stable workflow metadata."""

    def test_infer_repo_understand_plan_workflow(self):
        """Repository analysis plus planning should map to the plan workflow."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)

        workflow_type = orchestrator._infer_workflow_type(
            "analyze this repository and give me an implementation plan"
        )

        assert workflow_type == "repo_understand_plan"

    def test_build_workflow_summary(self):
        """Workflow summary should expose a predictable structure."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)
        plan = {
            "title": "Smart Medium Plan",
            "workflow_type": "repo_understand_plan",
            "pipeline": ["analyzer", "architect", "modifier"],
            "estimated_cost": 0.125,
        }

        summary = orchestrator.build_workflow_summary(plan)

        assert summary["workflow_type"] == "repo_understand_plan"
        assert summary["stages"] == ["analyzer", "architect", "modifier"]
        assert "Workflow: repo_understand_plan" in summary["summary_lines"][0]
        assert "Pipeline: analyzer -> architect -> modifier" in summary["summary_lines"][1]

    def test_display_workflow_summary_renders_summary_lines(self):
        """Workflow display should print each standardized summary line."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)
        summary = {
            "summary_lines": [
                "Workflow: repo_understand_plan",
                "Pipeline: analyzer -> architect",
                "Estimated cost: $0.125",
            ]
        }

        with patch("src.agents.orchestrator.console.print") as mock_print:
            orchestrator._display_workflow_summary(summary)

        rendered = [call.args[0] for call in mock_print.call_args_list]
        assert rendered[0] == "🧭 [bold cyan]Workflow Summary[/bold cyan]"
        assert "   - Workflow: repo_understand_plan" in rendered
        assert "   - Pipeline: analyzer -> architect" in rendered
        assert "   - Estimated cost: $0.125" in rendered

    def test_build_agent_result_summary_with_changes_and_issues(self):
        """Agent summary should expose files, warnings, and errors consistently."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)
        result = SimpleNamespace(
            success=False,
            created_files=["a.py"],
            modified_files=["b.py", "c.py"],
            warnings=["warning"],
            errors=["error"],
        )

        summary = orchestrator.build_agent_result_summary("modifier", result)

        assert summary["phase_name"] == "Implementation"
        assert summary["agent_display"] == "🔧 Code Modifier Agent"
        assert summary["status_text"] == "created 1 files, modified 2 files, 1 warnings, 1 errors"
        assert summary["icon"] == "❌"

    def test_build_agent_result_summary_handles_missing_result(self):
        """Missing results should be summarized explicitly."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)

        summary = orchestrator.build_agent_result_summary("tester", None)

        assert summary["phase_name"] == "Testing"
        assert summary["status_text"] == "no result recorded"
        assert summary["icon"] == "❌"

    def test_display_agent_results_summary_renders_standard_block(self):
        """Summary renderer should print the standardized header and lines."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)
        result = SimpleNamespace(
            success=True,
            created_files=[],
            modified_files=[],
            warnings=[],
            errors=[],
        )

        with patch("src.agents.orchestrator.console.print") as mock_print:
            orchestrator._display_agent_results_summary([("analyzer", result), ("tester", None)])

        rendered = [call.args[0] for call in mock_print.call_args_list]
        assert rendered[0] == "📌 [bold cyan]Result Summary[/bold cyan]"
        assert "Analysis by 🔍 Code Analyzer Agent → completed with no file changes ✅" in rendered[1]
        assert "Testing by 🧪 Testing Agent → no result recorded ❌" in rendered[2]
