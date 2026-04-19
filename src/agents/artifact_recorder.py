"""Phase artifact and meta-learning manifest persistence helpers."""

import json
import time
from pathlib import Path
from typing import Any, Dict


def generate_phase_artifacts(
    agent_type: str,
    phase_name: str,
    result: Any,
    artifacts: Dict[str, list],
) -> None:
    """Write a truthful phase manifest and update the shared artifacts dict."""
    artifacts_dir = Path("artifacts") / phase_name
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    reported = []
    reported.extend(getattr(result, "created_files", []) or [])
    reported.extend(getattr(result, "modified_files", []) or [])

    manifest_path = artifacts_dir / "phase_manifest.json"
    manifest = {
        "agent": agent_type,
        "phase": phase_name,
        "timestamp": time.time(),
        "success": getattr(result, "success", True),
        "created_files": getattr(result, "created_files", []) or [],
        "modified_files": getattr(result, "modified_files", []) or [],
        "warnings": getattr(result, "warnings", []) or [],
        "errors": getattr(result, "errors", []) or [],
    }

    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    artifacts[phase_name] = reported + [str(manifest_path)]


def record_meta_learning_manifest(artifacts: Dict[str, list]) -> None:
    """Persist a truthful manifest for the post-run meta-learning step."""
    artifacts_dir = Path("artifacts") / "metalearning"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = artifacts_dir / "phase_manifest.json"
    manifest = {
        "agent": "metalearning",
        "phase": "metalearning",
        "timestamp": time.time(),
        "success": True,
        "created_files": [],
        "modified_files": [],
        "warnings": [],
        "errors": [],
        "notes": [
            "No standalone meta-learning output files are generated yet.",
            "This manifest records the post-run learning step only.",
        ],
    }

    with open(manifest_path, "w", encoding="utf-8") as fh:
        json.dump(manifest, fh, indent=2)

    artifacts["metalearning"] = [str(manifest_path)]
