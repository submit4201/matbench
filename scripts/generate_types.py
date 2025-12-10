"""
Generate TypeScript interfaces from Pydantic models.
Exports a combined JSON Schema that can be converted with json-schema-to-typescript.
"""
import os
import sys
import json

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def export_json_schema():
    """Export JSON schemas from Pydantic models as a combined schema."""
    from src.models.world import LaundromatState, Machine, StaffMember, Building
    from src.models.financial import Transaction, FinancialLedger, Bill, RevenueStream, Loan, FinancialReport
    from src.models.agent import Observation, Action, Message
    from src.models.social import SocialScore, Ticket
    from src.models.commerce import VendorProfile, SupplyOffer, SupplyChainEvent, Proposal
    from src.models.population import CustomerMemory, Persona
    from src.models.communication import Alliance, CommunicationGroup, CommunicationMessage
    
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    output_dir = os.path.join(base_dir, "frontend", "src", "types")
    os.makedirs(output_dir, exist_ok=True)
    
    models = [
        # World
        LaundromatState, Machine, StaffMember, Building,
        # Financial
        Transaction, FinancialLedger, Bill, RevenueStream, Loan, FinancialReport,
        # Agent
        Observation, Action, Message,
        # Social
        SocialScore, Ticket,
        # Commerce
        VendorProfile, SupplyOffer, SupplyChainEvent, Proposal,
        # Population
        CustomerMemory, Persona,
        # Communication
        Alliance, CommunicationGroup, CommunicationMessage,
    ]
    
    # Build combined schema with all definitions
    combined_defs = {}
    for model in models:
        schema = model.model_json_schema()
        model_name = model.__name__
        
        # Merge $defs from each model into combined
        if "$defs" in schema:
            for def_name, def_schema in schema["$defs"].items():
                combined_defs[def_name] = def_schema
            del schema["$defs"]
        
        # Add the model itself as a definition
        combined_defs[model_name] = schema
    
    # Create a schema where all types are properties (for proper TS generation)
    properties = {}
    for name in combined_defs:
        properties[name] = {"$ref": f"#/$defs/{name}"}
    
    combined_schema = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$defs": combined_defs,
        "type": "object",
        "title": "GameModels",
        "description": "All game model types",
        "properties": properties,
        "additionalProperties": False
    }
    
    output_file = os.path.join(output_dir, "schema.json")
    with open(output_file, "w") as f:
        json.dump(combined_schema, f, indent=2)
    
    print(f"✅ JSON Schema exported to: {output_file}")
    print(f"   Contains {len(combined_defs)} type definitions")
    print(f"")
    print(f"To generate TypeScript, run:")
    print(f"  cd frontend")
    print(f"  npx json-schema-to-typescript src/types/schema.json -o src/types/generated.ts --declareExternallyReferenced")

if __name__ == "__main__":
    export_json_schema()
