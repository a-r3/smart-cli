# Smart CLI Backlog

## How to Use This Backlog

This file turns the roadmap into concrete work items.

Rules for using it:
- finish P0 items before expanding the product surface
- do not mark an item complete unless behavior is validated
- update acceptance criteria when scope changes

## Current Focus

Current milestone:
- Phase 1: Product Truth Alignment

Current next milestone after that:
- Phase 2: Reliable Core

## P0: Product Truth Alignment

### P0-1: Unify CLI entrypoint

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: first P0 milestone
- State: done

### Notes
- `src/cli.py` was reduced to one callback-based startup path.
- Interactive startup now calls `SmartCLI.start()` instead of a mismatched `run()` path.
- Added an explicit `version` command alongside the global `--version` flag.

### Validation
- `pytest tests/test_cli.py -q`

Problem:
- `src/cli.py` contains overlapping callback flows and inconsistent startup behavior.

Tasks:
- keep one startup callback
- remove duplicate interactive entry logic
- ensure startup calls the real public `SmartCLI` lifecycle method
- make `--help` and `--version` behavior deterministic

Acceptance criteria:
- CLI has one clear startup path
- help output is stable
- version output is callable through the supported interface
- no dead startup code remains in `src/cli.py`

Suggested files:
- `src/cli.py`
- `src/smart_cli.py`

### P0-2: Define the real command contract

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: first P0 milestone
- State: done

### Notes
- The current supported contract is now documented as:
- `smart`
- `smart --version`
- `smart version`
- `smart config show`
- `smart config api-key ...`
- `smart config github-token ...`
- README examples were reduced to this real surface.

### Validation
- `pytest tests/test_cli.py -q`

Problem:
- tests, README, and code disagree on which commands exist.

Tasks:
- decide which commands are supported now
- remove undocumented ghost commands from tests
- either implement or explicitly defer `health`, `init`, `generate`, `review`
- align help text, README examples, and tests

Acceptance criteria:
- one source of truth exists for supported commands
- examples in README do not reference unsupported commands
- CLI tests validate the current contract only

Suggested files:
- `README.md`
- `src/cli.py`
- `tests/test_cli.py`

### P0-3: Make tests match implementation

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: first P0 milestone
- State: done

### Notes
- `tests/test_cli.py` was rewritten around the actual Typer app contract.
- Removed assertions for nonexistent commands such as `health`, `init`, `generate`, and `review`.
- Tests now patch `src.cli.ConfigManager` directly and validate the interactive startup path safely.

### Validation
- `pytest tests/test_cli.py -q`

Problem:
- CLI tests are currently written against a different interface and use brittle patch targets.

Tasks:
- rewrite tests around the real Typer surface
- patch import locations correctly
- remove tests that assert nonexistent commands
- convert misleading integration tests into either real integration tests or unit tests

Acceptance criteria:
- `tests/test_cli.py` passes against the actual CLI
- tests fail only on real regressions
- test names describe real user behavior

Suggested files:
- `tests/test_cli.py`
- `tests/conftest.py`

### P0-4: Replace misleading public roadmap language

Problem:
- old roadmap messaging implied broad completion that is not yet validated.

Tasks:
- keep `docs/ROADMAP.md` as the execution source of truth
- ensure README points to roadmap instead of claiming full maturity
- check adjacent docs for similar overstatements

Acceptance criteria:
- public docs do not overclaim shipped functionality

Suggested files:
- `README.md`
- `docs/ROADMAP.md`
- `docs/ARCHITECTURE.md`
- `docs/TESTING.md`

## P1: Reliable Core

### P1-1: First-run setup flow

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after first P0 milestone
- State: done

### Notes
- Interactive startup now stops early with actionable guidance when no AI provider is configured.
- Startup guidance now includes both CLI config commands and environment-variable setup paths.
- README examples were already reduced to the real supported setup flow.

### Validation
- `pytest tests/test_cli.py -q`

Problem:
- a new user does not yet have one proven, friction-free setup path.

Tasks:
- define setup prerequisites clearly
- verify config behavior when keys are missing
- improve first-run messaging
- make interactive startup fail clearly and safely without required config

Acceptance criteria:
- a new user can understand how to configure and launch the tool
- missing API keys produce actionable output
- no stack trace leaks into normal first-run UX

Suggested files:
- `src/cli.py`
- `src/smart_cli.py`
- `src/utils/config.py`
- `README.md`

### P1-2: Stabilize SmartCLI lifecycle

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after first P0 milestone
- State: done

### Notes
- CLI startup now routes to `SmartCLI.start()` through one public path.
- `SmartCLI` now exposes an explicit `shutdown()` path for resource cleanup.
- Startup failure, successful startup, and shutdown behavior are covered by focused CLI tests.

