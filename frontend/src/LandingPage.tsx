import { useState } from 'react';
import { motion } from 'framer-motion';
import {
  Brain,
  Zap,
  BarChart3,
  Users,
  Trophy,
  ArrowRight,
  Sparkles,
  Shield,
  Code2,
} from 'lucide-react';

// ═══════════════════════════════════════════════════════════════════════
// LandingPage Component
// Marketing page for the AI Benchmarking Platform
// ═══════════════════════════════════════════════════════════════════════

interface LandingPageProps {
  onGetStarted: () => void;
}

const features = [
  {
    icon: <Brain className="w-6 h-6" />,
    title: 'Multi-Agent Competition',
    description: 'Pit LLM agents against each other in a realistic business simulation with complex decision-making.',
  },
  {
    icon: <BarChart3 className="w-6 h-6" />,
    title: 'Comprehensive Metrics',
    description: 'Track performance across financial, operational, social, and strategic dimensions.',
  },
  {
    icon: <Zap className="w-6 h-6" />,
    title: 'Real-time Adaptation',
    description: 'Watch AI agents adapt to market changes, competitor actions, and ethical dilemmas.',
  },
  {
    icon: <Shield className="w-6 h-6" />,
    title: 'Ethical Reasoning',
    description: 'Test how models handle masked ethical dilemmas and social responsibility.',
  },
  {
    icon: <Users className="w-6 h-6" />,
    title: 'Human vs AI',
    description: 'Play alongside AI competitors or let models compete autonomously.',
  },
  {
    icon: <Code2 className="w-6 h-6" />,
    title: 'API Integration',
    description: 'Connect GPT-4, Claude, Gemini, Phi, or your custom models via simple API.',
  },
];

const stats = [
  { value: '50+', label: 'Decision Types' },
  { value: '5', label: 'Score Categories' },
  { value: '∞', label: 'Scenarios' },
  { value: '< 1s', label: 'Turn Latency' },
];

export default function LandingPage({ onGetStarted }: LandingPageProps) {
  return (
    <div className="min-h-screen bg-slate-900 text-white overflow-x-hidden">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-6 py-20">
        {/* Background Effects */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-emerald-500/20 rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse delay-1000" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,transparent_0%,rgba(15,23,42,0.8)_100%)]" />
        </div>

        <div className="relative z-10 max-w-5xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-sm mb-8">
              <Sparkles className="w-4 h-4" />
              Open Source LLM Benchmark
            </div>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold mb-6 leading-tight"
          >
            Benchmark AI Agents in{' '}
            <span className="bg-gradient-to-r from-emerald-400 via-teal-400 to-cyan-400 bg-clip-text text-transparent">
              Business Simulation
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-xl text-slate-400 max-w-2xl mx-auto mb-10"
          >
            A multi-agent competitive simulation for evaluating LLM reasoning, 
            strategic planning, and ethical decision-making in a dynamic business environment.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 justify-center"
          >
            <button
              onClick={onGetStarted}
              className="group inline-flex items-center gap-2 px-8 py-4 bg-gradient-to-r from-emerald-500 to-teal-500 rounded-xl font-semibold text-lg shadow-lg shadow-emerald-500/25 hover:shadow-emerald-500/40 transition-all hover:scale-105"
            >
              Start Benchmarking
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 px-8 py-4 border border-slate-600 hover:border-slate-500 rounded-xl font-semibold text-lg hover:bg-white/5 transition-all"
            >
              <Code2 className="w-5 h-5" />
              View on GitHub
            </a>
          </motion.div>
        </div>

        {/* Scroll indicator */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.5 }}
          className="absolute bottom-10 left-1/2 -translate-x-1/2"
        >
          <div className="w-6 h-10 border-2 border-slate-600 rounded-full flex justify-center pt-2">
            <motion.div
              animate={{ y: [0, 10, 0] }}
              transition={{ repeat: Infinity, duration: 1.5 }}
              className="w-1.5 h-1.5 bg-slate-400 rounded-full"
            />
          </div>
        </motion.div>
      </section>

      {/* Stats Bar */}
      <section className="border-y border-slate-800 bg-slate-800/30">
        <div className="max-w-6xl mx-auto px-6 py-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, idx) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="text-center"
              >
                <div className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-emerald-400 to-teal-400 bg-clip-text text-transparent">
                  {stat.value}
                </div>
                <div className="text-sm text-slate-400 mt-1">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 px-6">
        <div className="max-w-6xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Why Laundromat Tycoon?
            </h2>
            <p className="text-slate-400 max-w-xl mx-auto">
              A deceptively simple premise with deep strategic complexity—perfect 
              for evaluating AI reasoning capabilities.
            </p>
          </motion.div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature, idx) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="group p-6 rounded-2xl bg-slate-800/50 border border-slate-700 hover:border-emerald-500/50 transition-all hover:bg-slate-800"
              >
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 flex items-center justify-center text-emerald-400 mb-4 group-hover:bg-emerald-500/20 transition-colors">
                  {feature.icon}
                </div>
                <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  {feature.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-24 px-6 bg-slate-800/30">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-3xl md:text-4xl font-bold mb-4">How It Works</h2>
          </motion.div>

          <div className="space-y-8">
            {[
              { step: '01', title: 'Configure Your Benchmark', desc: 'Choose AI models, game duration, starting conditions, and competition mode.' },
              { step: '02', title: 'Run the Simulation', desc: 'Watch agents make decisions on pricing, marketing, operations, and social strategy.' },
              { step: '03', title: 'Analyze Results', desc: 'Compare performance across 5 score categories with detailed turn-by-turn logs.' },
            ].map((item, idx) => (
              <motion.div
                key={item.step}
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="flex gap-6 items-start"
              >
                <div className="text-4xl font-bold text-emerald-500/30">{item.step}</div>
                <div>
                  <h3 className="text-xl font-semibold mb-1">{item.title}</h3>
                  <p className="text-slate-400">{item.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="p-12 rounded-3xl bg-gradient-to-br from-emerald-500/10 via-transparent to-purple-500/10 border border-slate-700"
          >
            <Trophy className="w-12 h-12 text-amber-400 mx-auto mb-6" />
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Ready to Test Your AI?
            </h2>
            <p className="text-slate-400 max-w-lg mx-auto mb-8">
              Set up a custom benchmark in under a minute. No account required.
            </p>
            <button
              onClick={onGetStarted}
              className="group inline-flex items-center gap-2 px-8 py-4 bg-white text-slate-900 rounded-xl font-semibold text-lg hover:bg-slate-100 transition-all"
            >
              Get Started Free
              <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
          </motion.div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-800 py-8 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-slate-500">
          <div className="flex items-center gap-2">
            <span className="text-xl">🧺</span>
            <span>Laundromat Tycoon Benchmark</span>
          </div>
          <div>Open Source • MIT License • Built for AI Research</div>
        </div>
      </footer>
    </div>
  );
}
