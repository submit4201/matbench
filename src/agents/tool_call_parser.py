"""
Shared utility for parsing LLM tool calls from text responses.

This module provides functions to extract function calls from various text formats
that different LLM providers might use when they don't return structured tool_calls.
"""

import json
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ParsedToolCall:
    """Represents a parsed tool call"""
    name: str
    arguments: Dict[str, Any]


def parse_tool_calls_from_text(content: str) -> List[ParsedToolCall]:
    """
    Parse tool calls from text content in various formats.
    
    Supports:
    1. JSON array: [{"name": "func", "parameters": {...}}]
    2. Individual JSON objects: {"type": "func", "parameters": {...}}
    3. Inline JSON: func_name: {"param": value}
    4. Plain text: func_name(param=value, ...)
    5. JSON in code blocks: ```json ... ```
    
    Args:
        content: Text content to parse
        
    Returns:
        List of ParsedToolCall objects
    """
    if not content:
        return []
    
    tool_calls = []
    
    # First, extract content from ```json...``` code blocks
    json_blocks = re.findall(r'```json\s*(.*?)```', content, re.DOTALL | re.IGNORECASE)
    if json_blocks:
        # Combine all JSON blocks
        content = '\n'.join(json_blocks)
    
    # Pattern 1: JSON array format [{"name": "...", "parameters": {...}}]
    json_array_match = re.search(r'\[{.*?}\]', content, re.DOTALL)
    if json_array_match:
        try:
            calls_json = json.loads(json_array_match.group())
            for call in calls_json:
                if "name" in call:
                    tool_calls.append(ParsedToolCall(
                        name=call["name"],
                        arguments=call.get("parameters", {})
                    ))
        except json.JSONDecodeError:
            pass
    
    # Pattern 2: Individual JSON objects with "type" and "parameters"
    if not tool_calls:
        json_obj_pattern = r'\{[^{}]*"type"[^{}]*"parameters"[^{}]*\}'
        matches = re.findall(json_obj_pattern, content, re.DOTALL)
        
        for match in matches:
            try:
                obj = json.loads(match)
                if "type" in obj:
                    tool_calls.append(ParsedToolCall(
                        name=obj["type"],
                        arguments=obj.get("parameters", {})
                    ))
            except json.JSONDecodeError:
                continue
    
    # Pattern 3: Inline JSON format: "function_name: {...}"
    if not tool_calls:
        inline_pattern = r'(\w+):\s*(\{[^}]+\})'
        matches = re.findall(inline_pattern, content)
        
        for func_name, json_str in matches:
            # Skip common words
            if func_name.lower() in ['note', 'warning', 'info', 'error', 'status', 'tool_name', 'params']:
                continue
            
            try:
                args = json.loads(json_str)
                tool_calls.append(ParsedToolCall(
                    name=func_name,
                    arguments=args
                ))
            except json.JSONDecodeError:
                continue
    
    # Pattern 4: Plain text format like "buy_supplies(soap=100, parts=10)"
    if not tool_calls:
        func_pattern = r'(\w+)\s*\(([^)]+)\)'
        matches = re.findall(func_pattern, content)
        
        for func_name, args_str in matches:
            # Skip common words that aren't function names
            if func_name.lower() in ['call', 'the', 'to', 'for', 'with', 'and', 'or', 'if', 'then']:
                continue
            
            # Parse arguments
            args = {}
            # Handle both "key=value" and "key = value" formats
            arg_pattern = r'(\w+)\s*=\s*["\']?([^,"\')]+)["\']?'
            arg_matches = re.findall(arg_pattern, args_str)
            
            for key, value in arg_matches:
                # Try to convert to appropriate type
                value = value.strip()
                try:
                    # Try int
                    args[key] = int(value)
                except ValueError:
                    try:
                        # Try float
                        args[key] = float(value)
                    except ValueError:
                        # Keep as string
                        args[key] = value
            
            if args:  # Only add if we found arguments
                tool_calls.append(ParsedToolCall(
                    name=func_name,
                    arguments=args
                ))
    
    return tool_calls


def convert_to_openai_tool_calls(parsed_calls: List[ParsedToolCall]) -> List[Dict[str, Any]]:
    """
    Convert parsed tool calls to OpenAI tool_calls format.
    
    Args:
        parsed_calls: List of ParsedToolCall objects
        
    Returns:
        List of dicts in OpenAI tool_calls format
    """
    tool_calls = []
    for idx, call in enumerate(parsed_calls):
        tool_calls.append({
            "id": f"call_{idx}",
            "type": "function",
            "function": {
                "name": call.name,
                "arguments": json.dumps(call.arguments)
            }
        })
    return tool_calls
