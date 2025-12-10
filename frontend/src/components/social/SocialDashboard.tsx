import {
  Heart,
  Building2,
  Leaf,
  Briefcase,
  Shield,
  Handshake,
  Trophy,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Badge, Button } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// SocialDashboard Component
// Social score breakdown, alliances, diplomacy
// ═══════════════════════════════════════════════════════════════════════

const componentIcons: Record<string, React.ReactNode> = {
  customer_satisfaction: <Heart className="w-4 h-4" />,
  community_standing: <Building2 className="w-4 h-4" />,
  ethical_conduct: <Shield className="w-4 h-4" />,
  employee_relations: <Briefcase className="w-4 h-4" />,
  environmental_responsibility: <Leaf className="w-4 h-4" />,
};

export default function SocialDashboard() {
  const { getPlayerLaundromat, getCompetitors, sendAction, isLoading } = useGameStore();
  const laundromat = getPlayerLaundromat();
  const competitors = getCompetitors();

  if (!laundromat) {
    return (
      <Card variant="glass" className="text-center py-12">
        <p className="text-slate-400">No social data available.</p>
      </Card>
    );
  }

  // Extract social score with proper defaults
  const socialScore =
    typeof laundromat.social_score === 'number'
      ? { total_score: laundromat.social_score, components: {}, tier_info: { tier_name: 'Unknown', badge: '🤷', benefits: [] as string[], penalties: [] as string[] } }
      : laundromat.social_score;

  const handleProposeAlliance = (competitorId: string) => {
    sendAction('PROPOSE_ALLIANCE', { target_id: competitorId });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Header with Tier */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="text-4xl">{socialScore?.tier_info?.badge ?? '🏆'}</div>
          <div>
            <h2 className="text-xl font-semibold text-white">Social Standing</h2>
            <p className="text-sm text-slate-400">
              {socialScore?.tier_info?.tier_name ?? 'Community Member'}
            </p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-3xl font-bold text-emerald-400">
            {socialScore?.total_score?.toFixed(1) ?? '—'}
          </p>
          <p className="text-xs text-slate-400">Social Score</p>
        </div>
      </div>

      {/* Score Components */}
      <Card variant="glass">
        <h3 className="text-lg font-semibold text-white mb-4">Score Breakdown</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {socialScore?.components &&
            Object.entries(socialScore.components).map(([key, value]) => (
              <div
                key={key}
                className="flex items-center gap-3 p-3 rounded-lg bg-white/5"
              >
                <div className="p-2 rounded-lg bg-emerald-500/20 text-emerald-400">
                  {componentIcons[key] ?? <Trophy className="w-4 h-4" />}
                </div>
                <div className="flex-1">
                  <p className="text-xs text-slate-400 capitalize">
                    {key.replace(/_/g, ' ')}
                  </p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-emerald-500"
                        style={{ width: `${Math.min(value * 10, 100)}%` }}
                      />
                    </div>
                    <span className="text-sm font-medium text-white">
                      {(value as number).toFixed(1)}
                    </span>
                  </div>
                </div>
              </div>
            ))}
        </div>
      </Card>

      {/* Tier Benefits/Penalties */}
      {socialScore?.tier_info && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {'benefits' in socialScore.tier_info && socialScore.tier_info.benefits && socialScore.tier_info.benefits.length > 0 && (
            <Card variant="glow">
              <h3 className="text-sm font-medium text-emerald-400 mb-3">Benefits</h3>
              <ul className="space-y-2">
                {socialScore.tier_info.benefits.map((benefit: string, idx: number) => (
                  <li key={idx} className="text-sm text-slate-300 flex items-center gap-2">
                    <span className="text-emerald-400">✓</span>
                    {benefit}
                  </li>
                ))}
              </ul>
            </Card>
          )}
          {'penalties' in socialScore.tier_info && socialScore.tier_info.penalties && socialScore.tier_info.penalties.length > 0 && (
            <Card variant="outline" className="border-red-500/30">
              <h3 className="text-sm font-medium text-red-400 mb-3">Penalties</h3>
              <ul className="space-y-2">
                {socialScore.tier_info.penalties.map((penalty: string, idx: number) => (
                  <li key={idx} className="text-sm text-slate-300 flex items-center gap-2">
                    <span className="text-red-400">✗</span>
                    {penalty}
                  </li>
                ))}
              </ul>
            </Card>
          )}
        </div>
      )}

      {/* Alliances / Diplomacy */}
      <Card variant="glass">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-white flex items-center gap-2">
            <Handshake className="w-5 h-5 text-blue-400" />
            Diplomacy
          </h3>
        </div>
        <div className="space-y-3">
          {competitors.length > 0 ? (
            competitors.map((competitor) => (
              <div
                key={competitor.id}
                className="flex items-center justify-between p-3 rounded-lg bg-white/5"
              >
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-slate-700 flex items-center justify-center text-lg">
                    🏪
                  </div>
                  <div>
                    <p className="text-white font-medium">{competitor.name}</p>
                    <p className="text-xs text-slate-400">
                      Rep: {competitor.reputation}% | Score:{' '}
                      {typeof competitor.social_score === 'number'
                        ? competitor.social_score.toFixed(1)
                        : (competitor.social_score?.total_score ?? 0).toFixed(1)}
                    </p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Badge variant="default">Neutral</Badge>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => handleProposeAlliance(competitor.id)}
                    loading={isLoading}
                  >
                    <Handshake className="w-4 h-4" />
                    Propose
                  </Button>
                </div>
              </div>
            ))
          ) : (
            <p className="text-slate-500 text-center py-4">No competitors available.</p>
          )}
        </div>
      </Card>
    </div>
  );
}
