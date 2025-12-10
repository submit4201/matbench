import {
    Trophy,
    TrendingUp,
    DollarSign,
    Users,
    Heart,
    Brain,
    Zap,
    Medal,
    Crown,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Badge } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// Scoreboard Component
// Multi-category ranking display per World Bible 4.0
// ═══════════════════════════════════════════════════════════════════════

const SCORE_CATEGORIES = [
    { id: 'business', label: 'Business', icon: DollarSign, weight: 30, color: 'emerald' },
    { id: 'social', label: 'Social', icon: Users, weight: 25, color: 'blue' },
    { id: 'ethics', label: 'Ethics', icon: Heart, weight: 20, color: 'pink' },
    { id: 'strategy', label: 'Strategy', icon: Brain, weight: 15, color: 'purple' },
    { id: 'adaptive', label: 'Adaptive', icon: Zap, weight: 10, color: 'amber' },
];

export default function Scoreboard() {
    const { gameState, getPlayerLaundromat, getCompetitors } = useGameStore();
    const player = getPlayerLaundromat();
    const competitors = getCompetitors();

    // Generate placeholder scores for all participants
    const participants = [
        { id: 'p1', name: player?.name ?? 'Your Laundromat', isPlayer: true, scores: { business: 75, social: 68, ethics: 82, strategy: 60, adaptive: 70 } },
        ...competitors.map((c, i) => ({
            id: c.id,
            name: c.name,
            isPlayer: false,
            scores: {
                business: Math.floor(50 + Math.random() * 40),
                social: Math.floor(50 + Math.random() * 40),
                ethics: Math.floor(50 + Math.random() * 40),
                strategy: Math.floor(50 + Math.random() * 40),
                adaptive: Math.floor(50 + Math.random() * 40),
            },
        })),
    ];

    // Calculate total weighted score
    const calculateTotal = (scores: Record<string, number>) => {
        return SCORE_CATEGORIES.reduce((total, cat) => {
            return total + (scores[cat.id] ?? 0) * (cat.weight / 100);
        }, 0);
    };

    // Sort by total score
    const rankedParticipants = [...participants].sort(
        (a, b) => calculateTotal(b.scores) - calculateTotal(a.scores)
    );

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Trophy className="w-6 h-6 text-yellow-400" />
                    Scoreboard
                </h2>
                <Badge variant="info">
                    Week {gameState?.week ?? 1} Rankings
                </Badge>
            </div>

            {/* Category Legend */}
            <div className="flex flex-wrap gap-2">
                {SCORE_CATEGORIES.map((cat) => {
                    const Icon = cat.icon;
                    return (
                        <Badge key={cat.id} variant="default" className={`bg-${cat.color}-500/20 text-${cat.color}-400`}>
                            <Icon className="w-3 h-3 mr-1" />
                            {cat.label} ({cat.weight}%)
                        </Badge>
                    );
                })}
            </div>

            {/* Rankings Table */}
            <Card variant="glass">
                <div className="space-y-3">
                    {rankedParticipants.map((p, index) => {
                        const total = calculateTotal(p.scores);
                        const rankIcon = index === 0 ? <Crown className="w-5 h-5 text-yellow-400" /> :
                            index === 1 ? <Medal className="w-5 h-5 text-slate-300" /> :
                                index === 2 ? <Medal className="w-5 h-5 text-amber-600" /> :
                                    <span className="w-5 text-center text-slate-500 font-medium">{index + 1}</span>;

                        return (
                            <div
                                key={p.id}
                                className={`flex items-center justify-between p-4 rounded-lg transition-colors ${p.isPlayer
                                        ? 'bg-emerald-500/10 border border-emerald-500/30'
                                        : 'bg-white/5 hover:bg-white/10'
                                    }`}
                            >
                                <div className="flex items-center gap-4">
                                    <div className="w-8 flex justify-center">{rankIcon}</div>
                                    <div>
                                        <p className={`font-medium ${p.isPlayer ? 'text-emerald-400' : 'text-white'}`}>
                                            {p.name}
                                            {p.isPlayer && <span className="text-xs ml-2 text-emerald-300">(You)</span>}
                                        </p>
                                        <div className="flex gap-2 mt-1">
                                            {SCORE_CATEGORIES.map((cat) => (
                                                <span key={cat.id} className={`text-xs text-${cat.color}-400`}>
                                                    {p.scores[cat.id]}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-2xl font-bold text-white">{total.toFixed(0)}</p>
                                    <p className="text-xs text-slate-400">Total Score</p>
                                </div>
                            </div>
                        );
                    })}
                </div>
            </Card>
        </div>
    );
}
