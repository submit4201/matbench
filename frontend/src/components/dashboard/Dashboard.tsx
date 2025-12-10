import React from 'react';
import { DollarSign, Users, Star, TrendingUp, AlertCircle } from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, StatCard } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// Dashboard Component
// Main overview with key metrics and mini calendar
// ═══════════════════════════════════════════════════════════════════════

export default function Dashboard() {
  const isLoading = useGameStore((state) => state.isLoading);
  const error = useGameStore((state) => state.error);
  const gameState = useGameStore((state) => state.gameState);
  const playerId = useGameStore((state) => state.playerId);

  // Reactive selector for the player's laundromat
  const laundromat = useGameStore((state) =>
    state.gameState?.laundromats?.[state.playerId] ?? null
  );

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

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header with Clock */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">{laundromat.name}</h1>
          <p className="text-slate-400 text-sm">Business Dashboard</p>
        </div>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Balance"
          value={formattedBalance}
          icon={<DollarSign className="w-5 h-5" />}
          trend={laundromat.balance > 10000 ? { value: 5.2, isPositive: true } : undefined}
        />
        <StatCard
          label="Customers"
          value={laundromat.active_customers ?? '—'}
          icon={<Users className="w-5 h-5" />}
        />
        <StatCard
          label="Reputation"
          value={`${laundromat.reputation}%`}
          icon={<Star className="w-5 h-5" />}
        />
        <StatCard
          label="Social Score"
          value={socialScore.toFixed(1)}
          icon={<TrendingUp className="w-5 h-5" />}
        />
      </div>

      {/* Quick Info Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Machine Summary */}
        <Card variant="glass">
          <h3 className="text-sm font-medium text-slate-400 mb-3">Machines</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">
              {laundromat.machines - laundromat.broken_machines}
            </span>
            <span className="text-slate-500">/ {laundromat.machines} operational</span>
          </div>
          {laundromat.broken_machines > 0 && (
            <p className="text-xs text-amber-400 mt-2">
              ⚠ {laundromat.broken_machines} machine(s) need repair
            </p>
          )}
        </Card>

        {/* Pricing */}
        <Card variant="glass">
          <h3 className="text-sm font-medium text-slate-400 mb-3">Current Price</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-emerald-400">
              ${laundromat.price.toFixed(2)}
            </span>
            <span className="text-slate-500">per load</span>
          </div>
        </Card>

        {/* Open Tickets */}
        <Card variant="glass">
          <h3 className="text-sm font-medium text-slate-400 mb-3">Open Tickets</h3>
          <div className="flex items-baseline gap-2">
            <span className="text-2xl font-bold text-white">
              {laundromat.tickets?.filter((t) => t.status === 'open').length ?? 0}
            </span>
            <span className="text-slate-500">to resolve</span>
          </div>
        </Card>
      </div>

      {/* Events Feed */}
      {gameState?.events && gameState.events.length > 0 && (
        <Card variant="outline">
          <h3 className="text-sm font-medium text-slate-400 mb-3">Recent Events</h3>
          <ul className="space-y-2 max-h-40 overflow-y-auto custom-scrollbar">
            {gameState.events.slice(-5).map((event, idx) => (
              <li key={idx} className="text-sm text-slate-300 pl-3 border-l-2 border-slate-700">
                {event}
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  );
}
