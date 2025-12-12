from typing import Dict, List, Any, Optional
from src.utils.logger import get_logger
from src.world.laundromat import LaundromatState
from src.engine.core.time import TimeSystem, WeekPhase, Day
from src.engine.core.events import EventManager
from src.engine.social.ethical_events import EthicalEventManager
from src.engine.commerce.market import MarketSystem as EconomySystem
from src.world.regulator import RegulatoryBody
from src.engine.social.communication import CommunicationChannel, ChannelType, MessageIntent
from src.engine.social.alliances import TrustSystem, AllianceType
from src.engine.commerce.mergers import MergerSystem
from src.engine.finance import FinancialReport, TaxRecord, Bill, FinancialSystem
from src.engine.commerce.proposals import ProposalManager
from src.engine.commerce.vendor import VendorManager
from src.engine.commerce.real_estate import RealEstateManager
from src.engine.metrics_auditor import MetricsAuditor
from src.engine.persistence.event_repo import EventRepository
from src.engine.projections.state_builder import StateBuilder
from src.engine.actions.registry import ActionRegistry
from src.models.events.finance import DailyRevenueProcessed
from src.models.events.operations import MachineWearUpdated, MarketingBoostDecayed
from src.models.events.social import ReputationChanged, ScandalStarted
import copy
# Load handlers modules to register them
import src.engine.actions.handlers 

