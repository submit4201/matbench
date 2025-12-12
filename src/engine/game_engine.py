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
            customer_count=int(customer_count)
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
        
        # 0. Update Market Trends
        self.economy_system.update_trends(self.time_system.current_week)
        trend = self.economy_system.active_trend
        if trend and trend.week == self.time_system.current_week:
            logger.info(f"Market Trend: {trend.news_headline}")
            # Broadcast news
            for agent_id in self.agent_ids:
                self.communication.send_system_message(agent_id, f"BREAKING NEWS: {trend.news_headline}", self.time_system.current_week, intent=MessageIntent.ANNOUNCEMENT)

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
                        self.communication.send_system_message(
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
                # Calculate Staff Bonuses
                staff_effects = self._calculate_staff_effects(state)

                # Apply Cleanliness (Decayed by traffic, boosted by staff)
                # Traffic decay placeholder: -0.1 per 100 customers?
                # For now just set base Cleanliness + Staff Boost
                base_clean = 0.5
                state.cleanliness = min(1.0, base_clean + staff_effects["cleanliness_boost"])

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
                
                # Apply Demand Multiplier (Events + Market Trend)
                raw_demand *= effects["demand_multiplier"]
                if trend and trend.demand_shift != 1.0:
                     raw_demand *= trend.demand_shift

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
                    # Boosted by Attendants
                    service_quality = 1.0 + staff_effects["service_boost"]
                    service_boost = (customer_count / 200.0) * 1.5 * service_quality
                    
                    state.update_social_score("customer_satisfaction", service_boost)
                    logger.info(f"Agent {agent_id}: Customer service boost +{service_boost:.1f} for {customer_count:.0f} customers (Quality: {service_quality:.2f})")
                
                # 1.5 Ethical Dilemmas
                # Trigger a dilemma if conditions are met
                dilemma_context = {
                    "balance": state.balance,
                    "reputation": state.reputation,
                    "customer_count": customer_count
                }
                dilemma = self.ethical_event_manager.check_for_dilemmas(self.time_system.current_week, agent_id, dilemma_context)
                if dilemma:
                    # Notify agent via Message
                    logger.info(f"Triggered Dilemma {dilemma.id} for {agent_id}")
                    
                    # Serialize choices for frontend buttons
                    choices_data = [
                        {
                            "id": c.id,
                            "label": c.label,
                            "description": c.description,
                            "risk": c.risk_description if c.risk_factor > 0 else None
                        } for c in dilemma.choices
                    ]
                    
                    self.communication.send_system_message(
                        recipient_id=agent_id,
                        content=f"{dilemma.description}",
                        week=self.time_system.current_week,
                        intent=MessageIntent.DILEMMA,
                        attachments=choices_data
                    )

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
                    # Cleanliness bonus also applied here
                    bonus = 1.0 + (1.0 if state.cleanliness > 0.8 else 0.0)
                    state.update_social_score("customer_satisfaction", bonus)
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
                
                # Financial System Orchestration (Bills, Credit, Tax)
                self.financial_system.process_week(state, self.time_system.current_week, financial_report)
                
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
        
        # 5.5 Record Metrics (Audit)
        self.metrics_auditor.record_weekly_state(self.time_system.current_week, self.states)

        # 6. Advance Time - REMOVED (Controlled by Server/Loop)
        # self.time_system.advance_week()
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
             vendor_id = action.get("vendor_id", "bulkwash")
             # ... Call inner logic akin to existing 'NEGOTIATE' handling or redirect
             # Let's simple redirect to the 'NEGOTIATE' block existing above?
             # Or duplicate logic for clarity. It essentially calls vendor.negotiate_price
             vendor = self.vendor_manager.get_vendor(vendor_id)
             if vendor:
                social_score = state.social_score.total_score
                result = vendor.negotiate_price(item, state.name, social_score, agent_id=state.id)
                self.communication.send_message(vendor.profile.name, state.id, result["message"], self.time_system.current_week)
                if result["success"]:
                    logger.info(f"Agent {state.id} negotiated {item} with {vendor_id}")
             else:
                 self.communication.send_system_message(state.id, f"Vendor {vendor_id} not found.", self.time_system.current_week)

        elif action_type == "INSPECT_VENDOR":
             vendor_id = action.get("vendor_id")
             vendor = self.vendor_manager.get_vendor(vendor_id)
             if vendor:
                 catalog_str = json.dumps(vendor.catalog, indent=2)
                 self.communication.send_system_message(state.id, f"Vendor {vendor_id} Catalog:\n{catalog_str}", self.time_system.current_week)
             else:
                 self.communication.send_system_message(state.id, f"Vendor {vendor_id} not found.", self.time_system.current_week)

        elif action_type == "INSPECT_DELIVERIES":
             pending = state.pending_deliveries
             msg = f"Pending Deliveries: {json.dumps(pending, indent=2)}" if pending else "No pending deliveries."
             self.communication.send_system_message(state.id, msg, self.time_system.current_week)

        elif action_type == "GET_FINANCIAL_REPORT":
             # Get last report
             if state.financial_reports:
                 last_report = state.financial_reports[-1]
                 # Convert to readable string
                 msg = f"Last Week Report (Week {last_report.week}):\nRevenue: ${last_report.total_revenue:.2f}\nExpenses: ${last_report.total_operating_expenses:.2f}\nNet Income: ${last_report.net_income:.2f}\nCash: ${last_report.cash_ending:.2f}"
                 self.communication.send_system_message(state.id, msg, self.time_system.current_week)
             else:
                 self.communication.send_system_message(state.id, "No financial reports generated yet.", self.time_system.current_week)

        elif action_type == "CHECK_CREDIT_SCORE":
             # Query financial system
             score = self.financial_system.get_credit_score_summary(state.id)
             self.communication.send_system_message(state.id, f"Credit Audit:\n{json.dumps(score, indent=2)}", self.time_system.current_week)

        # --- Final Gaps Logic ---

        elif action_type == "EMERGENCY_REPAIR":
            machine_id = action.get("machine_id")
            machine = next((m for m in state.machines if m.id == machine_id), None)
            if machine:
                cost = 250.0 # High cost for emergency service
                if state.balance >= cost:
                    state.ledger.add(-cost, "maintenance", f"Emergency Repair ({machine_id})", self.time_system.current_week)
                    machine.is_broken = False
                    machine.condition = 1.0 # Fully restored
                    self.communication.send_system_message(state.id, f"Emergency repair complete for {machine_id}. Cost: ${cost}", self.time_system.current_week)
                    logger.info(f"Agent {state.id} used emergency repair on {machine_id}")
                else:
                    self.communication.send_system_message(state.id, "Insufficient funds for emergency repair ($250).", self.time_system.current_week)
            else:
                 self.communication.send_system_message(state.id, f"Machine {machine_id} not found.", self.time_system.current_week)

        elif action_type == "CHECK_REGULATIONS":
            # Mock Regulatory Body response
            # In future: self.regulatory_system.get_status(state.id)
            reg_status = "Active Regulations: Environmental Compliance (Active). No pending fines. Compliance Score: 100%."
            self.communication.send_system_message(state.id, reg_status, self.time_system.current_week)

        elif action_type == "CHECK_REPUTATION":
            # Breakdown of Social Score
            # In future: self.social_system.get_detailed_score(state.id)
            breakdown = f"Reputation Audit:\nTotal: {state.social_score.total_score:.1f}\n- Community: {state.social_score.community_trust:.1f}\n- Eco: {state.social_score.eco_rating:.1f}\n- Labor: {state.social_score.labor_practices:.1f}"
            self.communication.send_system_message(state.id, breakdown, self.time_system.current_week)

        elif action_type == "INSPECT_PUBLIC_RECORDS":
            target_id = action.get("entity_id", "global")
            # Mock Records
            if target_id == "global" or not target_id:
                 msg = "Public Records: No major incidents reported in the district."
            else:
                 msg = f"Public Records ({target_id}): Clean record. Licensed operator since 2024."
            self.communication.send_system_message(state.id, msg, self.time_system.current_week)

        elif action_type == "CHECK_MARKET_TRENDS":
            report = self.economy_system.get_market_report()
            msg = f"Market Report (Week {self.time_system.current_week}):\n" \
                  f"Headline: {report['headline']}\n" \
                  f"Status: {report['status']}\n" \
                  f"Impact: {report.get('impact_resource', 'None')} " \
                  f"(Price x{report.get('price_factor', 1.0)}, Demand x{report.get('demand_factor', 1.0)})"
            self.communication.send_system_message(state.id, msg, self.time_system.current_week)

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
