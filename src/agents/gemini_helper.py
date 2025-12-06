"""
Google Gemini Client

A wrapper for Google Gemini API that provides an OpenAI-like interface
for easy integration with existing LLM agent flows.

Uses the official google-genai package (newer SDK).
"""

import os
import json
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field

try:
    from google import genai
    from google.genai import types
except ImportError:
    raise ImportError("Please install google-genai: pip install google-genai")

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars set elsewhere


@dataclass
class ToolCall:
    """Represents a tool call from Gemini's response"""
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


class GeminiClient:
    """
    Google Gemini API client with OpenAI-compatible interface.
    
    Usage:
        client = GeminiClient(
            api_key="your-gemini-key",
            model="gemini-flash-lite-latest"
        )
        
        response = client.chat.completions.create(
            model="gemini-flash-lite-latest",
            messages=[{"role": "user", "content": "Hello!"}],
            tools=[...],  # OpenAI-format tools
            temperature=0.7,
            max_tokens=1000
        )
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gemini-flash-lite-latest"  # Updated to correct model name
    ):
        self.api_key = api_key
        self.model = model
        
        # Initialize the Gemini client
        self.client = genai.Client(api_key=api_key)
        
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
        """Internal method to create completion via Gemini API"""
        
        # Extract system instruction and convert messages
        system_instruction = None
        gemini_contents = []
        
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            elif msg["role"] == "user":
                gemini_contents.append(types.Content(
                    role="user",
                    parts=[types.Part(text=msg["content"])]
                ))
            elif msg["role"] == "assistant":
                gemini_contents.append(types.Content(
                    role="model",
                    parts=[types.Part(text=msg["content"])]
                ))
        
        # Build generation config
        config = types.GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens,
            system_instruction=system_instruction if system_instruction else None,
        )
        
        # Convert tools if provided
        if tools:
            gemini_tools = self._convert_tools_to_gemini(tools)
            config.tools = gemini_tools
        
        # Generate response
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=gemini_contents,
                config=config
            )
        except Exception as e:
            raise Exception(f"Gemini API request failed: {str(e)}")
        
        # Convert to OpenAI format
        return self._convert_response_to_openai(response, model)
    
    def _convert_tools_to_gemini(self, openai_tools: List[Dict[str, Any]]) -> List[types.Tool]:
        """Convert OpenAI-format tools to Gemini format"""
        gemini_declarations = []
        
        for tool in openai_tools:
            if tool.get("type") == "function":
                func = tool["function"]
                
                # Convert to Gemini FunctionDeclaration
                declaration = types.FunctionDeclaration(
                    name=func["name"],
                    description=func.get("description", ""),
                    parameters=func.get("parameters", {"type": "object", "properties": {}})
                )
                gemini_declarations.append(declaration)
        
        return [types.Tool(function_declarations=gemini_declarations)] if gemini_declarations else []
    
    def _convert_response_to_openai(self, gemini_response, model: str) -> ChatCompletion:
        """Convert Gemini response to OpenAI ChatCompletion format"""
        
        # Extract text content and function calls
        text_content = None
        tool_calls = []
        
        try:
            # Check for function calls in candidates first
            if hasattr(gemini_response, 'candidates') and gemini_response.candidates:
                candidate = gemini_response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    text_parts = []
                    for idx, part in enumerate(candidate.content.parts):
                        # Extract text from text parts
                        if hasattr(part, 'text') and part.text:
                            text_parts.append(part.text)
                        
                        # Extract function calls
                        if hasattr(part, 'function_call') and part.function_call:
                            func_call = part.function_call
                            tool_call = ToolCall(
                                id=f"call_{idx}",
                                type="function",
                                function=FunctionCall(
                                    name=func_call.name,
                                    arguments=json.dumps(dict(func_call.args))
                                )
                            )
                            tool_calls.append(tool_call)
                    
                    # Combine text parts
                    if text_parts:
                        text_content = "\n".join(text_parts)
            
            # Fallback: try to get text directly (for non-function-call responses)
            if not text_content and not tool_calls:
                if hasattr(gemini_response, 'text') and gemini_response.text:
                    text_content = gemini_response.text
                    
        except Exception as e:
            # If we can't extract content, use empty string
            print(f"[Gemini] Warning extracting response: {e}")
            text_content = text_content or ""
        
        # Build message
        message = Message(
            role="assistant",
            content=text_content,
            tool_calls=tool_calls if tool_calls else None
        )
        
        # If no structured tool calls found, try parsing from text
        if not tool_calls and text_content:
            from .tool_call_parser import parse_tool_calls_from_text, convert_to_openai_tool_calls
            parsed_calls = parse_tool_calls_from_text(text_content)
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
                message.tool_calls = tool_calls if tool_calls else None
        
        # Determine finish reason
        finish_reason = "stop"
        if tool_calls:
            finish_reason = "tool_calls"
        
        # Build choice
        choice = Choice(
            index=0,
            message=message,
            finish_reason=finish_reason
        )
        
        # Build usage info
        usage = Usage(
            prompt_tokens=0,
            completion_tokens=0,
            total_tokens=0
        )
        
        if hasattr(gemini_response, 'usage_metadata'):
            usage = Usage(
                prompt_tokens=getattr(gemini_response.usage_metadata, 'prompt_token_count', 0),
                completion_tokens=getattr(gemini_response.usage_metadata, 'candidates_token_count', 0),
                total_tokens=getattr(gemini_response.usage_metadata, 'total_token_count', 0)
            )
        
        return ChatCompletion(
            id="chatcmpl-gemini",
            model=model,
            choices=[choice],
            usage=usage
        )


# Factory function for easy instantiation
def get_gemini_client(
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> GeminiClient:
    """
    Create a Gemini client from environment variables or provided values.
    
    Uses:
        GEMINI_api_key - API key for Google Gemini
    
    Returns:
        GeminiClient instance
    """
    key = api_key or os.environ.get("GEMINI_api_key")
    model_name = model or "gemini-flash-lite-latest"  # Correct model name
    
    if not key:
        raise ValueError("No API key provided. Set GEMINI_api_key env var, or pass api_key.")
    
    return GeminiClient(api_key=key, model=model_name)


# Convenience alias
GoogleGemini = GeminiClient


if __name__ == "__main__":
    # Quick test
    client = get_gemini_client()
    
    response = client.chat.completions.create(
        model=client.model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are 3 things to visit in Seattle?"}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    print("Response:", response.choices[0].message.content)
