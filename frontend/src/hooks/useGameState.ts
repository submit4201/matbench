import { useEffect } from 'react';
import { useGameStore } from '../stores/gameStore';

// ═══════════════════════════════════════════════════════════════════════
// useGameState Hook
// Convenience wrapper around Zustand store with initialization
// ═══════════════════════════════════════════════════════════════════════

export function useGameState() {
  const store = useGameStore();
  
  useEffect(() => {
    // Only fetch if we don't have state yet
    if (!store.gameState && !store.isLoading) {
      store.fetchState();
    }
  }, [store.gameState, store.isLoading]);

  return store;
}

// Re-export the store for direct access
export { useGameStore };
