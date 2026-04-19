# Smart CLI Workflows

## v1.0.0: Explicit Repository Analysis Workflows

Smart CLI v1.0.0 features explicit, first-class CLI commands for repository analysis workflows.

## Available Commands

### 1. Repository Plan

```bash
smart workflow repo-plan <target>
```

Analyze a repository and provide an implementation plan.

**Pipeline:**
- Analyzer → Architect → Tester → Reviewer

**Output:**
- Terminal summary
- Execution log: `artifacts/session/execution_<session_id>.json`
- Phase artifacts: `artifacts/<phase>/`

---

### 2. Repository Analysis  

```bash
smart workflow repo-analyze <target>
```

Quick repository analysis without planning.

**Pipeline:**
- Analyzer → Tester

**Output:**
- Terminal summary
- Execution log
- Phase artifacts

---

## Execution Logs

Every workflow generates structured JSON logs with:
- Session metadata
- Classification results
- Orchestrator summary
- Agent execution records
- Artifacts manifest
- Completion status

Location: `artifacts/session/execution_<session_id>.json`

---

## Primary Product Workflow

The current product wedge for Smart CLI is:

`repo understand -> plan -> implement summary`

This is the workflow that should be strongest, most testable, and easiest to demonstrate.

### Why This Workflow

This workflow fits the current codebase better than broad feature claims because Smart CLI already has:
- repository-aware request classification
- analysis and development routing
- orchestration and planning primitives
- file and project handlers

It is a better product story than generic "AI chat for everything".

## Workflow Stages

### 1. Understand

Goal:
- identify what the repository is
- identify the likely stack
- identify the most relevant files
- identify obvious risks or gaps

Expected outcome:
- short repository understanding summary
- key files or modules to inspect next

Example prompts:
- `analyze this repository`
- `understand this codebase`
- `review this project structure`

### 2. Plan

Goal:
- turn repository understanding into a concrete implementation plan
- define the least risky next changes
- explain what should be done first

Expected outcome:
- scoped plan
- acceptance criteria
- likely files to change

Example prompts:
- `analyze this repository and give me an implementation plan`
- `review this codebase and tell me the next steps`

Standard metadata:
- `workflow_type: repo_understand_plan`
- orchestrator plan includes `workflow_summary`

### 3. Implement Summary

Goal:
- after changes, summarize what was implemented and what remains

Expected outcome:
- change summary
- validation summary
- remaining risks

Example prompts:
- `implement the plan and summarize the result`
- `fix this repository and tell me what changed`

Standard metadata:
- `workflow_type: repo_understand_implement`
- plan/result summaries should stay short and action-oriented

## Stable Expectation

The workflow does not require every advanced mode or every agent feature to be perfect.

It does require:
- stable request classification
- truthful command surface
- stable startup
- trusted tests

## Relationship to Modes

Recommended mode mapping:
- `smart`: default entrypoint for the workflow
- `analysis`: best for repository understanding
- `code`: best for implementation

Experimental modes should not be required for the primary workflow.
