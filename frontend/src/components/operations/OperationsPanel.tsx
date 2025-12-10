import { useState } from 'react';
import {
  Wrench,
  Megaphone,
  DollarSign,
  Users,
  Zap,
  Package,
  Gauge,
  Trash2,
  GraduationCap,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, Button, Badge, TabGroup, TabContent } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// OperationsPanel Component
// Pricing, marketing, machines, staff, services
// ═══════════════════════════════════════════════════════════════════════

const tabs = [
  { id: 'pricing', label: 'Pricing', icon: <DollarSign className="w-4 h-4" /> },
  { id: 'marketing', label: 'Marketing', icon: <Megaphone className="w-4 h-4" /> },
  { id: 'machines', label: 'Machines', icon: <Wrench className="w-4 h-4" /> },
  { id: 'staff', label: 'Staff', icon: <Users className="w-4 h-4" /> },
  { id: 'services', label: 'Services', icon: <Zap className="w-4 h-4" /> },
  { id: 'supplies', label: 'Supplies', icon: <Package className="w-4 h-4" /> },
];

export default function OperationsPanel() {
  const { getPlayerLaundromat, sendAction, isLoading, getCompetitors } = useGameStore();
  const laundromat = getPlayerLaundromat();
  const competitors = getCompetitors();

  // Local state for sliders
  const [newPrice, setNewPrice] = useState(laundromat?.price ?? 3.0);

  if (!laundromat) {
    return (
      <Card variant="glass" className="text-center py-12">
        <p className="text-slate-400">No operations data available.</p>
      </Card>
    );
  }

  const handleSetPrice = () => {
    sendAction('SET_PRICE', { new_price: newPrice });
  };

  const handleLaunchCampaign = (campaignType: string, cost: number) => {
    sendAction('MARKETING_CAMPAIGN', { campaign_type: campaignType, cost: cost });
  };

  const handleRepairMachines = () => {
    sendAction('REPAIR_MACHINES', {});
  };

  const handleHireStaff = () => {
    sendAction('HIRE_STAFF', { cost: 100, role: 'Attendant' });
  };

  // Average competitor price
  const avgCompetitorPrice =
    competitors.length > 0
      ? competitors.reduce((sum, c) => sum + c.price, 0) / competitors.length
      : 3.0;

  return (
    <div className="space-y-6 animate-fade-in">
      <TabGroup tabs={tabs} defaultValue="pricing">
        {/* Pricing Tab */}
        <TabContent value="pricing">
          <Card variant="glass">
            <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
              <DollarSign className="w-5 h-5 text-emerald-400" />
              Pricing Strategy
            </h3>
            <div className="space-y-6">
              <div>
                <div className="flex justify-between mb-2">
                  <span className="text-slate-400">Your Price</span>
                  <span className="text-2xl font-bold text-emerald-400">${newPrice.toFixed(2)}</span>
                </div>
                <input
                  type="range"
                  min="1.00"
                  max="10.00"
                  step="0.25"
                  value={newPrice}
                  onChange={(e) => setNewPrice(parseFloat(e.target.value))}
                  className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
                />
                <div className="flex justify-between text-xs text-slate-500 mt-1">
                  <span>$1.00</span>
                  <span>$10.00</span>
                </div>
              </div>

              <div className="flex items-center justify-between p-3 rounded-lg bg-white/5">
                <span className="text-slate-400">Competitor Average</span>
                <span className="text-white font-medium">${avgCompetitorPrice.toFixed(2)}</span>
              </div>

              <Button
                variant="primary"
                onClick={handleSetPrice}
                loading={isLoading}
                disabled={newPrice === laundromat.price}
                className="w-full"
              >
                Update Price
              </Button>
            </div>
          </Card>
        </TabContent>

        {/* Marketing Tab */}
        <TabContent value="marketing">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {[
              { type: 'flyers', name: 'Flyer Campaign', cost: 100, desc: 'Local neighborhood reach' },
              { type: 'social', name: 'Social Media', cost: 200, desc: 'Online presence boost' },
              { type: 'radio', name: 'Radio Ads', cost: 500, desc: 'Wide audience coverage' },
              { type: 'tv', name: 'TV Commercial', cost: 1000, desc: 'Maximum exposure' },
            ].map((campaign) => (
              <Card key={campaign.type} variant="outline" hover>
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <h4 className="font-medium text-white">{campaign.name}</h4>
                    <p className="text-xs text-slate-400">{campaign.desc}</p>
                  </div>
                  <Badge variant="info">${campaign.cost}</Badge>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleLaunchCampaign(campaign.type, campaign.cost)}
                  loading={isLoading}
                  className="w-full"
                >
                  Launch
                </Button>
              </Card>
            ))}
          </div>
          <div className="mt-4 p-4 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex justify-between items-center">
            <div>
              <p className="text-white font-medium">Current Marketing Impact</p>
              <p className="text-xs text-slate-400">Boosts customer acquisition rate</p>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-indigo-400">+{((laundromat.marketing_boost || 0) * 10).toFixed(0)}%</p>
              <p className="text-xs text-indigo-300">Traffic Multiplier</p>
            </div>
          </div>
        </TabContent>

        {/* Machines Tab */}
        <TabContent value="machines">
          <Card variant="glass">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-white">Machine Status</h3>
              <Badge
                variant={laundromat.broken_machines > 0 ? 'warning' : 'success'}
                dot
              >
                {laundromat.broken_machines > 0
                  ? `${laundromat.broken_machines} Needs Repair`
                  : 'All Operational'}
              </Badge>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-4 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-center">
                <div className="text-3xl font-bold text-emerald-400">
                  {laundromat.machines - laundromat.broken_machines}
                </div>
                <div className="text-xs text-slate-400 uppercase">Working</div>
              </div>
              <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20 text-center">
                <div className="text-3xl font-bold text-amber-400">
                  {laundromat.broken_machines}
                </div>
                <div className="text-xs text-slate-400 uppercase">Broken</div>
              </div>
            </div>

            <div className="flex gap-3">
              <Button
                variant="secondary"
                onClick={handleRepairMachines}
                loading={isLoading}
                disabled={laundromat.broken_machines === 0}
                className="flex-1"
              >
                <Wrench className="w-4 h-4" />
                Repair All (${laundromat.broken_machines * 50})
              </Button>
              <Button variant="ghost" className="flex-1">
                <Gauge className="w-4 h-4" />
                Upgrade
              </Button>
            </div>
          </Card>
        </TabContent>

        {/* Staff Tab */}
        <TabContent value="staff">
          <Card variant="glass">
            <h3 className="text-lg font-semibold text-white mb-4">Staff Management</h3>

            {laundromat.staff && laundromat.staff.length > 0 ? (
              <div className="space-y-3">
                {laundromat.staff.map((member) => (
                  <div
                    key={member.id}
                    className="flex items-center justify-between p-3 rounded-lg bg-white/5"
                  >
                    <div>
                      <p className="text-white font-medium">{member.name}</p>
                      <p className="text-xs text-slate-400">{member.role}</p>
                    </div>
                    <div className="flex items-center gap-3">
                      <div className="text-right mr-2">
                        <p className="text-emerald-400 font-medium">${member.wage}/wk</p>
                        <p className="text-xs text-slate-400">Skill: {member.skill_level.toFixed(1)}/10</p>
                      </div>
                      <Button
                        variant="secondary"
                        size="sm"
                        onClick={() => sendAction('TRAIN_STAFF', { staff_id: member.id, cost: 150 })}
                        loading={isLoading}
                        title="Train Staff ($150)"
                      >
                        <GraduationCap className="w-4 h-4" />
                      </Button>
                      <Button
                        variant="danger"
                        size="sm"
                        onClick={() => sendAction('FIRE_STAFF', { staff_id: member.id })}
                        loading={isLoading}
                        title="Fire Staff (Pays 2wks Severance)"
                      >
                        <Trash2 className="w-4 h-4" />
                      </Button>
                    </div>
                  </div>
                ))}
                <div className="border-t border-white/10 my-4 pt-4">
                  <Button variant="primary" className="w-full" onClick={handleHireStaff} loading={isLoading}>
                    <Users className="w-4 h-4 mr-2" /> Hire General Staff (Cost: $100)
                  </Button>
                </div>
              </div>
            ) : (
              <div className="text-center py-8">
                <p className="text-slate-500 mb-4">No staff hired yet.</p>
                <Button variant="primary" onClick={handleHireStaff} loading={isLoading}>
                  Hire General Staff (Cost: $100)
                </Button>
              </div>
            )}
          </Card>
        </TabContent>

        {/* Services Tab */}
        <TabContent value="services">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {laundromat.revenue_streams ? (
              Object.entries(laundromat.revenue_streams).map(([key, stream]) => (
                <Card
                  key={key}
                  variant={stream.unlocked ? 'glow' : 'outline'}
                  className="relative"
                >
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-white">{stream.name}</h4>
                    <Badge variant={stream.unlocked ? 'success' : 'default'}>
                      {stream.unlocked ? 'Active' : 'Locked'}
                    </Badge>
                  </div>
                  <p className="text-xs text-slate-400 mb-3">{stream.description}</p>
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-slate-400">Price: ${stream.price}</span>
                    {stream.setup_cost && !stream.unlocked && (
                      <span className="text-amber-400">Setup: ${stream.setup_cost}</span>
                    )}
                  </div>
                  {!stream.unlocked && (
                    <Button
                      variant="secondary"
                      size="sm"
                      className="w-full mt-3"
                      onClick={() =>
                        sendAction('REVENUE_STREAM', { stream_name: key, action: 'activate' })
                      }
                    >
                      Activate
                    </Button>
                  )}
                </Card>
              ))
            ) : (
              <Card variant="glass" className="col-span-2 text-center py-8">
                <p className="text-slate-500">No services available.</p>
              </Card>
            )}
          </div>
        </TabContent>

        {/* Supplies Tab */}
        <TabContent value="supplies">
          <Card variant="glass">
            <h3 className="text-lg font-semibold text-white mb-4">Inventory Levels</h3>
            <div className="space-y-4">
              {Object.entries(laundromat.inventory).map(([item, quantity]) => {
                // Determine low stock threshold
                const isLow = (quantity as number) < 20;
                return (
                  <div key={item} className="space-y-2 p-3 bg-white/5 rounded-lg">
                    <div className="flex justify-between items-center">
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-slate-200 capitalize font-medium">{item.replace(/_/g, ' ')}</span>
                          {isLow && <Badge variant="warning" size="sm">Low</Badge>}
                        </div>
                        <span className="text-xs text-slate-400">{(quantity as number)} units in stock</span>
                      </div>

                      <div className="flex items-center gap-2">
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => sendAction('BUY_SUPPLIES', { item: item, quantity: 20 })}
                          loading={isLoading}
                          title={`Buy 20 ${item}`}
                        >
                          +20
                        </Button>
                        <Button
                          variant="secondary"
                          size="sm"
                          onClick={() => sendAction('BUY_SUPPLIES', { item: item, quantity: 50 })}
                          loading={isLoading}
                          title={`Buy 50 ${item}`}
                        >
                          +50
                        </Button>
                      </div>
                    </div>
                    <div className="w-full h-1.5 bg-slate-700 rounded-full overflow-hidden">
                      <div
                        className={`h-full transition-all ${(quantity as number) > 50
                          ? 'bg-emerald-500'
                          : (quantity as number) > 20
                            ? 'bg-amber-500'
                            : 'bg-red-500'
                          }`}
                        style={{ width: `${Math.min((quantity as number), 100)}%` }}
                      />
                    </div>
                  </div>
                )
              })}
            </div>
            <div className="mt-4 text-xs text-center text-slate-500">
              Supplies take 1-3 days to arrive correctly.
            </div>
          </Card>
        </TabContent>
      </TabGroup>
    </div>
  );
}
