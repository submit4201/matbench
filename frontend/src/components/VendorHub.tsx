import React, { useState } from 'react';
import { ShoppingCart, MessageCircle, Truck, Star, AlertTriangle, Rocket, ArrowUpRight, ChevronRight, Package, Wrench } from 'lucide-react';
import type { Vendor, Laundromat } from '../types';

interface VendorHubProps {
  vendors: Vendor[];
  laundromat: Laundromat;
  supplyChainEvents: any[];
  onBuy: (item: string, qty: number, vendorId: string) => void;
  onNegotiate: (vendorId: string, item: string) => void;
  onUpgrade: (type: string) => void;
}

const VendorHub: React.FC<VendorHubProps> = ({ vendors, laundromat, supplyChainEvents, onBuy, onNegotiate, onUpgrade }) => {
  const [activeTab, setActiveTab] = useState<'supplies' | 'equipment'>('supplies');

  return (
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-900 via-indigo-800 to-slate-900 px-6 py-4 shadow-lg flex-shrink-0">
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-6 -right-6 w-24 h-24 bg-blue-500/10 rounded-full blur-xl animate-pulse"></div>
          </div>
          <div className="relative flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20">
                <Truck className="text-white" size={24} />
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Vendor Hub</h2>
                <p className="text-indigo-200/70 text-sm">Supply Chain & Equipment</p>
              </div>
            </div>
            
            {/* Tabs */}
            <div className="flex bg-slate-800/50 p-1 rounded-lg border border-white/10">
               <button
                 onClick={() => setActiveTab('supplies')}
                 className={`px-4 py-1.5 rounded-md text-sm font-bold flex items-center gap-2 transition-all ${
                   activeTab === 'supplies' ? 'bg-indigo-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                 }`}
               >
                 <Package size={14} /> Supplies
               </button>
               <button
                 onClick={() => setActiveTab('equipment')}
                  className={`px-4 py-1.5 rounded-md text-sm font-bold flex items-center gap-2 transition-all ${
                   activeTab === 'equipment' ? 'bg-purple-600 text-white shadow-md' : 'text-slate-400 hover:text-white'
                 }`}
               >
                 <Wrench size={14} /> Equipment
               </button>
            </div>
          </div>
        </div>

      {/* Content */}
      <div className="flex-1 overflow-y-auto bg-slate-900/50 rounded-2xl border border-slate-700/50 p-6 custom-scrollbar">
        
        {activeTab === 'supplies' && (
          <div className="space-y-6">
            {/* Supply Chain Alerts */}
            {supplyChainEvents && supplyChainEvents.length > 0 && (
              <div className="mb-8">
                <h3 className="text-sm font-bold text-slate-500 uppercase tracking-wider mb-3">Supply Chain Alerts</h3>
                <div className="grid gap-3">
                  {supplyChainEvents.map((event, idx) => (
                    <div key={idx} className={`p-4 rounded-xl border-l-4 flex items-start gap-3 ${
                      event.severity === 'critical' ? 'bg-red-900/20 border-red-500 text-red-200' : 'bg-orange-900/20 border-orange-500 text-orange-200'
                    }`}>
                      <AlertTriangle size={20} className="shrink-0 mt-0.5" />
                      <div>
                        <span className="font-bold block text-sm">{event.vendor_id ? `Alert: ${event.vendor_id}` : 'General Alert'}</span>
                        <p className="text-sm opacity-80">{event.description}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Vendors Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {vendors.map(vendor => (
                <div key={vendor.id} className="bg-slate-800 rounded-xl border border-slate-700 shadow-sm hover:border-indigo-500/50 hover:shadow-lg transition-all overflow-hidden group">
                  {/* Vendor Header */}
                  <div className="p-5 border-b border-slate-700 bg-gradient-to-r from-slate-800 to-slate-800 group-hover:from-slate-800 group-hover:to-indigo-900/20 transition-colors">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h3 className="text-lg font-bold text-white group-hover:text-indigo-300 transition-colors">{vendor.name}</h3>
                        <div className="flex items-center gap-2 text-xs text-slate-400 mt-1">
                          <span className={`px-2 py-0.5 rounded-full font-medium ${
                            vendor.tier === 'Premium' ? 'bg-purple-500/20 text-purple-300 border border-purple-500/20' :
                            vendor.tier === 'Standard' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/20' :
                            'bg-slate-700 text-slate-400 border border-slate-600'
                          }`}>
                            {vendor.tier} Tier
                          </span>
                          <span>•</span>
                          <span>{vendor.delivery_days} Day Delivery</span>
                        </div>
                      </div>
                      <div className="flex flex-col items-end">
                        <div className="flex items-center gap-1 text-amber-400 font-bold">
                          <Star size={14} fill="currentColor" />
                          <span>{(vendor.reliability * 100).toFixed(0)}%</span>
                        </div>
                        <span className="text-[10px] text-slate-500 uppercase tracking-wide">Reliability</span>
                      </div>
                    </div>
                    <p className="text-sm text-slate-500 italic">"{vendor.slogan}"</p>
                  </div>

                  {/* Special Offer */}
                  {vendor.special_offer && (
                    <div className="px-5 py-3 bg-emerald-900/20 border-y border-emerald-500/20 flex items-center gap-3">
                      <div className="w-8 h-8 rounded-full bg-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0">
                        <Star size={16} />
                      </div>
                      <div>
                        <div className="text-xs font-bold text-emerald-400 uppercase tracking-wide">Special Offer</div>
                        <div className="text-sm text-emerald-200 font-medium">{vendor.special_offer.description}</div>
                      </div>
                    </div>
                  )}

                  {/* Products Table */}
                  <div className="p-2">
                    <table className="w-full text-sm">
                      <thead className="text-xs text-slate-500 uppercase bg-slate-900/30">
                        <tr>
                          <th className="px-3 py-2 text-left font-medium">Item</th>
                          <th className="px-3 py-2 text-right font-medium">Price</th>
                          <th className="px-3 py-2 text-right font-medium">Actions</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-700/50">
                        {Object.entries(vendor.prices).map(([item, price]) => (
                          <tr key={item} className="group/row hover:bg-slate-700/30 transition-colors">
                            <td className="px-3 py-3 font-medium text-slate-300 capitalize">
                              {item === 'soap' ? 'Detergent' : item.replace('_', ' ')}
                            </td>
                            <td className="px-3 py-3 text-right text-white font-mono">${price.toFixed(2)}</td>
                            <td className="px-3 py-3 text-right">
                              <div className="flex justify-end gap-2 opacity-0 group-hover/row:opacity-100 transition-opacity">
                                <button 
                                  onClick={() => onNegotiate(vendor.id, item)}
                                  className="p-1.5 text-orange-400 hover:bg-orange-500/20 rounded-lg transition-colors"
                                  title="Negotiate Price"
                                >
                                  <MessageCircle size={16} />
                                </button>
                                <button 
                                  onClick={() => onBuy(item, 100, vendor.id)}
                                  className="flex items-center gap-1 px-2 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-500 transition-colors shadow-sm shadow-blue-500/20"
                                  title="Buy 100 Units"
                                >
                                  <ShoppingCart size={14} />
                                  <span className="text-xs font-bold">Buy</span>
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'equipment' && (
           <div className="space-y-6">
              {/* Equipment Header */}
              <div className="bg-gradient-to-r from-purple-900/50 via-violet-900/50 to-indigo-900/50 p-6 rounded-2xl border border-white/10 flex items-center gap-4">
                  <div className="w-12 h-12 bg-purple-500/20 rounded-xl flex items-center justify-center border border-purple-500/30">
                    <Rocket className="text-purple-300" size={24} />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">Business Expansion</h3>
                    <p className="text-purple-200 text-sm">Invest in growth & capacity upgrades</p>
                  </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Machine Upgrade Card */}
                <div className="group p-6 bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-slate-700 hover:border-purple-500/50 hover:shadow-xl hover:shadow-purple-900/20 transition-all">
                  <div className="flex items-start gap-4">
                    <div className="w-16 h-16 bg-gradient-to-br from-purple-600 to-violet-700 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-900/20 border border-white/10 shrink-0">
                      <span className="text-3xl filter drop-shadow">🧺</span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-bold text-white text-lg truncate">New Washing Machine</h4>
                          <p className="text-sm text-slate-400 line-clamp-1">Increase capacity & throughput</p>
                        </div>
                         <div className="text-right shrink-0 ml-2">
                           <div className="font-mono font-bold text-2xl text-purple-400">$500</div>
                           <div className="text-xs text-slate-500">investment</div>
                         </div>
                      </div>
                      
                      <div className="flex flex-wrap gap-2 mb-4">
                         <span className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-md text-xs font-bold flex items-center gap-1 border border-purple-500/20">
                            <ArrowUpRight size={12} /> +1 Machine
                         </span>
                         <span className="px-2 py-1 bg-emerald-500/20 text-emerald-300 rounded-md text-xs font-bold border border-emerald-500/20">
                            💰 +$50-100/wk
                         </span>
                      </div>

                      <div className="flex items-center gap-2 mb-4 text-sm text-slate-400 bg-slate-900/50 p-2 rounded-lg border border-slate-700/50">
                        <span>Current Fleet:</span>
                        <span className="font-bold text-purple-400">{laundromat.machines} machines</span>
                      </div>
                      
                      <button 
                        onClick={() => onUpgrade('machine')}
                        disabled={laundromat.balance < 500}
                        className="w-full py-3 bg-gradient-to-r from-purple-600 to-violet-600 text-white rounded-xl font-bold hover:shadow-lg hover:shadow-purple-900/20 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-98 border border-purple-400/20"
                      >
                        <ChevronRight size={18} />
                        Purchase Upgrade
                      </button>
                    </div>
                  </div>
                </div>

                {/* Coming Soon - Store Renovation */}
                <div className="p-6 bg-slate-900/30 rounded-2xl border-2 border-dashed border-slate-700/50 relative overflow-hidden group hover:border-slate-600 transition-colors">
                  <div className="absolute top-3 right-3 px-2 py-0.5 bg-slate-800 text-slate-500 rounded text-[10px] font-bold border border-slate-700 uppercase tracking-wide">Dev Roadmap</div>
                  <div className="flex items-center gap-4 opacity-40 group-hover:opacity-60 transition-opacity h-full">
                    <div className="w-16 h-16 bg-slate-800 rounded-2xl flex items-center justify-center">
                      <span className="text-3xl filter grayscale">🏪</span>
                    </div>
                    <div>
                      <h4 className="font-bold text-slate-300 text-lg">Store Renovation</h4>
                      <p className="text-sm text-slate-500">Premium customer experience upgrades</p>
                    </div>
                  </div>
                </div>
              </div>
           </div>
        )}
      </div>
    </div>
  );
};

export default VendorHub;
