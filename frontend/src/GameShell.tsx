import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  LayoutDashboard,
  Wallet,
  Settings,
  MessageSquare,
  Users,
  Store,
  Map,
  History,
  Trophy,
  Bug,
  Menu,
  X,
} from 'lucide-react';
import { useGameStore } from './stores/gameStore';
import { Dashboard, TurnControls } from './components/dashboard/index';
import { FinancePanel } from './components/finance';
import { OperationsPanel } from './components/operations';
import { MessageCenter } from './components/communications';
import { SocialDashboard } from './components/social';
import { NotificationDot } from './components/shared';
import VendorHub from './components/vendors/VendorHub';
import NeighborhoodView from './components/neighborhood/NeighborhoodView';
import HistoryViewer from './components/history/HistoryViewer';
import Scoreboard from './components/scoreboard/Scoreboard';

// ═══════════════════════════════════════════════════════════════════════
// GameShell Component
// Main layout with sidebar navigation and content area
// ═══════════════════════════════════════════════════════════════════════

// Navigation items configuration
const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'finance', label: 'Finance', icon: Wallet },
  { id: 'operations', label: 'Operations', icon: Settings },
  { id: 'messages', label: 'Messages', icon: MessageSquare, hasBadge: true },
  { id: 'social', label: 'Social', icon: Users },
  { id: 'vendors', label: 'Vendors', icon: Store },
  { id: 'neighborhood', label: 'Neighborhood', icon: Map },
  { id: 'history', label: 'History', icon: History },
  { id: 'scoreboard', label: 'Scoreboard', icon: Trophy },
];

interface GameShellProps {
  onRestart?: () => void;
}

export default function GameShell({ onRestart }: GameShellProps) {
  const activeTab = useGameStore((state) => state.activeTab);
  const setActiveTab = useGameStore((state) => state.setActiveTab);
  const fetchState = useGameStore((state) => state.fetchState);
  const gameState = useGameStore((state) => state.gameState);

  // Selector for unread count to ensure reactivity
  const unreadCount = useGameStore((state) =>
    state.gameState?.messages?.filter((m) => !m.is_read).length ?? 0
  );

  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showDebug, setShowDebug] = useState(false);

  // Fetch state on mount
  useEffect(() => {
    fetchState();
  }, [fetchState]);



  // Render content based on active tab
  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'finance':
        return <FinancePanel />;
      case 'operations':
        return <OperationsPanel />;
      case 'messages':
        return <MessageCenter />;
      case 'social':
        return <SocialDashboard />;
      case 'vendors':
        return <VendorHub />;
      case 'neighborhood':
        return <NeighborhoodView />;
      case 'history':
        return <HistoryViewer />;
      case 'scoreboard':
        return <Scoreboard />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="flex h-screen bg-slate-900 overflow-hidden">
      {/* Sidebar */}
      <AnimatePresence mode="wait">
        {sidebarOpen && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 240, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="flex flex-col bg-slate-800/50 backdrop-blur-sm border-r border-slate-700 overflow-hidden"
          >
            {/* Logo */}
            <div className="p-4 border-b border-slate-700">
              <h1 className="text-lg font-bold text-white flex items-center gap-2">
                <span className="text-2xl">🧺</span>
                Laundromat Tycoon
              </h1>
            </div>

            {/* Navigation */}
            <nav className="flex-1 p-3 space-y-1 overflow-y-auto custom-scrollbar">
              {navItems.map((item) => {
                const Icon = item.icon;
                const isActive = activeTab === item.id;

                return (
                  <button
                    key={item.id}
                    onClick={() => setActiveTab(item.id)}
                    className={`
                      relative w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium
                      transition-all duration-200
                      ${isActive
                        ? 'bg-emerald-500/20 text-emerald-400 shadow-lg shadow-emerald-500/10'
                        : 'text-slate-400 hover:bg-white/5 hover:text-white'
                      }
                    `}
                  >
                    <Icon className="w-5 h-5" />
                    <span>{item.label}</span>
                    {item.hasBadge && unreadCount > 0 && (
                      <NotificationDot count={unreadCount} className="relative top-0 right-0" />
                    )}
                  </button>
                );
              })}
            </nav>

            {/* Debug Toggle */}
            <div className="p-3 border-t border-slate-700">
              <button
                onClick={() => setShowDebug((prev) => !prev)}
                className={`
                  w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm
                  ${showDebug ? 'bg-amber-500/20 text-amber-400' : 'text-slate-500 hover:bg-white/5'}
                `}
              >
                <Bug className="w-4 h-4" />
                Debug Mode
              </button>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <header className="flex items-center justify-between px-6 py-4 bg-slate-800/30 border-b border-slate-700">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen((prev) => !prev)}
              className="p-2 text-slate-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
            >
              {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
            <h2 className="text-lg font-semibold text-white capitalize">{activeTab}</h2>
          </div>
          <TurnControls onRestart={onRestart} />
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto p-6 custom-scrollbar">
          <AnimatePresence mode="wait">
            <motion.div
              key={activeTab}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              transition={{ duration: 0.2 }}
            >
              {renderContent()}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>

      {/* Debug Panel (if enabled) */}
      <AnimatePresence>
        {showDebug && gameState && (
          <motion.aside
            initial={{ width: 0, opacity: 0 }}
            animate={{ width: 320, opacity: 1 }}
            exit={{ width: 0, opacity: 0 }}
            className="bg-slate-900 border-l border-slate-700 overflow-hidden"
          >
            <div className="p-4 border-b border-slate-700">
              <h3 className="font-semibold text-amber-400">Debug Panel</h3>
            </div>
            <div className="p-4 text-xs font-mono text-slate-400 overflow-auto h-full">
              <pre className="whitespace-pre-wrap">
                {JSON.stringify(gameState, null, 2)}
              </pre>
            </div>
          </motion.aside>
        )}
      </AnimatePresence>
    </div>
  );
}
