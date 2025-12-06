from src.engine.time import Season
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Optional
import random

class EventType(Enum):
    GLOBAL_HEATWAVE = "global_heatwave"
    GLOBAL_RECESSION = "global_recession"
    LOCAL_MACHINE_BREAKDOWN = "local_machine_breakdown"
    LOCAL_BAD_REVIEW = "local_bad_review"
    SEASONAL_SPIKE = "seasonal_spike"
    SEASONAL_LULL = "seasonal_lull"

@dataclass
class GameEvent:
    type: EventType
    target_agent_id: Optional[str] # None for global
    description: str
    duration: int # Weeks remaining
    effect_data: Dict[str, float] = None

class EventManager:
    def __init__(self, use_llm: bool = False, llm_provider: str = "openai"):
        self.active_events: List[GameEvent] = []
        self.use_llm = use_llm
        self.llm_provider = llm_provider
        self.llm = None
        self.deployment = None
        self.world_news: List[str] = []
        
        if use_llm:
            try:
                from src.engine.llm_utils import LLMHelper
                self.llm, self.deployment = LLMHelper.setup_llm(llm_provider)
            except Exception as e:
                print(f"[EventManager] Failed to setup LLM: {e}. Using simple descriptions.")
                self.use_llm = False

    def generate_random_events(self, week: int, agent_ids: List[str], season: Season = Season.SPRING) -> List[GameEvent]:
        new_events = []
        
        # 1. Global Events (Low chance)
        # Heatwave only in Summer
        if season == Season.SUMMER and random.random() < 0.15:
            event = GameEvent(
                type=EventType.GLOBAL_HEATWAVE,
                target_agent_id=None,
                description="A massive heatwave has struck! People are sweating more.",
                duration=2,
                effect_data={"demand_multiplier": 1.5}
            )
            new_events.append(event)
            
        # Cold Snap in Winter
        if season == Season.WINTER and random.random() < 0.15:
             event = GameEvent(
                type=EventType.SEASONAL_SPIKE,
                target_agent_id=None,
                description="A bitter cold snap! Bulky coats need washing.",
                duration=2,
                effect_data={"demand_multiplier": 1.3}
            )
             new_events.append(event)
             
        # Student Rush in Autumn
        if season == Season.AUTUMN and week % 4 == 0: # Start of month roughly
             event = GameEvent(
                type=EventType.SEASONAL_SPIKE,
                target_agent_id=None,
                description="Students are back! Laundry bags are overflowing.",
                duration=1,
                effect_data={"demand_multiplier": 1.4}
            )
             new_events.append(event)

        # 2. Local Events (Per agent chance)
        for agent_id in agent_ids:
            if random.random() < 0.1: # 10% chance per week
                if random.random() < 0.5:
                    event = GameEvent(
                        type=EventType.LOCAL_MACHINE_BREAKDOWN,
                        target_agent_id=agent_id,
                        description="One of your washing machines broke down!",
                        duration=1,
                        effect_data={"machine_loss": 1}
                    )
                else:
                    event = GameEvent(
                        type=EventType.LOCAL_BAD_REVIEW,
                        target_agent_id=agent_id,
                        description="A customer left a scathing review online.",
                        duration=4, # Lasts a month
                        effect_data={"customer_satisfaction_penalty": 5.0}
                    )
                
                # Enhance description with LLM if enabled
                if self.use_llm:
                     event.description = self._enhance_event_description(
                        event.type.value,
                        event.description,
                        week,
                        agent_id
                    )
                
                new_events.append(event)
        
        self.active_events.extend(new_events)
        return new_events

    def process_events(self):
        # Decrease duration and remove expired
        self.active_events = [e for e in self.active_events if e.duration > 0]
        for e in self.active_events:
            e.duration -= 1

    def get_active_effects(self, agent_id: str) -> Dict[str, float]:
        effects = {
            "demand_multiplier": 1.0,
            "customer_satisfaction_penalty": 0.0,
            "machine_loss": 0
        }
        
        for e in self.active_events:
            if e.target_agent_id is None or e.target_agent_id == agent_id:
                if e.type == EventType.GLOBAL_HEATWAVE:
                    effects["demand_multiplier"] *= e.effect_data.get("demand_multiplier", 1.0)
                elif e.type == EventType.LOCAL_BAD_REVIEW:
                    effects["customer_satisfaction_penalty"] += e.effect_data.get("customer_satisfaction_penalty", 0.0)
                elif e.type == EventType.LOCAL_MACHINE_BREAKDOWN:
                    effects["machine_loss"] += int(e.effect_data.get("machine_loss", 0))
                    
        return effects
    
    def _enhance_event_description(
        self,
        event_type: str,
        event_summary: str,
        week: int,
        agent_id: Optional[str] = None
    ) -> str:
        """Use LLM to create a more narrative-rich event description."""
        if not self.use_llm:
            return event_summary
        
        try:
            from src.engine.llm_utils import LLMHelper
            
            scope = "neighborhood-wide" if agent_id is None else f"at laundromat {agent_id}"
            
            prompt = f"""You are a narrator for a business simulation game.
Week {week}: A new event has occurred {scope}.

Event type: {event_type}
Basic summary: {event_summary}

Write a brief, engaging description of this event (1-2 sentences).
Make it vivid and interesting, but keep it professional and realistic.

Respond with just the description text, no JSON or extra formatting."""

            enhanced = LLMHelper.safe_call_llm(
                self.llm,
                self.deployment,
                prompt,
                max_tokens=100,
                temperature=0.8,
                provider=self.llm_provider,
                fallback_value=event_summary
            )
            
            if enhanced:
                return enhanced.strip()
                
        except Exception as e:
            print(f"[EventManager] Failed to enhance event description: {e}")
        
        return event_summary
    
    def generate_world_news(self, week: int, laundromats_info: List[Dict]) -> Optional[str]:
        """Generate world/neighborhood news based on current state."""
        if not self.use_llm:
            return None
        
        try:
            from src.engine.llm_utils import LLMHelper
            
            # Build context
            business_summary = []
            for l in laundromats_info:
                business_summary.append(
                    f"- {l.get('name')}: ${l.get('price'):.2f}/load, "
                    f"social score {l.get('social_score')}/100"
                )
            
            active_events_summary = [e.description for e in self.active_events[:3]]
            
            prompt = f"""You are a local news reporter covering the laundromat industry in Sunnyside neighborhood.
Week {week} update:

Current businesses:
{chr(10).join(business_summary)}

Recent events:
{chr(10).join(active_events_summary) if active_events_summary else "Business as usual"}

Write a short news headline and brief update (2-3 sentences) about the local laundromat scene.
Make it interesting and relevant to the current market conditions.

Respond with just the news text, no JSON or extra formatting."""

            news = LLMHelper.safe_call_llm(
                self.llm,
                self.deployment,
                prompt,
                max_tokens=150,
                temperature=0.7,
                provider=self.llm_provider
            )
            
            if news:
                news_text = news.strip()
                self.world_news.append(f"Week {week}: {news_text}")
                return news_text
                
        except Exception as e:
            print(f"[EventManager] Failed to generate world news: {e}")
        
        return None
