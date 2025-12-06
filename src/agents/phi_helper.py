"""
Azure PHI Client using Azure AI Inference SDK

Provides an OpenAI-compatible interface for PHI models using the correct
Azure AI Inference SDK instead of the OpenAI SDK.
"""

import os
import json
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

try:
    from azure.ai.inference import ChatCompletionsClient
    from azure.ai.inference.models import (
        SystemMessage,
        UserMessage,
        AssistantMessage,
        ChatCompletionsToolDefinition,
        FunctionDefinition,
        UserMessage as ChatRequestUserMessage,
        SystemMessage as ChatRequestSystemMessage
    )
    from azure.core.credentials import AzureKeyCredential
except ImportError:
    raise ImportError("Please install: pip install azure-ai-inference")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


# OpenAI-compatible response structures
@dataclass
class FunctionCall:
    name: str
    arguments: str


@dataclass
class ToolCall:
    id: str
    type: str
    function: FunctionCall


@dataclass
class Message:
    role: str
    content: Optional[str]
    tool_calls: Optional[List[ToolCall]] = None


@dataclass
class Choice:
    message: Message
    index: int = 0
    finish_reason: str = "stop"


@dataclass
class ChatCompletion:
    choices: List[Choice]
    model: str


class ChatCompletionsWrapper:
    """Wrapper to provide OpenAI-compatible chat.completions interface"""
    
    def __init__(self, client: ChatCompletionsClient, deployment_name: str):
        self.client = client
        self.deployment_name = "Phi-4-multimodal-instruct"
        self.api_version = "2024-12-01-preview"
    
    def create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        temperature: Optional[float] = None,
        max_completion_tokens: Optional[int] = None,
        **kwargs
    ) -> ChatCompletion:
        """OpenAI-compatible create method"""
        
        # Convert OpenAI messages to Azure AI Inference format
        azure_messages = []
        
        # For PHI models, embed tools in system prompt using special format
        system_content = ""
        for msg in messages:
            if msg.get("role") == "system":
                system_content = msg.get("content", "")
                break
        
        # Add tools to system prompt if provided
        if tools:
            # Convert OpenAI tools to PHI JSON format
            phi_tools = []
            for tool in tools:
                if tool.get("type") == "function":
                    func = tool["function"]
                    phi_tools.append({
                        "name": func["name"],
                        "description": func.get("description", ""),
                        "parameters": func.get("parameters", {})
                    })
            
            # Embed tools in system prompt with special tokens and explicit instructions
            tools_json = json.dumps(phi_tools)
            format_instructions = """

When you want to call a function, you MUST respond with a JSON array in this EXACT format:
[{"name": "function_name", "parameters": {"param1": value1, "param2": value2}}]

Example:
[{"name": "buy_supplies", "parameters": {"soap": 100, "parts": 10}}]

You can call multiple functions by including multiple objects in the array:
[{"name": "buy_supplies", "parameters": {"soap": 100}}, {"name": "set_price", "parameters": {"price": 4.5}}]

IMPORTANT: Use this exact JSON array format. Do not use any other format."""
            
            system_content = f"{system_content}<|tool|>{tools_json}<|/tool|>{format_instructions}"
        
        # Build messages with modified system prompt
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            
            if role == "system":
                # Use modified system content with tools
                azure_messages.append(SystemMessage(content=system_content))
            elif role == "user":
                azure_messages.append(UserMessage(content=content))
            elif role == "assistant":
                azure_messages.append(AssistantMessage(content=content))
        
        # Call Azure AI Inference API without tools parameter
        # (tools are already in system prompt)
        response = self.client.complete(
            messages=azure_messages,
            temperature=temperature,
            max_tokens=max_completion_tokens,
            model=self.deployment_name
        )
        
        # Convert response to OpenAI format
        return self._convert_response(response)
    
    def _convert_response(self, azure_response) -> ChatCompletion:
        """Convert Azure AI Inference response to OpenAI format"""
        
        choice = azure_response.choices[0]
        message = choice.message
        
        # PHI models return tool calls in the text response, not as structured tool_calls
        # Use shared parser to extract them
        tool_calls = None
        content = message.content
        
        if content:
            from .tool_call_parser import parse_tool_calls_from_text, convert_to_openai_tool_calls
            parsed_calls = parse_tool_calls_from_text(content)
            if parsed_calls:
                openai_calls = convert_to_openai_tool_calls(parsed_calls)
                # Convert to ToolCall objects
                tool_calls = []
                for call in openai_calls:
                    tool_calls.append(
                        ToolCall(
                            id=call["id"],
                            type=call["type"],
                            function=FunctionCall(
                                name=call["function"]["name"],
                                arguments=call["function"]["arguments"]
                            )
                        )
                    )
        
        openai_message = Message(
            role=message.role,
            content=content,
            tool_calls=tool_calls if tool_calls else None
        )
        
        openai_choice = Choice(
            message=openai_message,
            index=0,
            finish_reason=choice.finish_reason if hasattr(choice, 'finish_reason') else "stop"
        )
        
        return ChatCompletion(
            choices=[openai_choice],
            model=self.deployment_name
        )


class AzurePhiClient:
    """
    Azure PHI client using Azure AI Inference SDK with OpenAI-compatible interface.
    
    Usage:
        client = AzurePhiClient(
            api_key="your-key",
            endpoint="https://your-endpoint.services.ai.azure.com",
            deployment_name="Phi-4"
        )
        
        response = client.chat.completions.create(
            model="Phi-4",
            messages=[{"role": "user", "content": "Hello!"}],
            tools=[...],
            temperature=0.7
        )
    """
    
    def __init__(
        self,
        api_key: str,
        endpoint: str,
        deployment_name: str
    ):
        self.api_key = api_key
        self.endpoint = endpoint.rstrip('/')
        self.deployment_name = deployment_name
        
        # Create Azure AI Inference client
        self.client = ChatCompletionsClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(api_key),
            api_version="2024-05-01-preview"  # Correct API version for PHI models
        )
        
        # Expose OpenAI-compatible interface
        self.chat = type('Chat', (), {
            'completions': ChatCompletionsWrapper(self.client, deployment_name)
        })()


def get_phi_client(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    deployment: Optional[str] = None
) -> AzurePhiClient:
    """
    Create an Azure PHI client from environment variables or provided values.
    
    Uses:
        PHI_api_key - API key for Azure PHI
        PHI_base_url - Azure PHI endpoint URL
        PHI_deployment_name - Model deployment name
    
    Note: Azure AI Inference SDK does not use API versions
    
    Returns:
        AzurePhiClient instance
    """
    key = api_key or os.environ.get("PHI_api_key")
    url = endpoint or "https://sigal.services.ai.azure.com/models"
    deploy = deployment or "Phi-4-multimodal-instruct"  # Model that supports tool calling
    
    if not key:
        raise ValueError("No API key provided. Set PHI_api_key env var, or pass api_key.")
    if not url:
        raise ValueError("No endpoint provided. Set PHI_base_url env var, or pass endpoint.")
    if not deploy:
        raise ValueError("No deployment name provided. Set PHI_deployment_name env var, or pass deployment.")
    
    client = AzurePhiClient(
        api_key=key,
        endpoint=url,
        deployment_name=deploy
    )
    return client


# Convenience alias
AzurePhi = AzurePhiClient


if __name__ == "__main__":
    # Quick test
    client = get_phi_client()
    
    response = client.chat.completions.create(
        model=client.deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are 3 things to visit in Seattle?"}
        ],
        max_completion_tokens=500,
        temperature=0.7
    )
    
    print("Response:", response.choices[0].message.content)
