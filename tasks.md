# Refactoring Checklist & Implementation Notes

This document compiles all refactoring suggestions and specific user notes gathered from the project documentation.
# legend
- [ ] - not done
- [x] - done
- [/] - partial
- [x] **Logging**: Implement centralized, structured logging.
    - [x] Create `src/core/logger.py` (or update `src/utils/logger.py`).
    - [x] Implement rotation and compression policies (every couple hours / end of day).
    - [x] Ensure separate folders per log type (if applicable, or just clear naming).
    - [x] Replace `print` statements with logger calls throughout `src`.
        - [x] Server & Agents
        - [x] Game Engine
        - [x] Commerce (Vendor, Market)
        - [x] Finance
        - [x] Core (Events, Time)
    - [x] Add JSON formatting for structured logs.

- [x] **Testing**: Implement comprehensive testing (Rule 3).
    - [x] Create `.test` directory structure.
    - [x] Configure `pytest`.
    - [x] Integrate logging into tests.

## Frontend

- [ ] **State Management**: Evaluate moving from `useState`/`prop drilling` to
- - [/] - zustand
- - [ ] - noy sure if this is a good idea  idk if i like it or not
- [x] **Dashboard Fix**: Resolve Dashboard Component issues.
  - _User Note_: `# ! [x] working as of 12/8`
- [/] **Turn Handling**: Add daily options alongside real-time/weekly modes.
  - _User Note_: `# [x] we decide on a 10 minute day/turn`
  - _User Note_: `# [ ] we need to complete the turn system`
- [ ] **Type Safety**: Automate generation of TypeScript interfaces from Python Pydantic models.
  - _User Note_: `# [ ] it seem we kibda did this vut never finished`
- [ ] **Real-time Updates**: Implement WebSockets for state updates (replacing polling).
  - _User Note_: `# [ ] we need to complete the turn system`
- [/] __**Provider Logic**: Use a Factory pattern for LLM providers.__
  - _User Note_: `# [ ] we need to complete this  system`
  - [ ] - we to makr dure whatever llns the playwe chooses thats what we use
  - [ ] - we should off offer chooses on the game master and judge llms too
---
```markdown
# this section is being completed by agent - ione
### Agent Tools Wishlist (Registration Needed) (COMPLETED)

      - [x] `pay_bill(bill_id: str)`: Pay specific outstanding bills. (`ActionType.PAY_BILL` map exists)
      - [x] `check_financial_health()`: Get a comprehensive financial report. (`get_financial_report`)
      - [x] `check_bank_balance()`: View current bank account balance. (Included in financial report)
      - [x] expense_report(): Generate a detailed expense report. (Included in financial report)
      - [x] income_report(): Generate a detailed income report. (Included in financial report)
      - [x] loan_report(): Generate a detailed loan report. (Included in financial report)
      - [x] credit_report(): Generate a detailed credit report. (`check_credit_score`)
      - [x] tools for finance management and the use of the bank

  #### Management & Operations

      - [x] `maintenance()`: Pre-emptive repair to lower breakdown chance. (`perform_maintenance`)
      - [x] `hire_staff(role: str)`: Recruit employees (if staff module active).
      - [x] `manage_staff(action: str, staff_id: str)`: manage staff.
        - [x] - hire, fire, pay, promote, assign, train, transfer (`hire_staff`, `fire_staff`, `train_staff` implemented)
      - [x] `inspect_facility()`: View current facility status and resource availability.
        - [x] -  machine status, cleaning status, etc
        - [x] emergency_repair(): emergency repair to fix breakdown. (Partially covered by standard maintenance, needs specific tool if different)
      - [x] tools for management and operations

  #### vendor & Logistics

      - [x] `inspect_inventory()`: Check current stock levels and resource availability.
      - [x] tools for vendor and logistics management  
      - [x] `order_resources()`: Order resources from vendors. (`buy_supplies` / `ActionType.ORDER_RESOURCES`)
      - [x] `inspect_orders()`: View current orders and their status. (`inspect_deliveries`)
      - [x] `inspect_deliveries()`: View current deliveries and their status.
      - [x] `inspect_vendor()`: View current vendor status and resource availability.
      - [x] purposals, negotiations, offers and care of those systems (`negotiate_contract`, `send_formal`)

  #### Diplomacy & Social

      - [x] `send_dm(recipient: str, content: str, intent: str)`: Enhanced messaging with intent classification.
      - [x] `propose_treaty(target: str, terms: dict)`: Formalize alliances beyond simple text. (`send_formal` / `propose_alliance`)
      - [x] chat message, create message, send message, respond to message, read message, delete message, 
      - [x]  regulatory systems implementation
      - [x] scores and reputation system the veiwing of
      - [x] public records and history and relations
  
  #### Next Steps (From Tool Implementation)
  
  - [x] **Implementation**: Implement specific logic for `check_market_trends` (Connected to MarketSystem).
  - [ ] **Refinement**: Refine `inspect_competitor` to filter based on "Fog of War" or Intelligence Level.
  - [x] **Integration**: Integrate `Staff` mechanics more deeply into the simulation (Cleaners, Techs, Attendants active).
        - [x]  regulatory systems implementation - need tools here for llm to understand and use these systesm
        - [x] scores and reputation system we tools for this system
        - [x] public records and history and relations and i think we need tools for this system  but maybe i missed it earlier 
        not sure if we have marketing  tooling either


        ```
