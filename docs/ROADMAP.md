# Smart CLI Roadmap

## Purpose

This roadmap turns the current audit into an execution plan that can be tracked inside the repository.

It is intentionally pragmatic:
- fix product truth before adding more surface area
- make CI trustworthy before claiming maturity
- strengthen the core interactive CLI before expanding advanced modes and agents

Actionable task breakdown:
- See [docs/BACKLOG.md](BACKLOG.md) for prioritized implementation items.

## Current Reality (as of 2026-04-20, post-PQ window)

Window PQ is complete. Infrastructure is now healthy:
- CI runs all 457 tests across Python 3.9–3.12 ✅
- Base dependencies trimmed from 23 to 7 ✅
- Automated PyPI + Docker release pipeline in place ✅
- `orchestrator.py` decomposed: 836 → 592 lines + 4 extracted modules ✅
- `intelligent_execution_planner.py` decomposed: 797 → 173 lines + 2 extracted modules ✅

A full codebase audit (2026-04-20) uncovered new blockers:

**Security (PS — must fix before next release):**
- `src/utils/config.py:92` — hardcoded fallback encryption key `"default-key-change-me"`
- `src/utils/cache.py` — `pickle.loads` at 4 call sites (deserialization attack vector)

**Correctness (PC — must fix before feature work):**
- 10 bare `except:` clauses across 6 files — silently swallow all exceptions
- `AgentReport` defined twice with different content (`base_agent.py` vs `core/agent_task.py`)
- `_is_agent_completed` always returns `False` — dependency checking is non-functional
- `generate` and `review code` CLI commands are empty stubs visible in `--help`
- README advertises SSO, RBAC, FastAPI, Prometheus, Grafana — none implemented in `src/`

**Deferred (Window F+):**
- 21 of 64 source modules still have no dedicated test file

## Product Goal

Smart CLI should become a reliable developer assistant with a narrow but strong core:
- interactive AI CLI that works predictably
- clear command contract
- stable provider integrations
- trusted tests and CI
- focused automation for developer workflows

## Guiding Principles

- Prefer a smaller, honest product over a broader but unreliable one.
- Every user-facing claim should map to a tested behavior.
- New features should only ship after the command surface and CI are stable.
- Modes and agents should be treated as multipliers, not as the foundation.

## Phase 1: Product Truth Alignment

Objective:
- Make documentation, tests, and implementation describe the same product.

Deliverables:
- Define the supported command surface for `smart`.
- Remove duplicate or conflicting CLI startup paths.
- Decide which commands are real now: `config`, `version`, `health`, `init`, `generate`, `review`, or a reduced subset.
- Update tests to match the actual contract, or implement the missing commands if they are considered core.
- Replace misleading roadmap language in public docs with the real plan.

Exit criteria:
- README, CLI help output, and tests all describe the same command surface.
- `tests/test_cli.py` verifies the real behavior instead of an older planned interface.

Priority:
- Highest

## Phase 2: Reliable Core

Objective:
- Make the interactive CLI consistently usable for first-run users.

Deliverables:
- Stabilize `src/cli.py` and `src/smart_cli.py` startup flow.
- Ensure the primary interactive path has one entrypoint and one lifecycle.
- Harden config loading and missing-key behavior.
- Define a first-run flow:
  - install
  - configure API key
  - launch interactive session
  - receive one successful response

Exit criteria:
- A new user can complete the first-run flow without reading source code.
- Core startup tests pass consistently in CI.

Priority:
- Highest

## Phase 3: Test and CI Credibility

Objective:
- Turn CI into a quality gate instead of a presentation layer.

Deliverables:
- Remove synthetic coverage generation from `.github/workflows/ci.yml`.
- Run real tests only.
- Ensure async tests have the required pytest support and markers configured correctly.
- Split tests into realistic layers:
  - unit
  - integration
  - e2e
- Convert skip-heavy tests into either real tests or delete them.

Exit criteria:
- CI status reflects the actual health of the repository.
- Coverage is based on code exercised by real tests.
- A failing core feature causes CI to fail.

Priority:
- Highest

## Phase 4: Provider Architecture

Objective:
- Make model/provider support real, explicit, and testable.

