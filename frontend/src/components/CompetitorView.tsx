import React, { useState } from 'react';
import { Users, TrendingUp, Star, DollarSign, Eye, Target, Zap, Trophy, Shield } from 'lucide-react';
import type { Laundromat } from '../types';

interface CompetitorViewProps {
  competitors: Laundromat[];
}

const CompetitorView: React.FC<CompetitorViewProps> = ({ competitors }) => {
  const [selectedId, setSelectedId] = useState<string>(competitors[0]?.id || '');

  if (competitors.length === 0) return (
    <div className="h-full flex items-center justify-center text-gray-400">
      <div className="text-center">
        <Users className="mx-auto mb-3 text-gray-300" size={48} />
        <p className="font-bold">No competitors found</p>
      </div>
    </div>
  );

  const selectedComp = competitors.find(c => c.id === selectedId) || competitors[0];

  const getSocialScoreValue = (score: number | { total_score: number }): number => {
    if (typeof score === 'number') return score;
    return score.total_score;
  };

  const socialScore = getSocialScoreValue(selectedComp.social_score);
  
  // Determine threat level
  const threatLevel = socialScore > 70 ? 'High' : socialScore > 40 ? 'Medium' : 'Low';
  const threatColor = threatLevel === 'High' ? 'text-red-600 bg-red-50 border-red-200' : 
                      threatLevel === 'Medium' ? 'text-amber-600 bg-amber-50 border-amber-200' : 
                      'text-green-600 bg-green-50 border-green-200';

  return (
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Header */}
      <div className="flex items-center gap-3 flex-shrink-0">
        <div className="w-12 h-12 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-purple-200">
          <Eye className="text-white" size={24} />
        </div>
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Market Intelligence</h2>
          <p className="text-sm text-gray-500">Monitor your competition</p>
        </div>
      </div>

      {/* Competitor Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-1 flex-shrink-0">
        {competitors.map((comp, i) => {
          const compScore = getSocialScoreValue(comp.social_score);
          const isSelected = selectedComp.id === comp.id;
          
          return (
            <button
              key={comp.id}
              onClick={() => setSelectedId(comp.id)}
              className={`group flex items-center gap-3 px-4 py-3 rounded-xl font-bold transition-all flex-shrink-0 ${
                isSelected
                  ? 'bg-gradient-to-r from-purple-500 to-indigo-600 text-white shadow-lg shadow-purple-200'
                  : 'bg-white border border-gray-200 text-gray-700 hover:border-purple-300 hover:shadow-md'
              }`}
            >
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center font-mono text-lg ${
                isSelected ? 'bg-white/20' : 'bg-purple-100 text-purple-600'
              }`}>
                #{i + 1}
              </div>
              <div className="text-left">
                <div className="font-bold">{comp.name}</div>
                <div className={`text-xs ${isSelected ? 'text-white/70' : 'text-gray-400'}`}>
                  Score: {compScore.toFixed(0)}
                </div>
              </div>
            </button>
          );
        })}
      </div>

      {/* Main Content */}
      <div className="flex-1 grid grid-cols-3 gap-4 min-h-0">
        
        {/* Left Column - Key Metrics */}
        <div className="col-span-2 flex flex-col gap-4">
          {/* Metric Cards */}
          <div className="grid grid-cols-3 gap-4">
            <div className="group bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-lg hover:border-green-200 transition-all">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-green-500 to-emerald-500 rounded-lg flex items-center justify-center shadow-md">
                  <DollarSign className="text-white" size={20} />
                </div>
                <span className="text-gray-500 font-bold text-sm">Pricing</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 font-mono">${selectedComp.price.toFixed(2)}</div>
              <div className="h-2 bg-gray-100 rounded-full mt-3 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-emerald-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (selectedComp.price / 10) * 100)}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-400 mt-1">per wash cycle</div>
            </div>
            
            <div className="group bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-lg hover:border-yellow-200 transition-all">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center shadow-md">
                  <Star className="text-white" size={20} fill="white" />
                </div>
                <span className="text-gray-500 font-bold text-sm">Reputation</span>
              </div>
              <div className="text-3xl font-bold text-gray-900">{socialScore.toFixed(1)}</div>
              <div className="h-2 bg-gray-100 rounded-full mt-3 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full transition-all duration-500"
                  style={{ width: `${socialScore}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-400 mt-1">customer satisfaction</div>
            </div>
            
            <div className="group bg-white p-5 rounded-xl border border-gray-100 shadow-sm hover:shadow-lg hover:border-blue-200 transition-all">
              <div className="flex items-center gap-2 mb-3">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center shadow-md">
                  <TrendingUp className="text-white" size={20} />
                </div>
                <span className="text-gray-500 font-bold text-sm">Capital</span>
              </div>
              <div className="text-3xl font-bold text-gray-900 font-mono">${selectedComp.balance.toFixed(0)}</div>
              <div className="h-2 bg-gray-100 rounded-full mt-3 overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500"
                  style={{ width: `${Math.min(100, (selectedComp.balance / 10000) * 100)}%` }}
                ></div>
              </div>
              <div className="text-xs text-gray-400 mt-1">estimated balance</div>
            </div>
          </div>

          {/* Intel Report */}
          <div className="flex-1 bg-white rounded-xl border border-gray-100 shadow-sm p-5 flex flex-col">
            <div className="flex items-center gap-2 mb-4">
              <Target className="text-purple-600" size={20} />
              <h4 className="font-bold text-gray-800">Strategic Intel</h4>
            </div>
            
            <div className="flex-1 space-y-3">
              <div className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-lg border border-gray-200">
                <div className="text-xs text-gray-500 uppercase font-bold mb-1">Operations</div>
                <p className="text-gray-700">
                  <strong>{selectedComp.name}</strong> operates with <span className="font-bold text-purple-600">{selectedComp.machines} machines</span>.
                  {selectedComp.broken_machines > 0 && (
                    <span className="text-red-500"> ({selectedComp.broken_machines} currently broken)</span>
                  )}
                </p>
              </div>
              
              <div className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-lg border border-gray-200">
                <div className="text-xs text-gray-500 uppercase font-bold mb-1">Pricing Strategy</div>
                <p className="text-gray-700">
                  {selectedComp.price < 3 
                    ? "Aggressive low-price strategy to capture market share. May be operating at thin margins." 
                    : selectedComp.price < 5 
                    ? "Competitive mid-range pricing balancing volume and profit." 
                    : "Premium positioning with higher margins. Relies on service quality to justify price."}
                </p>
              </div>
              
              <div className="p-4 bg-gradient-to-r from-gray-50 to-white rounded-lg border border-gray-200">
                <div className="text-xs text-gray-500 uppercase font-bold mb-1">Market Position</div>
                <p className="text-gray-700">
                  {socialScore > 70 
                    ? "Strong market presence with loyal customer base. A formidable competitor." 
                    : socialScore > 40 
                    ? "Average standing. Opportunity to differentiate could shift customers." 
                    : "Struggling with customer satisfaction. Vulnerable to market capture."}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column - Threat Assessment */}
        <div className="flex flex-col gap-4">
          {/* Threat Level */}
          <div className={`p-5 rounded-xl border-2 ${threatColor}`}>
            <div className="flex items-center gap-2 mb-3">
              <Shield size={20} />
              <span className="font-bold text-sm uppercase">Threat Level</span>
            </div>
            <div className="text-3xl font-bold">{threatLevel}</div>
            <p className="text-sm mt-2 opacity-80">
              {threatLevel === 'High' && "Major competitor. Monitor closely."}
              {threatLevel === 'Medium' && "Moderate threat. Keep an eye on them."}
              {threatLevel === 'Low' && "Limited competitive pressure."}
            </p>
          </div>
          
          {/* Comparison */}
          <div className="flex-1 bg-white rounded-xl border border-gray-100 shadow-sm p-5">
            <div className="flex items-center gap-2 mb-4">
              <Trophy className="text-amber-500" size={20} />
              <h4 className="font-bold text-gray-800">Head-to-Head</h4>
            </div>
            
            <div className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Price Competition</span>
                  <span className="font-bold">{selectedComp.price < 4 ? 'They Win' : 'You Win'}</span>
                </div>
                <div className="flex gap-1 h-2">
                  <div className="flex-1 bg-blue-500 rounded-l"></div>
                  <div className={`flex-1 ${selectedComp.price < 4 ? 'bg-purple-500' : 'bg-gray-200'} rounded-r`}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Reputation</span>
                  <span className="font-bold">{socialScore > 60 ? 'They Lead' : 'You Lead'}</span>
                </div>
                <div className="flex gap-1 h-2">
                  <div className={`flex-1 ${socialScore > 60 ? 'bg-gray-200' : 'bg-blue-500'} rounded-l`}></div>
                  <div className={`flex-1 ${socialScore > 60 ? 'bg-purple-500' : 'bg-gray-200'} rounded-r`}></div>
                </div>
              </div>
              
              <div>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500">Capacity</span>
                  <span className="font-bold">{selectedComp.machines} machines</span>
                </div>
                <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-purple-500 rounded-full"
                    style={{ width: `${(selectedComp.machines / 20) * 100}%` }}
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompetitorView;
