# Module: Benchmark

## Path

`src/benchmark/`

## Overview

The `benchmark` package is used to run automated evaluations of the AI agents. It does not run the interactive web server; instead, it runs a headless simulation to gather data on agent performance.

## Components

### `Runner` (`runner.py`)

- **Description**: Headless game loop. Runs N weeks of simulation without waiting for HTTP requests.
- **Output**: Generates JSON logs of balance, social score, and decisions.

### `Scenarios` (`scenarios.py`)

- **Description**: Defines starting conditions (e.g., "Rescession", "Boom", "Crowded Market") to test agents under different pressures.

## Usage

- Run via terminal: `python src/tests/run_benchmark.py`
