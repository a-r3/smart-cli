"""Workflow summary and terminal display helpers for the orchestrator."""

from typing import Any, Callable, Dict, List, Optional, Tuple

from rich.console import Console

_console = Console()


def infer_workflow_type(user_request: str) -> str:
    """Infer the primary workflow type from the user request text."""
    text = user_request.lower()
    repo_terms = ["repo", "repository", "codebase", "project", "layihə", "kod bazası"]
    plan_terms = ["plan", "roadmap", "next steps", "implementation plan", "planla"]
    implement_terms = ["implement", "build", "fix", "apply", "tətbiq et", "düzəlt", "yarat"]
    understand_terms = ["analyze", "review", "understand", "inspect", "təhlil", "anla", "yoxla"]

    has_repo = any(t in text for t in repo_terms)
    has_plan = any(t in text for t in plan_terms)
    has_implement = any(t in text for t in implement_terms)
    has_understand = any(t in text for t in understand_terms)

    if has_repo and has_understand and has_plan:
        return "repo_understand_plan"
    if has_repo and has_understand and has_implement:
        return "repo_understand_implement"
    if has_repo and has_understand:
        return "repo_understand"
    return "generic"


def build_workflow_summary(plan: Dict[str, Any]) -> Dict[str, Any]:
    """Build a standardized workflow summary dict for downstream display."""
    workflow_type = plan.get("workflow_type", "generic")
    pipeline = plan.get("pipeline", [])
    return {
        "workflow_type": workflow_type,
        "title": plan.get("title", "Smart Plan"),
        "stages": pipeline,
        "estimated_cost": plan.get("estimated_cost", 0.0),
        "summary_lines": [
            f"Workflow: {workflow_type}",
            f"Pipeline: {' -> '.join(pipeline) if pipeline else 'none'}",
            f"Estimated cost: ${plan.get('estimated_cost', 0.0):.3f}",
        ],
    }


def display_workflow_summary(summary: Dict[str, Any], console: Console = _console) -> None:
    """Render a workflow summary block in the terminal."""
    console.print("🧭 [bold cyan]Workflow Summary[/bold cyan]")
    for line in summary.get("summary_lines", []):
        console.print(f"   - {line}")


def build_agent_result_summary(
    agent_type: str,
    result: Optional[Any],
    active_agents: Dict[str, str],
    phase_key_fn: Callable[[str], str],
) -> Dict[str, str]:
    """Build a stable user-facing summary for one agent result."""
    phase_name = phase_key_fn(agent_type).title()
    agent_display = active_agents.get(agent_type, f"{agent_type} Agent")

    if result is None:
        return {
            "phase_name": phase_name,
            "agent_display": agent_display,
            "status_text": "no result recorded",
            "icon": "❌",
        }

    status_parts = []
    created_files = getattr(result, "created_files", []) or []
    modified_files = getattr(result, "modified_files", []) or []
    warnings = getattr(result, "warnings", []) or []
    errors = getattr(result, "errors", []) or []

    if created_files:
        status_parts.append(f"created {len(created_files)} files")
    if modified_files:
        status_parts.append(f"modified {len(modified_files)} files")
    if warnings:
        status_parts.append(f"{len(warnings)} warnings")
    if errors:
        status_parts.append(f"{len(errors)} errors")

    status_text = ", ".join(status_parts) if status_parts else "completed with no file changes"
    icon = "✅" if getattr(result, "success", False) else "❌"
    return {
        "phase_name": phase_name,
        "agent_display": agent_display,
        "status_text": status_text,
        "icon": icon,
    }


def display_agent_results_summary(
    agent_results: List[Tuple[str, Optional[Any]]],
    active_agents: Dict[str, str],
    phase_key_fn: Callable[[str], str],
    console: Console = _console,
) -> None:
    """Render the standardized agent result summary block."""
    console.print("📌 [bold cyan]Result Summary[/bold cyan]")
    for agent_type, result in agent_results:
        summary = build_agent_result_summary(agent_type, result, active_agents, phase_key_fn)
        console.print(
            f"   - {summary['phase_name']} by {summary['agent_display']}"
            f" → {summary['status_text']} {summary['icon']}"
        )
