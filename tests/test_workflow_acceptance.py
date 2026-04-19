"""Acceptance-style tests for the primary repository workflow."""

import asyncio
from unittest.mock import AsyncMock, Mock

from src.core.enhanced_request_router import EnhancedRequestRouter
from src.core.intelligent_request_classifier import ClassificationResult, RequestType


class TestRepositoryWorkflowAcceptance:
    """Validate the repo understand -> plan contract through the router."""

    def make_router(self):
        """Create a router with a mocked SmartCLI shell."""
        smart_cli = Mock()
        smart_cli.orchestrator = Mock()
        smart_cli.command_handler = Mock()
        smart_cli.handlers = {}
        smart_cli.debug = False
        smart_cli.config = {}
        smart_cli._process_ai_request = AsyncMock()
        router = EnhancedRequestRouter(smart_cli)
        return router, smart_cli

    def test_repo_understand_plan_metadata_reaches_orchestrator(self):
        """Classifier workflow hints should be attached to the orchestrator plan."""
        router, smart_cli = self.make_router()
        classification = ClassificationResult(
            request_type=RequestType.DEVELOPMENT,
            confidence=0.91,
            reasoning=["Repository workflow detected"],
            suggested_action="Run repo understand -> plan workflow",
            context_hints={
                "workflow_target": "repository",
                "workflow_stage": "plan",
                "original_text": "analyze this repository and give me an implementation plan",
            },
        )

        smart_cli.orchestrator.create_detailed_plan = AsyncMock(
            return_value={
                "title": "Smart Medium Plan",
                "workflow_type": "repo_understand_plan",
                "workflow_summary": {"workflow_type": "repo_understand_plan"},
                "pipeline": ["analyzer", "architect", "modifier"],
            }
        )
        smart_cli.orchestrator.execute_task_plan = AsyncMock(return_value=True)

        result = asyncio.run(
            router._process_development(
                "analyze this repository and give me an implementation plan",
                classification,
                {},
            )
        )

        assert result is True
        execute_args = smart_cli.orchestrator.execute_task_plan.await_args.args
        enriched_plan = execute_args[0]
        assert enriched_plan["workflow_type"] == "repo_understand_plan"
        assert enriched_plan["workflow_target"] == "repository"
        assert enriched_plan["workflow_stage"] == "plan"
        assert enriched_plan["suggested_action"] == "Run repo understand -> plan workflow"
        assert enriched_plan["confidence"] == 0.91
        assert execute_args[1] == "analyze this repository and give me an implementation plan"
