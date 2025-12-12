import { create } from 'zustand';
import type { GameState, Laundromat, Message, Vendor, AIThought, CreditReport, ZoneInfo, ScheduledAction, CalendarStats } from '../types';

// ═══════════════════════════════════════════════════════════════════════
// Zustand Game Store
// Central state management for Laundromat Tycoon
// ═══════════════════════════════════════════════════════════════════════

const API_BASE = 'http://localhost:8000';

interface GameStore {
  // ─── Core State ───────────────────────────────────────────────────────
  gameState: GameState | null;
  isLoading: boolean;
  error: string | null;
  activeTab: string;
  playerId: string;

  // ─── Extended State ───────────────────────────────────────────────────
  creditReport: CreditReport | null;
  zoneInfo: ZoneInfo | null;
  calendar: { stats: CalendarStats; scheduled_actions: ScheduledAction[] } | null;

  // ─── Actions ──────────────────────────────────────────────────────────
  setActiveTab: (tab: string) => void;
  fetchState: () => Promise<void>;
  nextTurn: () => Promise<void>;
  nextDay: () => Promise<void>;
  sendAction: (actionType: string, params: Record<string, unknown>) => Promise<boolean>;
  negotiate: (vendorId: string, item: string) => Promise<{ accepted: boolean; new_price?: number; message?: string }>;
  resetGame: () => Promise<void>;
  startScenario: (scenarioName: string | null) => Promise<void>;
  fetchCreditReport: () => Promise<void>;
  fetchZoneInfo: () => Promise<void>;
  fetchCalendar: () => Promise<void>;
  sendMessage: (channel: string, recipientId: string, content: string, intent: string) => Promise<void>;

  // ─── Selectors ────────────────────────────────────────────────────────
  getPlayerLaundromat: () => Laundromat | null;
  getCompetitors: () => Laundromat[];
  getVendors: () => Vendor[];
  getMessages: () => Message[];
  getUnreadMessageCount: () => number;
  getAIThoughts: () => Record<string, AIThought>;
}

