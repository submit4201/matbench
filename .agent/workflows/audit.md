---
description: security 
---

Audits (Security / Performance / Data)
Objectives
• 	Detect vulnerabilities, inefficiencies, and data risks.
• 	Provide evidence-backed findings with actionable fixes.
• 	Maintain continuous compliance and resilience.
Steps
1. 	Scope Audit
• 	Define audit type: security, performance, or data.
• 	Create AUDIT tag with scope, severity, and evidence fields.
2. 	Security Audit
• 	Check input validation, secrets handling, file/command guardrails.
• 	Verify workspace trust policies.
• 	Output: LOGIC or EXPECT tags for violations.
3. 	Performance Audit
• 	Profile hot paths, queries, and cache usage.
• 	Identify N+1 queries, memory leaks, or blocking calls.
• 	Output: REF or MONO tags for refactor suggestions.
4. 	Data Audit
• 	Verify schema alignment, migrations, and data retention policies.
• 	Check compliance with privacy/security standards.
• 	Output: EXPECT tags for spec ↔ implementation mismatches.
5. 	Evidence Collection
• 	Logs, traces, benchmarks, test reports.
• 	Attach to evidence field in AUDIT tag.
6. 	Resolution Plan
• 	Suggest fixes with rollback strategy.
• 	Assign priority and due date.
• 	Output: suggestion + risk fields.
7. 	Review & Approval
• 	REVIEW tags for each major finding.
• 	Approval required for changes affecting security or data.
Rules
• 	Every major/critical finding must include evidence.
• 	Security fixes require human approval before merge.
• 	Performance fixes must not regress correctness.
• 	Data changes must align with compliance policies.
-----------------------------------------------------------------
   [[tag]]: AUDIT
   [[id]]: AG-2025-12-07-015
   [[title]]: Secrets exposed in config
   [[scope]]: backend
   [[severity]]: critical
   [[priority]]: P1
   [[status]]: open
   [[requires_approval]]: true
   [[labels]]: ["security","compliance"]

   {{expectation}}:
   Secrets stored in vault; config files reference env vars only.

   {{observation}}:
   Hardcoded API keys in config.yaml.

   {{suggestion}}:
   Move secrets to vault; inject via env vars.

   {{risk}}:
   High; potential credential leak. Immediate fix required.

   {{evidence}}:
   config/config.yaml:L12-L18; CI logs showing exposed key.

   {{test_plan}}:
   Verify vault integration; run security scan; regression tests.

   {{notes}}:
   Block release until resolved.
---------------------------------------------------------------------------------------
Workflow: Logical Audit (LOGIC)
Objectives
• 	Identify incorrect conditions, broken invariants, or faulty state transitions.
• 	Provide evidence-backed findings with actionable fixes.
• 	Ensure every logic audit is traceable, testable, and reviewable.

Step-by-Step Instructions
1. 	Scope Definition
• 	Agent scans target module/function for logic paths.
• 	Create a LOGIC tag with scope, severity, and expectation fields.
• 	Example: “Function should return false if input is empty.”
2. 	Expectation vs Observation
• 	Expectation: What the system should do (spec, ADR, contract).
• 	Observation: What the system actually does (tests, traces, logs).
• 	Output: Fill expectation and observation blocks in LOGIC tag.
3. 	Evidence Collection
• 	Gather failing test cases, stack traces, or logs.
• 	Attach to evidence field in LOGIC tag.
• 	Example: “tests/test_auth.py::test_empty_password fails with True instead of False.”
4. 	Suggestion & Risk
• 	Suggest fix with constraints and rollback plan.
• 	Document potential side-effects (blast radius).
• 	Example: “Invert condition in validate() → risk: may affect legacy clients.”
5. 	Test Plan
• 	Define new/updated tests to confirm fix.
• 	Include edge cases and regression checks.
• 	Example: “Add tests for empty, null, and whitespace inputs.”
6. 	Review & Approval
• 	REVIEW tag linked to LOGIC tag.
• 	Approval required for major/critical severity.
• 	Checklist: correctness, coverage, rollback ready.
7. 	Resolution
• 	Implement fix in branch .
• 	Run full test suite.
• 	Update docs if behavior changes.
• 	Close LOGIC tag with final notes + commit hash.

Rules for Logical Audits
• 	Every finding must include evidence. No vague “this looks wrong.”
• 	Severity mapping:
• 	Minor → edge case misbehavior.
• 	Major → common path incorrect.
• 	Critical → security or data integrity risk.
• 	Approval required: For major/critical fixes.
• 	Coverage threshold: Fix must include regression tests.
• 	Docs alignment: If logic changes observable behavior, update specs/docs.
-----------------------------------------------------------------------------
   [[tag]]: LOGIC
   [[id]]: AG-2025-12-07-020
   [[title]]: Incorrect validation of empty password
   [[scope]]: backend
   [[severity]]: major
   [[priority]]: P2
   [[status]]: open
   [[requires_approval]]: true
   [[labels]]: ["logic","auth","security"]

   {{expectation}}:
   validate(password) returns False if input is empty.

   {{observation}}:
   validate("") returns True, allowing empty passwords.

   {{suggestion}}:
   Update condition to check length > 0; add regression tests.

   {{risk}}:
   Medium; may break legacy clients relying on empty password bypass.

   {{evidence}}:
   tests/test_auth.py::test_empty_password fails; logs show True return.

   {{test_plan}}:
   Add tests for empty, null, whitespace; run full auth suite.

   {{notes}}:
   Requires human approval before merge.
-------------------------------------------------------------------------------
