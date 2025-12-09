# Module: Enhanced Engine

## Path

`src/engine/enhanced_engine.py`

## Overview

`EnhancedGameEngine` is a subclass of `GameEngine` that composes the newer, modular systems (`FinancialSystem`, `TimeSystem`, `SocialSystem` updates) on top of the base legacy engine.

## Purpose

- **Bridge**: Allows gradual migration from the monolithic `GameEngine` to modular components.
- **Features**:
  - Initializes `BankSystem` (Finance).
  - Initializes `CalendarManager`.
  - Initializes `CreditSystem`.
  - Overrides `process_turn` to include `Credit` and `Calendar` updates.

## Roadmap

- Eventually, `EnhancedGameEngine` should just become `GameEngine` once all legacy code is removed.
