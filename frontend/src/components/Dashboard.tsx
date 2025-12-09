import React from 'react';
import { Users, Droplets, Star, MessageCircle, Sparkles, Activity, Package, TrendingUp, AlertCircle } from 'lucide-react';
import type { Laundromat } from '../types';
import SocialScoreCard from './SocialScoreCard';
import ZoneCard from './ZoneCard';
import CalendarWidget from './CalendarWidget';

interface DashboardProps {
  laundromat: Laundromat;
  week: number;
  season: string;
  customerThoughts: string[];
}

const Dashboard: React.FC<DashboardProps> = ({ laundromat, week, season, customerThoughts }) => {
  // Calculate occupancy based on active customers (use real data or fallback)
  const activeCustomers = laundromat.active_customers !== undefined 
    ? laundromat.active_customers 
    : Math.floor(laundromat.reputation / 10); 
  const workingMachines = laundromat.machines - laundromat.broken_machines;
  const machinesInUse = Math.min(workingMachines, activeCustomers);
  const utilizationRate = workingMachines > 0 ? (machinesInUse / workingMachines) * 100 : 0;

  return (
    <div className="h-full flex flex-col gap-4 overflow-y-auto custom-scrollbar p-1">
      {/* Top Stats Row */}
      <div className="grid grid-cols-5 gap-4 flex-shrink-0">
        {/* Balance Card */}
        <div className="group relative overflow-hidden bg-gradient-to-br from-emerald-600 to-teal-700 p-4 rounded-xl shadow-lg hover:shadow-emerald-500/20 hover:scale-[1.02] transition-all border border-emerald-500/20">
          <div className="absolute -top-4 -right-4 w-16 h-16 bg-white/10 rounded-full blur-xl"></div>
          <div className="relative">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 bg-black/20 rounded-lg flex items-center justify-center backdrop-blur-sm">
                <TrendingUp className="text-emerald-100" size={16} />
              </div>
              <span className="text-emerald-100/80 text-xs font-bold uppercase tracking-wider">Balance</span>
            </div>
            <div className="text-2xl font-bold text-white font-mono tracking-tight">${laundromat.balance.toFixed(0)}</div>
          </div>
        </div>

        {/* Customers Card */}
        <div className="group bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700 hover:border-blue-500/50 transition-all hover:bg-slate-750">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-blue-500/20 rounded-lg flex items-center justify-center">
              <Users className="text-blue-400" size={16} />
            </div>
            <span className="text-slate-400 text-xs font-bold uppercase">Customers</span>
          </div>
          <div className="text-2xl font-bold text-white">{activeCustomers}</div>
          <div className="text-xs text-slate-500">active now</div>
        </div>

        {/* Machines Card */}
        <div className="group bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700 hover:border-indigo-500/50 transition-all hover:bg-slate-750">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-indigo-500/20 rounded-lg flex items-center justify-center">
              <Droplets className="text-indigo-400" size={16} />
            </div>
            <span className="text-slate-400 text-xs font-bold uppercase">Machines</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-white">{machinesInUse}</span>
            <span className="text-slate-500">/ {laundromat.machines}</span>
          </div>
          {laundromat.broken_machines > 0 && (
            <div className="text-xs text-rose-400 flex items-center gap-1 mt-1 font-medium">
              <AlertCircle size={10} />
              {laundromat.broken_machines} broken
            </div>
          )}
        </div>

        {/* Reputation Card */}
        <div className="group bg-slate-800 p-4 rounded-xl shadow-lg border border-slate-700 hover:border-amber-500/50 transition-all hover:bg-slate-750">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-amber-500/20 rounded-lg flex items-center justify-center">
              <Star className="text-amber-400" size={16} fill="currentColor" />
            </div>
            <span className="text-slate-400 text-xs font-bold uppercase">Reputation</span>
          </div>
          <div className="text-2xl font-bold text-white">{laundromat.reputation.toFixed(1)}</div>
          <div className="h-1.5 bg-slate-700 rounded-full mt-2 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-amber-400 to-orange-500 rounded-full transition-all duration-500 shadow-[0_0_10px_rgba(251,191,36,0.5)]"
              style={{ width: `${Math.min(laundromat.reputation, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Supply Status Card */}
        {laundromat.inventory_metrics && (
          <div className={`group bg-slate-800 p-4 rounded-xl shadow-lg border transition-all hover:bg-slate-750 ${
            laundromat.inventory_metrics.status === 'Good' ? 'border-slate-700 hover:border-emerald-500/50' : 
            laundromat.inventory_metrics.status === 'Low' ? 'border-orange-900/50 hover:border-orange-500/50' : 
            'border-rose-900/50 hover:border-rose-500/50'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center ${
                laundromat.inventory_metrics.status === 'Good' ? 'bg-emerald-500/20 text-emerald-400' : 
                laundromat.inventory_metrics.status === 'Low' ? 'bg-orange-500/20 text-orange-400' : 
                'bg-rose-500/20 text-rose-400'
              }`}>
                <Package size={16} />
              </div>
              <span className="text-slate-400 text-xs font-bold uppercase">Supply</span>
            </div>
            <div className="text-2xl font-bold text-white">{laundromat.inventory_metrics.days_of_supply.toFixed(0)}d</div>
            <div className="text-xs text-slate-500">{laundromat.inventory_metrics.burn_rate} loads/day</div>
          </div>
        )}
      </div>

      {/* Main Content Area - Split into Rows */}
      
      {/* Middle Row: Floor & Social/Chatter */}
      <div className="grid grid-cols-3 gap-4 min-h-[400px] flex-shrink-0">
        {/* Laundromat Floor - Takes 2 columns */}
        <div className="col-span-2 bg-slate-800 rounded-xl shadow-lg border border-slate-700 flex flex-col overflow-hidden relative">
           {/* Glass Header */}
          <div className="px-5 py-4 border-b border-slate-700/50 flex items-center justify-between flex-shrink-0 bg-slate-800/50 backdrop-blur-sm">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-indigo-500/20 text-indigo-400 rounded-xl flex items-center justify-center border border-indigo-500/20">
                <Sparkles size={20} />
              </div>
              <div>
                <h3 className="font-bold text-white text-lg">Laundromat Floor</h3>
                <p className="text-xs text-slate-400 font-mono">Week {week} • {season}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-indigo-900/30 border border-indigo-500/20 rounded-lg">
              <Activity className="text-indigo-400" size={14} />
              <span className="text-sm font-bold text-indigo-300">{utilizationRate.toFixed(0)}% utilization</span>
            </div>
          </div>
          
          <div className="flex-1 p-6 overflow-y-auto bg-slate-900/50">
            <div className="grid grid-cols-5 gap-4">
              {Array.from({ length: laundromat.machines }).map((_, i) => {
                const isBroken = i < laundromat.broken_machines;
                const isWorking = !isBroken;
                const isInUse = isWorking && i < (machinesInUse + laundromat.broken_machines);

                return (
                  <div 
                    key={i} 
                    className={`group aspect-square rounded-xl flex flex-col items-center justify-center border-2 transition-all duration-300 cursor-default relative overflow-hidden ${
                      isBroken 
                        ? 'bg-rose-900/10 border-rose-500/30 hover:border-rose-500/60' 
                        : isInUse
                          ? 'bg-indigo-900/20 border-indigo-500/40 shadow-[0_0_15px_rgba(99,102,241,0.15)] hover:border-indigo-400'
                          : 'bg-slate-800/50 border-slate-700 hover:border-slate-500'
                    }`}
                  >
                    {isInUse && <div className="absolute inset-0 bg-indigo-500/5 animate-pulse"></div>}
                    
                    <div className={`text-4xl mb-2 transition-transform duration-500 ${isInUse ? 'scale-110' : 'group-hover:scale-105'} filter`}>
                      {isBroken ? '🔧' : '🧺'}
                    </div>
                    <div className={`text-[10px] font-bold uppercase tracking-wider z-10 ${
                      isBroken ? 'text-rose-400' : isInUse ? 'text-indigo-300' : 'text-slate-500'
                    }`}>
                      {isBroken ? 'Broken' : isInUse ? 'Running' : 'Ready'}
                    </div>
                    {isInUse && (
                      <div className="w-10 h-1 bg-indigo-900/50 rounded-full mt-2 overflow-hidden">
                        <div className="h-full bg-indigo-500 rounded-full animate-[shimmer_2s_infinite]" style={{ width: '100%' }}></div>
                      </div>
                    )}
                  </div>
                );
              })}
              
               {/* Add New Machine Placeholder */}
               <div className="aspect-square rounded-xl flex flex-col items-center justify-center border-2 border-dashed border-slate-700 bg-slate-800/30 hover:bg-slate-800 hover:border-slate-600 transition-all cursor-pointer group">
                  <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center mb-2 group-hover:bg-indigo-600 transition-colors">
                    <span className="text-xl text-slate-400 group-hover:text-white">+</span>
                  </div>
                  <span className="text-xs text-slate-500 font-medium group-hover:text-slate-300">Expand</span>
               </div>
            </div>
          </div>
        </div>

        {/* Right Column: Social & Chatter */}
        <div className="col-span-1 flex flex-col gap-4">
          <div className="h-1/2 min-h-[220px]">
             <SocialScoreCard socialScore={laundromat.social_score} />
          </div>
          
          <div className="h-1/2 flex-1 bg-slate-800 rounded-xl shadow-lg border border-slate-700 flex flex-col min-h-0 overflow-hidden">
            <div className="px-4 py-3 border-b border-slate-700 flex items-center gap-2 flex-shrink-0 bg-slate-800">
              <div className="w-8 h-8 bg-rose-500/20 text-rose-400 rounded-lg flex items-center justify-center">
                <MessageCircle size={16} />
              </div>
              <h3 className="font-bold text-white">Customer Chatter</h3>
            </div>
            
            <div className="flex-1 overflow-y-auto p-3 space-y-2 bg-slate-900/30 custom-scrollbar">
              {customerThoughts.length === 0 ? (
                <div className="text-center py-8 text-slate-500">
                  <MessageCircle className="mx-auto mb-2 opacity-50" size={32} />
                  <p className="text-sm italic">It's quiet... for now.</p>
                </div>
              ) : (
                customerThoughts.slice(-8).reverse().map((thought, i) => (
                  <div 
                    key={i} 
                    className="group bg-slate-800 p-3 rounded-lg border border-slate-700 text-sm text-slate-300 hover:border-rose-500/30 hover:bg-slate-750 transition-all shadow-sm"
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-rose-400 flex-shrink-0 animate-pulse">💬</span>
                      <span className="line-clamp-2 leading-relaxed">"{thought}"</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom Row: Widgets (New Placement) */}
      <div className="grid grid-cols-2 gap-4 pb-4 flex-shrink-0">
          <div className="h-[280px]">
            <ZoneCard agentId={laundromat.id || 'p1'} />
          </div>
          <div className="h-[280px]">
            <CalendarWidget agentId={laundromat.id || 'p1'} currentWeek={week} />
          </div>
      </div>
    </div>
  );
};

export default Dashboard;
