from src.agents.base_agent import BaseAgent, Observation, Action, ActionType

class HumanAgent(BaseAgent):
    def decide_action(self, observation: Observation) -> Action:
        print(f"\n--- Agent: {self.name} (Week {observation.week}) ---")
        print(f"Stats: Balance=${observation.my_stats['balance']:.2f}, "
              f"Reputation={observation.my_stats['reputation']:.1f}, "
              f"Price=${observation.my_stats['price']:.2f}")
        
        print("\nAvailable Actions:")
        print("1. Set Price (price)")
        print("2. Run Marketing (cost)")
        print("3. Upgrade Machine (cost)")
        print("4. Send Message (recipient_id content...)")
        print("5. Buy Supplies (item quantity)")
        print("   Items: detergent, softener, parts, cleaning_supplies")
        print("6. Resolve Ticket (ticket_id)")
        print("7. Wait")
        
        while True:
            choice = input("Enter action (e.g., '1 5.50' or '7'): ").strip().split()
            if not choice:
                continue
                
            cmd = choice[0]
            
            if cmd == "1" and len(choice) > 1:
                try:
                    price = float(choice[1])
                    return Action(ActionType.SET_PRICE, {"price": price})
                except ValueError:
                    print("Invalid price.")
            elif cmd == "2" and len(choice) > 1:
                try:
                    cost = float(choice[1])
                    return Action(ActionType.MARKETING_CAMPAIGN, {"cost": cost})
                except ValueError:
                    print("Invalid cost.")
            elif cmd == "3":
                return Action(ActionType.UPGRADE_MACHINE)
            elif cmd == "4" and len(choice) > 2:
                recipient = choice[1]
                content = " ".join(choice[2:])
                return Action(ActionType.SEND_MESSAGE, {"recipient_id": recipient, "content": content})
            elif cmd == "5" and len(choice) > 2:
                item = choice[1]
                try:
                    qty = int(choice[2])
                    return Action(ActionType.BUY_SUPPLIES, {"item": item, "quantity": qty})
                except ValueError:
                    print("Invalid quantity.")
            elif cmd == "6" and len(choice) > 1:
                ticket_id = choice[1]
                return Action(ActionType.RESOLVE_TICKET, {"ticket_id": ticket_id})
            elif cmd == "7":
                return Action(ActionType.WAIT)
            else:
                print("Invalid command. Try again.")
