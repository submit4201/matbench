from src.engine.game_engine import GameEngine
from src.engine.time import Season
import json

def debug_financials():
    # Initialize engine with one agent
    engine = GameEngine(["agent_1"])
    state = engine.get_state("agent_1")
    
    # Set some baseline values
    state.reputation = 50.0
    state.marketing_boost = 0.0
    state.price = 3.00 # Base price
    
    # Process one turn
    print("Processing Turn 1...")
    result = engine.process_turn()
    
    # Get the financial report
    report = state.financial_reports[-1]
    
    with open("debug_result_v2.txt", "w", encoding="utf-8") as f:
        f.write("\n--- Financial Debug Report ---\n")
        f.write(f"Week: {report.week}\n")
        f.write(f"Customer Count: {result['results']['agent_1']['customers']}\n")
        f.write(f"Total Revenue: ${report.total_revenue:.2f}\n")
        f.write(f"  - Wash: ${report.revenue_wash:.2f}\n")
        f.write(f"  - Dry: ${report.revenue_dry:.2f}\n")
        f.write(f"  - Vending: ${report.revenue_vending:.2f}\n")
        f.write(f"Total Expenses: ${(report.total_operating_expenses + report.total_cogs):.2f}\n")
        f.write(f"  - COGS: ${report.total_cogs:.2f}\n")
        f.write(f"  - OpEx: ${report.total_operating_expenses:.2f}\n")
        f.write(f"Net Income: ${report.net_income:.2f}\n")
        
        f.write("\n--- State Data ---\n")
        f.write(f"Reputation: {state.reputation}\n")
        f.write(f"Marketing Boost: {state.marketing_boost}\n")
        f.write(f"Base Customers Calculation:\n")
        total_market = 2400
        base_customers = total_market / 1
        f.write(f"  Total Market: {total_market}\n")
        f.write(f"  Base Customers (per agent): {base_customers}\n")
        f.write(f"  Calculated Raw Demand: {base_customers} * (1 + {state.marketing_boost}) * ({state.reputation} / 50.0) = {base_customers * (1 + state.marketing_boost) * (state.reputation / 50.0)}\n")
        
        # Capacity check
        num_washers = sum(1 for m in state.machines if "washer" in m.type and not m.is_broken)
        max_weekly_capacity = num_washers * 7 * 7
        f.write(f"  Capacity: {num_washers} washers * 7 loads/day * 7 days = {max_weekly_capacity}\n")
        
        f.write("\n--- Inventory Check ---\n")
        f.write(f"Soap Remaining: {state.inventory.get('soap')}\n")
        f.write(f"Softener Remaining: {state.inventory.get('softener')}\n")
        f.write(f"Parts Remaining: {state.inventory.get('parts')}\n")

if __name__ == "__main__":
    debug_financials()
