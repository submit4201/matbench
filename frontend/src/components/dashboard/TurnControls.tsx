import React from 'react';
import { Play, RotateCcw, FastForward, StepForward } from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Button } from '../shared';
import GameClock from './GameClock';

// ═══════════════════════════════════════════════════════════════════════
// TurnControls Component
// Next Turn button, Auto-play toggle, Restart
// ═══════════════════════════════════════════════════════════════════════

interface TurnControlsProps {
  onRestart?: () => void;
}

export default function TurnControls({ onRestart }: TurnControlsProps) {
  const { nextTurn, nextDay, resetGame, isLoading, gameState } = useGameStore();
  const [autoPlay, setAutoPlay] = React.useState(false);
  const autoPlayRef = React.useRef<ReturnType<typeof setInterval> | null>(null);

  // Auto-play logic
  React.useEffect(() => {
    if (autoPlay && gameState) {
      autoPlayRef.current = setInterval(() => {
        nextTurn();
      }, 3000);
    }


    return () => {
      if (autoPlayRef.current) {
        clearInterval(autoPlayRef.current);
      }
    };
  }, [autoPlay, gameState, nextTurn]);

  const handleNextTurn = async () => {
    await nextTurn();
  };

  const handleRestart = async () => {
    setAutoPlay(false);
    await resetGame();
    onRestart?.();
  };

  const toggleAutoPlay = () => {
    setAutoPlay((prev) => !prev);
  };

  return (
    <div className="flex items-center gap-4">
      {/* Turn Info */}
      <GameClock />

      <div className="flex items-center gap-2">
        {/* Auto-play Toggle */}
        <Button
          variant={autoPlay ? 'primary' : 'ghost'}
          size="sm"
          onClick={toggleAutoPlay}
          icon={<FastForward className="w-4 h-4" />}
          title={autoPlay ? 'Stop Auto-play' : 'Start Auto-play'}
        >
          {autoPlay ? 'Auto' : ''}
        </Button>

        {/* Next Day */}
        <Button
          variant="secondary"
          size="sm"
          onClick={() => nextDay()}
          loading={isLoading}
          disabled={autoPlay}
          icon={<StepForward className="w-4 h-4" />}
          title="Advance Day"
        >
          Next Day
        </Button>

        {/* Next Week */}
        <Button
          variant="primary"
          size="md"
          onClick={handleNextTurn}
          loading={isLoading}
          disabled={autoPlay}
          icon={<Play className="w-4 h-4" />}
          title="Advance Week"
        >
          Next Week
        </Button>

        {/* Restart */}
        <Button
          variant="ghost"
          size="sm"
          onClick={handleRestart}
          icon={<RotateCcw className="w-4 h-4" />}
          title="Restart Game"
        >
          Restart
        </Button>
      </div>
    </div>
  );
}
