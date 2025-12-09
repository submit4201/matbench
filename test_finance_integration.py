import pytest
from src.engine.game_engine import GameEngine
from src.engine.finance.models import Bill, TransactionCategory

def test_financial_integration():
    print("\n--- Testing Financial System Integration in GameEngine ---")
    
    # 1. Init GameEngine
    engine = GameEngine(["p1"])
    state = engine.states["p1"]
    
    # 2. Check FinancialSystem Init
    assert engine.financial_system is not None
    assert len(engine.financial_system.credit_system.agent_accounts.get("p1", [])) >= 1, "Should have SBA loan"
    
    print("SBA Loan present.")
    
    # 3. Simulate a turn (Week 1)
    # Give some revenue
    state.revenue_streams["Standard Wash"].unlocked = True
    
    # Run Process Turn
    results = engine.process_turn()
    
    # 4. Verify Ledger has Revenue
    print("Checking Ledger for Revenue...")
    txs = state.ledger.transactions
    revenues = [t for t in txs if t.category == TransactionCategory.REVENUE]
    assert len(revenues) > 0, "Should have weekly revenue transaction"
    print(f"Revenue found: ${revenues[0].amount}")
    
    # 5. Verify Bills Generated (Rent, etc)
    print("Checking Bills...")
    rent_bill = next((b for b in state.bills if b.category == "rent"), None)
    assert rent_bill is not None, "Rent bill should be generated"
    print(f"Rent Bill: ${rent_bill.amount}")
    
    # 6. Verify Loan Repayment Bill
    loan_bill = next((b for b in state.bills if b.category == "loan_repayment"), None)
    assert loan_bill is not None, "Loan repayment bill should be generated"
    print(f"Loan Payment Bill: ${loan_bill.amount}")
    
    # 7. Test Bill Payment
    print("Testing Bill Payment...")
    initial_balance = state.ledger.balance
    bill_amount = rent_bill.amount
    
    # Submit Pay Action
    action = {
        "type": "PAY_BILL",
        "bill_id": rent_bill.id
    }
    engine.submit_action("p1", action)
    engine.process_turn() # Process actions next turn
    
    # Check if bill paid
    rent_bill_updated = next((b for b in state.bills if b.id == rent_bill.id), None)
    assert rent_bill_updated.is_paid, "Rent bill should be paid"
    
    # Check Ledger expense
    expenses = [t for t in state.ledger.transactions if "Paid Bill" in t.description]
    assert len(expenses) > 0
    print("Bill payment recorded in ledger.")
    
    print("--- Integration Test Passed ---")

if __name__ == "__main__":
    try:
        test_financial_integration()
    except Exception as e:
        print(f"FAILED: {e}")
        import traceback
        traceback.print_exc()
