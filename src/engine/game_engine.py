from typing import Dict, List, Any, Optional
import logging
from src.world.laundromat import LaundromatState
from src.engine.time import TimeSystem, WeekPhase, Day
from src.engine.events import EventManager
from src.engine.economy import EconomySystem
from src.world.regulator import RegulatoryBody
from src.engine.communication import CommunicationChannel
from src.world.alliances import TrustSystem, AllianceType
from src.engine.mergers import MergerSystem
from src.world.financials import FinancialReport, TaxRecord
from src.engine.proposals import ProposalManager
from src.engine.vendor import VendorManager
import copy

logger = logging.getLogger(__name__)

class GameEngine:
    """
    Central Game Engine that acts as the source of truth for the simulation.
    Manages the main loop, state updates, and rule enforcement.
    """
    def __init__(self, agent_ids: List[str]):
        self.agent_ids = agent_ids
        self.states: Dict[str, LaundromatState] = {
            agent_id: LaundromatState(name=f"Laundromat {agent_id}", id=agent_id)
            for agent_id in agent_ids
        }
        self.economy_system = EconomySystem()
        
        # Initialize Revenue Streams
        for state in self.states.values():
            for stream in self.economy_system.base_streams:
                state.revenue_streams[stream.name] = copy.deepcopy(stream)
        self.time_system = TimeSystem()
        self.event_manager = EventManager()
        # self.economy_system = EconomySystem() # Moved up
        self.regulator = RegulatoryBody()
        self.communication = CommunicationChannel()
        self.trust_system = TrustSystem(agent_ids)
        self.merger_system = MergerSystem()
        self.vendor_manager = VendorManager()
        self.proposal_manager = ProposalManager(self)
        
        # Track pending actions for the current turn (batching)
        self.pending_actions: Dict[str, List[Dict[str, Any]]] = {
            agent_id: [] for agent_id in agent_ids
        }

    def get_state(self, agent_id: str) -> Optional[LaundromatState]:
        return self.states.get(agent_id)

    def get_public_state(self) -> Dict[str, Any]:
        """Returns public information about all agents (for competitors)."""
        return {
            agent_id: {
                "name": state.name,
                "reputation": state.reputation,
                "social_score": state.social_score,
                "price": state.price,
                "machines_count": len(state.machines),
                "is_open": True # Placeholder
            }
            for agent_id, state in self.states.items()
        }

    def submit_action(self, agent_id: str, action: Dict[str, Any]) -> bool:
        """
        Submit an action for the current turn.
        Actions are validated and stored until the turn is processed.
        """
        if agent_id not in self.agent_ids:
            logger.error(f"Unknown agent {agent_id} tried to submit action.")
            return False
            
        # Basic validation could happen here
        self.pending_actions[agent_id].append(action)
        return True

    def process_turn(self) -> Dict[str, Any]:
        """
        Processes the current turn (usually a week).
        1. Apply pending actions.
        2. Simulate customer traffic (Peak Phase).
        3. Apply economic effects.
        4. Check for Regulatory Violations.
        5. Generate Events.
        6. Advance Time.
        """
        results = {}
        
        # 1. Apply Actions (simplified for now)
        for agent_id, actions in self.pending_actions.items():
            state = self.states[agent_id]
            for action in actions:
                self._apply_action(state, action)
            # Clear actions after processing
            self.pending_actions[agent_id] = []

        # 1.5 Process Pending Deliveries
        for agent_id, state in self.states.items():
            if hasattr(state, "pending_deliveries"):
                remaining_deliveries = []
                for delivery in state.pending_deliveries:
                    if delivery["arrival_week"] <= self.time_system.current_week:
                        # Arrived!
                        item = delivery["item"]
                        qty = delivery["quantity"]
                        state.inventory[item] = state.inventory.get(item, 0) + qty
                        
                        # Notify
                        self.communication.send_message(
                            sender_id="System",
                            recipient_id=agent_id,
                            content=f"Delivery of {qty} {item} from {delivery['vendor_name']} has arrived.",
                            week=self.time_system.current_week
                        )
                    else:
                        remaining_deliveries.append(delivery)
                state.pending_deliveries = remaining_deliveries

        # 2. Simulate Week (if we are in PEAK phase or just batching weekly)
        # For now, we assume this is called once per week after all decisions
        
        seasonal_mods = self.time_system.get_seasonal_modifier()
        
        for agent_id, state in self.states.items():
            try:
                # Get active effects
                effects = self.event_manager.get_active_effects(agent_id)
                
                # Apply Social Penalties
                if effects["customer_satisfaction_penalty"] > 0:
                    state.update_social_score("customer_satisfaction", -effects["customer_satisfaction_penalty"])

                # World Bible 2.1.1: Weekly demand ~2,400 loads
                total_market = 2400
                base_customers = total_market / max(1, len(self.states))
                
                # Calculate customer count
                # Base share modified by reputation (baseline 50) and marketing
                raw_demand = base_customers * (1 + state.marketing_boost) * (state.social_score.total_score / 50.0)
                
                # Apply Demand Multiplier
                raw_demand *= effects["demand_multiplier"]
                
                if agent_id == "p1":
                    logger.info(f"[DEBUG] P1 Demand: Base={base_customers}, Soc={state.social_score.total_score}, Mkt={state.marketing_boost}, Eff={effects['demand_multiplier']}")

                # Calculate Capacity (Supply Constraint)
                # Realistic TPD (Turns Per Day) is 3-5 avg, 6-8 high. We use 7 as a hard physical cap for "busy" days.
                num_washers = sum(1 for m in state.machines if "washer" in m.type and not m.is_broken)
                max_weekly_capacity = num_washers * 7 * 7
                
                # Cap customers at capacity
                customer_count = min(raw_demand, max_weekly_capacity)
                
                # === CUSTOMER INTERACTION SOCIAL SCORE TRIGGERS ===
                
                # 1. Good service bonus - Customers are generally happy when served
                if customer_count > 50:
                    # Small boost for each 100 customers served (representing good experiences)
                    service_boost = (customer_count / 200.0) * 1.5  # ~1-3 points for busy weeks
                    state.update_social_score("customer_satisfaction", service_boost)
                    logger.info(f"Agent {agent_id}: Customer service boost +{service_boost:.1f} for {customer_count:.0f} customers")
                
                # 2. Price satisfaction - Competitive pricing boosts reputation
                avg_market_price = sum(s.price for s in self.states.values()) / len(self.states)
                if state.price <= avg_market_price:
                    # Reward for competitive pricing
                    price_boost = (avg_market_price - state.price) * 0.5  # Up to ~1-2 points
                    if price_boost > 0.1:
                        state.update_social_score("community_standing", min(price_boost, 2.0))
                elif state.price > avg_market_price * 1.3:
                    # Penalty for high prices
                    state.update_social_score("community_standing", -1.0)
                
                # 3. Out-of-stock penalty - Customers unhappy if can't buy supplies
                detergent_stock = state.inventory.get("detergent", 0)
                if detergent_stock < 10 and customer_count > 20:
                    state.update_social_score("customer_satisfaction", -2.0)
                    logger.info(f"Agent {agent_id}: Low detergent stock penalty -2.0")
                
                # 4. Machine quality bonus - No broken machines = better experience
                broken_count = sum(1 for m in state.machines if m.is_broken)
                if broken_count == 0 and len(state.machines) >= 10:
                    state.update_social_score("customer_satisfaction", 1.0)
                elif broken_count > len(state.machines) * 0.3:
                    # More than 30% broken is a problem
                    state.update_social_score("customer_satisfaction", -2.0)
                
                # 5. Penalty for overcrowding (Unmet demand)
                if raw_demand > max_weekly_capacity:
                    overcrowding_ratio = raw_demand / max_weekly_capacity
                    if overcrowding_ratio > 1.2: # If demand is >20% over capacity
                        # Reputation hit for long wait times
                        state.update_social_score("customer_satisfaction", -1.5)
                        logger.info(f"Agent {agent_id} is overcrowded! Demand: {raw_demand:.0f}, Cap: {max_weekly_capacity}. Rep -1.5.")
                
                # Financial Processing
                financial_report = self._process_financials(state, seasonal_mods, customer_count)
                
                results[agent_id] = {
                    "revenue": round(financial_report.total_revenue, 2),
                    "expenses": round(financial_report.total_operating_expenses + financial_report.total_cogs, 2),
                    "profit": round(financial_report.net_income, 2),
                    "customers": round(customer_count),
                    "new_balance": round(state.balance, 2)
                }
            except Exception as e:
                logger.error(f"Failed to process turn for agent {agent_id}: {e}", exc_info=True)
                results[agent_id] = {"error": str(e), "customers": 0, "revenue": 0}
        
        # 6. Advance Time - CRITICAL: This is what increments the week!
        self.time_system.advance_week()
        logger.info(f"Advanced to Week {self.time_system.current_week}")
        
        return results

    def _apply_action(self, state: LaundromatState, action: Dict[str, Any]):
        """Applies a single action to the state."""
        action_type = action.get("type")
        
        if action_type == "SET_PRICE":
            state.price = float(action.get("amount", state.price))
        elif action_type == "BUY_INVENTORY":
            item = action.get("item")
            qty = int(action.get("quantity", 0))
            vendor_id = action.get("vendor_id", "bulkwash")
            
            vendor = self.vendor_manager.get_vendor(vendor_id)
            if not vendor: vendor = self.vendor_manager.get_vendor("bulkwash")
            
            # Use agent-specific price (includes negotiated discounts)
            unit_price = vendor.get_price(item, agent_id=state.id)
            cost = qty * unit_price
            
            if state.balance >= cost:
                state.balance -= cost
                
                # Process order in vendor to update relationship
                result = vendor.process_order(
                    {item: qty}, 
                    self.time_system.current_week, 
                    self.vendor_manager.supply_chain, 
                    agent_id=state.id
                )
                
                # Determine arrival time
                # If delivery_days <= 2, it arrives same week (instant for gameplay flow)
                # Otherwise it arrives next week (or later)
                delivery_days = vendor.profile.delivery_days
                arrival_offset = 0
                if delivery_days > 2:
                    arrival_offset = 1 + (delivery_days - 3) // 7
                
                arrival_week = self.time_system.current_week + arrival_offset
                
                # Apply inventory update based on result (handling partial shipments)
                actual_qty = int(qty * result.get("quantity_multiplier", 1.0))
                
                if arrival_week <= self.time_system.current_week:
                    state.inventory[item] = state.inventory.get(item, 0) + actual_qty
                else:
                    state.pending_deliveries.append({
                        "item": item,
                        "quantity": actual_qty,
                        "arrival_week": arrival_week,
                        "vendor_name": vendor.profile.name
                    })
                    logger.info(f"Agent {state.id} ordered {actual_qty} {item} from {vendor.profile.name}. Arrives Week {arrival_week}.")
                
        elif action_type == "NEGOTIATE":
            item = action.get("item")
            vendor_id = action.get("vendor_id", "bulkwash")
            vendor = self.vendor_manager.get_vendor(vendor_id)
            if vendor:
                # Get social score total
                social_score = state.social_score.total_score if hasattr(state.social_score, "total_score") else state.reputation
                result = vendor.negotiate_price(item, state.name, social_score, agent_id=state.id)
                
                # Send response message
                self.communication.send_message(
                    sender_id=vendor.profile.name, # Use vendor name as sender
                    recipient_id=state.id,
                    content=result["message"],
                    week=self.time_system.current_week
                )
                
                if result["success"]:
                    logger.info(f"Agent {state.id} successfully negotiated with {vendor.profile.name} for {item}.")

        elif action_type == "MARKETING":
            amount = float(action.get("amount", 0))
            if state.balance >= amount:
                state.balance -= amount
                boost = amount / 100.0
                state.marketing_boost += boost
                state.update_social_score("community_standing", boost)
        
        elif action_type == "RESOLVE_TICKET":
            ticket_id = action.get("ticket_id")
            for t in state.tickets:
                if t.id == ticket_id and t.status.value == "open": # Check status value
                    t.status = t.status.__class__.RESOLVED # Set to RESOLVED enum
                    state.update_social_score("customer_satisfaction", 2.0)
                    
        elif action_type == "UPGRADE_MACHINE":
            if state.balance >= 500:
                state.balance -= 500
                # Add a new machine (simplified)
                from src.world.laundromat import Machine
                new_id = f"M{len(state.machines)}"
                state.machines.append(Machine(id=new_id, type="standard_washer"))
        
        elif action_type == "SEND_MESSAGE":
            recipient = action.get("recipient")
            content = action.get("content")
            if recipient:
                self.communication.send_message(state.id, recipient, content, self.time_system.current_week)
                
        elif action_type == "PROPOSE_ALLIANCE":
            target = action.get("target")
            duration = int(action.get("duration", 4))
            # Simplified: Auto-accept if trust is high enough (handled by TrustSystem logic)
            self.trust_system.propose_alliance(state.id, target, AllianceType.NON_AGGRESSION, duration)
            
        elif action_type == "INITIATE_BUYOUT":
            target_id = action.get("target")
            offer = float(action.get("offer", 0))
            target_state = self.states.get(target_id)
            if target_state:
                try:
                    self.merger_system.initiate_buyout(state, target_state, offer)
                except ValueError as e:
                    logger.warning(f"Buyout failed: {e}")

    def _process_financials(self, state: LaundromatState, seasonal_mods: Dict[str, float], customer_count: float) -> FinancialReport:
        report = FinancialReport(week=self.time_system.current_week)
        
        # 1. Revenue Calculation
        # Distribute customers across unlocked streams based on demand multipliers
        # Simplified: Assume "Standard Wash" and "Standard Dry" get the bulk, others are add-ons
        
        # Reset all stream revenues for this week
        for s in state.revenue_streams.values():
            s.weekly_revenue = 0.0

        # Base Wash/Dry
        wash_stream = state.revenue_streams.get("Standard Wash")
        dry_stream = state.revenue_streams.get("Standard Dry")
        
        wash_price = wash_stream.price if wash_stream else state.price
        dry_price = dry_stream.price if dry_stream else state.price * 0.75
        
        report.revenue_wash = customer_count * wash_price
        if wash_stream: wash_stream.weekly_revenue = report.revenue_wash
        
        report.revenue_dry = customer_count * dry_price # Assume 100% dry ratio for simplicity for now
        if dry_stream: dry_stream.weekly_revenue = report.revenue_dry
        
        # Add-ons (Vending, etc)
        # Calculate specific supply sales
        # Logic: 50% of customers bring their own soap. The rest buy if available.
        customers_needing_soap = int(customer_count * 0.5)
        customers_needing_softener = int(customer_count * 0.3) # 30% want softener and don't have it
        
        detergent_stream = state.revenue_streams.get("Detergent Sale")
        softener_stream = state.revenue_streams.get("Softener Sale")
        
        soap_sold = 0
        softener_sold = 0
        
        if detergent_stream and detergent_stream.unlocked:
             soap_sold = min(customers_needing_soap, state.inventory.get("detergent", 0))
             soap_revenue = soap_sold * detergent_stream.price
             report.revenue_vending += soap_revenue
             detergent_stream.weekly_revenue = soap_revenue
             
        if softener_stream and softener_stream.unlocked:
             softener_sold = min(customers_needing_softener, state.inventory.get("softener", 0))
             softener_revenue = softener_sold * softener_stream.price
             report.revenue_vending += softener_revenue
             softener_stream.weekly_revenue = softener_revenue

        for name, stream in state.revenue_streams.items():
            if not stream.unlocked: continue
            if stream.category == "vending" and name not in ["Detergent Sale", "Softener Sale"]:
                # Other vending (Snacks & Drinks, Dryer Sheets)
                if name == "Snacks & Drinks":
                    # Snacks require inventory - 20% of customers want snacks
                    customers_wanting_snacks = int(customer_count * 0.2)
                    snacks_available = state.inventory.get("snacks", 0)
                    snacks_sold = min(customers_wanting_snacks, snacks_available)
                    if snacks_sold > 0:
                        rev = snacks_sold * stream.price
                        report.revenue_vending += rev
                        stream.weekly_revenue = rev
                        report.cogs_vending += snacks_sold * stream.cost_per_unit
                        state.inventory["snacks"] = snacks_available - snacks_sold
                else:
                    # Dryer sheets etc - assume 20% of customers buy
                    sales = customer_count * 0.2 * stream.price
                    report.revenue_vending += sales
                    stream.weekly_revenue = sales
                    report.cogs_vending += customer_count * 0.2 * stream.cost_per_unit
            elif stream.category == "premium":
                # Assume 5% take premium
                sales = customer_count * 0.05 * stream.price
                report.revenue_premium += sales
                stream.weekly_revenue = sales # Track revenue for this stream
                # Cost?
        
        # Update State Active Customers (for Frontend)
        state.active_customers = int(customer_count)
        
        report.total_revenue = (report.revenue_wash + report.revenue_dry + 
                              report.revenue_vending + report.revenue_premium + 
                              report.revenue_membership + report.revenue_other)
        
        # 2. COGS (Supplies)
        # Detergent/Softener usage
        # Total usage = Sold + Complimentary?
        # For now, assume we ONLY sell. If they bring their own, we use 0.
        # Wait, machines use water/elec, but soap is per load.
        # If customer brings own soap, we don't use inventory.
        # If customer buys soap, we use inventory.
        
        soap_used = soap_sold
        softener_used = softener_sold
        
        # Check if we ran out for those who needed it
        if soap_sold < customers_needing_soap:
            # Missed sales opportunity, maybe small rep hit?
            # state.reputation -= 0.1
            pass
        
        # Calculate Cost (Replacement Cost)
        # We use a standard replacement cost for reporting
        detergent_cost_unit = 0.15 
        softener_cost_unit = 0.10
        
        report.cogs_supplies = (soap_used * detergent_cost_unit) + (softener_used * softener_cost_unit)
        
        report.total_cogs = report.cogs_supplies + report.cogs_vending
        report.gross_profit = report.total_revenue - report.total_cogs
        
        # 3. Operating Expenses (Fixed)
        # Rent: $1000/month -> $250/week
        report.expense_rent = 250.0
        
        # Utilities: Variable based on usage + Fixed
        # Water: $0.15/load, Elec: $0.20/wash, $0.25/dry, Gas: $0.10/dry
        water_cost = customer_count * 0.15
        elec_cost = customer_count * (0.20 + 0.25)
        gas_cost = customer_count * 0.10
        report.expense_utilities = (water_cost + elec_cost + gas_cost) * seasonal_mods.get("heating_cost", 1.0)
        
        # Labor
        report.expense_labor = sum(staff.wage * 20 for staff in state.staff) # 20hrs/week part time
        
        # Maintenance
        # Routine maintenance consumes parts occasionally
        # Assume 1 part used per 10 machines per week on average
        parts_needed = max(1, int(len(state.machines) / 10))
        parts_available = state.inventory.get("parts", 0)
        
        parts_used = min(parts_needed, parts_available)
        
        # Update Inventory Usage
        usage = {
            "detergent": soap_used,
            "softener": softener_used,
            "parts": parts_used
        }
        if hasattr(state, "update_inventory_usage"):
            state.update_inventory_usage(usage)
        else:
            # Fallback if method missing
            state.inventory["detergent"] = max(0, detergent_available - soap_used)
            state.inventory["softener"] = max(0, softener_available - softener_used)
            state.inventory["parts"] = max(0, parts_available - parts_used)
        
        base_maintenance_cost = 20.0 * len(state.machines)
        
        # If parts missing, maintenance is more expensive (emergency service) or less effective
        if parts_used < parts_needed:
            base_maintenance_cost *= 1.5 # 50% penalty cost for calling external tech
            logger.info(f"Agent {state.id} missing parts for maintenance! Cost penalty applied.")
            
        report.expense_maintenance = base_maintenance_cost
        
        # Marketing
        # If marketing boost is active, assume some spend was made (handled in actions, but maybe ongoing?)
        # For now, just fixed insurance/other
        report.expense_insurance = 37.5 # $150/month
        report.expense_other = 25.0 # Internet/Security
        
        report.total_operating_expenses = (report.expense_rent + report.expense_utilities + 
                                         report.expense_labor + report.expense_maintenance + 
                                         report.expense_marketing + report.expense_insurance + 
                                         report.expense_other)
        
        report.operating_income = report.gross_profit - report.total_operating_expenses
        
        # 4. Loans & Interest
        for loan in state.loans:
            if loan.balance > 0:
                interest = loan.balance * (loan.interest_rate_monthly / 4.0)
                report.expense_interest += interest
                loan.balance += interest # Add interest to balance
                
                # Payment
                payment = min(loan.weekly_payment, loan.balance)
                if state.balance >= payment:
                    state.balance -= payment
                    loan.balance -= payment
                    loan.weeks_remaining -= 1
                else:
                    # Default logic (simplified)
                    loan.missed_payments += 1
                    loan.is_defaulted = True
        
        report.net_income_before_tax = report.operating_income - report.expense_interest + report.income_interest - report.fines
        
        # 5. Taxes (Quarterly Provision)
        # We calculate provision weekly for reporting, but pay quarterly
        report.tax_provision = self.economy_system.calculate_taxes(report.total_revenue, 
                                                                 report.total_operating_expenses + report.total_cogs + report.expense_interest, 
                                                                 0) # Deductions placeholder
        
        report.net_income = report.net_income_before_tax - report.tax_provision
        
        # Update State
        report.cash_beginning = state.balance
        state.balance += report.net_income # Add net income (cash flow approximation)
        report.cash_ending = state.balance
        
        # Archive
        state.financial_reports.append(report)
        state.process_week(report.total_revenue, report.total_operating_expenses + report.total_cogs) # Legacy compat
        
        return report
