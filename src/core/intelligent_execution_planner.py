"""Intelligent Execution Planner — thin facade over execution_phases helpers."""

from typing import Any, Dict, List, Optional

from rich.console import Console

from .execution_types import (  # re-export so existing imports keep working
    AgentCapability,
    AgentDependency,
    AgentProfile,
    ExecutionMode,
    ExecutionPhase,
    ExecutionPlan,
    ParallelGroup,
    ResourceConflict,
)
from .execution_phases import (
    build_legacy_execution_plan,
    create_dependency_graph,
    detect_conflicts_in,
    display_execution_plan,
    estimate_total_execution_time,
    generate_execution_phases,
    get_execution_statistics,
    optimize_for_parallel_execution,
    optimize_parallel_groups,
    topological_sort_agents,
    validate_execution_plan,
)

console = Console()

__all__ = [
    "AgentCapability", "AgentDependency", "AgentProfile",
    "ExecutionMode", "ExecutionPhase", "ExecutionPlan",
    "ParallelGroup", "ResourceConflict",
    "IntelligentExecutionPlanner",
]


class IntelligentExecutionPlanner:
    """Advanced execution planner with dependency management."""

    def __init__(self):
        self.agent_profiles: Dict[str, AgentProfile] = {
            "analyzer": AgentProfile(
                name="analyzer",
                capabilities=[AgentCapability.READ_ONLY, AgentCapability.ANALYSIS],
                dependencies=[],
                conflicts_with=[],
                resource_requirements=["project_files"],
                execution_time_estimate=30.0,
                parallel_safe=True,
                priority_level=2,
            ),
            "architect": AgentProfile(
                name="architect",
                capabilities=[AgentCapability.ARCHITECTURE, AgentCapability.ANALYSIS],
                dependencies=["analyzer"],
                conflicts_with=[],
                resource_requirements=["project_files"],
                execution_time_estimate=45.0,
                parallel_safe=False,
                priority_level=4,
            ),
            "modifier": AgentProfile(
                name="modifier",
                capabilities=[AgentCapability.FILE_CREATION, AgentCapability.FILE_MODIFICATION, AgentCapability.CODE_GENERATION],
                dependencies=["architect"],
                conflicts_with=["tester"],
                resource_requirements=["file_system_write"],
                execution_time_estimate=60.0,
                parallel_safe=False,
                priority_level=3,
            ),
            "tester": AgentProfile(
                name="tester",
                capabilities=[AgentCapability.TESTING],
                dependencies=["modifier"],
                conflicts_with=["modifier"],
                resource_requirements=["file_system_read", "test_environment"],
                execution_time_estimate=35.0,
                parallel_safe=True,
                priority_level=2,
            ),
            "reviewer": AgentProfile(
                name="reviewer",
                capabilities=[AgentCapability.READ_ONLY, AgentCapability.REVIEW],
                dependencies=["modifier"],
                conflicts_with=[],
                resource_requirements=["project_files"],
                execution_time_estimate=25.0,
                parallel_safe=True,
                priority_level=1,
            ),
        }

        self.execution_scenarios = {
            "simple_analysis": {"agents": ["analyzer"], "strategy": "single_agent"},
            "quick_review": {"agents": ["analyzer", "reviewer"], "strategy": "parallel_readonly"},
            "full_implementation": {"agents": ["analyzer", "architect", "modifier", "tester", "reviewer"], "strategy": "smart_pipeline"},
            "code_generation": {"agents": ["analyzer", "modifier"], "strategy": "sequential_creation"},
        }

        self.agent_dependencies: Dict[str, AgentDependency] = {
            "analyzer": AgentDependency(agent="analyzer", depends_on=[], provides=["analysis"], conflicts_with=[], priority=2),
            "architect": AgentDependency(agent="architect", depends_on=["analyzer"], provides=["architecture"], conflicts_with=[], priority=4),
            "modifier": AgentDependency(agent="modifier", depends_on=["analyzer"], provides=["code_changes"], conflicts_with=["tester"], priority=3),
            "tester": AgentDependency(agent="tester", depends_on=["modifier"], provides=["test_results"], conflicts_with=["modifier"], priority=2),
            "reviewer": AgentDependency(agent="reviewer", depends_on=["tester"], provides=["review_feedback"], conflicts_with=[], priority=1),
        }

    # ------------------------------------------------------------------
    # Primary entry point
    # ------------------------------------------------------------------

    def create_intelligent_execution_plan(
        self, agent_tasks: List[Dict[str, Any]], scenario_hint: Optional[str] = None
    ) -> List[ExecutionPhase]:
        console.print("🧠 [bold blue]Creating intelligent execution plan...[/bold blue]")
        agent_names = [t.get("agent") for t in agent_tasks]
        if not scenario_hint:
            scenario_hint = self._detect_execution_scenario(agent_names)
        console.print(f"📋 [blue]Detected scenario: {scenario_hint}[/blue]")

        graph = create_dependency_graph(agent_names, self.agent_profiles)
        phases = generate_execution_phases(graph, agent_tasks, self.agent_profiles)
        optimized = optimize_for_parallel_execution(phases, self.agent_profiles)
        display_execution_plan(optimized, console)
        return optimized

    def _detect_execution_scenario(self, agent_names: List[str]) -> str:
        agent_set = set(agent_names)
        for scenario, cfg in self.execution_scenarios.items():
            if set(cfg["agents"]) == agent_set:
                return scenario
        if len(agent_names) == 1:
            return "single_agent"
        if all(self.agent_profiles[a].parallel_safe for a in agent_names if a in self.agent_profiles):
            return "parallel_readonly"
        if "modifier" in agent_names and "tester" in agent_names:
            return "full_implementation"
        return "custom_scenario"

    # ------------------------------------------------------------------
    # Delegating methods (preserve existing public API)
    # ------------------------------------------------------------------

    def validate_execution_plan(self, phases: List[ExecutionPhase]) -> Dict[str, Any]:
        return validate_execution_plan(phases, self.agent_profiles)

    def get_execution_statistics(self, phases: List[ExecutionPhase]) -> Dict[str, Any]:
        return get_execution_statistics(phases, self.agent_profiles)

    def get_agent_dependencies(self, agent: str) -> AgentDependency:
        return self.agent_dependencies.get(agent, AgentDependency(agent=agent))

    def detect_conflicts(self, agents: List[str]) -> List[ResourceConflict]:
        return detect_conflicts_in(agents, self.agent_profiles)

    def topological_sort(self, agents: List[str]) -> List[str]:
        return topological_sort_agents(agents, self.agent_dependencies)

    def optimize_parallel_execution(self, agents: List[str]) -> List[ParallelGroup]:
        return optimize_parallel_groups(agents, self.agent_profiles, self.agent_dependencies)

    def estimate_execution_time(self, agents: List[str], complexity: str, risk_level: str) -> float:
        return estimate_total_execution_time(agents, complexity, risk_level, self.agent_profiles, self.agent_dependencies)

    def create_execution_plan(
        self, agents: List[str], task_description: str, complexity: str, risk_level: str
    ) -> ExecutionPlan:
        return build_legacy_execution_plan(agents, task_description, complexity, risk_level, self.agent_profiles, self.agent_dependencies)
