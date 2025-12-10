# Module: Core Engine

## Path

`src/engine/core/`

## Overview

The `core` package contains fundamental gameplay systems that don't fit into a specific domain (like finance or social). These are the "Clock" and the "God" of the simulation.

## Components

### `TimeSystem` (`time.py`, `calendar.py`)

- **Type**: System
- **Description**: Tracks Weeks/Seasons. `CalendarManager` handles scheduling of future actions.
- **Key Concepts**: `WeekPhase`, `Season`, `ScheduledAction`. # ~ beeds daily timer and real time modes 

### `EventManager` (`events.py`)

- **Type**: System
- **Description**: The "Random Number Generator" of the world. Spawns `GameEvents` (Heatwaves, broken pipes, etc.). # [ ]  should be removed  in favor of  `NarrativeManager` and `GameMaster` 
# !  agreeed lets do this 
- **Usage**: Called by `GameEngine.process_turn`.

### `GameMaster` (`game_master.py`)

- **Type**: AI System / Judge
- **Description**: An LLM-backed evaluator that judges subjective player actions (Narrative choices, ethical reasoning, creative proposals). # [ ] also should be used for ethical events and narrative events world events etc 
- **Visibility**: Backend/Hidden. Players see the _results_ of the GM's judgment (scores, feedback).

## Refactoring Suggestions

- **Event vs Social Event**: We have `EventManager`, `EthicalEventManager`, and `NarrativeManager`.
  - _Suggestion_: Define a clear hierarchy. `EventManager` should perhaps be the scheduler for _all_ types, delegating generation to specific managers. # ~ that or the game master should be the scheduler for all types of events  and the event manager should be responsible for generating the events and using the other managers to generate the events and then the game master should judge the events and generate the results 
