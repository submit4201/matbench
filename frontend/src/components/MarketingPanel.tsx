import React from 'react';
import type { Laundromat } from '../types';
import MarketingWidget from './widgets/MarketingWidget';
import { Megaphone, HeartHandshake, Mic2 } from 'lucide-react';

interface MarketingPanelProps {
  laundromat: Laundromat;
  onMarketingCampaign: (cost: number) => void;
}

const MarketingPanel: React.FC<MarketingPanelProps> = ({ laundromat, onMarketingCampaign }) => {
  return (
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-5 shadow-xl flex-shrink-0">
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute bottom-0 left-0 w-64 h-64 bg-pink-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/5 via-transparent to-transparent"></div>
        </div>
        
        <div className="relative flex items-center gap-4">
          <div className="w-14 h-14 bg-gradient-to-br from-pink-600 to-rose-600 rounded-2xl flex items-center justify-center shadow-lg shadow-pink-500/30 ring-2 ring-white/20">
            <Megaphone className="text-white" size={28} />
          </div>
          <div>
            <h2 className="text-2xl font-bold text-white">Marketing & PR</h2>
            <p className="text-slate-400 text-sm">Campaigns and public relations</p>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto min-h-0 bg-slate-800 rounded-2xl shadow-lg border border-slate-700 p-4 space-y-6">
        
        {/* Core Marketing Widget */}
        <section>
            <h3 className="text-white font-bold mb-3 flex items-center gap-2">
                <Megaphone size={16} className="text-pink-400" />
                Active Campaigns
            </h3>
            <MarketingWidget laundromat={laundromat} onMarketingCampaign={onMarketingCampaign} />
        </section>

        {/* PR & Apologies Section (Placeholder) */}
        <section className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700 hover:border-slate-500 transition-colors cursor-not-allowed opacity-75">
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-orange-500/20 flex items-center justify-center">
                        <Mic2 size={20} className="text-orange-400" />
                    </div>
                    <div>
                        <h4 className="text-white font-bold">Public Apology</h4>
                        <p className="text-xs text-slate-400">Recover reputation</p>
                    </div>
                </div>
                <button disabled className="w-full py-2 mt-2 bg-slate-800 rounded-lg text-xs font-bold text-slate-500 border border-slate-700">Coming Soon</button>
            </div>

            <div className="p-4 bg-slate-900/50 rounded-xl border border-slate-700 hover:border-slate-500 transition-colors cursor-not-allowed opacity-75">
                <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                        <HeartHandshake size={20} className="text-emerald-400" />
                    </div>
                    <div>
                        <h4 className="text-white font-bold">Charity Event</h4>
                        <p className="text-xs text-slate-400">Boost local image</p>
                    </div>
                </div>
                <button disabled className="w-full py-2 mt-2 bg-slate-800 rounded-lg text-xs font-bold text-slate-500 border border-slate-700">Coming Soon</button>
            </div>
        </section>

      </div>
    </div>
  );
};

export default MarketingPanel;
