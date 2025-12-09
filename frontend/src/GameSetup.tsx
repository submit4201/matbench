import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Play,
  Settings,
  Clock,
  DollarSign,
  Brain,
  Zap,
  Calendar,
  Users,
  ChevronLeft,
} from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════
// GameSetup Component
// Custom game configuration (replaces scenario selection)
// ═══════════════════════════════════════════════════════════════════════

interface GameSetupProps {
  onStart: (config: GameConfig) => void;
  onBack: () => void;
}

export interface GameConfig {
  aiModel: string;
  timeMode: 'realtime' | 'daily' | 'weekly' | 'manual';
  weeks: number;
  startingMoney: number;
  competitorCount: number;
  difficulty: 'easy' | 'medium' | 'hard' | 'chaos';
}

const aiModels = [
  { id: 'gemini', name: 'Gemini 2.0', provider: 'Google', icon: '🟢' },
  { id: 'gpt4', name: 'GPT-4o', provider: 'OpenAI', icon: '🟣' },
  { id: 'claude', name: 'Claude 3.5', provider: 'Anthropic', icon: '🟠' },
  { id: 'phi', name: 'Phi-3', provider: 'Microsoft', icon: '🔵' },
  { id: 'llama', name: 'Llama 3', provider: 'Meta', icon: '🦙' },
  { id: 'custom', name: 'Custom API', provider: 'Your Model', icon: '⚙️' },
];

const timeModes = [
  { id: 'realtime', name: 'Real-time', desc: '1 turn per second', icon: <Zap className="w-4 h-4" /> },
  { id: 'daily', name: 'Daily', desc: '1 turn per day', icon: <Clock className="w-4 h-4" /> },
  { id: 'weekly', name: 'Weekly', desc: '1 turn per week', icon: <Calendar className="w-4 h-4" /> },
  { id: 'manual', name: 'Manual', desc: 'Click to advance', icon: <Play className="w-4 h-4" /> },
];

const difficulties = [
  { id: 'easy', name: 'Easy', desc: 'Forgiving market', color: 'text-green-400 border-green-500/30 bg-green-500/10' },
  { id: 'medium', name: 'Medium', desc: 'Balanced challenge', color: 'text-amber-400 border-amber-500/30 bg-amber-500/10' },
  { id: 'hard', name: 'Hard', desc: 'Aggressive AI', color: 'text-red-400 border-red-500/30 bg-red-500/10' },
  { id: 'chaos', name: 'Chaos', desc: 'Random events', color: 'text-purple-400 border-purple-500/30 bg-purple-500/10' },
];

