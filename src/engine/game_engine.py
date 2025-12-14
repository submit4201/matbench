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
from src.engine.core.event_bus import EventBus
from src.engine.projections.state_builder import StateBuilder
from src.engine.actions.registry import ActionRegistry
from src.models.events.finance import DailyRevenueProcessed, BillGenerated, WeeklySpendingReset, WeeklyReportGenerated
from src.models.events.operations import MachineWearUpdated, MarketingBoostDecayed, CleanlinessUpdated
from src.models.events.social import ReputationChanged
from src.models.events.commerce import ShipmentReceived
import copy
# Load handlers modules to register them
import src.engine.actions.handlers 
from src.engine.reactions.communication import CommunicationReactions 
from src.engine.reactions.notifications import NotificationReactions 

# Utility cost constants per load
STANDARD_WATER_COST_PER_LOAD = 0.15
STANDARD_ELECTRICITY_COST_PER_LOAD = 0.20
ECO_WATER_COST_PER_LOAD = 0.08
ECO_ELECTRICITY_COST_PER_LOAD = 0.12
DRYER_GAS_COST_PER_LOAD = 0.10
DRYER_ELECTRICITY_COST_PER_LOAD = 0.25

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
        
        # For Phase 1 transition, I will keep 'self.states' but manage it via events.
        
        self.event_bus = EventBus()
        self.event_repo = EventRepository(event_bus=self.event_bus)
        
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
        self.financial_system = FinancialSystem(agent_ids)
        self.real_estate_manager = RealEstateManager()
        self.vendor_manager = VendorManager() # Init first
        
        # Initialize Reactions
        self.comm_reactions = CommunicationReactions(self.communication)
        self.comm_reactions.register(self.event_bus)
        
        self.notification_reactions = NotificationReactions(self.communication)
        self.notification_reactions.register(self.event_bus)
        
        from src.engine.reactions.commerce import CommerceReactions
        self.commerce_reactions = CommerceReactions(self.vendor_manager)
        self.commerce_reactions.register(self.event_bus, communication_system=self.communication, calendar_system=None) 
        
        from src.engine.reactions.finance import FinanceReactions
        self.finance_reactions = FinanceReactions(self.event_bus, self.financial_system.credit_system, self.communication)
        
        self.trust_system = TrustSystem(agent_ids)
        self.merger_system = MergerSystem() 
        self.proposal_manager = ProposalManager(self)
        self.metrics_auditor = MetricsAuditor()


        
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
            self.logger.error(f"Unknown agent {agent_id} tried to submit action.")
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
                self.apply_action(state, action)
            self.pending_actions[agent_id] = []

        # 2. Process Daily Financials for each agent (single-pass per-agent)
        seasonal_mods = self.time_system.get_seasonal_modifier()
        daily_results = {}
        
        for agent_id, state in self.states.items():
            try:
                daily_results[agent_id] = self._run_daily_financials(agent_id, state, seasonal_mods)
            except Exception as e:
                self.logger.error(f"Failed daily processing for {agent_id}: {e}")
                daily_results[agent_id] = {"error": str(e)}

        # 3. Advance Time (Day)
        week_advanced = self.time_system.advance_day()
        
        # 4. Weekly Processing (if Sunday ended) - bills, taxes, events, etc.
        results = {}
        if week_advanced:
            self.logger.info(f"Week advanced to {self.time_system.current_week}. Running Weekly Processes.")
            results = self.process_week()
            results["daily"] = daily_results
        else:
            self.logger.info(f"Advanced to {self.time_system.current_day.value}")
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
        soap_sold = 0  # Ensure soap_sold is always defined
        
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
            water_cost_per_load = STANDARD_WATER_COST_PER_LOAD
            electricity_cost_per_load = STANDARD_ELECTRICITY_COST_PER_LOAD
            if "eco" in machine.type:
                water_cost_per_load = ECO_WATER_COST_PER_LOAD
                electricity_cost_per_load = ECO_ELECTRICITY_COST_PER_LOAD
            
            daily_utility_cost += loads * (water_cost_per_load + electricity_cost_per_load)
            
        # Dryer Utility (Gas/Elec) - Link to wash loads?
        # Assume 1 dryer load per wash load roughly
        dryer_loads = customer_count 
        daily_utility_cost += dryer_loads * (DRYER_GAS_COST_PER_LOAD + DRYER_ELECTRICITY_COST_PER_LOAD)
        
        # Supply Cost Calculation (COGS)
        daily_supply_cost = 0.0
        # Detergent
        if soap_sold > 0:
            daily_supply_cost += soap_sold * 0.15  # Unit cost
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
            self.logger.info(f"Market Trend: {trend.news_headline}")
            # Broadcast news
            for agent_id in self.agent_ids:
                self.communication.send_system_message(agent_id, f"BREAKING NEWS: {trend.news_headline}", self.time_system.current_week, intent=MessageIntent.ANNOUNCEMENT)

        # 1.5 Process Pending Deliveries via Events
        delivery_events = []
        for agent_id, state in self.states.items():
            if hasattr(state, "pending_deliveries"):
                arrived = []
                remaining = []
                for delivery in state.pending_deliveries:
                    if delivery["arrival_week"] <= self.time_system.current_week:
                        arrived.append(delivery)
                    else:
                        remaining.append(delivery)
                
                # Emit events for arrived deliveries
                for delivery in arrived:
                    event = ShipmentReceived(
                        week=self.time_system.current_week,
                        agent_id=agent_id,
                        order_id=delivery.get("order_id", delivery.get("id", "unknown")),
                        items_received={delivery["item"]: delivery["quantity"]}
                    )
                    delivery_events.append(event)
                    
                    # Notify (side effect - OK for now)
                    self.communication.send_system_message(
                        recipient_id=agent_id,
                        content=f"Delivery of {delivery['quantity']} {delivery['item']} from {delivery.get('vendor_name', 'supplier')} has arrived.",
                        week=self.time_system.current_week
                    )
                
                # Emit DeliveryListUpdated event (replaces direct mutation)
                from src.models.events.commerce import DeliveryListUpdated
                delivery_events.append(DeliveryListUpdated(
                    week=self.time_system.current_week,
                    agent_id=agent_id,
                    remaining_deliveries=remaining
                ))
        
        # Save & Apply delivery events
        if delivery_events:
            self.event_repo.save_batch(delivery_events)
            for event in delivery_events:
                StateBuilder.apply_event(self.states[event.agent_id], event)


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

                # --- Cleanliness Decay ---
                base_decay = 0.05  # 5% natural decay per week
                staff_effects = self._calculate_staff_effects(state)
                cleaner_boost = staff_effects.get("cleanliness_boost", 0.0)
                current_cleanliness = state.primary_location.cleanliness
                new_cleanliness = max(0.0, min(1.0, current_cleanliness - base_decay + cleaner_boost))
                
                if new_cleanliness != current_cleanliness:
                    cleanliness_event = CleanlinessUpdated(
                        week=self.time_system.current_week,
                        agent_id=agent_id,
                        new_cleanliness=new_cleanliness,
                        delta=new_cleanliness - current_cleanliness,
                        reason="weekly_decay_with_staff"
                    )
                    weekly_events.append(cleanliness_event)

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

                # --- Generate Bills from Accumulated Weekly Spending ---
                weekly_spending = getattr(state.primary_location, 'weekly_spending', {})
                util_total = weekly_spending.get("utility", 0.0)
                supply_total = weekly_spending.get("supplies", 0.0)
                
                if util_total > 0:
                    util_bill_event = BillGenerated(
                        week=self.time_system.current_week,
                        agent_id=state.id,
                        bill_id=f"utility_{self.time_system.current_week}_{state.id}",
                        bill_type="Utility",
                        amount=util_total,
                        due_week=self.time_system.current_week + 1
                    )
                    weekly_events.append(util_bill_event)
                
                if supply_total > 0:
                    supply_bill_event = BillGenerated(
                        week=self.time_system.current_week,
                        agent_id=state.id,
                        bill_id=f"supplies_{self.time_system.current_week}_{state.id}",
                        bill_type="Supplies",
                        amount=supply_total,
                        due_week=self.time_system.current_week + 1
                    )
                    weekly_events.append(supply_bill_event)
                
                # Reset accumulators
                if util_total > 0 or supply_total > 0:
                    reset_event = WeeklySpendingReset(
                        week=self.time_system.current_week,
                        agent_id=state.id,
                        utility_total=util_total,
                        supply_total=supply_total
                    )
                    weekly_events.append(reset_event)

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

                # --- Financial Report Generation ---
                customer_count_est = state.active_customers * 7  # Rough weekly estimate
                
                # Compute FinancialReport (single source of truth)
                financial_report = self._process_financials(state, seasonal_mods, customer_count_est)
                
                # Create event from report (using helper for single mapping)
                report_event = self._build_weekly_report_event(state, financial_report)
                weekly_events.append(report_event)
                
                # Financial System Orchestration (uses data from event)
                # Note: We need to reconstruct FinancialReport for FinancialSystem here
                # until FinancialSystem is also refactored to use events
                financial_report = self._financial_report_from_event(report_event)
                self.financial_system.process_week(state, self.time_system.current_week, financial_report)
                
                results[agent_id] = {
                    "revenue": round(financial_report.total_revenue, 2),
                    "expenses": round(financial_report.total_operating_expenses + financial_report.total_cogs, 2),
                    "profit": round(financial_report.net_income, 2),
                    "customers": round(state.active_customers),
                    "new_balance": round(state.balance, 2)
                }
            except Exception as e:
                self.logger.error(f"Failed to process turn for agent {agent_id}: {e}", exc_info=True)
                results[agent_id] = {"error": str(e), "customers": 0, "revenue": 0}
        
        # 3. Save & Apply Weekly Events
        if weekly_events:
            self.event_repo.save_batch(weekly_events)
            # Group events by agent_id for batch application
            events_by_agent = {}
            for event in weekly_events:
                events_by_agent.setdefault(event.agent_id, []).append(event)
            for agent_id, events in events_by_agent.items():
                StateBuilder.apply_events(self.states[agent_id], events)

        # 5.5 Record Metrics (Audit)
        self.metrics_auditor.record_weekly_state(self.time_system.current_week, self.states)

        self.logger.info(f"Processed logic for Week {self.time_system.current_week}")
        
        return results

    def apply_action(self, state: LaundromatState, action: Dict[str, Any]):
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
            self.logger.warning(f"Action '{action_type}' received but not handled by Registry.")
            return False
            
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


    def _process_financials(self, state: LaundromatState, seasonal_mods: Dict[str, float], customer_count: float) -> FinancialReport:
        """
        Generates weekly financial report as a domain object (read-only, no state mutation).
        Returns: FinancialReport (single source of truth for financial calculations)
        """
        report = FinancialReport(week=self.time_system.current_week)
        
        # 1. Revenue from accumulated daily streams (READ ONLY)
        wash_stream = state.revenue_streams.get("Standard Wash")
        dry_stream = state.revenue_streams.get("Standard Dry")
        
        report.revenue_wash = wash_stream.weekly_revenue if wash_stream else 0.0
        report.revenue_dry = dry_stream.weekly_revenue if dry_stream else 0.0
        
        # Vending revenue from accumulated streams
        detergent_stream = state.revenue_streams.get("Detergent Sale")
        softener_stream = state.revenue_streams.get("Softener Sale")
        dryer_sheets_stream = state.revenue_streams.get("Dryer Sheets")
        
        report.revenue_vending = 0.0
        if detergent_stream:
            report.revenue_vending += detergent_stream.weekly_revenue or 0.0
        if softener_stream:
            report.revenue_vending += softener_stream.weekly_revenue or 0.0
        if dryer_sheets_stream:
            report.revenue_vending += dryer_sheets_stream.weekly_revenue or 0.0

        # Other revenue streams
        report.revenue_premium = 0.0
        report.revenue_membership = 0.0
        report.revenue_other = 0.0
        for name, stream in state.revenue_streams.items():
            if not stream.unlocked:
                continue
            if stream.category == "vending" and name not in ["Detergent Sale", "Softener Sale", "Dryer Sheets"]:
                report.revenue_vending += stream.weekly_revenue or 0.0
            elif stream.category == "premium":
                report.revenue_premium += stream.weekly_revenue or 0.0
            elif stream.category == "membership":
                report.revenue_membership += stream.weekly_revenue or 0.0
            elif stream.category == "other":
                report.revenue_other += stream.weekly_revenue or 0.0
        
        report.total_revenue = (report.revenue_wash + report.revenue_dry + report.revenue_vending + 
                               report.revenue_premium + report.revenue_membership + report.revenue_other)
        
        # 2. COGS (Supplies) - estimated based on customer count
        detergent_cost_unit = 0.15 
        softener_cost_unit = 0.10
        
        estimated_soap_used = customer_count * 0.5
        estimated_softener_used = customer_count * 0.3
        
        report.cogs_supplies = (estimated_soap_used * detergent_cost_unit) + (estimated_softener_used * softener_cost_unit)
        
        report.cogs_vending = 0.0
        for stream in state.revenue_streams.values():
            if stream.category == "vending" and stream.cost_per_unit > 0:
                estimated_sales = customer_count * 0.2
                report.cogs_vending += estimated_sales * stream.cost_per_unit
        
        report.total_cogs = report.cogs_supplies + report.cogs_vending
        report.gross_profit = report.total_revenue - report.total_cogs
        
        # 3. Operating Expenses
        report.expense_rent = 250.0
        
        # Utilities
        water_cost = customer_count * 0.15
        elec_cost = customer_count * (0.20 + 0.25)
        gas_cost = customer_count * 0.10
        report.expense_utilities = (water_cost + elec_cost + gas_cost) * seasonal_mods.get("heating_cost", 1.0)
        
        # Labor
        report.expense_labor = sum(staff.wage * 20 for staff in state.staff)
        
        # Maintenance - calculate parts to use (NO MUTATION HERE)
        parts_needed = max(1, int(len(state.machines) / 10))
        parts_available = state.inventory.get("parts", 0)
        report.parts_used = min(parts_needed, parts_available)
        
        base_maintenance_cost = 20.0 * len(state.machines)
        if report.parts_used < parts_needed:
            base_maintenance_cost *= 1.5
            self.logger.info(f"Agent {state.id} missing parts for maintenance! Cost penalty applied.")
            
        report.expense_maintenance = base_maintenance_cost
        report.expense_insurance = 37.5
        report.expense_other = 25.0
        
        # Note: No state mutation occurs here. This function returns an event describing the financials;
        # the actual ledger update happens in the event handler, not in this processing function.
        report.total_operating_expenses = (report.expense_rent + report.expense_utilities + report.expense_labor + 
                                           report.expense_maintenance + report.expense_insurance + report.expense_other)
        
        report.operating_income = report.gross_profit - report.total_operating_expenses
        
        # 4. Loans & Interest (READ ONLY)
        report.expense_interest = 0.0
        for loan in state.loans:
            if loan.balance > 0:
                interest = loan.balance * (loan.interest_rate_monthly / 4.0)
                report.expense_interest += interest
        
        report.net_income_before_tax = report.operating_income - report.expense_interest
        
        # 5. Taxes
        report.tax_provision = self.economy_system.calculate_taxes(
            report.total_revenue, 
            report.total_operating_expenses + report.total_cogs + report.expense_interest, 
            0
        )
        
        report.net_income = report.net_income_before_tax - report.tax_provision
        
        # Cash (READ ONLY)
        report.cash_beginning = state.balance
        report.cash_ending = state.balance  # No changes until events apply
        
        # Customer count for handler
        report.active_customers = int(customer_count)
        
        return report

    # ═══════════════════════════════════════════════════════════════════════
    # HELPER METHODS FOR ORCHESTRATION
    # ═══════════════════════════════════════════════════════════════════════
    
    def _run_daily_financials(
        self, 
        agent_id: str, 
        state: LaundromatState, 
        seasonal_mods: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Process daily financials for a single agent.
        Computes event, persists, applies, and returns response dict.
        """
        event = self._process_daily_financials(state, seasonal_mods)
        
        # Persist + apply immediately
        self.event_repo.save_batch([event])
        StateBuilder.apply_event(state, event)
        
        # Build response from event + updated state
        return {
            "customers": event.customer_count,
            "revenue": round(event.revenue_wash + event.revenue_dry + event.revenue_vending, 2),
            "day": self.time_system.current_day.value,
            "new_balance": round(state.balance, 2),
        }
    
    def _build_weekly_report_event(
        self, 
        state: LaundromatState, 
        report: FinancialReport
    ) -> WeeklyReportGenerated:
        """
        Create WeeklyReportGenerated event from FinancialReport.
        Single mapping location to reduce duplication.
        """
        return WeeklyReportGenerated(
            week=self.time_system.current_week,
            agent_id=state.id,
            revenue_wash=report.revenue_wash,
            revenue_dry=report.revenue_dry,
            revenue_vending=report.revenue_vending,
            revenue_premium=report.revenue_premium,
            revenue_membership=report.revenue_membership,
            revenue_other=report.revenue_other,
            total_revenue=report.total_revenue,
            cogs_supplies=report.cogs_supplies,
            cogs_vending=report.cogs_vending,
            total_cogs=report.total_cogs,
            gross_profit=report.gross_profit,
            expense_rent=report.expense_rent,
            expense_utilities=report.expense_utilities,
            expense_labor=report.expense_labor,
            expense_maintenance=report.expense_maintenance,
            expense_insurance=report.expense_insurance,
            expense_other=report.expense_other,
            total_operating_expenses=report.total_operating_expenses,
            operating_income=report.operating_income,
            expense_interest=report.expense_interest,
            net_income_before_tax=report.net_income_before_tax,
            tax_provision=report.tax_provision,
            net_income=report.net_income,
            cash_beginning=report.cash_beginning,
            cash_ending=report.cash_ending,
            active_customers=report.active_customers,
            parts_used=report.parts_used
        )
