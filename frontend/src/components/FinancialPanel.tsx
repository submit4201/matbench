import React from 'react';
import { TrendingUp, TrendingDown, ShoppingCart, Package, Sparkles, ArrowUpRight, ArrowDownRight, Wallet, PiggyBank } from 'lucide-react';
import type { Laundromat } from '../types';

interface FinancialPanelProps {
  laundromat: Laundromat;
}

const FinancialPanel: React.FC<FinancialPanelProps> = ({ laundromat }) => {
  // Calculate expenses
  const supplyExpenses = Object.entries(laundromat.inventory).reduce((total, [item, qty]) => {
    const priceMap: Record<string, number> = {
      detergent: 1.60,
      softener: 1.60,
      parts: 15.5,
      cleaning_supplies: 1.60
    };
    return total + (qty * (priceMap[item] || 0));
  }, 0);

  const marketingExpenses = 0;
  const maintenanceExpenses = 0;
  const totalExpenses = supplyExpenses + marketingExpenses + maintenanceExpenses;

  // Calculate total revenue from streams
  const totalRevenue = laundromat.revenue_streams 
    ? Object.values(laundromat.revenue_streams).reduce((sum: number, stream: any) => 
        sum + (stream.weekly_revenue || 0), 0)
    : 0;

  const netIncome = totalRevenue - totalExpenses;
  const profitMargin = totalRevenue > 0 ? (netIncome / totalRevenue) * 100 : 0;

  return (
    <div className="h-full flex flex-col gap-6 overflow-hidden">
      
      {/* Premium Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-900 via-purple-900 to-indigo-900 p-6 shadow-xl border border-violet-500/20">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/5 rounded-full blur-2xl animate-pulse"></div>
          <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-white/5 rounded-full blur-xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative flex items-center gap-4">
          <div className="w-16 h-16 bg-white/10 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg border border-white/20">
            <Wallet className="text-white" size={32} />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight">Financial Overview</h2>
            <p className="text-slate-300 font-medium mt-1">Track revenue, expenses, and profitability</p>
          </div>
        </div>
      </div>

      {/* Summary Cards - Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 flex-shrink-0">
        {/* Total Revenue Card */}
        <div className="group relative overflow-hidden bg-gradient-to-br from-emerald-900 to-teal-900 p-6 rounded-2xl shadow-lg border border-emerald-500/30 hover:border-emerald-500/50 transition-all duration-300 hover:scale-[1.02]">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-500/5 to-teal-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="absolute -top-6 -right-6 w-24 h-24 bg-emerald-500/10 rounded-full blur-xl"></div>
          
          <div className="relative">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-emerald-500/20 rounded-xl flex items-center justify-center">
                <TrendingUp className="text-emerald-400" size={24} />
              </div>
              <span className="text-sm font-bold text-emerald-100/80 uppercase tracking-wider">Total Revenue</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white font-mono tracking-tight">${totalRevenue.toFixed(2)}</span>
            </div>
            <div className="mt-3 flex items-center gap-2 text-emerald-300">
              <ArrowUpRight size={16} />
              <span className="text-sm font-medium">Weekly earnings</span>
            </div>
          </div>
        </div>

        {/* Total Expenses Card */}
        <div className="group relative overflow-hidden bg-gradient-to-br from-rose-900 to-red-950 p-6 rounded-2xl shadow-lg border border-rose-500/30 hover:border-rose-500/50 transition-all duration-300 hover:scale-[1.02]">
          <div className="absolute inset-0 bg-gradient-to-br from-rose-500/5 to-red-500/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="absolute -top-6 -right-6 w-24 h-24 bg-rose-500/10 rounded-full blur-xl"></div>
          
          <div className="relative">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-rose-500/20 rounded-xl flex items-center justify-center">
                <TrendingDown className="text-rose-400" size={24} />
              </div>
              <span className="text-sm font-bold text-rose-100/80 uppercase tracking-wider">Total Expenses</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white font-mono tracking-tight">${totalExpenses.toFixed(2)}</span>
            </div>
            <div className="mt-3 flex items-center gap-2 text-rose-300">
              <ArrowDownRight size={16} />
              <span className="text-sm font-medium">Inventory + Operating</span>
            </div>
          </div>
        </div>

        {/* Net Income Card */}
        <div className={`group relative overflow-hidden p-6 rounded-2xl shadow-lg border transition-all duration-300 hover:scale-[1.02] ${
          netIncome >= 0 
            ? 'bg-gradient-to-br from-blue-900 to-indigo-900 border-blue-500/30 hover:border-blue-500/50' 
            : 'bg-gradient-to-br from-amber-900 to-orange-950 border-amber-500/30 hover:border-amber-500/50'
        }`}>
          <div className="absolute inset-0 bg-white/5 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="absolute -top-6 -right-6 w-24 h-24 bg-white/5 rounded-full blur-xl"></div>
          
          <div className="relative">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-white/10 rounded-xl flex items-center justify-center">
                <PiggyBank className="text-white" size={24} />
              </div>
              <span className="text-sm font-bold text-white/80 uppercase tracking-wider">Net Income</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white font-mono tracking-tight">
                {netIncome >= 0 ? '+' : ''}${netIncome.toFixed(2)}
              </span>
            </div>
            <div className="mt-3 flex items-center gap-2 text-white/80">
              <Sparkles size={16} />
              <span className="text-sm font-medium">
                {netIncome >= 0 ? `${profitMargin.toFixed(0)}% margin` : 'Operating at loss'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Main Grid - 2 columns */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 flex-1 min-h-0">
        
        {/* Revenue Breakdown */}
        <div className="bg-slate-800 rounded-2xl shadow-lg border border-slate-700 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-3 p-5 border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-500/20">
              <TrendingUp className="text-white" size={20} />
            </div>
            <h3 className="text-lg font-bold text-white">Revenue Streams</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3 custom-scrollbar">
            {laundromat.revenue_streams && Object.values(laundromat.revenue_streams).length > 0 ? (
              Object.values(laundromat.revenue_streams).map((stream: any) => (
                <div 
                  key={stream.name} 
                  className="group flex justify-between items-center p-4 bg-slate-700/30 rounded-xl border border-slate-600/50 hover:bg-slate-700/50 hover:border-emerald-500/30 transition-all duration-300"
                >
                  <div className="flex-1">
                    <span className="font-bold text-white">{stream.name}</span>
                    <div className="flex items-center gap-2 mt-1">
                      {stream.active ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] rounded-full font-bold border border-emerald-500/20">
                          <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse"></span>
                          ACTIVE
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 bg-slate-600/50 text-slate-400 text-[10px] rounded-full font-bold">INACTIVE</span>
                      )}
                      <span className="text-xs text-slate-400">{stream.category}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono font-bold text-emerald-400 text-xl">${(stream.weekly_revenue || 0).toFixed(2)}</div>
                    <div className="text-xs text-slate-500">/week</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-slate-700/50 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="text-slate-500" size={32} />
                </div>
                <p className="text-slate-400 font-medium">No revenue streams yet</p>
                <p className="text-slate-500 text-sm mt-1">Add services to start earning</p>
              </div>
            )}
          </div>
        </div>

        {/* Expenses & Inventory */}
        <div className="bg-slate-800 rounded-2xl shadow-lg border border-slate-700 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-3 p-5 border-b border-slate-700 bg-slate-800/50 backdrop-blur-sm">
            <div className="w-10 h-10 bg-gradient-to-br from-rose-500 to-red-600 rounded-xl flex items-center justify-center shadow-lg shadow-rose-500/20">
              <ShoppingCart className="text-white" size={20} />
            </div>
            <h3 className="text-lg font-bold text-white">Expenses & Inventory</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
            {/* Expense Summary */}
            <div className="space-y-2">
              <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Operating Costs</div>
              
              <div className="flex justify-between items-center p-4 bg-rose-900/10 rounded-xl border border-rose-500/20 hover:bg-rose-900/20 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-rose-500/20 rounded-lg flex items-center justify-center">
                    <Package className="text-rose-400" size={16} />
                  </div>
                  <span className="font-medium text-slate-200">Supply Inventory Value</span>
                </div>
                <span className="font-mono font-bold text-rose-400 text-lg">${supplyExpenses.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between items-center p-4 bg-slate-700/30 rounded-xl border border-slate-600/50 hover:bg-slate-700/50 transition-colors">
                <span className="font-medium text-slate-300">Marketing Campaigns</span>
                <span className="font-mono font-bold text-slate-400">${marketingExpenses.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between items-center p-4 bg-slate-700/30 rounded-xl border border-slate-600/50 hover:bg-slate-700/50 transition-colors">
                <span className="font-medium text-slate-300">Maintenance & Repairs</span>
                <span className="font-mono font-bold text-slate-400">${maintenanceExpenses.toFixed(2)}</span>
              </div>
            </div>

            {/* Inventory Breakdown */}
            <div className="space-y-3 pt-4 border-t border-slate-700/50">
              <div className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">Current Inventory</div>
              <div className="grid grid-cols-2 gap-3">
                {Object.entries(laundromat.inventory).map(([item, qty]) => {
                  const priceMap: Record<string, number> = {
                    detergent: 1.60,
                    softener: 1.60,
                    parts: 15.5,
                    cleaning_supplies: 1.60
                  };
                  const value = qty * (priceMap[item] || 0);
                  const displayName = item === 'detergent' ? 'Detergent' : 
                                     item === 'cleaning_supplies' ? 'Cleaning Supplies' :
                                     item.charAt(0).toUpperCase() + item.slice(1);
                  
                  // Dynamic color based on item
                  const colors: Record<string, string> = {
                    detergent: 'from-blue-500 to-cyan-500 shadow-blue-500/20',
                    softener: 'from-pink-500 to-rose-500 shadow-pink-500/20',
                    parts: 'from-amber-500 to-orange-500 shadow-amber-500/20',
                    cleaning_supplies: 'from-violet-500 to-purple-500 shadow-violet-500/20'
                  };
                  
                  return (
                    <div key={item} className="group p-4 bg-slate-700/30 rounded-xl border border-slate-600/50 hover:border-blue-500/30 hover:bg-slate-700/50 transition-all duration-300">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-8 h-8 bg-gradient-to-br ${colors[item] || 'from-slate-400 to-slate-500'} rounded-lg flex items-center justify-center shadow-lg`}>
                          <Package className="text-white" size={14} />
                        </div>
                        <div className="text-xs font-bold text-slate-400 uppercase tracking-wider">{displayName}</div>
                      </div>
                      <div className="text-2xl font-bold text-white">{qty}</div>
                      <div className="text-xs text-slate-500 font-medium">≈ ${value.toFixed(2)}</div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

    </div>
  );
};

export default FinancialPanel;
