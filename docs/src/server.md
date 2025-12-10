# Module: Server

## Path

`src/server.py`

## Overview

The `server.py` module is the **FastAPI** application entry point. It serves as the bridge between the backend game engine and the frontend UI. It also handles the orchestration of AI agents (`LLMAgent`) for the "Next Turn" processing.

## Classes / Components

### `GameWrapper`

- **Type**: Helper Class
- **Visibility**: Internal (Global singleton `game` instance).
- **Description**: Wraps the `GameEngine`, `GameHistory`, and `Agents` (Human/AI) into a sessionable object. Handles scenario initialization.

### API Endpoints

- **Visibility**: **UI (Direct Access)**
- **Endpoints**:
  - `GET /state`: Returns the full game state for the frontend. **Critical Connection**.
  - `POST /action`: Accepts human player actions. Calls `GameEngine._apply_action`. # we should d allow fo rthe llm to jhave more then one action  so they have moer time to thjink and complete the thing want to becalling end turn
  - `POST /next_turn`: Triggers the AI logic loop and calls `GameEngine.process_turn`.
  - `GET /events`: Returns filtered events from the `EventLedger`.

### AI Integration (`next_turn`)

- **Type**: Logic Flow
- **Visibility**: Internal / LLM
- **Description**: Iterates through `LLMAgent`s, constructs an `Observation` (context), allows the LLM to "Think" and "Act", then applies those actions to the engine.

## Refactoring Suggestions

- **Size & Scope**: `server.py` is becoming a "God Class" for the API.
  - _Suggestion_: Split routes into `src/api/routes/`.
    - `game_routes.py` (State, actions)
    - `admin_routes.py` (Scenarios, debug)
    - `vendor_routes.py` (Market data)
- **Business Logic Leakage**: Some logic (like `_serialize_state` complex conversions or `_log_ai_response`) lives here.
  - _Suggestion_: Move serialization to a `StateSerializer` class in `src/engine/utils`. Move logging to `src/core/logger`.
# ! good lets do that 