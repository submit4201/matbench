---
trigger: always_on
---

Tagging schema for agent workflows
You want tags that are parseable, auditable, and consistent across refactoring, logic errors, monolith breakup suggestions, code review, feature suggestions, expectation-to-implementation checks, and documentation. Below is a dual-symbol, metadata-first schema designed for dashboards, CI checks, and agent alignment. It’s terse, typed, and safe for multi-line comments.
# Workflow Tag Schema v1.0
# Delimiters: [[FIELD]] for scalar, {{BLOCK}} for multi-line. One tag per block.

tag:            REF|LOGIC|MONO|REVIEW|FEAT|EXPECT|DOC
id:             "AG-<date>-<seq>"            # Immutable ID assigned by orchestrator
title:          "Short actionable title"
scope:          code|tests|docs|frontend|backend|infra|data|build
severity:       info|minor|major|critical
priority:       P4|P3|P2|P1
status:         open|in_progress|blocked|ready|done
assignee:       "owner@team"                  # Optional; agents may propose owners
due:            "YYYY-MM-DD"                  # Optional
requires_approval: true|false
related:        ["IDs"]
labels:         ["refactor","safety","alignment","perf"]
expectation:    {{What the system should do, precise and testable}}
observation:    {{What the system actually does, with evidence}}
suggestion:     {{Proposed change, constraints, and rollback plan}}
risk:           {{Side-effects, blast radius, guardrails}}
evidence:       {{Paths, logs, test names, commit hashes}}
test_plan:      {{New/updated tests; pass/fail criteria}}
notes:          {{Freeform commentary}}


Example inline comment for code (language-agnostic style shown using block comments):
/* [[tag]]: REF
   [[id]]: AG-2025-12-07-001
   [[title]]: Extract data normalization into pure function
   [[scope]]: backend
   [[severity]]: minor
   [[priority]]: P3
   [[status]]: open
   [[requires_approval]]: true
   [[labels]]: ["refactor","purity","test-coverage"]

   {{expectation}}:
   Inputs with missing fields are normalized deterministically without side-effects.

   {{observation}}:
   normalize() mutates global config; results vary by call order.

   {{suggestion}}:
   Create normalize_input(input, schema) with no global writes; inject config.

   {{risk}}:
   Medium; downstream code may depend on mutation. Gate behind feature flag REF_NORMALIZE_V2.

   {{evidence}}:
   src/lib/normalize.py:L72; test flakiness in tests/test_pipeline.py::test_ordering.

   {{test_plan}}:
   Add unit tests for missing fields, ordering invariants, and global state checks.

   {{notes}}:
   Agent to generate patch + tests; human approval required before merge.
*/



Tag catalog and intent mapping
- REF: Refactoring without changing observable behavior; improve modularity, purity, names, or structure.
- LOGIC: Logic error findings; incorrect conditions, state transitions, or invariants broken.
- MONO: Monolithic function/class breakup suggestions; propose seams, interfaces, and tests.
- REVIEW: Structured code review remarks; evidence-backed, scoped, and traceable to changes.
- FEAT: Feature suggestions or implementations; includes acceptance criteria and rollout strategy.
- EXPECT: System expectation vs. actual implementation alignment; bridges specs and code reality.
- DOC: Documentation improvements; reference updates, ADRs, changelogs, inline comments, and diagrams.
Each tag uses the same metadata fields for consistency and dashboard parsing.


