# [ ]↔T: Enhanced Game Engine with New Systems
#   - [x] Wraps existing GameEngine
#   - [x] Adds Game Master integration
#   - [x] Adds Credit System
#   - [x] Adds Calendar Manager  
#   - [x] Adds Neighborhood System
#   - [x] Adds Ethical Events
# PRIORITY: P1 - Core integration layer
# STATUS: Complete

"""
Enhanced Game Engine

This module extends the base GameEngine with advanced features:
- LLM Game Master for dynamic events
- Credit/FICO scoring system with SBA loans
- Calendar and scheduling for strategic planning
- Neighborhood zones
- Ethical dilemma evaluation

Usage:
    engine = EnhancedGameEngine(['p1', 'ai1', 'ai2'])
    engine.process_turn()  # All new systems integrated
"""

from typing import Dict, List, Any, Optional
import logging
from src.engine.game_engine import GameEngine
from src.engine.core.game_master import GameMaster
from src.engine.finance import CreditSystem
from src.engine.core.calendar import CalendarManager
from src.engine.social.neighborhood import NeighborhoodSystem
from src.engine.social.ethical_events import EthicalEventManager

logger = logging.getLogger(__name__)


class EnhancedGameEngine:
    """
    Enhanced Game Engine that composes the base GameEngine with new systems.
    
    This approach maintains backward compatibility while adding:
    - LLM Game Master
    - Credit/FICO System (via FinancialSystem)
    - Calendar/Scheduling
    - Neighborhood Zones
    - Ethical Events
    """
    
    def __init__(self, agent_ids: List[str], llm_provider: str = "azure"):
        self.engine = GameEngine(agent_ids)
        self.agent_ids = agent_ids
        
        # New Systems
        self.game_master = GameMaster(self.engine)  # Pass engine reference
        
        # Financial System is now in GameEngine, but we can expose it
        self.financial_system = self.engine.financial_system
        # self.credit_system = CreditSystem(agent_ids) # DEPRECATED: Use financial_system.credit_system
        
        self.calendar_manager = CalendarManager(agent_ids)
        self.neighborhood = NeighborhoodSystem(agent_ids)
        self.ethical_manager = EthicalEventManager()
        
        # Forward common attributes
        # Forwarding is handled by properties or __getattr__
        # self.states = self.engine.states
        # self.time_system = self.engine.time_system
        # self.economy_system = self.engine.economy_system
        # self.vendor_manager = self.engine.vendor_manager
        # self.proposal_manager = self.engine.proposal_manager
        # self.communication = self.engine.communication
        # self.trust_system = self.engine.trust_system
        
        # Track current day
        self.current_day = 1  # 1-7 (Mon-Sun)
        
        # Initialize each agent with new systems
        for agent_id in agent_ids:
            self._initialize_agent(agent_id)
        
        logger.info("EnhancedGameEngine initialized with all new systems")
    
    def _initialize_agent(self, agent_id: str):
        """Initialize an agent with credit, zone, and calendar."""
        # Credit system - SBA loan starting condition
        credit_info = self.financial_system.credit_system.initialize_agent(agent_id, starting_week=1)
        
        # Update starting balance from loan proceeds
        state = self.engine.states[agent_id]
        state.balance = credit_info["sba_loan_amount"]
        
        # Assign zone location
        zone = self.neighborhood.assign_random_location(agent_id)
        logger.info(f"Agent {agent_id}: Zone={zone.value}, SBA Loan=${credit_info['sba_loan_amount']}")
        
        # Sync payment schedule to calendar
        self.calendar_manager.sync_credit_payments(
            agent_id, 
            self.financial_system.credit_system, 
            current_week=1
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # DELEGATE CORE METHODS TO BASE ENGINE
    # ═══════════════════════════════════════════════════════════════════════
    
    @property
    def states(self):
        return self.engine.states
    
    @property
    def time_system(self):
        return self.engine.time_system
    
    @property
    def communication(self):
        return self.engine.communication
    
    @property
    def event_manager(self):
        return self.engine.event_manager
    
    @property
    def vendor_manager(self):
        return self.engine.vendor_manager
    
    @property
    def trust_system(self):
        return self.engine.trust_system
    
    def get_state(self, agent_id: str):
        return self.engine.get_state(agent_id)
    
    def get_public_state(self):
        return self.engine.get_public_state()
    
    def submit_action(self, agent_id: str, action: Dict[str, Any]) -> bool:
        return self.engine.submit_action(agent_id, action)
    
    # ═══════════════════════════════════════════════════════════════════════
    # ENHANCED PROCESS TURN
    # ═══════════════════════════════════════════════════════════════════════
    
    def process_turn(self) -> Dict[str, Any]:
        """
        Enhanced turn processing that includes all new systems.
        
        Processing order:
        1. Base engine processing (actions, financials, events)
        2. Game Master events
        3. Credit payment processing
        4. Calendar reminders
        5. Ethical dilemmas
        6. Advance time
        """
        current_week = self.time_system.current_week
        
        # 1. Base engine processing
        base_results = self.engine.process_turn()
        
        # 2. Game Master daily events
        self._process_game_master_events(current_week)
        
        # 3. Credit payment processing
        self._process_credit_payments(current_week)
        
        # 4. Calendar reminders
        self._process_calendar(current_week)
        
        # 5. Ethical dilemmas - scoring integration
        self._process_ethical_dilemmas(current_week)
        
        # Reset day counter
        self.current_day = 1
        
        return base_results
    
    def _process_game_master_events(self, week: int):
        """Run Game Master event generation."""
        try:
            agent_state_summaries = {
                aid: {
                    "balance": s.balance,
                    "social_score": s.social_score.total_score,
                    "customers": getattr(s, 'active_customers', 0)
                }
                for aid, s in self.states.items()
            }
            
            events = self.game_master.generate_daily_events(
                week=week,
                day=self.current_day,
                game_state={"season": getattr(self.time_system, 'season', 'spring')},
                agent_states=agent_state_summaries
            )
            
            for event in events:
                target_agents = event.target_agents or list(self.agent_ids)
                for agent_id in target_agents:
                    if agent_id in self.states:
                        state = self.states[agent_id]
                        effects = event.effects
                        
                        if "cash_impact" in effects:
                            state.balance += effects["cash_impact"]
                        
                        if "reputation_change" in effects:
                            state.update_social_score("community_standing", effects["reputation_change"])
                        
                        self.communication.send_message(
                            sender_id="Game Master",
                            recipient_id=agent_id,
                            content=f"📰 {event.title}: {event.description}",
                            week=week
                        )
                
                logger.info(f"Game Master event: {event.title}")
        except Exception as e:
            logger.error(f"Game Master processing failed: {e}")
    
    def _process_credit_payments(self, week: int):
        """Process due credit payments."""
        for agent_id in self.agent_ids:
            try:
                due_payments = self.credit_system.get_due_payments(agent_id, week)
                
                for payment in due_payments:
                    state = self.states[agent_id]
                    
                    if state.balance >= payment.amount_due:
                        state.balance -= payment.amount_due
                        result = self.credit_system.make_payment(
                            agent_id,
                            payment.id,
                            payment.amount_due,
                            week
                        )
                        
                        self.communication.send_message(
                            sender_id="Credit System",
                            recipient_id=agent_id,
                            content=f"💳 Payment of ${payment.amount_due:.2f} processed. Credit score: {result.get('new_credit_score', 'N/A')}",
                            week=week
                        )
                    else:
                        self.credit_system.mark_missed_payment(
                            agent_id,
                            payment.id,
                            week
                        )
                        self.communication.send_message(
                            sender_id="Credit System",
                            recipient_id=agent_id,
                            content=f"⚠️ MISSED PAYMENT: ${payment.amount_due:.2f} due. Insufficient funds!",
                            week=week
                        )
                
                self.credit_system.update_history_length(agent_id, week)
                
            except Exception as e:
                logger.error(f"Credit processing failed for {agent_id}: {e}")
    
    def _process_calendar(self, week: int):
        """Process calendar reminders."""
        try:
            reminders = self.calendar_manager.process_day(week, self.current_day)
            
            for agent_id, messages in reminders.items():
                for msg in messages:
                    self.communication.send_message(
                        sender_id="Calendar",
                        recipient_id=agent_id,
                        content=msg,
                        week=week
                    )
        except Exception as e:
            logger.error(f"Calendar processing failed: {e}")
    
    def _process_ethical_dilemmas(self, week: int):
        """Generate and process ethical dilemmas."""
        for agent_id in self.agent_ids:
            try:
                context = {
                    "balance": self.states[agent_id].balance,
                    "social_score": self.states[agent_id].social_score.total_score,
                    "week": week
                }
                
                dilemma = self.ethical_events.check_for_dilemmas(week, agent_id, context)
                
                if dilemma:
                    self.communication.send_message(
                        sender_id="Ethics Board",
                        recipient_id=agent_id,
                        content=f"⚠️ ETHICAL DILEMMA: {dilemma.name}\n{dilemma.description}",
                        week=week,
                        intent="dilemma"
                    )
                    logger.info(f"Ethical dilemma '{dilemma.name}' for agent {agent_id}")
                    
            except Exception as e:
                logger.error(f"Ethical dilemma processing failed for {agent_id}: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════
    # NEW SYSTEM ACCESSORS
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_credit_report(self, agent_id: str) -> Dict[str, Any]:
        """Get credit report for an agent."""
        return self.credit_system.get_credit_report(agent_id)
    
    def get_calendar(self, agent_id: str):
        """Get calendar for an agent."""
        return self.calendar_manager.get_calendar(agent_id)
    
    def get_zone_info(self, agent_id: str) -> Dict[str, Any]:
        """Get neighborhood zone info for an agent."""
        zone_id = self.neighborhood.laundromat_locations.get(agent_id)
        if zone_id:
            zone = self.neighborhood.zones[zone_id]
            return {
                "zone_id": zone_id.value,
                "name": zone_id.name.replace("_", " ").title(),
                "base_foot_traffic": zone.base_foot_traffic,
                "weekly_rent": zone.weekly_rent,
                "visibility_bonus": zone.visibility_bonus,
                "demographics": zone.demographics
            }
        return {}
    
    def evaluate_ethical_choice(
        self,
        agent_id: str,
        dilemma_context: str,
        choice_made: str,
        reasoning: str = ""
    ) -> Dict[str, Any]:
        """Use Game Master to evaluate an ethical choice."""
        return self.game_master.evaluate_ethical_choice(
            agent_id, dilemma_context, choice_made, reasoning
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize enhanced state for API responses."""
        return {
            "week": self.time_system.current_week,
            "day": self.current_day,
            "agents": {
                aid: {
                    "state": {
                        "balance": s.balance,
                        "social_score": s.social_score.total_score,
                        "price": s.price
                    },
                    "credit": self.credit_system.to_dict(aid),
                    "zone": self.get_zone_info(aid),
                    "calendar": self.calendar_manager.get_calendar(aid).get_statistics()
                }
                for aid, s in self.states.items()
            },
            "game_master": self.game_master.to_dict()
        }
