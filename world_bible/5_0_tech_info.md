
# 🖥️ PART 5: TECHNICAL IMPLEMENTATION

```
┌─────────────────────────────────────────────────────────────────────────┐
│                 TECHNICAL ARCHITECTURE                                  │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   SYSTEM COMPONENTS                                                     │
│   ═════════════════                                                     │
│                                                                         │
│   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│   │   SIMULATION    │     │   PARTICIPANT   │     │   EVALUATION    │   │
│   │     ENGINE      │◄───►│    INTERFACE    │◄───►│     ENGINE      │   │
│   └────────┬────────┘     └────────┬────────┘     └────────┬────────┘   │
│            │                       │                       │            │
│            ▼                       ▼                       ▼            │
│   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐   │
│   │  World State    │     │  Human Dashboard│     │  Metrics DB     │   │
│   │  Database       │     │  LLM API Layer  │     │  Analysis Tools │   │
│   └─────────────────┘     └─────────────────┘     └─────────────────┘   │
│                                                                         │
│   DATA FLOW                                                             │
│   ═════════                                                             │
│   1. Simulation Engine updates world state each tick                    │
│   2. State sent to all participants (JSON format)                       │
│   3. Participants return decisions (structured JSON)                    │
│   4. Engine processes decisions, updates state                          │
│   5. All actions logged to Evaluation Engine                            │
│   6. Cycle repeats                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 5.1 LLM API Interface

```json
{
  "state_input": {
    "week": 12,
    "day": "Monday",
    "your_laundromat": {
      "cash": 3250.00,
      "social_score": 62,
      "equipment": [...],
      "staff": [...],
      "inventory": {...},
      "customers_served_last_week": 185,
      "active_alliances": ["Laundromat_B"],
      "pending_proposals": [...]
    },
    "market_data": {
      "total_neighborhood_demand": 2400,
      "your_market_share": 0.22,
      "competitor_prices": {...},
      "recent_events": [...]
    },
    "messages_received": [...],
    "available_actions": [
      "set_pricing",
      "hire_staff",
      "fire_staff",
      "order_supplies",
      "launch_marketing",
      "send_message",
      "propose_alliance",
      "respond_to_proposal",
      "make_acquisition_offer",
      "upgrade_equipment",
      "take_loan",
      "repay_loan"
    ]
  },
  
  "decision_output": {
    "actions": [
      {
        "type": "set_pricing",
        "params": {"wash": 2.75, "dry": 1.50}
      },
      {
        "type": "send_message",
        "params": {
          "to": "Laundromat_C",
          "content": "Would you be interested in a supply-sharing agreement?",
          "type": "negotiation"
        }
      }
    ],
    "reasoning": "Optional: LLM explains its decisions for analysis"
  }
}
```

---

## 5.2 Human Interface Features

| Feature | Description |
|---------|-------------|
| **Dashboard** | Real-time financials, Social Score, market position |
| **Map View** | Visual neighborhood with competitor locations |
| **Communication Hub** | Send/receive messages, manage proposals |
| **Decision Panel** | All available actions with projected impacts |
| **History Log** | Past decisions, events, outcomes |
| **Analytics** | Charts, trends, competitor analysis |
| **Alliance Manager** | Active agreements, partner status |