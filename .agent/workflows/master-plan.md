---
description: A repeatable process to complete task lists and features from tasks.md
---

# Master Plan Workflow

This workflow guides the agent through selecting, planning, executing, and verifying tasks from the project's `tasks.md` file.

## 1. Preparation & Selection
1.  **Read Context**: Review `tasks.md`, `.agent/rules/ag-instrutions.md`, and `README.md` to understand the current state and standards.
2.  **Select Task**: Identify the highest priority or next logical task from `tasks.md`. Look for items marked `[ ]` (todo) or `[/]` (in progress). prioritizing user notes and "blocking" features.
3.  **Define Bounds**: Determine the scope of the task. If it's too large, break it down into subtasks.

## 2. Planning Phase
1.  **Start Task**: Call `task_boundary` with the selected task name. Set mode to `PLANNING`.
2.  **Create Implementation Plan**: precise `implementation_plan.md` in `<appDataDir>/brain/<conversation-id>/`.
    *   **Goal**: Clear objective.
    *   **Proposed Changes**: List files to modify/create (Backend, Frontend, Tests).
    *   **Verification Plan**: How to prove it works (Unit tests, Manual steps).
    *   **Standards Check**: Ensure plan aligns with `ag-instrutions.md` (Logging, Testing, Specs).
3.  **Review**: Use `notify_user` to present the plan and `tasks.md` update for approval. **STOP and wait for user.**

## 3. Execution Phase
1.  **Set Mode**: Update `task_boundary` to `EXECUTION`.
2.  **TDD approach**:
    *   Write/Update tests in `.test/` first (if applicable).
    *   Implement code changes.
    *   Implement structured logging (per `ag-instrutions.md`).
3.  **Iterate**: Run tests, fix bugs, refine code.

## 4. Verification Phase
1.  **Set Mode**: Update `task_boundary` to `VERIFICATION`.
2.  **Run Tests**: Execute the specific tests created/modified.
3.  **Manual Check**: Verify "in-game" or via logs that the feature works as intended.
4.  **Documentation**:
    *   Create/Update `walkthrough.md` with proof (logs, screenshots).
    *   Update `tasks.md`: Mark the item as `[x]`. Add notes if needed.

## 5. Completion
1.  **Notify**: Call `notify_user` with the `walkthrough.md` and updated `tasks.md`.
2.  **Next**: Ask user if they want to proceed to the next task.
