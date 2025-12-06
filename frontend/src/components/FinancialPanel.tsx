import React from 'react';
import { DollarSign, TrendingUp, TrendingDown, ShoppingCart, Package, Sparkles, ArrowUpRight, ArrowDownRight, Wallet, PiggyBank } from 'lucide-react';
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
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-violet-600 via-purple-600 to-indigo-700 p-6 shadow-xl">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full blur-2xl animate-pulse"></div>
          <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-white/10 rounded-full blur-xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
        </div>
        
        <div className="relative flex items-center gap-4">
          <div className="w-16 h-16 bg-white/20 backdrop-blur-sm rounded-2xl flex items-center justify-center shadow-lg border border-white/30">
            <Wallet className="text-white" size={32} />
          </div>
          <div>
            <h2 className="text-3xl font-bold text-white tracking-tight">Financial Overview</h2>
            <p className="text-white/80 font-medium mt-1">Track revenue, expenses, and profitability</p>
          </div>
        </div>
      </div>

      {/* Summary Cards - Hero Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 flex-shrink-0">
        {/* Total Revenue Card */}
        <div className="group relative overflow-hidden bg-gradient-to-br from-emerald-500 to-teal-600 p-6 rounded-2xl shadow-xl hover:shadow-2xl hover:shadow-emerald-200 transition-all duration-300 hover:scale-[1.02]">
          <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="absolute -top-6 -right-6 w-24 h-24 bg-white/10 rounded-full blur-xl"></div>
          
          <div className="relative">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <TrendingUp className="text-white" size={24} />
              </div>
              <span className="text-sm font-bold text-white/80 uppercase tracking-wider">Total Revenue</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white font-mono">${totalRevenue.toFixed(2)}</span>
            </div>
            <div className="mt-3 flex items-center gap-2 text-emerald-100">
              <ArrowUpRight size={16} />
              <span className="text-sm font-medium">Weekly earnings</span>
            </div>
          </div>
        </div>

        {/* Total Expenses Card */}
        <div className="group relative overflow-hidden bg-gradient-to-br from-rose-500 to-red-600 p-6 rounded-2xl shadow-xl hover:shadow-2xl hover:shadow-rose-200 transition-all duration-300 hover:scale-[1.02]">
          <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="absolute -top-6 -right-6 w-24 h-24 bg-white/10 rounded-full blur-xl"></div>
          
          <div className="relative">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <TrendingDown className="text-white" size={24} />
              </div>
              <span className="text-sm font-bold text-white/80 uppercase tracking-wider">Total Expenses</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white font-mono">${totalExpenses.toFixed(2)}</span>
            </div>
            <div className="mt-3 flex items-center gap-2 text-rose-100">
              <ArrowDownRight size={16} />
              <span className="text-sm font-medium">Inventory + Operating</span>
            </div>
          </div>
        </div>

        {/* Net Income Card */}
        <div className={`group relative overflow-hidden p-6 rounded-2xl shadow-xl hover:shadow-2xl transition-all duration-300 hover:scale-[1.02] ${
          netIncome >= 0 
            ? 'bg-gradient-to-br from-blue-500 to-indigo-600 hover:shadow-blue-200' 
            : 'bg-gradient-to-br from-amber-500 to-orange-600 hover:shadow-amber-200'
        }`}>
          <div className="absolute inset-0 bg-gradient-to-br from-white/0 to-white/10 opacity-0 group-hover:opacity-100 transition-opacity"></div>
          <div className="absolute -top-6 -right-6 w-24 h-24 bg-white/10 rounded-full blur-xl"></div>
          
          <div className="relative">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                <PiggyBank className="text-white" size={24} />
              </div>
              <span className="text-sm font-bold text-white/80 uppercase tracking-wider">Net Income</span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className="text-4xl font-bold text-white font-mono">
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
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-3 p-5 border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-teal-50">
            <div className="w-10 h-10 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-xl flex items-center justify-center shadow-lg shadow-emerald-200">
              <TrendingUp className="text-white" size={20} />
            </div>
            <h3 className="text-lg font-bold text-gray-800">Revenue Streams</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-3">
            {laundromat.revenue_streams && Object.values(laundromat.revenue_streams).length > 0 ? (
              Object.values(laundromat.revenue_streams).map((stream: any) => (
                <div 
                  key={stream.name} 
                  className="group flex justify-between items-center p-4 bg-gradient-to-r from-emerald-50 via-white to-teal-50 rounded-xl border-2 border-emerald-100 hover:border-emerald-300 hover:shadow-lg hover:shadow-emerald-50 transition-all duration-300"
                >
                  <div className="flex-1">
                    <span className="font-bold text-gray-800">{stream.name}</span>
                    <div className="flex items-center gap-2 mt-1">
                      {stream.active ? (
                        <span className="inline-flex items-center gap-1 px-2 py-0.5 bg-emerald-500 text-white text-xs rounded-full font-bold">
                          <span className="w-1.5 h-1.5 bg-white rounded-full animate-pulse"></span>
                          ACTIVE
                        </span>
                      ) : (
                        <span className="px-2 py-0.5 bg-gray-200 text-gray-500 text-xs rounded-full font-bold">INACTIVE</span>
                      )}
                      <span className="text-xs text-gray-400">{stream.category}</span>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="font-mono font-bold text-emerald-600 text-xl">${(stream.weekly_revenue || 0).toFixed(2)}</div>
                    <div className="text-xs text-gray-400">/week</div>
                  </div>
                </div>
              ))
            ) : (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-gray-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <TrendingUp className="text-gray-300" size={32} />
                </div>
                <p className="text-gray-400 font-medium">No revenue streams yet</p>
                <p className="text-gray-300 text-sm mt-1">Add services to start earning</p>
              </div>
            )}
          </div>
        </div>

        {/* Expenses & Inventory */}
        <div className="bg-white rounded-2xl shadow-lg border border-gray-100 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-3 p-5 border-b border-gray-100 bg-gradient-to-r from-rose-50 to-red-50">
            <div className="w-10 h-10 bg-gradient-to-br from-rose-500 to-red-500 rounded-xl flex items-center justify-center shadow-lg shadow-rose-200">
              <ShoppingCart className="text-white" size={20} />
            </div>
            <h3 className="text-lg font-bold text-gray-800">Expenses & Inventory</h3>
          </div>
          
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {/* Expense Summary */}
            <div className="space-y-2">
              <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Operating Costs</div>
              
              <div className="flex justify-between items-center p-4 bg-gradient-to-r from-rose-50 to-red-50 rounded-xl border-2 border-rose-200 hover:border-rose-300 transition-colors">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-rose-100 rounded-lg flex items-center justify-center">
                    <Package className="text-rose-600" size={16} />
                  </div>
                  <span className="font-medium text-gray-700">Supply Inventory Value</span>
                </div>
                <span className="font-mono font-bold text-rose-600 text-lg">${supplyExpenses.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl border-2 border-gray-200 hover:border-gray-300 transition-colors">
                <span className="font-medium text-gray-700">Marketing Campaigns</span>
                <span className="font-mono font-bold text-gray-500">${marketingExpenses.toFixed(2)}</span>
              </div>
              
              <div className="flex justify-between items-center p-4 bg-gray-50 rounded-xl border-2 border-gray-200 hover:border-gray-300 transition-colors">
                <span className="font-medium text-gray-700">Maintenance & Repairs</span>
                <span className="font-mono font-bold text-gray-500">${maintenanceExpenses.toFixed(2)}</span>
              </div>
            </div>

            {/* Inventory Breakdown */}
            <div className="space-y-3 pt-4 border-t border-gray-200">
              <div className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Current Inventory</div>
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
                    detergent: 'from-blue-500 to-cyan-500 shadow-blue-200',
                    softener: 'from-pink-500 to-rose-500 shadow-pink-200',
                    parts: 'from-amber-500 to-orange-500 shadow-amber-200',
                    cleaning_supplies: 'from-violet-500 to-purple-500 shadow-violet-200'
                  };
                  
                  return (
                    <div key={item} className="group p-4 bg-gradient-to-br from-gray-50 to-white rounded-xl border-2 border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all duration-300">
                      <div className="flex items-center gap-2 mb-2">
                        <div className={`w-8 h-8 bg-gradient-to-br ${colors[item] || 'from-gray-400 to-gray-500'} rounded-lg flex items-center justify-center shadow-lg`}>
                          <Package className="text-white" size={14} />
                        </div>
                        <div className="text-xs font-bold text-gray-600 uppercase tracking-wider">{displayName}</div>
                      </div>
                      <div className="text-2xl font-bold text-gray-900">{qty}</div>
                      <div className="text-xs text-gray-400 font-medium">≈ ${value.toFixed(2)}</div>
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
