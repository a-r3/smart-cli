"""Tests for the primary repository workflow classification."""

from src.core.intelligent_request_classifier import (
    IntelligentRequestClassifier,
    RequestType,
)


class TestWorkflowClassifier:
    """Ensure the product wedge is detectable by the classifier."""

    def test_repo_understand_plan_workflow_is_detected(self):
        """Repository understanding plus planning should map to the workflow hint."""
        classifier = IntelligentRequestClassifier()

        result = classifier.classify_request(
            "analyze this repository and give me an implementation plan"
        )

        assert result.request_type in {RequestType.DEVELOPMENT, RequestType.ANALYSIS}
        assert result.suggested_action == "Run repo understand -> plan workflow"
        assert result.context_hints["workflow_target"] == "repository"
        assert result.context_hints["workflow_stage"] == "plan"

    def test_repo_understand_workflow_stage_is_extracted(self):
        """Repository understanding without planning should still expose workflow metadata."""
        classifier = IntelligentRequestClassifier()

        result = classifier.classify_request("understand this codebase and review it")

        assert result.suggested_action == "Run repo understanding workflow"
        assert result.context_hints["workflow_target"] == "repository"
        assert result.context_hints["workflow_stage"] == "understand"
