"""Enhanced Smart CLI Request Router - Complete mode-aware processing system."""

import asyncio
import os
from typing import Any, Dict, Optional

from rich.console import Console

console = Console()

try:
    from .intelligent_request_classifier import (
        ClassificationResult,
        RequestType,
        get_intelligent_classifier,
    )
    from .mode_manager import get_mode_manager, SmartMode
    from .context_manager import get_context_manager
except ImportError:
    from intelligent_request_classifier import (
        ClassificationResult,
        RequestType,
        get_intelligent_classifier,
    )
    from mode_manager import get_mode_manager, SmartMode
    from context_manager import get_context_manager


class EnhancedRequestRouter:
    """Complete mode-aware request router with intelligent processing."""

    def __init__(self, smart_cli_instance):
        """Initialize enhanced router with full mode support."""
        self.smart_cli = smart_cli_instance
        self.orchestrator = smart_cli_instance.orchestrator
        self.handlers = smart_cli_instance.handlers
        self.command_handler = smart_cli_instance.command_handler
        self.debug = smart_cli_instance.debug

        # Initialize intelligent systems
        self.classifier = get_intelligent_classifier()
        self.mode_manager = get_mode_manager(smart_cli_instance.config)
        self.context_manager = get_context_manager()
        
        # Mode command patterns
        self.mode_commands = {
            "/mode": self._handle_mode_command,
            "/modestatus": self._handle_mode_status,
            "/context": self._handle_context_command,
            "/switch": self._handle_quick_switch
        }

    async def process_request(self, user_input: str) -> bool:
        """Process user request with complete mode awareness."""
        if not user_input.strip():
            return True

        # Handle explicit mode commands first
        if await self._handle_mode_commands(user_input):
            return True

        # Get enhanced context
        context = self._get_enhanced_context()
        current_mode = self.mode_manager.current_mode
        
        # Auto-suggest mode switch if beneficial
        await self._auto_suggest_mode_switch(user_input, context)

        # Process based on current mode
        if current_mode == SmartMode.SMART:
            return await self._process_with_intelligent_classification(user_input, context)
        else:
            return await self._process_in_specific_mode(user_input, current_mode, context)

    def _get_enhanced_context(self) -> Dict[str, any]:
        """Get complete context with mode and historical information."""
        context = self._get_basic_environment_context()
        
        # Add mode information
        current_mode = self.mode_manager.current_mode
        context["current_mode"] = current_mode.value
        context["mode_config"] = self.mode_manager.get_current_config()
        context["mode_permissions"] = self.mode_manager.get_mode_permissions()
        
        # Add context manager data
        mode_context = self.context_manager.get_mode_context(current_mode.value)
        context["mode_context"] = mode_context
        context["context_summary"] = self.context_manager.get_context_summary()
        
        return context
    
    def _get_basic_environment_context(self) -> Dict[str, any]:
        """Get basic environment context."""
        context = {}

        try:
            context["is_git_repo"] = os.path.exists(".git") or os.path.exists("../.git")
        except:
            context["is_git_repo"] = False

        try:
            code_extensions = [".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c"]
            files = os.listdir(".")
            context["has_code_files"] = any(f.endswith(tuple(code_extensions)) for f in files)
        except:
            context["has_code_files"] = False

        try:
            context["current_dir"] = os.path.basename(os.getcwd())
        except (FileNotFoundError, OSError):
            context["current_dir"] = "unknown"

        return context
    
    # Mode Command Handlers
    
    async def _handle_mode_commands(self, user_input: str) -> bool:
        """Handle explicit mode commands."""
        if not user_input.startswith("/"):
            return False
            
        parts = user_input.split()
        command = parts[0]
        
        if command in self.mode_commands:
            handler = self.mode_commands[command]
            await handler(parts[1:] if len(parts) > 1 else [])
            return True
            
        return False
    
    async def _handle_mode_command(self, args: list):
        """Handle /mode command."""
        if not args:
            console.print("🎭 [bold blue]Stable mode-lər:[/bold blue]")
            for mode in self.mode_manager.get_public_modes():
                config = self.mode_manager.mode_configs[mode]
                current_indicator = "✓" if mode == self.mode_manager.current_mode else " "
                console.print(f"{current_indicator} [cyan]{mode.value}[/cyan]: {config.description}")
            experimental_modes = self.mode_manager.get_experimental_modes()
            if experimental_modes:
                console.print("🧪 [bold yellow]Experimental mode-lər:[/bold yellow]")
                for mode in experimental_modes:
                    config = self.mode_manager.mode_configs[mode]
                    current_indicator = "✓" if mode == self.mode_manager.current_mode else " "
                    console.print(f"{current_indicator} [yellow]{mode.value}[/yellow]: {config.description}")
            return
        
        target_mode = args[0]
        reason = " ".join(args[1:]) if len(args) > 1 else "Manual keçid"
        
        if await self.mode_manager.switch_mode(target_mode, reason):
            self.context_manager.update_mode_context(
                target_mode, 
                {"switched_at": target_mode, "reason": reason}
            )
    
    async def _handle_mode_status(self, args: list):
        """Handle /modestatus command."""
        status = self.mode_manager.get_mode_status()
        
        console.print("📊 [bold green]Mode Status:[/bold green]")
        console.print(f"🎯 Hazırkı: [cyan]{status['current_mode']}[/cyan]")
        console.print(f"📝 Təsvir: {status['description']}")
        console.print(f"🧭 Səth: {'stable' if status['is_public'] else 'experimental'}")
        console.print(f"🤖 Model: {status['preferred_model'] or 'Default'}")
        console.print(f"💾 Context: {status['context_size']} token")
        console.print(f"⚙️ Alətlər: {status['tools_count']} mövcud")
        
        if status['previous_mode']:
            console.print(f"⬅️ Əvvəlki: {status['previous_mode']}")

        console.print(f"✅ Stable mode-lər: {', '.join(status['public_modes'])}")
        console.print(f"🧪 Experimental mode-lər: {', '.join(status['experimental_modes'])}")

        context_summary = self.context_manager.get_context_summary()
        console.print(f"📋 Context: {len(context_summary['active_modes'])} aktiv mode")
    
    async def _handle_context_command(self, args: list):
        """Handle /context command."""
        if not args or args[0] == "status":
            summary = self.context_manager.get_context_summary()
            console.print("🧠 [bold magenta]Context Xülasəsi:[/bold magenta]")
            console.print(f"Aktiv mode-lər: {', '.join(summary['active_modes'])}")
            console.print(f"Ortaq yaddaş: {summary['shared_memory_size']} element")
            console.print(f"Çapraz referanslar: {summary['cross_references_count']}")
        
        elif args[0] == "clear":
            mode = args[1] if len(args) > 1 else self.mode_manager.current_mode.value
            self.context_manager.clear_mode_context(mode)
        
        elif args[0] == "optimize":
            self.context_manager.optimize_context_memory()
    
    async def _handle_quick_switch(self, args: list):
        """Handle /switch command."""
        if not args:
            if self.mode_manager.previous_mode:
                await self.mode_manager.switch_mode(
                    self.mode_manager.previous_mode.value, 
                    "Sürətli əvvəlki mode-a keçid"
                )
            else:
                console.print("⚠️ [yellow]Keçmək üçün əvvəlki mode yoxdur[/yellow]")
        else:
            await self._handle_mode_command(args)
    
    async def _auto_suggest_mode_switch(self, user_input: str, context: Dict):
        """Auto-suggest mode switch if beneficial."""
        suggestion = await self.mode_manager.suggest_mode_switch(user_input, context)
        
        if suggestion and suggestion != self.mode_manager.current_mode.value:
            console.print(f"💡 [dim yellow]Təklif: '/mode {suggestion}' bu tapşırıq üçün daha yaxşı ola bilər[/dim yellow]")
    
    # Smart Mode Processing
    
    async def _process_with_intelligent_classification(self, user_input: str, context: Dict) -> bool:
        """Process using intelligent classification (Smart mode)."""
        classification = self.classifier.classify_request(user_input, context)

        if self.debug:
            console.print(f"🔍 [dim]Request: {classification.request_type.value} (confidence: {classification.confidence:.2f})[/dim]")
            console.print(f"💭 [dim]Reasoning: {', '.join(classification.reasoning)}[/dim]")

        try:
            return await self._route_to_processor(classification, user_input, context)
        except Exception as e:
            console.print(f"❌ [red]Request processing error: {str(e)}[/red]")
            if self.debug:
                console.print_exception()
            return True

    def _enrich_plan_with_classification(
        self, plan: Dict[str, Any], classification: ClassificationResult
    ) -> Dict[str, Any]:
        """Attach stable workflow and classification metadata to a plan."""
        if "context_hints" not in plan:
            plan["context_hints"] = classification.context_hints
        plan["confidence"] = classification.confidence
        plan["reasoning"] = classification.reasoning
        plan["suggested_action"] = classification.suggested_action

        workflow_target = classification.context_hints.get("workflow_target")
        workflow_stage = classification.context_hints.get("workflow_stage")
        if workflow_target:
            plan["workflow_target"] = workflow_target
        if workflow_stage:
            plan["workflow_stage"] = workflow_stage

        return plan
    
    async def _route_to_processor(self, classification: ClassificationResult, user_input: str, context: Dict) -> bool:
        """Route request based on intelligent classification."""
        request_type = classification.request_type
        current_mode = self.mode_manager.current_mode
        
        # Update context with classification
        self.context_manager.update_mode_context(
            current_mode.value,
            {
                "last_classification": {
                    "type": request_type.value,
                    "confidence": classification.confidence,
                    "reasoning": classification.reasoning
                }
            }
        )

        # Route based on classification
        if request_type == RequestType.COMMAND:
            return await self._process_command(user_input)
        elif request_type == RequestType.DEVELOPMENT:
            return await self._process_development(user_input, classification, context)
        elif request_type == RequestType.UTILITY:
            return await self._process_utility(user_input, classification, context)
        elif request_type == RequestType.ANALYSIS:
            return await self._process_analysis(user_input, classification, context)
        elif request_type == RequestType.LEARNING:
            return await self._process_learning(user_input, classification, context)
        else:  # CONVERSATION
            return await self._process_conversation(user_input)

        return True
    
    # Specific Mode Processing
    
    async def _process_in_specific_mode(self, user_input: str, mode: SmartMode, context: Dict) -> bool:
        """Process request in specific mode."""
        console.print(f"🎭 [dim blue]{mode.value.title()} Mode[/dim blue]")
        
        # Get and update mode context
        mode_context = self.context_manager.get_mode_context(mode.value)
        self.context_manager.update_mode_context(
            mode.value,
            {"last_request": user_input, "request_time": context.get("timestamp")}
        )
        
        # Route to specific mode handler
        if mode == SmartMode.CODE:
            return await self._process_code_mode(user_input, mode_context)
        elif mode == SmartMode.ANALYSIS:
            return await self._process_analysis_mode(user_input, mode_context)
        elif mode == SmartMode.ARCHITECT:
            return await self._process_architect_mode(user_input, mode_context)
        elif mode == SmartMode.LEARNING:
            return await self._process_learning_mode(user_input, mode_context)
        elif mode == SmartMode.FAST:
            return await self._process_fast_mode(user_input, mode_context)
        elif mode == SmartMode.ORCHESTRATOR:
            return await self._process_orchestrator_mode(user_input, mode_context)
        else:
            return await self._process_with_intelligent_classification(user_input, context)
    
    async def _process_code_mode(self, user_input: str, context: Dict) -> bool:
        """Process in Code mode - development focused."""
        if self.orchestrator:
            console.print("💻 [bold blue]Kod Development Mode → Orchestrator[/bold blue]")
            try:
                plan = await self.orchestrator.create_detailed_plan(user_input)
                plan["mode_context"] = context
                plan["forced_mode"] = "code"
                return await self.orchestrator.execute_task_plan(plan, user_input)
            except Exception as e:
                console.print(f"⚠️ [yellow]Orchestrator xətası: {e}, AI-ya keçid[/yellow]")
        
        return await self._process_conversation(user_input)
    
    async def _process_analysis_mode(self, user_input: str, context: Dict) -> bool:
        """Process in Analysis mode."""
        console.print("🔍 [green]Analysis Mode Activated[/green]")
        
        analysis_prompt = f"Ətraflı analiz et: {user_input}"
        
        if self.orchestrator:
            try:
                plan = await self.orchestrator.create_detailed_plan(analysis_prompt)
                plan["analysis_mode"] = True
                plan["mode_context"] = context
                return await self.orchestrator.execute_task_plan(plan, user_input)
            except Exception:
                pass
        
        return await self._process_conversation(analysis_prompt)
    
    async def _process_architect_mode(self, user_input: str, context: Dict) -> bool:
        """Process in Architect mode."""
        console.print("🏢 [magenta]Architecture Mode Activated[/magenta]")
        
        architect_prompt = f"Sistem arxitekturası baxımından: {user_input}"
        return await self._process_conversation(architect_prompt)
    
    async def _process_learning_mode(self, user_input: str, context: Dict) -> bool:
        """Process in Learning mode."""
        console.print("📚 [yellow]Learning Mode Activated[/yellow]")
        
        learning_prompt = f"Addım-addım izah et: {user_input}"
        return await self._process_conversation(learning_prompt)
    
    async def _process_fast_mode(self, user_input: str, context: Dict) -> bool:
        """Process in Fast mode."""
        console.print("⚡ [red]Fast Mode - Sürətli İşləmə[/red]")
        
        # Try handlers first for quick operations
        for handler in self.handlers:
            try:
                if await handler.handle(user_input):
                    return True
            except Exception:
                continue
        
        return await self._process_conversation(user_input)
    
    async def _process_orchestrator_mode(self, user_input: str, context: Dict) -> bool:
        """Process in Orchestrator mode."""
        console.print("🎭 [bold magenta]Multi-Agent Orchestrator Mode[/bold magenta]")
        
        if not self.orchestrator:
            console.print("⚠️ [yellow]Orchestrator mövcud deyil[/yellow]")
            return await self._process_conversation(user_input)
        
        try:
            plan = await self.orchestrator.create_detailed_plan(user_input)
            plan["orchestrator_mode"] = True
            plan["mode_context"] = context
            plan["multi_agent"] = True
            
            return await self.orchestrator.execute_task_plan(plan, user_input)
        except Exception as e:
            console.print(f"⚠️ [yellow]Orchestrator xətası: {e}[/yellow]")
            return await self._process_conversation(user_input)
    
    # Legacy Processor Methods (kept for compatibility)
    
    async def _process_command(self, user_input: str) -> bool:
        """Process system commands."""
        return await self.command_handler.handle_command(user_input)

    async def _process_development(self, user_input: str, classification: ClassificationResult, context: Dict) -> bool:
        """Process development tasks."""
        if not self.orchestrator:
            console.print("⚠️ [yellow]Orchestrator development üçün mövcud deyil[/yellow]")
            return await self._process_conversation(user_input)

        console.print("🎭 [bold blue]Development Task → Smart CLI Orchestrator[/bold blue]")
        
        try:
            plan = await self.orchestrator.create_detailed_plan(user_input)
            plan = self._enrich_plan_with_classification(plan, classification)

            success = await self.orchestrator.execute_task_plan(plan, user_input)
            if not success:
                console.print("⚠️ [yellow]Orchestrator task uğursuz, AI conversation-a keçid[/yellow]")
                return await self._process_conversation(user_input)

            return True

        except Exception as e:
            console.print(f"⚠️ [yellow]Orchestrator xətası: {str(e)}, AI-ya keçid[/yellow]")
            return await self._process_conversation(user_input)

    async def _process_utility(self, user_input: str, classification: ClassificationResult, context: Dict) -> bool:
        """Process utility operations."""
        console.print(f"🔧 [blue]Utility Operation: {classification.suggested_action}[/blue]")

        # Try handlers with intelligent prioritization
        context_hints = classification.context_hints
        prioritized_handlers = self._prioritize_handlers(self.handlers, context_hints)

        for handler in prioritized_handlers:
            try:
                if await handler.handle(user_input):
                    return True
            except Exception as e:
                if self.debug:
                    console.print(f"⚠️ [dim yellow]Handler {handler.__class__.__name__} xətası: {str(e)}[/dim yellow]")
                continue

        console.print("🤖 [yellow]Spesifik handler tapılmadı, AI conversation-a keçid[/yellow]")
        return await self._process_conversation(user_input)

    async def _process_analysis(self, user_input: str, classification: ClassificationResult, context: Dict) -> bool:
        """Process analysis requests."""
        console.print("🔍 [green]Analysis Mode Activated[/green]")

        if self.orchestrator:
            try:
                plan = await self.orchestrator.create_detailed_plan(f"Analiz et: {user_input}")
                plan["analysis_mode"] = True
                plan = self._enrich_plan_with_classification(plan, classification)

                return await self.orchestrator.execute_task_plan(plan, user_input)
            except Exception as e:
                if self.debug:
                    console.print(f"⚠️ [dim yellow]Analysis orchestrator xətası: {str(e)}[/dim yellow]")

        return await self._process_conversation(f"Analiz et: {user_input}")

    async def _process_learning(self, user_input: str, classification: ClassificationResult, context: Dict) -> bool:
        """Process learning requests."""
        console.print("📚 [magenta]Learning Mode Activated[/magenta]")

        context_info = classification.context_hints
        tech_stack = context_info.get("tech_stack", "general")

        educational_prompt = f"Təhsil məqsədilə izah et: {user_input}"
        if tech_stack != "general":
            educational_prompt += f" ({tech_stack} kontekstində)"

        return await self._process_conversation(educational_prompt)

    async def _process_conversation(self, user_input: str) -> bool:
        """Process general AI conversation."""
        if hasattr(self.smart_cli, "_process_ai_request"):
            try:
                await asyncio.wait_for(
                    self.smart_cli._process_ai_request(user_input), timeout=30.0
                )
            except asyncio.TimeoutError:
                console.print("⏰ [yellow]AI sorğu vaxt aşımı[/yellow]")
            except Exception as e:
                console.print(f"❌ [red]AI işləmə xətası: {str(e)}[/red]")
        else:
            console.print("⚠️ [yellow]AI işləmə mövcud deyil[/yellow]")

        return True

    def _prioritize_handlers(self, handlers, context_hints):
        """Prioritize handlers based on context."""
        git_keywords = ["git", "commit", "push", "pull"]
        cost_keywords = ["cost", "budget", "xərc"]

        prioritized = []
        regular = []

        for handler in handlers:
            handler_name = handler.__class__.__name__.lower()

            if "git" in handler_name and any(kw in context_hints.get("original_text", "") for kw in git_keywords):
                prioritized.append(handler)
            elif "cost" in handler_name and any(kw in context_hints.get("original_text", "") for kw in cost_keywords):
                prioritized.append(handler)
            else:
                regular.append(handler)

        return prioritized + regular

# Compatibility alias
RequestRouter = EnhancedRequestRouter
