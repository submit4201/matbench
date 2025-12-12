import { useState } from 'react';
import { MessageSquare, User } from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Badge } from '../shared';

export default function CustomerChatter() {
    const gameState = useGameStore((state) => state.gameState);
    const playerId = useGameStore((state) => state.playerId);
    const [filter, setFilter] = useState<'all' | 'mine' | 'competitors'>('mine');

    if (!gameState?.customer_thoughts || gameState.customer_thoughts.length === 0) {
        return (
            <Card variant="glass" className="h-full">
                <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-blue-400" />
                    Customer Chatter
                </h3>
                <p className="text-slate-400 text-sm text-center py-8">
                    The streets are quiet...
                </p>
            </Card>
        );
    }

    const thoughts = gameState.customer_thoughts.filter((t) => {
        if (filter === 'all') return true;
        if (filter === 'mine') return t.laundromat_id === playerId;
        if (filter === 'competitors') return t.laundromat_id !== playerId && t.laundromat_id !== 'unknown';
        return true;
    });

    return (
        <Card variant="glass" className="h-[400px] flex flex-col">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <MessageSquare className="w-5 h-5 text-blue-400" />
                    Customer Chatter
                </h3>

                <div className="flex bg-slate-800/50 rounded-lg p-1">
                    <button
                        onClick={() => setFilter('mine')}
                        className={`px-3 py-1 text-xs rounded-md transition-colors ${filter === 'mine' ? 'bg-blue-500/20 text-blue-400' : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        My Place
                    </button>
                    <button
                        onClick={() => setFilter('competitors')}
                        className={`px-3 py-1 text-xs rounded-md transition-colors ${filter === 'competitors' ? 'bg-amber-500/20 text-amber-400' : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        Competitors
                    </button>
                    <button
                        onClick={() => setFilter('all')}
                        className={`px-3 py-1 text-xs rounded-md transition-colors ${filter === 'all' ? 'bg-slate-500/20 text-slate-300' : 'text-slate-400 hover:text-white'
                            }`}
                    >
                        All
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto space-y-3 custom-scrollbar pr-2">
                {thoughts.length > 0 ? (
                    thoughts.map((thought, idx) => (
                        <div key={idx} className="flex gap-3 text-sm p-3 rounded-lg bg-white/5 border border-white/5">
                            <div className="flex-shrink-0 mt-0.5">
                                <div className="w-8 h-8 rounded-full bg-slate-700 flex items-center justify-center">
                                    <User className="w-4 h-4 text-slate-400" />
                                </div>
                            </div>
                            <div className="flex-1">
                                <div className="flex justify-between items-start mb-1">
                                    <span className="text-xs text-slate-500">Customer</span>
                                    {thought.laundromat_id !== 'unknown' && (
                                        <Badge variant={thought.laundromat_id === playerId ? 'default' : 'info'} className="text-[10px] py-0">
                                            {thought.laundromat_id === playerId ? 'You' : `Comp ${thought.laundromat_id}`}
                                        </Badge>
                                    )}
                                </div>
                                <p className="text-slate-300 italic">"{thought.text}"</p>
                            </div>
                        </div>
                    ))
                ) : (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500">
                        <p>No chatter about {filter === 'mine' ? 'you' : 'competitors'} right now.</p>
                    </div>
                )}
            </div>
        </Card>
    );
}
