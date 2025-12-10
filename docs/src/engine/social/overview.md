# Module: Social Engine

## Path

`src/engine/social/`

## Overview

The `social` package has been expanded to include a robust communication system, alliance management, and narrative control. It moves beyond simple "Social Scores" to simulate complex interactions between agents, NPCs, and the world.

## Components

### `CommunicationSystem` (`communication.py`)

- **Type**: System
- **Description**: Handles all message passing (DM, Group, Public, Formal).
- **Features**:
  - **Channels**: strict visibility rules (e.g., DMs are private).
  - **Intent Tracking**: Messages have semantic intents (`PROPOSAL`, `THREAT`, etc.).
  - **Game Master Hooks**: Ready for sentiment/deception analysis.

### `TrustSystem` (`alliances.py`)

- **Type**: System
- **Description**: Manages trust metrics (0-100) between agents and tracks active alliances.
- **Alliance Types**: Non-Aggression, Price Stability, Joint Marketing.

### `NarrativeManager` (`narrative_manager.py`)

- **Type**: "Director" System
- **Description**: Manages story threads and NPC dialogue generation. Bridges the simulation data with LLM-generated flavor text.

### `EthicalEventManager` (`ethical_events.py`)

- **Type**: Event System
- **Description**: Generates moral dilemmas for players.

### `Neighborhood` (`neighborhood.py`)

- **Type**: Data Model
- **Description**: Represents the physical/demographic context of the laundromat (Traffic, Tier).

## Refactoring Suggestions

- **`GameEngine` Integration**: `GameEngine` still holds `CommunicationChannel` (legacy).
  - _Suggestion_: Replace legacy channel with `CommunicationSystem`.
- **Event Unification**: `EthicalEventManager` and `NarrativeManager` both trigger "Events".
  - _Suggestion_: Create a unified `SocialEvent` or `NarrativeEvent` pipeline. and this should be used by the game master to generate events and gets judged by the judge once implemented
