# Module: Rule-Based Agents

## Path

`src/agents/rule_based/`

## Overview

These agents do **not** use LLMs. They use hardcoded logic (heuristics) to make decisions. They serve as:

1.  **Baseline Competitors**: predictably behaving opponents for benchmarking.
2.  **Fallback**: What an `LLMAgent` falls back to if the API fails.
3.  **Tutorial Opponents**: Easier to beat/predict.

## Agents

### `ConservativeAgent` (`conservative_agent.py`)

- **Strategy**: Low risk. Maintains high cash buffer. Rarely upgrades. Prices mid-range.

### `AggressivePricer` (`aggressive_pricer.py`)

- **Strategy**: Undercuts the market. High volume, low margin.

### `QualityFocused` (`quality_focused.py`)

- **Strategy**: Maintains high prices but keeps machines in perfect condition. Buys premium supplies.

### `BalancedAgent` (`balanced_agent.py`)

- **Strategy**: Mixed approach.

## Usage

- Can be selected during game setup for P2/P3 slots.

## Refactoring Suggestions

- **Shared Heuristics**: Much code is duplicated (e.g., "if balance > X then buy Y").
  - _Suggestion_: Create a `HeuristicLibrary` or `Strategy` objects that can be composed.