---
## Engines

- [x] **Market System**: Implement full Market/Economy system logic (Trends, Fluctuations, Reports).
- [ ] **Supply Chain**: Implement detailed logistics simulation. delivery shipments, 
- [ ] **Vendor Order Logic**: Separate concerns by splitting `OrderProcessor`&`Vendor`
- [ ] **Time System**: Implement Daily Timer and Real-Time modes.
- [ ] **Event System**:  `NarrativeManager` `GameMaster` event architecture
- [ ] **Game Master Role**: Expand GM to judge Ethical, Narrative, and World events.
      -[ ] ethical narrative world social business events 
      ~ [ ] the scheduler for all events 
      - [ ] consaquencies , effects, triggers, rewards, states,  storylines
      ~ [ ] event managers are the thing that controls the logistics of events"
        - [ ] ? wonder if we could have the gm or something dilver code for the event manager like if it needs to enforce rules, or change game state or scoring or messaging changing front ends or promts effects if gms events 
      ~ [ ] judge should judge events for scores and effectiveness return suggestion for umprovments to gms events and the game  as well as scores to be added immedialtly to the player /explination or add at end of game cuase irs not a public record
      ~ [ ] judge immplimented  include history and gms \ players whole history  
      - [ ] gm should recieve his own hidtory past planned events internal history  and plan judges suggestions | not player history gm
      - [ ] should not be able to change event based on  eco standing 
      - [ ] should be able to change events based on players actions 
      - [ ] gm able to change events based on players actions 
      - [ ] can test a players- ethics, morals, gullibility, manipulation, persuasion, lying, bribery, loyalty
  - [ ] **Financials**: logic to within the Finance System.
   - [ ] taxes and fees
   - [ ] bank and credit system
   - [ ] loans and debts
   - [ ] insurance
   - [ ] stocks and bonds
   - [ ] real estate
   - [ ] rent utilities and services
   - [ ] payroll 
   - [ ] payments 
   - [ ] advanced dashboard analytics
   - [ ] a exense system and income system 
   - [ ] a budget system 
  - **Public Relations** system for ads promotions discounts things to increase sales traffic public perception and reputation
  -equitment upgrade system
  -service upgrade and creation system with activation and deactivation and costs and effects of those changes [could get help from the gm this could get complex]

  - history / logging system for everythng for through scoring and history we'll neeed to create a format for the history and scoring system 
- neighboor hood, customer system population system  all simular so could combine them 
- communication system  for play to player, llm to llm, play/llm to vendor, vendor to player/llm, group chat, public chat, email, phone, mail, notification. news etc
 

