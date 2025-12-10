import { useState } from 'react';
import {
    Map,
    Building,
    Users,
    TrendingUp,
    DollarSign,
    Layers,
    AlertCircle,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Badge, Button } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// NeighborhoodView Component
// Displays zone information, demographics, and foot traffic
// ═══════════════════════════════════════════════════════════════════════

// Zone tier configuration (per World Bible 2.0)
const ZONE_DATA = [
    { id: 'A', name: 'Downtown Core', rent: 2000, traffic: 'Very High', demo: 'Young Professionals', color: 'emerald' },
    { id: 'B', name: 'Commercial Strip', rent: 1500, traffic: 'High', demo: 'Mixed', color: 'blue' },
    { id: 'C', name: 'Residential', rent: 1000, traffic: 'Medium', demo: 'Families', color: 'amber' },
    { id: 'D', name: 'College Area', rent: 800, traffic: 'Medium-High', demo: 'Students', color: 'purple' },
    { id: 'E', name: 'Industrial Fringe', rent: 500, traffic: 'Low', demo: 'Workers', color: 'slate' },
];

export default function NeighborhoodView() {
    const { gameState, getPlayerLaundromat, getCompetitors } = useGameStore();
    const player = getPlayerLaundromat();
    const competitors = getCompetitors();
    const [selectedZone, setSelectedZone] = useState<string | null>(null);

    return (
        <div className="space-y-6 animate-fade-in">
            <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white flex items-center gap-2">
                    <Map className="w-6 h-6 text-blue-400" />
                    Neighborhood Map
                </h2>
                <Badge variant="info">
                    Week {gameState?.week ?? 1}
                </Badge>
            </div>

            {/* Zone Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {ZONE_DATA.map((zone) => {
                    const competitorsInZone = competitors.filter(() => Math.random() > 0.6); // Placeholder logic
                    const isPlayerZone = player && player.name.includes('Main'); // Placeholder

                    return (
                        <Card
                            key={zone.id}
                            variant={selectedZone === zone.id ? 'glow' : 'glass'}
                            hover
                            onClick={() => setSelectedZone(selectedZone === zone.id ? null : zone.id)}
                            className={`cursor-pointer border-l-4 border-${zone.color}-500`}
                        >
                            <div className="flex items-start justify-between mb-3">
                                <div>
                                    <h3 className="font-semibold text-white">{zone.name}</h3>
                                    <p className="text-xs text-slate-400">Zone {zone.id}</p>
                                </div>
                                {isPlayerZone && <Badge variant="success">Your Zone</Badge>}
                            </div>

                            <div className="grid grid-cols-2 gap-3 text-sm">
                                <div className="flex items-center gap-2 text-slate-300">
                                    <DollarSign className="w-4 h-4 text-amber-400" />
                                    <span>${zone.rent}/mo</span>
                                </div>
                                <div className="flex items-center gap-2 text-slate-300">
                                    <TrendingUp className="w-4 h-4 text-green-400" />
                                    <span>{zone.traffic}</span>
                                </div>
                                <div className="flex items-center gap-2 text-slate-300">
                                    <Users className="w-4 h-4 text-blue-400" />
                                    <span>{zone.demo}</span>
                                </div>
                                <div className="flex items-center gap-2 text-slate-300">
                                    <Building className="w-4 h-4 text-purple-400" />
                                    <span>{competitorsInZone.length} Rivals</span>
                                </div>
                            </div>

                            {selectedZone === zone.id && (
                                <div className="mt-4 pt-4 border-t border-white/10 animate-fade-in">
                                    <p className="text-sm text-slate-400 mb-3">
                                        {zone.demo} customers prefer this zone. Foot traffic peaks on weekends.
                                    </p>
                                    <Button variant="secondary" size="sm" className="w-full">
                                        <Layers className="w-4 h-4 mr-2" />
                                        View Demographics
                                    </Button>
                                </div>
                            )}
                        </Card>
                    );
                })}
            </div>

            {/* Tip Box */}
            <Card variant="outline" className="bg-blue-500/5 border-blue-500/20">
                <div className="flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-blue-400 flex-shrink-0 mt-0.5" />
                    <div>
                        <p className="text-sm text-blue-300">
                            <strong>Tip:</strong> Higher rent zones attract more premium customers but cost more.
                            Balance your expansion strategy with your cash flow.
                        </p>
                    </div>
                </div>
            </Card>
        </div>
    );
}
