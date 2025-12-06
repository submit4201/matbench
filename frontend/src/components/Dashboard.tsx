import React from 'react';
import { Users, Droplets, Star, MessageCircle, Sparkles, Activity, Package, Zap, TrendingUp, AlertCircle } from 'lucide-react';
import type { Laundromat } from '../types';
import SocialScoreCard from './SocialScoreCard';

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
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Top Stats Row */}
      <div className="grid grid-cols-5 gap-4 flex-shrink-0">
        {/* Balance Card */}
        <div className="group relative overflow-hidden bg-gradient-to-br from-emerald-500 to-teal-600 p-4 rounded-xl shadow-lg hover:shadow-xl hover:scale-[1.02] transition-all">
          <div className="absolute -top-4 -right-4 w-16 h-16 bg-white/10 rounded-full blur-xl"></div>
          <div className="relative">
            <div className="flex items-center gap-2 mb-2">
              <div className="w-8 h-8 bg-white/20 rounded-lg flex items-center justify-center">
                <TrendingUp className="text-white" size={16} />
              </div>
              <span className="text-white/80 text-xs font-bold uppercase">Balance</span>
            </div>
            <div className="text-2xl font-bold text-white font-mono">${laundromat.balance.toFixed(0)}</div>
          </div>
        </div>

        {/* Customers Card */}
        <div className="group bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-lg hover:border-blue-200 transition-all">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center shadow-md">
              <Users className="text-white" size={16} />
            </div>
            <span className="text-gray-500 text-xs font-bold uppercase">Customers</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{activeCustomers}</div>
          <div className="text-xs text-gray-400">active now</div>
        </div>

        {/* Machines Card */}
        <div className="group bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-lg hover:border-indigo-200 transition-all">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-lg flex items-center justify-center shadow-md">
              <Droplets className="text-white" size={16} />
            </div>
            <span className="text-gray-500 text-xs font-bold uppercase">Machines</span>
          </div>
          <div className="flex items-baseline gap-1">
            <span className="text-2xl font-bold text-gray-900">{machinesInUse}</span>
            <span className="text-gray-400">/ {laundromat.machines}</span>
          </div>
          {laundromat.broken_machines > 0 && (
            <div className="text-xs text-red-500 flex items-center gap-1 mt-1">
              <AlertCircle size={10} />
              {laundromat.broken_machines} broken
            </div>
          )}
        </div>

        {/* Reputation Card */}
        <div className="group bg-white p-4 rounded-xl shadow-sm border border-gray-100 hover:shadow-lg hover:border-yellow-200 transition-all">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center shadow-md">
              <Star className="text-white" size={16} fill="white" />
            </div>
            <span className="text-gray-500 text-xs font-bold uppercase">Reputation</span>
          </div>
          <div className="text-2xl font-bold text-gray-900">{laundromat.reputation.toFixed(1)}</div>
          <div className="h-1.5 bg-gray-100 rounded-full mt-2 overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-yellow-400 to-orange-500 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(laundromat.reputation, 100)}%` }}
            ></div>
          </div>
        </div>

        {/* Supply Status Card */}
        {laundromat.inventory_metrics && (
          <div className={`group bg-white p-4 rounded-xl shadow-sm border transition-all hover:shadow-lg ${
            laundromat.inventory_metrics.status === 'Good' ? 'border-gray-100 hover:border-green-200' : 
            laundromat.inventory_metrics.status === 'Low' ? 'border-orange-200 hover:border-orange-300' : 
            'border-red-200 hover:border-red-300'
          }`}>
            <div className="flex items-center gap-2 mb-2">
              <div className={`w-8 h-8 rounded-lg flex items-center justify-center shadow-md ${
                laundromat.inventory_metrics.status === 'Good' ? 'bg-gradient-to-br from-green-500 to-emerald-500' : 
                laundromat.inventory_metrics.status === 'Low' ? 'bg-gradient-to-br from-orange-400 to-amber-500' : 
                'bg-gradient-to-br from-red-500 to-rose-500'
              }`}>
                <Package className="text-white" size={16} />
              </div>
              <span className="text-gray-500 text-xs font-bold uppercase">Supply</span>
            </div>
            <div className="text-2xl font-bold text-gray-900">{laundromat.inventory_metrics.days_of_supply.toFixed(0)}d</div>
            <div className="text-xs text-gray-400">{laundromat.inventory_metrics.burn_rate} loads/day</div>
          </div>
        )}
      </div>

      {/* Main Content Area */}
      <div className="flex-1 grid grid-cols-3 gap-4 min-h-0">
        
        {/* Laundromat Floor - Takes 2 columns */}
        <div className="col-span-2 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col overflow-hidden">
          <div className="px-5 py-4 border-b border-gray-100 flex items-center justify-between flex-shrink-0 bg-gradient-to-r from-gray-50 to-white">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-blue-200">
                <Sparkles className="text-white" size={20} />
              </div>
              <div>
                <h3 className="font-bold text-gray-800">Laundromat Floor</h3>
                <p className="text-xs text-gray-400">Week {week} • {season}</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-3 py-1.5 bg-blue-50 rounded-lg">
              <Activity className="text-blue-600" size={14} />
              <span className="text-sm font-bold text-blue-700">{utilizationRate.toFixed(0)}% utilization</span>
            </div>
          </div>
          
          <div className="flex-1 p-4 overflow-y-auto">
            <div className="grid grid-cols-5 gap-3">
              {Array.from({ length: laundromat.machines }).map((_, i) => {
                const isBroken = i < laundromat.broken_machines;
                const isWorking = !isBroken;
                const isInUse = isWorking && i < (machinesInUse + laundromat.broken_machines);

                return (
                  <div 
                    key={i} 
                    className={`group aspect-square rounded-xl flex flex-col items-center justify-center border-2 transition-all duration-300 cursor-default ${
                      isBroken 
                        ? 'bg-gradient-to-br from-red-50 to-rose-50 border-red-200 hover:border-red-300' 
                        : isInUse
                          ? 'bg-gradient-to-br from-blue-50 to-indigo-50 border-blue-300 shadow-md shadow-blue-100 hover:shadow-lg'
                          : 'bg-gradient-to-br from-gray-50 to-white border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className={`text-3xl mb-1 transition-transform ${isInUse ? 'animate-pulse' : ''}`}>
                      {isBroken ? '🔧' : '🧺'}
                    </div>
                    <div className={`text-[10px] font-bold uppercase tracking-wider ${
                      isBroken ? 'text-red-500' : isInUse ? 'text-blue-600' : 'text-gray-400'
                    }`}>
                      {isBroken ? 'Broken' : isInUse ? 'Running' : 'Ready'}
                    </div>
                    {isInUse && (
                      <div className="w-8 h-1 bg-blue-200 rounded-full mt-1.5 overflow-hidden">
                        <div className="h-full bg-blue-500 rounded-full animate-pulse" style={{ width: '70%' }}></div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="col-span-1 flex flex-col gap-4 min-h-0">
          {/* Social Score Card */}
          <SocialScoreCard socialScore={laundromat.social_score} />
          
          {/* Customer Chatter */}
          <div className="flex-1 bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col min-h-0 overflow-hidden">
            <div className="px-4 py-3 border-b border-gray-100 flex items-center gap-2 flex-shrink-0 bg-gradient-to-r from-pink-50 to-rose-50">
              <div className="w-8 h-8 bg-gradient-to-br from-pink-500 to-rose-500 rounded-lg flex items-center justify-center shadow-md">
                <MessageCircle className="text-white" size={16} />
              </div>
              <h3 className="font-bold text-gray-800">Customer Chatter</h3>
            </div>
            
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
              {customerThoughts.length === 0 ? (
                <div className="text-center py-8 text-gray-400">
                  <MessageCircle className="mx-auto mb-2 text-gray-200" size={32} />
                  <p className="text-sm italic">It's quiet... for now.</p>
                </div>
              ) : (
                customerThoughts.slice(-8).reverse().map((thought, i) => (
                  <div 
                    key={i} 
                    className="group bg-gradient-to-r from-gray-50 to-white p-3 rounded-lg border border-gray-100 text-sm text-gray-700 hover:border-pink-200 hover:shadow-sm transition-all"
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-pink-400 flex-shrink-0">💬</span>
                      <span className="line-clamp-2">"{thought}"</span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
