from src.world.ticket import Ticket, TicketType
import uuid
import random
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class CustomerMemory:
    laundromat_id: str
    interaction_count: int = 0
    bad_experiences: int = 0
    good_experiences: int = 0
    last_visit_week: int = -1

class CustomerSegment:
    STUDENT = "Student"
    FAMILY = "Family"
    SENIOR = "Senior"
    ADULT = "Adult"

SEGMENT_DISTRIBUTION = {
    CustomerSegment.STUDENT: 0.25,
    CustomerSegment.FAMILY: 0.28,
    CustomerSegment.SENIOR: 0.18,
    CustomerSegment.ADULT: 0.29
}

SEGMENT_PROFILES = {
    CustomerSegment.STUDENT: {
        "price_sensitivity": (0.8, 1.0),
        "quality_sensitivity": (0.2, 0.5),
        "ethics_sensitivity": (0.4, 0.6),
        "patience": (0.3, 0.6),
        "irrationality": (0.1, 0.3)
    },
    CustomerSegment.FAMILY: {
        "price_sensitivity": (0.4, 0.6),
        "quality_sensitivity": (0.7, 0.9),
        "ethics_sensitivity": (0.2, 0.5),
        "patience": (0.4, 0.7),
        "irrationality": (0.0, 0.2)
    },
    CustomerSegment.SENIOR: {
        "price_sensitivity": (0.2, 0.4),
        "quality_sensitivity": (0.8, 1.0),
        "ethics_sensitivity": (0.3, 0.6),
        "patience": (0.7, 1.0),
        "irrationality": (0.1, 0.4)
    },
    CustomerSegment.ADULT: {
        "price_sensitivity": (0.4, 0.7),
        "quality_sensitivity": (0.4, 0.7),
        "ethics_sensitivity": (0.3, 0.6),
        "patience": (0.1, 0.4),
        "irrationality": (0.1, 0.3)
    }
}

class Persona:
    def __init__(self, name: str, price_sensitivity: float, quality_sensitivity: float, ethics_sensitivity: float, patience: float, irrationality_factor: float = 0.0, segment: str = "Unknown"):
        self.name = name
        self.price_sensitivity = price_sensitivity      # 0.0 to 1.0 (1.0 = very cheap)
        self.quality_sensitivity = quality_sensitivity  # 0.0 to 1.0 (1.0 = demands luxury)
        self.ethics_sensitivity = ethics_sensitivity    # 0.0 to 1.0 (1.0 = cares about social score)
        self.patience = patience                        # 0.0 to 1.0 (1.0 = very patient)
        self.irrationality_factor = irrationality_factor # 0.0 to 1.0 (1.0 = completely random/spiteful)
        self.segment = segment

    @staticmethod
    def generate_random():
        # Select segment based on distribution
        segments = list(SEGMENT_DISTRIBUTION.keys())
        weights = list(SEGMENT_DISTRIBUTION.values())
        segment = random.choices(segments, weights=weights, k=1)[0]
        
        profile = SEGMENT_PROFILES[segment]
        
        # Generate stats within ranges
        p = random.uniform(*profile["price_sensitivity"])
        q = random.uniform(*profile["quality_sensitivity"])
        e = random.uniform(*profile["ethics_sensitivity"])
        pat = random.uniform(*profile["patience"])
        irr = random.uniform(*profile["irrationality"])
        
        # Generate name
        name = f"{segment} {random.randint(100, 999)}"
        
        return Persona(name, p, q, e, pat, irr, segment)

