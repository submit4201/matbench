import React from 'react';
import { Shield, Users, Heart, Leaf } from 'lucide-react';
import type { SocialScore } from '../types';

interface SocialScoreCardProps {
  socialScore: SocialScore | number;
}

const SocialScoreCard: React.FC<SocialScoreCardProps> = ({ socialScore }) => {
  if (typeof socialScore === 'number') {
    return (
      <div className="bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700">
        <div className="text-sm text-slate-400 font-medium">Social Score</div>
        <div className="text-2xl font-bold text-white">{socialScore.toFixed(1)}</div>
      </div>
    );
  }

  const { total_score, components, tier_info } = socialScore;

  return (
    <div className="bg-slate-800 p-6 rounded-xl shadow-lg border border-slate-700 h-full flex flex-col">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold text-white">Social Standing</h3>
          <div className="text-sm text-slate-400">{tier_info.tier_name}</div>
        </div>
        <div className="text-3xl filter drop-shadow-lg">{tier_info.badge}</div>
      </div>

      <div className="flex items-end gap-2 mb-6">
        <div className="text-4xl font-bold text-blue-400">{total_score.toFixed(1)}</div>
        <div className="text-slate-500 mb-1">/ 100</div>
      </div>

      <div className="space-y-4 flex-1">
        <ScoreRow icon={<Users size={16} />} label="Customer Satisfaction" value={components.customer_satisfaction} color="blue" />
        <ScoreRow icon={<Heart size={16} />} label="Community Standing" value={components.community_standing} color="pink" />
        <ScoreRow icon={<Shield size={16} />} label="Ethical Conduct" value={components.ethical_conduct} color="purple" />
        <ScoreRow icon={<Users size={16} />} label="Employee Relations" value={components.employee_relations} color="orange" />
        <ScoreRow icon={<Leaf size={16} />} label="Environmental" value={components.environmental_responsibility} color="emerald" />
      </div>
      
      {tier_info.benefits && tier_info.benefits.length > 0 && (
        <div className="mt-6 pt-4 border-t border-slate-700/50">
            <div className="text-xs font-bold text-emerald-400 uppercase mb-2 tracking-wider">Active Benefits</div>
            <ul className="text-xs text-slate-400 space-y-1.5">
                {tier_info.benefits.map((b, i) => <li key={i} className="flex items-start gap-1.5"><span className="text-emerald-500 mt-0.5">✓</span>{b}</li>)}
            </ul>
        </div>
      )}
       {tier_info.penalties && tier_info.penalties.length > 0 && (
        <div className="mt-4 pt-4 border-t border-slate-700/50">
            <div className="text-xs font-bold text-rose-400 uppercase mb-2 tracking-wider">Active Penalties</div>
            <ul className="text-xs text-slate-400 space-y-1.5">
                {tier_info.penalties.map((b, i) => <li key={i} className="flex items-start gap-1.5"><span className="text-rose-500 mt-0.5">⚠</span>{b}</li>)}
            </ul>
        </div>
      )}
    </div>
  );
};

const ScoreRow = ({ icon, label, value, color }: any) => (
  <div className="flex items-center justify-between group">
    <div className="flex items-center gap-2 text-slate-400 text-sm group-hover:text-slate-200 transition-colors">
      <span className={`text-${color}-400`}>{icon}</span>
      {label}
    </div>
    <div className="flex items-center gap-3">
      <div className="w-24 h-2 bg-slate-700/50 rounded-full overflow-hidden">
        <div 
          className={`h-full bg-${color}-500 rounded-full shadow-[0_0_10px_rgba(var(--${color}-rgb),0.3)] transition-all duration-500`} 
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs font-bold text-slate-300 w-8 text-right">{value.toFixed(0)}</span>
    </div>
  </div>
);

export default SocialScoreCard;