### Validation
- `pytest tests/test_cli.py -q`

Problem:
- `SmartCLI` startup behavior and CLI startup behavior are not fully aligned.

Tasks:
- define one public lifecycle for initialization and run loop
- ensure cleanup paths are explicit
- handle keyboard interrupt and startup exceptions consistently

Acceptance criteria:
- startup and shutdown logic are easy to trace
- lifecycle methods are testable
- normal interruption exits cleanly

Suggested files:
- `src/smart_cli.py`
- `src/cli.py`

### P1-3: Honest CI

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after first P0 milestone
- State: done

### Notes
- `.github/workflows/ci.yml` no longer generates synthetic coverage tests.
- CI now installs the package and runs a trusted real test suite:
- `tests/test_cli.py`
- `tests/test_config.py`
- `tests/test_basic.py`
- `pytest.ini` now declares `asyncio_mode = auto` for environments where `pytest-asyncio` is installed.

### Validation
- `pytest tests/test_cli.py tests/test_config.py tests/test_basic.py --tb=short -q`

Problem:
- CI currently generates synthetic coverage and tolerates weak signals.

Tasks:
- remove generated coverage test creation from workflow
- run real tests only
- ensure async test support is installed and configured
- fail on real breakage

Acceptance criteria:
- CI reflects actual repository health
- coverage comes from real exercised code
- async markers are recognized

Suggested files:
- `.github/workflows/ci.yml`
- `pyproject.toml`
- `pytest.ini`

## P2: Provider Architecture

### P2-1: Split provider implementations

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after stable core milestone
- State: done

### Notes
- `src/utils/simple_ai_client.py` now separates provider-specific concerns:
- endpoint path
- auth headers
- request payload shape
- response parsing
- OpenRouter remains the default when both keys exist.
- Direct Anthropic mode now uses `/messages` with Anthropic-specific headers and payload layout.
- Added focused provider tests in `tests/test_simple_ai_client.py`.

### Validation
- `pytest tests/test_simple_ai_client.py --tb=short -q`
- `pytest tests/test_cli.py tests/test_config.py tests/test_basic.py tests/test_simple_ai_client.py --tb=short -q`

Problem:
- the current AI client mixes provider selection with a request format that appears OpenAI-style by default.

Tasks:
- define a provider interface
- separate OpenRouter and Anthropic request builders
- add provider-specific error handling
- test request payload generation

Acceptance criteria:
- advertised providers have valid request paths
- provider switching does not silently use incompatible payloads

Suggested files:
- `src/utils/simple_ai_client.py`
- `tests/test_ai_client.py`

## P3: Mode System Simplification

### P3-1: Reduce public modes to tested modes

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after stable core milestone
- State: done

### Notes
- Stable public mode surface is now explicitly limited to:
- `smart`
- `code`
- `analysis`
- `architect`, `learning`, `fast`, and `orchestrator` are now treated as experimental in code and docs.
- `ModeManager` alias was added to align terminology with the public/test surface.
- Added focused mode-surface tests in `tests/test_mode_surface.py`.

### Validation
- `pytest tests/test_mode_surface.py --tb=short -q`
- `pytest tests/test_cli.py tests/test_config.py tests/test_basic.py tests/test_simple_ai_client.py tests/test_mode_surface.py --tb=short -q`

Problem:
- mode system breadth is ahead of product maturity.

Tasks:
- identify which modes truly differ in behavior today
- keep `smart`, `code`, and `analysis` public first
- mark other modes as experimental or internal
- align docs, tests, and class naming

Acceptance criteria:
- every public mode has a clear contract
- mode terminology is consistent across code and docs

Suggested files:
- `src/core/mode_manager.py`
- `docs/MODE_SYSTEM.md`
- `tests/test_mode_system.py`

## P4: Primary Workflow

### P4-1: Make the repository workflow explicit

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after stable core and mode-surface cleanup
- State: done

### Notes
- The primary product workflow is now documented in `docs/WORKFLOWS.md`.
- The classifier now exposes workflow intent for repository-oriented prompts:
- repo understand
- repo understand -> plan
- repo understand -> implement
- Added focused tests in `tests/test_workflow_classifier.py`.
- Fixed a classifier bug where `hi` inside words like `this` was incorrectly treated as greeting-only conversation.

### Validation
- `pytest tests/test_workflow_classifier.py --tb=short -q`
- `pytest tests/test_cli.py tests/test_config.py tests/test_basic.py tests/test_simple_ai_client.py tests/test_mode_surface.py tests/test_workflow_classifier.py --tb=short -q`

Problem:
- Smart CLI needed one concrete workflow that was stronger than generic AI chat.

Tasks:
- make the primary workflow explicit in docs
- expose workflow hints in request classification
- add tests for repository workflow prompts

