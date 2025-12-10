import React from 'react';
import { Megaphone, ArrowUpRight, Zap } from 'lucide-react';
import type { Laundromat } from '../../types';

interface MarketingWidgetProps {
  laundromat: Laundromat;
  onMarketingCampaign: (cost: number) => void;
}

const MarketingWidget: React.FC<MarketingWidgetProps> = ({ laundromat, onMarketingCampaign }) => {
  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
      <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-pink-900 via-rose-900 to-red-900 p-5 border-b border-white/10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center border border-white/10">
              <Megaphone className="text-white" size={20} />
            </div>
            <div>
              <h3 className="font-bold text-white text-lg">Marketing Campaigns</h3>
              <p className="text-pink-200 text-xs">Boost your visibility & reputation</p>
            </div>
          </div>
        </div>

        <div className="p-5 space-y-4">
          {/* Social Media Campaign */}
          <div className="group p-5 bg-gradient-to-br from-pink-900/10 to-rose-900/10 rounded-xl border border-pink-500/30 hover:border-pink-500/50 hover:shadow-lg transition-all hover:bg-slate-750">
            <div className="flex items-start gap-4">
              <div className="w-14 h-14 bg-gradient-to-br from-pink-600 to-rose-700 rounded-2xl flex items-center justify-center shadow-lg shadow-pink-900/20 border border-white/10">
                <span className="text-2xl filter drop-shadow">📱</span>
              </div>
              <div className="flex-1">
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <h4 className="font-bold text-white text-lg">Social Media Blast</h4>
                    <p className="text-sm text-slate-400">Viral marketing to attract customers</p>
                  </div>
                  <div className="text-right">
                    <div className="font-mono font-bold text-2xl text-pink-400">$100</div>
                    <div className="text-xs text-slate-500">one-time</div>
                  </div>
                </div>
                <div className="flex items-center gap-4 mb-4">
                  <span className="px-2 py-1 bg-pink-500/20 text-pink-300 rounded text-xs font-bold flex items-center gap-1 border border-pink-500/20">
                    <ArrowUpRight size={12} /> +5 Social Score
                  </span>
                  <span className="px-2 py-1 bg-blue-500/20 text-blue-300 rounded text-xs font-bold border border-blue-500/20">
                    🎯 Instant Impact
                  </span>
                </div>
                <button 
                  onClick={() => onMarketingCampaign(100)}
                  disabled={laundromat.balance < 100}
                  className="w-full py-3 bg-gradient-to-r from-pink-600 to-rose-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-pink-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-98 border border-pink-400/20"
                >
                  <Zap size={18} fill="currentColor" />
                  Launch Campaign
                </button>
              </div>
            </div>
          </div>

          {/* Coming Soon */}
          <div className="p-5 bg-slate-900/30 rounded-xl border-2 border-dashed border-slate-700 relative overflow-hidden group">
            <div className="absolute top-2 right-2 px-2 py-0.5 bg-slate-700 text-slate-400 rounded text-xs font-bold border border-slate-600">COMING SOON</div>
            <div className="flex items-center gap-4 opacity-50 group-hover:opacity-75 transition-opacity">
              <div className="w-14 h-14 bg-slate-700 rounded-2xl flex items-center justify-center">
                <span className="text-2xl filter grayscale opacity-70">📺</span>
              </div>
              <div>
                <h4 className="font-bold text-slate-400 text-lg">Local TV Spot</h4>
                <p className="text-sm text-slate-600">Premium brand awareness</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MarketingWidget;
