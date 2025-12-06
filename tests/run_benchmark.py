"""
Example script showing how to run benchmarks

Usage:
    python run_benchmark.py --scenario stable_market --runs 10
    python run_benchmark.py --all  # Run all scenarios
"""
import sys
import argparse
import os

# Add project root to path so we can find src module
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from src.benchmark.runner import BenchmarkRunner, update_leaderboard
from src.benchmark.scenarios import get_scenario, list_scenarios
from src.agents.rule_based import AggressivePricer, ConservativeAgent, QualityFocusedAgent


def main():
    parser = argparse.ArgumentParser(description="Run benchmark scenarios")
    parser.add_argument("--scenario", type=str, help="Scenario name to run")
    parser.add_argument("--all", action="store_true", help="Run all scenarios")
    parser.add_argument("--runs", type=int, default=10, help="Number of runs per scenario")
    args = parser.parse_args()
    
    # Create agents
    agents = [
        AggressivePricer("p1", "Aggressive Pricer"),
        ConservativeAgent("p2", "Conservative"),
        QualityFocusedAgent("p3", "Quality Focused")
    ]
    
    runner = BenchmarkRunner(output_dir="results")
    
    if args.all:
        # Run all scenarios
        scenarios = list_scenarios()
        for scenario_name in scenarios:
            scenario = get_scenario(scenario_name)
            runner.run_scenario(scenario, agents, num_runs=args.runs)
    elif args.scenario:
        # Run specific scenario
        scenario = get_scenario(args.scenario)
        runner.run_scenario(scenario, agents, num_runs=args.runs)
    else:
        print("Please specify --scenario <name> or --all")
        print(f"Available scenarios: {', '.join(list_scenarios())}")
        sys.exit(1)
    
    # Update global leaderboard
    update_leaderboard()
    print("\n✅ Benchmark complete! Check results/ directory for output.")


if __name__ == "__main__":
    main()
