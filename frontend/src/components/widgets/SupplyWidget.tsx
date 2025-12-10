import React, { useState } from 'react';
import { Truck, Star, Gift, MessageSquare, ShoppingCart, Percent } from 'lucide-react';
import type { Laundromat, GameState } from '../../types';

interface SupplyWidgetProps {
  laundromat: Laundromat;
  market: GameState['market'];
  onBuySupplies: (item: string, quantity: number, vendor_id?: string) => void;
}

const SupplyWidget: React.FC<SupplyWidgetProps> = ({ laundromat, market, onBuySupplies }) => {
  const [buyQuantity, setBuyQuantity] = useState(10);
  const [selectedVendorId, setSelectedVendorId] = useState<string>('bulkwash');
  const [negotiatingItem, setNegotiatingItem] = useState<string | null>(null);
  const [negotiationResult, setNegotiationResult] = useState<{item: string, price: number, message: string} | null>(null);

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

  const supplies = [
    { id: 'soap', name: 'Detergent', icon: '🧴', color: 'blue', baseCost: 0.5 },
    { id: 'softener', name: 'Softener', icon: '🌸', color: 'pink', baseCost: 0.5 },
    { id: 'snacks', name: 'Snacks', icon: '🍫', color: 'amber', baseCost: 1.0 },
    { id: 'parts', name: 'Spare Parts', icon: '🔧', color: 'slate', baseCost: 10.0 },
    { id: 'cleaning_supplies', name: 'Cleaning', icon: '🧹', color: 'green', baseCost: 0.5 }
  ];

  return (
    <div className="space-y-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
      {/* Vendor Selector */}
      <div className="bg-slate-800 rounded-2xl border border-slate-700 shadow-sm overflow-hidden">
        <div className="bg-gradient-to-r from-blue-900 via-indigo-900 to-purple-900 p-5 border-b border-white/10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/10 rounded-xl flex items-center justify-center border border-white/10">
                <Truck className="text-white" size={20} />
              </div>
              <div>
                <h3 className="font-bold text-white text-lg">Supply Chain</h3>
                <p className="text-blue-200 text-xs">Manage your inventory</p>
              </div>
            </div>
            
            <select 
              value={selectedVendorId} 
              onChange={(e) => setSelectedVendorId(e.target.value)}
              className="px-4 py-2 bg-slate-900/50 backdrop-blur rounded-xl font-bold text-white shadow-inner border border-slate-700 focus:ring-2 focus:ring-blue-500/50 outline-none"
            >
              {market.vendors?.map(v => (
                <option key={v.id} value={v.id} className="bg-slate-800">{v.name}</option>
              ))}
            </select>
          </div>

          {/* Vendor Stats */}
          {currentVendor && (
            <div className="flex items-center gap-4">
              <span className={`px-3 py-1 rounded-full font-bold text-xs uppercase ${
                currentVendor.tier === 'STRATEGIC' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                currentVendor.tier === 'PREFERRED' ? 'bg-blue-500/20 text-blue-300 border border-blue-500/30' :
                'bg-slate-700 text-slate-300'
              }`}>
                {currentVendor.tier}
              </span>
              <span className="text-slate-300 text-sm flex items-center gap-1">
                <Star size={14} fill="currentColor" className="text-amber-400" />
                {(currentVendor.reliability * 100).toFixed(0)}% reliable
              </span>
              <span className="text-slate-300 text-sm flex items-center gap-1">
                <Truck size={14} />
                {currentVendor.delivery_days}d delivery
              </span>
            </div>
          )}
        </div>

        {/* Order Quantity */}
        <div className="p-4 border-b border-slate-700 flex items-center justify-between bg-slate-800/50">
          <span className="font-bold text-slate-400">Order Quantity</span>
          <div className="flex gap-2">
            {[10, 50, 100, 500].map(qty => (
              <button
                key={qty}
                onClick={() => setBuyQuantity(qty)}
                className={`px-4 py-2 rounded-lg font-bold text-sm transition-all border ${
                  buyQuantity === qty
                    ? 'bg-blue-600 text-white border-blue-500 shadow-md'
                    : 'bg-slate-800 text-slate-400 border-slate-700 hover:bg-slate-700 hover:text-white'
                }`}
              >
                {qty}
              </button>
            ))}
          </div>
        </div>

        {/* Special Offer */}
        {currentVendor?.special_offer && (
          <div className="mx-4 mt-4 p-4 bg-gradient-to-r from-amber-900/30 to-yellow-900/30 rounded-xl border border-amber-500/30 flex items-center justify-between relative overflow-hidden">
             <div className="absolute inset-0 bg-amber-500/5 animate-pulse"></div>
            <div className="relative flex items-center gap-3">
              <div className="w-10 h-10 bg-amber-500/20 rounded-xl flex items-center justify-center shadow-lg shadow-amber-900/20 border border-amber-500/20">
                <Gift className="text-amber-400" size={20} />
              </div>
              <div>
                <div className="font-bold text-amber-400">{currentVendor.special_offer.description}</div>
                <div className="text-xs text-amber-500/80">Limited time offer!</div>
              </div>
            </div>
            <button 
              onClick={() => onBuySupplies(currentVendor.special_offer!.item_name, buyQuantity, selectedVendorId)}
              className="relative px-5 py-2 bg-amber-600 text-white rounded-xl font-bold hover:bg-amber-500 shadow-lg shadow-amber-900/30 transition-all hover:scale-105 border border-amber-400/30"
            >
              Claim
            </button>
          </div>
        )}

        {/* Negotiation Result */}
        {negotiationResult && (
          <div className="mx-4 mt-4 p-4 bg-gradient-to-r from-emerald-900/30 to-green-900/30 rounded-xl border border-emerald-500/30">
            <div className="flex items-center gap-2 mb-2">
              <MessageSquare size={16} className="text-emerald-400" />
              <span className="font-bold text-emerald-300">"{negotiationResult.message}"</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-emerald-400">New price: <strong className="font-mono text-emerald-300">${negotiationResult.price.toFixed(2)}</strong></span>
              <button 
                onClick={() => {
                  onBuySupplies(negotiationResult.item, buyQuantity, selectedVendorId);
                  setNegotiationResult(null);
                }}
                className="px-4 py-1.5 bg-emerald-600 text-white rounded-lg font-bold hover:bg-emerald-500 transition-all shadow-lg shadow-emerald-900/20 border border-emerald-500/30"
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
                className={`group relative p-4 rounded-xl border transition-all hover:shadow-lg hover:border-opacity-100 ${
                  lowStock 
                    ? 'bg-rose-900/10 border-rose-500/30 hover:bg-rose-900/20 hover:border-rose-500/50' 
                    : 'bg-slate-800 border-slate-700 hover:border-blue-500/50 hover:bg-slate-750'
                }`}
              >
                {isDiscounted && (
                  <div className="absolute -top-2 -right-2 w-8 h-8 bg-emerald-600 rounded-full flex items-center justify-center shadow-lg shadow-emerald-900/30 border border-white/10 z-10">
                    <Percent size={14} className="text-white" />
                  </div>
                )}
                
                <div className="flex items-start justify-between mb-3">
                  <div className="flex items-center gap-2">
                    <span className="text-2xl filter drop-shadow-md">{s.icon}</span>
                    <div>
                      <div className="font-bold text-white">{s.name}</div>
                      <div className={`text-xs font-bold ${lowStock ? 'text-rose-400 animate-pulse' : 'text-slate-500'}`}>
                        Stock: {stock}
                      </div>
                    </div>
                  </div>
                  <div className={`font-mono font-bold text-lg ${isDiscounted ? 'text-emerald-400' : 'text-slate-300'}`}>
                    ${currentPrice.toFixed(3)}
                  </div>
                </div>
                
                <div className="flex gap-2">
                  <button 
                    onClick={() => handleNegotiate(s.id)}
                    disabled={negotiatingItem === s.id}
                    className="flex-1 px-3 py-2 bg-slate-700 text-slate-300 rounded-lg font-bold text-sm hover:bg-slate-600 hover:text-white transition-all flex items-center justify-center gap-1"
                  >
                    {negotiatingItem === s.id ? (
                      <div className="w-4 h-4 border-2 border-slate-400 border-t-transparent rounded-full animate-spin" />
                    ) : (
                      <>
                        <MessageSquare size={14} />
                        Neg.
                      </>
                    )}
                  </button>
                  <button 
                    onClick={() => onBuySupplies(s.id, buyQuantity, selectedVendorId)}
                    className="flex-1 px-3 py-2 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-lg font-bold text-sm hover:shadow-lg hover:shadow-blue-900/20 transition-all flex items-center justify-center gap-1 hover:scale-[1.02] active:scale-98 border border-white/10"
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
  );
};

export default SupplyWidget;
