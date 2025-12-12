import { useEffect, useState } from 'react';
import {
    TrendingUp,
    TrendingDown,
    Newspaper,
    Package,
    AlertCircle,
    RefreshCw,
} from 'lucide-react';
import { Card, Badge, Button } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// MarketPanel Component
// Market trends, vendor prices, and supply chain events
// ═══════════════════════════════════════════════════════════════════════

interface MarketTrend {
    week?: number;
    status?: string;
    impact_resource?: string;
    price_factor?: number;
    demand_factor?: number;
    headline?: string;
}

interface VendorPrice {
    name: string;
    prices: Record<string, number>;
}

interface SupplyChainEvent {
    vendor_id: string;
    event_type: string;
    impact: number;
    message?: string;
}

interface MarketData {
    current_week: number;
    trend: MarketTrend;
    vendor_prices: Record<string, VendorPrice>;
    supply_chain_events: SupplyChainEvent[];
}

export default function MarketPanel() {
    const [marketData, setMarketData] = useState<MarketData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const fetchMarketData = async () => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch('http://localhost:8000/market');
            if (!response.ok) throw new Error('Failed to fetch market data');
            const data = await response.json();
            setMarketData(data);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        }
        setLoading(false);
    };

    useEffect(() => {
        fetchMarketData();
    }, []);

    if (loading && !marketData) {
        return (
            <Card variant="glass" className="text-center py-12 animate-pulse">
                <RefreshCw className="w-8 h-8 mx-auto text-slate-400 animate-spin" />
                <p className="text-slate-400 mt-4">Loading market data...</p>
            </Card>
        );
    }

    if (error) {
        return (
            <Card variant="outline" className="text-center py-12">
                <AlertCircle className="w-8 h-8 mx-auto text-red-400" />
                <p className="text-red-400 mt-4">{error}</p>
                <Button variant="secondary" size="sm" onClick={fetchMarketData} className="mt-4">
                    Retry
                </Button>
            </Card>
        );
    }

    const trend = marketData?.trend || {};
    const vendorPrices = marketData?.vendor_prices || {};
    const supplyChainEvents = marketData?.supply_chain_events || [];

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-semibold text-white flex items-center gap-2">
                    <TrendingUp className="w-6 h-6 text-emerald-400" />
                    Market Analysis
                </h2>
                <Button variant="ghost" size="sm" onClick={fetchMarketData} loading={loading}>
                    <RefreshCw className="w-4 h-4" />
                    Refresh
                </Button>
            </div>

            {/* Market Trend Card */}
            <Card variant="glow">
                <div className="flex items-start gap-4">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${trend.status === 'Volatile' ? 'bg-red-500/20 text-red-400' : 'bg-emerald-500/20 text-emerald-400'
                        }`}>
                        {trend.status === 'Volatile' ? <TrendingDown className="w-6 h-6" /> : <TrendingUp className="w-6 h-6" />}
                    </div>
                    <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                            <Badge variant={trend.status === 'Volatile' ? 'warning' : 'success'}>
                                {trend.status || 'Stable'}
                            </Badge>
                            {trend.impact_resource && (
                                <Badge variant="info">{trend.impact_resource}</Badge>
                            )}
                        </div>
                        <h3 className="text-lg font-medium text-white mb-1">
                            {trend.headline || 'The market is calm.'}
                        </h3>
                        {trend.price_factor && (
                            <p className="text-sm text-slate-400">
                                Price Factor: <span className={trend.price_factor > 1 ? 'text-red-400' : 'text-emerald-400'}>
                                    {(trend.price_factor * 100 - 100).toFixed(0)}%
                                </span>
                                {' • '}
                                Demand Factor: <span className={trend.demand_factor && trend.demand_factor > 1 ? 'text-emerald-400' : 'text-red-400'}>
                                    {((trend.demand_factor || 1) * 100 - 100).toFixed(0)}%
                                </span>
                            </p>
                        )}
                    </div>
                </div>
            </Card>

            {/* Vendor Prices Grid */}
            <div>
                <h3 className="text-sm font-medium text-slate-400 mb-3">Vendor Pricing</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {Object.entries(vendorPrices).map(([vendorId, vendor]) => (
                        <Card key={vendorId} variant="glass">
                            <h4 className="font-medium text-white mb-3">{vendor.name}</h4>
                            <div className="space-y-1.5">
                                {Object.entries(vendor.prices).map(([item, price]) => (
                                    <div key={item} className="flex justify-between text-sm">
                                        <span className="text-slate-300 capitalize">{item.replace(/_/g, ' ')}</span>
                                        <span className="text-emerald-400 font-mono">${price}</span>
                                    </div>
                                ))}
                            </div>
                        </Card>
                    ))}
                </div>
            </div>

            {/* Supply Chain Events */}
            {supplyChainEvents.length > 0 && (
                <div>
                    <h3 className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
                        <Package className="w-4 h-4" />
                        Supply Chain Events
                    </h3>
                    <div className="space-y-2">
                        {supplyChainEvents.map((event, idx) => (
                            <Card key={idx} variant="outline">
                                <div className="flex items-center gap-3">
                                    <Badge variant={event.impact > 0 ? 'danger' : 'success'}>
                                        {event.event_type}
                                    </Badge>
                                    <span className="text-sm text-slate-300">{event.message || `Impact: ${event.impact}`}</span>
                                </div>
                            </Card>
                        ))}
                    </div>
                </div>
            )}

            {/* News Section Placeholder */}
            <Card variant="glass">
                <h3 className="text-sm font-medium text-slate-400 mb-3 flex items-center gap-2">
                    <Newspaper className="w-4 h-4" />
                    Latest News
                </h3>
                <p className="text-slate-500 text-sm italic">
                    {trend.headline || 'No major news at this time.'}
                </p>
            </Card>
        </div>
    );
}