class Customer:
    def __init__(self, customer_id: str):
        self.id = customer_id
        self.persona = Persona.generate_random()
        self.memory: Dict[str, CustomerMemory] = {}
        self.current_thought: str = ""
        self.bias_map: Dict[str, float] = {} # agent_id -> bias score (-1.0 to 1.0)

    def decide_laundromat(self, laundromats: List['Laundromat']) -> 'Laundromat':
        # Simple scoring logic based on persona and memory
        best_score = -float('inf')
        chosen_laundromat = None

        # Irrational Mood Swing
        mood_swing = 0.0
        if random.random() < self.persona.irrationality_factor:
            mood_swing = random.uniform(-5.0, 5.0)
            self.current_thought = "I'm feeling unpredictable today!"

        for l in laundromats:
            score = 0
            
            # Price factor (lower price is better for price sensitive)
            score -= l.price * self.persona.price_sensitivity * 2

            # Quality/Reputation factor
            score += l.reputation * self.persona.quality_sensitivity

            # Ethics factor (social_score is now always a Pydantic model)
            score += l.social_score.total_score * self.persona.ethics_sensitivity

            # Memory factor
            mem = self.memory.get(l.id)
            if mem:
                score -= mem.bad_experiences * 5
                score += mem.good_experiences * 2
            
            # Bias factor (Irrational preference/spite)
            bias = self.bias_map.get(l.id, 0.0)
            score += bias * 10.0 # Bias has strong effect
            
            # Apply mood swing randomly to one option if irrational
            if mood_swing != 0.0 and random.random() < 0.2:
                score += mood_swing

            if score > best_score:
                best_score = score
                chosen_laundromat = l
        
        if chosen_laundromat:
            self.current_thought = f"I'm going to {chosen_laundromat.name}. Hope it's good!"
        else:
            self.current_thought = "Nowhere good to go..."

        return chosen_laundromat

    def visit_laundromat(self, laundromat: 'Laundromat', week: int) -> bool:
        """
        Simulates the visit. Returns True if successful, False if issues occurred (and ticket generated).
        """
        # Spite Check (Irrational refusal)
        if random.random() < self.persona.irrationality_factor * 0.1: # Small chance to just leave
             self.current_thought = f"I walked into {laundromat.name} but just didn't like the vibe. Leaving."
             return False

        # Check Inventory (use 'detergent' key - that's what the inventory actually uses)
        if laundromat.inventory.get("detergent", 0) <= 0:
            self._create_ticket(laundromat, TicketType.OUT_OF_SOAP, "No soap available!", week)
            self.current_thought = f"Ugh, {laundromat.name} is out of soap! Never coming back."
            return False
        
        # Consume Inventory
        laundromat.inventory["detergent"] = laundromat.inventory.get("detergent", 0) - 1
        
        # Random Machine Breakdown Check
        if random.random() > self.persona.patience and laundromat.broken_machines > 0:
             self._create_ticket(laundromat, TicketType.MACHINE_BROKEN, "Machine ate my coin!", week)
             self.current_thought = f"My machine at {laundromat.name} broke! I'm so mad!"
             return False

        # Drama Event (Irrational Complaint)
        if random.random() < self.persona.irrationality_factor * 0.2: # 20% of irrationality factor
            self._create_ticket(laundromat, TicketType.OTHER, "The lighting is too aggressive!", week)
            self.current_thought = f"I demanded to speak to the manager at {laundromat.name} about the lighting."
            return False

        # Success!
        self.current_thought = f"Had a great wash at {laundromat.name}. Fresh and clean!"
        return True

    def _create_ticket(self, laundromat: 'Laundromat', type: TicketType, desc: str, week: int):
        severity = "medium"
        if type == TicketType.MACHINE_BROKEN:
            severity = "high"
        elif type == TicketType.DIRTY_FLOOR:
            severity = "low"
        
        # Drama Escalation
        if self.persona.irrationality_factor > 0.7:
            severity = "critical"
            desc = f"[DRAMA] {desc.upper()}!!! I AM CALLING THE MAYOR!"
            
        ticket = Ticket(
            id=str(uuid.uuid4())[:8],
            type=type,
            description=desc,
            customer_id=self.id,
            laundromat_id=laundromat.id,
            created_week=week,
            severity=severity
        )
        laundromat.tickets.append(ticket)
        self.record_experience(laundromat.id, is_good=False, week=week)

    def record_experience(self, laundromat_id: str, is_good: bool, week: int):
        if laundromat_id not in self.memory:
            self.memory[laundromat_id] = CustomerMemory(laundromat_id)
        
        mem = self.memory[laundromat_id]
        mem.interaction_count += 1
        mem.last_visit_week = week
        if is_good:
            mem.good_experiences += 1
            # Positive bias reinforcement
            self.bias_map[laundromat_id] = min(1.0, self.bias_map.get(laundromat_id, 0) + 0.1)
        else:
            mem.bad_experiences += 1
            # Negative bias reinforcement (grudge)
            self.bias_map[laundromat_id] = max(-1.0, self.bias_map.get(laundromat_id, 0) - 0.2)