Acceptance criteria:
- repository workflow prompts produce stable workflow metadata
- docs describe the workflow as a first-class product path

### P4-2: Standardize workflow summaries

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after workflow classification becomes stable
- State: done

### Notes
- `src/agents/orchestrator.py` now adds `workflow_type` and `workflow_summary` to plans.
- Workflow summary format is standardized for downstream UI/reporting use.
- Added focused tests in `tests/test_workflow_summary.py`.

### Validation
- `pytest tests/test_workflow_summary.py --tb=short -q`
- `pytest tests/test_cli.py tests/test_config.py tests/test_basic.py tests/test_simple_ai_client.py tests/test_mode_surface.py tests/test_workflow_classifier.py tests/test_workflow_summary.py --tb=short -q`

Problem:
- The repository workflow needed a stable summary shape, not just classifier hints.

Tasks:
- infer workflow type at plan creation time
- attach workflow metadata to orchestrator plans
- standardize summary lines for downstream rendering

Acceptance criteria:
- orchestrator plans include `workflow_type`
- orchestrator plans include `workflow_summary`
- summary shape is covered by tests

### P4-3: Add workflow acceptance coverage

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after workflow summary metadata is stable
- State: done

### Notes
- Added acceptance-style coverage in `tests/test_workflow_acceptance.py`.
- The router now enriches orchestrator plans with stable classification metadata:
- `suggested_action`
- `workflow_target`
- `workflow_stage`
- `confidence`
- `reasoning`
- This makes the repository workflow contract visible at the handoff between classification and plan execution.

### Validation
- `pytest tests/test_workflow_acceptance.py --tb=short -q`
- `pytest tests/test_cli.py tests/test_config.py tests/test_basic.py tests/test_simple_ai_client.py tests/test_mode_surface.py tests/test_workflow_classifier.py tests/test_workflow_summary.py tests/test_workflow_acceptance.py --tb=short -q`

Problem:
- The primary workflow needed an acceptance-style contract test, not just unit tests for classifier and summary helpers.

Tasks:
- verify workflow hints survive router-to-orchestrator handoff
- verify enriched plan metadata reaches execution

Acceptance criteria:
- repository workflow metadata is present on the orchestrator plan at execution time

### P4-4: Show workflow summary in terminal output

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after workflow summary metadata is stable
- State: done

### Notes
- Added `_display_workflow_summary()` to `src/agents/orchestrator.py`.
- The orchestrator now prints the standardized workflow summary during plan creation and again before execution begins.
- This makes the active repository workflow visible in terminal output instead of keeping it as metadata only.

### Validation
- `pytest tests/test_workflow_summary.py --tb=short -q`

Problem:
- Workflow summary existed as plan metadata but was not consistently surfaced to the user during execution.

Tasks:
- add one shared workflow summary renderer
- display summary lines at plan time
- display summary lines at execution start
- cover terminal rendering with a focused test

Acceptance criteria:
- workflow summary is visible in terminal output
- rendering uses the standardized summary lines
- display behavior is covered by tests

## P5: Artifact Truthfulness

### P5-1: Remove synthetic artifact generation

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after workflow visibility work
- State: done

### Notes
- `src/agents/orchestrator.py` no longer invents phase-specific output files such as fake reports and diffs.
- The orchestrator now writes a truthful `phase_manifest.json` for each phase and preserves any real files reported by agents.
- Added focused coverage in `tests/test_artifact_manifest.py`.

### Validation
- `pytest tests/test_artifact_manifest.py --tb=short -q`

Problem:
- The orchestrator was generating synthetic artifact files that implied work had happened even when those files were not produced by agents.

Tasks:
- stop creating fake artifact reports
- persist one truthful manifest per phase
- keep real agent-reported files in the artifact list
- align final terminal messaging with actual saved outputs

Acceptance criteria:
- orchestrator no longer creates synthetic analysis, implementation, testing, or review files
- each phase writes a truthful manifest
- terminal output does not overclaim saved artifacts

### P5-2: Remove simulated orchestrator progress

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after synthetic artifact cleanup
- State: done

### Notes
- `src/agents/orchestrator.py` no longer prints fabricated per-agent progress steps before real delegation.
- The post-run meta-learning step now writes a truthful manifest instead of claiming updates to nonexistent global files.
- Added focused coverage in `tests/test_orchestrator_truthfulness.py`.

### Validation
- `pytest tests/test_orchestrator_truthfulness.py --tb=short -q`

Problem:
- The orchestrator was still simulating detailed work states and fake meta-learning outputs, which weakened trust in terminal output.

Tasks:
- replace simulated progress bars with factual delegation status
- remove artificial sleeps from sequential orchestration
- replace fake meta-learning file claims with a truthful manifest
- cover output behavior with focused tests

