# Smart CLI Release Checklist

**Version:** 1.0.0  
**Date:** 2026-04-19  
**Focus:** Narrowed product surface with explicit workflow contract and comprehensive testing

## Pre-Release Validation

### 1. Explicit Workflow Contract

- [ ] **Workflow Command Available**: `smart workflow` command is defined and discoverable
  - Test: `smart workflow --help` shows available workflows
  - File: `src/cli.py` contains `workflow_command` function
  
- [ ] **Repository Workflows Work**: Both primary workflows are functional
  - [ ] `smart workflow repo-plan <target>` - analyze + planning
  - [ ] `smart workflow repo-analyze <target>` - analysis only
  - Test: Manual invocation on fixture repository

- [ ] **CLI Accepts Target Parameter**: Workflows can operate on arbitrary repository paths
  - Test: `smart workflow repo-plan /path/to/repo` executes successfully
  - File: `tests/test_workflow_command.py` covers target handling

### 2. Test Suite Coverage

**Run Full Test Suite:**
```bash
pytest tests/test_cli.py \
        tests/test_workflow_command.py \
        tests/test_repo_workflow_e2e.py \
        tests/test_reviewer_contract.py \
        tests/test_basic_fallback_contracts.py \
        tests/test_execution_logs.py \
        --tb=short -q
```

**Actual Results:** 54 tests pass

### Test Suite Breakdown

- [ ] **CLI Tests** (`tests/test_cli.py`): 11 tests
  - Command registration
  - Help text display
  - Version command
  
- [ ] **Workflow Command Tests** (`tests/test_workflow_command.py`): 8 tests
  - Command availability
  - Subcommand routing
  - Error handling
  - Help documentation
  
- [ ] **End-to-End Workflow Tests** (`tests/test_repo_workflow_e2e.py`): 11 tests
  - Classifier recognizes repository analysis requests
  - Orchestrator builds workflow summaries
  - Agent fallback paths operate correctly
  - Artifact manifests maintain structure
  
- [ ] **ReviewerAgent Contract Tests** (`tests/test_reviewer_contract.py`): 2 tests
  - Success path doesn't claim file changes
  - Failure path provides correct error messages
  
- [ ] **Fallback Contract Tests** (`tests/test_basic_fallback_contracts.py`): 6 tests
  - AnalyzerAgent fallback stability
  - ArchitectAgent fallback stability
  - TesterAgent fallback stability
  - File change truthfulness
  
- [ ] **Execution Logging Tests** (`tests/test_execution_logs.py`): 18 tests
  - Log initialization
  - JSON schema stability
  - Persistence to disk
  - Complete workflow scenarios

### 3. End-to-End Workflow Verification

- [ ] **Fixture Repository Works**: Sample calculator repository under `tests/fixtures/sample_repo/` is valid
  - Contains: `src/calculator.py`, `tests/test_calculator.py`, `README.md`
  - Can be analyzed without errors

- [ ] **Golden-Path Request**: "analyze this repository and give me an implementation plan"
  - [ ] Classification succeeds
  - [ ] Orchestrator summary generates
  - [ ] All agents execute without errors
  - [ ] Output matches artifact manifests

- [ ] **File Change Contracts**: All agents report truthfully about modifications
  - [ ] ReviewerAgent claims no file changes
  - [ ] AnalyzerAgent claims no file changes
  - [ ] ArchitectAgent claims no file changes (fallback)
  - [ ] TesterAgent claims no file changes (fallback)

### 4. Execution Logging Verification

- [ ] **Log Files Generated**: Workflows produce execution logs
  - Location: `artifacts/session/execution_*.json`
  - Format: Valid JSON matching schema
  
- [ ] **Log Contains Required Fields**:
  - [ ] session_id
  - [ ] timestamp
  - [ ] workflow_type
  - [ ] original_request
  - [ ] classifier_result
  - [ ] orchestrator_summary
  - [ ] agent_results (array)
  - [ ] artifacts (dict)
  - [ ] warnings (array)
  - [ ] errors (array)
  - [ ] completion_status ("success" or "failed")
  - [ ] execution_time (seconds)

