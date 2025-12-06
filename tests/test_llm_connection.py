import os
import sys

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.agents.llm_agent import LLMAgent
from openai import AzureOpenAI
from anthropic import AnthropicFoundry
from dotenv import load_dotenv

load_dotenv()
api = os.environ.get("FOUNDERYAPI")
base =  os.environ.get("FOUNDERYBASE")