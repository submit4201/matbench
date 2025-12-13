# Proxy to redirect imports to new Pydantic models
# Uses lazy loading to avoid circular imports

_lazy_map = {
    # From models.world
    'LaundromatState': 'src.models.world',
    'Machine': 'src.models.world',
    'StaffMember': 'src.models.world',
    'Building': 'src.models.world',
    # From engine.finance.models
    'RevenueStream': 'src.engine.finance.models',
    'Loan': 'src.engine.finance.models',
    'TaxRecord': 'src.engine.finance.models',
    'FinancialReport': 'src.engine.finance.models',
    'FinancialLedger': 'src.engine.finance.models',
    'Bill': 'src.engine.finance.models',
    # From models.social
    'SocialScore': 'src.models.social',
    'Ticket': 'src.models.social',
    # From models.event_ledger
    'GameEventLedger': 'src.models.event_ledger',
}

def __getattr__(name: str):
    if name in _lazy_map:
        import importlib
        module = importlib.import_module(_lazy_map[name])
        return getattr(module, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
