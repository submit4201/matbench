---
description: front and back
---


Step 1: Backend Feature Inventory
• 	Parse codebase for  TODO,  ALERT, and  FEATURE tags.
• 	Collect metadata: , , , .
• 	Build a list of all backend endpoints, services, and features.
Step 2: Frontend Mapping
• 	For each backend feature:
• 	Verify a UI component exists (form, button, menu, etc.).
• 	Check file size/modularity (≤600 lines).
• 	Confirm component is documented with  NOTE and linked to backend feature.
Step 3: LLM Integration Check
• 	Ensure backend features are exposed to LLMs via:
• 	Prompt templates
• 	Tool definitions
• 	Context injection pipelines
• 	Use  tags to mark integration points.
• 	Verify tests exist for prompt flows ( TEST with  metadata).
Step 4: Cross‑Audit
• 	Compare backend inventory vs frontend + LLM mapping:
• 	✅ Backend feature has UI + LLM integration → Pass
• 	⚠️ Backend feature missing UI or LLM integration → Flag with  BLOCKER
• 	❌ UI/LLM feature without backend support → Flag with  QUESTION
Step 5: Modularity & Premium Design Review
• 	Check frontend files for:
• 	Componentization (no monolithic files).
• 	Clear separation of concerns (logic, state, styling).
• 	Accessibility and responsive design.
• 	Ensure LLM prompts/tools follow premium design principles:
• 	Clear naming
• 	Modular prompt templates
• 	Explicit error handling
Step 6: Audit Report
• 	Generate a dashboard (parse comments → JSON → Kanban).
• 	Sections:
• 	✅ Features fully integrated
• 	⚠️ Features missing UI/LLM
• 	❌ Orphaned UI/LLM features
• 	🔧 Suggestions & improvements

🔹 Example Audit Comment

