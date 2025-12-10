# Module: Commerce

## Path

`src/engine/commerce/`

## Overview

The `commerce` package handles the B2B (Business-to-Business) aspects of the simulation: dealing with Vendors, the Supply Chain, and Market mechanics.

## Components

### `VendorManager` (`vendor.py`)

- **Type**: System
- **Description**: Manages the list of `Vendor` entities. Handles price negotiation logic and order processing.
- **Key Classes**: `Vendor`, `VendorProfile`.

### `MarketSystem` (`market.py` / `EconomySystem`)

- **Type**: System # [ ]  needs implementation
- **Description**: Simulates broader economic conditions (Inflation, Recession, Booms). Currently simpler base logic in `GameEngine`.
- **Note**: Often aliased as `EconomySystem` in `GameEngine`.

### `SupplyChain` (`supply.py`)

- **Type**: System # [ ]  needs implementation
- **Description**: Simulates logistics. Deliveries can be delayed, lost, or early.

### `ProposalManager` (`proposals.py`)

- **Type**: System
- **Description**: Handles player proposals for new business features or revenue streams to the "Board" (Game Master).

### `MergerSystem` (`mergers.py`)

- **Type**: System
- **Description**: Logic for buyouts and acquiring competitors.

## Refactoring Suggestions

- **Separation of Concerns**: `Vendor.process_order` does a lot (inventory logic, relationship update, event generation). # !  agreeed lets do this 
  - _Suggestion_: Split `OrderProcessor` from `Vendor` entity.
