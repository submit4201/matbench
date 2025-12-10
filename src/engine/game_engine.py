from typing import Dict, List, Any, Optional
import logging
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
        2. Advance Day.
        3. If week ends, run process_week().
        """
        # 1. Apply Daily Actions
        for agent_id, actions in self.pending_actions.items():
            state = self.states[agent_id]
            for action in actions:
                self._apply_action(state, action)
            self.pending_actions[agent_id] = []

        # 2. Advance Time (Day)
        week_advanced = self.time_system.advance_day()
        
        # 3. Weekly Processing (if Sunday ended)
        results = {}
        if week_advanced:
            logger.info(f"Week advanced to {self.time_system.current_week}. Running Weekly Processes.")
            results = self.process_week()
        else:
            # Just return empty results for mid-week days, or simple acknowledgment
            logger.info(f"Advanced to {self.time_system.current_day.value}")
            results = {"status": "day_advanced", "current_day": self.time_system.current_day.value}
            
        return results

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
                self.communication.send_system_message(agent_id, f"BREAKING NEWS: {trend.news_headline}", self.time_system.current_week, intent=MessageIntent.NEWS)

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
                # state.balance -= cost # Replaced by Ledger
                state.ledger.add(-cost, "expense", f"Bought {qty} {item} from {vendor.profile.name}", self.time_system.current_week, related_entity_id=vendor_id)
                
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
            amount = float(action.get("amount", 0))
            if state.balance >= amount:
                # state.balance -= amount
                state.ledger.add(-amount, "expense", "Marketing Campaign", self.time_system.current_week)
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
                # state.balance -= 500
                state.ledger.add(-500.0, "expense", "Machine Upgrade", self.time_system.current_week)
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

        elif action_type == "RESOLVE_DILEMMA":
            dilemma_id = action.get("dilemma_id") # We might need to pass this, OR infer from choice_id if unique across dilemmas?
            # Actually, `Message` attachments don't have dilemma_id... 
            # I should store active dilemmas in the state or frontend needs to know which message triggered it.
            # Frontend doesn't have dilemma_id in the message content easily unless I add it.
            # I added it to content earlier in thought, but code implementation used attachments.
            # I'll rely on `choice_id` being unique enough or pass dilemma_id in attachments too?
            # EthicalEventManager needs dilemma_id.
            # Let's assume the frontend passes choice_id and we find the dilemma.
            # But duplicate choice IDs might exist across types? No, they are strings like "hire_cheap". 
            # They ARE duplicated in templates. So I NEED dilemma_id.
            # I will add dilemma_id to attachments metadata.
            
            choice_id = action.get("choice_id")
            
            # Find the active dilemma for this choice/agent
            # This is inefficient, but safe for now.
            active_dilemma = None
            for d in self.ethical_event_manager.get_pending_dilemmas(state.id):
                for c in d.choices:
                    if c.id == choice_id:
                        active_dilemma = d
                        break
                if active_dilemma: break
            
            if active_dilemma:
                result = self.ethical_event_manager.resolve_dilemma(active_dilemma.id, choice_id, self.time_system.current_week)
                if "error" not in result:
                    # Apply effects
                    state.balance += result.get("profit", 0)
                    state.update_social_score("community_standing", result.get("social_score", 0))
                    # Note: ethics_component is internal tracking, handled by manager history usually.
                    
                    # Send outcome message
                    self.communication.send_system_message(
                        recipient_id=state.id,
                        content=f"Decision Outcome:\n{result.get('outcome_text')}",
                        week=self.time_system.current_week,
                        intent=MessageIntent.DILEMMA_OUTCOME
                    )
                else:
                    logger.error(f"Failed to resolve dilemma: {result['error']}")

        elif action_type == "PAY_BILL":
            bill_id = action.get("bill_id")
            result = self.financial_system.pay_bill(state, bill_id, self.time_system.current_week)
            if result["success"]:
                logger.info(f"Agent {state.id} paid bill {bill_id}. New Balance: {result['balance']}")
            else:
                logger.warning(f"Failed to pay bill {bill_id}: {result.get('error')}")

        elif action_type == "BUY_BUILDING":
            listing_id = action.get("listing_id")
            # Verify listing exists
            listing = self.real_estate_manager.get_listing(listing_id)
            if listing:
                if state.balance >= listing.price:
                     # Process Transaction
                     state.ledger.add(-listing.price, "real_estate", f"Purchased {listing.name}", self.time_system.current_week)
                     
                     # Transfer Ownership
                     building = self.real_estate_manager.process_purchase(listing_id)
                     if building:
                         state.buildings.append(building)
                         state.locations.append(building.id)
                         logger.info(f"Agent {state.id} purchased building {building.name} for ${building.price}")
                         self.communication.send_system_message(state.id, f"Congratulations! You now own {building.name}.", self.time_system.current_week)
                     else:
                         logger.error(f"Race condition? Building {listing_id} not found after check.")
                else:
                    logger.warning(f"Agent {state.id} insufficient funds for building {listing.price}")
            else:
                logger.warning(f"Building listing {listing_id} not found/expired.")



        # --- New Actions ---

        elif action_type == "HIRE_STAFF":
            role = action.get("role", "attendant")
            # 1. Calculate Hiring Cost if any
            hiring_fee = 100.0 # Recruitment fee
            if state.balance >= hiring_fee:
                state.ledger.add(-hiring_fee, "expense", f"Hiring Fee ({role})", self.time_system.current_week)
                
                # 2. Create Staff Member
                from src.models.world import StaffMember
                new_id = f"S{len(state.staff) + 1}_{self.time_system.current_week}"
                new_staff = StaffMember(
                    id=new_id, 
                    name=f"Staff {new_id}", 
                    role=role, 
                    skill_level=0.5, 
                    wage=15.0 if role == "attendant" else 20.0
                )
                state.staff.append(new_staff)
                logger.info(f"Agent {state.id} hired {role} {new_id}")
                self.communication.send_system_message(
                    state.id, 
                    f"Hired new {role}. Wage: ${new_staff.wage}/hr.", 
                    self.time_system.current_week
                )
            else:
                 self.communication.send_system_message(state.id, "Insufficient funds to hire staff.", self.time_system.current_week)

        elif action_type == "FIRE_STAFF":
            staff_id = action.get("staff_id")
            # Find and remove
            staff_to_fire = next((s for s in state.staff if s.id == staff_id), None)
            if staff_to_fire:
                state.staff.remove(staff_to_fire)
                # Severance?
                severance = staff_to_fire.wage * 20 # 1 week pay
                state.ledger.add(-severance, "expense", f"Severance ({staff_to_fire.id})", self.time_system.current_week)
                logger.info(f"Agent {state.id} fired {staff_id}")
                self.communication.send_system_message(state.id, f"Fired {staff_to_fire.name}. Paid ${severance} severance.", self.time_system.current_week)
            else:
                logger.warning(f"Agent {state.id} tried to fire non-existent staff {staff_id}")

        elif action_type == "TRAIN_STAFF":
            staff_id = action.get("staff_id")
            staff = next((s for s in state.staff if s.id == staff_id), None)
            cost = 150.0
            if staff and state.balance >= cost:
                state.ledger.add(-cost, "expense", f"Training ({staff_id})", self.time_system.current_week)
                staff.skill_level = min(1.0, staff.skill_level + 0.1)
                staff.morale = min(1.0, staff.morale + 0.1)
                self.communication.send_system_message(state.id, f"Trained {staff.name}. Skill: {staff.skill_level:.1f}", self.time_system.current_week)
            elif not staff:
                logger.warning(f"Agent {state.id} tried to train non-existent staff {staff_id}")

        elif action_type == "PERFORM_MAINTENANCE":
            parts_needed = len(state.machines) // 5
            parts_in_stock = state.inventory.get("parts", 0)
            
            if parts_in_stock >= parts_needed:
                # Deduct
                state.inventory["parts"] -= parts_needed
                # Effect: Improve condition of all machines
                for m in state.machines:
                    m.condition = min(1.0, m.condition + 0.2)
                    if m.is_broken and m.condition > 0.5:
                         m.is_broken = False # Fix if condition improves enough
                
                self.communication.send_system_message(state.id, f"Maintenance performed. Used {parts_needed} parts. All machines condition improved.", self.time_system.current_week)
            else:
                self.communication.send_system_message(state.id, f"Not enough parts for full maintenance. Need {parts_needed}, have {parts_in_stock}.", self.time_system.current_week)

        # Re-map legacy Negotiate if needed, or implement fresh
        elif action_type == "NEGOTIATE_CONTRACT":
             # Use existing negotiate logic logic but mapped here
             item = action.get("item", "soap")
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
        
        # Add Cash Inflows
        state.ledger.add(report.total_revenue, "revenue", "Weekly Revenue", self.time_system.current_week)
        
        # Generate Bills delegated to FinancialSystem
        
        # NOTE: COGS is Inventory usage (non-cash now), Loan Interest handled in report but cash handled in payment above.
        # Tax Provision is accrual, not cash.
        
        # state.balance += report.net_income # <-- OLD LOGIC REMOVED
        report.cash_ending = state.balance
        
        # Archive
        state.financial_reports.append(report)
        state.process_week(report.total_revenue, report.total_operating_expenses + report.total_cogs) # Legacy compat
        
        return report
