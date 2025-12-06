import React, { useState, useEffect } from 'react';
import { TrendingUp, Plus, CheckCircle, Clock, XCircle, Lightbulb, Edit2, Check, X, Power, DollarSign, Zap, Sparkles, ArrowUpRight, Star, Activity, Target, Layers } from 'lucide-react';
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
        <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-emerald-500 via-teal-500 to-cyan-600 px-6 py-4 shadow-lg flex-shrink-0">
          <div className="absolute inset-0 overflow-hidden">
            <div className="absolute -top-6 -right-6 w-24 h-24 bg-white/10 rounded-full blur-xl animate-pulse"></div>
          </div>
          <div className="relative flex items-center gap-3">
            <div className="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center border border-white/30">
              <Sparkles className="text-white" size={24} />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white">Service Hub</h2>
              <p className="text-white/70 text-sm">Manage & grow revenue</p>
            </div>
          </div>
        </div>

        {/* Quick Stats Row */}
        <div className="flex-1 grid grid-cols-4 gap-3">
          <div className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg hover:border-emerald-300 transition-all group">
            <div className="flex items-center gap-2 text-gray-500 text-xs font-bold uppercase tracking-wide mb-1">
              <Activity size={14} className="text-emerald-500" />
              Weekly Revenue
            </div>
            <div className="text-2xl font-bold text-gray-900 font-mono">${totalWeeklyRevenue.toFixed(0)}</div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg hover:border-blue-300 transition-all">
            <div className="flex items-center gap-2 text-gray-500 text-xs font-bold uppercase tracking-wide mb-1">
              <Layers size={14} className="text-blue-500" />
              Total Services
            </div>
            <div className="text-2xl font-bold text-gray-900">{totalServices}</div>
          </div>
          
          <div className="bg-white rounded-xl border border-gray-200 p-4 hover:shadow-lg hover:border-purple-300 transition-all">
            <div className="flex items-center gap-2 text-gray-500 text-xs font-bold uppercase tracking-wide mb-1">
              <Target size={14} className="text-purple-500" />
              Avg Price
            </div>
            <div className="text-2xl font-bold text-gray-900 font-mono">${avgPrice.toFixed(2)}</div>
          </div>
          
          <button 
            onClick={() => setShowForm(true)}
            className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-4 hover:shadow-lg hover:scale-[1.02] transition-all flex flex-col items-center justify-center gap-1 group"
          >
            <Plus size={24} className="text-white group-hover:rotate-90 transition-transform" />
            <span className="text-white font-bold text-sm">New Proposal</span>
          </button>
        </div>
      </div>

      {/* Main Content - 2x2 Grid Layout */}
      <div className="flex-1 grid grid-cols-2 grid-rows-2 gap-4 min-h-0">
        
        {/* Active Services - Top Left */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-100 bg-gradient-to-r from-emerald-50 to-teal-50 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-emerald-500 to-teal-500 rounded-lg flex items-center justify-center shadow-md">
              <Zap className="text-white" size={16} />
            </div>
            <h3 className="font-bold text-gray-800">Active Services</h3>
            <span className="ml-auto px-2 py-0.5 bg-emerald-500 text-white rounded-full font-bold text-xs">{activeStreams.length}</span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {activeStreams.map((stream: RevenueStream) => (
              <div 
                key={stream.name} 
                className="group p-3 bg-gradient-to-r from-emerald-50 to-white rounded-lg border border-emerald-200 hover:border-emerald-400 hover:shadow-md transition-all"
              >
                <div className="flex justify-between items-center">
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-gray-900 truncate flex items-center gap-2">
                      {stream.name}
                      <span className="inline-flex items-center gap-0.5 px-1.5 py-0.5 bg-emerald-500 text-white text-[10px] rounded font-bold">
                        <span className="w-1 h-1 bg-white rounded-full animate-pulse"></span>
                        LIVE
                      </span>
                    </div>
                    <div className="text-xs text-gray-500 truncate">{stream.description}</div>
                  </div>
                  
                  <div className="flex items-center gap-2 ml-3 flex-shrink-0">
                    {editingStream === stream.name ? (
                      <div className="flex items-center gap-1">
                        <input
                          type="number"
                          step="0.01"
                          value={editPrice}
                          onChange={(e) => setEditPrice(e.target.value)}
                          className="w-16 px-2 py-1 border border-emerald-400 rounded text-right font-mono text-sm focus:ring-1 focus:ring-emerald-500 outline-none"
                          autoFocus
                        />
                        <button onClick={() => handlePriceSave(stream.name)} className="p-1 bg-emerald-500 text-white rounded hover:bg-emerald-600">
                          <Check size={14} />
                        </button>
                        <button onClick={() => setEditingStream(null)} className="p-1 bg-red-100 text-red-600 rounded hover:bg-red-200">
                          <X size={14} />
                        </button>
                      </div>
                    ) : (
                      <>
                        <div className="text-right">
                          <div className="font-mono font-bold text-emerald-700">${stream.price.toFixed(2)}</div>
                          {stream.weekly_revenue !== undefined && stream.weekly_revenue > 0 && (
                            <div className="text-[10px] text-emerald-600 flex items-center gap-0.5 justify-end">
                              <ArrowUpRight size={10} />${stream.weekly_revenue.toFixed(0)}/wk
                            </div>
                          )}
                        </div>
                        <button 
                          onClick={() => handlePriceEdit(stream.name, stream.price)}
                          className="p-1.5 text-gray-400 hover:text-emerald-600 hover:bg-emerald-50 rounded opacity-0 group-hover:opacity-100 transition-all"
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
              <div className="text-center py-8 text-gray-400">
                <Zap className="mx-auto mb-2 text-gray-300" size={32} />
                <p className="font-medium">No active services</p>
              </div>
            )}
          </div>
        </div>

        {/* Inactive Services - Top Right */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-100 bg-gradient-to-r from-slate-50 to-gray-50 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-slate-400 to-gray-500 rounded-lg flex items-center justify-center shadow-md">
              <Power className="text-white" size={16} />
            </div>
            <h3 className="font-bold text-gray-800">Available Services</h3>
            <span className="ml-auto px-2 py-0.5 bg-gray-300 text-gray-600 rounded-full font-bold text-xs">{inactiveStreams.length}</span>
          </div>
          
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {inactiveStreams.map((stream: RevenueStream) => (
              <div key={stream.name} className="group p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-300 hover:shadow-md transition-all">
                <div className="flex justify-between items-center">
                  <div className="flex-1 min-w-0">
                    <div className="font-bold text-gray-700 truncate">{stream.name}</div>
                    <div className="text-xs text-gray-400 truncate">{stream.description}</div>
                    <div className="flex items-center gap-3 mt-1">
                      <span className="font-mono text-sm text-gray-600">${stream.price.toFixed(2)}</span>
                      {stream.setup_cost && stream.setup_cost > 0 && (
                        <span className="text-xs text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded font-medium">
                          Setup: ${stream.setup_cost}
                        </span>
                      )}
                    </div>
                  </div>
                  
                  <button 
                    onClick={() => handleActivate(stream.name)}
                    className="ml-3 px-3 py-2 bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-lg font-bold text-xs hover:shadow-lg transition-all flex items-center gap-1.5 flex-shrink-0"
                  >
                    <Zap size={14} />
                    Activate
                  </button>
                </div>
              </div>
            ))}
            
            {inactiveStreams.length === 0 && (
              <div className="text-center py-8 text-gray-400">
                <CheckCircle className="mx-auto mb-2 text-emerald-300" size={32} />
                <p className="font-medium">All services active!</p>
              </div>
            )}
          </div>
        </div>

        {/* Proposals - Bottom Left */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-100 bg-gradient-to-r from-amber-50 to-yellow-50 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-amber-400 to-yellow-500 rounded-lg flex items-center justify-center shadow-md">
              <Lightbulb className="text-white" size={16} />
            </div>
            <h3 className="font-bold text-gray-800">Proposals</h3>
            <span className="ml-auto px-2 py-0.5 bg-amber-100 text-amber-700 rounded-full font-bold text-xs">{proposals.length}</span>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {proposals.length === 0 ? (
              <div className="text-center py-8 text-gray-400">
                <Lightbulb className="mx-auto mb-2 text-amber-200" size={32} />
                <p className="font-medium mb-3">No proposals yet</p>
                <button 
                  onClick={() => setShowForm(true)}
                  className="px-4 py-2 bg-amber-100 text-amber-700 rounded-lg font-bold text-sm hover:bg-amber-200 transition-colors"
                >
                  Create First Proposal
                </button>
              </div>
            ) : (
              proposals.map(p => (
                <div key={p.id} className="p-3 border border-gray-200 rounded-lg hover:border-amber-300 hover:shadow-md transition-all bg-gradient-to-r from-white to-amber-50/30">
                  <div className="flex justify-between items-start mb-2">
                    <h4 className="font-bold text-gray-900">{p.name}</h4>
                    <Badge status={p.status} />
                  </div>
                  <p className="text-xs text-gray-600 mb-2 line-clamp-2">{p.description}</p>
                  
                  {p.evaluation && p.evaluation.feasibility_score && (
                    <div className="flex items-center gap-3 text-xs mb-2">
                      <span className="flex items-center gap-1 text-blue-600">
                        <Star size={12} fill="currentColor" />
                        {p.evaluation.feasibility_score}/100
                      </span>
                      <span className="text-gray-500">{p.evaluation.profitability}</span>
                    </div>
                  )}

                  {p.status === 'pending' && (
                    <button 
                      onClick={() => handleApprove(p.id)}
                      className="w-full py-2 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-lg font-bold text-sm hover:shadow-lg flex items-center justify-center gap-1.5 transition-all"
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
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 flex flex-col min-h-0 overflow-hidden">
          <div className="flex items-center gap-2 px-4 py-3 border-b border-gray-100 bg-gradient-to-r from-violet-50 to-purple-50 flex-shrink-0">
            <div className="w-8 h-8 bg-gradient-to-br from-violet-500 to-purple-600 rounded-lg flex items-center justify-center shadow-md">
              <TrendingUp className="text-white" size={16} />
            </div>
            <h3 className="font-bold text-gray-800">Revenue Breakdown</h3>
          </div>

          <div className="flex-1 overflow-y-auto p-3 space-y-2">
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
                      <div key={stream.name} className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                        <div className="flex justify-between items-center mb-2">
                          <span className="font-bold text-gray-800 text-sm">{stream.name}</span>
                          <span className="font-mono font-bold text-violet-600">${(stream.weekly_revenue || 0).toFixed(0)}</span>
                        </div>
                        <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                          <div 
                            className="h-full bg-gradient-to-r from-violet-500 to-purple-600 rounded-full transition-all duration-500"
                            style={{ width: `${percentage}%` }}
                          ></div>
                        </div>
                        <div className="text-xs text-gray-400 mt-1">{percentage.toFixed(0)}% of total</div>
                      </div>
                    );
                  })}
                
                {/* Summary */}
                <div className="p-3 bg-gradient-to-r from-violet-100 to-purple-100 rounded-lg border border-violet-200 mt-2">
                  <div className="flex justify-between items-center">
                    <span className="font-bold text-violet-800">Total Weekly</span>
                    <span className="text-xl font-mono font-bold text-violet-700">${totalWeeklyRevenue.toFixed(2)}</span>
                  </div>
                </div>
              </>
            ) : (
              <div className="text-center py-8 text-gray-400">
                <TrendingUp className="mx-auto mb-2 text-gray-300" size={32} />
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
          <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full p-6 max-h-[90vh] overflow-y-auto">
            <div className="flex justify-between items-center mb-6">
               <div className="flex items-center gap-3">
                 <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg">
                   <Plus className="text-white" size={20} />
                 </div>
                 <h3 className="text-xl font-bold text-gray-800">New Proposal</h3>
               </div>
               <button onClick={() => setShowForm(false)} className="p-2 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded-lg">
                 <XCircle size={24} />
               </button>
            </div>
            
            <form onSubmit={handleSubmit} className="flex flex-col gap-4">
              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-1.5">Service Name</label>
                <input 
                  type="text" 
                  value={formData.name}
                  onChange={e => setFormData({...formData, name: e.target.value})}
                  className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none transition-all"
                  placeholder="e.g., Eco-Friendly Wash"
                  required
                />
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block text-xs font-bold text-gray-600 uppercase mb-1.5">Category</label>
                  <select 
                    value={formData.category}
                    onChange={e => setFormData({...formData, category: e.target.value})}
                    className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none bg-white"
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
                   <label className="block text-xs font-bold text-gray-600 uppercase mb-1.5">Setup Cost ($)</label>
                   <input 
                    type="number" 
                    step="0.01"
                    value={formData.setup_cost}
                    onChange={e => setFormData({...formData, setup_cost: e.target.value})}
                    className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none font-mono"
                    placeholder="0.00"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-1.5">Pricing Model</label>
                <input 
                 type="text" 
                 value={formData.pricing_model}
                 onChange={e => setFormData({...formData, pricing_model: e.target.value})}
                 className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
                 placeholder="e.g., $5.00 per load"
                 required
               />
              </div>

              <div>
                <label className="block text-xs font-bold text-gray-600 uppercase mb-1.5">Description</label>
                <textarea 
                  value={formData.description}
                  onChange={e => setFormData({...formData, description: e.target.value})}
                  className="w-full px-3 py-2.5 border-2 border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none h-20 resize-none"
                  placeholder="Describe the service..."
                  required
                />
              </div>

              <div className="flex justify-end gap-3 mt-2 pt-4 border-t border-gray-200">
                <button 
                  type="button" 
                  onClick={() => setShowForm(false)}
                  className="px-5 py-2.5 text-gray-600 hover:bg-gray-100 rounded-xl font-bold transition-colors"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl font-bold hover:shadow-lg transition-all"
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
    pending: "bg-amber-100 text-amber-700",
    approved: "bg-emerald-100 text-emerald-700",
    rejected: "bg-red-100 text-red-700",
    deferred: "bg-gray-100 text-gray-700"
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
