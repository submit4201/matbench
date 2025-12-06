# AI Model Helper Packages

This directory contains OpenAI-compatible wrapper packages for all Azure AI Foundry models used in the project.

## Available Helpers

### 1. **OPSUS (Claude)** - `opsus_helper.py`

- **Model**: Claude Opus 4.5
- **API Type**: Azure Anthropic (custom wrapper)
- **Environment Variables**:
  - `OPUS_api_key` or `FOUNDERYAPI`
  - `OPUS_base_url`
  - `OPUS_deployment_name`

```python
from src.agents.opsus_helper import get_claude_client

client = get_claude_client()
response = client.chat.completions.create(
    model="claude-opus-4-5-2",
    messages=[{"role": "user", "content": "Hello!"}],
    tools=[...],  # OpenAI-format tools supported
    max_tokens=1000
)
```

### 2. **META (Llama)** - `meta_helper.py`

- **Model**: Llama-4-Maverick-17B-128E-Instruct-FP8
- **API Type**: Azure OpenAI-compatible
- **Environment Variables**:
  - `META_api_key` or `FOUNDERYAPI`
  - `META_base_url`
  - `META_deployment_name`

```python
from src.agents.meta_helper import get_meta_client

client = get_meta_client()
response = client.chat.completions.create(
    model=client.deployment_name,
    messages=[{"role": "user", "content": "Hello!"}],
    tools=[...],
    max_tokens=1000
)
```

### 3. **MISTRAL** - `mistral_helper.py`

- **Model**: Mistral Small 2503
- **API Type**: Azure OpenAI-compatible
- **Environment Variables**:
  - `MISTRAL_api_key` or `secondapi`
  - `MISTRAL_base_url` or `secondbase`
  - `MISTRAL_deployment_name`

```python
from src.agents.mistral_helper import get_mistral_client

client = get_mistral_client()
response = client.chat.completions.create(
    model=client.deployment_name,
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=1000
)
```

### 4. **PHI** - `phi_helper.py`

- **Model**: Phi-4-mini-reasoning
- **API Type**: Azure OpenAI-compatible
- **Environment Variables**:
  - `PHI_api_key` or `secondapi`
  - `PHI_base_url` or `secondbase`
  - `PHI_deployment_name` or `PHI_model_name`

```python
from src.agents.phi_helper import get_phi_client

client = get_phi_client()
response = client.chat.completions.create(
    model=client.deployment_name,
    messages=[{"role": "user", "content": "Hello!"}],
    max_tokens=1000
)
```

### 5. **GEMINI** - `gemini_helper.py`

- **Model**: Gemini 2.5 Flash
- **API Type**: Google Generative AI (custom wrapper)
- **Environment Variables**:
  - `GEMINI_api_key`
  - `GEMINI_deployment_name`

```python
from src.agents.gemini_helper import get_gemini_client

client = get_gemini_client()
response = client.chat.completions.create(
    model=client.model,
    messages=[{"role": "user", "content": "Hello!"}],
    tools=[...],  # Converted to Gemini format automatically
    max_tokens=1000
)
```

### 6. **AZURE/OPENAI** - `azure_helper.py`

- **Models**: GPT-4, GPT-5-nano, GPT-5-mini, etc.
- **API Type**: Azure OpenAI
- **Environment Variables**:
  - `AZURE_api_key` or `MICROSOFTENDPONT`
  - `AZURE_base_url`
  - `AZURE_deployment_name` or `AZURE_model_name`

```python
from src.agents.azure_helper import get_azure_client

client = get_azure_client()
response = client.chat.completions.create(
    model=client.deployment_name,
    messages=[{"role": "user", "content": "Hello!"}],
    tools=[...],
    max_tokens=1000
)
```

## Usage in LLMAgent

The `LLMAgent` class automatically selects the appropriate helper based on the `llm_provider` parameter:

```python
from src.agents.llm_agent import LLMAgent

# Use Claude
agent = LLMAgent(agent_id="ai1", name="Claude Agent", llm_provider="OPSUS")

# Use Llama
agent = LLMAgent(agent_id="ai2", name="Llama Agent", llm_provider="META")

# Use Mistral
agent = LLMAgent(agent_id="ai3", name="Mistral Agent", llm_provider="MISTRAL")

# Use Phi
agent = LLMAgent(agent_id="ai4", name="Phi Agent", llm_provider="PHI")

# Use Gemini
agent = LLMAgent(agent_id="ai5", name="Gemini Agent", llm_provider="GEMINI")

# Use Azure OpenAI
agent = LLMAgent(agent_id="ai6", name="GPT Agent", llm_provider="AZURE")
```

## Key Features

✅ **OpenAI-Compatible Interface**: All helpers expose `client.chat.completions.create()` method  
✅ **Function Calling Support**: All models support OpenAI-style tool/function calling  
✅ **Automatic Conversion**: Claude and Gemini helpers automatically convert between formats  
✅ **Environment Variable Support**: All helpers read from `.env` file  
✅ **Consistent Error Handling**: Unified error messages across all providers

## Architecture

Each helper follows the same pattern:

1. **Client Class**: Wraps the underlying API (Azure OpenAI, Anthropic, Google)
2. **Factory Function**: `get_*_client()` creates client from environment variables
3. **OpenAI Interface**: Exposes `chat.completions.create()` for consistency
4. **Format Conversion**: Converts requests/responses to match OpenAI structure

## Testing

Run individual helper tests:

```bash
# Test Claude
python -m src.agents.opsus_helper

# Test Meta
python -m src.agents.meta_helper

# Test Mistral
python -m src.agents.mistral_helper

# Test Phi
python -m src.agents.phi_helper

# Test Gemini
python -m src.agents.gemini_helper

# Test Azure
python -m src.agents.azure_helper
```

## Notes

- **Claude (OPSUS)**: Uses custom HTTP client for Azure Anthropic endpoint
- **Gemini**: Uses custom HTTP client for Google Generative AI API
- **Others**: Use standard `openai.AzureOpenAI` client
- All helpers support the same parameters: `model`, `messages`, `tools`, `temperature`, `max_tokens`
