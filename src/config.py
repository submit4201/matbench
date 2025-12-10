import os
from dotenv import load_dotenv

load_dotenv()   

E=os.environ.get
VERSION="2024-12-01-preview"
LLMDICT={
      "AZURE":{
        "APIKEY":E("AZURE_api_key"),
        "BASEURL":E("AZURE_base_url"),
        "MODEL":E("AZURE_deployment_name"),
        "VERSION":VERSION

    },
      "OPENAI":{
        "APIKEY":E("OPENAI_api_key"),
        "BASEURL":E("OPENAI_base_url"),
        "MODEL":E("OPENAI_deployment_name"),
        "VERSION":VERSION

    },
      "GEMINI":{
        "APIKEY":E("GEMINI_api_key"),
        "BASEURL":E("GEMINI_base_url"),
        "MODEL":"gemini-flash-lite-latest",
        "VERSION":VERSION
    },
      "OPSUS":{
        "APIKEY":E("OPUS_api_key"),
        "BASEURL":E("OPUS_base_url"),
        "MODEL":E("OPUS_deployment_name"),
        "VERSION":VERSION 
    },
      "META":{
        "APIKEY":E("META_api_key"),
        "BASEURL":E("META_base_url"),
        "MODEL":E("META_deployment_name"),
        "VERSION":VERSION
    },
      "MISTRAL":{
        "APIKEY":E("MISTRAL_api_key"),
        "BASEURL":E("MISTRAL_base_url"),
        "MODEL":E("MISTRAL_deployment_name"),
        "VERSION":VERSION
    },
      "PHI":{
        "APIKEY":E("PHI_api_key"),
        "BASEURL":E("PHI_base_url"),
        "MODEL":E("PHI_deployment_name"),
        "VERSION":VERSION
    }
}
import random
rabd = [i for i in LLMDICT.keys()]
NPC = random.choice(rabd)
from pprint import pprint
# pprint(NPC)
npc = LLMDICT[NPC]
LLMDICT["NPC"] = npc
# pprint(LLMDICT)

# NPC Provider for dynamic world generation (customers, vendors, events)
# Use fast/cheap models to minimize costs gemini is also fast and cheap
GAME_MASTE_MODEL = "gemini-flash-latest"
GAME_MASTE_PROVIDER = "GEMINI"
JUDGE_MODEL = "claude-4.5-opus"
JUDGE_PROVIDER = "OPSUS"
NPC_PROVIDER = "PHI"  # or "MISTRAL" - both are fast and cheap

