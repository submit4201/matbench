import React, { useState, useEffect } from 'react';
import { LayoutDashboard, Settings, MessageSquare, Users, Play, RotateCw, Trophy, PlayCircle, WifiOff, Brain, BarChart3, TrendingUp, Truck, Terminal, X } from 'lucide-react';
import DebugPanel from './components/DebugPanel';
import Dashboard from './components/Dashboard';
import ControlPanel from './components/ControlPanel';
import TicketSystem from './components/TicketSystem';
import CompetitorView from './components/CompetitorView';
import FinancialChart from './components/FinancialChart';
import RevenuePanel from './components/RevenuePanel';
import VendorHub from './components/VendorHub';
import { AIThinkingPanel } from './components/AIThinkingPanel';
import { HistoryViewer } from './components/HistoryViewer';
import FinancialPanel from './components/FinancialPanel';
import { ToastProvider, useToast } from './components/ToastContext';
import type { GameState } from './types';

const LayoutContent: React.FC = () => {
  const [gameState, setGameState] = useState<GameState | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'dashboard' | 'controls' | 'tickets' | 'competitors' | 'revenue' | 'services'>('dashboard');
  const [gameStarted, setGameStarted] = useState(false);
  const [gameWon, setGameWon] = useState(false);
  const [winDismissed, setWinDismissed] = useState(false);
  const [balanceHistory, setBalanceHistory] = useState<number[]>([]);
  const { addToast } = useToast();
  const [connectionError, setConnectionError] = useState(false);
  const [showAIThinking, setShowAIThinking] = useState(true);
  const [showHistory, setShowHistory] = useState(false);
  const [showVendorHub, setShowVendorHub] = useState(false);
  const [showDebug, setShowDebug] = useState(false);
  
  const getSocialScore = (score: number | { total_score: number }): number => {
    if (typeof score === 'number') return score;
    return score.total_score;
  };
  
  // Removed scenario state for now - using base game only

  const fetchState = async () => {
    try {
      const res = await fetch('http://localhost:8000/state');
      if (!res.ok) throw new Error("Server Error");
      const data = await res.json();
      setGameState(data);
      setConnectionError(false);
      
      // Update history if new week or just started
      const currentBalance = data.laundromats['p1'].balance;
      setBalanceHistory(prev => {
        if (prev.length === 0 || prev[prev.length - 1] !== currentBalance) {
           // Keep last 20 points
           const newHist = [...prev, currentBalance];
           return newHist.slice(-20);
        }
        return prev;
      });

      // Check Game End Condition (Week 24)
      if (data.week >= 24 && !gameWon && !winDismissed) {
        setGameWon(true);
      }
    } catch (err) {
      console.error("Failed to fetch state", err);
      setConnectionError(true);
    }
  };

  const handleNextTurn = async () => {
    if (loading) return;
    setLoading(true);
    try {
      const res = await fetch('http://localhost:8000/next_turn', { method: 'POST' });
      if (!res.ok) throw new Error("Simulation Failed");
      await fetchState();
      addToast(`Week ${gameState?.week ? gameState.week + 1 : '?'} Started`, 'info');
    } catch (err) {
      console.error("Failed to advance turn", err);
      addToast("Failed to advance turn. Is server running?", 'error');
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (actionType: string, params: any) => {
    try {
      const res = await fetch('http://localhost:8000/action', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: 'p1',
          action_type: actionType,
          parameters: params
        })
      });
      
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(errorData.detail || 'Action Failed');
      }
      
      const result = await res.json();
      
      // Validate result has expected structure
      if (result.status !== 'accepted') {
        throw new Error('Action was not accepted by server');
      }
      
      // Optimistic update or refetch? Refetch is safer.
      await fetchState();
      
      // Success Feedback
      if (actionType === 'buy_supplies') {
        addToast(`Ordered ${params.quantity} ${params.item}`, 'success');
      } else if (actionType === 'set_price') {
        addToast(`Price updated to $${params.price}`, 'success');
      } else if (actionType === 'resolve_ticket') {
        addToast("Ticket Resolved!", 'success');
      } else if (actionType === 'upgrade_machine') {
        addToast("Machine Upgraded!", 'success');
      } else if (actionType === 'marketing_campaign') {
        addToast("Marketing Campaign Launched! 🚀", 'success');
      }

    } catch (err) {
      console.error("Action failed", err);
      const errorMessage = err instanceof Error ? err.message : "Action failed. Check connection.";
      addToast(errorMessage, 'error');
    }
  };

  const handleNegotiate = async (vendorId: string, item: string) => {
    try {
      const res = await fetch('http://localhost:8000/negotiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: 'p1',
          vendor_id: vendorId,
          item: item
        })
      });
      
      if (!res.ok) throw new Error("Negotiation failed");
      const data = await res.json();
      
      addToast(data.message, 'info');
      // Refresh state to see updated prices if any
      await fetchState();
    } catch (err) {
      addToast("Negotiation failed", 'error');
    }
  };

  useEffect(() => {
    fetchState();
    const interval = setInterval(fetchState, 5000); // Poll occasionally
    return () => clearInterval(interval);
  }, [gameStarted]);

  // Handle restart removed unused scenario fetch - using base game for now

  if (connectionError && !gameState) return (
    <div className="h-screen w-screen flex flex-col items-center justify-center bg-gray-50 gap-4">
      <WifiOff size={48} className="text-red-400" />
      <h2 className="text-xl font-bold text-gray-700">Connection Lost</h2>
      <p className="text-gray-500">Is the backend server running?</p>
      <button onClick={fetchState} className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">Retry</button>
    </div>
  );

  if (!gameState) return (
    <div className="h-screen w-screen flex items-center justify-center bg-gray-50">
      <div className="flex flex-col items-center gap-4">
        <RotateCw className="animate-spin text-blue-600" size={40} />
        <p className="text-gray-500 font-medium">Loading Laundromat OS...</p>
      </div>
    </div>
  );

  const myLaundromat = gameState.laundromats['p1'];
  const competitors = Object.values(gameState.laundromats).filter(l => l.id !== 'p1');

  const handleRestart = async () => {
    try {
      await fetch('http://localhost:8000/reset', { method: 'POST' });
      window.location.reload();
    } catch (err) {
      console.error("Failed to restart game", err);
      addToast("Failed to restart. Try refreshing the page.", 'error');
    }
  };

  // Premium Start Screen
  if (!gameStarted) {
    return (
      <div className="h-screen w-screen relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900">
          {/* Floating orbs */}
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-blue-500/20 rounded-full blur-3xl animate-pulse"></div>
          <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          <div className="absolute top-1/2 left-1/2 w-64 h-64 bg-teal-500/15 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '2s' }}></div>
          
          {/* Grid overlay */}
          <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:50px_50px]"></div>
          
          {/* Radial gradient overlay */}
          <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_0%,rgba(0,0,0,0.5)_100%)]"></div>
        </div>

        {/* Content */}
        <div className="relative z-10 h-full flex items-center justify-center p-8">
          <div className="max-w-4xl w-full">
            {/* Logo & Title */}
            <div className="text-center mb-12">
              <div className="inline-flex items-center justify-center w-24 h-24 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600 rounded-3xl shadow-2xl shadow-indigo-500/30 mb-6 animate-float">
                <span className="text-5xl">🧺</span>
              </div>
              <h1 className="text-6xl font-black text-transparent bg-clip-text bg-gradient-to-r from-blue-400 via-indigo-400 to-purple-400 mb-4 tracking-tight">
                Laundromat Tycoon
              </h1>
              <p className="text-xl text-slate-400 max-w-lg mx-auto">
                Build, manage, and dominate the neighborhood laundry business
              </p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-3 gap-6 mb-12">
              <div className="group bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6 hover:bg-white/10 hover:border-white/20 transition-all hover:scale-105 hover:-translate-y-1">
                <div className="w-14 h-14 bg-gradient-to-br from-emerald-400 to-green-600 rounded-xl flex items-center justify-center mb-4 shadow-lg shadow-emerald-500/30">
                  <span className="text-2xl">💰</span>
                </div>
                <div className="text-3xl font-black text-white mb-1">$2,500</div>
                <div className="text-slate-400 font-medium">Starting Capital</div>
              </div>
              
              <div className="group bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6 hover:bg-white/10 hover:border-white/20 transition-all hover:scale-105 hover:-translate-y-1">
                <div className="w-14 h-14 bg-gradient-to-br from-blue-400 to-indigo-600 rounded-xl flex items-center justify-center mb-4 shadow-lg shadow-blue-500/30">
                  <span className="text-2xl">🧺</span>
                </div>
                <div className="text-3xl font-black text-white mb-1">15</div>
                <div className="text-slate-400 font-medium">Machines Ready</div>
              </div>
              
              <div className="group bg-white/5 backdrop-blur-xl rounded-2xl border border-white/10 p-6 hover:bg-white/10 hover:border-white/20 transition-all hover:scale-105 hover:-translate-y-1">
                <div className="w-14 h-14 bg-gradient-to-br from-amber-400 to-orange-600 rounded-xl flex items-center justify-center mb-4 shadow-lg shadow-amber-500/30">
                  <span className="text-2xl">🎯</span>
                </div>
                <div className="text-3xl font-black text-white mb-1">24</div>
                <div className="text-slate-400 font-medium">Weeks to Dominate</div>
              </div>
            </div>

            {/* Start Button */}
            <div className="text-center">
              <button 
                onClick={() => setGameStarted(true)}
                className="group relative px-12 py-5 bg-gradient-to-r from-blue-500 via-indigo-500 to-purple-600 text-white rounded-2xl font-bold text-xl shadow-2xl shadow-indigo-500/30 hover:shadow-indigo-500/50 hover:scale-105 transition-all overflow-hidden"
              >
                <span className="relative z-10 flex items-center gap-3">
                  <Play size={24} fill="currentColor" />
                  Start Your Empire
                </span>
                {/* Shimmer effect */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent -translate-x-full group-hover:translate-x-full transition-transform duration-1000"></div>
              </button>
              
              <p className="text-slate-500 text-sm mt-6">
                Compete against AI rivals • Manage inventory • Build reputation
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen w-screen bg-gray-100 flex overflow-hidden font-sans text-gray-900 relative">
      
    {/* Premium Game End Screen Overlay */}
      {gameWon && (
        <div className="absolute inset-0 z-[70] flex items-center justify-center p-4">
          {/* Animated background */}
          <div className="absolute inset-0 bg-gradient-to-br from-slate-900/95 via-indigo-950/95 to-slate-900/95 backdrop-blur-md">
            <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-amber-500/20 rounded-full blur-3xl animate-pulse"></div>
            <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }}></div>
          </div>
          
          <div className="relative bg-white/10 backdrop-blur-xl rounded-3xl border border-white/20 max-w-lg w-full p-8 text-center shadow-2xl animate-bounce-in">
            {/* Trophy */}
            <div className="w-28 h-28 bg-gradient-to-br from-amber-400 via-yellow-500 to-orange-500 rounded-3xl flex items-center justify-center mx-auto mb-6 shadow-2xl shadow-amber-500/30 animate-float">
              <Trophy size={56} className="text-white drop-shadow-lg" />
            </div>
            
            <h2 className="text-4xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-200 via-yellow-300 to-amber-200 mb-2">Victory!</h2>
            <p className="text-slate-300 mb-8">
              You've conquered the 24-week challenge. Here's your legacy:
            </p>
            
            <div className="grid grid-cols-2 gap-4 mb-8">
              <div className="bg-white/10 backdrop-blur rounded-2xl p-5 border border-white/10">
                <div className="text-slate-400 text-sm font-medium mb-1">Final Balance</div>
                <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-emerald-400 to-green-400 font-mono">
                  ${myLaundromat.balance.toFixed(0)}
                </div>
              </div>
              <div className="bg-white/10 backdrop-blur rounded-2xl p-5 border border-white/10">
                <div className="text-slate-400 text-sm font-medium mb-1">Reputation</div>
                <div className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-yellow-400 font-mono">
                  {getSocialScore(myLaundromat.social_score).toFixed(1)}
                </div>
              </div>
            </div>

            <div className="flex gap-4">
              <button 
                onClick={() => { setGameWon(false); setWinDismissed(true); }} 
                className="flex-1 px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl border border-white/20 transition-all"
              >
                View Dashboard
              </button>
              <button 
                onClick={handleRestart} 
                className="flex-1 px-6 py-3 bg-gradient-to-r from-blue-500 to-indigo-600 text-white font-bold rounded-xl shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 hover:scale-105 transition-all"
              >
                Play Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Debug Panel Modal */}
      {showDebug && gameState && (
        <DebugPanel 
          laundromat={myLaundromat} 
          gameState={gameState} 
          onClose={() => setShowDebug(false)} 
        />
      )}

      {/* History Viewer Modal */}
      <HistoryViewer isOpen={showHistory} onClose={() => setShowHistory(false)} />

      {/* Vendor Hub Modal */}
      {gameState && (
        <VendorHub 
          isOpen={showVendorHub} 
          onClose={() => setShowVendorHub(false)}
          vendors={gameState.market?.vendors || []}
          supplyChainEvents={gameState.market?.supply_chain_events || []}
          onBuy={(item, qty, vendorId) => handleAction('buy_supplies', { item, quantity: qty, vendor_id: vendorId })}
          onNegotiate={handleNegotiate}
        />
      )}

      {/* Premium Sidebar */}
      <div className="w-[72px] bg-gradient-to-b from-slate-900 via-slate-800 to-slate-900 flex flex-col items-center py-4 gap-2 shadow-xl z-[60]">
        {/* Logo */}
        <div className="w-11 h-11 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-white font-bold text-lg shadow-lg shadow-blue-500/30 mb-3">
          <span className="font-mono">LT</span>
        </div>
        
        <nav className="flex flex-col gap-1.5 w-full px-2 flex-1 overflow-y-auto min-h-0 py-2 scrollbar-hide">
          <NavButton 
            active={activeTab === 'dashboard' && !showVendorHub && !showHistory} 
            onClick={() => { setActiveTab('dashboard'); setShowVendorHub(false); setShowHistory(false); }} 
            icon={<LayoutDashboard size={20} />} 
            label="Dash"
          />
          <NavButton 
            active={activeTab === 'controls' && !showVendorHub && !showHistory} 
            onClick={() => { setActiveTab('controls'); setShowVendorHub(false); setShowHistory(false); }} 
            icon={<Settings size={20} />} 
            label="Manage"
          />
          <NavButton 
            active={showVendorHub} 
            onClick={() => { setShowVendorHub(true); setShowHistory(false); }} 
            icon={<Truck size={20} />} 
            label="Vendors"
          />
          <NavButton 
            active={activeTab === 'revenue' && !showVendorHub && !showHistory} 
            onClick={() => { setActiveTab('revenue'); setShowVendorHub(false); setShowHistory(false); }} 
            icon={<TrendingUp size={20} />} 
            label="Finance"
          />
          <NavButton 
            active={activeTab === 'services' && !showVendorHub && !showHistory} 
            onClick={() => { setActiveTab('services'); setShowVendorHub(false); setShowHistory(false); }} 
            icon={<BarChart3 size={20} />} 
            label="Services"
          />
          <NavButton 
            active={activeTab === 'tickets' && !showVendorHub && !showHistory} 
            onClick={() => { setActiveTab('tickets'); setShowVendorHub(false); setShowHistory(false); }} 
            icon={<MessageSquare size={20} />} 
            label="Tickets"
            badge={myLaundromat.tickets.filter(t => t.status === 'open').length}
          />
          <NavButton 
            active={activeTab === 'competitors' && !showVendorHub && !showHistory} 
            onClick={() => { setActiveTab('competitors'); setShowVendorHub(false); setShowHistory(false); }} 
            icon={<Users size={20} />} 
            label="Rivals"
          />
          <NavButton 
            active={showAIThinking} 
            onClick={() => setShowAIThinking(!showAIThinking)} 
            icon={<Brain size={20} />} 
            label="AI"
          />
          <NavButton 
            active={showHistory} 
            onClick={() => { setShowHistory(true); setShowVendorHub(false); }} 
            icon={<BarChart3 size={20} />} 
            label="History"
          />
          <NavButton 
            active={showDebug} 
            onClick={() => { setShowDebug(true); setShowVendorHub(false); setShowHistory(false); }} 
            icon={<Terminal size={20} />} 
            label="Debug"
          />
        </nav>

        <div className="flex flex-col gap-2 w-full px-2">
           {/* Restart Button */}
           <button 
            onClick={handleRestart}
            className="w-full aspect-square rounded-xl flex items-center justify-center transition-all bg-red-500/20 text-red-400 hover:bg-red-500/30 hover:text-red-300 hover:scale-105 active:scale-95"
            title="Restart Game"
          >
            <RotateCw size={20} />
          </button>
           {/* Next Turn Button */}
           <button 
            onClick={handleNextTurn}
            disabled={loading}
            className={`w-full aspect-square rounded-xl flex items-center justify-center transition-all ${
              loading 
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed' 
                : 'bg-gradient-to-br from-emerald-500 to-green-600 text-white shadow-lg shadow-emerald-500/30 hover:shadow-xl hover:scale-105 active:scale-95'
            }`}
            title="Next Week"
          >
            {loading ? <RotateCw className="animate-spin" size={20} /> : <Play fill="currentColor" size={20} />}
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Premium Top Bar */}
        <header className="h-16 bg-white border-b border-gray-100 flex items-center justify-between px-6 shadow-sm">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-white text-lg font-bold shadow-md">
              🧺
            </div>
            <div>
              <h1 className="text-lg font-bold text-gray-800">{myLaundromat.name}</h1>
              <p className="text-[10px] text-gray-400 uppercase tracking-wider font-bold">{gameState.season} Season</p>
            </div>
            
            {/* Week Progress Bar */}
            <div className="flex items-center gap-3 px-4 py-2 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-xl border border-indigo-200">
              <div className="text-center">
                <div className="text-[10px] text-indigo-500 uppercase font-bold">Week</div>
                <div className="text-xl font-black text-indigo-700">{gameState.week}</div>
              </div>
              <div className="flex flex-col gap-1">
                <div className="w-32 h-2 bg-indigo-100 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-gradient-to-r from-indigo-500 to-purple-500 rounded-full transition-all duration-500" 
                    style={{ width: `${(gameState.week / 24) * 100}%` }}
                  ></div>
                </div>
                <div className="text-[10px] text-gray-500 text-center">{gameState.week} of 24 weeks</div>
              </div>
            </div>
          </div>
          
          <div className="flex items-center gap-3">
             <div className="px-4 py-2 bg-gradient-to-r from-emerald-50 to-green-50 rounded-xl border border-emerald-200">
                <div className="text-[10px] text-emerald-600 uppercase font-bold tracking-wider">Balance</div>
                <div className="text-lg font-bold text-emerald-700 font-mono">${myLaundromat.balance.toFixed(0)}</div>
             </div>
             <div className="px-4 py-2 bg-gradient-to-r from-amber-50 to-yellow-50 rounded-xl border border-amber-200">
                <div className="text-[10px] text-amber-600 uppercase font-bold tracking-wider">Reputation</div>
                <div className="text-lg font-bold text-amber-700 font-mono">
                  {getSocialScore(myLaundromat.social_score).toFixed(1)}
                </div>
             </div>
          </div>
        </header>

        {/* Event Ticker */}
        {gameState.events && gameState.events.length > 0 && (
          <div className="bg-indigo-600 text-white px-4 py-2 text-sm font-medium flex items-center gap-2 overflow-hidden whitespace-nowrap">
            <span className="font-bold bg-indigo-800 px-2 py-0.5 rounded text-xs uppercase tracking-wider">News</span>
            <div className="animate-marquee inline-block">
               {gameState.events.join(" • ")}
            </div>
          </div>
        )}

        {/* View Area */}
        <main className="flex-1 p-6 overflow-hidden bg-gray-50/50">
          {/* AI Thinking Panel - shown above main content */}
          {showAIThinking && (
            <div className="max-w-7xl mx-auto mb-4">
              {gameState.ai_thoughts && Object.keys(gameState.ai_thoughts).length > 0 ? (
                <AIThinkingPanel 
                  thoughts={gameState.ai_thoughts} 
                  isExpanded={showAIThinking}
                  onToggle={() => setShowAIThinking(false)}
                />
              ) : (
                <div className="bg-white p-4 rounded-xl shadow-sm border border-blue-100 flex items-center gap-3 text-gray-500">
                  <Brain className="text-blue-300" size={20} />
                  <span className="text-sm font-medium">AI is analyzing the market... (No insights available yet)</span>
                </div>
              )}
            </div>
          )}
          
          <div className="h-full max-w-7xl mx-auto w-full">
            {activeTab === 'dashboard' && (
              <Dashboard 
                laundromat={myLaundromat} 
                week={gameState.week} 
                season={gameState.season} 
                customerThoughts={gameState.customer_thoughts || []}
              />
            )}
            
            {activeTab === 'controls' && (
              <div className="h-full grid grid-cols-1 md:grid-cols-2 gap-6">
                <ControlPanel 
                  laundromat={myLaundromat}
                  market={gameState.market}
                  onSetPrice={(p) => handleAction('set_price', { price: p })}
                  onBuySupplies={(i, q, v) => handleAction('buy_supplies', { item: i, quantity: q, vendor_id: v })}
                  onUpgrade={(t) => handleAction('upgrade_machine', { type: t })}
                  onMarketingCampaign={(cost) => handleAction('marketing_campaign', { cost })}
                />
                
                <div className="bg-white rounded-xl shadow-lg border border-gray-100 p-6 flex flex-col">
                   <h3 className="text-lg font-bold text-gray-800 mb-4">Financial Overview</h3>
                   <div className="flex-1 min-h-0">
                      <FinancialChart data={balanceHistory} />
                   </div>
                </div>
              </div>
            )}

            {activeTab === 'revenue' && (
              <FinancialPanel laundromat={myLaundromat} />
            )}

            {activeTab === 'services' && (
              <RevenuePanel laundromat={myLaundromat} />
            )}

            {activeTab === 'tickets' && (
              <div className="h-full max-w-4xl mx-auto">
                <TicketSystem 
                  tickets={myLaundromat.tickets} 
                  onResolve={(id) => handleAction('resolve_ticket', { ticket_id: id })}
                />
              </div>
            )}

            {activeTab === 'competitors' && (
              <CompetitorView competitors={competitors} />
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

interface NavButtonProps {
  active: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  badge?: number;
}

const NavButton: React.FC<NavButtonProps> = ({ active, onClick, icon, label, badge }) => (
  <button
    onClick={onClick}
    className={`w-full py-2.5 rounded-xl flex flex-col items-center justify-center gap-0.5 transition-all relative group ${
      active 
        ? 'bg-gradient-to-br from-blue-500 to-indigo-600 text-white shadow-lg shadow-blue-500/30' 
        : 'text-slate-400 hover:bg-slate-700/50 hover:text-slate-200'
    }`}
  >
    {icon}
    <span className="text-[9px] font-medium tracking-wide">{label}</span>
    {badge ? (
      <span className="absolute top-0.5 right-0.5 w-4 h-4 bg-red-500 text-white text-[10px] flex items-center justify-center rounded-full font-bold shadow-sm">
        {badge}
      </span>
    ) : null}
  </button>
);

const Layout: React.FC = () => (
  <ToastProvider>
    <LayoutContent />
  </ToastProvider>
);

export default Layout;
