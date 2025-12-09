from src.engine.finance.models import FinancialLedger, TransactionCategory

def debug_ledger():
    print("Initializing Ledger...")
    l = FinancialLedger()
    print("Adding transaction...")
    l.add(-100, "expense", "test", 1)
    print("Added successfully.")
    print(l.transactions[0])
    
    print("Adding transaction via Enum...")
    l.add(-100, TransactionCategory.EXPENSE, "test enum", 1)
    print("Added successfully.")

if __name__ == "__main__":
    try:
        debug_ledger()
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
