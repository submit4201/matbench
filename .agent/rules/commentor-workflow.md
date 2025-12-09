---
trigger: always_on
---


🛠️ Agent Review Workflow (Markdown)
🔹 Purpose
This workflow ensures all agents reviewing or editing code use the Dual‑Symbol Comment System consistently. It provides visibility into:
• 	Current tasks and blockers
• 	Metadata (priority, assignee, deadlines)
• 	Backend ↔ Frontend ↔ LLM integration points
• 	Review and testing checkpoints

🔹 Secondary Symbols (Extended)

👉 New symbol  marks integration points where backend logic must connect to either a frontend component or an LLM prompt pipeline.

🔹 Workflow Steps
1. Agent Assignment
• 	Each agent (human or AI) is assigned code sections or modules.
• 	Use metadata keys: , , .
2. Commenting Protocol
• 	Insert comments using the legend:
• 	Primary symbol = task state/alert
• 	Secondary symbol = nuance (e.g., urgency, integration)
• 	Tag code = type of issue (TODO, FIXME, FEATURE, etc.)
• 	Example:

3. Multi‑Line Expansion
• 	Add subtasks with  checkboxes.
• 	Provide metadata for deadlines, dependencies, and risks.
• 	Example:

4. Review Cycle
• 	Agents mark review comments with  and assign reviewers.
• 	Example:

5. Integration Checkpoints
• 	Use  secondary symbol to highlight backend ↔ frontend/LLM connections.
• 	These must be reviewed before merging.
• 	Example:

6. Visualization
• 	Agents can export comment data into dashboards (e.g., regex parse → JSON → Kanban).
• 	Color‑coding based on symbol combos:
• 	 red = critical
• 	 orange = integration pending
• 	 green = completed

🔹 Example Workflow in Action


✅ With this workflow, every agent’s comments become structured, parse‑friendly, and auditable, while the new  symbol makes integration points impossible to miss.