"""Shared types for the intelligent execution planner."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List


class AgentCapability(Enum):
    READ_ONLY = "read_only"
    FILE_CREATION = "file_creation"
    FILE_MODIFICATION = "file_modification"
    ANALYSIS = "analysis"
    ARCHITECTURE = "architecture"
    CODE_GENERATION = "code_generation"
    TESTING = "testing"
    REVIEW = "review"


class ExecutionMode(Enum):
    SEQUENTIAL = "sequential"
    PARALLEL_SAFE = "parallel_safe"
    HYBRID = "hybrid"


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
    dependencies: List[str]
    conflicts_with: List[str]
    resource_requirements: List[str]
    execution_time_estimate: float
    parallel_safe: bool = False
    priority_level: int = 1


@dataclass
class ExecutionPhase:
    """A phase in the execution plan."""
    phase_number: int
    agents: List[str]
    execution_mode: ExecutionMode
    estimated_duration: float
    dependencies_satisfied: List[str]
    resource_locks_needed: List[str]
