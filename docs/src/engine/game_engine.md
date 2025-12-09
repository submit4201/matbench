# Module: GameEngine

## Path

`src/engine/game_engine.py`

## Overview

The `GameEngine` is the central controller for the simulation. It manages the main game loop (`process_turn`), state updates, time progression, and orchestrates other subsystems (Economy, Events, Social, etc.). It acts as the "Source of Truth" for the game state.

## Classes

### `GameEngine`

- **Type**: Class
- **Visibility**:
  - **Internal**: Core logic.
  - **UI**: Exposed via `server.py` -> `get_state`.
  - **LLM**: Agents interact with it via `submit_action` and receive data from it via `Observation`.
- **Connections**:
  - **Manages**: `LaundromatState` (per agent).
  - **Uses**:
    - `TimeSystem` (Time tracking)
    - `EventManager` (Random events) # [ ] this should be handled by the game master world events system
    - `FinancialSystem` (Billing, taxes - _Partial integration_)
    - `VendorManager` (Supply chain) # [ ] this should be handled by the game master world vendors system
    - `TrustSystem` (Alliances)
    - `CommunicationChannel` (Messaging) # [ ] this should be handled by the game master communication system if not a player or llm player
    - `MetricsAuditor` (Logging)
- **Key Methods**:
  - `process_turn()`: Advances the simulation by one week. Triggers traffic, financial calculations, events, and time advancement.
  - `submit_action(agent_id, action)`: Queues user/agent actions for processing.
  - `_apply_action(state, action)`: Executes a specific action (e.g., BUY_INVENTORY, SET_PRICE).
  - `_process_financials(state, ...)`: **Legacy/Hybrid**. Calculates revenue/expenses. _Note: Moving towards `FinancialSystem`._ # REFACTOR [ ]

## Refactoring Suggestions

- **Monolithic `_apply_action`**: This method is a large switch-statement-like block.
  - _Suggestion_: Implement the Command Pattern or a Dispatcher logic. Each `ActionType` could have a handler class (e.g., `BuyInventoryHandler`, `SetPriceHandler`). $ REFACTOR [ ] 
# TODO: i like the command pattern idea each command has a handler and a receiver
- **`_process_financials` Complexity**: This method mixes logic for revenue calculation, inventory usage, and reporting. # [ ] TODO: move to financial system
  - _Suggestion_: Move detailed revenue logic to `RevenueSystem` or `EconomySystem`. Move cost calculations to `CostSystem` or deeper into `FinancialSystem`. # [ ] TODO: move to financial system or economy system  
- **Hardcoded Values**: Many magic numbers (e.g., `$250 rent`, `0.15 water cost`) are inside the code.
  - _Suggestion_: Move these to a `GameBalanceConfig` or `Scenario` configuration file. # [ ] TODO: move to game config so when we add different game modes we can change these values without touching the code
