import React, { useState, useEffect } from 'react';

interface Scenario {
  name: string;
  description: string;
  difficulty: string;
  weeks: number;
}

interface StartScreenProps {
  onStartGame: (scenarioName: string) => void;
}

const difficultyColors: { [key: string]: string } = {
  easy: '#4CAF50',
  medium: '#FF9800',
  hard: '#f44336',
  chaos: '#9C27B0'
};

const StartScreen: React.FC<StartScreenProps> = ({ onStartGame }) => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('http://localhost:8000/scenarios')
      .then(res => res.json())
      .then(data => {
        setScenarios(data.scenarios);
        setLoading(false);
      })
      .catch(err => {
        console.error("Failed to load scenarios", err);
        setLoading(false);
      });
  }, []);

  const handleStart = async () => {
    if (!selectedScenario) {
      alert("Please select a scenario!");
      return;
    }
    
    await fetch('http://localhost:8000/start_scenario', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ scenario_name: selectedScenario })
    });
    
    onStartGame(selectedScenario);
  };

  if (loading) {
    return <div style={{ textAlign: 'center', padding: '50px' }}>Loading scenarios...</div>;
  }

  return (
    <div style={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      padding: '40px',
      fontFamily: 'Arial, sans-serif'
    }}>
      <div style={{ maxWidth: '900px', margin: '0 auto' }}>
        <header style={{ textAlign: 'center', marginBottom: '40px' }}>
          <h1 style={{ fontSize: '3em', color: 'white', textShadow: '2px 2px 4px rgba(0,0,0,0.3)', marginBottom: '10px' }}>
            🧼 Laundromat Tycoon 2.0
          </h1>
          <p style={{ color: 'rgba(255,255,255,0.9)', fontSize: '1.2em' }}>
            Compete against AI in the ultimate business simulation
          </p>
        </header>

        <div style={{ 
          background: 'white', 
          borderRadius: '16px', 
          padding: '30px',
          boxShadow: '0 10px 40px rgba(0,0,0,0.2)'
        }}>
          <h2 style={{ marginTop: 0, marginBottom: '20px', color: '#333' }}>Select Scenario</h2>
          
          <div style={{ 
            display: 'grid', 
            gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', 
            gap: '15px',
            marginBottom: '30px'
          }}>
            {scenarios.map(scenario => (
              <div 
                key={scenario.name}
                onClick={() => setSelectedScenario(scenario.name)}
                style={{ 
                  border: selectedScenario === scenario.name ? '3px solid #667eea' : '2px solid #ddd',
                  borderRadius: '12px',
                  padding: '20px',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  background: selectedScenario === scenario.name ? '#f0f4ff' : 'white',
                  transform: selectedScenario === scenario.name ? 'scale(1.02)' : 'scale(1)'
                }}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '10px' }}>
                  <h3 style={{ margin: 0, fontSize: '1.1em' }}>
                    {scenario.name.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())}
                  </h3>
                  <span style={{ 
                    background: difficultyColors[scenario.difficulty] || '#888',
                    color: 'white',
                    padding: '3px 10px',
                    borderRadius: '12px',
                    fontSize: '0.75em',
                    fontWeight: 'bold',
                    textTransform: 'uppercase'
                  }}>
                    {scenario.difficulty}
                  </span>
                </div>
                <p style={{ color: '#666', fontSize: '0.9em', margin: 0, lineHeight: 1.4 }}>
                  {scenario.description}
                </p>
                <div style={{ marginTop: '10px', color: '#888', fontSize: '0.8em' }}>
                  📅 {scenario.weeks} weeks
                </div>
              </div>
            ))}
          </div>

          <div style={{ textAlign: 'center' }}>
            <button 
              onClick={handleStart}
              disabled={!selectedScenario}
              style={{ 
                padding: '15px 50px', 
                fontSize: '1.2em', 
                background: selectedScenario ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' : '#ccc',
                color: 'white', 
                border: 'none', 
                borderRadius: '30px', 
                cursor: selectedScenario ? 'pointer' : 'not-allowed',
                fontWeight: 'bold',
                boxShadow: selectedScenario ? '0 4px 15px rgba(102, 126, 234, 0.4)' : 'none',
                transition: 'all 0.3s ease'
              }}
            >
              🎮 Start Game
            </button>
          </div>
        </div>

        <footer style={{ textAlign: 'center', marginTop: '30px', color: 'rgba(255,255,255,0.7)' }}>
          <p>Built for LLM Agent Benchmarking • v2.0</p>
        </footer>
      </div>
    </div>
  );
};

export default StartScreen;
