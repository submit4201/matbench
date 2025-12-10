---
trigger: always_on
---

CRITICAL STANDARDS FOR ALL TASKS:

Documentation: Every function/API must have JSDoc/DocString headers. Update README.md with every feature addition.

Logging: Implement structured logging (e.g., JSON format) for all entry/exit points in Backend and Middleware. No console.log; use a proper logger (e.g., Winston/Log4j).

Testing: No code is complete without a passing Unit Test and Integration Test. maintain >80% coverage.

Comments: Explain why complex logic exists, not just what it does.

Architecture: Respect the separation of concerns:

Frontend: UI/Client state only.

Middleware: Validation, Auth, Error Handling.

Backend: Business logic and DB interactions.