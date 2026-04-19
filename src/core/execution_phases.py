"""Pure phase-generation, validation, and optimization functions.

All functions accept agent_profiles / agent_dependencies as explicit
parameters so they are independently testable without the planner class.
"""

from typing import Any, Dict, List

from rich.console import Console

from .execution_types import (
    AgentDependency,
    AgentProfile,
    ExecutionMode,
    ExecutionPhase,
    ExecutionPlan,
    ParallelGroup,
    ResourceConflict,
)

_console = Console()


# ---------------------------------------------------------------------------
# Dependency graph helpers
# ---------------------------------------------------------------------------

def create_dependency_graph(
    agent_names: List[str],
    agent_profiles: Dict[str, AgentProfile],
) -> Dict[str, List[str]]:
    return {
        agent: agent_profiles[agent].dependencies.copy()
        for agent in agent_names
        if agent in agent_profiles
    }


def topological_sort_graph(graph: Dict[str, List[str]]) -> List[str]:
    """Kahn's algorithm; returns [] on cycle detection."""
    in_degree = {node: 0 for node in graph}
    for node in graph:
        for dep in graph[node]:
            if dep in in_degree:
                in_degree[dep] += 1

    queue = [n for n in in_degree if in_degree[n] == 0]
    result: List[str] = []
    while queue:
        node = queue.pop(0)
        result.append(node)
        for dependent in graph:
            if node in graph[dependent]:
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

    return result if len(result) == len(graph) else []


# ---------------------------------------------------------------------------
# Phase generation helpers
# ---------------------------------------------------------------------------

def determine_phase_execution_mode(
    agents: List[str],
    agent_profiles: Dict[str, AgentProfile],
) -> ExecutionMode:
    if len(agents) == 1:
        return ExecutionMode.SEQUENTIAL
    all_safe = all(
        agent_profiles[a].parallel_safe for a in agents if a in agent_profiles
    )
    return ExecutionMode.PARALLEL_SAFE if all_safe else ExecutionMode.HYBRID


def calculate_phase_duration(
    agents: List[str],
    execution_mode: ExecutionMode,
    agent_profiles: Dict[str, AgentProfile],
) -> float:
    times = [
        agent_profiles[a].execution_time_estimate
        for a in agents
        if a in agent_profiles
    ]
    if not times:
        return 30.0
    return max(times) if execution_mode == ExecutionMode.PARALLEL_SAFE else sum(times)


def get_required_resource_locks(
    agents: List[str],
    agent_profiles: Dict[str, AgentProfile],
) -> List[str]:
    locks: set = set()
    for a in agents:
        if a in agent_profiles:
            locks.update(agent_profiles[a].resource_requirements)
    return list(locks)


def generate_execution_phases(
    dependency_graph: Dict[str, List[str]],
    agent_tasks: List[Dict[str, Any]],
    agent_profiles: Dict[str, AgentProfile],
) -> List[ExecutionPhase]:
    topo_order = topological_sort_graph(dependency_graph)
    if not topo_order:
        _console.print("⚠️ [yellow]Circular dependency detected, using fallback ordering[/yellow]")
        topo_order = list(dependency_graph.keys())

    phases: List[ExecutionPhase] = []
    processed: set = set()
    phase_number = 1

    while len(processed) < len(topo_order):
        current_agents: List[str] = []
        for agent in topo_order:
            if agent in processed:
                continue
            if agent not in agent_profiles:
                continue
            profile = agent_profiles[agent]
            deps_ok = all(d in processed or d not in topo_order for d in profile.dependencies)
            if deps_ok and not any(c in current_agents for c in profile.conflicts_with):
                current_agents.append(agent)

        if not current_agents:
            remaining = set(topo_order) - processed
            _console.print(f"⚠️ [yellow]Cannot process remaining agents: {remaining}[/yellow]")
            break

        mode = determine_phase_execution_mode(current_agents, agent_profiles)
        phases.append(ExecutionPhase(
            phase_number=phase_number,
            agents=current_agents,
            execution_mode=mode,
            estimated_duration=calculate_phase_duration(current_agents, mode, agent_profiles),
            dependencies_satisfied=list(processed),
            resource_locks_needed=get_required_resource_locks(current_agents, agent_profiles),
        ))
        processed.update(current_agents)
        phase_number += 1

    return phases


