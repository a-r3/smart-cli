"""Intelligent Execution Planner - Smart agent scheduling with dependency management."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

# import networkx as nx  # Using simple dependency resolution instead
from rich.console import Console

console = Console()


class AgentCapability(Enum):
    """Agent capabilities for intelligent planning."""

    READ_ONLY = "read_only"  # Can read files safely
    FILE_CREATION = "file_creation"  # Creates new files
    FILE_MODIFICATION = "file_modification"  # Modifies existing files
    ANALYSIS = "analysis"  # Analyzes code/projects
    ARCHITECTURE = "architecture"  # Designs system structure
    CODE_GENERATION = "code_generation"  # Generates code
    TESTING = "testing"  # Runs tests
    REVIEW = "review"  # Reviews code quality


class ExecutionMode(Enum):
    """Execution modes for different scenarios."""

    SEQUENTIAL = "sequential"  # One by one execution
    PARALLEL_SAFE = "parallel_safe"  # Parallel with no conflicts
    HYBRID = "hybrid"  # Mix of sequential and parallel


@dataclass
class AgentDependency:
    """Compatibility dependency contract expected by older tests."""

    agent: str
    depends_on: List[str] = field(default_factory=list)
    provides: List[str] = field(default_factory=list)
    conflicts_with: List[str] = field(default_factory=list)
    priority: int = 1


@dataclass
class ParallelGroup:
    """Compatibility execution group contract expected by older tests."""

    agents: List[str]
    estimated_duration: float
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ResourceConflict:
    """Compatibility resource conflict contract expected by older tests."""

    agent1: str
    agent2: str
    resource: str
    severity: str
    resolution: str


@dataclass
class ExecutionPlan:
    """Compatibility execution plan contract expected by older tests."""

    parallel_groups: List[ParallelGroup]
    execution_order: List[str]
    estimated_total_duration: float
    resource_conflicts: List[ResourceConflict]
    optimization_applied: bool = False


@dataclass
class AgentProfile:
    """Comprehensive agent profile for intelligent planning."""

    name: str
    capabilities: List[AgentCapability]
    dependencies: List[str]  # Which agents must run before this one
    conflicts_with: List[str]  # Which agents cannot run simultaneously
    resource_requirements: List[str]  # What resources this agent needs
    execution_time_estimate: float  # Estimated execution time
    parallel_safe: bool = False  # Can this agent run in parallel?
    priority_level: int = 1  # 1=low, 5=critical


@dataclass
class ExecutionPhase:
    """A phase in the execution plan."""

    phase_number: int
    agents: List[str]
    execution_mode: ExecutionMode
    estimated_duration: float
    dependencies_satisfied: List[str]
    resource_locks_needed: List[str]


class IntelligentExecutionPlanner:
    """Advanced execution planner with dependency management."""

    def __init__(self):
        # Agent profiles with detailed capabilities
        self.agent_profiles = {
            "analyzer": AgentProfile(
                name="analyzer",
                capabilities=[AgentCapability.READ_ONLY, AgentCapability.ANALYSIS],
                dependencies=[],  # No dependencies - can run first
                conflicts_with=[],  # Safe with everyone
                resource_requirements=["project_files"],
                execution_time_estimate=30.0,
                parallel_safe=True,  # Can run with other read-only agents
                priority_level=2,
            ),
            "architect": AgentProfile(
                name="architect",
                capabilities=[AgentCapability.ARCHITECTURE, AgentCapability.ANALYSIS],
                dependencies=["analyzer"],  # Needs analysis first
                conflicts_with=[],
                resource_requirements=["project_files"],
                execution_time_estimate=45.0,
                parallel_safe=False,  # Architecture should be planned alone
                priority_level=4,  # High priority
            ),
            "modifier": AgentProfile(
                name="modifier",
                capabilities=[
                    AgentCapability.FILE_CREATION,
                    AgentCapability.FILE_MODIFICATION,
                    AgentCapability.CODE_GENERATION,
                ],
                dependencies=["architect"],  # Needs architecture first
                conflicts_with=[
                    "tester"
                ],  # Cannot run while tester is testing same files
                resource_requirements=["file_system_write"],
                execution_time_estimate=60.0,
                parallel_safe=False,  # File creation is sensitive
                priority_level=3,
            ),
            "tester": AgentProfile(
                name="tester",
                capabilities=[AgentCapability.TESTING],
                dependencies=["modifier"],  # Needs files to test
                conflicts_with=[
                    "modifier"
                ],  # Cannot test while files are being modified
                resource_requirements=["file_system_read", "test_environment"],
                execution_time_estimate=35.0,
                parallel_safe=True,  # Can run with reviewer
                priority_level=2,
            ),
            "reviewer": AgentProfile(
                name="reviewer",
                capabilities=[AgentCapability.READ_ONLY, AgentCapability.REVIEW],
                dependencies=["modifier"],  # Needs code to review
                conflicts_with=[],  # Safe with everyone (read-only)
                resource_requirements=["project_files"],
                execution_time_estimate=25.0,
                parallel_safe=True,  # Safe to run in parallel
                priority_level=1,
            ),
        }

        # Execution scenarios with different strategies
        self.execution_scenarios = {
            "simple_analysis": {"agents": ["analyzer"], "strategy": "single_agent"},
            "quick_review": {
                "agents": ["analyzer", "reviewer"],
                "strategy": "parallel_readonly",
            },
            "full_implementation": {
                "agents": ["analyzer", "architect", "modifier", "tester", "reviewer"],
                "strategy": "smart_pipeline",
            },
            "code_generation": {
                "agents": ["analyzer", "modifier"],
                "strategy": "sequential_creation",
            },
        }
        self.agent_dependencies = {
            "analyzer": AgentDependency(
                agent="analyzer",
                depends_on=[],
                provides=["analysis"],
                conflicts_with=[],
                priority=2,
            ),
            "architect": AgentDependency(
                agent="architect",
                depends_on=["analyzer"],
                provides=["architecture"],
                conflicts_with=[],
                priority=4,
            ),
            "modifier": AgentDependency(
                agent="modifier",
                depends_on=["analyzer"],
                provides=["code_changes"],
                conflicts_with=["tester"],
                priority=3,
            ),
            "tester": AgentDependency(
                agent="tester",
                depends_on=["modifier"],
                provides=["test_results"],
                conflicts_with=["modifier"],
                priority=2,
            ),
            "reviewer": AgentDependency(
                agent="reviewer",
                depends_on=["tester"],
                provides=["review_feedback"],
                conflicts_with=[],
                priority=1,
            ),
        }

    def create_intelligent_execution_plan(
        self, agent_tasks: List[Dict[str, Any]], scenario_hint: str = None
    ) -> List[ExecutionPhase]:
        """Create intelligent execution plan based on agent dependencies and capabilities."""

        console.print(
            f"🧠 [bold blue]Creating intelligent execution plan...[/bold blue]"
        )

        # Extract agent names from tasks
        agent_names = [task.get("agent") for task in agent_tasks]

        # Detect scenario if not provided
        if not scenario_hint:
            scenario_hint = self._detect_execution_scenario(agent_names)

        console.print(f"📋 [blue]Detected scenario: {scenario_hint}[/blue]")

        # Create dependency graph
        dependency_graph = self._create_dependency_graph(agent_names)

        # Generate execution phases using topological sort
        execution_phases = self._generate_execution_phases(
            dependency_graph, agent_tasks
        )

        # Optimize for parallel execution where safe
        optimized_phases = self._optimize_for_parallel_execution(execution_phases)

        # Display execution plan
        self._display_execution_plan(optimized_phases)

        return optimized_phases

    def _detect_execution_scenario(self, agent_names: List[str]) -> str:
        """Detect execution scenario based on agent combination."""
        agent_set = set(agent_names)

        # Check for known scenarios
        for scenario, config in self.execution_scenarios.items():
            if set(config["agents"]) == agent_set:
                return scenario

        # Classify based on agent types
        if len(agent_names) == 1:
            return "single_agent"
        elif all(
            self.agent_profiles[agent].parallel_safe
            for agent in agent_names
            if agent in self.agent_profiles
        ):
            return "parallel_readonly"
        elif "modifier" in agent_names and "tester" in agent_names:
            return "full_implementation"
        else:
            return "custom_scenario"

    def _create_dependency_graph(self, agent_names: List[str]) -> Dict[str, List[str]]:
        """Create dependency graph using simple dictionary structure."""
        graph = {}

        # Initialize graph
        for agent in agent_names:
            if agent in self.agent_profiles:
                graph[agent] = self.agent_profiles[agent].dependencies.copy()

        return graph

    def _topological_sort(self, graph: Dict[str, List[str]]) -> List[str]:
        """Simple topological sort implementation."""
        # Calculate in-degrees
        in_degree = {node: 0 for node in graph}

        for node in graph:
            for dep in graph[node]:
                if dep in in_degree:
                    in_degree[dep] += 1

        # Find nodes with no incoming edges
        queue = [node for node in in_degree if in_degree[node] == 0]
        result = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            # Remove edges from this node
            for dependent in graph:
                if node in graph[dependent]:
                    in_degree[dependent] -= 1
                    if in_degree[dependent] == 0:
                        queue.append(dependent)

        # Check if all nodes are processed (no cycles)
        if len(result) != len(graph):
            return []  # Cycle detected

        return result

    def _generate_execution_phases(
        self, dependency_graph: Dict[str, List[str]], agent_tasks: List[Dict[str, Any]]
    ) -> List[ExecutionPhase]:
        """Generate execution phases using simple topological sorting."""
        # Simple topological sort implementation
        topo_order = self._topological_sort(dependency_graph)

        if not topo_order:
            console.print(
                "⚠️ [yellow]Circular dependency detected, using fallback ordering[/yellow]"
            )
            topo_order = list(dependency_graph.keys())

        # Create task mapping
        task_map = {task.get("agent"): task for task in agent_tasks}

        # Group agents into phases based on dependencies and conflicts
        phases = []
        processed_agents = set()

        phase_number = 1

        while len(processed_agents) < len(topo_order):
            current_phase_agents = []

            for agent in topo_order:
                if agent in processed_agents:
                    continue

                # Check if all dependencies are satisfied
                if agent in self.agent_profiles:
                    profile = self.agent_profiles[agent]
                    dependencies_satisfied = all(
                        dep in processed_agents or dep not in topo_order
                        for dep in profile.dependencies
                    )

                    if dependencies_satisfied:
                        # Check conflicts with agents already in current phase
                        has_conflicts = any(
                            conflict in current_phase_agents
                            for conflict in profile.conflicts_with
                        )

                        if not has_conflicts:
                            current_phase_agents.append(agent)

            if current_phase_agents:
                # Determine execution mode for this phase
                execution_mode = self._determine_phase_execution_mode(
                    current_phase_agents
                )

                # Calculate estimated duration
                estimated_duration = self._calculate_phase_duration(
                    current_phase_agents, execution_mode
                )

                # Get satisfied dependencies
                satisfied_deps = list(processed_agents)

                # Get resource locks needed
                resource_locks = self._get_required_resource_locks(current_phase_agents)

                phase = ExecutionPhase(
                    phase_number=phase_number,
                    agents=current_phase_agents,
                    execution_mode=execution_mode,
                    estimated_duration=estimated_duration,
                    dependencies_satisfied=satisfied_deps,
                    resource_locks_needed=resource_locks,
                )

                phases.append(phase)
                processed_agents.update(current_phase_agents)
                phase_number += 1
            else:
                # No agents can be processed - break to avoid infinite loop
                remaining = set(topo_order) - processed_agents
                console.print(
                    f"⚠️ [yellow]Cannot process remaining agents: {remaining}[/yellow]"
                )
                break

        return phases

    def _determine_phase_execution_mode(self, agents: List[str]) -> ExecutionMode:
        """Determine execution mode for a phase."""
        if len(agents) == 1:
            return ExecutionMode.SEQUENTIAL

        # Check if all agents in phase are parallel-safe
        all_parallel_safe = all(
            self.agent_profiles[agent].parallel_safe
            for agent in agents
            if agent in self.agent_profiles
        )

        if all_parallel_safe:
            return ExecutionMode.PARALLEL_SAFE
        else:
            return ExecutionMode.HYBRID

    def _calculate_phase_duration(
        self, agents: List[str], execution_mode: ExecutionMode
    ) -> float:
        """Calculate estimated phase duration."""
        if not agents:
            return 0.0

        execution_times = [
            self.agent_profiles[agent].execution_time_estimate
            for agent in agents
            if agent in self.agent_profiles
        ]

        if execution_mode == ExecutionMode.PARALLEL_SAFE:
            # Parallel execution - duration is the maximum time
            return max(execution_times) if execution_times else 30.0
        else:
            # Sequential execution - duration is sum of times
            return sum(execution_times) if execution_times else 30.0

    def _get_required_resource_locks(self, agents: List[str]) -> List[str]:
        """Get required resource locks for agents in phase."""
        resource_locks = set()

        for agent in agents:
            if agent in self.agent_profiles:
                resource_locks.update(self.agent_profiles[agent].resource_requirements)

        return list(resource_locks)

    def _optimize_for_parallel_execution(
        self, phases: List[ExecutionPhase]
    ) -> List[ExecutionPhase]:
        """Optimize phases for better parallel execution."""
        optimized_phases = []

        for phase in phases:
            # Check if we can split phase for better parallelization
            if len(phase.agents) > 1 and phase.execution_mode == ExecutionMode.HYBRID:

                # Separate parallel-safe from non-parallel-safe agents
                parallel_safe_agents = []
                non_parallel_safe_agents = []

                for agent in phase.agents:
                    if agent in self.agent_profiles:
                        if self.agent_profiles[agent].parallel_safe:
                            parallel_safe_agents.append(agent)
                        else:
                            non_parallel_safe_agents.append(agent)

                # Create separate phases if beneficial
                if parallel_safe_agents and non_parallel_safe_agents:
                    # Phase for parallel-safe agents
                    if parallel_safe_agents:
                        parallel_phase = ExecutionPhase(
                            phase_number=phase.phase_number,
                            agents=parallel_safe_agents,
                            execution_mode=ExecutionMode.PARALLEL_SAFE,
                            estimated_duration=self._calculate_phase_duration(
                                parallel_safe_agents, ExecutionMode.PARALLEL_SAFE
                            ),
                            dependencies_satisfied=phase.dependencies_satisfied,
                            resource_locks_needed=self._get_required_resource_locks(
                                parallel_safe_agents
                            ),
                        )
                        optimized_phases.append(parallel_phase)

                    # Phase for non-parallel-safe agents
                    if non_parallel_safe_agents:
                        sequential_phase = ExecutionPhase(
                            phase_number=phase.phase_number + 0.5,  # Sub-phase
                            agents=non_parallel_safe_agents,
                            execution_mode=ExecutionMode.SEQUENTIAL,
                            estimated_duration=self._calculate_phase_duration(
                                non_parallel_safe_agents, ExecutionMode.SEQUENTIAL
                            ),
                            dependencies_satisfied=phase.dependencies_satisfied
                            + parallel_safe_agents,
                            resource_locks_needed=self._get_required_resource_locks(
                                non_parallel_safe_agents
                            ),
                        )
                        optimized_phases.append(sequential_phase)
                else:
                    optimized_phases.append(phase)
            else:
                optimized_phases.append(phase)

        return optimized_phases

    def _display_execution_plan(self, phases: List[ExecutionPhase]):
        """Display the execution plan in a readable format."""
        console.print("\n📋 [bold blue]INTELLIGENT EXECUTION PLAN[/bold blue]")
        console.print("=" * 60)

        total_duration = 0

        for phase in phases:
            console.print(
                f"\n🔸 [bold yellow]Phase {phase.phase_number:.1f}[/bold yellow] - {phase.execution_mode.value.upper()}"
            )
            console.print(f"   Agents: {', '.join(phase.agents)}")
            console.print(f"   Duration: {phase.estimated_duration:.1f}s")
            console.print(
                f"   Dependencies: {', '.join(phase.dependencies_satisfied) if phase.dependencies_satisfied else 'None'}"
            )

            if phase.execution_mode == ExecutionMode.PARALLEL_SAFE:
                console.print("   ⚡ [green]Parallel execution (safe)[/green]")
            elif phase.execution_mode == ExecutionMode.SEQUENTIAL:
                console.print("   🔄 [blue]Sequential execution[/blue]")
            else:
                console.print("   🔀 [yellow]Hybrid execution[/yellow]")

            total_duration += phase.estimated_duration

        console.print(
            f"\n⏱️ [bold green]Total Estimated Duration: {total_duration:.1f}s[/bold green]"
        )
        console.print("=" * 60)

    def validate_execution_plan(self, phases: List[ExecutionPhase]) -> Dict[str, Any]:
        """Validate the execution plan for correctness."""
        validation_result = {
            "valid": True,
            "warnings": [],
            "errors": [],
            "optimization_suggestions": [],
        }

        all_agents_in_plan = set()
        processed_agents = set()

        for phase in phases:
            all_agents_in_plan.update(phase.agents)

            # Check dependency satisfaction
            for agent in phase.agents:
                if agent in self.agent_profiles:
                    profile = self.agent_profiles[agent]

                    # Check if dependencies are satisfied
                    unsatisfied_deps = [
                        dep
                        for dep in profile.dependencies
                        if dep not in processed_agents and dep in all_agents_in_plan
                    ]

                    if unsatisfied_deps:
                        validation_result["errors"].append(
                            f"Agent {agent} has unsatisfied dependencies: {unsatisfied_deps}"
                        )
                        validation_result["valid"] = False

            # Check for conflicts within phase
            if phase.execution_mode == ExecutionMode.PARALLEL_SAFE:
                for agent in phase.agents:
                    if agent in self.agent_profiles:
                        profile = self.agent_profiles[agent]
                        conflicts_in_phase = [
                            conflict
                            for conflict in profile.conflicts_with
                            if conflict in phase.agents
                        ]

                        if conflicts_in_phase:
                            validation_result["errors"].append(
                                f"Agent {agent} conflicts with {conflicts_in_phase} in same parallel phase"
                            )
                            validation_result["valid"] = False

            processed_agents.update(phase.agents)

        # Check for optimization opportunities
        parallel_phases = [
            p for p in phases if p.execution_mode == ExecutionMode.PARALLEL_SAFE
        ]
        if len(parallel_phases) < len(phases) / 2:
            validation_result["optimization_suggestions"].append(
                "Consider optimizing agent profiles for more parallel execution"
            )

        return validation_result

    def get_execution_statistics(self, phases: List[ExecutionPhase]) -> Dict[str, Any]:
        """Get execution plan statistics."""
        total_agents = sum(len(phase.agents) for phase in phases)
        parallel_agents = sum(
            len(phase.agents)
            for phase in phases
            if phase.execution_mode == ExecutionMode.PARALLEL_SAFE
        )

        sequential_duration = sum(
            sum(
                self.agent_profiles[agent].execution_time_estimate
                for agent in phase.agents
                if agent in self.agent_profiles
            )
            for phase in phases
        )

        parallel_duration = sum(phase.estimated_duration for phase in phases)

        efficiency = (
            ((sequential_duration - parallel_duration) / sequential_duration * 100)
            if sequential_duration > 0
            else 0
        )

        return {
            "total_phases": len(phases),
            "total_agents": total_agents,
            "parallel_agents": parallel_agents,
            "parallelization_rate": (
                (parallel_agents / total_agents * 100) if total_agents > 0 else 0
            ),
            "sequential_duration": sequential_duration,
            "parallel_duration": parallel_duration,
            "efficiency_gain": efficiency,
        }

    def get_agent_dependencies(self, agent: str) -> AgentDependency:
        """Return dependency metadata for one agent."""
        return self.agent_dependencies.get(agent, AgentDependency(agent=agent))

    def detect_conflicts(self, agents: List[str]) -> List[ResourceConflict]:
        """Detect pairwise resource conflicts among agents."""
        conflicts: List[ResourceConflict] = []
        unique_agents = list(dict.fromkeys(agents))
        for index, agent in enumerate(unique_agents):
            profile = self.agent_profiles.get(agent)
            if not profile:
                continue
            for other in unique_agents[index + 1 :]:
                other_profile = self.agent_profiles.get(other)
                if not other_profile:
                    continue
                if other in profile.conflicts_with or agent in other_profile.conflicts_with:
                    conflicts.append(
                        ResourceConflict(
                            agent1=agent,
                            agent2=other,
                            resource="file_system",
                            severity="high",
                            resolution="sequential",
                        )
                    )
        return conflicts

    def topological_sort(self, agents: List[str]) -> List[str]:
        """Return a dependency-respecting execution order for agents."""
        unique_agents = list(dict.fromkeys(agents))
        graph: Dict[str, List[str]] = {}
        for agent in unique_agents:
            dependency = self.agent_dependencies.get(agent)
            graph[agent] = [
                depends_on
                for depends_on in (dependency.depends_on if dependency else [])
                if depends_on in unique_agents
            ]

        in_degree = {agent: len(dependencies) for agent, dependencies in graph.items()}
        dependents: Dict[str, List[str]] = {agent: [] for agent in unique_agents}
        for agent, dependencies in graph.items():
            for dependency_name in dependencies:
                dependents.setdefault(dependency_name, []).append(agent)

        queue = [agent for agent in unique_agents if in_degree.get(agent, 0) == 0]
        result: List[str] = []

        while queue:
            current = queue.pop(0)
            result.append(current)
            for dependent in dependents.get(current, []):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(result) != len(unique_agents):
            return unique_agents

        return result

    def optimize_parallel_execution(self, agents: List[str]) -> List[ParallelGroup]:
        """Group agents into simple parallel-safe batches."""
        execution_order = self.topological_sort(agents)
        groups: List[ParallelGroup] = []

        for agent in execution_order:
            profile = self.agent_profiles.get(agent)
            placed = False

            if profile and profile.parallel_safe:
                for group in groups:
                    group_conflicts = {
                        conflict.agent1
                        for conflict in self.detect_conflicts(group.agents + [agent])
                    } | {
                        conflict.agent2
                        for conflict in self.detect_conflicts(group.agents + [agent])
                    }
                    dependencies_satisfied = all(
                        dependency not in group.agents
                        for dependency in profile.dependencies
                    )
                    if not group_conflicts and dependencies_satisfied:
                        group.agents.append(agent)
                        group.estimated_duration = max(
                            group.estimated_duration,
                            profile.execution_time_estimate,
                        )
                        group.resource_requirements["cpu"] = (
                            group.resource_requirements.get("cpu", 0) + 1
                        )
                        placed = True
                        break

            if not placed:
                groups.append(
                    ParallelGroup(
                        agents=[agent],
                        estimated_duration=(
                            profile.execution_time_estimate if profile else 10.0
                        ),
                        resource_requirements={"cpu": 1, "memory": 512},
                    )
                )

        return groups

    def estimate_execution_time(
        self, agents: List[str], complexity: str, risk_level: str
    ) -> float:
        """Estimate execution time for a plan."""
        complexity_factor = {"low": 0.8, "medium": 1.0, "high": 1.3}.get(
            complexity, 1.0
        )
        risk_factor = {"low": 1.0, "medium": 1.1, "critical": 1.25}.get(
            risk_level, 1.0
        )
        groups = self.optimize_parallel_execution(agents)
        base_duration = sum(group.estimated_duration for group in groups)
        return base_duration * complexity_factor * risk_factor

    def create_execution_plan(
        self, agents: List[str], task_description: str, complexity: str, risk_level: str
    ) -> ExecutionPlan:
        """Create the legacy execution plan contract expected by older tests."""
        if not agents:
            return ExecutionPlan(
                parallel_groups=[],
                execution_order=[],
                estimated_total_duration=0,
                resource_conflicts=[],
                optimization_applied=False,
            )

        execution_order = self.topological_sort(agents)
        parallel_groups = self.optimize_parallel_execution(execution_order)
        estimated_total_duration = self.estimate_execution_time(
            execution_order, complexity, risk_level
        )
        resource_conflicts = self.detect_conflicts(execution_order)

        return ExecutionPlan(
            parallel_groups=parallel_groups,
            execution_order=execution_order,
            estimated_total_duration=estimated_total_duration,
            resource_conflicts=resource_conflicts,
            optimization_applied=len(parallel_groups) < len(execution_order),
        )
