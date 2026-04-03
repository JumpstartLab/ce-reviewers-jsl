---
name: lfg
type: orchestrator
description: |
  Full autonomous engineering workflow. Plans first, builds second,
  reviews third. No steps skipped, no shortcuts. The standard
  ship-it pipeline.
orchestrator-model: inherit
agent-model: sonnet
phases:
  - name: plan
    skill: ce:plan
    args: "$ARGUMENTS"
    gate: |
      Verify that ce:plan produced a plan file in docs/plans/.
      If no plan file was created, run ce:plan again.
      Do NOT proceed until a written plan exists.
      Record the plan file path for later phases.
  - name: work
    skill: ce:work
    gate: |
      Verify that implementation work was performed — files were
      created or modified beyond the plan. Do NOT proceed if no
      code changes were made.
  - name: review
    skill: ce:review
    args: "mode:autofix plan:$PLAN_PATH"
  - name: todo-resolve
    skill: compound-engineering:todo-resolve
  - name: test-browser
    skill: compound-engineering:test-browser
  - name: feature-video
    skill: compound-engineering:feature-video
  - name: done
    signal: "<promise>DONE</promise>"
review-preferences:
  min-reviewers: 3
  require-categories:
    - correctness
    - security
  prefer-categories:
    - architecture
    - testing
    - performance
  synthesis: always
synthesis:
  agent: always
  lens: |
    Standard review synthesis. Showstoppers must be fixed before
    proceeding. Surface meaningful patterns but don't nitpick.
    Group findings by impact, not by reviewer. Recommend which
    items to fix now vs. track as follow-up todos.
---

You are a no-nonsense build pipeline. Execute each phase in strict
order. Respect gates — if a gate fails, retry the phase before
moving on. Pass the plan path from the plan phase through to review.

## Skip Rules

This orchestrator does not skip steps. Every phase runs in order.
For a lighter workflow, use a different orchestrator.
