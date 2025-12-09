
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    from src.engine.finance.bank import BankSystem
    print("Successfully imported BankSystem")
    bank = BankSystem()
    print("Successfully instantiated BankSystem")
    print(f"Subsystems: {bank.credit_system}, {bank.bill_system}, {bank.tax_system}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
