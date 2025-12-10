import React, { useState } from 'react';
import { DollarSign, Zap } from 'lucide-react';
import type { Laundromat } from '../../types';

interface PricingWidgetProps {
  laundromat: Laundromat;
  onSetPrice: (price: number) => void;
}

const PricingWidget: React.FC<PricingWidgetProps> = ({ laundromat, onSetPrice }) => {
  const [priceInput, setPriceInput] = useState(laundromat.price.toString());

  const handlePriceSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSetPrice(parseFloat(priceInput));
  };

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
      {/* Main Price Card */}
      <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-emerald-900 to-teal-900 p-5 border-b border-white/10">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center border border-white/10">
              <DollarSign className="text-emerald-400" size={20} />
            </div>
            <div>
              <h3 className="font-bold text-white text-lg">Wash Price</h3>
              <p className="text-emerald-200 text-xs">Set competitive pricing</p>
            </div>
          </div>
          
          <form onSubmit={handlePriceSubmit} className="flex gap-3">
            <div className="flex-1 relative">
              <span className="absolute left-4 top-1/2 -translate-y-1/2 text-emerald-500 font-bold text-lg">$</span>
              <input 
                type="number" 
                step="0.1" 
                value={priceInput} 
                onChange={(e) => setPriceInput(e.target.value)}
                className="w-full pl-10 pr-4 py-4 bg-slate-900/50 backdrop-blur rounded-xl font-mono text-2xl font-bold text-white focus:ring-2 focus:ring-emerald-500/50 outline-none shadow-inner border border-slate-700 transition-all placeholder-slate-600"
              />
            </div>
            <button type="submit" className="px-8 bg-emerald-600 text-white rounded-xl font-bold hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-900/20 flex items-center gap-2 hover:scale-105 active:scale-95 border border-emerald-500/20">
              <Zap size={18} fill="currentColor" />
              Update
            </button>
          </form>
        </div>
        
        {/* Price Tips */}
        <div className="p-5 grid grid-cols-3 gap-4">
          <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700 text-center group hover:bg-blue-900/20 hover:border-blue-500/30 transition-all cursor-default">
            <div className="text-2xl mb-1">🏷️</div>
            <div className="text-xs font-bold text-slate-500 uppercase">Budget</div>
            <div className="font-mono font-bold text-slate-300">$2.00-3.00</div>
          </div>
          <div className="p-4 bg-emerald-900/20 rounded-xl border border-emerald-500/30 text-center relative overflow-hidden">
            <div className="absolute inset-0 bg-emerald-500/5 animate-pulse"></div>
            <div className="relative">
              <div className="text-2xl mb-1">⭐</div>
              <div className="text-xs font-bold text-emerald-400 uppercase">Optimal</div>
              <div className="font-mono font-bold text-emerald-300">$3.00-5.00</div>
            </div>
          </div>
          <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700 text-center group hover:bg-purple-900/20 hover:border-purple-500/30 transition-all cursor-default">
            <div className="text-2xl mb-1">👑</div>
            <div className="text-xs font-bold text-slate-500 uppercase">Premium</div>
            <div className="font-mono font-bold text-slate-300">$5.00-8.00</div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PricingWidget;
