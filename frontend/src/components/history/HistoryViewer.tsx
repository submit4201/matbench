import {
    History,
    Calendar,
    DollarSign,
    Users,
    Megaphone,
    AlertTriangle,
    ChevronRight,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Badge, TabGroup, TabContent } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// HistoryViewer Component
// Turn-by-turn history log with filtering
// ═══════════════════════════════════════════════════════════════════════

const HISTORY_TABS = [
    { id: 'all', label: 'All', icon: <History className="w-4 h-4" /> },
    { id: 'financial', label: 'Financial', icon: <DollarSign className="w-4 h-4" /> },
    { id: 'social', label: 'Social', icon: <Users className="w-4 h-4" /> },
    { id: 'events', label: 'Events', icon: <AlertTriangle className="w-4 h-4" /> },
];

export default function HistoryViewer() {
    const { gameState } = useGameStore();

    // Placeholder history data - would come from gameState.history or a dedicated endpoint
    const historyItems = [
        { week: gameState?.week ?? 1, type: 'financial', title: 'Weekly Revenue', value: '+$1,250', positive: true },
        { week: gameState?.week ?? 1, type: 'social', title: 'Customer Satisfaction', value: '+5 pts', positive: true },
        { week: (gameState?.week ?? 1) - 1, type: 'event', title: 'Supply Delay', value: 'Resolved', positive: false },
        { week: (gameState?.week ?? 1) - 1, type: 'financial', title: 'Rent Payment', value: '-$500', positive: false },
        { week: (gameState?.week ?? 1) - 2, type: 'marketing', title: 'Flyer Campaign', value: 'Launched', positive: true },
    ];

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <History className="w-6 h-6 text-purple-400" />
                    History Viewer
                </h2>
                <div className="flex items-center gap-2">
                    <Badge variant="default">
                        <Calendar className="w-3 h-3 mr-1" />
                        Week {gameState?.week ?? 1}
                    </Badge>
                </div>
            </div>

            <TabGroup tabs={HISTORY_TABS} defaultValue="all">
                <TabContent value="all">
                    <Card variant="glass">
                        <div className="space-y-3">
                            {historyItems.map((item, i) => (
                                <div
                                    key={i}
                                    className="flex items-center justify-between p-3 rounded-lg bg-white/5 hover:bg-white/10 transition-colors"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className={`p-2 rounded-lg ${item.positive ? 'bg-emerald-500/20' : 'bg-red-500/20'}`}>
                                            {item.type === 'financial' && <DollarSign className={`w-4 h-4 ${item.positive ? 'text-emerald-400' : 'text-red-400'}`} />}
                                            {item.type === 'social' && <Users className={`w-4 h-4 ${item.positive ? 'text-emerald-400' : 'text-red-400'}`} />}
                                            {item.type === 'event' && <AlertTriangle className={`w-4 h-4 ${item.positive ? 'text-emerald-400' : 'text-amber-400'}`} />}
                                            {item.type === 'marketing' && <Megaphone className={`w-4 h-4 ${item.positive ? 'text-emerald-400' : 'text-red-400'}`} />}
                                        </div>
                                        <div>
                                            <p className="text-white font-medium">{item.title}</p>
                                            <p className="text-xs text-slate-400">Week {item.week}</p>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-2">
                                        <span className={`font-medium ${item.positive ? 'text-emerald-400' : 'text-red-400'}`}>
                                            {item.value}
                                        </span>
                                        <ChevronRight className="w-4 h-4 text-slate-500" />
                                    </div>
                                </div>
                            ))}
                        </div>
                    </Card>
                </TabContent>

                <TabContent value="financial">
                    <Card variant="glass" className="text-center py-8">
                        <DollarSign className="w-12 h-12 mx-auto text-slate-500 mb-4" />
                        <p className="text-slate-400">Financial history filter coming soon.</p>
                    </Card>
                </TabContent>

                <TabContent value="social">
                    <Card variant="glass" className="text-center py-8">
                        <Users className="w-12 h-12 mx-auto text-slate-500 mb-4" />
                        <p className="text-slate-400">Social history filter coming soon.</p>
                    </Card>
                </TabContent>

                <TabContent value="events">
                    <Card variant="glass" className="text-center py-8">
                        <AlertTriangle className="w-12 h-12 mx-auto text-slate-500 mb-4" />
                        <p className="text-slate-400">Event history filter coming soon.</p>
                    </Card>
                </TabContent>
            </TabGroup>
        </div>
    );
}
