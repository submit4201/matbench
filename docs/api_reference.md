# REST API Reference

The backend exposes a REST API via FastAPI. Below are the available endpoints.

## Game & Simulation

| Method | Endpoint          | Description                                                              |
| :----- | :---------------- | :----------------------------------------------------------------------- |
| `GET`  | `/scenarios`      | List all available game scenarios                                        |
| `POST` | `/start_scenario` | Start a new game session with a selected scenario                        |
| `GET`  | `/state`          | Get the full current game state (defaults to `p1`)                       |
| `POST` | `/next_turn`      | Advance the simulation to the next week (triggers AI turns)              |
| `GET`  | `/events`         | Query game events from the event ledger (filters: category, week, agent) |

## Player Actions

| Method | Endpoint             | Description                                                                 |
| :----- | :------------------- | :-------------------------------------------------------------------------- |
| `POST` | `/action`            | Execute a player action (Set Price, Buy Supplies, Upgrade, Marketing, etc.) |
| `POST` | `/negotiate`         | Negotiate a price with a vendor                                             |
| `POST` | `/diplomacy/propose` | Propose a diplomatic action (Alliance, Buyout, etc.)                        |

## Proposals (Revenue Streams)

| Method | Endpoint                           | Description                          |
| :----- | :--------------------------------- | :----------------------------------- |
| `GET`  | `/proposals`                       | Get submitted proposals for an agent |
| `POST` | `/proposals`                       | Submit a new revenue stream proposal |
| `POST` | `/proposals/{proposal_id}/approve` | Approve a proposal (Admin/Debug)     |
| `POST` | `/proposals/{proposal_id}/reject`  | Reject a proposal                    |

## Enhanced Systems

| Method | Endpoint                     | Description                          |
| :----- | :--------------------------- | :----------------------------------- |
| `GET`  | `/credit/{agent_id}`         | Get detailed credit report and score |
| `POST` | `/credit/{agent_id}/payment` | Process a loan payment               |
| `GET`  | `/calendar/{agent_id}`       | Get agent's calendar and schedule    |
| `GET`  | `/zone/{agent_id}`           | Get neighborhood zone information    |

---

# Finance System Internal Reference

This document provides a reference for the core components of the Finance System implementation.

## Bank System (`src.engine.finance.bank`)

The `BankSystem` acts as the central financial authority in the simulation.

### `BankSystem`

**Key Methods:**

#### `calculate_quarterly_tax(state: LaundromatState, quarter: int) -> Dict[str, float]`

Calculate taxes for a specific quarter based on World Bible 2.3.3.

- **Args:**
  - `state`: Current agent state.
  - `quarter`: Fiscal quarter (1-4).
- **Returns:** Dictionary with `tax_owed`, `net_profit`, `credits_applied`, etc.

#### `generate_operating_bills(state: LaundromatState, report: FinancialReport) -> List[Bill]`

Generate weekly operating bills (Rent, Utilities, Labor, etc).

- **Returns:** List of unpaid `Bill` objects.

#### `process_payment(state: LaundromatState, bill_id: str) -> Dict[str, Any]`

Process a bill payment.

- **Returns:** Success status and balances.

## Credit System (`src.engine.finance.credit`)

Manages FICO-like credit scoring and loan products.

### `CreditSystem`

**Key Methods:**

#### `apply_for_loan(agent_id, loan_type, amount, current_week) -> Dict`

Apply for a loan given current credit score.

- **Loan Types:** `operating_credit`, `equipment_loan`, `expansion_loan`, `emergency_loan`.
- **Returns:** Approval details and terms (interest rate, payment).

#### `make_payment(agent_id, payment_id, amount, current_week) -> Dict`

Process a loan payment and update credit score.

- **Impact:**
  - On Time: +2 pts
  - Late (<30 days): -5 pts
  - Default (90+ days): -50 pts

#### `get_credit_report(agent_id) -> Dict`

Get comprehensive credit details.

- **Returns:** Score (300-850), Rating, utilization ratio, active accounts history.

## Financial Models (`src.engine.finance.models`)

### Data Structures

#### `Transaction`

Immutable ledger entry.

- `amount`: float
- `category`: `TransactionCategory` (REVENUE, EXPENSE, TAX, etc)
- `description`: str
- `week`: int

#### `FinancialLedger`

Append-only log of all financial events.

- `add(...)`: Record new transaction.
- `balance`: Real-time cash balance derived from history.

#### `Loan`

Active loan obligation.

- `interest_rate_monthly`: Base rate + risk premium.
- `weeks_remaining`: Count down to maturity.

#### `CreditScore`

FICO-like score component tracker.

- `total_score`: 300-850 integer.
- `payment_history_score`: 35% weight.
- `utilization_score`: 30% weight.
