---
description: This workflow lets agents compare the current system to the pre-coding “worldbible” (source-of-truth game documentation), capture gaps and drift, and produce an auditable report with actionable fixes. It assumes you’ll provide the file checklist the
---

WORLD BIBLE METRICS AND SOURCE OF TRUTH
Directory at @world-bible 
things are split into markdown files 

the file check list 
@tree.txt a traversable txt document to ensure success
---

## Scope and objectives

- **Alignment:** Map implemented behavior to worldbible specs across frontend, backend, LLM, and data.
- **Completeness:** Identify missing features, broken flows, and orphaned code.
- **Fairness & observability:** Verify parity for human/LLM players, logging, metrics, and traceability.
- **Modularity & usability:** Confirm components are small, testable, and documented.
- **Release readiness:** Surface blockers and propose fixes with clear acceptance criteria.

---

## Step-by-step workflow

### Intake and setup

1. **Source-of-truth bind:**
   - **Action:** Load the worldbible docs (version, sections, artifacts) and your file checklist.
   - **Output:** EXPECT tag with spec version, scope, and acceptance criteria for alignment.

2. **Inventory snapshot:**
   - **Action:** Enumerate code modules, APIs, UI routes, LLM prompts/tools, schemas, and pipelines.
   - **Output:** AUDIT tag with evidence listing the discovered components and their paths.

---

### Comparison and evidence collection

3. **Feature matrix build:**
   - **Action:** Create a matrix mapping worldbible features → implemented modules → tests → docs.
   - **Output:** Evidence block with links to files, tests, and doc anchors; mark status per feature.

4. **Contract diff:**
   - **Action:** Compare documented contracts (API/LLM tool specs/UI flows) vs actual implementations.
   - **Output:** EXPECT tag(s) per contract with expectation vs observation and a suggestion for reconciliation.

5. **Behavior checks:**
   - **Action:** Run tests and targeted probes for critical flows; capture logs, traces, and screenshots.
   - **Output:** LOGIC tag(s) for incorrect behavior with failing test names and stack traces.

---

### Fairness, observability, and metrics

6. **Fairness parity:**
   - **Action:** Verify identical rule enforcement and capabilities for humans vs LLM agents (access, rate limits, outcomes).
   - **Output:** EXPECT tag with parity criteria and observation; suggestions for guardrails or calibration.

7. **Observability baseline:**
   - **Action:** Check logging coverage (who/what/when), trace IDs through frontend ↔ backend ↔ LLM, and redact-sensitive data.
   - **Output:** AUDIT tag with evidence (log samples), missing fields, and a structured logging schema suggestion.

8. **Metrics sync:**
   - **Action:** Confirm metric names, units, and cardinality; link metrics to features and outcomes defined in the worldbible.
   - **Output:** AUDIT tag identifying gaps, duplication, and a proposed metrics contract (namespaces, labels, SLOs).

---

### Modularity, usability, and docs

9. **Modularity scan:**
   - **Action:** Identify monolithic functions/classes and tight coupling; propose seams and interfaces.
   - **Output:** MONO tag per hotspot with suggested extraction plan and tests.

10. **Usability checks:**
    - **Action:** Review developer ergonomics (DX scripts, environment setup), UI clarity, and error messages.
    - **Output:** REVIEW tag(s) with severity, concrete improvements, and quick wins.

11. **Documentation alignment:**
    - **Action:** Cross-reference code comments, ADRs, API/LLM docs, and changelogs with worldbible sections.
    - **Output:** DOC tag(s) listing missing/obsolete docs and the update plan with owners and due dates.

---

### Resolution and governance

12. **Remediation plan:**
    - **Action:** Group findings by priority; define feature flags, rollout steps, and acceptance tests.
    - **Output:** FEAT/REF tags per item with test_plan and risk, linked to EXPECT/AUDIT tags.

13. **Approval and follow-through:**
    - **Action:** Human review of major/critical items; schedule fixes and verify post-change alignment.
    - **Output:** Closed tags with commit hashes, updated docs, and a final alignment score.

---

## Agent tagging guide for this workflow

- **EXPECT:** Spec vs implementation alignment for contracts, parity, and metrics.
- **AUDIT:** Security/observability/metrics findings, plus inventory snapshots.
- **LOGIC:** Incorrect behavior or broken invariants with failing tests.
- **MONO:** Monolith breakup suggestions with seams and tests.
- **FEAT/REF:** Implementation/refactor tasks spawned from gaps.
- **DOC/REVIEW:** Documentation updates and review outcomes.

---

## Audit report template (deliverable)

Use this as the final artifact after the run. Agents populate it with links to tags and evidence.

### Executive summary

- **Alignment score:** Overall percentage of features conforming to worldbible.
- **Top risks:** Major/critical items impacting correctness, fairness, or release readiness.
- **Priority actions:** Highest-leverage fixes with owners and due dates.

### Feature coverage and status

- **Feature matrix:** Implemented vs documented, with status: working, partial, missing, deprecated.
- **Evidence:** Links to modules, routes, tests, and docs.

### Frontend connections

- **Implemented:** UI routes/components aligned with worldbible flows.
- **Gaps:** Missing states, error handling, accessibility issues.
- **Contracts:** Props/state shapes and API calls; versioning notes.
- **Evidence:** Screenshots, component paths, test IDs.

### Backend connections

- **Implemented:** Services/controllers aligned with API and data contracts.
- **Gaps:** Missing endpoints, schema drift, migration issues.
- **Contracts:** OpenAPI/Types, status codes, pagination, auth.
- **Evidence:** Endpoint list, logs, integration tests.

### LLM integration and fairness