- [ ] **Log Matches Execution**: Log reflects actual workflow execution
  - Agent names match active agents
  - File counts match actual files analyzed
  - Error messages match actual errors
  - Warnings correspond to actual issues

### 5. Documentation Accuracy

- [ ] **README.md**
  - [ ] Explicit workflow commands are documented
  - [ ] Example invocations are shown
  - [ ] Command syntax is accurate
  
- [ ] **Code Comments**
  - [ ] No misleading or outdated comments
  - [ ] Comments explain "why" not just "what"
  
- [ ] **Backlog Consistency**
  - [ ] All completed items marked as "done"
  - [ ] Started dates recorded
  - [ ] Implementation files listed

### 6. Code Quality

- [ ] **No Deprecated Warnings**
  - Run full test suite and verify no deprecation warnings
  - Example: Python 3.12+ datetime warnings
  
- [ ] **No Broken Imports**
  - [ ] All imports resolve correctly
  - [ ] Try/except import patterns work
  
- [ ] **Consistent Style**
  - Module docstrings present and accurate
  - Function signatures are consistent
  - Type hints used where present

### 7. Release Artifacts

- [ ] **Changelog Entry**: Note new features
  - Explicit workflow command
  - End-to-end testing
  - Execution logging
  
- [ ] **Version Number**: Updated if applicable
  - Check: `src/cli.py` and `pyproject.toml`
  - Version: 1.0.0 (first release of narrowed surface)

## Release Decision Tree

```
Start Release Process
│
├─ All tests pass? ──NO──> Stop. Fix failing tests.
│                 │ YES
│                  ▼
├─ Workflows execute without error? ──NO──> Stop. Debug workflows.
│                                  │ YES
│                                   ▼
├─ Execution logs valid? ──NO──> Stop. Fix logging.
│                      │ YES
│                       ▼
├─ Documentation matches code? ──NO──> Stop. Update docs.
│                            │ YES
│                             ▼
├─ No critical warnings? ──NO──> Stop. Fix warnings.
│                      │ YES
│                       ▼
└─ READY FOR RELEASE ✓
```

## Post-Release Verification

- [ ] **Tag Release**: Create git tag (e.g. `v1.1.0`)
- [ ] **Changelog Updated**: CHANGELOG.md reflects release
- [ ] **CI Passes**: GitHub Actions `ci.yml` shows green across all matrix versions
- [ ] **Automated publish triggered**: `release.yml` workflow ran on the new tag

## Automated Release Pipeline

Pushing a version tag triggers `.github/workflows/release.yml`:

1. **Build** — `python -m build` produces wheel + sdist
2. **PyPI publish** — via `pypa/gh-action-pypi-publish` (uses OIDC, no token needed if environment `pypi` is configured in repo settings)
3. **Docker push** — image pushed to `ghcr.io/<owner>/smart-cli:<version>` and `:latest`

### Required setup (one-time, per repo)

| What | Where |
|------|-------|
| PyPI Trusted Publisher | PyPI → Your projects → smart-cli → Publishing → Add publisher → GitHub Actions |
| GHCR | Automatic — uses `GITHUB_TOKEN` (no secret needed) |
| GitHub environment | Repo Settings → Environments → create `pypi` |

## Sign-Off

- [ ] **Owner Review**: Code owner confirms quality
- [ ] **Test Review**: All test results reviewed
- [ ] **Documentation Review**: Docs match product
- [ ] **Release Manager**: Approves release

---

**Release Notes Format:**

```markdown
## Smart CLI v1.0.0

### Features
- Explicit repository workflow command: `smart workflow repo-plan` and `smart workflow repo-analyze`
- End-to-end workflow testing with fixture repository
- Structured execution logging for debugging and verification

### Tests
- 57+ tests covering CLI, workflows, agents, and logging
- 11 end-to-end workflow tests with fixture repository
- Comprehensive contract validation for ReviewerAgent and fallback paths

### Documentation
- Explicit workflow command documented
- Execution logging schema defined
- Test suite structure described

### Quality
- All file change claims validated
- No silent failures in agent paths
- Machine-readable execution logs for every run
```

## Maintenance Post-Release

- Monitor execution logs for unexpected errors
- Track user feedback on workflow commands
- Update test suite as new agents are added
- Maintain execution log schema backwards compatibility