Acceptance criteria:
- orchestrator output does not simulate internal progress states it cannot verify
- meta-learning output no longer references nonexistent files
- new behavior is covered by tests

### P5-3: Align intelligent pipeline output with real execution

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after orchestrator truthfulness cleanup
- State: done

### Notes
- `src/agents/orchestrator.py` now records real per-agent artifacts during intelligent pipeline execution instead of printing generic artifact directories.
- Final intelligent-pipeline completion output no longer overclaims universal success.
- `src/agents/orchestrator_extension.py` no longer simulates 25/50/75 progress updates before agent execution.
- Added focused coverage in `tests/test_intelligent_pipeline_truthfulness.py`.

### Validation
- `pytest tests/test_intelligent_pipeline_truthfulness.py --tb=short -q`

Problem:
- The intelligent pipeline and extension path still contained simulated progress and generic artifact output that did not reflect actual results.

Tasks:
- use real phase keys for artifact recording
- persist manifests from actual intelligent-pipeline agent results
- remove simulated extension progress updates
- make completion messaging neutral and factual

Acceptance criteria:
- intelligent pipeline artifact output comes from real agent results
- extension path no longer simulates progress percentages
- completion messaging does not overclaim success

### P5-4: Standardize agent result summaries

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after intelligent pipeline truthfulness cleanup
- State: done

### Notes
- `src/agents/orchestrator.py` now uses one shared summary builder for agent results.
- Sequential and intelligent pipeline flows now render the same result-summary block.
- Summary output now handles missing results explicitly and uses a stable “completed with no file changes” fallback.
- Added focused coverage in `tests/test_workflow_summary.py`.

### Validation
- `pytest tests/test_workflow_summary.py --tb=short -q`

Problem:
- Agent result summaries were assembled inline and inconsistently across execution paths.

Tasks:
- add one result-summary helper
- reuse it across sequential and intelligent pipeline outputs
- define explicit fallback text for empty or missing results
- cover summary formatting with focused tests

Acceptance criteria:
- agent result summary format is stable
- sequential and intelligent paths use the same summary logic
- missing results are shown explicitly instead of failing silently

### P5-5: Enforce file-change reporting in ModifierAgent

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after result-summary standardization
- State: done

### Notes
- `src/agents/modifier_agent.py` now keeps `created_files` and `modified_files` separate across fix and generation helpers.
- Fix flows now report the generated `_fixed.py` artifact as created and the original patched file as modified.
- Added focused coverage in `tests/test_modifier_contract.py`.

### Validation
- `pytest tests/test_modifier_contract.py --tb=short -q`

Problem:
- ModifierAgent was mixing modified files into `created_files`, which made orchestrator summaries and manifests less trustworthy.

Tasks:
- separate helper return values for created vs modified files
- preserve that separation in top-level execute
- add regression coverage for fix-task behavior

Acceptance criteria:
- ModifierAgent reports created files distinctly from modified files
- fix-task summaries and manifests reflect real file changes
- behavior is covered by focused tests

### P5-6: Lock report helper contracts for analyzer-style agents

### Status
- Owner: Codex
- Started: 2026-04-19
- Target: after ModifierAgent reporting cleanup
- State: done

### Notes
- Added focused coverage for `AnalyzerAgent`, `ArchitectAgent`, and `TesterAgent` report/document helpers.
- Tests now verify that helper methods return file paths that actually exist on disk after execution.
- This protects orchestrator manifests and summaries from drifting away from real report outputs.

### Validation
- `pytest tests/test_agent_report_contracts.py --tb=short -q`

Problem:
- Analyzer-style agents appeared to report created report/document files correctly, but the contract was not locked by tests.

Tasks:
- verify analyzer report helper writes a real file
- verify architect documentation helper returns real files
- verify tester report helper writes a real file
- cover these contracts with focused tests

Acceptance criteria:
- report/document helpers return paths for files that exist
- analyzer, architect, and tester helper contracts are covered by tests

## Suggested Execution Order

1. P0-1: Unify CLI entrypoint
2. P0-2: Define the real command contract
3. P0-3: Make tests match implementation
4. P1-1: First-run setup flow
5. P1-2: Stabilize SmartCLI lifecycle
6. P1-3: Honest CI
7. P2-1: Split provider implementations
8. P3-1: Reduce public modes to tested modes

## Good First Milestone

The first milestone should include:
- P0-1
- P0-2
- P0-3

Milestone result:
- Smart CLI has a truthful CLI contract and passing core CLI tests.

## Tracking Template

Use this format when starting an item:

```md
### Status
- Owner:
- Started:
- Target:
- State: not started | in progress | blocked | done

### Notes
- 

### Validation
- 
```
