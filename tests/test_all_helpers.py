"""
Test script for all AI model helper packages

Tests connectivity and basic functionality for:
- OPSUS (Claude)
- META (Llama)
- MISTRAL
- PHI
- GEMINI
- AZURE/OPENAI
"""

import sys
import os
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

load_dotenv()

def test_helper(name, get_client_func, deployment_attr='deployment_name'):
    """Test a helper package"""
    print(f"\n{'='*60}")
    print(f"Testing {name}")
    print(f"{'='*60}")
    
    try:
        # Initialize client
        client = get_client_func()
        print(f"✓ Client initialized successfully")
        
        # Get model name
        if hasattr(client, deployment_attr):
            model = getattr(client, deployment_attr)
        elif hasattr(client, 'model'):
            model = client.model
        else:
            model = "unknown"
        
        print(f"  Model: {model}")
        
        # Make a simple API call
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello from {}'!".format(name)}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        content = response.choices[0].message.content
        print(f"✓ API call successful")
        print(f"  Response: {content[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("="*60)
    print("AI MODEL HELPER PACKAGE TESTS")
    print("="*60)
    
    results = {}
    
    # Test OPSUS (Claude)
    try:
        from agents.opsus_helper import get_claude_client
        results['OPSUS (Claude)'] = test_helper('OPSUS', get_claude_client, 'deployment_name')
    except ImportError as e:
        print(f"\n✗ Could not import opsus_helper: {e}")
        results['OPSUS (Claude)'] = False
    
    # Test META (Llama)
    try:
        from agents.meta_helper import get_meta_client
        results['META (Llama)'] = test_helper('META', get_meta_client, 'deployment_name')
    except ImportError as e:
        print(f"\n✗ Could not import meta_helper: {e}")
        results['META (Llama)'] = False
    
    # Test MISTRAL
    try:
        from agents.mistral_helper import get_mistral_client
        results['MISTRAL'] = test_helper('MISTRAL', get_mistral_client, 'deployment_name')
    except ImportError as e:
        print(f"\n✗ Could not import mistral_helper: {e}")
        results['MISTRAL'] = False
    
    # Test PHI
    try:
        from agents.phi_helper import get_phi_client
        results['PHI'] = test_helper('PHI', get_phi_client, 'deployment_name')
    except ImportError as e:
        print(f"\n✗ Could not import phi_helper: {e}")
        results['PHI'] = False
    
    # Test GEMINI
    try:
        from agents.gemini_helper import get_gemini_client
        results['GEMINI'] = test_helper('GEMINI', get_gemini_client, 'model')
    except ImportError as e:
        print(f"\n✗ Could not import gemini_helper: {e}")
        results['GEMINI'] = False
    
    # Test AZURE/OPENAI
    try:
        from agents.azure_helper import get_azure_client
        results['AZURE (OpenAI)'] = test_helper('AZURE', get_azure_client, 'deployment_name')
    except ImportError as e:
        print(f"\n✗ Could not import azure_helper: {e}")
        results['AZURE (OpenAI)'] = False
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for name, passed in results.items():
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name:20s} {status}")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
