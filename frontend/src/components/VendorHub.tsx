import React from 'react';
import { ShoppingCart, MessageCircle, Truck, Star, AlertTriangle } from 'lucide-react';
import type { Vendor } from '../types';

interface VendorHubProps {
  vendors: Vendor[];
  supplyChainEvents: any[];
  onBuy: (item: string, qty: number, vendorId: string) => void;
  onNegotiate: (vendorId: string, item: string) => void;
  isOpen: boolean;
  onClose: () => void;
}

const VendorHub: React.FC<VendorHubProps> = ({ vendors, supplyChainEvents, onBuy, onNegotiate, isOpen, onClose }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-5xl max-h-[90vh] overflow-hidden flex flex-col">
        
        {/* Header */}
        <div className="p-6 border-b border-gray-100 flex justify-between items-center bg-gray-50">
          <div>
            <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
              <Truck className="text-blue-600" /> Vendor Hub
            </h2>
            <p className="text-gray-500 text-sm">Manage your supply chain and negotiate contracts</p>
          </div>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600 transition-colors">
            <span className="text-2xl">×</span>
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6 bg-gray-50/50">
          
          {/* Supply Chain Alerts */}
          {supplyChainEvents && supplyChainEvents.length > 0 && (
            <div className="mb-8">
              <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-3">Supply Chain Alerts</h3>
              <div className="grid gap-3">
                {supplyChainEvents.map((event, idx) => (
                  <div key={idx} className={`p-4 rounded-xl border-l-4 flex items-start gap-3 ${
                    event.severity === 'critical' ? 'bg-red-50 border-red-500 text-red-900' : 'bg-orange-50 border-orange-500 text-orange-900'
                  }`}>
                    <AlertTriangle size={20} className="shrink-0 mt-0.5" />
                    <div>
                      <span className="font-bold block text-sm">{event.vendor_id ? `Alert: ${event.vendor_id}` : 'General Alert'}</span>
                      <p className="text-sm opacity-90">{event.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Vendors Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {vendors.map(vendor => (
              <div key={vendor.id} className="bg-white rounded-xl border border-gray-200 shadow-sm hover:shadow-md transition-shadow overflow-hidden">
                {/* Vendor Header */}
                <div className="p-5 border-b border-gray-100 bg-gradient-to-r from-white to-gray-50">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="text-lg font-bold text-gray-900">{vendor.name}</h3>
                      <div className="flex items-center gap-2 text-xs text-gray-500 mt-1">
                        <span className={`px-2 py-0.5 rounded-full font-medium ${
                          vendor.tier === 'Premium' ? 'bg-purple-100 text-purple-700' :
                          vendor.tier === 'Standard' ? 'bg-blue-100 text-blue-700' :
                          'bg-gray-100 text-gray-700'
                        }`}>
                          {vendor.tier} Tier
                        </span>
                        <span>•</span>
                        <span>{vendor.delivery_days} Day Delivery</span>
                      </div>
                    </div>
                    <div className="flex flex-col items-end">
                      <div className="flex items-center gap-1 text-yellow-500 font-bold">
                        <Star size={14} fill="currentColor" />
                        <span>{(vendor.reliability * 100).toFixed(0)}%</span>
                      </div>
                      <span className="text-[10px] text-gray-400 uppercase tracking-wide">Reliability</span>
                    </div>
                  </div>
                  <p className="text-sm text-gray-500 italic">"{vendor.slogan}"</p>
                </div>

                {/* Special Offer */}
                {vendor.special_offer && (
                  <div className="px-5 py-3 bg-green-50 border-y border-green-100 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-full bg-green-100 flex items-center justify-center text-green-600 shrink-0">
                      <Star size={16} />
                    </div>
                    <div>
                      <div className="text-xs font-bold text-green-800 uppercase tracking-wide">Special Offer</div>
                      <div className="text-sm text-green-900 font-medium">{vendor.special_offer.description}</div>
                    </div>
                  </div>
                )}

                {/* Products Table */}
                <div className="p-2">
                  <table className="w-full text-sm">
                    <thead className="text-xs text-gray-400 uppercase bg-gray-50/50">
                      <tr>
                        <th className="px-3 py-2 text-left font-medium">Item</th>
                        <th className="px-3 py-2 text-right font-medium">Price</th>
                        <th className="px-3 py-2 text-right font-medium">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-gray-50">
                      {Object.entries(vendor.prices).map(([item, price]) => (
                        <tr key={item} className="group hover:bg-gray-50 transition-colors">
                          <td className="px-3 py-3 font-medium text-gray-700 capitalize">
                            {item === 'soap' ? 'Detergent' : item.replace('_', ' ')}
                          </td>
                          <td className="px-3 py-3 text-right text-gray-900 font-mono">${price.toFixed(2)}</td>
                          <td className="px-3 py-3 text-right">
                            <div className="flex justify-end gap-2 opacity-0 group-hover:opacity-100 transition-opacity">
                              <button 
                                onClick={() => onNegotiate(vendor.id, item)}
                                className="p-1.5 text-orange-600 hover:bg-orange-50 rounded-lg transition-colors"
                                title="Negotiate Price"
                              >
                                <MessageCircle size={16} />
                              </button>
                              <button 
                                onClick={() => onBuy(item, 100, vendor.id)}
                                className="flex items-center gap-1 px-2 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors shadow-sm shadow-blue-200"
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
      </div>
    </div>
  );
};

export default VendorHub;
