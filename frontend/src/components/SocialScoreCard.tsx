import React from 'react';
import { Shield, Users, Heart, Leaf } from 'lucide-react';
import type { SocialScore } from '../types';

interface SocialScoreCardProps {
  socialScore: SocialScore | number;
}

const SocialScoreCard: React.FC<SocialScoreCardProps> = ({ socialScore }) => {
  if (typeof socialScore === 'number') {
    return (
      <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100">
        <div className="text-sm text-gray-500 font-medium">Social Score</div>
        <div className="text-2xl font-bold text-gray-900">{socialScore.toFixed(1)}</div>
      </div>
    );
  }

  const { total_score, components, tier_info } = socialScore;

  return (
    <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 h-full">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-bold text-gray-800">Social Standing</h3>
          <div className="text-sm text-gray-500">{tier_info.tier_name}</div>
        </div>
        <div className="text-3xl">{tier_info.badge}</div>
      </div>

      <div className="flex items-end gap-2 mb-6">
        <div className="text-4xl font-bold text-blue-600">{total_score.toFixed(1)}</div>
        <div className="text-gray-400 mb-1">/ 100</div>
      </div>

      <div className="space-y-3">
        <ScoreRow icon={<Users size={16} />} label="Customer Satisfaction" value={components.customer_satisfaction} color="blue" />
        <ScoreRow icon={<Heart size={16} />} label="Community Standing" value={components.community_standing} color="pink" />
        <ScoreRow icon={<Shield size={16} />} label="Ethical Conduct" value={components.ethical_conduct} color="purple" />
        <ScoreRow icon={<Users size={16} />} label="Employee Relations" value={components.employee_relations} color="orange" />
        <ScoreRow icon={<Leaf size={16} />} label="Environmental" value={components.environmental_responsibility} color="green" />
      </div>
      
      {tier_info.benefits && tier_info.benefits.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="text-xs font-bold text-green-600 uppercase mb-2">Active Benefits</div>
            <ul className="text-xs text-gray-600 space-y-1">
                {tier_info.benefits.map((b, i) => <li key={i}>• {b}</li>)}
            </ul>
        </div>
      )}
       {tier_info.penalties && tier_info.penalties.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-100">
            <div className="text-xs font-bold text-red-600 uppercase mb-2">Active Penalties</div>
            <ul className="text-xs text-gray-600 space-y-1">
                {tier_info.penalties.map((b, i) => <li key={i}>• {b}</li>)}
            </ul>
        </div>
      )}
    </div>
  );
};

const ScoreRow = ({ icon, label, value, color }: any) => (
  <div className="flex items-center justify-between">
    <div className="flex items-center gap-2 text-gray-600 text-sm">
      <span className={`text-${color}-500`}>{icon}</span>
      {label}
    </div>
    <div className="flex items-center gap-2">
      <div className="w-24 h-2 bg-gray-100 rounded-full overflow-hidden">
        <div 
          className={`h-full bg-${color}-500 rounded-full`} 
          style={{ width: `${value}%` }}
        />
      </div>
      <span className="text-xs font-bold text-gray-700 w-8 text-right">{value.toFixed(0)}</span>
    </div>
  </div>
);

export default SocialScoreCard;
