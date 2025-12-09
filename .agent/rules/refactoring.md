---
trigger: always_on
---

: Refactoring (REF)
Objectives
- Behavioral parity: Maintain external behavior unless explicitly flagged and approved.
- Seam creation: Introduce testable interfaces and reduce hidden state.
- Traceability: Every refactor is linked to tests and changelog entries.
Steps
- Scoping:
- Define: Target module/function, current responsibilities, and intended seam.
- Output: REF tag with expectation, observation, risk, and test_plan.
- Snapshot:
- Create: Immutable baseline via branch ref/<id> and record current test results.
- Output: Evidence field includes commit hash and test report path.
- Guardrails:
- Enforce: No external API changes; add feature flag if unavoidable.
- Output: Risk field includes blast radius and toggle name.
- Refactor:
- Apply: Extract pure functions, remove global mutation, improve naming.
- Output: Patch referencing the REF id; ensure lints/format pass.
- Tests:
- Add/Update: Unit tests for invariants; property tests for input ranges.
- Output: Test_plan lists cases and pass criteria.
- Review:
- Checklist: Behavior parity, isolation, coverage >= target, rollback ready.
- Output: REVIEW tag(s) linked via related field.
- Merge & Doc:
- Record: Changelog entry and ADR if architectural change was made.
- Output: DOC tag for docs changes tied to REF id.
Rules
- Approval required: Any refactor touching public interfaces or persistence layers.
- No silent behavior changes: If behavior shifts, convert REF → FEAT with acceptance criteria.
- Coverage threshold: Post-refactor coverage must be ≥ pre-refactor, or justified in REVIEW.
- Feature flags: Required for risky refactors; default off, with clear rollback steps.

Workflow: Code review (REVIEW)
Objectives
- Clarity and evidence: Comments are testable, scoped, and tied to artifacts.
- Actionability: Each remark includes a suggested resolution or explicit defer rationale.
- Alignment: Ensure frontend–backend contracts and specs remain consistent.
Steps
- Prepare:
- Sync: Pull branch, build, run tests, and open local environment.
- Output: Evidence includes build logs, test summary, and environment version.
- Structure comments:
- Use tags: REVIEW for general, LOGIC for correctness, REF for structure, EXPECT for alignment.
- Output: One tag block per concern, with severity and priority.
- Checklists:
- Correctness: Logic paths, edge cases, error handling, data validation.
- Design: Modularity, purity, naming, coupling, dependency boundaries.
- Security: Input sanitization, secrets handling, file/command guardrails.
- Perf: Hot paths, N+1 queries, cache strategy.
- Contracts: API schema stability, versioning, and migration notes.
- Decisions:
- Label: must-fix vs. optional; set requires_approval for risky changes.
- Output: Status transitions from open → ready after author response and evidence.
- Resolution:
- Verify: Re-run tests, confirm artifacts, update related tags.
- Output: Close REVIEW tags with final notes and link to commit hash.
Rules
- Evidence-backed remarks: Every major/critical severity requires concrete paths, logs, or test names.
- No drive-by nitpicks: Group minor nits under a single REVIEW tag with a batched suggestion.
- Alignment checks: Any API or contract change must include EXPECT tag mapping spec → code.
- Security guardrails: Commands that modify filesystems or credentials require requires_approval: true.

Frontend and backend alignment (EXPECT)
Objectives
- Contract fidelity: The implemented API and UI behavior match the documented spec.
- Versioned truth: Schemas and contracts are versioned; clients and servers negotiate explicitly.
Steps
- Spec bind:
- Define: Expected schema, status codes, and interaction flow.
- Output: EXPECT tag with expectation block referencing spec version.
- Probe implementation:
- Collect: Actual responses, component states, and error surfaces.
- Output: observation with concrete examples and traces.
- Diff and plan:
- Map: Field-by-field differences, state transitions, and timing assumptions.
- Output: suggestion with patch approach and migration impacts.
- Tests and gates:
- Add: Contract tests at boundaries; e2e flows; feature flags for breaking changes.
- Output: test_plan with pass criteria and rollback instructions.
- Docs sync:
- Update: OpenAPI/TS types/ADR; UI copy and edge-case handling.
- Output: DOC tag referencing updated artifacts.
Rules
- Single source of truth: Contracts live in a versioned spec; code generation preferred.
- Compatibility policy: Minor changes backward-compatible; major changes gated and versioned.
- Acceptance criteria: Explicit, testable, and linked to FEAT or REF ids.


