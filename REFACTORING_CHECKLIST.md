# Refactoring Checklist & Implementation Notes

This document compiles all refactoring suggestions and specific user notes gathered from the project documentation.

## Frontend

- [ ] **State Management**: Evaluate moving from `useState`/`prop drilling` to Redux or Context implementation.
  - _User Note_: `# [ ] should we consider this?`
- [x] **Dashboard Fix**: Resolve Dashboard Component issues.
  - _User Note_: `# ! [x] working as of 12/8`
- [ ] **Turn Handling**: Add daily options alongside real-time/weekly modes.
  - _User Note_: `# [ ] we should have a daily option as well as real time option eventually daily is a must`
- [ ] **Type Safety**: Automate generation of TypeScript interfaces from Python Pydantic models.
  - _User Note_: `# [ ] agreeed lets do this`
- [ ] **Real-time Updates**: Implement WebSockets for state updates (replacing polling).
- [/] **Provider Logic**: Use a Factory pattern for LLM providers.

### Agent Tools Wishlist (Registration Needed)

These tools need to be implemented and added to `src/agents/tools/registry.py` to support the full "Think-Act-React" loop.

#### Information Gathering (Active Perception)

- [ ] `inspect_competitor(competitor_id: str)`: View detailed public stats (price, reputation) of a specific rival.
- [ ] `check_market_trends()`: Get report on global resource prices and demand shifts.
- [ ] `read_news()`: Retrieve active world events and narratives affecting the market.
- [ ] `get_calendar()`: View schedule of upcoming bills, maintenance, and events.

#### Finance & Tycoon Extensions

- [ ] `check_credit_score()`: View current credit rating and borrowing power.
- [ ] `apply_for_loan(amount: float)`: Request capital from the bank.
- [ ] `pay_bill(bill_id: str)`: Pay specific outstanding bills.

#### Management & Operations

- [ ] `schedule_maintenance()`: Pre-emptive repair to lower breakdown chance.
- [ ] `hire_staff(role: str)`: Recruit employees (if staff module active).
- [ ] `manage_staff(action: str, staff_id: str)`: Fire/Promote/Assign staff.

#### Diplomacy & Social

- [ ] `send_dm(recipient: str, content: str, intent: str)`: Enhanced messaging with intent classification.
- [ ] `propose_treaty(target: str, terms: dict)`: Formalize alliances beyond simple text.

## Engine: Commerce

- [ ] **Market System**: Implement full Market/Economy system logic.
  - _User Note_: `# [ ] needs implementation`
- [ ] **Supply Chain**: Implement detailed logistics simulation.
  - _User Note_: `# [ ] needs implementation`
- [ ] **Vendor Order Logic**: Separate concerns by splitting `OrderProcessor` from `Vendor` entity.
  - _User Note_: `# ! agreeed lets do this`

## Engine: Core

- [ ] **Time System**: Implement Daily Timer and Real-Time modes.
  - _User Note_: `# ~ beeds daily timer and real time modes`
- [ ] **Event Architecture**: Refactor `EventManager` in favor of `NarrativeManager` and `GameMaster` control.
  - _User Note_: `# ! agreeed lets do this`
- [ ] **Game Master Role**: Expand GM to judge Ethical, Narrative, and World events.
  - _User Note_: `# [ ] also should be used for ethical events and narrative events world events etc`
  - _User Note_: `# ~ that or the game master should be the scheduler for all types of events and the event manager should be responsible for generating the events and using the other managers to generate the events and then the game master should judged the events and generate the results`
  - _User Note_: `# GM controls event timing/effects/triggers (social, ethical, business, vendor, narrative). Also includes testing behavior (morals, integrity, loyalty). GM uses EventManager to implement history for the Judge (another LLM) to score/analyze/submit state changes. the judge is a unbaised observer, that has to all events , conversations, actions, and decisions with in the game to score/analyze and helps have a complete sense of the game and the benchmark solid and complete`

## Engine: Finance

- [ ] **Integration**: Migrate `_process_financials` logic to `RevenueStream.calculate` within the Finance System.
- [ ] **Naming**: Rename `BankSystem` to `FinancialController`.
  - _User Note_: `# ! agreeed lets do this`

## Engine: Game Architecture (GameEngine)

- [ ] **Event Handling**: Delegate event handling to Game Master/World Event System.
  - _User Note_: `# [ ] this should be handled by the game master world events system`
- [ ] **Vendor Handling**: Delegate vendor logic to Game Master/World Vendor System.
  - _User Note_: `# [ ] this should be handled by the game master world vendors system`
- [ ] **Communication**: Delegate messaging to Game Master Communication System.
  - _User Note_: `# [ ] this should be handled by the game master communication system if not a player or llm player`
- [ ] **Action Dispatching**: specific `ActionType` handlers (Command Pattern) for `_apply_action`.
  - _User Note_: `# TODO: i like the command pattern idea each command has a handler and a receiver`
- [ ] **Financial Logic**: Move `_process_financials` complexity to Finance/Economy system.
  - _User Note_: `# [ ] TODO: move to financial system or economy system`
- [ ] **Configuration**: Externalize hardcoded magic numbers to `GameBalanceConfig`.
  - _User Note_: `# [ ] TODO: move to game config so when we add different game modes we can change these values without touching the code`

## Engine: Population

- [ ] **Cohort Model**: Implement Cohort simulation for performance at scale.
  - _User Note_: `# [ ] TODO: implement cohort model at the same time we maybe want to move this to the game master population system that can handle this making cohorts and individual customers when needed keeping notes for memory to keep track of the customers and their preferences and state. along with storylines for the customers and their interactions with the laundromats. so we can have a more dynamic and interesting game experience.`

## Engine: Social

- [ ] **Communication & Judging**: Split Game Master logic into "Judge" vs "GM" roles.
  - _User Note_: `# the judge should also be callled in this scents maybe we split the game master into a judge and a game master`
- [ ] **Event Generation**: Use EventManager to generate dilemmas, which are then judged by the GM/Judge.
  - _User Note_: `# used by event manager to generate dilemmas and the eventmanager is used by the game master to generate events and gets judged by the judge once implemented`
- [ ] **Event Pipeline**: Unified Social/Narrative event pipeline under GM supervision.
  - _User Note_: `# and this should be used by the game master to generate events and gets judged by the judge once implemented`

## Server

- [ ] **LLM Action Budget**: Allow LLM agents to perform multiple actions per turn before ending turn.
  - _User Note_: `# we should d allow fo rthe llm to jhave more then one action so they have moer time to thjink and complete the thing want to becalling end turn`
- [ ] **Code Organization**: Extract business logic (serialization, logging) out of `server.py`.
  - _User Note_: `# ! good lets do that`

## World

- [ ] **Logging & Scoring Module**: Centralized history tracking and scoring for Judge/GM analysis.
  - _User Note_: `# need a logging / history / scoring module`
- [ ] **State Architecture**: Deconstruct `LaundromatState` into component-based architecture.
  - _User Note_: `# [ ] TOD) lets get some models and components setup for the laundromat state system keep in mind we want to be able to have multiple laundromats in the world and each one should have its own state. to some extent its each player has there state and that hold their laundromats and the laundromats have their own state. and then theres the game state, world state, and financial state.`
- [ ] **Serialization**: Implement Pydantic models for auto-serialization.
  - _User Note_: `# [ ] TODO pydantic models maybe a good idea but we need to make sure we can handle the nested objects and relationships between them.`