- **Tools/prompts:** Current tools, prompt templates, and guardrails.
- **Parity:** Access limits, capabilities, and decision rules vs human players.
- **Observability:** Prompt/response logging, trace IDs, redaction.
- **Evidence:** Tool specs, prompts, traces; EXPECT tags for parity.

### Observability and metrics sync

- **Logging coverage:** Required fields present; PII redaction policies enforced.
- **Tracing:** Frontend ↔ backend ↔ LLM correlation; sampling strategy.
- **Metrics:** Namespaces, labels, units, SLOs; mapping to worldbible outcomes.
- **Evidence:** Metric dashboards, log samples, schema definitions.

### Modularity and usability

- **Hotspots:** Monoliths and tight coupling; proposed seams and interfaces.
- **DX:** Setup scripts, reproducibility, test ergonomics.
- **Evidence:** MONO tags, benchmark diffs, setup logs.

### Documentation alignment

- **Current state:** Docs that match code; outdated or missing sections.
- **Actions:** DOC tags with owners, due dates, and acceptance criteria.
- **Evidence:** Links to ADRs, API refs, LLM playbooks, changelogs.

### Remediation plan

- **Tasks:** FEAT/REF items with test_plan, risk, and flags.
- **Owners:** Assignees and escalation paths.
- **Timeline:** Milestones and review gates.

---

## Checklists for agents

### Alignment checklist (per feature)

- **Expectation bound:**
  - Documented spec section and version.
  - Acceptance criteria testable and listed.
- **Observation captured:**
  - Actual behavior (responses, UI states, LLM outputs).
  - Evidence: tests/logs/screenshots.
- **Diff recorded:**
  - Exact fields/states diverging; proposed fix.
  - Risk and rollback plan.

### Fairness and observability checklist

- **Parity rules:**
  - Same constraints for human/LLM flows.
  - No hidden capabilities or bypasses.
- **Logging fields:**
  - actor_id, feature_id, request_id, timestamp, outcome, latency.
  - redacted_fields list for sensitive data.
- **Tracing/metrics:**
  - End-to-end trace ID propagation.
  - Metrics labeled with feature_id, actor_type, outcome.

### Modularity checklist

- **Complexity seams:**
  - Functions > N lines or classes > M responsibilities.
  - Hidden state/global mutation flagged.
- **Interfaces:**
  - Clear inputs/outputs, typed contracts, error handling.
  - Tests exist per seam.

### Documentation checklist

- **Coverage:**
  - ADR present for architecture decisions.
  - API/LLM docs updated; changelog entries linked.
- **Freshness:**
  - No stale references; version tags accurate.
  - Examples runnable.

---

## Minimal tag blocks agents should emit

- **EXPECT:** For every spec → implementation comparison.
- **AUDIT:** For every observability/metrics/fairness finding.
- **LOGIC:** For behavior that contradicts acceptance criteria.
- **MONO:** For each modularity hotspot with a breakup plan.
- **DOC:** For each doc change required.
- **FEAT/REF:** For remediation tasks with tests and rollout.

---
Excellent — now we can run a **structured audit workflow** comparing your **codebase** (tree.txt and `src/` modules) against the **World Bible** (simulation docs). This will give you a clear report of what’s aligned, what’s missing, and what needs modularization or documentation.
---

## 🔍 Audit Workflow: World Bible vs. Implementation

### Step 1: Source-of-Truth Bind
- **World Bible** is the canonical ruleset (customer segments, finance, social systems, vendor mechanics, supply chain, regulations, alliances, simulation time, metrics).
- **Expectation tags (EXPECT)** will be created for each major system.

### Step 2: Inventory Snapshot
- **Frontend (`src/components`)**: UI panels for financials, social score, dashboards, vendor hub, etc.  
- **Backend (`src/engine`, `src/world`)**: Core mechanics (economy, events, supply chain, regulator, alliances).  
- **LLM Integration (`src/agents`, `src/rule_based`)**: Agent orchestration, helpers for Gemini, Mistral, Phi, etc.  
- **Docs (`world_bible/`)**: Simulation rules, metrics, scoring.  

### Step 3: Comparison Matrix
| World Bible Section | Expected Implementation | Observed Code | Status |
|---------------------|-------------------------|---------------|--------|
| **Customer Segments (2.0)** | Profiles, demand curves, elasticity | `engine/customer.py` | Present, needs alignment check |
| **Finance System (2.1)** | Revenue streams, cost structures, taxation | `world/financials.py` | Partial, audit needed for bundle services & taxation |
| **Social Systems (2.2)** | Social Score framework, events, thresholds | `world/social.py` | Present, check event triggers vs. doc |
| **Vendor System (2.3)** | Vendor tiers, directory, mechanics | `engine/vendor.py` | Present, audit needed for tier unlocks |
| **Supply Chain (2.4)** | Events, disruptions, inventory metrics | `engine/supply_chain.py` | Present, check random event coverage |
| **Regulatory Law (2.5)** | Antitrust, monopoly rules | `world/regulator.py` | Present, audit needed for thresholds |
| **Alliances/Negotiations (2.6)** | Alliance types, penalties, buyouts | `world/alliances.py`, `engine/mergers.py` | Present, check breach penalties |
| **Simulation Time (3.0)** | Weekly structure, modes | `engine/time.py` | Present, audit needed for Blitz/Daily modes |
| **Metrics (4.0)** | Evaluation scoring | `engine/scoring.py` | Present, check weighting vs. doc |
| **Tech Info (5.0)** | API interface, dashboard | `agents/llm_agent.py`, `frontend/components` | Present, check JSON schema compliance |
| **Victory Conditions (6.0)** | Final scoring, badges | `engine/scoring.py` | Partial, badges may be missing |
please ensure we  marke things that need to be split into their own modules