import { Calendar, Sun, Cloud, Snowflake, Leaf, DollarSign } from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';

// ═══════════════════════════════════════════════════════════════════════
// GameClock Component
// Week/Day display with season indicator, calendar button, and balance
// ═══════════════════════════════════════════════════════════════════════

const seasonIcons: Record<string, React.ReactNode> = {
  spring: <Leaf className="w-4 h-4 text-green-400" />,
  summer: <Sun className="w-4 h-4 text-amber-400" />,
  fall: <Cloud className="w-4 h-4 text-orange-400" />,
  autumn: <Cloud className="w-4 h-4 text-orange-400" />,
  winter: <Snowflake className="w-4 h-4 text-blue-400" />,
};

const seasonColors: Record<string, string> = {
  spring: 'from-green-500/20 to-emerald-500/20 border-green-500/30',
  summer: 'from-amber-500/20 to-yellow-500/20 border-amber-500/30',
  fall: 'from-orange-500/20 to-red-500/20 border-orange-500/30',
  autumn: 'from-orange-500/20 to-red-500/20 border-orange-500/30',
  winter: 'from-blue-500/20 to-cyan-500/20 border-blue-500/30',
};

export default function GameClock() {
  const { gameState, getPlayerLaundromat, setActiveTab } = useGameStore();
  const laundromat = getPlayerLaundromat();

  if (!gameState) return null;

  const { week, season } = gameState;
  const seasonLower = season?.toLowerCase() ?? 'spring';
  const icon = seasonIcons[seasonLower] ?? <Calendar className="w-4 h-4 text-slate-400" />;
  const colorClass = seasonColors[seasonLower] ?? 'from-slate-500/20 to-slate-600/20 border-slate-500/30';

  const balance = laundromat?.balance ?? 0;

  return (
    <div className="flex items-center gap-3">
      {/* Money on Hand */}
      <div className="flex items-center gap-2 px-3 py-2 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
        <DollarSign className="w-4 h-4 text-emerald-400" />
        <span className="text-sm font-bold text-emerald-400">
          ${balance.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
        </span>
      </div>

      {/* Date/Season Display */}
      <div
        className={`inline-flex items-center gap-3 px-4 py-2 rounded-xl bg-gradient-to-r ${colorClass} border backdrop-blur-sm`}
      >
        <div className="flex items-center gap-2">
          <Calendar className="w-4 h-4 text-slate-400" />
          <span className="text-sm font-medium text-white">Week {week}</span>
          <span className="text-xs text-slate-400">|</span>
          <span className="text-sm font-medium text-emerald-400">{gameState.day ?? 'Monday'}</span>
        </div>
        <div className="w-px h-4 bg-white/20" />
        <div className="flex items-center gap-1.5">
          {icon}
          <span className="text-sm text-slate-300 capitalize">{season || 'Spring'}</span>
        </div>
      </div>

      {/* Calendar Button */}
      <button
        onClick={() => setActiveTab('calendar')}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-slate-700/50 hover:bg-slate-600/50 border border-slate-600 transition-colors"
        title="View Calendar / History"
      >
        <Calendar className="w-4 h-4 text-slate-300" />
        <span className="text-sm text-slate-300 hidden sm:inline">Calendar</span>
      </button>
    </div>
  );
}
