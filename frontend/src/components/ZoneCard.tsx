/**
 * ZoneCard.tsx - Neighborhood Zone Display
 * 
 * A visually striking zone info card featuring:
 * - Dynamic gradient based on zone tier
 * - Animated traffic indicator
 * - Competition meter
 * - Demographic badges
 */

import { useState, useEffect } from 'react';
import type { ZoneInfo } from '../types';
import { Trophy, Gem, Building, Home, Construction } from 'lucide-react';

// Zone tier styling
const ZONE_STYLES: Record<string, { gradient: string; icon: any; badge: string }> = {
  premium: { 
    gradient: 'from-amber-500 via-yellow-400 to-orange-500', 
    icon: Trophy, 
    badge: 'Premium District' 
  },
  upscale: { 
    gradient: 'from-purple-500 via-violet-400 to-indigo-500', 
    icon: Gem, 
    badge: 'Upscale Area' 
  },
  midrange: { 
    gradient: 'from-blue-500 via-cyan-400 to-teal-500', 
    icon: Building, 
    badge: 'Mid-Range Zone' 
  },
  affordable: { 
    gradient: 'from-emerald-500 via-green-400 to-lime-500', 
    icon: Home, 
    badge: 'Affordable District' 
  },
  budget: { 
    gradient: 'from-slate-500 via-gray-400 to-zinc-500', 
    icon: Construction, 
    badge: 'Budget Zone' 
  },
};

interface ZoneCardProps {
  agentId?: string;
}

export function ZoneCard({ agentId = 'p1' }: ZoneCardProps) {
  const [zone, setZone] = useState<ZoneInfo | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchZoneInfo();
  }, [agentId]);

  const fetchZoneInfo = async () => {
    try {
      const res = await fetch(`http://localhost:8000/zone/${agentId}`);
      const data = await res.json();
      setZone(data.zone);
    } catch (err) {
      console.error('Failed to fetch zone info:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-5 animate-pulse h-48" />
    );
  }

  if (!zone) {
    return (
      <div className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl p-5 text-center text-gray-400">
        No zone data
      </div>
    );
  }

  // Determine zone tier from demographic or use default
  const tierKey = zone.demographic?.toLowerCase().includes('affluent') ? 'upscale' 
    : zone.demographic?.toLowerCase().includes('student') ? 'budget'
    : zone.demographic?.toLowerCase().includes('professional') ? 'midrange'
    : 'midrange';
  
  const style = ZONE_STYLES[tierKey] || ZONE_STYLES.midrange;
  const trafficPercent = Math.min(100, (zone.base_foot_traffic / 150) * 100);
  const competitionPercent = Math.min(100, zone.competition_level * 20);

  return (
    <div className="relative bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl overflow-hidden group hover:shadow-xl transition-all duration-300">
      {/* Gradient Top Border */}
      <div className={`h-1.5 bg-gradient-to-r ${style.gradient}`} />
      
      {/* Floating Icon */}
      <div className={`absolute -top-4 right-4 w-16 h-16 rounded-2xl bg-gradient-to-br ${style.gradient} flex items-center justify-center shadow-lg transform group-hover:scale-110 transition-transform duration-300`}>
        <style.icon className="text-white w-8 h-8 animate-float" />
      </div>

      <div className="p-5 space-y-4">
        {/* Zone Header */}
        <div className="pr-16">
          <h3 className="text-lg font-bold text-white">{zone.zone_name || `Zone ${zone.zone_id}`}</h3>
          <div className={`inline-block px-3 py-1 mt-2 rounded-full text-xs font-medium bg-gradient-to-r ${style.gradient} text-white shadow-sm`}>
            {style.badge}
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-2 gap-3 pt-2">
          {/* Foot Traffic */}
          <div className="bg-slate-700/30 rounded-xl p-3 backdrop-blur">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">👥</span>
              <span className="text-xs text-gray-400">Foot Traffic</span>
            </div>
            <div className="relative h-2 bg-slate-600/50 rounded-full overflow-hidden">
              <div 
                className="absolute left-0 top-0 h-full bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full transition-all duration-700"
                style={{ width: `${trafficPercent}%` }}
              />
            </div>
            <div className="text-right mt-1">
              <span className="text-sm font-bold text-cyan-400">{zone.base_foot_traffic}</span>
              <span className="text-xs text-gray-400">/day</span>
            </div>
          </div>

          {/* Competition */}
          <div className="bg-slate-700/30 rounded-xl p-3 backdrop-blur">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">⚔️</span>
              <span className="text-xs text-gray-400">Competition</span>
            </div>
            <div className="relative h-2 bg-slate-600/50 rounded-full overflow-hidden">
              <div 
                className={`absolute left-0 top-0 h-full rounded-full transition-all duration-700 ${
                  competitionPercent > 60 ? 'bg-gradient-to-r from-red-400 to-rose-500' :
                  competitionPercent > 30 ? 'bg-gradient-to-r from-yellow-400 to-orange-500' :
                  'bg-gradient-to-r from-green-400 to-emerald-500'
                }`}
                style={{ width: `${competitionPercent}%` }}
              />
            </div>
            <div className="text-right mt-1">
              <span className={`text-sm font-bold ${
                competitionPercent > 60 ? 'text-red-400' :
                competitionPercent > 30 ? 'text-yellow-400' : 'text-green-400'
              }`}>
                {competitionPercent > 60 ? 'High' : competitionPercent > 30 ? 'Medium' : 'Low'}
              </span>
            </div>
          </div>
        </div>

        {/* Rent & Demographics */}
        <div className="flex items-center justify-between pt-2 border-t border-slate-700/50">
          <div className="flex items-center gap-2">
            <span className="text-lg">🏠</span>
            <div>
              <div className="text-xs text-gray-400">Weekly Rent</div>
              <div className="text-lg font-bold text-emerald-400">${zone.rent_cost}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-xs text-gray-400">Demographics</div>
            <div className="text-sm font-medium text-white">{zone.demographic || 'Mixed'}</div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ZoneCard;
