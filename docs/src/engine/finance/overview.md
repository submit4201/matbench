# Module: Finance

## Path

`src/engine/finance/`

## Overview

The `finance` package handles all monetary transactions, accounting, and financial instruments (loans, credit, taxes). It has been recently refactored to be modular, replacing the legacy monolithic logic in `GameEngine`.

## Components

### `FinancialSystem` (Alias for `BankSystem`)

- **Type**: Controller Class
- **Path**: `src/engine/finance/bank.py`
- **Visibility**:
  - **Internal**: Main entry point for `GameEngine`.
- **Responsibilities**:
  - Central coordinator for sub-systems (Credit, Tax, Bills).
  - `process_week()`: orchestrates weekly financial updates.

### Sub-Systems

- **`CreditSystem`** (`credit.py`): Manages credit scores, credit limits, and loan eligibility.
- **`LoanSystem`** (`loans.py`): Manages active loans, interest calculations, and amortization.
- **`TaxSystem`** (`tax.py`): Calculates estimated taxes and processes quarterly payments.
- **`BillSystem`** (`bills.py`): Generates recurring bills (Rent, Utilities).

### Data Models (`models.py`)

- **`FinancialReport`**: Weekly summary of performance.
- **`FinancialLedger`**: Introduction of double-entry-like tracking (or at least granular transaction logging).
- **`Transaction`**: Immutable record of a money move.

## Refactoring Suggestions

- **`GameEngine` Integration**: `GameEngine` still contains `_process_financials` which duplicates some logic or acts as a pre-processor.
  - _Suggestion_: Fully migrate `_process_financials` logic into `RevenueStream.calculate()` methods within the Finance system.
- **Naming**: `BankSystem` acts as the `FinancialSystem`.
  - _Suggestion_: Rename `BankSystem` to `FinancialController` to avoid confusion with "Banks" as game entities.
# !  agreeed lets do this 