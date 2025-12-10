# System: Ethical Events

## Path

`src/engine/social/ethical_events.py`

## Overview

The `EthicalEventManager` injects moral complexity into the business simulation. It triggers "Dilemmas" where players must choose between profit, reputation, and ethics.

## Core Concepts

### `Dilemma`

- A specific scenario (e.g., "Supplier uses child labor").
- **Choices**: usually 2-3 options (e.g., "Ignore it (Save $)", "Switch Supplier (Cost $$, Rep ++)", "Report it").

### `EthicalEventManager`

- **Logic**: Checks per-turn triggers.
- **State**: Tracks `ethics_score` (hidden metric) and history of choices.
- **Integration**:
  - Sends `Message` with intent `DILEMMA` to the player.
  - Resolves choices via `resolve_dilemma`.

## Usage

- **GameEngine**: Calls `check_for_dilemmas` weekly.
- **Frontend**: Renders dilemmas as urgent modals or notifications.

# used by event manager to generate dilemmas and the eventmanager is used by the game master to generate events and gets judged by the judge once implemented