import React, { useState, useEffect } from 'react';
import './HistoryViewer.css';

interface ComparisonData {
  participants: Record<string, {
    name: string;
    is_human: boolean;
    total_actions: number;
    action_breakdown: Record<string, number>;
    thinking_samples: string[];
    balance_trajectory: { week: number; balance: number }[];
    initial_balance: number;
    final_balance: number;
    balance_change: number;
    final_social_score: number;
  }>;
  summary: {
    total_participants: number;
    total_weeks_played: number;
    winner: string;
    most_active: string;
  };
}

interface HistoryViewerProps {
  isOpen: boolean;
  onClose: () => void;
}

export const HistoryViewer: React.FC<HistoryViewerProps> = ({ isOpen, onClose }) => {
  const [comparison, setComparison] = useState<ComparisonData | null>(null);
  const [thinkingTimeline, setThinkingTimeline] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'comparison' | 'timeline' | 'export'>('comparison');
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    if (isOpen) {
      fetchData();
    }
  }, [isOpen]);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [compRes, thinkRes] = await Promise.all([
        fetch('http://localhost:8000/history/comparison'),
        fetch('http://localhost:8000/history/thinking')
      ]);
      
      // Check if responses are OK
      if (!compRes.ok || !thinkRes.ok) {
        console.warn('[HistoryViewer] History endpoints not available yet');
        setComparison({ participants: {}, summary: { total_participants: 0, total_weeks_played: 0, winner: '', most_active: '' } });
        setThinkingTimeline([]);
        setLoading(false);
        return;
      }
      
      const compData = await compRes.json();
      const thinkData = await thinkRes.json();
      
      console.log('[HistoryViewer] Comparison data:', compData);
      console.log('[HistoryViewer] Participants count:', Object.keys(compData.participants || {}).length);
      
      setComparison(compData);
      setThinkingTimeline(thinkData.timeline || []);
    } catch (error) {
      console.error('Failed to fetch history:', error);
      // Set empty data instead of leaving it null
      setComparison({ participants: {}, summary: { total_participants: 0, total_weeks_played: 0, winner: '', most_active: '' } });
      setThinkingTimeline([]);
    } finally {
      setLoading(false);
    }
  };

  const handleExport = async () => {
    setExporting(true);
    try {
      const timestamp = new Date().toISOString().split('T')[0];
      const response = await fetch(`http://localhost:8000/history/export?filename=game_${timestamp}.json`, {
        method: 'POST'
      });
      const result = await response.json();
      alert(`History exported to: ${result.path}`);
    } catch (error) {
      console.error('Export failed:', error);
      alert('Export failed. Check console for details.');
    } finally {
      setExporting(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="history-modal-overlay" onClick={onClose}>
      <div className="history-modal" onClick={e => e.stopPropagation()}>
        <div className="modal-header">
          <h2>📊 Game History & Analysis</h2>
          <button className="close-btn" onClick={onClose}>×</button>
        </div>

        <div className="tab-bar">
          <button 
            className={`tab ${activeTab === 'comparison' ? 'active' : ''}`}
            onClick={() => setActiveTab('comparison')}
          >
            🏆 Comparison
          </button>
          <button 
            className={`tab ${activeTab === 'timeline' ? 'active' : ''}`}
            onClick={() => setActiveTab('timeline')}
          >
            💭 Thinking Timeline
          </button>
          <button 
            className={`tab ${activeTab === 'export' ? 'active' : ''}`}
            onClick={() => setActiveTab('export')}
          >
            📥 Export
          </button>
        </div>

        <div className="modal-content">
          {loading ? (
            <div className="loading">Loading history data...</div>
          ) : (
            <>
              {activeTab === 'comparison' && (
                comparison && Object.keys(comparison.participants || {}).length > 0 ? (
                  <ComparisonView data={comparison} />
                ) : (
                  <div className="empty-state" style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    padding: '3rem',
                    color: '#6b7280'
                  }}>
                    <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📊</div>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 'bold', marginBottom: '0.5rem', color: '#374151' }}>
                      No History Yet
                    </h3>
                    <p style={{ textAlign: 'center', maxWidth: '400px' }}>
                      Start playing the game and click "Next Week" to begin tracking your business performance!
                    </p>
                  </div>
                )
              )}
              {activeTab === 'timeline' && (
                <TimelineView timeline={thinkingTimeline} />
              )}
              {activeTab === 'export' && (
                <ExportView onExport={handleExport} exporting={exporting} />
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

const ComparisonView: React.FC<{ data: ComparisonData }> = ({ data }) => {
  const participants = Object.entries(data.participants);
  
  return (
    <div className="comparison-view">
      {data.summary && (
        <div className="summary-cards">
          <div className="summary-card winner">
            <span className="card-label">🏆 Winner</span>
            <span className="card-value">{data.participants[data.summary.winner]?.name || 'N/A'}</span>
          </div>
          <div className="summary-card">
            <span className="card-label">📅 Weeks Played</span>
            <span className="card-value">{data.summary.total_weeks_played}</span>
          </div>
          <div className="summary-card">
            <span className="card-label">⚡ Most Active</span>
            <span className="card-value">{data.participants[data.summary.most_active]?.name || 'N/A'}</span>
          </div>
        </div>
      )}

      <div className="participants-grid">
        {participants.map(([id, p]) => (
          <div key={id} className={`participant-card ${p.is_human ? 'human' : 'ai'}`}>
            <div className="card-header">
              <span className="participant-name">{p.name}</span>
              <span className="participant-type">{p.is_human ? '👤 Human' : '🤖 AI'}</span>
            </div>
            
            <div className="stats-row">
              <div className="stat">
                <span className="stat-label">Final Balance</span>
                <span className={`stat-value ${p.balance_change >= 0 ? 'positive' : 'negative'}`}>
                  ${p.final_balance.toFixed(0)}
                </span>
              </div>
              <div className="stat">
                <span className="stat-label">Change</span>
                <span className={`stat-value ${p.balance_change >= 0 ? 'positive' : 'negative'}`}>
                  {p.balance_change >= 0 ? '+' : ''}${p.balance_change.toFixed(0)}
                </span>
              </div>
            </div>
            
            <div className="stat">
              <span className="stat-label">Social Score</span>
              <span className="stat-value">{p.final_social_score}/100</span>
            </div>
            
            <div className="stat">
              <span className="stat-label">Total Actions</span>
              <span className="stat-value">{p.total_actions}</span>
            </div>
            
            {p.action_breakdown && Object.keys(p.action_breakdown).length > 0 && (
              <div className="action-breakdown">
                <span className="breakdown-label">Actions Breakdown:</span>
                <div className="breakdown-chips">
                  {Object.entries(p.action_breakdown).map(([action, count]) => (
                    <span key={action} className="breakdown-chip">
                      {action}: {count}
                    </span>
                  ))}
                </div>
              </div>
            )}
            
            {p.thinking_samples && p.thinking_samples.length > 0 && (
              <div className="thinking-preview">
                <span className="preview-label">Sample Thoughts:</span>
                <ul>
                  {p.thinking_samples.slice(0, 3).map((thought, idx) => (
                    <li key={idx}>{thought.slice(0, 100)}...</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

const TimelineView: React.FC<{ timeline: any[] }> = ({ timeline }) => {
  const [filter, setFilter] = useState<string>('all');
  
  const agents = Array.from(new Set(timeline.map(t => t.agent_id)));
  const filtered = filter === 'all' 
    ? timeline 
    : timeline.filter(t => t.agent_id === filter);

  return (
    <div className="timeline-view">
      <div className="timeline-filters">
        <button 
          className={`filter-btn ${filter === 'all' ? 'active' : ''}`}
          onClick={() => setFilter('all')}
        >
          All
        </button>
        {agents.map(agent => (
          <button
            key={agent}
            className={`filter-btn ${filter === agent ? 'active' : ''}`}
            onClick={() => setFilter(agent)}
          >
            {agent}
          </button>
        ))}
      </div>
      
      <div className="timeline-list">
        {filtered.length === 0 ? (
          <div className="empty-state">No thinking recorded yet</div>
        ) : (
          filtered.map((item, idx) => (
            <div key={idx} className="timeline-item">
              <div className="item-header">
                <span className="week-badge">Week {item.week}</span>
                <span className="agent-name">{item.agent_name}</span>
                <div className="action-list">
                  {item.actions_taken?.map((a: string, i: number) => (
                    <span key={i} className="action-mini">{a}</span>
                  ))}
                </div>
              </div>
              <div className="item-thoughts">
                {item.thinking?.map((thought: string, i: number) => (
                  <p key={i} className="thought-text">{thought}</p>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};

const ExportView: React.FC<{ onExport: () => void; exporting: boolean }> = ({ 
  onExport, 
  exporting 
}) => {
  return (
    <div className="export-view">
      <div className="export-info">
        <h3>📥 Export Game History</h3>
        <p>
          Export the complete game history to a JSON file for analysis.
          This includes all turns, thinking processes, actions, and state changes.
        </p>
        <ul>
          <li>All participant turns with timestamps</li>
          <li>Full thinking content from AI agents</li>
          <li>Complete action log with parameters</li>
          <li>State snapshots (before/after each turn)</li>
          <li>Competitor context for each decision</li>
        </ul>
      </div>
      <button 
        className="export-btn"
        onClick={onExport}
        disabled={exporting}
      >
        {exporting ? 'Exporting...' : '📥 Export to JSON'}
      </button>
    </div>
  );
};

export default HistoryViewer;