## Calendar System  
**sceduling and reminding of responsibilities**
events schduled and currently happening,
payments payrole
help with realing time human players can plan their turns  and be able to leave the game and still plan their next turns.
```log
2025-12-09 21:23:45,914 | INFO     | calendar:schedule_action:159 - Agent p3 scheduled: Loan Payment Due: $99.12 for Week 2 Day 7
2025-12-09 21:23:45,914 | INFO     | calendar:schedule_action:159 - Agent p3 scheduled: Loan Payment Due: $99.12 for Week 3 Day 7
2025-12-09 21:23:45,914 | INFO     | calendar:schedule_action:159 - Agent p3 scheduled: Loan Payment Due: $99.12 for Week 4 Day 7
2025-12-09 21:23:45,914 | INFO     | calendar:schedule_action:159 - Agent p3 scheduled: Loan Payment Due: $99.12 for Week 5 Day 7
2025-12-09 21:23:45,914 | INFO     | calendar:schedule_action:159 - Agent p3 scheduled: Loan Payment Due: $99.12 for Week 6 Day 7
2025-12-09 21:23:45,914 | INFO     | calendar:schedule_action:159 - Agent p3 scheduled: Loan Payment Due: $99.12 for Week 7 Day 7
2025-12-09 21:23:45,914 | INFO     | calendar:schedule_action:159 - Agent p3 scheduled: Loan Payment Due: $99.12 for Week 8 Day 7
2025-12-09 21:23:45,914 | INFO     | calendar:schedule_action:159 - Agent p3 scheduled: Loan Payment Due: $99.12 for Week 9 Day 7
```
this should noot be automatic the players should schedule based on theyre terms and conditions and the game should only remind them of their responsibilities if they set them upin the calendar it is on them to plan their turns and schedule their actions and track there responsibilities the game should not schedule for them or do it for them  only score them if they dont follow through with their responsibilities

## Engine: Game Architecture (GameEngine)

- [ ] **Event Handling**: Delegate event handling to Game Master/World Event System.
   - and how they will be handled and constructed and implemented with gm and judge
- [ ] **Vendor Handling**: Delegate vendor logic to Game Master/World Vendor System.
     how the vendor system with use the gm for player facing actions
     how the vendor system effects the market ing and inventory dilvery systems
- [ ] **Communication**: Delegate messaging to Game Master Communication System.
     deligatiopn to a gm llm for interactions with seprate historys per agent, or customer or vendor or entity
- [ ] **Action Dispatching**: set up and complete action dispatching system command stratagy with retrievers and handlers
- [ ] **Financial Logic**: Move all financial logic to Finance System. 
- [x] **Configuration**: all game config should be in one place


## Engine: Population

- [ ] **Cohort Model**: Implement Cohort simulation for performance at scale.
  - _User Note_: `# [ ] TODO: implement cohort model at the same time we maybe want to move this to the game master population system that can handle this making cohorts and individual customers when needed keeping notes for memory to keep track of the customers and their preferences and state. along with storylines for the customers and their interactions with the laundromats. so we can have a more dynamic and interesting game experience.`

## Engine: Social

- [ ] **Communication & Judging**: Split Game Master logic into "Judge" vs "GM" roles.
- [ ] **Event Generation**: Use EventManager to generate dilemmas, which are then judged by the GM/Judge.
- [ ] **Event Pipeline**: Unified Social/Narrative event pipeline under GM supervision.

## Server

- [ ] **LLM Action Budget**: Allow LLM agents to perform multiple actions per turn before ending turn.
- [ ] **Code Organization**: Extract business logic 


## World

- [ ] **Logging & Scoring Module**: Centralized history tracking and scoring for Judge/GM analysis.
- [ ] **State Architecture**: Deconstruct `LaundromatState` into component-based architecture.
- [ ] **Serialization**: Implement Pydantic models for auto-serialization.
- [ ] **Types**: Implement Pydantic models for auto-serialization.
- [ ] **Testing**: Implement testing for all components.