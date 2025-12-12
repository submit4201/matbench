import { useState, useEffect } from 'react';
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
  const { getPlayerLaundromat, sendAction, isLoading, getCompetitors, getVendors } = useGameStore();
  const laundromat = getPlayerLaundromat();
  const competitors = getCompetitors();
  const _vendors = getVendors(); // Keep for potential future use

  // Local state for sliders
  const [newPrice, setNewPrice] = useState(laundromat?.price ?? 3.0);

  // ! Sync local price state with Zustand store when game state updates
  useEffect(() => {
    if (laundromat?.price !== undefined) {
      setNewPrice(laundromat.price);
    }
  }, [laundromat?.price]);

  if (!laundromat) {
    return (
      <Card variant="glass" className="text-center py-12">
        <p className="text-slate-400">No operations data available.</p>
      </Card>
    );
  }

  const handleSetPrice = () => {
    sendAction('SET_PRICE', { price: newPrice });
  };

  const handleLaunchCampaign = (campaignType: string, cost: number) => {
    sendAction('MARKETING_CAMPAIGN', { campaign_type: campaignType, cost: cost });
  };

  const handleRepairMachines = () => {
    sendAction('PERFORM_MAINTENANCE', {});
  };

  const handleEmergencyRepair = () => {
    sendAction('EMERGENCY_REPAIR', {});
  };

  const handleHireStaff = () => {
    sendAction('HIRE_STAFF', { cost: 100, role: 'Attendant' });
  };

  const handleUpgradeMachine = () => {
    sendAction('UPGRADE_MACHINE', {});
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
                  {(Array.isArray(laundromat.machines) ? laundromat.machines.length : laundromat.machines) - laundromat.broken_machines}
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

            <div className="flex gap-2">
              <Button
                variant="secondary"
                onClick={handleRepairMachines}
                loading={isLoading}
                disabled={(laundromat.inventory?.parts || 0) < 1}
                className="flex-1 text-xs px-2"
                title="Improve condition of all machines (Uses 1 part/5 machines)"
              >
                <Wrench className="w-3 h-3 mr-1" />
                Maintain (Parts)
              </Button>
              <Button
                variant="danger"
                onClick={handleEmergencyRepair}
                loading={isLoading}
                disabled={laundromat.broken_machines === 0}
                className="flex-1 text-xs px-2"
                title="Instantly fix all broken machines (High Cost)"
              >
                <Zap className="w-3 h-3 mr-1" />
                Quick Fix (${laundromat.broken_machines * 150})
              </Button>
              <Button
                variant="ghost"
                className="flex-1 text-xs px-2"
                onClick={handleUpgradeMachine}
                loading={isLoading}
                title="Purchase New Machine"
              >
                <Gauge className="w-3 h-3 mr-1" />
                Buy ($500)
              </Button>
            </div>

            {Array.isArray(laundromat.machines) && (
              <div className="mt-6 space-y-3 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                <h4 className="text-sm font-medium text-slate-300 mb-2">Facility Equipment</h4>
                {laundromat.machines.map((m: any) => (
                  <div key={m.id} className="p-3 rounded-lg bg-white/5 flex justify-between items-center text-sm">
                    <div>
                      <div className="font-medium text-white capitalize">{m.type?.replace(/_/g, ' ') || 'Machine'} <span className="text-xs text-slate-500 ml-1">#{m.id}</span></div>
                      <div className="text-xs text-slate-400 mt-1 flex items-center gap-2">
                        <span>Cond: {(Number(m.condition || 0) * 100).toFixed(0)}%</span>
                        {m.age_weeks > 0 && <span>Age: {m.age_weeks}w</span>}
                      </div>
                    </div>
                    <Badge variant={m.is_broken ? 'warning' : 'success'} size="sm">
                      {m.is_broken ? 'Broken' : 'Ready'}
                    </Badge>
                  </div>
                ))}
              </div>
            )}
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

        {/* Supplies Tab - Redirect to Vendors */}
        <TabContent value="supplies">
          <Card variant="glass" className="text-center py-12">
            <Package className="w-12 h-12 mx-auto text-slate-500 mb-4" />
            <h3 className="text-lg font-semibold text-white mb-2">Supply Ordering Moved</h3>
            <p className="text-slate-400 mb-4">
              Order supplies directly from the <strong>Vendors</strong> tab for vendor-specific pricing and negotiation.
            </p>
            <Button
              variant="primary"
              onClick={() => useGameStore.getState().setActiveTab('vendors')}
            >
              <Package className="w-4 h-4 mr-2" />
              Go to Vendors
            </Button>

            {/* Still show pending deliveries */}
            {laundromat.pending_deliveries && laundromat.pending_deliveries.length > 0 && (
              <div className="mt-6 border-t border-white/10 pt-4 text-left">
                <h4 className="text-md font-semibold text-white mb-3">Pending Deliveries</h4>
                <div className="space-y-2">
                  {laundromat.pending_deliveries.map((delivery, idx) => (
                    <div key={idx} className="flex justify-between items-center p-2 bg-slate-800/50 rounded border border-slate-700/50 text-sm">
                      <div>
                        <span className="text-slate-200 font-medium capitalize">{delivery.item.replace(/_/g, ' ')}</span>
                        <span className="text-slate-400 ml-2">x{delivery.quantity}</span>
                      </div>
                      <div className="text-slate-400 text-xs">
                        Arrives Week {delivery.arrival_week}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        </TabContent>
      </TabGroup>
    </div>
  );
}