Deliverables:
- Separate provider adapters for OpenRouter, Anthropic, and OpenAI if all three are meant to be supported.
- Normalize request and response handling behind one interface.
- Move retry, timeout, caching, and rate limiting behind shared abstractions.
- Add provider-specific tests for payload shape and error handling.

Exit criteria:
- Each advertised provider has a valid request path.
- Provider switching does not rely on incompatible API shapes.

Priority:
- High

## Phase 5: Mode System Simplification

Objective:
- Reduce complexity until the mode system matches the maturity of the product.

Deliverables:
- Keep only the modes that have distinct behavior and tests.
- Suggested initial kept modes:
  - `smart`
  - `code`
  - `analysis`
- Move other modes behind feature flags or mark them experimental.
- Define what a mode changes:
  - prompt strategy
  - tool permissions
  - routing logic
  - output style

Exit criteria:
- Every public mode has a clear contract and at least one integration test.
- Mode names, classes, and docs use the same terminology.

Priority:
- High

## Phase 6: Workflow Differentiation

Objective:
- Build one or two developer workflows that are meaningfully better than generic AI chat.

Candidate workflow tracks:
- Repo understanding and guided code changes
- Git and GitHub review assistance
- Safe implementation planning before edits

Deliverables:
- Choose one primary workflow and optimize for it end-to-end.
- Add task-focused prompts, routing, and summaries around that workflow.
- Measure output quality using repeatable fixture repositories or test scenarios.

Exit criteria:
- Smart CLI has one clearly demonstrable developer use case that works reliably.

Priority:
- Medium

## Phase 7: Agents and Orchestration

Objective:
- Reintroduce advanced orchestration only after the single-agent core is dependable.

Deliverables:
- Define when orchestration is invoked.
- Make agent responsibilities explicit and observable.
- Add execution-plan validation and outcome tracing.
- Add tests for planner output and orchestration handoff.

Exit criteria:
- Multi-agent behavior is testable, debuggable, and not required for normal usage.

Priority:
- Medium

## Phase 8: Observability and Release Discipline

Objective:
- Make the project operable and releasable with confidence.

Deliverables:
- Structured logs for startup, routing, provider calls, and failures.
- Basic telemetry for success rate, latency, and token usage.
- Release checklist and semver discipline.
- Changelog and migration notes tied to actual shipped changes.

Exit criteria:
- Releases can be evaluated against measurable quality signals.

Priority:
- Medium

## Recommended Sequence (post-PQ)

1. **PS: Security fixes** — master key, pickle → must ship before next release tag
2. **PC: Correctness cleanup** — bare excepts, AgentReport, stub commands, README
3. **P9: Agent Capability Expansion** — parallel execution, cost tracking
4. **PQ-8: Test coverage** — 21 untested modules
5. **P10/P11: Advanced features**

## Suggested Execution Plan

### Window PS (immediate — days)
- PS-1: Remove hardcoded master key
- PS-2: Replace pickle with JSON in cache

### Window PC (days — 1 week)
- PC-1: 10 bare `except:` → specific exceptions
- PC-2: AgentReport name collision fix
- PC-3: `_is_agent_completed` implementation
- PC-4: Remove/implement stub CLI commands
- PC-5: README reality alignment

### Window E (1–3 weeks)
- P9-2: Parallel agent execution
- P9-3: Cost tracking integration

### Window F (3–6 weeks)
- PQ-8: Test coverage for 21 untested modules
- P10-1: Batch workflow execution

### Window G+
- P11-x: Workflow templates, interactive builder, webhook integration

## Backlog Candidates

These are intentionally deferred until the core is stable:
- richer team collaboration claims
- advanced enterprise auth and SSO claims
- full production deployment claims
- broad multi-agent marketing surface
- large monitoring stack expansion

## Definition of Done for the Next Milestone

The next milestone is complete when all of the following are true:
- `smart` has one clear startup contract
- README reflects real functionality
- core CLI tests pass
- CI runs real tests only
- provider behavior is not misleading
- at least one end-to-end developer workflow works reliably

## Owner Notes

When new ideas come up, add them under the relevant phase instead of expanding the public feature list immediately.

If a feature is not yet tested and user-visible, label it as experimental instead of complete.
