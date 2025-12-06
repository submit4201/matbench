# Laundromat Tycoon: Neighborhood Strategy Simulator
A Comprehensive Multi-Agent Benchmark for Evaluating LLM Decision-Making, Ethics, and Social Intelligence

# 1.1 What Is This Benchmark?

Laundromat Tycoon is a multi-agent business simulation designed to evaluate Large Language Models (LLMs) in a realistic, competitive environment. Unlike traditional benchmarks that test isolated skills, this simulation immerses LLMs in a dynamic economic ecosystem where they must autonomously manage virtual laundromats.

Participants (human or AI) face decisions across:

- Pricing and revenue optimization
- Staffing and human resource management
- Marketing and customer engagement
- Vendor relationships and supply chains
- Alliances, competition, and negotiation
- Ethical dilemmas and social reputation
- Crisis response and resilience

This benchmark generates multidimensional data about LLM behavior under autonomy, revealing insights into adaptability, foresight, ethics, and social intelligence that conventional testing cannot capture.

# 1.2 Why a Laundromat?

The laundromat setting is deliberately chosen for its balance of accessibility and strategic depth:

-   **Low Barrier to Entry:** Its universal familiarity ensures easy comprehension for participants.
-   **High Strategic Depth:** It encompasses complex decisions around pricing, customer loyalty, vendor relationships, staff management, competition, alliances, and ethical considerations.
-   **Rich Social Dynamics:** It naturally involves customer relationships, neighborhood reputation, and community engagement.
-   **Clear Feedback Loops:** The immediate and measurable impact of decisions (e.g., customer satisfaction, revenue, reputation changes) provides unambiguous signals for LLM learning and evaluation.
-   **Scalable Complexity:** The model allows for easy integration of additional layers, such as franchising, hostile takeovers, or environmental regulations, without losing its core accessibility.

# 1.3 Core Questions This Benchmark Answers

The simulation is designed to probe how LLMs handle integrated decision-making across multiple dimensions:

- **Adaptability**: How does the LLM respond to changing market conditions?
- **Innovation**: Can it identify and capitalize on new opportunities?
- **Leadership**: How does it manage and motivate employees?
- Reputation: Does it understand nuances of public relations and brand building?
- Trust & Alliances: How does it handle betrayal or unexpected partnerships?
- Strategic Depth: Does it sacrifice short-term gains for long-term success?
- Ethics: How does it respond to moral dilemmas and stakeholder trade-offs?
- Negotiation: Can it persuade, detect deception, and build alliances?
- Resilience: How does it recover from crises and pivot strategies?

# 1.4 Evaluation Framework
The benchmark evaluates LLMs across three pillars of intelligence and three domains of excellence:

## Pillars of Intelligence
  
  ### - Strategic Intelligence
        - Long-term planning
        - Resource optimization
        - Market positioning
        - Risk management
  ### - Social Intelligence
        - Negotiation and persuasion
        - Trust-building and alliance management
        - Betrayal detection
        - Reputation management
  ### - Ethical Reasoning
        - Value consistency
        - Moral trade-off handling
        - Stakeholder consideration
        - Transparency under pressure

## Domains of Excellence
  ### - Intelligence in Action
        - Crisis response
        - Strategy pivoting
        - Learning from failure
        - Exploiting opportunities
  ### - Operational Excellence
        - Efficiency optimization
        - Quality control
        - Customer service
        - Supply chain management
  ### - Communication Skill
        - Persuasion and clarity
        - Honesty vs. deception
        - Conflict resolution
        - Information gathering

# 1.5 Competition Format

┌─────────────────────────────────────────────────────────────────────────┐
│                         PARTICIPANT STRUCTURE                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│   HUMAN PLAYERS (1–3)               AI COMPETITORS (3–6)                │
│   ┌─────────────────┐               ┌─────────────────┐                 │
│   │   Dashboard     │               │   API Interface │                 │
│   │   Interface     │               │   (Structured   │                 │
│   │ • Visual UI     │               │    JSON I/O)    │                 │
│   │ • Chat system   │               │                 │                 │
│   │ • Analytics     │               │  Each LLM gets: │                 │
│   └─────────────────┘               │  • State data   │                 │
│                                     │  • Action menu  │                 │
│   Full autonomy over:               │  • Comm channel │                 │
│   • Pricing                         └─────────────────┘                 │
│   • Staffing                                                            │
│   • Marketing                       Full autonomy over:                 │
│   • Alliances                       • All decisions                     │
│   • Expansion                       • Communication                     │
│   • Ethics                          • Strategy                          │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│                           SHARED ENVIRONMENT                            │
│   • Same customer pool       • Same random events                       │
│   • Same regulations         • Same economic conditions                 │
│   • Same vendor options      • Same starting resources                  │
└─────────────────────────────────────────────────────────────────────────┘

continued page 2 