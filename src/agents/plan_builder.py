"""Pure helpers for building and costing execution plans."""

from typing import Any, Dict, List

_PHASE_MAP: Dict[str, str] = {
    "analyzer": "analysis",
    "architect": "architecture",
    "modifier": "implementation",
    "tester": "testing",
    "reviewer": "review",
    "metalearning": "metalearning",
}

_TASK_DESCRIPTIONS: Dict[str, str] = {
    "architect": "System design",
    "analyzer": "Code analysis",
    "modifier": "Implementation",
    "tester": "Quality assurance",
    "reviewer": "Final review",
    "metalearning": "Pattern learning",
}


def phase_key_for_agent(agent_type: str) -> str:
    """Map agent type to the phase artifact key."""
    return _PHASE_MAP.get(agent_type, agent_type)


def get_agent_task_description(agent_type: str) -> str:
    """Return a human-readable task label for an agent type."""
    return _TASK_DESCRIPTIONS.get(agent_type, f"{agent_type} processing")


def create_pipeline_steps(
    pipeline: List[str],
    models: Dict[str, str],
    complexity: Any,
    risk: Any,
) -> List[Dict[str, Any]]:
    """Build the ordered step list for an execution plan."""
    complexity_val = complexity.value if hasattr(complexity, "value") else str(complexity)
    return [
        {
            "id": f"step_{i}",
            "agent": agent_type,
            "action": f"{agent_type}_task",
            "description": f"Smart {complexity_val} {agent_type}",
            "model": models.get(agent_type, "llama-3-8b"),
        }
        for i, agent_type in enumerate(pipeline, 1)
    ]


def estimate_plan_cost(pipeline: List[str], cost_optimizer: Any) -> float:
    """Estimate total cost by querying the cost optimizer for each agent."""
    total = 0.0
    for agent_type in pipeline:
        try:
            _, cost = cost_optimizer.select_optimal_model(
                agent_type, f"task for {agent_type}", estimated_tokens=2000
            )
            total += cost
        except Exception:
            total += 0.02
    return total
