import json
import os

def generate_dashboard(log_file="simulation_log.json", output_file="dashboard.html"):
    if not os.path.exists(log_file):
        print(f"Error: {log_file} not found.")
        return

    with open(log_file, "r") as f:
        data = json.load(f)

    weeks = data["weeks"]
    agents = data["agents"]
    
    # Prepare datasets for Chart.js
    datasets_balance = []
    datasets_visits = []
    
    colors = ["#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF"]
    
    for i, (pid, stats) in enumerate(agents.items()):
        color = colors[i % len(colors)]
        datasets_balance.append({
            "label": f"{pid} Balance",
            "data": stats["balance"],
            "borderColor": color,
            "fill": False
        })
        datasets_visits.append({
            "label": f"{pid} Visits",
            "data": stats["visits"],
            "borderColor": color,
            "fill": False
        })

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Laundromat Tycoon Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{ font-family: sans-serif; padding: 20px; }}
        .chart-container {{ width: 80%; margin: 20px auto; }}
    </style>
</head>
<body>
    <h1>Laundromat Tycoon Results</h1>
    
    <div class="chart-container">
        <h2>Balance Over Time</h2>
        <canvas id="balanceChart"></canvas>
    </div>
    
    <div class="chart-container">
        <h2>Weekly Visits</h2>
        <canvas id="visitsChart"></canvas>
    </div>

    <script>
        const weeks = {json.dumps(weeks)};
        
        new Chart(document.getElementById('balanceChart'), {{
            type: 'line',
            data: {{
                labels: weeks,
                datasets: {json.dumps(datasets_balance)}
            }}
        }});
        
        new Chart(document.getElementById('visitsChart'), {{
            type: 'line',
            data: {{
                labels: weeks,
                datasets: {json.dumps(datasets_visits)}
            }}
        }});
    </script>
</body>
</html>
"""
    
    with open(output_file, "w") as f:
        f.write(html_content)
    print(f"Dashboard generated at {output_file}")

if __name__ == "__main__":
    generate_dashboard()
