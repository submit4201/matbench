# Module: World

## Path

`src/world/`

## Overview

The `world` package definitions the data structures and entities that populate the game world. These are primarily state containers with minimal logic (though some helper methods exist).

## Classes

### `LaundromatState` (`laundromat.py`)

- **Type**: Data Class / State Container
- **Visibility**:
  - **Core**: The heart of the simulation state for each player.
  - **UI**: Serialized and sent to frontend via `/state`.
- **Key Fields**:
  - `balance`: Cash on hand.
  - `social_score`: `SocialScore` object (Reputation).
  - `inventory`: Dict of supplies.
  - `machines`: List of `Machine` objects.
  - `event_ledger`: `EventLedger` for tracking history.
  - `ledger`: `FinancialLedger` for financial history.

### `EventLedger` (`event_ledger.py`)

- **Type**: History/Log System
- **Description**: Stores all significant game events (`GameEvent`) for an agent (tickets, sales, dilemmas).
- **Usage**: Used to render the "Activity Feed" in the UI and provide context to LLM Agents.

### `RegulatoryBody` (`regulator.py`)

- **Type**: Entity / System
- **Description**: Represents the government or authority. Issues fines and checks compliance.

### `Neighborhood` (`neighborhood.py`)

- **Type**: Data Model
- **Description**: Defines the zone/area where the laundromat exists (Traffic, Tier, Rent).

## Refactoring Suggestions

- **`LaundromatState` Bloat**: This class is becoming a god object holding everything.
  - _Suggestion_: Split into components. `InventoryComponent`, `MachineFleetComponent`. `LaundromatState` should just be a container of these components. # [ ] TOD) lets get some models and components setup for the laundromat state system  keep in mind we want to be able to have multiple laundromats in the world and each one should have its own state. to some extent its each player has there state and  that hold their laundromats and the laundromats have their own state. and then theres the game state, world state, and financial state.  
- **Serialization**: Currently handled in `server.py` with manual `__dict__` copying.
  - _Suggestion_: Add `to_dict()` or Pydantic models to these classes for auto-serialization. # [ ] TODO pydantic models maybe a good idea but we need to make sure we can handle the nested objects and relationships between them. 