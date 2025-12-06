import React, { useState } from 'react';
import { Terminal, Bug, Activity, Database, AlertCircle, X } from 'lucide-react';
import type { Laundromat, GameState } from '../types';

interface DebugPanelProps {
  laundromat: Laundromat;
  gameState: GameState;
  onClose: () => void;
}

const DebugPanel: React.FC<DebugPanelProps> = ({ laundromat, gameState, onClose }) => {
  const [activeTab, setActiveTab] = useState<'state' | 'social' | 'events'>('state');

  const getSocialComponents = () => {
    if (typeof laundromat.social_score === 'number') return null;
    return laundromat.social_score.components;
  };

  const socialComponents = getSocialComponents();

  return (
    <div className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-center justify-center p-8">
      <div className="bg-slate-900 w-full max-w-5xl h-[80vh] rounded-2xl shadow-2xl border border-slate-700 flex flex-col overflow-hidden text-slate-300 font-mono">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-700 bg-slate-950">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-red-500/10 rounded-lg flex items-center justify-center border border-red-500/20">
              <Bug className="text-red-500" size={20} />
            </div>
            <div>
              <h2 className="text-lg font-bold text-slate-100">Debug Console</h2>
              <p className="text-xs text-slate-500">System Internals Monitor</p>
            </div>
          </div>
          <button 
            onClick={onClose}
            className="p-2 hover:bg-slate-800 rounded-lg transition-colors text-slate-400 hover:text-white"
          >
            <X size={20} />
          </button>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-slate-700 bg-slate-900/50">
          <button
            onClick={() => setActiveTab('state')}
            className={`px-6 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'state' 
                ? 'border-blue-500 text-blue-400 bg-blue-500/5' 
                : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
          >
            <Database size={14} /> State Inspector
          </button>
          <button
            onClick={() => setActiveTab('social')}
            className={`px-6 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'social' 
                ? 'border-emerald-500 text-emerald-400 bg-emerald-500/5' 
                : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
          >
            <Activity size={14} /> Social Metrics
          </button>
          <button
            onClick={() => setActiveTab('events')}
            className={`px-6 py-3 text-xs font-bold uppercase tracking-wider border-b-2 transition-colors flex items-center gap-2 ${
              activeTab === 'events' 
                ? 'border-amber-500 text-amber-400 bg-amber-500/5' 
                : 'border-transparent text-slate-500 hover:text-slate-300'
            }`}
          >
            <AlertCircle size={14} /> Event System
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-auto p-6 bg-slate-900">
          {activeTab === 'state' && (
            <div className="space-y-6">
              <div className="grid grid-cols-3 gap-4">
                <MetricCard label="Active Customers" value={laundromat.active_customers || 0} />
                <MetricCard label="Internal Reputation" value={laundromat.reputation.toFixed(2)} />
                <MetricCard label="Simulation Week" value={gameState.week} />
              </div>
              
              <div className="bg-slate-950 rounded-xl border border-slate-800 p-4">
                <h3 className="text-sm font-bold text-slate-400 mb-2 uppercase">Raw State Dump</h3>
                <pre className="text-xs text-green-400 overflow-x-auto whitespace-pre-wrap font-mono">
                  {JSON.stringify(laundromat, null, 2)}
                </pre>
              </div>
            </div>
          )}

          {activeTab === 'social' && (
            <div className="grid grid-cols-2 gap-6">
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-2">
                  <Activity size={16} className="text-emerald-500" />
                  Component Breakdown
                </h3>
                {socialComponents ? (
                  <div className="space-y-3">
                    {Object.entries(socialComponents).map(([key, value]) => (
                      <div key={key} className="bg-slate-950 p-3 rounded-lg border border-slate-800">
                        <div className="flex justify-between items-center mb-2">
                          <span className="text-slate-400 text-xs uppercase">{key.replace('_', ' ')}</span>
                          <span className="text-emerald-400 font-bold">{Number(value).toFixed(1)}</span>
                        </div>
                        <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-emerald-500 rounded-full" 
                            style={{ width: `${Number(value)}%` }}
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="p-4 bg-slate-800/50 rounded-lg text-slate-400 italic">
                    Social score is a simple number ({laundromat.social_score}), not an object.
                  </div>
                )}
              </div>
              
              <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
                <h3 className="text-sm font-bold text-slate-100 mb-4">Logic Explanation</h3>
                <div className="space-y-2 text-xs text-slate-400">
                  <p><strong className="text-slate-300">Customer Satisfaction (30%)</strong>: Driven by successful wash cycles, low wait times, and ticket resolution.</p>
                  <p><strong className="text-slate-300">Community Standing (25%)</strong>: Driven by competitive pricing and marketing campaigns.</p>
                  <p><strong className="text-slate-300">Ethical Conduct (20%)</strong>: Driven by fair wages (coming soon) and honest business practices.</p>
                  <p><strong className="text-slate-300">Environmental (10%)</strong>: Driven by energy efficient upgrades and eco-friendly supplies.</p>
                  <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/20 rounded-lg text-blue-300">
                    Why stuck? Check if negative events (broken machines, high prices) are counteracting your gains.
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'events' && (
            <div>
               <h3 className="text-sm font-bold text-slate-100 mb-4">Active Engine Events</h3>
               {laundromat.active_events && laundromat.active_events.length > 0 ? (
                 <div className="space-y-2">
                   {laundromat.active_events.map((e, i) => (
                     <div key={i} className="p-3 bg-amber-500/10 border border-amber-500/20 rounded-lg text-amber-200">
                       {e}
                     </div>
                   ))}
                 </div>
               ) : (
                 <div className="text-slate-500 italic">No active events affecting this laundromat.</div>
               )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const MetricCard = ({ label, value }: { label: string, value: string | number }) => (
  <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
    <div className="text-slate-500 text-xs uppercase font-bold mb-1">{label}</div>
    <div className="text-2xl font-mono text-slate-200">{value}</div>
  </div>
);

export default DebugPanel;
