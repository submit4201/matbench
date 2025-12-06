import React, { useState } from 'react';
import './AIThinkingPanel.css';

interface AIThought {
  name: string;
  thinking: string[];
  actions: string[];
  raw_response?: string;  // Full LLM output for debugging
}

interface AIThoughtsPanelProps {
  thoughts: Record<string, AIThought>;
  isExpanded?: boolean;
  onToggle?: () => void;
}

export const AIThinkingPanel: React.FC<AIThoughtsPanelProps> = ({ 
  thoughts, 
  isExpanded = true,
  onToggle 
}) => {
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [showRaw, setShowRaw] = useState(false);

  const agents = Object.entries(thoughts);

  const handleCopyRaw = (text: string) => {
    navigator.clipboard.writeText(text);
    // Could add a toast notification here
  };

  if (agents.length === 0) {
    return (
      <div className="ai-thinking-panel empty">
        <div className="panel-header">
          <h3>🤖 AI Insights</h3>
          <button className="toggle-btn" onClick={onToggle}>
            {isExpanded ? '−' : '+'}
          </button>
        </div>
        {isExpanded && (
          <div className="panel-content">
            <p className="no-thoughts">No AI activity this turn</p>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`ai-thinking-panel ${isExpanded ? 'expanded' : 'collapsed'}`}>
      <div className="panel-header">
        <h3>🤖 AI Insights</h3>
        <button className="toggle-btn" onClick={onToggle}>
          {isExpanded ? '−' : '+'}
        </button>
      </div>
      
      {isExpanded && (
        <div className="panel-content">
          <div className="agent-tabs">
            {agents.map(([id, agent]) => (
              <button 
                key={id}
                className={`agent-tab ${selectedAgent === id ? 'active' : ''}`}
                onClick={() => setSelectedAgent(selectedAgent === id ? null : id)}
              >
                {agent.name}
              </button>
            ))}
          </div>
          
          {selectedAgent && thoughts[selectedAgent] && (
            <div className="thought-detail">
              <div className="thinking-section">
                <h4>💭 Thinking</h4>
                {thoughts[selectedAgent].thinking.length > 0 ? (
                  <ul className="thinking-list">
                    {thoughts[selectedAgent].thinking.map((thought, idx) => (
                      <li key={idx} className="thought-item">{thought}</li>
                    ))}
                  </ul>
                ) : (
                  <p className="no-content">No thoughts captured</p>
                )}
              </div>
              
              <div className="actions-section">
                <h4>⚡ Actions Taken</h4>
                {thoughts[selectedAgent].actions.length > 0 ? (
                  <div className="action-chips">
                    {thoughts[selectedAgent].actions.map((action, idx) => (
                      <span key={idx} className="action-chip">{action}</span>
                    ))}
                  </div>
                ) : (
                  <p className="no-content">No actions</p>
                )}
              </div>

              {/* Raw Response Section for Debugging */}
              <div className="raw-section">
                <div className="raw-header">
                  <h4>🔧 Raw LLM Response</h4>
                  <button 
                    className="raw-toggle-btn"
                    onClick={() => setShowRaw(!showRaw)}
                  >
                    {showRaw ? 'Hide' : 'Show'}
                  </button>
                </div>
                {showRaw && thoughts[selectedAgent].raw_response && (
                  <div className="raw-content">
                    <button 
                      className="copy-btn"
                      onClick={() => handleCopyRaw(thoughts[selectedAgent].raw_response || '')}
                      title="Copy to clipboard"
                    >
                      📋 Copy
                    </button>
                    <pre className="raw-response">
                      {thoughts[selectedAgent].raw_response}
                    </pre>
                  </div>
                )}
                {showRaw && !thoughts[selectedAgent].raw_response && (
                  <p className="no-content">No raw response available</p>
                )}
              </div>
            </div>
          )}
          
          {!selectedAgent && (
            <div className="summary-view">
              {agents.map(([id, agent]) => (
                <div key={id} className="agent-summary">
                  <span className="agent-name">{agent.name}</span>
                  <span className="action-count">
                    {agent.actions.length} action{agent.actions.length !== 1 ? 's' : ''}
                  </span>
                  <span className="thought-preview">
                    {agent.thinking[0]?.slice(0, 50) || 'No thoughts'}...
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default AIThinkingPanel;

