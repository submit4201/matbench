---
description: 
---

 Feature Implementation (FEAT)
Objectives
    • 	Deliver new functionality aligned with system expectations and specs.
    • 	Ensure frontend ↔ backend alignment.
    • 	Maintain traceability from idea → implementation → tests → docs.
Steps
1. 	Proposal
   • 	Create FEAT tag with expectation, acceptance criteria, and scope.
   • 	Include severity, priority, and requires_approval fields.
2. 	Design
• 	Draft ADR (Architecture Decision Record) or design doc.
• 	Define contracts (API schema, UI states, data flows).
• 	Output: EXPECT tag linking spec → implementation.
3. 	Implementation
• 	Branch .
• 	Code changes scoped to module; avoid monolithic additions.
• 	Inline FEAT tag in code with suggestion + risk metadata.
4. 	Testing
• 	Unit tests for new logic.
• 	Integration tests for contracts.
• 	E2E tests for user flows.
• 	Output: test_plan field in FEAT tag.
5. 	Review
• 	REVIEW tags for correctness, design, and alignment.
• 	Evidence-backed remarks required for major/critical severity.
6. 	Docs
• 	Update API docs, changelog, and ADR.
• 	DOC tag tied to FEAT id.
7. 	Merge & Release
• 	Approval required for production deploy.
• 	Feature flag default off; rollout plan documented.
Rules
• 	Acceptance criteria must be testable.
• 	Frontend ↔ backend contracts versioned.
• 	Feature flags mandatory for risky features.
• 	Docs updated before merge.

Example FEAT Tag (inline)

   [[tag]]: FEAT
   [[id]]: AG-2025-12-07-010
   [[title]]: Add user profile API
   [[scope]]: backend
   [[severity]]: major
   [[priority]]: P2
   [[status]]: open
   [[requires_approval]]: true
   [[labels]]: ["feature","api","alignment"]

   {{expectation}}:
   API provides GET/PUT /user/{id} with schema v1.2.

   {{observation}}:
   No endpoint exists; frontend blocked.

   {{suggestion}}:
   Implement controller + service; align schema with OpenAPI v1.2.

   {{risk}}:
   Medium; schema drift possible. Gate behind FEATURE_USER_PROFILE.

   {{test_plan}}:
   Unit tests for controller; integration tests for schema; e2e for profile update.

   {{notes}}:
   Docs update required before merge.