export const useGameStore = create<GameStore>((set, get) => ({
  // ─── Initial State ────────────────────────────────────────────────────
  gameState: null,
  isLoading: false,
  error: null,
  activeTab: 'dashboard',
  playerId: 'p1',
  creditReport: null,
  zoneInfo: null,
  calendar: null,

  // ─── Tab Navigation ───────────────────────────────────────────────────
  setActiveTab: (tab) => set({ activeTab: tab }),

  // ─── Fetch Game State ─────────────────────────────────────────────────
  fetchState: async () => {
    const { playerId } = get();
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/state?agent_id=${playerId}`);
      if (!response.ok) throw new Error(`Failed to fetch state: ${response.statusText}`);
      const data: GameState = await response.json();
      set({ gameState: data, isLoading: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error', isLoading: false });
    }
  },


  // ─── Next Turn ────────────────────────────────────────────────────────
  nextTurn: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/next_turn`, { method: 'POST' });
      if (!response.ok) throw new Error(`Failed to advance turn: ${response.statusText}`);
      // Refetch state after turn
      await get().fetchState();
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error', isLoading: false });
    }
  },

  nextDay: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/next_day`, { method: 'POST' });
      if (!response.ok) throw new Error(`Failed to advance day: ${response.statusText}`);
      const data = await response.json();
      set({ gameState: data, isLoading: false });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error', isLoading: false });
    }
  },

  // ─── Send Action ──────────────────────────────────────────────────────
  sendAction: async (actionType, params) => {
    const { playerId } = get();
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: playerId,
          action_type: actionType,
          parameters: params,
        }),
      });
      if (!response.ok) throw new Error(`Failed to send action: ${response.statusText}`);
      // Refetch state after action
      await get().fetchState();
      return true;
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error', isLoading: false });
      return false;
    }
  },

  // ─── Negotiate ────────────────────────────────────────────────────────
  negotiate: async (vendorId, item) => {
    const { playerId } = get();
    try {
      const response = await fetch(`${API_BASE}/negotiate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: playerId,
          vendor_id: vendorId,
          item: item,
        }),
      });
      if (!response.ok) throw new Error(`Negotiation failed: ${response.statusText}`);
      const result = await response.json();
      await get().fetchState();
      return result;
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
      return { accepted: false, message: 'Negotiation failed' };
    }
  },

  // ─── Reset Game ───────────────────────────────────────────────────────
  resetGame: async () => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/reset`, { method: 'POST' });
      if (!response.ok) throw new Error(`Failed to reset: ${response.statusText}`);
      set({ gameState: null, creditReport: null, zoneInfo: null, calendar: null });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error', isLoading: false });
    }
  },

  // ─── Start Scenario ───────────────────────────────────────────────────
  startScenario: async (scenarioName) => {
    set({ isLoading: true, error: null });
    try {
      const response = await fetch(`${API_BASE}/start_scenario`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ scenario_name: scenarioName }),
      });
      if (!response.ok) throw new Error(`Failed to start scenario: ${response.statusText}`);
      await get().fetchState();
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error', isLoading: false });
    }
  },

  // ─── Fetch Credit Report ──────────────────────────────────────────────
  fetchCreditReport: async () => {
    const { playerId } = get();
    try {
      const response = await fetch(`${API_BASE}/credit/${playerId}`);
      if (!response.ok) throw new Error(`Failed to fetch credit: ${response.statusText}`);
      const data = await response.json();
      // Backend returns { credit: {...} }, extract the inner object
      set({ creditReport: data.credit ?? data });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // ─── Fetch Zone Info ──────────────────────────────────────────────────
  fetchZoneInfo: async () => {
    const { playerId } = get();
    try {
      const response = await fetch(`${API_BASE}/zone/${playerId}`);
      if (!response.ok) throw new Error(`Failed to fetch zone: ${response.statusText}`);
      const data: ZoneInfo = await response.json();
      set({ zoneInfo: data });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // ─── Fetch Calendar ───────────────────────────────────────────────────
  fetchCalendar: async () => {
    const { playerId } = get();
    try {
      const response = await fetch(`${API_BASE}/calendar/${playerId}`);
      if (!response.ok) throw new Error(`Failed to fetch calendar: ${response.statusText}`);
      const data = await response.json();
      set({ calendar: data });
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // ─── Send Message ─────────────────────────────────────────────────────
  sendMessage: async (channel, recipientId, content, intent) => {
    const { playerId } = get();
    try {
      const response = await fetch(`${API_BASE}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: playerId,
          action_type: 'SEND_MESSAGE',
          parameters: { channel, recipient_id: recipientId, content, intent },
        }),
      });
      if (!response.ok) throw new Error(`Failed to send message: ${response.statusText}`);
      await get().fetchState();
    } catch (err) {
      set({ error: err instanceof Error ? err.message : 'Unknown error' });
    }
  },

  // ─── Selectors ────────────────────────────────────────────────────────
  getPlayerLaundromat: () => {
    const { gameState, playerId } = get();
    return gameState?.laundromats?.[playerId] ?? null;
  },

  getCompetitors: () => {
    const { gameState, playerId } = get();
    if (!gameState?.laundromats) return [];
    return Object.entries(gameState.laundromats)
      .filter(([id]) => id !== playerId)
      .map(([, laundromat]) => laundromat);
  },

  getVendors: () => {
    const { gameState } = get();
    return gameState?.market?.vendors ?? [];
  },

  getMessages: () => {
    const { gameState } = get();
    return gameState?.messages ?? [];
  },

  getUnreadMessageCount: () => {
    const { gameState } = get();
    return gameState?.messages?.filter((m) => !m.is_read).length ?? 0;
  },

  getAIThoughts: () => {
    const { gameState } = get();
    return gameState?.ai_thoughts ?? {};
  },
}));
