# Agent Refactoring & Prompting Strategy

## Goal

Optimize `LLMAgent` for "Self-Shaping" autonomous development using an **Active Information Retrieval (AIR)** architecture and **Evolving Memory**.

## Analysis: Evolving Memory vs. Static Personas

- **Concept**: Instead of hardcoding behavior ("You are greedy"), we let the agent define itself over time.
- **Mechanism**: The agent writes a `memory_note` at the end of each turn, which becomes the "Past Self's Voice" in the next turn's prompt.

## Proposed Architecture: Active Information Retrieval (AIR) + Memory

### Prompt Structure

#### 1. System Prompt (Static)

- **Identity**: "You are an autonomous laundromat owner. You define your own strategy and goals."
- **Directive**: "Learn from your history. Shape your personality based on your success or failure."
- **Memory Usage**: "Always review your 'Past Self's Note' to maintain continuity."

#### 2. Turn Prompt (Dynamic)

- **Status Header**: Week #, Balance.
- **Memory Context**: **CRITICAL**.
  - _Input_: `Previous Thought: "{{last_turn_memory}}"`
  - _Effect_: Ensures the agent remembers _why_ it did something (e.g., "I raised prices to test demand").

## Execution Loop: The "Think-Act-Replect" Cycle

1.  **OBSERVE**: Agent gets Turn Prompt + **Past Memory**.
2.  **THINK**: "Last week I said X. Did it work? What is my new plan?"
3.  **ACT**: Tools (`buy`, `check_price`).
4.  **REACT**: evaluate tool outputs.
5.  **DECIDE (End Turn)**:
    - **CRITICAL CHANGE**: `end_turn(memory_note: str)`
    - Agent MUST write a note for its future self.

- _Success Metric_: The Week 5 memory should reference decisions made in Week 1-4 (e.g., "Still recovering from that bad ad campaign").