class GameEngine:
    """
    Central Game Engine that acts as the source of truth for the simulation.
    Manages the main loop, state updates, and rule enforcement.
    """
    def __init__(self, agent_ids: List[str]):
        self.agent_ids = agent_ids
        # In EventSourcing, state is derived. However, for performance we keep a "Current State" cache logic.
        # But per instruction "Kill the Monolith", we should rely on Repo and Builder.
        # For Phase 1 transition, I will keep 'self.states' but manage it via events.
        
        self.event_repo = EventRepository()
        
        # Init States - we can create initial events or just init objects.
        # Creating initial objects for now to ease transition.
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
        self.ethical_event_manager = EthicalEventManager()
        # self.economy_system = EconomySystem() # Moved up
        self.regulator = RegulatoryBody()
        self.communication = CommunicationChannel()
        self.trust_system = TrustSystem(agent_ids)
        self.merger_system = MergerSystem()
        self.vendor_manager = VendorManager()
        self.proposal_manager = ProposalManager(self)
        self.metrics_auditor = MetricsAuditor()
        self.financial_system = FinancialSystem(agent_ids)
        self.real_estate_manager = RealEstateManager()
        
        # Initialize Logger
        self.logger = get_logger("src.engine", category="engine")
        
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

    def process_daily_turn(self) -> Dict[str, Any]:
        """
        Processes a single Day.
        1. Apply pending actions.
        2. Process daily financials for each agent.
        3. Advance Day.
        4. If week ends, run process_week() for weekly-only tasks.
        """
        # 1. Apply Daily Actions
        for agent_id, actions in self.pending_actions.items():
            state = self.states[agent_id]
            for action in actions:
                self._apply_action(state, action)
            self.pending_actions[agent_id] = []

        # 2. Process Daily Financials for each agent
        seasonal_mods = self.time_system.get_seasonal_modifier()
        daily_results = {}
        daily_events = []
        
        for agent_id, state in self.states.items():
            try:
                # Get Event instead of mutating state directly
                rev_event = self._process_daily_financials(state, seasonal_mods)
                daily_events.append(rev_event)
                
                # Reconstruct legacy result for return (Wait to apply event first?)
                # We need to apply event to get 'new_balance' correct
            except Exception as e:
                logger.error(f"Failed daily processing for {agent_id}: {e}")
                daily_results[agent_id] = {"error": str(e)}

        # Save & Apply Events (The "Brain" -> "Repository" -> "Scribe" loop)
        if daily_events:
            self.event_repo.save_batch(daily_events)
            for event in daily_events:
                # Apply to state
                StateBuilder.apply_event(self.states[event.agent_id], event)
                
                # Now populate results with updated state
                state = self.states[event.agent_id]
                # We need to re-calculate bill counts or pass them out?
                # _process_daily_financials handles logic, but extracting the purely readonly data requires access.
                # For now, simplistic reconstruction:
                daily_results[event.agent_id] = {
                    "customers": event.customer_count,
                    "revenue": round(event.revenue_wash + event.revenue_dry + event.revenue_vending, 2),
                    "day": self.time_system.current_day.value,
                    "new_balance": round(state.balance, 2),
                    "overdue_bills": 0, # TODO: Refactor bill notification loop to return this metric if needed
                    "bills_due_soon": 0 
                }

        # 3. Advance Time (Day)
        week_advanced = self.time_system.advance_day()
        
        # 4. Weekly Processing (if Sunday ended) - bills, taxes, events, etc.
        results = {}
        if week_advanced:
            logger.info(f"Week advanced to {self.time_system.current_week}. Running Weekly Processes.")
            results = self.process_week()
            results["daily"] = daily_results
        else:
            logger.info(f"Advanced to {self.time_system.current_day.value}")
            results = {
                "status": "day_advanced", 
                "current_day": self.time_system.current_day.value,
                "daily": daily_results
            }
            
        return results

    def _process_daily_financials(self, state: LaundromatState, seasonal_mods: Dict[str, float]) -> DailyRevenueProcessed:
        """
        Process daily revenue and expenses.
        Returns an Event describing the outcome. State mutation is handled by the Event Handler.
        """
        # Calculate daily customer count (weekly base / 7)
        total_market = 2400  # Weekly market demand
        base_customers = total_market / max(1, len(self.states)) / 7.0  # Daily share
        
        # Apply modifiers
        raw_demand = base_customers * (1 + state.marketing_boost) * (state.social_score.total_score / 50.0)
        
        # Get active effects
        effects = self.event_manager.get_active_effects(state.id)
        raw_demand *= effects["demand_multiplier"]
        
        # Apply market trend
        trend = self.economy_system.active_trend
        if trend and trend.demand_shift != 1.0:
            raw_demand *= trend.demand_shift
        
        # Capacity constraint
        num_washers = sum(1 for m in state.machines if "washer" in m.type and not m.is_broken)
        max_daily_capacity = num_washers * 7  # ~7 turns per day per machine
        
        customer_count = min(raw_demand, max_daily_capacity)
        
        # Calculate daily revenue
        wash_stream = state.revenue_streams.get("Standard Wash")
        dry_stream = state.revenue_streams.get("Standard Dry")
        
        wash_price = wash_stream.price if wash_stream else state.price
        dry_price = dry_stream.price if dry_stream else state.price * 0.75
        
        daily_wash_rev = customer_count * wash_price
        daily_dry_rev = customer_count * dry_price
        
        # Vending sales (daily portion)
        daily_vending = 0.0
        daily_soap_rev = 0.0
        daily_sheets_rev = 0.0
        
        customers_needing_soap = int(customer_count * 0.5)
        
        detergent_stream = state.revenue_streams.get("Detergent Sale")
        if detergent_stream and detergent_stream.unlocked:
            soap_sold = min(customers_needing_soap, state.inventory.get("detergent", 0))
            soap_rev = soap_sold * detergent_stream.price
            daily_soap_rev = soap_rev
            daily_vending += soap_rev
            # Inventory update is deferred to Handler
        
        # Dryer sheets stream
        dryer_sheets_stream = state.revenue_streams.get("Dryer Sheets")
        if dryer_sheets_stream and dryer_sheets_stream.unlocked:
            sheets_sold = customer_count * 0.2
            sheets_rev = sheets_sold * dryer_sheets_stream.price
            daily_sheets_rev = sheets_rev
            daily_vending += sheets_rev
        
        # Machine Physics - Utility Calculation
        daily_utility_cost = 0.0
        # Distribute customers across machines to simulate usage
        # Simple Logic: Avg loads per person = 1.0. 
        # Loads fill machines.
        loads_to_process = customer_count
        
        # Machine Configs (Constants for now, could be on Machine model)
        # Standard: Water 0.15, Elec 0.20
        # Eco: Water 0.08, Elec 0.12
        # Industrial: Water 0.25, Elec 0.40
        
        for machine in state.machines:
            if loads_to_process <= 0:
                break
            if machine.is_broken or "dryer" in machine.type: # Dryers handled separately or linked?
                continue
                
            # Assume 1 load capacity per turn * 7 turns = 7 loads/day max
            capacity = 7 
            loads = min(loads_to_process, capacity)
            loads_to_process -= loads
            
            # Rate Calculation
            w_cost = 0.15
            e_cost = 0.20
            if "eco" in machine.type:
                 w_cost = 0.08
                 e_cost = 0.12
            
            daily_utility_cost += loads * (w_cost + e_cost)
            
        # Dryer Utility (Gas/Elec) - Link to wash loads?
        # Assume 1 dryer load per wash load roughly
        dryer_loads = customer_count 
        daily_utility_cost += dryer_loads * (0.10 + 0.25) # Gas + Elec
        
        # Supply Cost Calculation (COGS)
        daily_supply_cost = 0.0
        # Detergent
        if soap_sold > 0:
             daily_supply_cost += soap_sold * 0.15 # Unit cost
             
        # Create Event
        revenue_event = DailyRevenueProcessed(
            week=self.time_system.current_week,
            day=self.time_system.current_day.value,
            agent_id=state.id,
            revenue_wash=float(daily_wash_rev),
            revenue_dry=float(daily_dry_rev),
            revenue_vending=float(daily_vending),
            revenue_soap=float(daily_soap_rev),
            revenue_sheets=float(daily_sheets_rev),
            customer_count=int(customer_count),
            utility_cost=float(daily_utility_cost),
            supply_cost=float(daily_supply_cost)
        )
        
        # === DAILY BILL CHECKING (Side Effect - Notifications) ===
        # Use Read-Only state access
        current_week = self.time_system.current_week
        
        for bill in state.bills:
            if bill.is_paid:
                continue
                
            # Bill is overdue
            if bill.due_week < current_week:
                # Send overdue notice (only once per bill - check if already notified)
                overdue_key = f"overdue_{bill.id}"
                if overdue_key not in getattr(state, '_notified_bills', set()):
                    if not hasattr(state, '_notified_bills'):
                        state._notified_bills = set()
                    state._notified_bills.add(overdue_key)
                    
                    self.communication.send_system_message(
                        recipient_id=state.id,
                        content=f"⚠️ **OVERDUE BILL**\\n\\n{bill.name}: ${bill.amount:.2f}\\nWas due Week {bill.due_week}. Please pay immediately to avoid penalties.",
                        week=current_week,
                        intent=MessageIntent.ANNOUNCEMENT
                    )
                    
            # Bill due this week (reminder on first day)
            elif bill.due_week == current_week and self.time_system.current_day.value == "Monday":
                self.communication.send_system_message(
                    recipient_id=state.id,
                    content=f"📋 **Bill Due This Week**\\n\\n{bill.name}: ${bill.amount:.2f}\\nDue by end of Week {bill.due_week}.",
                    week=current_week,
                    intent=MessageIntent.REMINDER
                )
        
        return revenue_event

    def _calculate_staff_effects(self, state: LaundromatState) -> Dict[str, float]:
        """Calculates total bonuses from staff members."""
        effects = {
            "cleanliness_boost": 0.0,
            "maintenance_skill": 0.0, # Reduces wear rate
            "service_boost": 0.0      # Improves customer satisfaction
        }
        
        for staff in state.staff:
            skill = staff.skill_level
            if staff.role == "cleaner":
                effects["cleanliness_boost"] += 0.2 * skill
            elif staff.role == "technician":
                effects["maintenance_skill"] += 0.1 * skill
            elif staff.role == "attendant":
                effects["service_boost"] += 0.15 * skill
                
        return effects

    def process_week(self) -> Dict[str, Any]:
        """
        Processes the End-of-Week logic (Financials, Events, etc.).
        This is now called by process_daily_turn when the week rolls over.
        """
        results = {}
        weekly_events = []
        
        # 0. Update Market Trends (Keep existing logic or event-ize? Market system updates itself internally)
        self.economy_system.update_trends(self.time_system.current_week)
        trend = self.economy_system.active_trend
        if trend and trend.week == self.time_system.current_week:
            logger.info(f"Market Trend: {trend.news_headline}")
            # Broadcast news
            for agent_id in self.agent_ids:
                self.communication.send_system_message(agent_id, f"BREAKING NEWS: {trend.news_headline}", self.time_system.current_week, intent=MessageIntent.ANNOUNCEMENT)

        # 1.5 Process Pending Deliveries (Logic remains for now, could be event-ized later)
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
                        self.communication.send_system_message(
                            recipient_id=agent_id,
                            content=f"Delivery of {qty} {item} from {delivery['vendor_name']} has arrived.",
                            week=self.time_system.current_week
                        )
                    else:
                        remaining_deliveries.append(delivery)
                state.pending_deliveries = remaining_deliveries


        # 2. Simulate Week
        seasonal_mods = self.time_system.get_seasonal_modifier()
        
        for agent_id, state in self.states.items():
            try:
                # --- Marketing Decay ---
                if state.marketing_boost > 0:
                    decay = state.marketing_boost * 0.2 # 20% decay per week
                    new_boost = max(0.0, state.marketing_boost - decay)
                    # Emit Event
                    marketing_event = MarketingBoostDecayed(
                        week=self.time_system.current_week,
                        agent_id=agent_id,
                        decay_amount=decay,
                        remaining_boost=new_boost
                    )
                    weekly_events.append(marketing_event)

                # --- Machine Wear (Physics) ---
                for machine in state.machines:
                    if not machine.is_broken:
                        # Wear depends on type/quality
                        base_wear = 0.02 # 2% per week default
                        if "commercial" in machine.type:
                            base_wear = 0.01
                        elif "industrial" in machine.type:
                            base_wear = 0.005
                        
                        # Technician Logic implied in StateBuilder (skill reduces wear)? 
                        # Or calculate specific wear here?
                        # Using basic wear for now.
                        wear_event = MachineWearUpdated(
                            week=self.time_system.current_week,
                            agent_id=state.id,
                            machine_id=machine.id,
                            wear_amount=base_wear,
                            current_condition=max(0.0, machine.condition - base_wear)
                        )
                        weekly_events.append(wear_event)

                # --- Social/Scandals ---
                effects = self.event_manager.get_active_effects(agent_id)
                
                # Active Scandal Persistence
                # If there's an active scandal effect, hit reputation
                if "scandal" in effects: # Simplified check
                    rep_hit = -5.0
                    scandal_event = ReputationChanged(
                        week=self.time_system.current_week,
                        agent_id=state.id,
                        delta=rep_hit,
                        reason="Active Scandal Fallout"
                    )
                    weekly_events.append(scandal_event)

                # --- Financial Report Generation (Safe Read) ---
                # NOTE: _process_financials still mutates 'parts' inventory. 
                # Ideally this should be an event "MaintenanceInventoryUsed". Keeping as legacy for now to satisfy report generation.
                # Use current customer count from state (updated daily)
                customer_count_est = state.active_customers * 7 # Rough est
                
                financial_report = self._process_financials(state, seasonal_mods, customer_count_est)
                
                # Financial System Orchestration
                self.financial_system.process_week(state, self.time_system.current_week, financial_report)
                
                results[agent_id] = {
                    "revenue": round(financial_report.total_revenue, 2),
                    "expenses": round(financial_report.total_operating_expenses + financial_report.total_cogs, 2),
                    "profit": round(financial_report.net_income, 2),
                    "customers": round(state.active_customers),
                    "new_balance": round(state.balance, 2)
                }
            except Exception as e:
                logger.error(f"Failed to process turn for agent {agent_id}: {e}", exc_info=True)
                results[agent_id] = {"error": str(e), "customers": 0, "revenue": 0}
        
        # 3. Save & Apply Weekly Events
        if weekly_events:
            self.event_repo.save_batch(weekly_events)
            for event in weekly_events:
                StateBuilder.apply_event(self.states[event.agent_id], event)

        # 5.5 Record Metrics (Audit)
        self.metrics_auditor.record_weekly_state(self.time_system.current_week, self.states)

        logger.info(f"Processed logic for Week {self.time_system.current_week}")
        
        return results

    def _apply_action(self, state: LaundromatState, action: Dict[str, Any]):
        """
        Executes an action by looking up its handler, generating events, and applying them.
        """
        action_type = action.get("type")
        week = self.time_system.current_week
        
        # Build Context (Service/System Dependencies)
        context = {
            "vendor_manager": self.vendor_manager,
            "financial_system": self.financial_system,
            "communication": self.communication,
            "real_estate_manager": getattr(self, "real_estate_manager", None),
            "ethical_event_manager": getattr(self, "ethical_event_manager", None),
            "trust_system": getattr(self, "trust_system", None),
            "merger_system": getattr(self, "merger_system", None),
            "economy_system": self.economy_system,
            # Add self for rare edge cases or read-only access if needed? 
            # Ideally avoid passing 'engine', but for 'get_state' calls in logic it might be needed.
            "engine": self 
        }

        # 1. Lookup Handler
        handler = ActionRegistry.get_handler(action_type)
        if not handler:
            # Fallback for ACTIONS NOT YET MIGRATED
            return self._apply_legacy_action(state, action)
            
        # 2. Execute Handler (Pure Logic)
        try:
            events = handler(state, action, week, context)
        except Exception as e:
            self.logger.error(f"Action Handler Failed [{action_type}]: {e}")
            # If handler fails, maybe try legacy? No, that's dangerous.
            return False
            
        if not events:
            return False
            
        # 3. Persist Events
        self.event_repo.save_batch(events)
        
        # 4. Update State (Rebuild or Apply)
        for event in events:
            StateBuilder.apply_event(state, event)
            
        return True

    def _apply_legacy_action(self, state: LaundromatState, action: Dict[str, Any]):
        """
        Legacy fallback - DEPRECATED.
        All actions should now be migrated to ActionRegistry.
        This method is left as a stub to prevent crashes if old actions linger,
        but it logs a warning.
        """
        self.logger.warning(f"Legacy action '{action.get('type')}' received but not handled by Registry. Ignoring.")
        return False

    def _process_financials(self, state: LaundromatState, seasonal_mods: Dict[str, float], customer_count: float) -> FinancialReport:
        """
        Generates weekly financial report using already-accumulated daily revenue.
        Customer_count is now used for COGS calculation only (weekly total).
        """
        report = FinancialReport(week=self.time_system.current_week)
        
        # 1. Use accumulated daily revenue from revenue streams
        wash_stream = state.revenue_streams.get("Standard Wash")
        dry_stream = state.revenue_streams.get("Standard Dry")
        
        # Use accumulated weekly values from daily processing
        report.revenue_wash = wash_stream.weekly_revenue if wash_stream else 0.0
        report.revenue_dry = dry_stream.weekly_revenue if dry_stream else 0.0
        
        # Get vending revenue from accumulated streams
        detergent_stream = state.revenue_streams.get("Detergent Sale")
        softener_stream = state.revenue_streams.get("Softener Sale")
        dryer_sheets_stream = state.revenue_streams.get("Dryer Sheets")
        
        if detergent_stream:
            report.revenue_vending += detergent_stream.weekly_revenue or 0.0
        if softener_stream:
            report.revenue_vending += softener_stream.weekly_revenue or 0.0
        if dryer_sheets_stream:
            report.revenue_vending += dryer_sheets_stream.weekly_revenue or 0.0

        # Other vending streams
        for name, stream in state.revenue_streams.items():
            if not stream.unlocked: continue
            if stream.category == "vending" and name not in ["Detergent Sale", "Softener Sale", "Dryer Sheets"]:
                report.revenue_vending += stream.weekly_revenue or 0.0
            elif stream.category == "premium":
                report.revenue_premium += stream.weekly_revenue or 0.0
            elif stream.category == "membership":
                report.revenue_membership += stream.weekly_revenue or 0.0
            elif stream.category == "other":
                report.revenue_other += stream.weekly_revenue or 0.0
        
        # Update State Active Customers (weekly total estimate)
        state.active_customers = int(customer_count)
        
        report.total_revenue = (report.revenue_wash + report.revenue_dry + 
                              report.revenue_vending + report.revenue_premium + 
                              report.revenue_membership + report.revenue_other)
        
        # Reset stream counters for next week AFTER using them
        for s in state.revenue_streams.values():
            s.weekly_revenue = 0.0
        
        # 2. COGS (Supplies) - estimated based on customer count
        # Inventory is already deducted daily, so this is for reporting only
        detergent_cost_unit = 0.15 
        softener_cost_unit = 0.10
        
        # Estimate weekly supply cost based on customer behavior
        # 50% of customers need soap, 30% need softener
        estimated_soap_used = customer_count * 0.5
        estimated_softener_used = customer_count * 0.3
        
        report.cogs_supplies = (estimated_soap_used * detergent_cost_unit) + (estimated_softener_used * softener_cost_unit)
        
        # COGS for vending items (dryer sheets etc)
        for stream in state.revenue_streams.values():
            if stream.category == "vending" and stream.cost_per_unit > 0:
                # Estimate 20% of customers buy vending items
                estimated_sales = customer_count * 0.2
                report.cogs_vending += estimated_sales * stream.cost_per_unit
        
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
        
        # Deduct parts from inventory
        if parts_used > 0:
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
        # (Managed by FinancialSystem/CreditSystem - interest added there? 
        # Actually existing model code added interest in loop. FinancialSystem should handle this now.
        # Removing manual loan loop here as per refactor plan to centralize.)
        # Note: Report tracks expense_interest. We need to query FinancialSystem or calculate it here.
        # Only simple interest calc for report for now.
        for loan in state.loans: # Legacy loans list? Or use CreditSystem?
             # For now, keep report estimation simple or rely on legacy list if not migrated fully.
             if loan.balance > 0:
                interest = loan.balance * (loan.interest_rate_monthly / 4.0)
                report.expense_interest += interest
                # Balance update delegated to FinancialSystem/Credit
        
        report.net_income_before_tax = report.operating_income - report.expense_interest + report.income_interest - report.fines
        
        # 5. Taxes (Quarterly Provision)
        # We calculate provision weekly for reporting, but pay quarterly
        report.tax_provision = self.economy_system.calculate_taxes(report.total_revenue, 
                                                                 report.total_operating_expenses + report.total_cogs + report.expense_interest, 
                                                                 0) # Deductions placeholder
        
        report.net_income = report.net_income_before_tax - report.tax_provision
        
        # Update State
        # Update State via Ledger (Cash Flow Basis)
        report.cash_beginning = state.balance
        
        # Revenue already added daily in _process_daily_financials
        # Do NOT add again here to avoid double-counting
        
        # Generate Bills delegated to FinancialSystem (bills are NOT auto-paid)
        
        # NOTE: COGS is Inventory usage (non-cash now), Loan Interest handled in report but cash handled in payment above.
        # Tax Provision is accrual, not cash.
        
        # state.balance += report.net_income # <-- OLD LOGIC REMOVED
        report.cash_ending = state.balance
        
        # Archive
        state.financial_reports.append(report)
        state.process_week(report.total_revenue, report.total_operating_expenses + report.total_cogs) # Legacy compat
        
        return report
