
import sys
import os

# Add src to path
sys.path.append(os.getcwd())

try:
    from tests.test_finance_alignment import test_loan_terms_alignment, test_tax_credits_logic
    
    print("Running test_loan_terms_alignment...")
    test_loan_terms_alignment()
    print("PASS: test_loan_terms_alignment")
    
    print("Running test_tax_credits_logic...")
    test_tax_credits_logic()
    print("PASS: test_tax_credits_logic")
    
    print("\nALL CHECKS PASSED")
    
except ImportError as e:
    print(f"ImportError: {e}")
    # Try to verify path
    print(f"Current Path: {sys.path}")
    print(f"FAIL: Error: {e}")
    import traceback
    traceback.print_exc()
