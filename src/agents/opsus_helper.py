"""
Azure Claude (Anthropic) Client

A wrapper for Azure-hosted Claude API that provides an OpenAI-like interface
for easy integration with existing LLM agent flows.

Converts OpenAI-style function calling to Claude's native tool format.
"""

import os
import json
import httpx
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars set elsewhere


@dataclass
class ToolCall:
    """Represents a tool call from Claude's response"""
    id: str
    type: str = "function"
    function: 'FunctionCall' = None


@dataclass
class FunctionCall:
    """Represents the function details in a tool call"""
    name: str
    arguments: str  # JSON string


@dataclass
class Message:
    """Represents a message in the response"""
    role: str
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None


@dataclass
class Choice:
    """Represents a choice in the completion response"""
    index: int
    message: Message
    finish_reason: str


@dataclass
class Usage:
    """Token usage information"""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


@dataclass
class ChatCompletion:
    """OpenAI-compatible completion response"""
    id: str
    object: str = "chat.completion"
    created: int = 0
    model: str = ""
    choices: List[Choice] = field(default_factory=list)
    usage: Optional[Usage] = None


class AzureClaudeClient:
    """
    Azure-hosted Claude API client with OpenAI-compatible interface.
    
    Usage:
        client = AzureClaudeClient(
            api_key="your-key",
            azure_endpoint="https://your-endpoint.azure.com/anthropic/v1/messages"
        )
        
        response = client.chat.completions.create(
            model="claude-opus-4-5",
            messages=[{"role": "user", "content": "Hello!"}],
            tools=[...],  # OpenAI-format tools
            temperature=0.7,
            max_tokens=1000
        )
    """
    
    def __init__(
        self,
        api_key: str,
        azure_endpoint: str,
        anthropic_version: str = "2023-06-01",
        timeout: float = 120.0
    ):
        self.api_key = api_key
        self.azure_endpoint = azure_endpoint.rstrip('/')
        self.anthropic_version = anthropic_version
        self.timeout = timeout
        
        # Nested chat.completions interface for OpenAI compatibility
        self.chat = self._ChatNamespace(self)
    
    class _ChatNamespace:
        def __init__(self, client):
            self.completions = client._CompletionsNamespace(client)
    
    class _CompletionsNamespace:
        def __init__(self, client):
            self.client = client
        
        def create(
            self,
            model: str,
            messages: List[Dict[str, Any]],
            tools: Optional[List[Dict[str, Any]]] = None,
            tool_choice: Optional[Union[str, Dict]] = None,
            temperature: float = 0.7,
            max_tokens: int = 1000,
            max_completion_tokens: Optional[int] = None,
            **kwargs
        ) -> ChatCompletion:
            """Create a chat completion (OpenAI-compatible interface)"""
            return self.client._create_completion(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice=tool_choice,
                temperature=temperature,
                max_tokens=max_completion_tokens or max_tokens,
                **kwargs
            )
    
    def _create_completion(
        self,
        model: str,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> ChatCompletion:
        """Internal method to create completion via Claude API"""
        
        # Extract system message if present
        system_content = None
        user_messages = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_content = msg["content"]
            else:
                user_messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Build request payload
        payload = {
            "model": model,
            "messages": user_messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }
        
        if system_content:
            payload["system"] = system_content
        
        # Convert OpenAI-format tools to Claude format
        if tools:
            claude_tools = self._convert_tools_to_claude(tools)
            payload["tools"] = claude_tools
            
            # Handle tool_choice
            if tool_choice:
                if tool_choice == "auto":
                    payload["tool_choice"] = {"type": "auto"}
                elif tool_choice == "required":
                    payload["tool_choice"] = {"type": "any"}
                elif tool_choice == "none":
                    # Don't include tool_choice for "none"
                    pass
                elif isinstance(tool_choice, dict) and "function" in tool_choice:
                    payload["tool_choice"] = {
                        "type": "tool",
                        "name": tool_choice["function"]["name"]
                    }
        
        # Make request
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": self.anthropic_version
        }
        
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    self.azure_endpoint,
                    headers=headers,
                    json=payload
                )
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as e:
            error_body = e.response.text if hasattr(e.response, 'text') else str(e)
            raise Exception(f"Claude API error: {e.response.status_code} - {error_body}")
        except Exception as e:
            raise Exception(f"Claude API request failed: {str(e)}")
        
        # Convert Claude response to OpenAI format
        return self._convert_response_to_openai(data, model)
    
    def _convert_tools_to_claude(self, openai_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert OpenAI-format tools to Claude format"""
        claude_tools = []
        
        for tool in openai_tools:
            if tool.get("type") == "function":
                func = tool["function"]
                claude_tool = {
                    "name": func["name"],
                    "description": func.get("description", ""),
                    "input_schema": func.get("parameters", {"type": "object", "properties": {}})
                }
                claude_tools.append(claude_tool)
        
        return claude_tools
    
    def _convert_response_to_openai(self, claude_response: Dict[str, Any], model: str) -> ChatCompletion:
        """Convert Claude response to OpenAI ChatCompletion format"""
        
        # Extract content and tool calls from Claude response
        content_parts = claude_response.get("content", [])
        
        text_content = None
        tool_calls = []
        
        for idx, block in enumerate(content_parts):
            if block.get("type") == "text":
                text_content = block.get("text", "")
            elif block.get("type") == "tool_use":
                tool_call = ToolCall(
                    id=block.get("id", f"call_{idx}"),
                    type="function",
                    function=FunctionCall(
                        name=block.get("name", ""),
                        arguments=json.dumps(block.get("input", {}))
                    )
                )
                tool_calls.append(tool_call)
        
        # Build message
        message = Message(
            role="assistant",
            content=text_content,
            tool_calls=tool_calls if tool_calls else None
        )
        
        # Determine finish reason
        stop_reason = claude_response.get("stop_reason", "stop")
        if stop_reason == "tool_use":
            finish_reason = "tool_calls"
        elif stop_reason == "end_turn":
            finish_reason = "stop"
        else:
            finish_reason = stop_reason
        
        # Build choice
        choice = Choice(
            index=0,
            message=message,
            finish_reason=finish_reason
        )
        
        # Build usage info
        usage_data = claude_response.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("input_tokens", 0),
            completion_tokens=usage_data.get("output_tokens", 0),
            total_tokens=usage_data.get("input_tokens", 0) + usage_data.get("output_tokens", 0)
        )
        
        return ChatCompletion(
            id=claude_response.get("id", "chatcmpl-claude"),
            model=model,
            choices=[choice],
            usage=usage
        )


# Factory function for easy instantiation
def get_claude_client(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None
) -> AzureClaudeClient:
    """
    Create an Azure Claude client from environment variables or provided values.
    
    Uses:
        LLMAPIKEYCUSTOMER - API key for Azure Anthropic
        LLMAPIKEYCUSTOMERURL - Azure Anthropic endpoint URL
    
    Returns:
        AzureClaudeClient instance
    """
    key = api_key or os.environ.get("LLMAPIKEYCUSTOMER") or os.environ.get("FOUNDERYAPI")
    url = endpoint or os.environ.get("OPUS_base_url")
    
    if not key:
        raise ValueError("No API key provided. Set LLMAPIKEYCUSTOMER or FOUNDERYAPI env var, or pass api_key.")
    if not url:
        raise ValueError("No endpoint provided. Set OPUS_base_url env var, or pass endpoint.")
    
    return AzureClaudeClient(api_key=key, azure_endpoint=url)


# Convenience alias matching OpenAI pattern
AzureClaude = AzureClaudeClient


if __name__ == "__main__":
    # Quick test
    client = get_claude_client()
    
    response = client.chat.completions.create(
        model="claude-opus-4-5",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are 3 things to visit in Seattle?"}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    print("Response:", response.choices[0].message.content)
