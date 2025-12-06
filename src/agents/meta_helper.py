"""
Azure Meta (Llama) Client

A wrapper for Azure-hosted Meta Llama models that provides an OpenAI-like interface
for easy integration with existing LLM agent flows.

Supports function calling via OpenAI-compatible endpoints.
"""

import os
from typing import Optional
from openai import OpenAI
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars set elsewhere


class AzureMetaClient:
    """
    Azure-hosted Meta Llama API client with OpenAI-compatible interface.
    
    Usage:
        client = AzureMetaClient(
            api_key="your-key",
            azure_endpoint="https://your-endpoint.services.ai.azure.com/openai/v1/",
            deployment_name="Llama-4-Maverick-17B-128E-Instruct-FP8"
        )
        
        response = client.chat.completions.create(
            model="Llama-4-Maverick-17B-128E-Instruct-FP8",
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
        # api_version: str = "2024-12-01-preview",
        # timeout: float = 120.0
    ):
        self.api_key = api_key
        self.base_url = azure_endpoint.rstrip('/')
        self.deployment_name = deployment_name
        # self.api_version = api_version
        # self.timeout = timeout
        
        # Create Azure OpenAI client
        self.client = OpenAI(
            api_key=api_key,
            base_url=azure_endpoint,
            # api_version=api_version,
            # timeout=timeout
        )
        
        # Expose chat.completions interface
        self.chat = self.client.chat


# Factory function for easy instantiation
def get_meta_client(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    deployment: Optional[str] = None,
    # api_version: Optional[str] = None
) -> AzureMetaClient:
    """
    Create an Azure Meta client from environment variables or provided values.
    
    Uses:
        META_api_key - API key for Azure Meta
        META_base_url - Azure Meta endpoint URL
        META_deployment_name - Model deployment name
    
    Returns:
        AzureMetaClient instance
    """
    key = api_key or os.environ.get("META_api_key") or os.environ.get("FOUNDERYAPI")
    url = endpoint or os.environ.get("META_base_url")
    deploy = deployment or os.environ.get("META_deployment_name")
    # version = api_version or os.environ.get("OPENAI_API_VERSION", "2024-12-01-preview")
    
    if not key:
        raise ValueError("No API key provided. Set META_api_key or FOUNDERYAPI env var, or pass api_key.")
    if not url:
        raise ValueError("No endpoint provided. Set META_base_url env var, or pass endpoint.")
    if not deploy:
        raise ValueError("No deployment name provided. Set META_deployment_name env var, or pass deployment.")
    
    return AzureMetaClient(
        api_key=key,
        azure_endpoint=url,
        deployment_name=deploy,
    )


# Convenience alias
AzureMeta = AzureMetaClient


if __name__ == "__main__":
    # Quick test
    client = get_meta_client()
    
    response = client.chat.completions.create(
        model=client.deployment_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What are 3 things to visit in Seattle?"}
        ],
        max_tokens=500,
        temperature=0.7
    )
    
    print("Response:", response.choices[0].message.content)
