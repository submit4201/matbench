import React, { useState } from 'react';
import { DollarSign, Sparkles, Rocket } from 'lucide-react';
import type { Laundromat, GameState } from '../types';
import PricingWidget from './widgets/PricingWidget';
import MachineWidget from './widgets/MachineWidget';

interface ControlPanelProps {
  laundromat: Laundromat;
  market: GameState['market'];
  onSetPrice: (price: number) => void;
  onUpgrade: (type: string) => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({ laundromat, market, onSetPrice, onUpgrade }) => {
  const [activeSection, setActiveSection] = useState<'pricing' | 'upgrade'>('pricing');

  const sections = [
    { id: 'pricing', label: 'Pricing', icon: DollarSign, color: 'emerald' },
    { id: 'upgrade', label: 'Upgrade', icon: Rocket, color: 'purple' }
  ];

  return (
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-5 shadow-xl flex-shrink-0">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-0 left-1/4 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-0 right-1/4 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/5 via-transparent to-transparent"></div>
        </div>
        
        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 ring-2 ring-white/20">
              <Sparkles className="text-white" size={28} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Operations</h2>
              <p className="text-slate-400 text-sm">Manage core business logic</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="px-4 py-2 bg-white/10 backdrop-blur-sm rounded-xl border border-white/10">
              <div className="text-[10px] text-emerald-400 uppercase font-bold">Balance</div>
              <div className="text-xl font-bold text-white font-mono">${laundromat.balance.toFixed(0)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Section Tabs */}
      <div className="flex gap-2 flex-shrink-0 bg-slate-900/50 p-1.5 rounded-xl overflow-x-auto border border-slate-700/50">
        {sections.map(s => (
          <button 
            key={s.id}
            onClick={() => setActiveSection(s.id as typeof activeSection)}
            className={`flex-1 flex items-center justify-center gap-2 py-2.5 px-3 rounded-lg font-bold text-sm transition-all min-w-[100px] ${
              activeSection === s.id
                ? `bg-gradient-to-r from-${s.color}-500 to-${s.color}-600 text-white shadow-md transform scale-[1.02]`
                : 'text-slate-400 hover:bg-slate-700 hover:text-white'
            }`}
          >
            <s.icon size={16} />
            {s.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto min-h-0 bg-slate-800 rounded-2xl shadow-lg border border-slate-700 p-4">
        
        {/* Pricing Section */}
        {activeSection === 'pricing' && (
          <PricingWidget laundromat={laundromat} onSetPrice={onSetPrice} />
        )}

        {/* Upgrade Section */}
        {activeSection === 'upgrade' && (
          <MachineWidget laundromat={laundromat} onUpgrade={onUpgrade} />
        )}
      </div>
    </div>
  );
};

export default ControlPanel;
