"""Smart CLI Multi-Agent Orchestrator."""

import asyncio
import time
from typing import Any, Dict, List, Optional

from rich.console import Console

from .agent_dispatcher import dispatch_agent
from .artifact_recorder import generate_phase_artifacts, record_meta_learning_manifest
from .plan_builder import (
    create_pipeline_steps as _create_pipeline_steps,
    estimate_plan_cost as _estimate_plan_cost,
    get_agent_task_description as _get_agent_task_description,
    phase_key_for_agent as _phase_key_for_agent,
)
from .workflow_display import (
    build_workflow_summary as _build_workflow_summary,
    build_agent_result_summary as _build_agent_result_summary,
    display_agent_results_summary as _display_agent_results_summary,
    display_workflow_summary as _display_workflow_summary,
    infer_workflow_type as _infer_workflow_type,
)

console = Console()


class SimpleEventLogger:
    """Simple event logger that replaces terminal UI to prevent spam."""
    
    def add_event(self, icon, agent, message, level="info"): pass
    def start_phase(self, phase_name): pass
    def update_phase_progress(self, phase_name, progress): pass
    def complete_phase(self, phase_name, success=True): pass
    def start_agent(self, agent_name, task=""): pass
    def update_agent_progress(self, agent_name, progress, metrics=None): pass
    def complete_agent(self, agent_name, success=True): pass


