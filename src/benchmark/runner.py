import json
import random
import os
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

from src.benchmark.scenarios import Scenario, get_scenario
from src.engine.core.time import TimeSystem
from src.engine.population.customer import Customer
from src.engine.core.events import EventManager
from src.engine.commerce.vendor import Vendor
from src.world.laundromat import LaundromatState, Machine
from src.world.ticket import TicketStatus
from src.agents.base_agent import BaseAgent, Observation, ActionType
from src.engine.scoring import ScoringSystem


@dataclass
class RunResult:
    """Results from a single simulation run"""
    scenario: str
    agent_id: str
    agent_name: str
    final_balance: float
    final_social_score: float
    final_reputation: float
    total_revenue: float
    total_visits: int
    final_score: float
    rank: int  # 1st, 2nd, 3rd place


@dataclass
class BenchmarkResult:
    """Aggregated results across multiple runs"""
    scenario: str
    agent_id: str
    agent_name: str
    num_runs: int
    mean_score: float
    std_score: float
    mean_balance: float
    std_balance: float
    wins: int  # How many times ranked 1st
    avg_rank: float
    timestamp: str


class BenchmarkRunner:
    """Run benchmark scenarios and evaluate agent performance"""
    
    def __init__(self, output_dir: str = "results"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def run_scenario(self, scenario: Scenario, agents: List[BaseAgent], num_runs: int = 10) -> List[BenchmarkResult]:
        """
        Run a scenario multiple times with the same agents
        Returns aggregated results for each agent
        """
        print(f"\n{'='*60}")
        print(f"Running Scenario: {scenario.name} ({num_runs} runs)")
        print(f"{'='*60}")
        
        all_run_results = []
        
        for run_idx in range(num_runs):
            print(f"\n--- Run {run_idx + 1}/{num_runs} ---")
            run_results = self._execute_single_run(scenario, agents, run_idx)
            all_run_results.extend(run_results)
        
        # Aggregate results by agent
        aggregated = self._aggregate_results(all_run_results, num_runs)
        
        # Save results
        self._save_results(scenario.name, aggregated)
        
        # Print summary
        self._print_summary(scenario.name, aggregated)
        
        return aggregated
    
    def _execute_single_run(self, scenario: Scenario, agents: List[BaseAgent], run_idx: int) -> List[RunResult]:
        """Execute a single simulation run"""
        # Set seed for reproducibility
        seed = scenario.seed + run_idx
        random.seed(seed)
        
        # Initialize game state
        time_system = TimeSystem(total_weeks=scenario.weeks)
        event_manager = EventManager()
        vendor = Vendor()
        
        # Initialize laundromats from scenario
        laundromats = {}
        for agent in agents:
            if agent.id == "p1":
                init = scenario.p1_initial
            elif agent.id == "p2":
                init = scenario.p2_initial
            else:
                init = scenario.p3_initial
            
            # Create machine list from count
            machine_list = []
            for m_idx in range(init.machines):
                # Simple logic: 2/3 washers, 1/3 dryers
                m_type = "standard_washer" if m_idx % 3 != 0 else "standard_dryer"
                machine_list.append(Machine(id=f"M{m_idx}", type=m_type))

            laundromats[agent.id] = LaundromatState(
                id=agent.id,
                name=agent.name,
                balance=init.balance,
                machines=machine_list,
                price=init.price,
                social_score=init.social_score,
                inventory=init.inventory.copy()
            )
        
        # Initialize customers
        customers = [Customer(f"c{i}") for i in range(50)]
        
        # Track metrics
        cumulative_revenue = {aid: 0.0 for aid in laundromats}
        cumulative_visits = {aid: 0 for aid in laundromats}
        
        # Simulation loop
        while True:
            # Agent decisions
            for agent in agents:
                my_state = laundromats[agent.id]
                competitors = [laundromats[k] for k in laundromats if k != agent.id]
                
                obs = Observation(
                    week=time_system.current_week,
                    season=time_system.current_season.value,
                    my_stats=my_state.__dict__,
                    competitor_stats=[c.__dict__ for c in competitors],
                    messages=[],
                    events=[]
                )
                
                action = agent.decide_action(obs)
                self._apply_action(my_state, action, vendor)
            
            # Customer simulation
            weekly_revenue = {aid: 0.0 for aid in laundromats}
            weekly_visits = {aid: 0 for aid in laundromats}
            
            laundromat_list = list(laundromats.values())
            for customer in customers:
                choice = customer.decide_laundromat(laundromat_list)
                if choice:
                    success = customer.visit_laundromat(choice, time_system.current_week)
                    if success:
                        weekly_visits[choice.id] += 1
                        weekly_revenue[choice.id] += choice.price
                        customer.record_experience(choice.id, random.random() > 0.1, time_system.current_week)
            
            # Update laundromats
            for aid, p in laundromats.items():
                revenue = weekly_revenue[aid]
                expenses = 100
                p.process_week(revenue, expenses)
                
                cumulative_revenue[aid] += revenue
                cumulative_visits[aid] += weekly_visits[aid]
            
            # Advance time
            vendor.update_market(time_system.current_week)
            if not time_system.advance_week():
                break
        
        # Calculate scores and rankings
        laundromat_list = list(laundromats.values())
        final_scores = ScoringSystem.calculate_final_scores(laundromat_list, cumulative_visits)
        
        # Sort by score
        ranked_agents = sorted(final_scores.items(), key=lambda x: x[1]['total'], reverse=True)
        
        # Create run results
        results = []
        for rank, (aid, score_data) in enumerate(ranked_agents, 1):
            p = laundromats[aid]
            results.append(RunResult(
                scenario=scenario.name,
                agent_id=aid,
                agent_name=p.name,
                final_balance=p.balance,
                final_social_score=p.social_score,
                final_reputation=p.reputation,
                total_revenue=cumulative_revenue[aid],
                total_visits=cumulative_visits[aid],
                final_score=score_data['total'],
                rank=rank
            ))
        
        return results
    
    def _apply_action(self, state: LaundromatState, action, vendor):
        """Apply an agent's action to their laundromat state"""
        if action.type == ActionType.SET_PRICE:
            state.price = action.parameters.get("price", state.price)
        elif action.type == ActionType.BUY_SUPPLIES:
            item = action.parameters.get("item")
            qty = action.parameters.get("quantity", 0)
            unit_price = vendor.get_price(item)
            cost = qty * unit_price
            if state.balance >= cost:
                state.balance -= cost
                state.inventory[item] = state.inventory.get(item, 0) + qty
        elif action.type == ActionType.RESOLVE_TICKET:
            ticket_id = action.parameters.get("ticket_id")
            for t in state.tickets:
                if t.id == ticket_id and t.status == TicketStatus.OPEN:
                    t.status = TicketStatus.RESOLVED
                    state.social_score += 2
        elif action.type == ActionType.UPGRADE_MACHINE:
            if state.balance >= 500:
                state.balance -= 500
                state.machines += 1
        elif action.type == ActionType.MARKETING_CAMPAIGN:
            cost = action.parameters.get("cost", 0)
            if state.balance >= cost:
                state.balance -= cost
                boost = cost / 50.0
                state.update_social_score(boost)
    
    def _aggregate_results(self, run_results: List[RunResult], num_runs: int) -> List[BenchmarkResult]:
        """Aggregate results across multiple runs"""
        # Group by agent
        agent_results = {}
        for result in run_results:
            if result.agent_id not in agent_results:
                agent_results[result.agent_id] = []
            agent_results[result.agent_id].append(result)
        
        # Calculate statistics
        aggregated = []
        for agent_id, results in agent_results.items():
            scores = [r.final_score for r in results]
            balances = [r.final_balance for r in results]
            ranks = [r.rank for r in results]
            wins = sum(1 for r in results if r.rank == 1)
            
            import statistics
            aggregated.append(BenchmarkResult(
                scenario=results[0].scenario,
                agent_id=agent_id,
                agent_name=results[0].agent_name,
                num_runs=len(results),
                mean_score=statistics.mean(scores),
                std_score=statistics.stdev(scores) if len(scores) > 1 else 0,
                mean_balance=statistics.mean(balances),
                std_balance=statistics.stdev(balances) if len(balances) > 1 else 0,
                wins=wins,
                avg_rank=statistics.mean(ranks),
                timestamp=datetime.now().isoformat()
            ))
        
        return sorted(aggregated, key=lambda x: x.mean_score, reverse=True)
    
    def _save_results(self, scenario_name: str, results: List[BenchmarkResult]):
        """Save results to JSON file"""
        filepath = os.path.join(self.output_dir, f"{scenario_name}_results.json")
        data = [asdict(r) for r in results]
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\nResults saved to: {filepath}")
    
    def _print_summary(self, scenario_name: str, results: List[BenchmarkResult]):
        """Print summary of results"""
        print(f"\n{'='*60}")
        print(f"SCENARIO: {scenario_name} - RESULTS")
        print(f"{'='*60}")
        print(f"{'Agent':<20} {'Mean Score':>12} {'Wins':>6} {'Avg Rank':>10}")
        print(f"{'-'*60}")
        for r in results:
            print(f"{r.agent_name:<20} {r.mean_score:>12.1f} {r.wins:>6} {r.avg_rank:>10.2f}")
        print(f"{'='*60}\n")


def update_leaderboard(results_dir: str = "results", leaderboard_file: str = "leaderboard.json"):
    """Aggregate all results into a global leaderboard"""
    all_results = []
    
    # Load all result files
    for filename in os.listdir(results_dir):
        if filename.endswith("_results.json"):
            filepath = os.path.join(results_dir, filename)
            with open(filepath, 'r') as f:
                all_results.extend(json.load(f))
    
    # Calculate overall rankings
    agent_stats = {}
    for result in all_results:
        aid = result['agent_id']
        if aid not in agent_stats:
            agent_stats[aid] = {
                'name': result['agent_name'],
                'total_wins': 0,
                'total_runs': 0,
                'scenarios_won': []
            }
        
        agent_stats[aid]['total_wins'] += result['wins']
        agent_stats[aid]['total_runs'] += result['num_runs']
        if result['wins'] > 0:
            agent_stats[aid]['scenarios_won'].append(result['scenario'])
    
    # Save leaderboard
    leaderboard_path = os.path.join(results_dir, leaderboard_file)
    with open(leaderboard_path, 'w') as f:
        json.dump(agent_stats, f, indent=2)
    
    print(f"Leaderboard saved to: {leaderboard_path}")
