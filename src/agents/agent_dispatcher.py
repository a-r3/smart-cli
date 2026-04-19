"""Agent instantiation and dispatch logic, extracted from the orchestrator."""

import time
from typing import Any, Optional

from rich.console import Console

console = Console()

_AGENT_MODULES = {
    "architect": ("architect_agent", "ArchitectAgent"),
    "analyzer": ("analyzer_agent", "AnalyzerAgent"),
    "modifier": ("modifier_agent", "ModifierAgent"),
    "tester": ("tester_agent", "TesterAgent"),
    "reviewer": ("reviewer_agent", "ReviewerAgent"),
}


async def dispatch_agent(
    agent_type: str,
    target: str,
    description: str,
    ai_client: Any,
    config_manager: Any,
    cost_optimizer: Any,
    task_classifier: Any,
    session_cost: list,  # mutable single-element list so caller sees updates
) -> Any:
    """Instantiate and execute an agent, returning its AgentReport."""
    try:
        from .base_agent import AgentReport
    except ImportError:
        from base_agent import AgentReport

    task_start = time.time()
    actual_cost = 0.0

    try:
        _, estimated_cost = cost_optimizer.select_optimal_model(
            agent_type, description, estimated_tokens=2000
        )
        if hasattr(ai_client, "set_model"):
            optimal_model, _ = cost_optimizer.select_optimal_model(
                agent_type, description, estimated_tokens=2000
            )
            ai_client.set_model(optimal_model)
        actual_cost = estimated_cost
    except Exception:
        pass

    try:
        if agent_type not in _AGENT_MODULES:
            console.print(f"⚠️ [yellow]Unknown agent: {agent_type}[/yellow]")
            return AgentReport(
                success=False,
                agent_name=f"Unknown Agent ({agent_type})",
                task_description=description,
                execution_time=0.0,
                created_files=[],
                modified_files=[],
                errors=[f"Unknown agent type: {agent_type}"],
                warnings=[],
                output_data={},
                next_recommendations=[],
            )

        module_name, class_name = _AGENT_MODULES[agent_type]
        try:
            mod = __import__(
                f"src.agents.{module_name}", fromlist=[class_name]
            )
        except ImportError:
            mod = __import__(f"{module_name}", fromlist=[class_name])

        agent_cls = getattr(mod, class_name)
        agent = agent_cls(ai_client, config_manager)
        result = await agent.execute(target, description)

        cost_optimizer.record_usage(actual_cost)
        session_cost[0] += actual_cost
        return result

    except Exception as exc:
        error_msg = f"Agent delegation failed: {exc}"
        console.print(f"❌ [red]{error_msg}[/red]")
        return AgentReport(
            success=False,
            agent_name=f"{agent_type} Agent",
            task_description=description,
            execution_time=time.time() - task_start,
            created_files=[],
            modified_files=[],
            errors=[error_msg],
            warnings=[],
            output_data={},
            next_recommendations=[],
        )
