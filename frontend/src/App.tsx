import { useState } from 'react';
import GameShell from './GameShell';
import LandingPage from './LandingPage';
import GameSetup from './GameSetup';
import type { GameConfig } from './GameSetup';
import { useGameStore } from './stores/gameStore';
import { Toaster } from 'sonner';

// ═══════════════════════════════════════════════════════════════════════
// App Component
// Router: LandingPage → GameSetup → GameShell
// ═══════════════════════════════════════════════════════════════════════

type AppView = 'landing' | 'setup' | 'game';

function App() {
  const startScenario = useGameStore((state) => state.startScenario);
  const [view, setView] = useState<AppView>('landing');
  const [_, setGameConfig] = useState<GameConfig | null>(null);

  const handleGetStarted = () => {
    setView('setup');
  };

  const handleStartGame = async (config: GameConfig) => {
    setGameConfig(config);
    // TODO: Pass config to backend when starting game
    // For now, start with default scenario
    await startScenario(null);
    setView('game');
  };

  const handleBackToLanding = () => {
    setView('landing');
  };

  const handleRestart = () => {
    setView('setup');
    setGameConfig(null);
  };

  return (
    <>
      <Toaster position="top-right" richColors />
      {view === 'landing' && <LandingPage onGetStarted={handleGetStarted} />}
      {view === 'setup' && <GameSetup onStart={handleStartGame} onBack={handleBackToLanding} />}
      {view === 'game' && <GameShell onRestart={handleRestart} />}
    </>
  );
}

export default App;