class SmartCLIOrchestrator:
    """Clean orchestrator with smart task classification and adaptive pipeline."""

    def __init__(self, ai_client=None, config_manager=None, execution_logger=None):
        self.smart_cli = None
        if (
            ai_client is not None
            and config_manager is None
            and execution_logger is None
            and hasattr(ai_client, "config")
        ):
            self.smart_cli = ai_client
            config_manager = getattr(ai_client, "config", None)
            ai_client = getattr(ai_client, "ai_client", None)

        self.ai_client = ai_client
        self.config_manager = config_manager
        
        # Initialize AI client if not provided but config manager is available
        if not self.ai_client and self.config_manager:
            from ..utils.simple_ai_client import SimpleOpenRouterClient
            self.ai_client = SimpleOpenRouterClient(self.config_manager)

        # Initialize smart systems
        try:
            from ..core.ai_cost_optimizer import get_cost_optimizer
            from ..core.task_classifier import get_task_classifier
            from ..core.terminal_ui import initialize_terminal_ui
            from ..core.intelligent_execution_planner import IntelligentExecutionPlanner
            from ..core.execution_logger import ExecutionLogger
        except ImportError:
            from core.ai_cost_optimizer import get_cost_optimizer
            from core.task_classifier import get_task_classifier
            from core.terminal_ui import initialize_terminal_ui
            from core.intelligent_execution_planner import IntelligentExecutionPlanner
            from core.execution_logger import ExecutionLogger

        self.cost_optimizer = get_cost_optimizer()
        self.task_classifier = get_task_classifier()
        self.execution_planner = IntelligentExecutionPlanner()
        self.session_cost = 0.0
        self.artifacts = {}
        
        # Initialize execution logger for workflow tracking
        self.execution_logger = execution_logger or ExecutionLogger()

        # Use simple event logger instead of terminal UI to prevent panel spam
        self.ui = SimpleEventLogger()

        # Active agents
        self.active_agents = {
            "architect": "🏗️ System Architect Agent",
            "analyzer": "🔍 Code Analyzer Agent",
            "modifier": "🔧 Code Modifier Agent",
            "tester": "🧪 Testing Agent",
            "reviewer": "👁️ Code Review Agent",
            "metalearning": "🧠 MetaLearning Agent",
        }

        # Initialize agent instances
        self.agents = self._initialize_agents()
        
        # Import extension methods
        self._import_extension_methods()
    def _initialize_agents(self):
        """Initialize agent instances."""
        return {}  # Lazy loading when needed
    
    def _import_extension_methods(self):
        """Import extension methods for orchestrator."""
        try:
            # Import extension methods
            import types
            from .orchestrator_extension import _execute_parallel_pipeline, _execute_single_agent
            
            # Bind extension methods to this instance
            self._execute_parallel_pipeline = types.MethodType(_execute_parallel_pipeline, self)
            self._execute_single_agent = types.MethodType(_execute_single_agent, self)
        except ImportError:
            # Extension methods not available - will fall back to sequential execution
            pass
    
    def _display_smart_cli_banner(self):
        """Display Smart CLI banner and header."""
        from rich.panel import Panel
        from rich.align import Align
        from rich.text import Text
        
        # Create banner text
        banner_text = Text()
        banner_text.append(">S_  ", style="bold green")
        banner_text.append("Smart CLI", style="bold white")
        
        subtitle = Text("Intelligent Code Assistant", style="dim white")
        
        # Simple banner format matching design document
        console.print()
        console.print(">S_  Smart CLI", style="bold cyan")
        console.print("─" * 36)
        console.print("  Intelligent Code Assistant", style="dim")
        console.print("─" * 36)
        console.print()

    def _infer_workflow_type(self, user_request: str) -> str:
        return _infer_workflow_type(user_request)

    def build_workflow_summary(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        return _build_workflow_summary(plan)

    def _display_workflow_summary(self, summary: Dict[str, Any]) -> None:
        _display_workflow_summary(summary, console)

    def build_agent_result_summary(
        self, agent_type: str, result: Optional[Any]
    ) -> Dict[str, str]:
        return _build_agent_result_summary(
            agent_type, result, self.active_agents, self._phase_key_for_agent
        )

    def _display_agent_results_summary(
        self, agent_results: List[tuple]
    ) -> None:
        _display_agent_results_summary(
            agent_results, self.active_agents, self._phase_key_for_agent, console
        )

    async def create_detailed_plan(self, user_request: str) -> Dict[str, Any]:
        """Create intelligent plan with advanced execution planning."""
        # Display Smart CLI banner
        self._display_smart_cli_banner()
        
        console.print("🤖 [bold cyan]Orchestrator:[/bold cyan] Initializing Smart CLI...")
        console.print("   - Collecting context")
        console.print("   - Classifying request")
        
        self.ui.add_event("🤖", "Orchestrator", "Initializing Smart CLI execution")
        self.ui.add_event("📋", "Orchestrator", "Collecting context and classifying request")

        # Classify task complexity and risk
        complexity, risk = self.task_classifier.classify_task(user_request)
        pipeline = self.task_classifier.get_recommended_pipeline(complexity, risk)
        models = self.task_classifier.get_recommended_models(complexity, risk)

        # Create intelligent execution plan
        # Convert pipeline to agent_tasks format
        agent_tasks = []
        for agent in pipeline:
            agent_tasks.append({
                "agent": agent,
                "description": f"{agent} task for: {user_request}",
                "complexity": complexity.value
            })
        
        execution_plan = self.execution_planner.create_intelligent_execution_plan(
            agent_tasks=agent_tasks,
            scenario_hint=f"{complexity.value} {user_request}"
        )

        # Create execution phase plan  
        phase_names = []
        for agent in pipeline:
            if agent == "analyzer":
                phase_names.append("Analysis")
            elif agent == "architect":
                phase_names.append("Architecture")
            elif agent == "modifier":
                phase_names.append("Implementation")
            elif agent == "tester":
                phase_names.append("Testing")
            elif agent == "reviewer":
                phase_names.append("Review")
        
        console.print(f"   - Creating phase plan ({' → '.join(phase_names)})")
        
        # Log orchestrator analysis results
        console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] Task classified as [bold]{complexity.value}[/bold] complexity, [bold]{risk.value}[/bold] risk")
        
        self.ui.add_event("📊", "Orchestrator", f"Task classified: {complexity.value} complexity, {risk.value} risk")
        
        # Show execution strategy
        if execution_plan and isinstance(execution_plan, list):
            parallel_phases = [p for p in execution_plan if p.execution_mode.value == "parallel_safe"]
            if parallel_phases:
                parallel_info = f"Parallel execution: {len(parallel_phases)} phases"
                console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] {parallel_info}")
                self.ui.add_event("⚡", "Orchestrator", parallel_info)
        
        pipeline_display = ' → '.join([agent.title() for agent in pipeline])
        console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] Pipeline: {pipeline_display}")
        self.ui.add_event("📋", "Orchestrator", f"Execution pipeline: {pipeline_display}")

        workflow_type = self._infer_workflow_type(user_request)

        # Create adaptive plan with intelligent execution
        plan = {
            "title": f"Smart {complexity.value.title()} Plan",
            "complexity": complexity.value,
            "risk": risk.value,
            "pipeline": pipeline,
            "models": models,
            "execution_plan": execution_plan,
            "steps": self._create_pipeline_steps(pipeline, models, complexity, risk),
            "estimated_cost": self._estimate_plan_cost(pipeline, models),
            "workflow_type": workflow_type,
        }

        plan["workflow_summary"] = self.build_workflow_summary(plan)

        console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] Estimated cost: [bold green]${plan['estimated_cost']:.3f}[/bold green]")
        self.ui.add_event("💰", "Orchestrator", f"Estimated cost: ${plan['estimated_cost']:.3f}")
        console.print(
            f"🤖 [bold cyan]Orchestrator:[/bold cyan] Workflow: [bold]{workflow_type}[/bold]"
        )
        self._display_workflow_summary(plan["workflow_summary"])
        
        console.print()  # Add spacing
        return plan

    def _create_pipeline_steps(self, pipeline, models, complexity, risk):
        return _create_pipeline_steps(pipeline, models, complexity, risk)

    def _estimate_plan_cost(self, pipeline, models) -> float:
        return _estimate_plan_cost(pipeline, self.cost_optimizer)

    async def execute_task_plan(
        self, plan: Dict[str, Any], original_request: str
    ) -> bool:
        """Execute smart adaptive pipeline."""
        if "pipeline" not in plan:
            self.ui.add_event(
                "⚠️",
                "System",
                "No smart pipeline found, using basic execution",
                "warning",
            )
            return False

        return await self._execute_smart_pipeline(plan, original_request)

    def _record_meta_learning_manifest(self) -> None:
        record_meta_learning_manifest(self.artifacts)

    async def _execute_smart_pipeline(
        self, plan: Dict[str, Any], original_request: str
    ) -> bool:
        """Execute smart adaptive pipeline with intelligent execution planning."""

        pipeline = plan.get("pipeline", [])
        models = plan.get("models", {})
        complexity = plan.get("complexity", "medium")
        risk = plan.get("risk", "medium")
        execution_plan = plan.get("execution_plan")

        # Map pipeline to phases
        phase_mapping = {
            "analyzer": "analysis",
            "architect": "architecture", 
            "modifier": "implementation",
            "tester": "testing",
            "reviewer": "review",
            "metalearning": "metalearning",
        }
        
        # Record workflow initiation in execution logger
        workflow_type = plan.get("workflow_type", "generic")
        self.execution_logger.record_workflow_type(workflow_type)
        
        workflow_summary = plan.get("workflow_summary")
        if workflow_summary:
            self.execution_logger.record_orchestrator_summary(workflow_summary)

        # Start UI with Live display - disable for clean orchestrator output
        execution_start_time = time.time()
        
        # Clean orchestrator execution without complex UI
        console.print("🤖 [bold cyan]Orchestrator:[/bold cyan] Starting execution pipeline")
        if workflow_summary:
            self._display_workflow_summary(workflow_summary)

        results = []
        total_cost = 0.0

        # Execute using intelligent execution planner if available
        if execution_plan and isinstance(execution_plan, list) and len(execution_plan) > 0:
            console.print("🤖 [bold cyan]Orchestrator:[/bold cyan] Using intelligent execution plan")
            results = await self._execute_intelligent_pipeline(
                execution_plan, original_request, complexity, risk
            )
            total_cost = sum(getattr(r, 'cost', 0.01) for r in results)
        else:
            # Fall back to sequential execution
            success_count = 0
            for i, agent_type in enumerate(pipeline, 1):
                # Start corresponding phase
                phase_name = phase_mapping.get(agent_type, "implementation")
                phase_display_name = phase_name.title()
                
                # Orchestrator dispatch message
                console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] Dispatching phase [{phase_display_name}]")

                # Start agent with enhanced display
                task_desc = self._get_agent_task_description(agent_type)
                agent_display = self.active_agents.get(agent_type, f"{agent_type} Agent")
                console.print(f"{agent_display}: Starting {task_desc.lower()}...")

                start_time = time.time()

                try:
                    # Execute actual agent with progress simulation
                    result = await self._execute_agent_with_progress(
                        agent_type, original_request, complexity, phase_name
                    )

                    results.append(result)
                    duration = time.time() - start_time
                    total_cost += 0.01  # Fallback cost estimate
                    
                    # Record agent execution in log
                    if result:
                        self.execution_logger.record_agent_execution(
                            agent_name=agent_display,
                            agent_type=agent_type,
                            success=result.success,
                            created_files=getattr(result, 'created_files', []) or [],
                            modified_files=getattr(result, 'modified_files', []) or [],
                            errors=getattr(result, 'errors', []) or [],
                            warnings=getattr(result, 'warnings', []) or [],
                            execution_time=duration,
                            output_data=getattr(result, 'output_data', {}),
                        )

                    # Generate and display artifacts
                    self._generate_phase_artifacts(agent_type, phase_name, result)
                    
                    # Orchestrator phase completion message
                    status = "completed successfully" if result.success else "failed"
                    console.print(f"✅ {agent_display} completed → {status}")
                    console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] {phase_display_name} phase {status} ({duration:.1f}s)")
                    
                    # Display artifacts
                    if phase_name in self.artifacts:
                        console.print("Artifacts:")
                        for artifact in self.artifacts[phase_name]:
                            console.print(f"  - {artifact}")
                    
                    # Track successful completions
                    if result.success:
                        success_count += 1
                    
                    # Check if critical task failed
                    if not result.success and risk in ["critical", "high"]:
                        console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] Critical failure detected → stopping pipeline")
                        break
                    
                    # Show next phase message (if not last)
                    if i < len(pipeline):
                        next_agent = pipeline[i]
                        next_phase = phase_mapping.get(next_agent, "implementation").title()
                        console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] Proceeding to {next_phase} phase...")

                except Exception as e:
                    console.print(f"❌ {agent_display} failed: {str(e)}")
                    console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] {phase_display_name} phase failed")
                    # Record error in log
                    self.execution_logger.record_error(f"{agent_type} execution failed: {str(e)}")
                    results.append(None)
                    if risk in ["critical", "high"]:
                        console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] Critical failure → stopping pipeline")
                        break

            # Add Meta Learning phase at the end if successful
            if success_count > 0 and "metalearning" not in pipeline:
                    console.print(f"🤖 [bold cyan]Orchestrator:[/bold cyan] Dispatching phase [Meta Learning]")
                    console.print("🧠 MetaLearning Agent: Recording post-run learning summary")
                    self._record_meta_learning_manifest()
                    console.print("Artifacts:")
                    for artifact in self.artifacts.get("metalearning", []):
                        console.print(f"  - {artifact}")
                    console.print("✅ MetaLearning Agent completed")

        # Show final summary
        success_count = sum(1 for r in results if r.success)
        self.session_cost += total_cost

        # Orchestrator final summary
        total_duration = time.time() - execution_start_time
        
        console.print()
        console.print("🤖 [bold cyan]Orchestrator:[/bold cyan] All phases completed")
        
        # Calculate and display total execution time
        minutes = int(total_duration // 60)
        seconds = int(total_duration % 60)
        time_display = f"{minutes:02d}:{seconds:02d}" if minutes > 0 else f"{seconds}s"
        console.print(f"🎉 [bold green]Project run finished in {time_display}[/bold green]")
        
        self._display_agent_results_summary(list(zip(pipeline, results)))
        
        # Display artifacts summary
        console.print("\n[bold]Artifacts saved to:[/bold]")
        console.print("  ./artifacts/ (phase manifests and any real agent outputs)")
        console.print()
        
        # Record final state and save execution log
        workflow_success = success_count > 0
        self.execution_logger.record_artifacts(self.artifacts)
        self.execution_logger.finalize(success=workflow_success)
        log_path = self.execution_logger.save_to_disk()
        console.print(f"📋 [dim]Execution log saved to: {log_path}[/dim]")

        return workflow_success

    def _generate_phase_artifacts(self, agent_type: str, phase_name: str, result) -> None:
        generate_phase_artifacts(agent_type, phase_name, result, self.artifacts)

    async def _execute_agent_with_progress(self, agent_type: str, original_request: str, complexity: str, phase_name: str):
        """Execute an agent with minimal factual status output."""
        console.print(f"   Status: delegating to {agent_type} agent")

        # Execute the actual agent
        result = await self.delegate_to_agent(
            agent_type,
            ".",
            f"Smart {complexity} task: {original_request}",
            "smart_execution",
        )
        
        return result

    def _get_agent_task_description(self, agent_type: str) -> str:
        return _get_agent_task_description(agent_type)

    async def delegate_to_agent(
        self, agent_type: str, target: str, description: str, action: str = ""
    ) -> Any:
        _cost_ref = [self.session_cost]
        result = await dispatch_agent(
            agent_type, target, description,
            self.ai_client, self.config_manager,
            self.cost_optimizer, self.task_classifier,
            _cost_ref,
        )
        self.session_cost = _cost_ref[0]
        return result

    async def _execute_intelligent_pipeline(self, execution_plan: list, original_request: str, complexity, risk):
        """Execute pipeline using intelligent execution plan phases."""
        results = []
        
        console.print("🤖 [bold cyan]Orchestrator:[/bold cyan] Executing intelligent pipeline phases...")
        
        for phase in execution_plan:
            # Phase name mapping
            phase_names = {
                1: "Analysis Phase",
                2: "Architecture Phase", 
                3: "Implementation Phase",
                4: "Testing & Review Phase"
            }
            phase_name = phase_names.get(phase.phase_number, f"Phase {phase.phase_number}")
            
            console.print(f"\n🤖 [bold cyan]Orchestrator:[/bold cyan] Dispatching [{phase_name}]")
            console.print()
            
            phase_start_time = time.time()
            phase_results = []

            if phase.execution_mode.value == "parallel_safe":
                tasks = []
                for agent in phase.agents:
                    task = self._execute_agent_with_progress(agent, original_request, complexity.value if hasattr(complexity, 'value') else str(complexity), f"Phase {phase.phase_number}")
                    tasks.append(task)
                
                try:
                    phase_results = await asyncio.gather(*tasks, return_exceptions=True)
                    for agent_name, result in zip(phase.agents, phase_results):
                        if isinstance(result, Exception):
                            continue
                        results.append(result)
                        phase_key = self._phase_key_for_agent(agent_name)
                        self._generate_phase_artifacts(agent_name, phase_key, result)
                except Exception as e:
                    console.print(f"⚠️ Phase {phase.phase_number} parallel execution error: {e}")
                    # Continue with next phase
                    
            else:
                # Execute agents sequentially
                for agent in phase.agents:
                    try:
                        result = await self._execute_agent_with_progress(agent, original_request, complexity.value if hasattr(complexity, 'value') else str(complexity), f"Phase {phase.phase_number}")
                        results.append(result)
                        phase_results.append(result)
                        phase_key = self._phase_key_for_agent(agent)
                        self._generate_phase_artifacts(agent, phase_key, result)
                    except Exception as e:
                        console.print(f"⚠️ Agent {agent} error: {e}")
                        # Continue with next agent
            
            # Phase completion message
            phase_duration = time.time() - phase_start_time
            console.print(f"\n🤖 [bold cyan]Orchestrator:[/bold cyan] {phase_name} completed ({phase_duration:.1f}s)")
            
            artifact_paths = []
            for agent_name in phase.agents:
                phase_key = self._phase_key_for_agent(agent_name)
                artifact_paths.extend(self.artifacts.get(phase_key, []))

            if artifact_paths:
                console.print("Artifacts:")
                for artifact in artifact_paths:
                    console.print(f"  - {artifact}")
        
        # Final summary by Orchestrator
        console.print("\n🤖 [bold cyan]Orchestrator:[/bold cyan] All phases completed")
        console.print("─" * 50)
        
        # Calculate total duration
        total_phases = len(execution_plan)
        console.print(f"Pipeline execution finished with {total_phases} phases")
        console.print()
        
        # Phase summary
        phase_names = {1: "Analysis", 2: "Architecture", 3: "Implementation", 4: "Testing & Review"}
        for i, phase in enumerate(execution_plan, 1):
            agent_list = ", ".join([f"{agent.title()} Agent" for agent in phase.agents])
            phase_name = phase_names.get(i, f"Phase {i}")
            console.print(f"- {phase_name}: {agent_list}")

        agent_results = []
        result_index = 0
        for phase in execution_plan:
            for agent in phase.agents:
                if result_index >= len(results):
                    agent_results.append((agent, None))
                else:
                    agent_results.append((agent, results[result_index]))
                result_index += 1
        if agent_results:
            console.print()
            self._display_agent_results_summary(agent_results)
        
        console.print("\nArtifacts saved to:")
        console.print("  ./artifacts/ (phase manifests and any real agent outputs)")
        console.print()
        
        return results

    def _phase_key_for_agent(self, agent_type: str) -> str:
        return _phase_key_for_agent(agent_type)


# Legacy public name retained for compatibility.
Orchestrator = SmartCLIOrchestrator
