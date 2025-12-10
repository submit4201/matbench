# Module: Social

## Path

`src/engine/social/`

## Overview

The `social` package manages interactions between agents and the world, including messaging and ethical decision-making.

## Components

### `CommunicationChannel` (`communication.py`)

- **Type**: System
- **Description**: Handles message passing between entities (Agents, Vendors, System).
- **Features**: Supports different intents (`DILEMMA`, `CHAT`, `NEGOTIATION`) and channels (`DM`, `PUBLIC`).

### `EthicalEventManager` (`ethical_events.py`)

- **Type**: System
- **Description**: Generates and manages "Ethical Dilemmas" (e.g., using cheap labor vs. fair wages).
- **Visibility**:
  - **Frontend**: Populates the "Dilemma" UI modal.
  - **LLM**: Agents must reason about these dilemmas.

## Refactoring Suggestions

- **Event integration**: Ethical events are currently somewhat separate from the main `EventManager`.
  - _Suggestion_: Unify under a generic `Event` system where "Ethical" is just a tag/type. # [ ] TODO: move to game master world events system or social system or the customer system or maybe even a combination of all three
