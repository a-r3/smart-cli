"""Legacy multi-agent compatibility layer for older tests."""

from __future__ import annotations

import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from .ai_client import AIResponse, ChatMessage


class AgentRole(Enum):
    """Legacy agent role identifiers."""

    CODE_GENERATOR = "code_generator"
    CODE_REVIEWER = "code_reviewer"
    DEBUGGER = "debugger"


@dataclass
class AgentTask:
    """Legacy task contract for multi-agent tests."""

    task_id: str
    agent_role: AgentRole
    description: str
    context: Dict[str, Any] = field(default_factory=dict)
    priority: int = 0
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class AgentResult:
    """Legacy agent result contract for multi-agent tests."""

    task_id: str
    agent_role: AgentRole
    success: bool
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    tokens_used: int = 0
    cost_estimate: float = 0.0
    completed_at: datetime = field(default_factory=datetime.now)


class Agent(ABC):
    """Base legacy agent."""

    def __init__(self, role: AgentRole, ai_client):
        self.role = role
        self.ai_client = ai_client
        self.performance_metrics = {
            "tasks_completed": 0,
            "total_execution_time": 0.0,
            "total_tokens_used": 0,
            "total_cost": 0.0,
            "successful_tasks": 0,
            "success_rate": 0.0,
        }

    @abstractmethod
    async def process_task(self, task: AgentTask) -> AgentResult:
        """Process one task."""

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Return the system prompt for the agent."""

    def update_metrics(self, result: AgentResult) -> None:
        """Update performance metrics from one result."""
        self.performance_metrics["tasks_completed"] += 1
        self.performance_metrics["total_execution_time"] += result.execution_time
        self.performance_metrics["total_tokens_used"] += result.tokens_used
        self.performance_metrics["total_cost"] += result.cost_estimate
        if result.success:
            self.performance_metrics["successful_tasks"] += 1

        completed = self.performance_metrics["tasks_completed"]
        successful = self.performance_metrics["successful_tasks"]
        self.performance_metrics["success_rate"] = successful / completed if completed else 0.0

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Return a copy of current performance metrics."""
        return dict(self.performance_metrics)


class CodeGeneratorAgent(Agent):
    """Legacy code generation agent."""

    def __init__(self, ai_client):
        super().__init__(AgentRole.CODE_GENERATOR, ai_client)

    def get_system_prompt(self) -> str:
        return (
            "You are a senior software engineer focused on code generation, "
            "clean architecture, maintainability, and testability."
        )

    def _build_generation_prompt(self, task: AgentTask) -> str:
        context = task.context or {}
        return (
            f"Task: {task.description}\n"
            f"Language: {context.get('language', 'python')}\n"
            f"Class: {context.get('class_name', '')}\n"
            f"Function: {context.get('function_name', '')}\n"
            f"Framework: {context.get('framework', '')}\n"
            f"Additional requirements: {context.get('additional_requirements', '')}\n"
            "Include unit tests and production-ready error handling."
        )

    async def process_task(self, task: AgentTask) -> AgentResult:
        start = time.time()
        try:
            prompt = self._build_generation_prompt(task)
            messages = [
                ChatMessage(role="system", content=self.get_system_prompt()),
                ChatMessage(role="user", content=prompt),
            ]
            response: AIResponse = await self.ai_client.generate_response(messages)
            result = AgentResult(
                task_id=task.task_id,
                agent_role=self.role,
                success=True,
                content=response.content,
                metadata={"model": response.model},
                execution_time=time.time() - start,
                tokens_used=response.usage.get("total_tokens", 0),
                cost_estimate=response.cost_estimate,
            )
        except Exception as exc:
            result = AgentResult(
                task_id=task.task_id,
                agent_role=self.role,
                success=False,
                content=str(exc),
                execution_time=time.time() - start,
            )
        self.update_metrics(result)
        return result


