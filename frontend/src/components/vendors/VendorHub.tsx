import { useState } from 'react';
import {
    Store,
    Truck,
    Star,
    DollarSign,
    Package,
    Handshake,
    Timer,
    Leaf,
    AlertTriangle,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Button, Badge } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// VendorHub Component
// Displays all vendors, their pricing, and allows negotiation
// ═══════════════════════════════════════════════════════════════════════

export default function VendorHub() {
    const { getVendors, negotiate, isLoading, gameState } = useGameStore();
    const vendors = getVendors();
    const [activeVendor, setActiveVendor] = useState<string | null>(null);
    const [negotiationResult, setNegotiationResult] = useState<{
        success: boolean;
        message: string;
    } | null>(null);

    const handleNegotiate = async (vendorId: string, item: string) => {
        setNegotiationResult(null);
        try {
            const result = await negotiate(vendorId, item);
            setNegotiationResult({
                success: result.accepted,
                message: result.message || (result.accepted ? 'Price reduced!' : 'Offer rejected.'),
            });
        } catch (e) {
            setNegotiationResult({ success: false, message: 'Negotiation failed.' });
        }
    };

    if (!vendors || vendors.length === 0) {
        return (
            <Card variant="glass" className="text-center py-12">
                <Store className="w-12 h-12 mx-auto text-slate-500 mb-4" />
                <p className="text-slate-400">No vendor data available.</p>
                <p className="text-xs text-slate-500 mt-2">
                    Vendor information loads with game state.
                </p>
            </Card>
        );
    }

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Store className="w-6 h-6 text-amber-400" />
                    Vendor Marketplace
                </h2>
                <Badge variant="info">
                    {vendors.length} Vendors Available
                </Badge>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {vendors.map((vendor) => (
                    <Card
                        key={vendor.id}
                        variant={activeVendor === vendor.id ? 'glow' : 'glass'}
                        hover
                        onClick={() => setActiveVendor(activeVendor === vendor.id ? null : vendor.id)}
                        className="cursor-pointer transition-all"
                    >
                        {/* Header */}
                        <div className="flex items-start justify-between mb-3">
                            <div>
                                <h3 className="font-semibold text-white text-lg">{vendor.name}</h3>
                                <p className="text-xs text-slate-400 italic">{vendor.slogan || 'Quality Supplies'}</p>
                            </div>
                            <Badge
                                variant={
                                    vendor.tier === 4 ? 'success' :
                                        vendor.tier === 3 ? 'info' :
                                            vendor.tier === 2 ? 'warning' : 'default'
                                }
                            >
                                {['New', 'Regular', 'Preferred', 'Strategic'][vendor.tier - 1] || 'New'}
                            </Badge>
                        </div>

                        {/* Quick Stats */}
                        <div className="grid grid-cols-3 gap-2 mb-4 text-center">
                            <div className="p-2 rounded bg-white/5">
                                <Timer className="w-4 h-4 mx-auto text-blue-400 mb-1" />
                                <p className="text-xs text-slate-400">Delivery</p>
                                <p className="text-sm font-medium text-white">{vendor.delivery_days || 2}d</p>
                            </div>
                            <div className="p-2 rounded bg-white/5">
                                <Star className="w-4 h-4 mx-auto text-yellow-400 mb-1" />
                                <p className="text-xs text-slate-400">Reliability</p>
                                <p className="text-sm font-medium text-white">{((vendor.reliability || 0.8) * 100).toFixed(0)}%</p>
                            </div>
                            <div className="p-2 rounded bg-white/5">
                                <Leaf className="w-4 h-4 mx-auto text-green-400 mb-1" />
                                <p className="text-xs text-slate-400">Eco Score</p>
                                <p className="text-sm font-medium text-white">{((vendor.sustainability || 0.5) * 100).toFixed(0)}%</p>
                            </div>
                        </div>

                        {/* Expanded Details */}
                        {activeVendor === vendor.id && (
                            <div className="border-t border-white/10 pt-4 mt-2 space-y-3 animate-fade-in">
                                <p className="text-sm text-slate-300">{vendor.description || 'A reliable supplier for your laundromat needs.'}</p>

                                {/* Pricing Table */}
                                <div className="space-y-2">
                                    <h4 className="text-xs uppercase text-slate-500 font-semibold">Current Prices</h4>
                                    {vendor.base_prices && Object.entries(vendor.base_prices).map(([item, price]) => (
                                        <div key={item} className="flex items-center justify-between p-2 rounded bg-white/5">
                                            <span className="text-slate-300 capitalize">{item.replace(/_/g, ' ')}</span>
                                            <div className="flex items-center gap-2">
                                                <span className="text-emerald-400 font-medium">${(price as number).toFixed(2)}</span>
                                                <Button
                                                    variant="ghost"
                                                    size="sm"
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        handleNegotiate(vendor.id, item);
                                                    }}
                                                    loading={isLoading}
                                                    title="Attempt Negotiation"
                                                >
                                                    <Handshake className="w-4 h-4" />
                                                </Button>
                                            </div>
                                        </div>
                                    ))}
                                </div>

                                {/* Risks */}
                                {vendor.risks && vendor.risks.length > 0 && (
                                    <div className="flex items-start gap-2 p-2 rounded bg-amber-500/10 border border-amber-500/20">
                                        <AlertTriangle className="w-4 h-4 text-amber-400 flex-shrink-0 mt-0.5" />
                                        <p className="text-xs text-amber-300">{vendor.risks.join(', ')}</p>
                                    </div>
                                )}

                                {/* Order Button */}
                                <Button
                                    variant="primary"
                                    className="w-full mt-2"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        // Navigate to supplies tab or open order modal
                                        // For now, just indicate which vendor to use
                                        alert(`To order from ${vendor.name}, go to Operations > Supplies.`);
                                    }}
                                >
                                    <Package className="w-4 h-4 mr-2" /> View Catalog
                                </Button>
                            </div>
                        )}

                        {/* Negotiation Result Toast (inline) */}
                        {activeVendor === vendor.id && negotiationResult && (
                            <div
                                className={`mt-3 p-2 rounded text-xs text-center ${negotiationResult.success
                                        ? 'bg-emerald-500/20 text-emerald-300'
                                        : 'bg-red-500/20 text-red-300'
                                    }`}
                            >
                                {negotiationResult.message}
                            </div>
                        )}
                    </Card>
                ))}
            </div>
        </div>
    );
}