class LLMCustomer(Customer):
    """LLM-powered customer with intelligent decision-making."""
    
    def __init__(self, customer_id: str, llm_provider: str = "openai"):
        super().__init__(customer_id)
        self.llm_provider = llm_provider
        self.use_llm = True
        
        try:
            from src.engine.llm_utils import LLMHelper
            self.llm, self.deployment = LLMHelper.setup_llm(llm_provider)
        except Exception as e:
            print(f"[LLMCustomer {customer_id}] Failed to setup LLM: {e}. Falling back to rule-based.")
            self.use_llm = False
    
    def decide_laundromat(self, laundromats: List['Laundromat']) -> 'Laundromat':
        """Use LLM to make intelligent laundromat choice with fallback to rule-based."""
        if not self.use_llm or not laundromats:
            return super().decide_laundromat(laundromats)
        
        try:
            from src.engine.llm_utils import LLMHelper
            
            # Build context for LLM
            laundromat_info = []
            for l in laundromats:
                mem = self.memory.get(l.id)
                mem_str = "No history"
                if mem:
                    mem_str = f"{mem.good_experiences} good, {mem.bad_experiences} bad experiences"
                
                laundromat_info.append({
                    "id": l.id,
                    "name": l.name,
                    "price": l.price,
                    "reputation": l.reputation,
                    "social_score": l.social_score.total_score,
                    "memory": mem_str
                })

            
            prompt = f"""You are a customer named {self.persona.name} ({self.persona.segment}) choosing a laundromat.

Your preferences:
- Price sensitivity: {self.persona.price_sensitivity:.1f} (0=don't care, 1=very price conscious)
- Quality sensitivity: {self.persona.quality_sensitivity:.1f} (0=don't care, 1=demand luxury)
- Ethics sensitivity: {self.persona.ethics_sensitivity:.1f} (0=don't care, 1=care about social responsibility)
- Patience: {self.persona.patience:.1f} (0=impatient, 1=very patient)

Available laundromats:
{chr(10).join([f"- {l['name']}: ${l['price']}, reputation={l['reputation']}, social_score={l['social_score']}, history=({l['memory']})" for l in laundromat_info])}

Choose the best laundromat for you and explain your reasoning briefly.

Respond in JSON format:
{{
    "chosen_id": "laundromat_id",
    "thought": "brief explanation of your choice"
}}"""

            response = LLMHelper.safe_call_llm(
                self.llm,
                self.deployment,
                prompt,
                max_tokens=200,
                temperature=0.7,
                provider=self.llm_provider
            )
            
            if response:
                data = LLMHelper.parse_json_response(response)
                chosen_id = data.get("chosen_id")
                self.current_thought = data.get("thought", "I made my choice.")
                
                # Find the laundromat
                for l in laundromats:
                    if l.id == chosen_id:
                        return l
                
                # Fallback if ID not found
                print(f"[LLMCustomer {self.id}] LLM chose invalid ID, falling back")
                
        except Exception as e:
            print(f"[LLMCustomer {self.id}] LLM decision failed: {e}, falling back")
        
        # Fallback to rule-based
        return super().decide_laundromat(laundromats)
    
    def _create_ticket(self, laundromat: 'Laundromat', type: TicketType, desc: str, week: int):
        """Override to generate more realistic complaints via LLM."""
        if self.use_llm:
            try:
                from src.engine.llm_utils import LLMHelper
                
                prompt = f"""You are {self.persona.name} ({self.persona.segment}), a customer at {laundromat.name} laundromat.
You just had a bad experience: {desc}

Your personality:
- Patience: {self.persona.patience:.1f} (0=very impatient, 1=very patient)

Write a complaint message (1-2 sentences) that fits your personality.
Respond with just the complaint text, no JSON or extra formatting."""

                complaint = LLMHelper.safe_call_llm(
                    self.llm,
                    self.deployment,
                    prompt,
                    max_tokens=100,
                    temperature=0.8,
                    provider=self.llm_provider,
                    fallback_value=desc
                )
                
                if complaint:
                    desc = complaint.strip()
                    
            except Exception as e:
                print(f"[LLMCustomer {self.id}] Failed to generate complaint: {e}")
        
        # Create ticket with potentially LLM-enhanced description
        severity = "medium"
        if type == TicketType.MACHINE_BROKEN:
            severity = "high"
        elif type == TicketType.DIRTY_FLOOR:
            severity = "low"
            
        ticket = Ticket(
            id=str(uuid.uuid4())[:8],
            type=type,
            description=desc,
            customer_id=self.id,
            laundromat_id=laundromat.id,
            created_week=week,
            severity=severity
        )
        laundromat.tickets.append(ticket)
        self.record_experience(laundromat.id, is_good=False, week=week)
