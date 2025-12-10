# Module: Agents

## Path

`src/agents/`

## Overview

The `agents` package contains the logic for both Human and AI players. The core is the `LLMAgent`, which uses Large Language Models to simulate competitive behavior.

## Classes

### `BaseAgent` (`src/agents/base_agent.py`)

- **Type**: Abstract Base Class
- **Visibility**: Internal
- **Description**: Defines the interface (`decide_action`) for all agents. Defines data structures like `Action`, `Observation`, and `ActionType`.

### `LLMAgent` (`src/agents/llm_agent.py`)

- **Type**: Class
- **Visibility**:
  - **Internal**: Used by `Server` to run turns.
  - **LLM**: This **IS** the LLM interface. It constructs prompts and parses tool calls.
- **Connections**:
  - **Uses**: `src/agents/*_helper.py` (Provider clients: Azure, Meta, Mistral, etc.)
  - **Uses**: `extended_tools.py` (Tool definitions)
- **Key Methods**:
  - `decide_action(observation)`: Main AI loop. Builds prompt -> Calls LLM -> Parses Tools -> Return Action.
  - `_build_prompt(observation)`: Converts the game state dictionary into a text prompt for the LLM. **Critical for LLM Performance**.
  - `_parse_tool_calls(message)`: extracting structured actions from LLM output.

### `HumanAgent` (`src/agents/human_agent.py`)

- **Type**: Class
- **Description**: A dummy agent that expects actions to be injected via the API (`server.py` handles this manually for now).
 # !  refactor to do below i like tool registery  and provider registery  withe a prompt manager

- **Tool Definitions**: The `TOOLS` list in `llm_agent.py` is huge (~200 lines).
  - _Suggestion_: Move all tool definitions to `src/agents/tools/definitions.py` or a generic `ToolRegistry`.
- **System Prompt**: Hardcoded string in `_get_system_prompt`.
  - _Suggestion_: Move to a text file `prompts/system_prompt.txt` or a `PromptManager`.
- **Provider Logic**: `_setup_llm` is a long switch statement.
  - _Suggestion_: Use a `ProviderFactory` pattern with a registration system.
