import { useEffect, useState } from 'react';
import { DollarSign, Users, Star, TrendingUp, AlertCircle, Package, TrendingDown } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';
import { useGameStore } from '../../stores/gameStore';
import { Card, StatCard } from '../shared';

const API_BASE = 'http://localhost:8000';

// Inventory items config with vibrant chart colors
const INVENTORY_ITEMS = [
  { key: 'detergent', label: 'Detergent', color: '#0ea5e9', icon: '🧴' }, // Sky Blue
  { key: 'softener', label: 'Softener', color: '#d946ef', icon: '🌸' }, // Fuchsia
  { key: 'snacks', label: 'Snacks', color: '#eab308', icon: '🍫' }, // Yellow
  { key: 'parts', label: 'Parts', color: '#f97316', icon: '🔧' }, // Orange
  { key: 'cleaning_supplies', label: 'Cleaning', color: '#84cc16', icon: '🧹' }, // Lime
];

export default function Dashboard() {
  const isLoading = useGameStore((state) => state.isLoading);
  const error = useGameStore((state) => state.error);
  const gameState = useGameStore((state) => state.gameState);
  const playerId = useGameStore((state) => state.playerId);
  const [history, setHistory] = useState<any[]>([]);

  // Reactive selector for the player's laundromat
  const laundromat = useGameStore((state) =>
    state.gameState?.laundromats?.[state.playerId] ?? null
  );

  // Fetch history for trend chart
  useEffect(() => {
    if (playerId) {
      fetch(`${API_BASE}/history/${playerId}`)
        .then(res => res.json())
        .then(data => {
          // Process data for chart
          const chartData = data.map((record: any) => ({
            week: `Wk ${record.week}`,
            ...record.inventory_after
          }));
          setHistory(chartData);
        })
        .catch(err => console.error("Failed to fetch history", err));
    }
  }, [playerId, gameState?.week]);

  if (isLoading && !gameState) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="w-8 h-8 border-2 border-emerald-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <Card variant="outline" className="border-red-500/30 bg-red-500/10">
        <div className="flex items-center gap-3 text-red-400">
          <AlertCircle className="w-5 h-5" />
          <span>Error loading game state: {error}</span>
        </div>
      </Card>
    );
  }

  if (!laundromat) {
    return (
      <Card variant="glass" className="text-center py-12">
        <p className="text-slate-400">No game in progress. Start a scenario to begin.</p>
      </Card>
    );
  }

  // Extract social score
  const socialScore =
    typeof laundromat.social_score === 'number'
      ? laundromat.social_score
      : laundromat.social_score?.total_score ?? 0;

  // Format balance
  const formattedBalance = new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(laundromat.balance);

  // Build inventory data
  const inventoryData = INVENTORY_ITEMS.map((item) => ({
    ...item,
    value: laundromat.inventory?.[item.key] || 0,
    low: (laundromat.inventory?.[item.key] || 0) < 20,
  }));

  const maxInventory = Math.max(...inventoryData.map((i) => i.value), 100);

  return (
    <div className="space-y-4 animate-fade-in">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-xl font-bold text-white">{laundromat.name}</h1>
          <p className="text-slate-400 text-xs">Business Dashboard</p>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
        <StatCard
          label="Balance"
          value={formattedBalance}
          icon={<DollarSign className="w-4 h-4" />}
          trend={laundromat.balance > 10000 ? { value: 5.2, isPositive: true } : undefined}
        />
        <StatCard
          label="Customers"
          value={laundromat.active_customers ?? '—'}
          icon={<Users className="w-4 h-4" />}
        />
        <StatCard
          label="Reputation"
          value={`${laundromat.reputation}%`}
          icon={<Star className="w-4 h-4" />}
        />
        <StatCard
          label="Social Score"
          value={socialScore.toFixed(1)}
          icon={<TrendingUp className="w-4 h-4" />}
        />
      </div>

      {/* Quick Info + Inventory */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
        {/* Left Column: Quick Stats */}
        <div className="space-y-3">
          {/* Machine Summary */}
          <Card variant="glass" className="p-3">
            <h3 className="text-xs font-medium text-slate-400 mb-2">Machines</h3>
            <div className="flex items-baseline gap-2">
              <span className="text-xl font-bold text-white">
                {(Array.isArray(laundromat.machines) ? laundromat.machines.length : laundromat.machines) - laundromat.broken_machines}
              </span>
              <span className="text-slate-500 text-sm">/ {Array.isArray(laundromat.machines) ? laundromat.machines.length : laundromat.machines} operational</span>
            </div>
            {laundromat.broken_machines > 0 && (
              <p className="text-[10px] text-amber-400 mt-1">⚠ {laundromat.broken_machines} need repair</p>
            )}
          </Card>

          {/* Pricing + Tickets Row */}
          <div className="grid grid-cols-2 gap-3">
            <Card variant="glass" className="p-3">
              <h3 className="text-xs font-medium text-slate-400 mb-2">Price</h3>
              <div className="flex items-baseline gap-1">
                <span className="text-xl font-bold text-emerald-400">${laundromat.price.toFixed(2)}</span>
                <span className="text-slate-500 text-xs">/load</span>
              </div>
            </Card>
            <Card variant="glass" className="p-3">
              <h3 className="text-xs font-medium text-slate-400 mb-2">Tickets</h3>
              <div className="flex items-baseline gap-1">
                <span className="text-xl font-bold text-white">
                  {laundromat.tickets?.filter((t) => t.status === 'open').length ?? 0}
                </span>
                <span className="text-slate-500 text-xs">open</span>
              </div>
            </Card>
          </div>
        </div>

        {/* Right Column: Inventory Bar Chart */}
        <Card variant="glass" className="p-3">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-xs font-medium text-slate-400 flex items-center gap-1">
              <Package className="w-3.5 h-3.5" /> Inventory Levels
            </h3>
            <span className="text-[10px] text-slate-500">Current stock</span>
          </div>

          <div className="space-y-2">
            {inventoryData.map((item) => (
              <div key={item.key} className="flex items-center gap-2">
                <span className="text-sm w-5">{item.icon}</span>
                <span className="text-[10px] text-slate-400 w-16 truncate">{item.label}</span>
                <div className="flex-1 h-4 bg-white/5 rounded-full overflow-hidden relative">
                  <div
                    className="h-full rounded-full transition-all duration-500"
                    style={{
                      width: `${Math.min((item.value / maxInventory) * 100, 100)}%`,
                      backgroundColor: item.low ? '#ef4444' : item.color,
                    }}
                  />
                  {item.low && (
                    <TrendingDown className="absolute right-1 top-0.5 w-3 h-3 text-red-400 animate-pulse" />
                  )}
                </div>
                <span className={`text-xs font-mono w-8 text-right ${item.low ? 'text-red-400' : 'text-slate-300'}`}>
                  {item.value}
                </span>
              </div>
            ))}
          </div>

          {inventoryData.some((i) => i.low) && (
            <p className="text-[10px] text-red-400 mt-2 flex items-center gap-1">
              <AlertCircle className="w-3 h-3" /> Low stock - visit Vendors to reorder
            </p>
          )}
        </Card>
      </div>

      {/* Historical Inventory Trend */}
      <Card variant="glass" className="p-4">
        <h3 className="text-sm font-bold text-slate-300 mb-4 flex items-center gap-2">
          <TrendingUp className="w-4 h-4 text-emerald-400" />
          Inventory Trends
        </h3>
        <div className="h-80 w-full bg-slate-900/50 rounded-lg p-2 border border-slate-700/50">
          {history.length > 0 ? (
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={history} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#475569" vertical={true} horizontal={true} />
                <XAxis
                  dataKey="week"
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: '#64748b' }}
                  tick={{ dy: 10 }}
                />
                <YAxis
                  stroke="#94a3b8"
                  fontSize={11}
                  tickLine={false}
                  axisLine={{ stroke: '#64748b' }}
                  tick={{ dx: -10 }}
                />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', color: '#f8fafc' }}
                  itemStyle={{ fontSize: '12px', fontWeight: 600 }}
                />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '15px' }} iconType="circle" />
                {INVENTORY_ITEMS.map(item => (
                  <Line
                    key={item.key}
                    type="monotone"
                    dataKey={item.key}
                    name={item.label}
                    stroke={item.color}
                    strokeWidth={3}
                    dot={{ r: 4, strokeWidth: 2, fill: '#0f172a', stroke: item.color }}
                    activeDot={{ r: 6, strokeWidth: 0, fill: item.color }}
                    isAnimationActive={true}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="h-full flex flex-col items-center justify-center text-slate-500">
              <TrendingUp className="w-8 h-8 mb-2 opacity-50" />
              <p className="text-xs">No historical data yet. Play a turn to see trends.</p>
            </div>
          )}
        </div>
      </Card>

      {/* Events Feed */}
      {gameState?.events && gameState.events.length > 0 && (
        <Card variant="outline" className="p-3">
          <h3 className="text-xs font-medium text-slate-400 mb-2">Recent Events</h3>
          <ul className="space-y-1 max-h-24 overflow-y-auto custom-scrollbar">
            {gameState.events.slice(-5).map((event: string, idx: number) => (
              <li key={idx} className="text-xs text-slate-300 pl-2 border-l-2 border-slate-700">
                {event}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
