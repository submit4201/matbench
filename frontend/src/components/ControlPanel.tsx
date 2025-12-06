import React, { useState, useEffect } from 'react';
import { ShoppingCart, DollarSign, Megaphone, MessageSquare, Truck, Star, Sparkles, Zap, ArrowUpRight, ChevronRight, ShoppingBag, Rocket, Crown, Gift, Percent, Edit3, Check } from 'lucide-react';
import type { Laundromat, GameState } from '../types';

interface ControlPanelProps {
  laundromat: Laundromat;
  market: GameState['market'];
  onSetPrice: (price: number) => void;
  onBuySupplies: (item: string, quantity: number, vendor_id?: string) => void;
  onUpgrade: (type: string) => void;
  onMarketingCampaign: (cost: number) => void;
}

const ControlPanel: React.FC<ControlPanelProps> = ({ laundromat, market, onSetPrice, onBuySupplies, onUpgrade, onMarketingCampaign }) => {
  const [buyQuantity, setBuyQuantity] = useState(10);
  const [selectedVendorId, setSelectedVendorId] = useState<string>('bulkwash');
  const [negotiatingItem, setNegotiatingItem] = useState<string | null>(null);
  const [negotiationResult, setNegotiationResult] = useState<{item: string, price: number, message: string} | null>(null);
  const [priceInput, setPriceInput] = useState(laundromat.price.toString());
  const [activeSection, setActiveSection] = useState<'pricing' | 'supply' | 'marketing' | 'upgrade'>('pricing');
  
  // Vending prices state
  const [detergentPrice, setDetergentPrice] = useState('1.50');
  const [softenerPrice, setSoftenerPrice] = useState('1.25');
  const [editingVending, setEditingVending] = useState<'detergent' | 'softener' | null>(null);
  const [pricesLoaded, setPricesLoaded] = useState(false);
  
  // Load vending prices from revenue streams ONLY on first load
  useEffect(() => {
    if (pricesLoaded) return; // Don't overwrite user edits
    const detergentStream = laundromat.revenue_streams?.['Detergent Sale'];
    const softenerStream = laundromat.revenue_streams?.['Softener Sale'];
    if (detergentStream || softenerStream) {
      if (detergentStream) setDetergentPrice(detergentStream.price?.toFixed(2) || '1.50');
      if (softenerStream) setSoftenerPrice(softenerStream.price?.toFixed(2) || '1.25');
      setPricesLoaded(true);
    }
  }, [laundromat.revenue_streams, pricesLoaded]);
  
  const updateVendingPrice = async (streamName: string, price: string) => {
    try {
      await fetch(`http://localhost:8000/revenue_streams/${encodeURIComponent(streamName)}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: 'p1', price: parseFloat(price) })
      });
      setEditingVending(null);
    } catch (err) {
      console.error('Failed to update vending price', err);
    }
  };

  const currentVendor = market.vendors?.find(v => v.id === selectedVendorId) || market.vendors?.[0];

  const handleNegotiate = async (item: string) => {
    setNegotiatingItem(item);
    try {
      const res = await fetch('http://localhost:8000/negotiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: 'p1', vendor_id: selectedVendorId, item })
      });
      const data = await res.json();
      setNegotiationResult({ item: data.item, price: data.offered_price, message: data.message });
      setTimeout(() => setNegotiationResult(null), 5000);
    } catch (err) {
      console.error("Negotiation failed", err);
    } finally {
      setNegotiatingItem(null);
    }
  };

  const handlePriceSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSetPrice(parseFloat(priceInput));
  };

  const supplies = [
    { id: 'soap', name: 'Detergent', icon: '🧴', color: 'blue', baseCost: 0.5 },
    { id: 'softener', name: 'Softener', icon: '🌸', color: 'pink', baseCost: 0.5 },
    { id: 'snacks', name: 'Snacks', icon: '🍫', color: 'amber', baseCost: 1.0 },
    { id: 'parts', name: 'Spare Parts', icon: '🔧', color: 'slate', baseCost: 10.0 },
    { id: 'cleaning_supplies', name: 'Cleaning', icon: '🧹', color: 'green', baseCost: 0.5 }
  ];

  const sections = [
    { id: 'pricing', label: 'Pricing', icon: DollarSign, color: 'emerald' },
    { id: 'supply', label: 'Supply', icon: ShoppingCart, color: 'blue' },
    { id: 'marketing', label: 'Marketing', icon: Megaphone, color: 'pink' },
    { id: 'upgrade', label: 'Upgrade', icon: Rocket, color: 'purple' }
  ];

  return (
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Hero Header */}
      <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 p-5 shadow-xl flex-shrink-0">
        {/* Animated background elements */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-0 left-1/4 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-0 right-1/4 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-white/5 via-transparent to-transparent"></div>
        </div>
        
        <div className="relative flex items-center justify-between">
          <div className="flex items-center gap-4">
            <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-lg shadow-blue-500/30 ring-2 ring-white/20">
              <Sparkles className="text-white" size={28} />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-white">Command Center</h2>
              <p className="text-slate-400 text-sm">Control every aspect of your business</p>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
            <div className="px-4 py-2 bg-white/10 backdrop-blur-sm rounded-xl border border-white/10">
              <div className="text-[10px] text-emerald-400 uppercase font-bold">Balance</div>
              <div className="text-xl font-bold text-white font-mono">${laundromat.balance.toFixed(0)}</div>
            </div>
          </div>
        </div>
      </div>

      {/* Section Tabs */}
      <div className="flex gap-2 flex-shrink-0">
        {sections.map(s => (
          <button 
            key={s.id}
            onClick={() => setActiveSection(s.id as typeof activeSection)}
            className={`flex-1 flex items-center justify-center gap-2 py-3 rounded-xl font-bold text-sm transition-all ${
              activeSection === s.id
                ? `bg-gradient-to-r from-${s.color}-500 to-${s.color}-600 text-white shadow-lg`
                : 'bg-white border border-gray-200 text-gray-600 hover:border-gray-300 hover:shadow-md'
            }`}
          >
            <s.icon size={18} />
            {s.label}
          </button>
        ))}
      </div>

      {/* Content Area */}
      <div className="flex-1 overflow-y-auto min-h-0">
        
        {/* Pricing Section */}
        {activeSection === 'pricing' && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            {/* Main Price Card */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-5">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                    <DollarSign className="text-white" size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">Wash Price</h3>
                    <p className="text-emerald-100 text-xs">Set competitive pricing</p>
                  </div>
                </div>
                
                <form onSubmit={handlePriceSubmit} className="flex gap-3">
                  <div className="flex-1 relative">
                    <span className="absolute left-4 top-1/2 -translate-y-1/2 text-emerald-700 font-bold text-lg">$</span>
                    <input 
                      type="number" 
                      step="0.1" 
                      value={priceInput} 
                      onChange={(e) => setPriceInput(e.target.value)}
                      className="w-full pl-10 pr-4 py-4 bg-white/95 backdrop-blur rounded-xl font-mono text-2xl font-bold text-gray-900 focus:ring-4 focus:ring-white/30 outline-none shadow-lg"
                    />
                  </div>
                  <button type="submit" className="px-8 bg-white text-emerald-600 rounded-xl font-bold hover:bg-emerald-50 transition-all shadow-lg flex items-center gap-2 hover:scale-105 active:scale-95">
                    <Zap size={18} />
                    Update
                  </button>
                </form>
              </div>
              
              {/* Price Tips */}
              <div className="p-5 grid grid-cols-3 gap-4">
                <div className="p-4 bg-gray-50 rounded-xl border border-gray-100 text-center group hover:bg-blue-50 hover:border-blue-200 transition-all cursor-default">
                  <div className="text-2xl mb-1">🏷️</div>
                  <div className="text-xs font-bold text-gray-500 uppercase">Budget</div>
                  <div className="font-mono font-bold text-gray-900">$2.00-3.00</div>
                </div>
                <div className="p-4 bg-emerald-50 rounded-xl border-2 border-emerald-200 text-center">
                  <div className="text-2xl mb-1">⭐</div>
                  <div className="text-xs font-bold text-emerald-600 uppercase">Optimal</div>
                  <div className="font-mono font-bold text-emerald-700">$3.00-5.00</div>
                </div>
                <div className="p-4 bg-gray-50 rounded-xl border border-gray-100 text-center group hover:bg-purple-50 hover:border-purple-200 transition-all cursor-default">
                  <div className="text-2xl mb-1">👑</div>
                  <div className="text-xs font-bold text-gray-500 uppercase">Premium</div>
                  <div className="font-mono font-bold text-gray-900">$5.00-8.00</div>
                </div>
              </div>
            </div>

            {/* Vending Prices */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm p-5">
              <h4 className="font-bold text-gray-800 mb-4 flex items-center gap-2">
                <ShoppingBag size={18} className="text-indigo-500" />
                Vending Machine Prices
                <span className="text-xs text-gray-400 font-normal ml-auto">Click to edit</span>
              </h4>
              <div className="grid grid-cols-2 gap-3">
                <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 rounded-xl border border-blue-200 hover:shadow-md transition-all">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">🧴</span>
                      <span className="font-bold text-gray-800">Detergent</span>
                    </div>
                    {editingVending === 'detergent' ? (
                      <div className="flex items-center gap-1">
                        <span className="text-indigo-600">$</span>
                        <input 
                          type="number" 
                          step="0.25" 
                          value={detergentPrice}
                          onChange={(e) => setDetergentPrice(e.target.value)}
                          className="w-16 px-2 py-1 text-lg font-mono font-bold rounded border border-indigo-300 focus:ring-2 focus:ring-indigo-400 outline-none"
                          autoFocus
                        />
                        <button 
                          onClick={() => updateVendingPrice('Detergent Sale', detergentPrice)}
                          className="p-1 bg-indigo-500 text-white rounded hover:bg-indigo-600"
                        >
                          <Check size={14} />
                        </button>
                      </div>
                    ) : (
                      <button 
                        onClick={() => setEditingVending('detergent')}
                        className="flex items-center gap-1 font-mono font-bold text-lg text-indigo-600 hover:text-indigo-800"
                      >
                        ${detergentPrice}
                        <Edit3 size={14} className="opacity-50" />
                      </button>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Customers buy if they don't bring their own</p>
                </div>
                <div className="p-4 bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl border border-pink-200 hover:shadow-md transition-all">
                  <div className="flex justify-between items-center">
                    <div className="flex items-center gap-2">
                      <span className="text-xl">🌸</span>
                      <span className="font-bold text-gray-800">Softener</span>
                    </div>
                    {editingVending === 'softener' ? (
                      <div className="flex items-center gap-1">
                        <span className="text-pink-600">$</span>
                        <input 
                          type="number" 
                          step="0.25" 
                          value={softenerPrice}
                          onChange={(e) => setSoftenerPrice(e.target.value)}
                          className="w-16 px-2 py-1 text-lg font-mono font-bold rounded border border-pink-300 focus:ring-2 focus:ring-pink-400 outline-none"
                          autoFocus
                        />
                        <button 
                          onClick={() => updateVendingPrice('Softener Sale', softenerPrice)}
                          className="p-1 bg-pink-500 text-white rounded hover:bg-pink-600"
                        >
                          <Check size={14} />
                        </button>
                      </div>
                    ) : (
                      <button 
                        onClick={() => setEditingVending('softener')}
                        className="flex items-center gap-1 font-mono font-bold text-lg text-pink-600 hover:text-pink-800"
                      >
                        ${softenerPrice}
                        <Edit3 size={14} className="opacity-50" />
                      </button>
                    )}
                  </div>
                  <p className="text-xs text-gray-500 mt-1">Optional premium add-on</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Supply Chain Section */}
        {activeSection === 'supply' && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            {/* Vendor Selector */}
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 p-5">
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                      <Truck className="text-white" size={20} />
                    </div>
                    <div>
                      <h3 className="font-bold text-white text-lg">Supply Chain</h3>
                      <p className="text-blue-100 text-xs">Manage your inventory</p>
                    </div>
                  </div>
                  
                  <select 
                    value={selectedVendorId} 
                    onChange={(e) => setSelectedVendorId(e.target.value)}
                    className="px-4 py-2 bg-white/95 backdrop-blur rounded-xl font-bold text-gray-800 shadow-lg focus:ring-2 focus:ring-white/30 outline-none"
                  >
                    {market.vendors?.map(v => (
                      <option key={v.id} value={v.id}>{v.name}</option>
                    ))}
                  </select>
                </div>

                {/* Vendor Stats */}
                {currentVendor && (
                  <div className="flex items-center gap-4">
                    <span className={`px-3 py-1 rounded-full font-bold text-xs uppercase ${
                      currentVendor.tier === 'STRATEGIC' ? 'bg-amber-400 text-amber-900' :
                      currentVendor.tier === 'PREFERRED' ? 'bg-blue-200 text-blue-800' :
                      'bg-white/30 text-white'
                    }`}>
                      {currentVendor.tier === 'STRATEGIC' && <Crown size={12} className="inline mr-1" />}
                      {currentVendor.tier}
                    </span>
                    <span className="text-white/80 text-sm flex items-center gap-1">
                      <Star size={14} fill="currentColor" className="text-yellow-300" />
                      {(currentVendor.reliability * 100).toFixed(0)}% reliable
                    </span>
                    <span className="text-white/80 text-sm flex items-center gap-1">
                      <Truck size={14} />
                      {currentVendor.delivery_days}d delivery
                    </span>
                  </div>
                )}
              </div>

              {/* Order Quantity */}
              <div className="p-4 border-b border-gray-100 flex items-center justify-between">
                <span className="font-bold text-gray-600">Order Quantity</span>
                <div className="flex gap-2">
                  {[10, 50, 100, 500].map(qty => (
                    <button
                      key={qty}
                      onClick={() => setBuyQuantity(qty)}
                      className={`px-4 py-2 rounded-lg font-bold text-sm transition-all ${
                        buyQuantity === qty
                          ? 'bg-blue-500 text-white shadow-md'
                          : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                      }`}
                    >
                      {qty}
                    </button>
                  ))}
                </div>
              </div>

              {/* Special Offer */}
              {currentVendor?.special_offer && (
                <div className="mx-4 mt-4 p-4 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl border-2 border-amber-200 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-amber-400 rounded-xl flex items-center justify-center shadow-md">
                      <Gift className="text-white" size={20} />
                    </div>
                    <div>
                      <div className="font-bold text-amber-900">{currentVendor.special_offer.description}</div>
                      <div className="text-xs text-amber-600">Limited time offer!</div>
                    </div>
                  </div>
                  <button 
                    onClick={() => onBuySupplies(currentVendor.special_offer!.item_name, buyQuantity, selectedVendorId)}
                    className="px-5 py-2 bg-amber-500 text-white rounded-xl font-bold hover:bg-amber-600 shadow-md transition-all hover:scale-105"
                  >
                    Claim
                  </button>
                </div>
              )}

              {/* Negotiation Result */}
              {negotiationResult && (
                <div className="mx-4 mt-4 p-4 bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl border-2 border-emerald-200">
                  <div className="flex items-center gap-2 mb-2">
                    <MessageSquare size={16} className="text-emerald-600" />
                    <span className="font-bold text-emerald-800">"{negotiationResult.message}"</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-emerald-700">New price: <strong className="font-mono">${negotiationResult.price.toFixed(2)}</strong></span>
                    <button 
                      onClick={() => {
                        onBuySupplies(negotiationResult.item, buyQuantity, selectedVendorId);
                        setNegotiationResult(null);
                      }}
                      className="px-4 py-1.5 bg-emerald-500 text-white rounded-lg font-bold hover:bg-emerald-600 transition-all"
                    >
                      Accept Deal
                    </button>
                  </div>
                </div>
              )}

              {/* Supply Items */}
              <div className="p-4 grid grid-cols-2 gap-3">
                {supplies.map(s => {
                  const inventoryKey = s.id === 'soap' ? 'detergent' : s.id;
                  const priceKey = s.id === 'soap' ? 'detergent' : s.id;
                  const currentPrice = currentVendor?.prices[priceKey] ?? s.baseCost;
                  const isDiscounted = currentPrice < s.baseCost;
                  const stock = laundromat.inventory[inventoryKey] || 0;
                  const lowStock = stock < 20;

                  return (
                    <div 
                      key={s.id} 
                      className={`group relative p-4 rounded-xl border-2 transition-all hover:shadow-lg ${
                        lowStock ? 'bg-red-50 border-red-200' : 'bg-white border-gray-200 hover:border-blue-300'
                      }`}
                    >
                      {isDiscounted && (
                        <div className="absolute -top-2 -right-2 w-8 h-8 bg-emerald-500 rounded-full flex items-center justify-center shadow-md">
                          <Percent size={14} className="text-white" />
                        </div>
                      )}
                      
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-center gap-2">
                          <span className="text-2xl">{s.icon}</span>
                          <div>
                            <div className="font-bold text-gray-900">{s.name}</div>
                            <div className={`text-xs font-bold ${lowStock ? 'text-red-600' : 'text-gray-500'}`}>
                              Stock: {stock}
                            </div>
                          </div>
                        </div>
                        <div className={`font-mono font-bold text-lg ${isDiscounted ? 'text-emerald-600' : 'text-gray-700'}`}>
                          ${currentPrice.toFixed(3)}
                        </div>
                      </div>
                      
                      <div className="flex gap-2">
                        <button 
                          onClick={() => handleNegotiate(s.id)}
                          disabled={negotiatingItem === s.id}
                          className="flex-1 px-3 py-2 bg-gray-100 text-gray-700 rounded-lg font-bold text-sm hover:bg-gray-200 transition-all flex items-center justify-center gap-1"
                        >
                          {negotiatingItem === s.id ? (
                            <div className="w-4 h-4 border-2 border-gray-600 border-t-transparent rounded-full animate-spin" />
                          ) : (
                            <>
                              <MessageSquare size={14} />
                              Negotiate
                            </>
                          )}
                        </button>
                        <button 
                          onClick={() => onBuySupplies(s.id, buyQuantity, selectedVendorId)}
                          className="flex-1 px-3 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg font-bold text-sm hover:shadow-md transition-all flex items-center justify-center gap-1 hover:scale-[1.02] active:scale-98"
                        >
                          <ShoppingCart size={14} />
                          Buy {buyQuantity}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}

        {/* Marketing Section */}
        {activeSection === 'marketing' && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="bg-gradient-to-r from-pink-500 via-rose-500 to-red-500 p-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                    <Megaphone className="text-white" size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">Marketing Campaigns</h3>
                    <p className="text-pink-100 text-xs">Boost your visibility & reputation</p>
                  </div>
                </div>
              </div>

              <div className="p-5 space-y-4">
                {/* Social Media Campaign */}
                <div className="group p-5 bg-gradient-to-br from-pink-50 to-rose-50 rounded-xl border-2 border-pink-200 hover:border-pink-300 hover:shadow-lg transition-all">
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-pink-500 to-rose-600 rounded-2xl flex items-center justify-center shadow-lg shadow-pink-200/50">
                      <span className="text-2xl">📱</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-bold text-gray-900 text-lg">Social Media Blast</h4>
                          <p className="text-sm text-gray-600">Viral marketing to attract customers</p>
                        </div>
                        <div className="text-right">
                          <div className="font-mono font-bold text-2xl text-pink-600">$100</div>
                          <div className="text-xs text-gray-500">one-time</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-4 mb-4">
                        <span className="px-2 py-1 bg-pink-100 text-pink-700 rounded text-xs font-bold flex items-center gap-1">
                          <ArrowUpRight size={12} /> +5 Social Score
                        </span>
                        <span className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs font-bold">
                          🎯 Instant Impact
                        </span>
                      </div>
                      <button 
                        onClick={() => onMarketingCampaign(100)}
                        disabled={laundromat.balance < 100}
                        className="w-full py-3 bg-gradient-to-r from-pink-500 to-rose-600 text-white rounded-xl font-bold hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-98"
                      >
                        <Zap size={18} />
                        Launch Campaign
                      </button>
                    </div>
                  </div>
                </div>

                {/* Coming Soon */}
                <div className="p-5 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 relative overflow-hidden">
                  <div className="absolute top-2 right-2 px-2 py-0.5 bg-gray-200 text-gray-500 rounded text-xs font-bold">COMING SOON</div>
                  <div className="flex items-center gap-4 opacity-50">
                    <div className="w-14 h-14 bg-gray-300 rounded-2xl flex items-center justify-center">
                      <span className="text-2xl">📺</span>
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-700 text-lg">Local TV Spot</h4>
                      <p className="text-sm text-gray-500">Premium brand awareness</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Upgrade Section */}
        {activeSection === 'upgrade' && (
          <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
            <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden">
              <div className="bg-gradient-to-r from-purple-500 via-violet-500 to-indigo-600 p-5">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-white/20 rounded-xl flex items-center justify-center">
                    <Rocket className="text-white" size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold text-white text-lg">Business Expansion</h3>
                    <p className="text-purple-100 text-xs">Invest in growth & capacity</p>
                  </div>
                </div>
              </div>

              <div className="p-5 space-y-4">
                {/* Machine Upgrade */}
                <div className="group p-5 bg-gradient-to-br from-purple-50 to-violet-50 rounded-xl border-2 border-purple-200 hover:border-purple-300 hover:shadow-lg transition-all">
                  <div className="flex items-start gap-4">
                    <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-violet-600 rounded-2xl flex items-center justify-center shadow-lg shadow-purple-200/50">
                      <span className="text-2xl">🧺</span>
                    </div>
                    <div className="flex-1">
                      <div className="flex justify-between items-start mb-2">
                        <div>
                          <h4 className="font-bold text-gray-900 text-lg">New Washing Machine</h4>
                          <p className="text-sm text-gray-600">Increase capacity & serve more customers</p>
                        </div>
                        <div className="text-right">
                          <div className="font-mono font-bold text-2xl text-purple-600">$500</div>
                          <div className="text-xs text-gray-500">investment</div>
                        </div>
                      </div>
                      <div className="flex items-center gap-3 mb-4">
                        <span className="px-2 py-1 bg-purple-100 text-purple-700 rounded text-xs font-bold flex items-center gap-1">
                          <ArrowUpRight size={12} /> +1 Machine
                        </span>
                        <span className="px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs font-bold">
                          💰 +$50-100/week
                        </span>
                      </div>
                      <div className="flex items-center gap-2 mb-4 text-sm text-gray-600">
                        <span>Current Capacity:</span>
                        <span className="font-bold text-purple-700">{laundromat.machines} machines</span>
                      </div>
                      <button 
                        onClick={() => onUpgrade('machine')}
                        disabled={laundromat.balance < 500}
                        className="w-full py-3 bg-gradient-to-r from-purple-500 to-violet-600 text-white rounded-xl font-bold hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 hover:scale-[1.02] active:scale-98"
                      >
                        <ChevronRight size={18} />
                        Purchase Upgrade
                      </button>
                    </div>
                  </div>
                </div>

                {/* Future upgrade placeholder */}
                <div className="p-5 bg-gray-50 rounded-xl border-2 border-dashed border-gray-200 relative overflow-hidden">
                  <div className="absolute top-2 right-2 px-2 py-0.5 bg-gray-200 text-gray-500 rounded text-xs font-bold">COMING SOON</div>
                  <div className="flex items-center gap-4 opacity-50">
                    <div className="w-14 h-14 bg-gray-300 rounded-2xl flex items-center justify-center">
                      <span className="text-2xl">🏪</span>
                    </div>
                    <div>
                      <h4 className="font-bold text-gray-700 text-lg">Store Renovation</h4>
                      <p className="text-sm text-gray-500">Premium customer experience</p>
                    </div>
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

export default ControlPanel;
