from src.engine.finance.taxation import TaxSystem
from src.engine.finance.models import TransactionCategory, FinancialLedger
from dataclasses import dataclass

@dataclass
class MockMachine:
    is_eco: bool = False

@dataclass
class MockStaff:
    pass

def debug_tax():
    print("Testing Tax System...")
    sys = TaxSystem()
    
    ledger = FinancialLedger()
    print("Adding donation...")
    ledger.add(-1000, "expense", "Charity Donation", 1)
    print(f"Transaction: {ledger.transactions[0]}")
    print(f"Category match? {ledger.transactions[0].category == TransactionCategory.EXPENSE}")
    
    machines = [MockMachine(is_eco=True)]
    staff = [MockStaff(), MockStaff()]
    
    print("Calculating credits...")
    credits = sys._calculate_tax_credits(ledger.transactions, machines, staff)
    print(f"Credits: {credits}")
    
    expected = 50 + 50 + 200 # 300
    if credits == expected:
        print("SUCCESS")
    else:
        print(f"FAILURE: Expected {expected}, got {credits}")

if __name__ == "__main__":
    try:
        debug_tax()
    except Exception as e:
        print(f"CRASH: {e}")
        import traceback
        traceback.print_exc()
