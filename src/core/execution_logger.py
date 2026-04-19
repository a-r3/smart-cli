"""Structured execution logging for Smart CLI workflows."""

import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional


class ExecutionLogger:
    """Log workflow execution in structured JSON format."""

    def __init__(self, session_id: Optional[str] = None):
        """Initialize execution logger."""
        self.session_id = session_id or f"session_{int(time.time() * 1000)}"
        self.start_time = time.time()
        self.execution_log: Dict[str, Any] = {
            "session_id": self.session_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "workflow_type": None,
            "original_request": None,
            "classifier_result": None,
            "orchestrator_summary": None,
            "agent_results": [],
            "artifacts": {},
            "warnings": [],
            "errors": [],
            "completion_status": "pending",
            "execution_time": 0.0,
        }

    def record_classification(
        self,
        request_type: str,
        confidence: float,
        reasoning: List[str],
        original_request: str,
    ) -> None:
        """Record the classifier result."""
        self.execution_log["original_request"] = original_request
        self.execution_log["classifier_result"] = {
            "request_type": request_type,
            "confidence": confidence,
            "reasoning": reasoning,
            "timestamp": time.time() - self.start_time,
        }

    def record_workflow_type(self, workflow_type: str) -> None:
        """Record inferred workflow type."""
        self.execution_log["workflow_type"] = workflow_type

    def record_orchestrator_summary(self, summary: Dict[str, Any]) -> None:
        """Record orchestrator workflow summary."""
        self.execution_log["orchestrator_summary"] = {
            **summary,
            "timestamp": time.time() - self.start_time,
        }

    def record_agent_execution(
        self,
        agent_name: str,
        agent_type: str,
        success: bool,
        created_files: List[str],
        modified_files: List[str],
        errors: List[str],
        warnings: List[str],
        execution_time: float,
        output_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record one agent's execution result."""
        self.execution_log["agent_results"].append({
            "agent_name": agent_name,
            "agent_type": agent_type,
            "success": success,
            "created_files": created_files or [],
            "modified_files": modified_files or [],
            "errors": errors or [],
            "warnings": warnings or [],
            "output_data": output_data or {},
            "execution_time": execution_time,
            "timestamp": time.time() - self.start_time,
        })

    def record_artifacts(self, artifacts: Dict[str, List[str]]) -> None:
        """Record final artifacts by agent phase."""
        self.execution_log["artifacts"] = artifacts

    def record_warning(self, warning: str) -> None:
        """Add a warning to the execution log."""
        if warning not in self.execution_log["warnings"]:
            self.execution_log["warnings"].append(warning)

    def record_error(self, error: str) -> None:
        """Add an error to the execution log."""
        if error not in self.execution_log["errors"]:
            self.execution_log["errors"].append(error)

    def finalize(self, success: bool) -> None:
        """Finalize the execution log."""
        self.execution_log["completion_status"] = "success" if success else "failed"
        self.execution_log["execution_time"] = time.time() - self.start_time

    def save_to_disk(self, artifacts_dir: str = "artifacts") -> Path:
        """Save execution log to disk under artifacts/session/."""
        session_dir = Path(artifacts_dir) / "session"
        session_dir.mkdir(parents=True, exist_ok=True)

        log_path = (
            session_dir / f"execution_{self.session_id}.json"
        )

        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(self.execution_log, f, indent=2, ensure_ascii=False)

        return log_path

    def get_log_dict(self) -> Dict[str, Any]:
        """Return the complete execution log dictionary."""
        return self.execution_log

    @staticmethod
    def get_latest_log(artifacts_dir: str = "artifacts") -> Optional[Path]:
        """Get the most recent execution log file."""
        session_dir = Path(artifacts_dir) / "session"
        if not session_dir.exists():
            return None

        log_files = list(session_dir.glob("execution_*.json"))
        if not log_files:
            return None

        return max(log_files, key=lambda p: p.stat().st_mtime)

    @staticmethod
    def load_log(log_path: Path) -> Dict[str, Any]:
        """Load and parse an execution log file."""
        with open(log_path, "r", encoding="utf-8") as f:
            return json.load(f)
