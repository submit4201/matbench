"""
Azure OpenAI Client

A wrapper for Azure-hosted OpenAI models (GPT-4, GPT-5, etc.) that provides 
a consistent interface matching other helper packages.

Supports function calling via OpenAI-compatible endpoints.
"""

import os
from typing import Optional
from openai import AzureOpenAI
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars set elsewhere


class AzureOpenAIClient:
    """
    Azure-hosted OpenAI API client with OpenAI-compatible interface.
    
    Usage:
        client = AzureOpenAIClient(
            api_key="your-key",
            azure_endpoint="https://your-endpoint.cognitiveservices.azure.com/",
            deployment_name="gpt-5-nano"
        )
        
        response = client.chat.completions.create(
            model="gpt-5-nano",
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
        deployment_name: str,
        api_version: str = "2024-12-01-preview",
        timeout: float = 120.0
    ):
        self.api_key = api_key
        self.azure_endpoint = azure_endpoint.rstrip('/')
        self.deployment_name = deployment_name
        self.api_version = api_version
        self.timeout = timeout
        
        # Create Azure OpenAI client
        self.client = AzureOpenAI(
            api_key=api_key,
            azure_endpoint=azure_endpoint,
            api_version=api_version,
            timeout=timeout
        )
        
        # Expose chat.completions interface
        self.chat = self.client.chat


# Factory function for easy instantiation
def get_azure_client(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    deployment: Optional[str] = None,
    api_version: Optional[str] = None
) -> AzureOpenAIClient:
    """
    Create an Azure OpenAI client from environment variables or provided values.
    
    Uses:
        AZURE_api_key - API key for Azure OpenAI
        AZURE_base_url - Azure OpenAI endpoint URL
        AZURE_deployment_name - Model deployment name
    
    Returns:
        AzureOpenAIClient instance
    """
    key = api_key or os.environ.get("AZURE_api_key") or os.environ.get("MICROSOFTENDPONT")
    url = endpoint or os.environ.get("AZURE_base_url")
    deploy = deployment or os.environ.get("AZURE_deployment_name") or os.environ.get("AZURE_model_name")
    version = api_version or os.environ.get("OPENAI_API_VERSION", "2024-12-01-preview")
    
    if not key:
        raise ValueError("No API key provided. Set AZURE_api_key env var, or pass api_key.")
    if not url:
        raise ValueError("No endpoint provided. Set AZURE_base_url env var, or pass endpoint.")
    if not deploy:
        raise ValueError("No deployment name provided. Set AZURE_deployment_name env var, or pass deployment.")
    
    return AzureOpenAIClient(
        api_key=key,
        azure_endpoint=url,
        deployment_name=deploy,
        api_version=version
    )


# Conveni   ence alias
AzureGPT = AzureOpenAIClient


if __name__ == "__main__":
    # Quick test
    client = get_azure_client()
    
    response = client.chat.completions.create(
        model="gpt-5-nano",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are 3 things to visit in Seattle?"}
        ],

    )
    
    print("Response:", response.choices[0].message.content)