def optimize_for_parallel_execution(
    phases: List[ExecutionPhase],
    agent_profiles: Dict[str, AgentProfile],
) -> List[ExecutionPhase]:
    result: List[ExecutionPhase] = []
    for phase in phases:
        if len(phase.agents) > 1 and phase.execution_mode == ExecutionMode.HYBRID:
            safe = [a for a in phase.agents if agent_profiles.get(a) and agent_profiles[a].parallel_safe]
            unsafe = [a for a in phase.agents if a not in safe]
            if safe and unsafe:
                if safe:
                    result.append(ExecutionPhase(
                        phase_number=phase.phase_number,
                        agents=safe,
                        execution_mode=ExecutionMode.PARALLEL_SAFE,
                        estimated_duration=calculate_phase_duration(safe, ExecutionMode.PARALLEL_SAFE, agent_profiles),
                        dependencies_satisfied=phase.dependencies_satisfied,
                        resource_locks_needed=get_required_resource_locks(safe, agent_profiles),
                    ))
                if unsafe:
                    result.append(ExecutionPhase(
                        phase_number=phase.phase_number + 0.5,
                        agents=unsafe,
                        execution_mode=ExecutionMode.SEQUENTIAL,
                        estimated_duration=calculate_phase_duration(unsafe, ExecutionMode.SEQUENTIAL, agent_profiles),
                        dependencies_satisfied=phase.dependencies_satisfied + safe,
                        resource_locks_needed=get_required_resource_locks(unsafe, agent_profiles),
                    ))
                continue
        result.append(phase)
    return result


# ---------------------------------------------------------------------------
# Display, validation, statistics
# ---------------------------------------------------------------------------

def display_execution_plan(phases: List[ExecutionPhase], console: Console = _console) -> None:
    console.print("\n📋 [bold blue]INTELLIGENT EXECUTION PLAN[/bold blue]")
    console.print("=" * 60)
    total = 0.0
    for phase in phases:
        console.print(f"\n🔸 [bold yellow]Phase {phase.phase_number:.1f}[/bold yellow] - {phase.execution_mode.value.upper()}")
        console.print(f"   Agents: {', '.join(phase.agents)}")
        console.print(f"   Duration: {phase.estimated_duration:.1f}s")
        deps = ', '.join(phase.dependencies_satisfied) if phase.dependencies_satisfied else 'None'
        console.print(f"   Dependencies: {deps}")
        if phase.execution_mode == ExecutionMode.PARALLEL_SAFE:
            console.print("   ⚡ [green]Parallel execution (safe)[/green]")
        elif phase.execution_mode == ExecutionMode.SEQUENTIAL:
            console.print("   🔄 [blue]Sequential execution[/blue]")
        else:
            console.print("   🔀 [yellow]Hybrid execution[/yellow]")
        total += phase.estimated_duration
    console.print(f"\n⏱️ [bold green]Total Estimated Duration: {total:.1f}s[/bold green]")
    console.print("=" * 60)


def validate_execution_plan(
    phases: List[ExecutionPhase],
    agent_profiles: Dict[str, AgentProfile],
) -> Dict[str, Any]:
    result: Dict[str, Any] = {"valid": True, "warnings": [], "errors": [], "optimization_suggestions": []}
    all_agents: set = set()
    processed: set = set()

    for phase in phases:
        all_agents.update(phase.agents)
        for agent in phase.agents:
            if agent in agent_profiles:
                unsatisfied = [
                    d for d in agent_profiles[agent].dependencies
                    if d not in processed and d in all_agents
                ]
                if unsatisfied:
                    result["errors"].append(f"Agent {agent} has unsatisfied dependencies: {unsatisfied}")
                    result["valid"] = False
        if phase.execution_mode == ExecutionMode.PARALLEL_SAFE:
            for agent in phase.agents:
                if agent in agent_profiles:
                    conflicts = [c for c in agent_profiles[agent].conflicts_with if c in phase.agents]
                    if conflicts:
                        result["errors"].append(f"Agent {agent} conflicts with {conflicts} in same parallel phase")
                        result["valid"] = False
        processed.update(phase.agents)

    parallel_phases = [p for p in phases if p.execution_mode == ExecutionMode.PARALLEL_SAFE]
    if len(parallel_phases) < len(phases) / 2:
        result["optimization_suggestions"].append("Consider optimizing agent profiles for more parallel execution")

    return result


def get_execution_statistics(
    phases: List[ExecutionPhase],
    agent_profiles: Dict[str, AgentProfile],
) -> Dict[str, Any]:
    total_agents = sum(len(p.agents) for p in phases)
    parallel_agents = sum(len(p.agents) for p in phases if p.execution_mode == ExecutionMode.PARALLEL_SAFE)
    sequential_duration = sum(
        agent_profiles[a].execution_time_estimate
        for p in phases for a in p.agents if a in agent_profiles
    )
    parallel_duration = sum(p.estimated_duration for p in phases)
    efficiency = ((sequential_duration - parallel_duration) / sequential_duration * 100) if sequential_duration > 0 else 0
    return {
        "total_phases": len(phases),
        "total_agents": total_agents,
        "parallel_agents": parallel_agents,
        "parallelization_rate": (parallel_agents / total_agents * 100) if total_agents > 0 else 0,
        "sequential_duration": sequential_duration,
        "parallel_duration": parallel_duration,
        "efficiency_gain": efficiency,
    }


