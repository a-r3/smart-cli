"""Tests for truthful phase artifact persistence."""

import json
import os
from unittest.mock import Mock

from src.agents.base_agent import AgentReport
from src.agents.orchestrator import SmartCLIOrchestrator


class TestArtifactManifest:
    """Ensure orchestrator persists real artifact metadata only."""

    def test_generate_phase_artifacts_writes_manifest(self, tmp_path):
        """Phase artifacts should be recorded in a manifest, not synthetic reports."""
        orchestrator = SmartCLIOrchestrator(ai_client=Mock(), config_manager=None)
        result = AgentReport(
            success=True,
            agent_name="Analyzer Agent",
            task_description="Analyze repository",
            execution_time=0.2,
            created_files=["reports/analysis.txt"],
            modified_files=["src/example.py"],
            errors=[],
            warnings=["minor warning"],
            output_data={},
            next_recommendations=[],
        )

        previous_cwd = os.getcwd()
        os.chdir(tmp_path)
        try:
            orchestrator._generate_phase_artifacts("analyzer", "analysis", result)
        finally:
            os.chdir(previous_cwd)

        manifest_path = tmp_path / "artifacts" / "analysis" / "phase_manifest.json"
        assert manifest_path.exists()

        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        assert manifest["agent"] == "analyzer"
        assert manifest["phase"] == "analysis"
        assert manifest["created_files"] == ["reports/analysis.txt"]
        assert manifest["modified_files"] == ["src/example.py"]
        assert manifest["warnings"] == ["minor warning"]

        assert orchestrator.artifacts["analysis"] == [
            "reports/analysis.txt",
            "src/example.py",
            "artifacts/analysis/phase_manifest.json",
        ]
