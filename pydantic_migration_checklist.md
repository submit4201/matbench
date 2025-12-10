# Pydantic Model Migration Checklist

> **Principle**: Models should be **pure data holders** — no business logic, no side effects.
> Business logic belongs in service classes, managers, or engine modules.

---

## ✅ Already Migrated (in `src/models/`)

| Model | File | Status |
|-------|------|--------|
| `Action` | [agent.py](file:///e:/projects/repo_mat/matbench/src/models/agent.py) | ✅ Done |
| `Message` | [agent.py](file:///e:/projects/repo_mat/matbench/src/models/agent.py) | ✅ Done |
| `Observation` | [agent.py](file:///e:/projects/repo_mat/matbench/src/models/agent.py) | ✅ Done |
| `Machine` | [world.py](file:///e:/projects/repo_mat/matbench/src/models/world.py) | ✅ Done |
| `StaffMember` | [world.py](file:///e:/projects/repo_mat/matbench/src/models/world.py) | ✅ Done |
| `Building` | [world.py](file:///e:/projects/repo_mat/matbench/src/models/world.py) | ✅ Done |
| `LaundromatState` | [world.py](file:///e:/projects/repo_mat/matbench/src/models/world.py) | ✅ Done |
| `Transaction` | [financial.py](file:///e:/projects/repo_mat/matbench/src/models/financial.py) | ✅ Done |
| `FinancialLedger` | [financial.py](file:///e:/projects/repo_mat/matbench/src/models/financial.py) | ✅ Done |
| `Bill` | [financial.py](file:///e:/projects/repo_mat/matbench/src/models/financial.py) | ✅ Done |
| `RevenueStream` | [financial.py](file:///e:/projects/repo_mat/matbench/src/models/financial.py) | ✅ Done |

---

## 🔲 To Migrate — By Domain

### 1. World Core (`src/world/`)

| Class | File | Type | Notes |
|-------|------|------|-------|
| `SocialScore` | [social.py](file:///e:/projects/repo_mat/matbench/src/world/social.py) | dataclass | Has `total_score`, `tier` properties → move to `computed_field` |
| `SocialTier` | [social.py](file:///e:/projects/repo_mat/matbench/src/world/social.py) | Enum | Convert to `str, Enum` |
| `Ticket` | [ticket.py](file:///e:/projects/repo_mat/matbench/src/world/ticket.py) | dataclass | Pure data |
| `TicketType` | [ticket.py](file:///e:/projects/repo_mat/matbench/src/world/ticket.py) | Enum | Convert to `str, Enum` |
| `TicketStatus` | [ticket.py](file:///e:/projects/repo_mat/matbench/src/world/ticket.py) | Enum | Convert to `str, Enum` |
| `Regulation` | [regulator.py](file:///e:/projects/repo_mat/matbench/src/world/regulator.py) | dataclass | Pure data |
| `GameEvent` | [event_ledger.py](file:///e:/projects/repo_mat/matbench/src/world/event_ledger.py) | dataclass | Rename to `EventRecord` to avoid collision with core/events |
| `EventCategory` | [event_ledger.py](file:///e:/projects/repo_mat/matbench/src/world/event_ledger.py) | Enum | Convert to `str, Enum` |

---

### 2. Engine Core (`src/engine/core/`)

| Class | File | Type | Notes |
|-------|------|------|-------|
| `Season` | [time.py](file:///e:/projects/repo_mat/matbench/src/engine/core/time.py) | Enum | Convert to `str, Enum` |
| `Day` | [time.py](file:///e:/projects/repo_mat/matbench/src/engine/core/time.py) | Enum | Convert to `str, Enum` |
| `WeekPhase` | [time.py](file:///e:/projects/repo_mat/matbench/src/engine/core/time.py) | Enum | Convert to `str, Enum` |
| `EventType` | [events.py](file:///e:/projects/repo_mat/matbench/src/engine/core/events.py) | Enum | Convert to `str, Enum` |
| `GameEvent` | [events.py](file:///e:/projects/repo_mat/matbench/src/engine/core/events.py) | dataclass | Rename to `WorldEvent` to avoid collision |
| `ScheduledAction` | [calendar.py](file:///e:/projects/repo_mat/matbench/src/engine/core/calendar.py) | dataclass | Pure data |
| `CalendarReminder` | [calendar.py](file:///e:/projects/repo_mat/matbench/src/engine/core/calendar.py) | dataclass | Pure data |
| `ActionCategory` | [calendar.py](file:///e:/projects/repo_mat/matbench/src/engine/core/calendar.py) | Enum | Convert to `str, Enum` |
| `ActionPriority` | [calendar.py](file:///e:/projects/repo_mat/matbench/src/engine/core/calendar.py) | Enum | Convert to `str, Enum` |
| `ActionStatus` | [calendar.py](file:///e:/projects/repo_mat/matbench/src/engine/core/calendar.py) | Enum | Convert to `str, Enum` |

---

### 3. Commerce (`src/engine/commerce/`)

| Class | File | Type | Notes |
|-------|------|------|-------|
| `VendorTier` | [vendor.py](file:///e:/projects/repo_mat/matbench/src/engine/commerce/vendor.py) | Enum → int | Keep as int-based Enum |
| `SupplyOffer` | [vendor.py](file:///e:/projects/repo_mat/matbench/src/engine/commerce/vendor.py) | dataclass | Pure data |
| `VendorProfile` | [vendor.py](file:///e:/projects/repo_mat/matbench/src/engine/commerce/vendor.py) | dataclass | Pure data |
| `ProposalStatus` | [proposals.py](file:///e:/projects/repo_mat/matbench/src/engine/commerce/proposals.py) | Enum | Convert to `str, Enum` |
| `Proposal` | [proposals.py](file:///e:/projects/repo_mat/matbench/src/engine/commerce/proposals.py) | dataclass | Pure data |
| `SupplyChainEvent` | [supply.py](file:///e:/projects/repo_mat/matbench/src/engine/commerce/supply.py) | dataclass | Needs audit |
| `SupplyChainEventType` | [supply.py](file:///e:/projects/repo_mat/matbench/src/engine/commerce/supply.py) | Enum | Convert to `str, Enum` |

---

### 4. Social (`src/engine/social/`)

| Class | File | Type | Notes |
|-------|------|------|-------|
| `ChannelType` | [communication.py](file:///e:/projects/repo_mat/matbench/src/engine/social/communication.py) | Enum | Convert to `str, Enum` |
| `MessageIntent` | [communication.py](file:///e:/projects/repo_mat/matbench/src/engine/social/communication.py) | Enum | Convert to `str, Enum` |
| `Message` | [communication.py](file:///e:/projects/repo_mat/matbench/src/engine/social/communication.py) | dataclass | ⚠️ Conflicts with `src/models/agent.py` — merge or rename |
| `Group` | [communication.py](file:///e:/projects/repo_mat/matbench/src/engine/social/communication.py) | dataclass | Pure data |
| `AllianceType` | [alliances.py](file:///e:/projects/repo_mat/matbench/src/engine/social/alliances.py) | Enum | Convert to `str, Enum` |
| `Alliance` | [alliances.py](file:///e:/projects/repo_mat/matbench/src/engine/social/alliances.py) | dataclass | Pure data |

---

### 5. Population (`src/engine/population/`)

| Class | File | Type | Notes |
|-------|------|------|-------|
| `CustomerMemory` | [customer.py](file:///e:/projects/repo_mat/matbench/src/engine/population/customer.py) | dataclass | Pure data |
| `Persona` | [customer.py](file:///e:/projects/repo_mat/matbench/src/engine/population/customer.py) | class | Has `generate_random()` static method — keep method or move to factory |
| `CustomerSegment` | [customer.py](file:///e:/projects/repo_mat/matbench/src/engine/population/customer.py) | class (pseudo-enum) | Convert to `str, Enum` |

---

### 6. Finance (`src/engine/finance/`)

| Class | File | Type | Notes |
|-------|------|------|-------|
| `Loan` | [models.py](file:///e:/projects/repo_mat/matbench/src/engine/finance/models.py) | dataclass | Pure data |
| `TaxRecord` | [models.py](file:///e:/projects/repo_mat/matbench/src/engine/finance/models.py) | dataclass | Pure data |
| `TaxFilingStatus` | [models.py](file:///e:/projects/repo_mat/matbench/src/engine/finance/models.py) | dataclass | Pure data |
| `FinancialReport` | [models.py](file:///e:/projects/repo_mat/matbench/src/engine/finance/models.py) | dataclass | Pure data (many fields) |
| `TransactionCategory` | [models.py](file:///e:/projects/repo_mat/matbench/src/engine/finance/models.py) | Enum | Already `str, Enum` in `src/models/financial.py` |

---

### 7. History & Benchmark (`src/engine/`, `src/benchmark/`)

| Class | File | Type | Notes |
|-------|------|------|-------|
| `TurnRecord` | [history.py](file:///e:/projects/repo_mat/matbench/src/engine/history.py) | dataclass | Pure data (many fields) |
| `ScenarioDifficulty` | [scenarios.py](file:///e:/projects/repo_mat/matbench/src/benchmark/scenarios.py) | Enum | Convert to `str, Enum` |
| `EventConfig` | [scenarios.py](file:///e:/projects/repo_mat/matbench/src/benchmark/scenarios.py) | dataclass | Pure data |
| `InitialConditions` | [scenarios.py](file:///e:/projects/repo_mat/matbench/src/benchmark/scenarios.py) | dataclass | Has `__post_init__` → use `model_post_init` |
| `Scenario` | [scenarios.py](file:///e:/projects/repo_mat/matbench/src/benchmark/scenarios.py) | dataclass | Has `__post_init__` → use `model_post_init` |

---

### 8. Agents (`src/agents/`)

| Class | File | Type | Notes |
|-------|------|------|-------|
| `ActionType` | [base_agent.py](file:///e:/projects/repo_mat/matbench/src/agents/base_agent.py) | Enum | Already `str, Enum` ✅ |

