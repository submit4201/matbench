import { useState } from 'react';
import {
    Store,
    Star,
    Package,
    Handshake,
    Timer,
    Leaf,
    AlertTriangle,
    ShoppingCart,
    TrendingDown,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Button, Badge } from '../shared';
import { toast } from 'sonner';

// ═══════════════════════════════════════════════════════════════════════
// VendorHub Component
// Displays vendors, pricing, ordering, and negotiation
// ═══════════════════════════════════════════════════════════════════════

export default function VendorHub() {
    const { getVendors, negotiate, isLoading, getPlayerLaundromat, sendAction } = useGameStore();
    const vendors = getVendors();
    const laundromat = getPlayerLaundromat();
    const [activeVendor, setActiveVendor] = useState<string | null>(null);
    const [orderQuantity, setOrderQuantity] = useState(50);
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
        } catch {
            setNegotiationResult({ success: false, message: 'Negotiation failed.' });
        }
    };

    const handleOrder = async (vendorId: string, item: string, price: number) => {
        const totalCost = price * orderQuantity;
        if (laundromat && laundromat.balance < totalCost) {
            toast.error(`Insufficient funds. Need $${totalCost.toFixed(2)}`);
            return;
        }

        const success = await sendAction('BUY_SUPPLIES', { item, quantity: orderQuantity, vendor_id: vendorId });
        if (success) {
            toast.success(`Ordered ${orderQuantity} ${item}`, {
                description: `$${totalCost.toFixed(2)} - check calendar for delivery`,
            });
        }
    };

    // Map item names for inventory lookup
    const getInventoryKey = (item: string): string => {
        if (item === 'soap') return 'detergent';
        return item;
    };

    const getInventoryLevel = (item: string): number => {
        if (!laundromat?.inventory) return 0;
        const key = getInventoryKey(item);
        return (laundromat.inventory[key] as number) || 0;
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
        <div className="space-y-4 animate-fade-in">
            <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold text-white flex items-center gap-2">
                    <Store className="w-5 h-5 text-amber-400" />
                    Vendor Marketplace
                </h2>
                <div className="flex items-center gap-2">
                    <span className="text-xs text-slate-400">Order Qty:</span>
                    <div className="flex rounded-md overflow-hidden border border-white/20 text-xs">
                        {[10, 50, 100, 500].map((qty) => (
                            <button
                                key={qty}
                                className={`px-2 py-1 ${orderQuantity === qty ? 'bg-blue-500 text-white' : 'bg-slate-700 text-slate-300 hover:bg-slate-600'}`}
                                onClick={() => setOrderQuantity(qty)}
                            >
                                {qty}
                            </button>
                        ))}
                    </div>
                    <Badge variant="info">{vendors.length} Vendors</Badge>
                </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
                {vendors.map((vendor) => {
                    // Vendor tier mapping
                    const tierMap: { [key: string]: number } = { NEW: 1, REGULAR: 2, PREFERRED: 3, STRATEGIC: 4 };
                    const vendorTier = typeof vendor.tier === 'string' ? (tierMap[vendor.tier] || 1) : 1;

                    const deliveryDays = vendor.delivery_days ?? 2;
                    const reliability = vendor.reliability ?? 0.8;
                    const sustainability = vendor.sustainability ?? 0;
                    const description = vendor.description || 'A reliable supplier.';
                    const prices = vendor.prices || {};
                    const risks = vendor.risks || [];

                    return (
                        <Card
                            key={vendor.id}
                            variant={activeVendor === vendor.id ? 'glow' : 'glass'}
                            hover
                            onClick={() => setActiveVendor(activeVendor === vendor.id ? null : vendor.id)}
                            className="cursor-pointer transition-all"
                        >
                            {/* Header */}
                            <div className="flex items-start justify-between mb-2">
                                <div>
                                    <h3 className="font-semibold text-white">{vendor.name}</h3>
                                    <p className="text-[10px] text-slate-400 italic">{vendor.slogan || 'Quality Supplies'}</p>
                                </div>
                                <Badge
                                    variant={
                                        vendorTier === 4 ? 'success' :
                                            vendorTier === 3 ? 'info' :
                                                vendorTier === 2 ? 'warning' : 'default'
                                    }
                                >
                                    {['New', 'Regular', 'Preferred', 'Strategic'][vendorTier - 1] || 'New'}
                                </Badge>
                            </div>

                            {/* Quick Stats */}
                            <div className="grid grid-cols-3 gap-1 mb-2 text-center">
                                <div className="p-1.5 rounded bg-white/5">
                                    <Timer className="w-3 h-3 mx-auto text-blue-400 mb-0.5" />
                                    <p className="text-[10px] text-slate-400">Delivery</p>
                                    <p className="text-xs font-medium text-white">{deliveryDays}d</p>
                                </div>
                                <div className="p-1.5 rounded bg-white/5">
                                    <Star className="w-3 h-3 mx-auto text-yellow-400 mb-0.5" />
                                    <p className="text-[10px] text-slate-400">Reliable</p>
                                    <p className="text-xs font-medium text-white">{(reliability * 100).toFixed(0)}%</p>
                                </div>
                                <div className="p-1.5 rounded bg-white/5">
                                    <Leaf className="w-3 h-3 mx-auto text-green-400 mb-0.5" />
                                    <p className="text-[10px] text-slate-400">Eco</p>
                                    <p className="text-xs font-medium text-white">{(sustainability * 100).toFixed(0)}%</p>
                                </div>
                            </div>

                            {/* Expanded: Ordering Interface */}
                            {activeVendor === vendor.id && (
                                <div className="border-t border-white/10 pt-3 mt-2 space-y-2 animate-fade-in">
                                    <p className="text-xs text-slate-400">{description}</p>

                                    {/* Item Order List */}
                                    <div className="space-y-1.5">
                                        <h4 className="text-[10px] uppercase text-slate-500 font-semibold">Order Supplies</h4>
                                        {Object.entries(prices).map(([item, price]) => {
                                            const priceNum = price as number;
                                            const stock = getInventoryLevel(item);
                                            const lowStock = stock < 20;
                                            const totalCost = priceNum * orderQuantity;

                                            return (
                                                <div key={item} className={`flex items-center justify-between p-2 rounded ${lowStock ? 'bg-red-500/10 border border-red-500/20' : 'bg-white/5'}`}>
                                                    <div className="flex items-center gap-2">
                                                        <Package className="w-4 h-4 text-slate-400" />
                                                        <div>
                                                            <span className="text-sm text-slate-200 capitalize">{item.replace(/_/g, ' ')}</span>
                                                            <div className="flex items-center gap-1 text-[10px]">
                                                                <span className={lowStock ? 'text-red-400' : 'text-slate-500'}>Stock: {stock}</span>
                                                                {lowStock && <TrendingDown className="w-3 h-3 text-red-400" />}
                                                            </div>
                                                        </div>
                                                    </div>
                                                    <div className="flex items-center gap-1.5">
                                                        <div className="text-right">
                                                            <span className="text-emerald-400 font-medium text-sm">${priceNum.toFixed(2)}</span>
                                                            <p className="text-[10px] text-slate-500">= ${totalCost.toFixed(2)}</p>
                                                        </div>
                                                        <Button
                                                            variant="ghost"
                                                            size="sm"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                handleNegotiate(vendor.id, item);
                                                            }}
                                                            loading={isLoading}
                                                            title="Negotiate"
                                                            className="!p-1"
                                                        >
                                                            <Handshake className="w-3.5 h-3.5" />
                                                        </Button>
                                                        <Button
                                                            variant="primary"
                                                            size="sm"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                handleOrder(vendor.id, item, priceNum);
                                                            }}
                                                            loading={isLoading}
                                                            className="!px-2 !py-1"
                                                        >
                                                            <ShoppingCart className="w-3 h-3 mr-1" />
                                                            Buy
                                                        </Button>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>

                                    {/* Risks */}
                                    {risks.length > 0 && (
                                        <div className="flex items-start gap-2 p-2 rounded bg-amber-500/10 border border-amber-500/20">
                                            <AlertTriangle className="w-3.5 h-3.5 text-amber-400 flex-shrink-0 mt-0.5" />
                                            <p className="text-[10px] text-amber-300">{risks.join(', ')}</p>
                                        </div>
                                    )}
                                </div>
                            )}

                            {/* Negotiation Result */}
                            {activeVendor === vendor.id && negotiationResult && (
                                <div
                                    className={`mt-2 p-2 rounded text-xs text-center ${negotiationResult.success
                                        ? 'bg-emerald-500/20 text-emerald-300'
                                        : 'bg-red-500/20 text-red-300'
                                        }`}
                                >
                                    {negotiationResult.message}
                                </div>
                            )}
                        </Card>
                    );
                })}
            </div>
        </div>
    );
}