export default function GameSetup({ onStart, onBack }: GameSetupProps) {
  const [config, setConfig] = useState<GameConfig>({
    aiModel: 'gemini',
    timeMode: 'manual',
    weeks: 52,
    startingMoney: 10000,
    competitorCount: 3,
    difficulty: 'medium',
  });

  const handleStart = () => {
    onStart(config);
  };

  const updateConfig = <K extends keyof GameConfig>(key: K, value: GameConfig[K]) => {
    setConfig((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="min-h-screen bg-slate-900 text-white">
      {/* Header */}
      <header className="border-b border-slate-800 px-6 py-4">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <button
            onClick={onBack}
            className="flex items-center gap-2 text-slate-400 hover:text-white transition-colors"
          >
            <ChevronLeft className="w-5 h-5" />
            Back
          </button>
          <div className="flex items-center gap-2">
            <span className="text-xl">🧺</span>
            <span className="font-semibold">Game Setup</span>
          </div>
          <div className="w-20" />
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-10">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="space-y-10"
        >
          {/* AI Model Selection */}
          <Section title="AI Competitor Model" icon={<Brain className="w-5 h-5" />}>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              {aiModels.map((model) => (
                <button
                  key={model.id}
                  onClick={() => updateConfig('aiModel', model.id)}
                  className={`p-4 rounded-xl border text-left transition-all ${
                    config.aiModel === model.id
                      ? 'border-emerald-500 bg-emerald-500/10'
                      : 'border-slate-700 hover:border-slate-600 bg-slate-800/50'
                  }`}
                >
                  <div className="text-2xl mb-2">{model.icon}</div>
                  <div className="font-medium">{model.name}</div>
                  <div className="text-xs text-slate-400">{model.provider}</div>
                </button>
              ))}
            </div>
          </Section>

          {/* Time Mode */}
          <Section title="Game Speed" icon={<Clock className="w-5 h-5" />}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {timeModes.map((mode) => (
                <button
                  key={mode.id}
                  onClick={() => updateConfig('timeMode', mode.id as GameConfig['timeMode'])}
                  className={`p-4 rounded-xl border text-center transition-all ${
                    config.timeMode === mode.id
                      ? 'border-emerald-500 bg-emerald-500/10'
                      : 'border-slate-700 hover:border-slate-600 bg-slate-800/50'
                  }`}
                >
                  <div className="flex justify-center mb-2 text-slate-400">{mode.icon}</div>
                  <div className="font-medium text-sm">{mode.name}</div>
                  <div className="text-xs text-slate-500">{mode.desc}</div>
                </button>
              ))}
            </div>
          </Section>

          {/* Game Duration */}
          <Section title="Game Duration" icon={<Calendar className="w-5 h-5" />}>
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <div className="flex justify-between mb-3">
                <span className="text-slate-400">Number of Weeks</span>
                <span className="text-2xl font-bold text-emerald-400">{config.weeks}</span>
              </div>
              <input
                type="range"
                min={12}
                max={104}
                step={4}
                value={config.weeks}
                onChange={(e) => updateConfig('weeks', parseInt(e.target.value))}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-2">
                <span>12 weeks (3 months)</span>
                <span>104 weeks (2 years)</span>
              </div>
            </div>
          </Section>

          {/* Starting Money */}
          <Section title="Starting Capital" icon={<DollarSign className="w-5 h-5" />}>
            <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
              <div className="flex justify-between mb-3">
                <span className="text-slate-400">Starting Balance</span>
                <span className="text-2xl font-bold text-emerald-400">
                  ${config.startingMoney.toLocaleString()}
                </span>
              </div>
              <input
                type="range"
                min={1000}
                max={100000}
                step={1000}
                value={config.startingMoney}
                onChange={(e) => updateConfig('startingMoney', parseInt(e.target.value))}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer accent-emerald-500"
              />
              <div className="flex justify-between text-xs text-slate-500 mt-2">
                <span>$1,000 (Bootstrap)</span>
                <span>$100,000 (Wealthy)</span>
              </div>
            </div>
          </Section>

          {/* Competitors */}
          <Section title="Number of AI Competitors" icon={<Users className="w-5 h-5" />}>
            <div className="flex gap-3">
              {[1, 2, 3, 4, 5].map((n) => (
                <button
                  key={n}
                  onClick={() => updateConfig('competitorCount', n)}
                  className={`flex-1 py-4 rounded-xl border font-bold text-lg transition-all ${
                    config.competitorCount === n
                      ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                      : 'border-slate-700 hover:border-slate-600 bg-slate-800/50 text-slate-400'
                  }`}
                >
                  {n}
                </button>
              ))}
            </div>
          </Section>

          {/* Difficulty */}
          <Section title="Difficulty" icon={<Settings className="w-5 h-5" />}>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {difficulties.map((diff) => (
                <button
                  key={diff.id}
                  onClick={() => updateConfig('difficulty', diff.id as GameConfig['difficulty'])}
                  className={`p-4 rounded-xl border text-center transition-all ${
                    config.difficulty === diff.id
                      ? diff.color
                      : 'border-slate-700 hover:border-slate-600 bg-slate-800/50'
                  }`}
                >
                  <div className="font-semibold">{diff.name}</div>
                  <div className="text-xs text-slate-400">{diff.desc}</div>
                </button>
              ))}
            </div>
          </Section>

          {/* Start Button */}
          <div className="pt-6">
            <button
              onClick={handleStart}
              className="w-full py-5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-500 font-bold text-lg shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all hover:scale-[1.02] flex items-center justify-center gap-3"
            >
              <Play className="w-6 h-6" />
              Start Game
            </button>
          </div>
        </motion.div>
      </main>
    </div>
  );
}

// ─── Section Component ──────────────────────────────────────────────────
function Section({
  title,
  icon,
  children,
}: {
  title: string;
  icon: React.ReactNode;
  children: React.ReactNode;
}) {
  return (
    <div>
      <h3 className="flex items-center gap-2 text-lg font-semibold mb-4">
        <span className="text-emerald-400">{icon}</span>
        {title}
      </h3>
      {children}
    </div>
  );
}
