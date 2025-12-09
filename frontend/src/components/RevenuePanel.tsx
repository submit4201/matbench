import React, { useState, useEffect } from 'react';
import { TrendingUp, Plus, CheckCircle, Clock, XCircle, Lightbulb, Edit2, Check, X, Power, Zap, Sparkles, ArrowUpRight, Target, Activity, Layers } from 'lucide-react';
import type { Laundromat, RevenueStream } from '../types';

interface Proposal {
  id: string;
  name: string;
  category: string;
  description: string;
  status: 'pending' | 'approved' | 'rejected' | 'deferred';
  evaluation: {
    feasibility_score?: number;
    profitability?: string;
    customer_appeal?: string;
    reasoning?: string;
  };
}

interface RevenuePanelProps {
  laundromat: Laundromat;
}

const RevenuePanel: React.FC<RevenuePanelProps> = ({ laundromat }) => {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [showForm, setShowForm] = useState(false);
  const [editingStream, setEditingStream] = useState<string | null>(null);
  const [editPrice, setEditPrice] = useState<string>('');
  const [formData, setFormData] = useState({
    name: '',
    category: 'wash',
    description: '',
    pricing_model: '',
    resource_requirements: '',
    setup_cost: '0'
  });

  const fetchProposals = async () => {
    try {
      const res = await fetch('http://localhost:8000/proposals?agent_id=p1');
      const data = await res.json();
      setProposals(data.proposals);
    } catch (err) {
      console.error("Failed to fetch proposals", err);
    }
  };

  useEffect(() => {
    fetchProposals();
    const interval = setInterval(fetchProposals, 5000);
    return () => clearInterval(interval);
  }, []);

  const handlePriceEdit = (streamName: string, currentPrice: number) => {
    setEditingStream(streamName);
    setEditPrice(currentPrice.toFixed(2));
  };

  const handlePriceSave = async (streamName: string) => {
    try {
      const res = await fetch(`http://localhost:8000/revenue_streams/${streamName}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          agent_id: 'p1',
          price: parseFloat(editPrice) 
        })
      });
      if (res.ok) {
        setEditingStream(null);
      }
    } catch (err) {
      console.error("Failed to update price", err);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      const res = await fetch('http://localhost:8000/proposals', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: 'p1',
          ...formData,
          setup_cost: parseFloat(formData.setup_cost) || 0
        })
      });
      if (res.ok) {
        setShowForm(false);
        setFormData({ name: '', category: 'wash', description: '', pricing_model: '', resource_requirements: '', setup_cost: '0' });
        fetchProposals();
      }
    } catch (err) {
      console.error("Failed to submit proposal", err);
    }
  };

  const handleApprove = async (id: string) => {
    try {
      await fetch(`http://localhost:8000/proposals/${id}/approve`, { method: 'POST' });
      fetchProposals();
    } catch (err) {
      console.error("Failed to approve", err);
    }
  };

  const handleActivate = async (streamName: string) => {
    try {
      const res = await fetch(`http://localhost:8000/revenue_streams/${encodeURIComponent(streamName)}/activate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ agent_id: 'p1' })
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Activation failed' }));
        console.error("Failed to activate service:", error.detail);
        alert(`Failed: ${error.detail}`);
      } else {
        console.log(`Activated ${streamName}`);
      }
    } catch (err) {
      console.error("Failed to activate service", err);
    }
  };

  // Separate active (unlocked) and inactive streams
  const activeStreams = laundromat.revenue_streams 
    ? Object.values(laundromat.revenue_streams).filter((s: RevenueStream) => s.unlocked)
    : [];
  const inactiveStreams = laundromat.revenue_streams 
    ? Object.values(laundromat.revenue_streams).filter((s: RevenueStream) => !s.unlocked)
    : [];

  // Calculate stats
  const totalWeeklyRevenue = activeStreams.reduce((sum, s) => sum + (s.weekly_revenue || 0), 0);
  const totalServices = activeStreams.length + inactiveStreams.length;
  const avgPrice = activeStreams.length > 0 
    ? activeStreams.reduce((sum, s) => sum + s.price, 0) / activeStreams.length 
    : 0;

  return (
    <div className="h-full flex flex-col gap-4 overflow-hidden">
      {/* Compact Header Row with Stats */}
      <div className="flex items-stretch gap-4 flex-shrink-0">
        {/* Title Card */}
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-600 via-teal-700 to-cyan-800 px-6 py-4 shadow-lg flex-shrink-0">
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-6 -right-6 w-24 h-24 bg-white/10 rounded-full blur-xl animate-pulse"></div>
          </div>
          <div className="relative flex items-center gap-3">
            <div className="w-12 h-12 bg-white/10 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/20">
              <Sparkles className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Service Hub</h2>
              <p className="text-emerald-100/70 text-sm">Manage & grow revenue</p>
            </div>
          </div>
        </div>

        {/* Quick Stats Row */}
        <div className="flex-1 grid grid-cols-4 gap-3">
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 hover:shadow-lg hover:border-emerald-500/50 transition-all group">
            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wide mb-1">
              <Activity size={14} className="text-emerald-400" />
              Weekly Revenue
            </div>
            <div className="text-2xl font-bold text-white font-mono">${totalWeeklyRevenue.toFixed(0)}</div>
          </div>
          
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 hover:shadow-lg hover:border-blue-500/50 transition-all">
            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wide mb-1">
              <Layers size={14} className="text-blue-400" />
              Total Services
            </div>
            <div className="text-2xl font-bold text-white">{totalServices}</div>
          </div>
          
          <div className="bg-slate-800 rounded-xl border border-slate-700 p-4 hover:shadow-lg hover:border-purple-500/50 transition-all">
            <div className="flex items-center gap-2 text-slate-400 text-xs font-bold uppercase tracking-wide mb-1">
              <Target size={14} className="text-purple-400" />
              Avg Price
            </div>
            <div className="text-2xl font-bold text-white font-mono">${avgPrice.toFixed(2)}</div>
          </div>
          
          <button 
            onClick={() => setShowForm(true)}
            className="bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl p-4 hover:shadow-lg hover:scale-[1.02] transition-all flex flex-col items-center justify-center gap-1 group border border-blue-500/30"
          >
            <Plus size={24} className="text-white group-hover:rotate-90 transition-transform" />
            <span className="text-white font-bold text-sm">New Proposal</span>
          </button>
        </div>
      </div>

      {/* Main Content - 2x2 Grid Layout */}
      <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-4 min-h-0">
        
        {/* Active Services - Top Left */}
        <div className="bg-slate-800 rounded-2xl shadow-sm border border-slate-700 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700 bg-gradient-to-r from-emerald-900/30 to-teal-900/30 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-600 to-teal-600 rounded-lg flex items-center justify-center shadow-md border border-white/10">
              <Zap className="text-white" size={16} />
            </div>
            <h3 className="font-bold text-white">Active Services</h3>
            <span className="ml-auto px-2 py-0.5 bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 rounded-full font-bold text-xs">{activeStreams.length}</span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
            {activeStreams.map((stream: RevenueStream) => (
              <div 
                key={stream.name} 
                className="group p-3 bg-slate-700/30 rounded-xl border border-slate-600 hover:border-emerald-500/50 hover:bg-slate-700/50 transition-all"
              >
                <div className="flex justify-between items-center">
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-white truncate flex items-center gap-2">
                      {stream.name}
                      <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-emerald-500 text-white text-[10px] rounded font-bold shadow-sm">
                        <span className="w-1 h-1 bg-white rounded-full animate-pulse"></span>
                        LIVE
                      </span>
                    </div>
                    <div className="text-xs text-slate-400 truncate">{stream.description}</div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-3 flex-shrink-0">
                    {editingStream === stream.name ? (
                      <div className="flex items-center gap-1">
                        <input
                          type="number"
                          step="0.01"
                          value={editPrice}
                          onChange={(e) => setEditPrice(e.target.value)}
                          className="w-16 px-2 py-1 bg-slate-600 border border-emerald-500/50 rounded text-right font-mono text-sm text-white focus:ring-1 focus:ring-emerald-500 outline-none"
                          autoFocus
                        />
                        <button onClick={() => handlePriceSave(stream.name)} className="p-1 bg-emerald-600 text-white rounded hover:bg-emerald-500 transition-colors">
                          <Check size={14} />
                        </button>
                        <button onClick={() => setEditingStream(null)} className="p-1 bg-slate-600 text-slate-300 rounded hover:bg-slate-500 transition-colors">
                          <X size={14} />
                        </button>
                      </div>
                    ) : (
                      <>
                        <div className="text-right">
                          <div className="font-mono font-bold text-emerald-400">${stream.price.toFixed(2)}</div>
                          {stream.weekly_revenue !== undefined && stream.weekly_revenue > 0 && (
                            <div className="text-[10px] text-emerald-500/70 flex items-center gap-0.5 justify-end">
                              <ArrowUpRight size={10} />${stream.weekly_revenue.toFixed(0)}/wk
                            </div>
                          )}
                        </div>
                        <button 
                          onClick={() => handlePriceEdit(stream.name, stream.price)}
                          className="p-1.5 text-slate-400 hover:text-emerald-400 hover:bg-emerald-500/10 rounded opacity-0 group-hover:opacity-100 transition-all"
                        >
                          <Edit2 size={14} />
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            ))}
            
            {activeStreams.length === 0 && (
              <div className="text-center py-8 text-slate-500">
                <Zap className="mx-auto mb-2 opacity-50" size={32} />
                <p className="font-medium">No active services</p>
              </div>
            )}
          </div>
        </div>

        {/* Inactive Services - Top Right */}
        <div className="bg-slate-800 rounded-2xl shadow-sm border border-slate-700 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700 bg-gradient-to-r from-slate-900/50 to-slate-800/50 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-slate-600 to-slate-700 rounded-lg flex items-center justify-center shadow-md border border-white/10">
              <Power className="text-white" size={16} />
            </div>
            <h3 className="font-bold text-white">Available Services</h3>
            <span className="ml-auto px-2 py-0.5 bg-slate-700 text-slate-300 rounded-full font-bold text-xs">{inactiveStreams.length}</span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
            {inactiveStreams.map((stream: RevenueStream) => (
              <div key={stream.name} className="group p-3 bg-slate-800/50 rounded-xl border border-slate-700 hover:border-blue-500/50 hover:bg-slate-700/50 transition-all">
                <div className="flex justify-between items-center">
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-slate-200 truncate">{stream.name}</div>
                    <div className="text-xs text-slate-500 truncate">{stream.description}</div>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="font-mono text-sm text-slate-400">${stream.price.toFixed(2)}</span>
                      {stream.setup_cost && stream.setup_cost > 0 && (
                        <span className="text-xs text-amber-500/80 bg-amber-500/10 px-1.5 py-0.5 rounded font-medium border border-amber-500/20">
                          Setup: ${stream.setup_cost}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <button 
                    onClick={() => handleActivate(stream.name)}
                    className="ml-3 px-3 py-2 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-lg font-bold text-xs hover:shadow-lg transition-all flex items-center gap-1.5 flex-shrink-0 border border-blue-500/30"
                  >
                    <Zap size={14} />
                    Activate
                  </button>
                </div>
              </div>
            ))}
            
            {inactiveStreams.length === 0 && (
              <div className="text-center py-8 text-slate-500">
                <CheckCircle className="mx-auto mb-2 text-emerald-500/50" size={32} />
                <p className="font-medium">All services active!</p>
              </div>
            )}
          </div>
        </div>

        {/* Proposals - Bottom Left */}
        <div className="bg-slate-800 rounded-2xl shadow-sm border border-slate-700 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700 bg-gradient-to-r from-amber-900/20 to-yellow-900/20 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-amber-500 to-yellow-600 rounded-lg flex items-center justify-center shadow-md border border-white/10">
              <Lightbulb className="text-white" size={16} />
            </div>
            <h3 className="font-bold text-white">Proposals</h3>
            <span className="ml-auto px-2 py-0.5 bg-amber-500/20 text-amber-300 border border-amber-500/20 rounded-full font-bold text-xs">{proposals.length}</span>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
            {proposals.length === 0 ? (
              <div className="text-center py-8 text-slate-500">
                <Lightbulb className="mx-auto mb-2 opacity-50" size={32} />
                <p className="font-medium mb-3">No proposals yet</p>
                <button 
                  onClick={() => setShowForm(true)}
                  className="px-4 py-2 bg-amber-500/10 text-amber-400 border border-amber-500/20 rounded-lg font-bold text-sm hover:bg-amber-500/20 transition-colors"
                >
                  Create First Proposal
                </button>
              </div>
            ) : (
              proposals.map(p => (
                <div key={p.id} className="p-3 border border-slate-700 rounded-xl hover:border-amber-500/30 hover:shadow-lg transition-all bg-gradient-to-r from-slate-800 to-amber-900/10">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-bold text-white">{p.name}</h4>
                    <Badge status={p.status} />
                  </div>
                  <p className="text-xs text-slate-400 mb-2 line-clamp-2">{p.description}</p>
                  
                  {p.evaluation && p.evaluation.feasibility_score && (
                    <div className="flex items-center gap-3 text-xs mb-2">
                      <span className="flex items-center gap-1 text-blue-400 font-medium">
                        <Activity size={12} />
                        {p.evaluation.feasibility_score}/100
                      </span>
                      <span className="text-slate-500">{p.evaluation.profitability}</span>
                    </div>
                  )}

                  {p.status === 'pending' && (
                    <button 
                      onClick={() => handleApprove(p.id)}
                      className="w-full py-2 bg-gradient-to-r from-emerald-600 to-teal-700 text-white rounded-lg font-bold text-sm hover:shadow-lg flex items-center justify-center gap-1.5 transition-all border border-emerald-500/30"
                    >
                      <CheckCircle size={14} />
                      Approve & Activate
                    </button>
                  )}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Revenue Insights - Bottom Right */}
        <div className="bg-slate-800 rounded-2xl shadow-sm border border-slate-700 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-slate-700 bg-gradient-to-r from-violet-900/20 to-purple-900/20 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-violet-600 to-purple-700 rounded-lg flex items-center justify-center shadow-md border border-white/10">
              <TrendingUp className="text-white" size={16} />
            </div>
            <h3 className="font-bold text-white">Revenue Breakdown</h3>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
            {activeStreams.length > 0 ? (
              <>
                {/* Revenue bars */}
                {activeStreams
                  .sort((a, b) => (b.weekly_revenue || 0) - (a.weekly_revenue || 0))
                  .map((stream: RevenueStream) => {
                    const percentage = totalWeeklyRevenue > 0 
                      ? ((stream.weekly_revenue || 0) / totalWeeklyRevenue) * 100 
                      : 0;
                    return (
                      <div key={stream.name} className="p-3 bg-slate-900/30 rounded-xl border border-slate-700/50">
                        <div className="flex justify-between items-center mb-2">
                          <span className="font-bold text-slate-200 text-sm">{stream.name}</span>
                          <span className="font-mono font-bold text-violet-400">${(stream.weekly_revenue || 0).toFixed(0)}</span>
                        </div>
                        <div className="h-2 bg-slate-700 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-violet-500 to-purple-500 rounded-full transition-all duration-500"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-slate-500 mt-1">{percentage.toFixed(0)}% of total</div>
                      </div>
                    );
                  })}
                
                {/* Summary */}
                <div className="p-3 bg-gradient-to-r from-violet-900/20 to-purple-900/20 rounded-xl border border-violet-500/20 mt-2">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-violet-300">Total Weekly</span>
                    <span className="text-xl font-mono font-bold text-violet-400">${totalWeeklyRevenue.toFixed(2)}</span>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-slate-500">
                <TrendingUp className="mx-auto mb-2 opacity-50" size={32} />
                <p className="font-medium">No revenue data</p>
                <p className="text-sm">Activate services to track</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Proposal Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-800 rounded-2xl shadow-2xl max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto border border-slate-700">
            <div className="flex justify-between items-center mb-6">
               <div className="flex items-center gap-3">
                 <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-700 rounded-xl flex items-center justify-center shadow-lg border border-white/10">
                   <Plus className="text-white" size={20} />
                 </div>
                 <h3 className="text-xl font-bold text-white">New Proposal</h3>
               </div>
               <button onClick={() => setShowForm(false)} className="p-2 text-slate-400 hover:text-white hover:bg-slate-700 rounded-lg transition-colors">
                 <XCircle size={24} />
               </button>
            </div>
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1.5">Service Name</label>
                <input 
                  type="text" 
                  value={formData.name}
                  onChange={e => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-blue-500 outline-none transition-all placeholder:text-slate-600"
                  placeholder="e.g., Eco-Friendly Wash"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-slate-400 uppercase mb-1.5">Category</label>
                  <select 
                    value={formData.category}
                    onChange={e => setFormData({...formData, category: e.target.value})}
                    className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-blue-500 outline-none"
                  >
                    <option value="wash">Wash Service</option>
                    <option value="dry">Dry Service</option>
                    <option value="bundle">Bundle</option>
                    <option value="vending">Vending</option>
                    <option value="premium">Premium Service</option>
                    <option value="ancillary">Ancillary</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                   <label className="block text-xs font-bold text-slate-400 uppercase mb-1.5">Setup Cost ($)</label>
                   <input 
                    type="number" 
                    step="0.01"
                    value={formData.setup_cost}
                    onChange={e => setFormData({...formData, setup_cost: e.target.value})}
                    className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-blue-500 outline-none font-mono placeholder:text-slate-600"
                    placeholder="0.00"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1.5">Pricing Model</label>
                <input 
                 type="text" 
                 value={formData.pricing_model}
                 onChange={e => setFormData({...formData, pricing_model: e.target.value})}
                 className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-blue-500 outline-none placeholder:text-slate-600"
                 placeholder="e.g., $5.00 per load"
                 required
               />
              </div>

              <div>
                <label className="block text-xs font-bold text-slate-400 uppercase mb-1.5">Description</label>
                <textarea 
                  value={formData.description}
                  onChange={e => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2.5 bg-slate-900 border border-slate-700 rounded-xl text-white focus:ring-2 focus:ring-blue-500 outline-none h-20 resize-none placeholder:text-slate-600"
                  placeholder="Describe the service..."
                  required
                />
              </div>

              <div className="flex justify-end gap-3 mt-2 pt-4 border-t border-slate-700">
                <button 
                  type="button" 
                  onClick={() => setShowForm(false)}
                  className="px-5 py-2.5 text-slate-400 hover:text-white hover:bg-slate-700 rounded-xl font-bold transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-700 text-white rounded-xl font-bold hover:shadow-lg transition-all border border-blue-500/30"
                >
                  Submit
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

const Badge = ({ status }: { status: string }) => {
  const styles = {
    pending: "bg-amber-500/10 text-amber-400 border border-amber-500/20",
    approved: "bg-emerald-500/10 text-emerald-400 border border-emerald-500/20",
    rejected: "bg-red-500/10 text-red-400 border border-red-500/20",
    deferred: "bg-slate-500/10 text-slate-400 border border-slate-500/20"
  };
  
  const icons = {
    pending: <Clock size={10} />,
    approved: <CheckCircle size={10} />,
    rejected: <XCircle size={10} />,
    deferred: <Clock size={10} />
  };

  return (
    <span className={`px-2 py-1 rounded-full text-[10px] font-bold flex items-center gap-1 uppercase ${styles[status as keyof typeof styles]}`}>
      {icons[status as keyof typeof icons]}
      {status}
    </span>
  );
};

export default RevenuePanel;
