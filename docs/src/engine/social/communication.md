# System: Communication

## Path

`src/engine/social/communication.py`

## Overview

The `CommunicationSystem` is a comprehensive messaging backbone for the simulation. It replaces simple "chat logs" with a structured system supporting various channel types, intents, and visibility rules.

## Key Classes

### `CommunicationSystem`

- **Responsibilities**:
  - Stores all `Message` objects.
  - Manages `Group`s (chat rooms/alliances).
  - Routes messages to agent "inboxes".
  - Tracks "Statements" for consistency checking (e.g., did an agent lie?).
- **Methods**:
  - `send_dm(sender, recipient, content, ...)`
  - `send_group_message(sender, group_id, ...)`
  - `send_public(...)`
  - `send_formal(...)`: For contracts/proposals.
  - `check_consistency(agent_id)`: **Analysis**. Compares public vs private statements.

### `Message` (Dataclass)

- Fields: `id`, `sender_id`, `channel`, `content`, `intent` (`THREAT`, `PROPOSAL`, `CHAT`), `sentiment_score` (populated by GM).

## Integration

- **Frontend**: Polls `get_inbox` or `to_dict` to display chat UI.
- **LLM Agent**: Receives messages in `Observation`. Must parse `intent` to understand context.
- **Game Master**: Uses `check_consistency` to penalize deception or reward transparency. # the judge should also be callled in this scents maybe we split the game master into a judge and a game master
