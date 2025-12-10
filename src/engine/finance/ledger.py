from typing import List, Dict, Any, Optional
from src.engine.finance.models import FinancialLedger, Transaction, TransactionCategory

class LedgerSystem:
    """
    Manages the append-only financial ledger.
    Acts as the single source of truth for an agent's financial history and current balance.
    """
    
    def __init__(self, ledger: FinancialLedger):
        self.ledger = ledger

    def add_transaction(self, amount: float, category: str, description: str, week: int, related_entity_id: str = None) -> Transaction:
        """
        Record a new financial transaction.
        
        Args:
            amount (float): The value of the transaction (positive for income, negative for expense).
            category (str): The category of the transaction (e.g., 'expense', 'revenue').
            description (str): Human-readable description.
            week (int): The game week.
            related_entity_id (str, optional): ID of related entity (e.g. loan_id, bill_id).
        
        Returns:
            Transaction: The created immutable transaction record.
        """
        try:
             # Handle both string alias and enum value
             cat = TransactionCategory(category.lower()) if isinstance(category, str) else category
        except ValueError:
             cat = TransactionCategory.ADJUSTMENT
             
        tx = Transaction(
            amount=amount,
            category=cat,
            description=description,
            week=week,
            related_entity_id=related_entity_id
        )
        self.ledger.transactions.append(tx)
        return tx

    @property
    def balance(self) -> float:
        """Calculate real-time balance from transaction history."""
        return sum(t.amount for t in self.ledger.transactions)

    def get_history(self) -> List[Transaction]:
        """Return chronological history of transactions."""
        return sorted(self.ledger.transactions, key=lambda x: x.timestamp)
