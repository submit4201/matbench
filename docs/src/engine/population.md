# Module: Population

## Path

`src/engine/population/`

## Overview

The `population` package simulates the customers that visit the laundromats.

## Components

### `Customer` (`customer.py`)

- **Type**: Agent / Entity
- **Description**: Individual customer with preferences (price sensitivity, quality preference, patience) and state (needs wash, current satisfaction).
- **Behavior**:
  - `decide_laundromat()`: Choose where to go based on public state.
  - `generate_thought()`: Produces flavor text for the UI ("This place is too expensive!").

## Usage

- **GameEngine**: Instantiates a pool of customers (e.g., 50-100) and iterates them during `process_turn`.

## Refactoring Suggestions

- **Performance**: Simulating 1000s of individual customers might be slow in Python.
  - _Suggestion_: For larger scales, switch to a "Cohort" model (simulating groups of similar customers) rather than individuals. # [ ] TODO: implement cohort model at the same time we maybe want to move this to the game master population system that can handle this making cohorts and individual customers when needed keeping notes for memory to keep track of the customers and their preferences and state. along with storylines for the customers and their interactions with the laundromats. so we can have a more dynamic and interesting game experience. 