class CodeReviewerAgent(Agent):
    """Legacy code reviewer agent."""

    def __init__(self, ai_client):
        super().__init__(AgentRole.CODE_REVIEWER, ai_client)

    def get_system_prompt(self) -> str:
        return (
            "You are a code review expert focused on security, performance, "
            "maintainability, and OWASP-aligned review practices."
        )

    def _build_review_prompt(self, task: AgentTask) -> str:
        context = task.context or {}
        return (
            f"Task: {task.description}\n"
            f"Language: {context.get('language', 'python')}\n"
            f"Focus: {context.get('focus', 'general')}\n"
            f"File: {context.get('file_path', '')}\n"
            f"Code:\n{context.get('code', '')}\n"
        )

    async def process_review_task(self, task: AgentTask) -> AgentResult:
        start = time.time()
        try:
            prompt = self._build_review_prompt(task)
            messages = [
                ChatMessage(role="system", content=self.get_system_prompt()),
                ChatMessage(role="user", content=prompt),
            ]
            response: AIResponse = await self.ai_client.generate_response(messages)
            result = AgentResult(
                task_id=task.task_id,
                agent_role=self.role,
                success=True,
                content=response.content,
                metadata={"model": response.model},
                execution_time=time.time() - start,
                tokens_used=response.usage.get("total_tokens", 0),
                cost_estimate=response.cost_estimate,
            )
        except Exception as exc:
            result = AgentResult(
                task_id=task.task_id,
                agent_role=self.role,
                success=False,
                content=str(exc),
                execution_time=time.time() - start,
            )
        self.update_metrics(result)
        return result

    async def process_task(self, task: AgentTask) -> AgentResult:
        """Alias to preserve the generic agent interface."""
        return await self.process_review_task(task)


class MultiAgentWorkflow:
    """Legacy workflow orchestration compatibility wrapper."""

    def __init__(self, ai_client):
        self.ai_client = ai_client
        self.agents: Dict[AgentRole, Agent] = {
            AgentRole.CODE_GENERATOR: CodeGeneratorAgent(ai_client),
            AgentRole.CODE_REVIEWER: CodeReviewerAgent(ai_client),
        }
        self.results: Dict[str, AgentResult] = {}

    def register_agent(self, agent: Agent) -> None:
        """Register a custom agent implementation."""
        self.agents[agent.role] = agent

    async def execute_workflow(self, tasks: List[AgentTask]) -> Dict[str, AgentResult]:
        """Execute tasks sequentially."""
        results: Dict[str, AgentResult] = {}
        for task in tasks:
            agent = self.agents.get(task.agent_role)
            if not agent:
                results[task.task_id] = AgentResult(
                    task_id=task.task_id,
                    agent_role=task.agent_role,
                    success=False,
                    content=f"Agent {task.agent_role.value} not available",
                )
                continue
            results[task.task_id] = await agent.process_task(task)
        self.results.update(results)
        return results

    async def execute_parallel_workflow(
        self, tasks: List[AgentTask]
    ) -> Dict[str, AgentResult]:
        """Execute tasks in parallel."""
        async def run_task(task: AgentTask) -> AgentResult:
            agent = self.agents.get(task.agent_role)
            if not agent:
                return AgentResult(
                    task_id=task.task_id,
                    agent_role=task.agent_role,
                    success=False,
                    content=f"Agent {task.agent_role.value} not available",
                )
            return await agent.process_task(task)

        task_results = await asyncio.gather(*(run_task(task) for task in tasks))
        results = {result.task_id: result for result in task_results}
        self.results.update(results)
        return results

    def get_workflow_summary(self) -> Dict[str, Any]:
        """Return aggregate workflow metrics."""
        total_tasks = len(self.results)
        successful_tasks = sum(1 for result in self.results.values() if result.success)
        total_execution_time = sum(result.execution_time for result in self.results.values())
        total_tokens_used = sum(result.tokens_used for result in self.results.values())
        total_estimated_cost = sum(result.cost_estimate for result in self.results.values())
        average_execution_time = total_execution_time / total_tasks if total_tasks else 0

        return {
            "total_tasks": total_tasks,
            "successful_tasks": successful_tasks,
            "success_rate": successful_tasks / total_tasks if total_tasks else 0,
            "total_execution_time": total_execution_time,
            "average_execution_time": average_execution_time,
            "total_tokens_used": total_tokens_used,
            "total_estimated_cost": total_estimated_cost,
            "agents_used": sorted(
                {result.agent_role.value for result in self.results.values()}
            ),
        }

    def get_agent_performance(self) -> Dict[str, Dict[str, Any]]:
        """Return per-agent performance metrics."""
        return {
            role.value: agent.get_performance_metrics()
            for role, agent in self.agents.items()
        }