# ---------------------------------------------------------------------------
# Conflict detection and topology for legacy API
# ---------------------------------------------------------------------------

def detect_conflicts_in(
    agents: List[str],
    agent_profiles: Dict[str, AgentProfile],
) -> List[ResourceConflict]:
    conflicts: List[ResourceConflict] = []
    unique = list(dict.fromkeys(agents))
    for i, agent in enumerate(unique):
        profile = agent_profiles.get(agent)
        if not profile:
            continue
        for other in unique[i + 1:]:
            other_profile = agent_profiles.get(other)
            if not other_profile:
                continue
            if other in profile.conflicts_with or agent in other_profile.conflicts_with:
                conflicts.append(ResourceConflict(
                    agent1=agent, agent2=other,
                    resource="file_system", severity="high", resolution="sequential",
                ))
    return conflicts


def topological_sort_agents(
    agents: List[str],
    agent_dependencies: Dict[str, AgentDependency],
) -> List[str]:
    unique = list(dict.fromkeys(agents))
    graph: Dict[str, List[str]] = {
        a: [d for d in (agent_dependencies[a].depends_on if a in agent_dependencies else []) if d in unique]
        for a in unique
    }
    in_degree = {a: len(deps) for a, deps in graph.items()}
    dependents: Dict[str, List[str]] = {a: [] for a in unique}
    for a, deps in graph.items():
        for d in deps:
            dependents.setdefault(d, []).append(a)

    queue = [a for a in unique if in_degree.get(a, 0) == 0]
    result: List[str] = []
    while queue:
        current = queue.pop(0)
        result.append(current)
        for dep in dependents.get(current, []):
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    return result if len(result) == len(unique) else unique


def optimize_parallel_groups(
    agents: List[str],
    agent_profiles: Dict[str, AgentProfile],
    agent_dependencies: Dict[str, AgentDependency],
) -> List[ParallelGroup]:
    order = topological_sort_agents(agents, agent_dependencies)
    groups: List[ParallelGroup] = []
    for agent in order:
        profile = agent_profiles.get(agent)
        placed = False
        if profile and profile.parallel_safe:
            for group in groups:
                all_conflicts = detect_conflicts_in(group.agents + [agent], agent_profiles)
                conflict_set = {c.agent1 for c in all_conflicts} | {c.agent2 for c in all_conflicts}
                deps_ok = all(d not in group.agents for d in profile.dependencies)
                if not conflict_set and deps_ok:
                    group.agents.append(agent)
                    group.estimated_duration = max(group.estimated_duration, profile.execution_time_estimate)
                    group.resource_requirements["cpu"] = group.resource_requirements.get("cpu", 0) + 1
                    placed = True
                    break
        if not placed:
            groups.append(ParallelGroup(
                agents=[agent],
                estimated_duration=profile.execution_time_estimate if profile else 10.0,
                resource_requirements={"cpu": 1, "memory": 512},
            ))
    return groups


def estimate_total_execution_time(
    agents: List[str],
    complexity: str,
    risk_level: str,
    agent_profiles: Dict[str, AgentProfile],
    agent_dependencies: Dict[str, AgentDependency],
) -> float:
    complexity_factor = {"low": 0.8, "medium": 1.0, "high": 1.3}.get(complexity, 1.0)
    risk_factor = {"low": 1.0, "medium": 1.1, "critical": 1.25}.get(risk_level, 1.0)
    groups = optimize_parallel_groups(agents, agent_profiles, agent_dependencies)
    return sum(g.estimated_duration for g in groups) * complexity_factor * risk_factor


def build_legacy_execution_plan(
    agents: List[str],
    task_description: str,
    complexity: str,
    risk_level: str,
    agent_profiles: Dict[str, AgentProfile],
    agent_dependencies: Dict[str, AgentDependency],
) -> ExecutionPlan:
    if not agents:
        return ExecutionPlan(
            parallel_groups=[], execution_order=[],
            estimated_total_duration=0, resource_conflicts=[], optimization_applied=False,
        )
    order = topological_sort_agents(agents, agent_dependencies)
    groups = optimize_parallel_groups(order, agent_profiles, agent_dependencies)
    duration = estimate_total_execution_time(order, complexity, risk_level, agent_profiles, agent_dependencies)
    conflicts = detect_conflicts_in(order, agent_profiles)
    return ExecutionPlan(
        parallel_groups=groups,
        execution_order=order,
        estimated_total_duration=duration,
        resource_conflicts=conflicts,
        optimization_applied=len(groups) < len(order),
    )
