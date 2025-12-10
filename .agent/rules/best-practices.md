---
trigger: manual
---

Code & Architecture
• 	Backend ↔ Frontend ↔ LLM Integration
• 	Every backend feature must have a corresponding UI component or LLM prompt/tool.
• 	Integration points must be explicitly commented with  in code.
• 	Modularity
• 	Frontend files capped at 300–600 lines; split into components/modules if larger.
• 	Backend services must expose clear APIs with documented contracts.
• 	Testing
• 	Every new feature requires at least one unit test and one integration test.
• 	LLM prompt flows must include mock tests to validate context injection.
• 	Documentation
• 	Missing dependencies or design gaps must be logged with  NOTE or  FIXME.
• 	Suggestions for improvement logged as  FEATURE with  metadata.
• 	Security & Performance
• 	Security concerns tagged with  SECURITY and risk level.
• 	Performance issues tagged with  OPTIMIZE.