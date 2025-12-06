import React, { useState, useEffect } from 'react';
import './ScenarioSelector.css';

interface Scenario {
  name: string;
  description: string;
  difficulty: string;
  weeks: number;
}

interface ScenarioSelectorProps {
  onSelect: (scenarioName: string | null) => void;
  currentScenario?: string | null;
}

export const ScenarioSelector: React.FC<ScenarioSelectorProps> = ({ 
  onSelect, 
  currentScenario 
}) => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedScenario, setSelectedScenario] = useState<string | null>(currentScenario || null);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    fetchScenarios();
  }, []);

  const fetchScenarios = async () => {
    try {
      const response = await fetch('http://localhost:8000/scenarios');
      const data = await response.json();
      setScenarios(data.scenarios || []);
    } catch (error) {
      console.error('Failed to fetch scenarios:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSelect = (scenarioName: string | null) => {
    setSelectedScenario(scenarioName);
    setIsOpen(false);
    onSelect(scenarioName);
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return '#4ade80';
      case 'medium': return '#facc15';
      case 'hard': return '#f87171';
      case 'chaos': return '#a855f7';
      default: return '#888';
    }
  };

  const getDifficultyEmoji = (difficulty: string) => {
    switch (difficulty) {
      case 'easy': return '🌱';
      case 'medium': return '⚡';
      case 'hard': return '🔥';
      case 'chaos': return '💀';
      default: return '❓';
    }
  };

  if (loading) {
    return <div className="scenario-selector loading">Loading scenarios...</div>;
  }

  return (
    <div className="scenario-selector">
      <button 
        className="selector-trigger" 
        onClick={() => setIsOpen(!isOpen)}
      >
        <span className="trigger-label">
          📋 {selectedScenario || 'Free Play'}
        </span>
        <span className="trigger-arrow">{isOpen ? '▲' : '▼'}</span>
      </button>
      
      {isOpen && (
        <div className="scenario-dropdown">
          <div className="dropdown-header">
            <h4>Select Scenario</h4>
            <p>Choose a starting challenge</p>
          </div>
          
          <div 
            className={`scenario-option free-play ${!selectedScenario ? 'selected' : ''}`}
            onClick={() => handleSelect(null)}
          >
            <div className="option-icon">🎮</div>
            <div className="option-content">
              <span className="option-name">Free Play</span>
              <span className="option-desc">Standard game with default settings</span>
            </div>
          </div>
          
          {scenarios.map((scenario) => (
            <div 
              key={scenario.name}
              className={`scenario-option ${selectedScenario === scenario.name ? 'selected' : ''}`}
              onClick={() => handleSelect(scenario.name)}
            >
              <div 
                className="option-icon"
                style={{ color: getDifficultyColor(scenario.difficulty) }}
              >
                {getDifficultyEmoji(scenario.difficulty)}
              </div>
              <div className="option-content">
                <div className="option-header">
                  <span className="option-name">{scenario.name.replace(/_/g, ' ')}</span>
                  <span 
                    className="difficulty-badge"
                    style={{ background: getDifficultyColor(scenario.difficulty) }}
                  >
                    {scenario.difficulty}
                  </span>
                </div>
                <span className="option-desc">{scenario.description}</span>
                <span className="option-weeks">{scenario.weeks} weeks</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default ScenarioSelector;
