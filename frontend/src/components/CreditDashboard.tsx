/**
 * CreditDashboard.tsx - Premium Credit Score & Loan Management UI
 * 
 * A stunning glassmorphic credit dashboard featuring:
 * - Animated credit score gauge with gradient ring
 * - Loan progress bars with shimmer effects
 * - Payment history timeline
 * - Interactive payment actions
 */

import { useState, useEffect } from 'react';
import type { CreditReport, LoanInfo, PaymentRecord } from '../types';

// Credit rating color mapping
const RATING_COLORS = {
  excellent: { bg: 'from-emerald-500 to-green-400', text: 'text-emerald-400', glow: 'shadow-emerald-500/30' },
  good: { bg: 'from-blue-500 to-cyan-400', text: 'text-blue-400', glow: 'shadow-blue-500/30' },
  fair: { bg: 'from-yellow-500 to-amber-400', text: 'text-yellow-400', glow: 'shadow-yellow-500/30' },
  poor: { bg: 'from-orange-500 to-red-400', text: 'text-orange-400', glow: 'shadow-orange-500/30' },
  very_poor: { bg: 'from-red-600 to-rose-500', text: 'text-red-400', glow: 'shadow-red-500/30' },
};

interface CreditDashboardProps {
  agentId?: string;
  onPayment?: (paymentId: string, amount: number) => void;
}

export function CreditDashboard({ agentId = 'p1', onPayment }: CreditDashboardProps) {
  const [credit, setCredit] = useState<CreditReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [selectedLoan, setSelectedLoan] = useState<string | null>(null);

  useEffect(() => {
    fetchCreditReport();
  }, [agentId]);

  const fetchCreditReport = async () => {
    try {
      const res = await fetch(`http://localhost:8000/credit/${agentId}`);
      const data = await res.json();
      setCredit(data.credit);
    } catch (err) {
      console.error('Failed to fetch credit report:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async (paymentId: string, amount: number) => {
    try {
      await fetch(`http://localhost:8000/credit/${agentId}/payment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ payment_id: paymentId, amount })
      });
      onPayment?.(paymentId, amount);
      fetchCreditReport();
    } catch (err) {
      console.error('Payment failed:', err);
    }
  };

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 animate-pulse">
        <div className="h-48 bg-slate-700/50 rounded-xl"></div>
      </div>
    );
  }

  if (!credit) {
    return (
      <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 text-center text-gray-400">
        No credit data available
      </div>
    );
  }

  const rating = credit.rating || 'fair';
  const colors = RATING_COLORS[rating];
  const scorePercent = Math.min(100, Math.max(0, (credit.credit_score - 300) / 550 * 100));

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl overflow-hidden">
      {/* Header with Glow */}
      <div className={`relative bg-gradient-to-r ${colors.bg} p-1`}>
        <div className="bg-slate-900 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className={`w-10 h-10 rounded-full bg-gradient-to-r ${colors.bg} flex items-center justify-center shadow-lg ${colors.glow}`}>
                <span className="text-xl">🏦</span>
              </div>
              <div>
                <h2 className="text-xl font-bold text-white">Financial Hub</h2>
                <p className="text-sm text-gray-400">Banking, Bills & Credit</p>
              </div>
            </div>
            <div className={`px-4 py-1.5 rounded-full bg-gradient-to-r ${colors.bg} text-white text-sm font-semibold uppercase tracking-wide shadow-lg ${colors.glow}`}>
              {rating.replace('_', ' ')}
            </div>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        {/* Credit Score Gauge */}
        <div className="flex items-center justify-center">
          <div className="relative w-48 h-48 group cursor-default">
            {/* Background Ring */}
            <svg className="w-full h-full -rotate-90" viewBox="0 0 100 100">
              <circle
                cx="50" cy="50" r="42"
                fill="none"
                stroke="rgba(100,116,139,0.3)"
                strokeWidth="8"
              />
              {/* Score Ring with Gradient */}
              <circle
                cx="50" cy="50" r="42"
                fill="none"
                stroke="url(#scoreGradient)"
                strokeWidth="8"
                strokeLinecap="round"
                strokeDasharray={`${scorePercent * 2.64} 264`}
                className="transition-all duration-1000 ease-out drop-shadow-[0_0_10px_rgba(16,185,129,0.5)]"
              />
              <defs>
                <linearGradient id="scoreGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#10b981" />
                  <stop offset="50%" stopColor="#3b82f6" />
                  <stop offset="100%" stopColor="#8b5cf6" />
                </linearGradient>
              </defs>
            </svg>
            {/* Center Content */}
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className={`text-5xl font-black ${colors.text} animate-pulse drop-shadow-lg`}>
                {credit.credit_score}
              </span>
              <span className="text-sm text-gray-400 mt-1 font-medium">FICO Score</span>
            </div>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4 text-center border border-slate-700/50 hover:bg-slate-800 transition-colors">
            <div className="text-2xl font-bold text-rose-400">${credit.total_debt?.toLocaleString() || 0}</div>
            <div className="text-xs text-gray-400 mt-1 uppercase tracking-wider">Total Debt</div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4 text-center border border-slate-700/50 hover:bg-slate-800 transition-colors">
            <div className="text-2xl font-bold text-amber-400">{credit.active_loans?.length || 0}</div>
            <div className="text-xs text-gray-400 mt-1 uppercase tracking-wider">Active Loans</div>
          </div>
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-4 text-center border border-slate-700/50 hover:bg-slate-800 transition-colors">
            <div className="text-2xl font-bold text-emerald-400">
              ${credit.next_payment?.amount?.toFixed(0) || 0}
            </div>
            <div className="text-xs text-gray-400 mt-1 uppercase tracking-wider">Next Payment</div>
          </div>
        </div>

        {/* Pending Bills Section */}
        <div className="space-y-3">
            <h3 className="text-sm font-bold text-gray-300 uppercase tracking-wide flex items-center gap-2">
              <span>🧾</span> Bills & Payments
            </h3>
            
            {/* Filter pending vs history */}
            {(() => {
                const pending = credit.payment_history?.filter(p => p.status === 'pending') || [];
                const history = credit.payment_history?.filter(p => p.status !== 'pending') || [];
                
                return (
                    <div className="space-y-4">
                        {/* Pending Items */}
                        {pending.length > 0 ? (
                           <div className="bg-slate-800/80 rounded-xl border border-indigo-500/30 overflow-hidden">
                             {pending.map((payment) => (
                                <div key={payment.payment_id} className="p-4 flex items-center justify-between border-b border-indigo-500/10 last:border-0 hover:bg-slate-700/50 transition-colors">
                                    <div className="flex items-center gap-3">
                                        <div className="w-10 h-10 rounded-full bg-rose-500/20 flex items-center justify-center text-rose-400 animate-pulse">
                                            ⚠️
                                        </div>
                                        <div>
                                            <div className="font-bold text-white">{payment.description || 'Bill Payment'}</div>
                                            <div className="text-xs text-rose-300">Due: Week {payment.due_week}</div>
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-3">
                                        <div className="font-mono font-bold text-white text-lg">${payment.amount.toFixed(2)}</div>
                                        <button
                                          onClick={() => handlePayment(payment.payment_id, payment.amount)}
                                          className="px-4 py-2 bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white text-xs font-bold rounded-lg shadow-lg shadow-emerald-500/20 transform hover:scale-105 active:scale-95 transition-all"
                                        >
                                          PAY NOW
                                        </button>
                                    </div>
                                </div>
                             ))}
                           </div>
                        ) : (
                            <div className="bg-slate-800/30 rounded-xl p-6 text-center border border-slate-700/50 border-dashed">
                                <div className="w-12 h-12 bg-emerald-500/10 rounded-full flex items-center justify-center mx-auto mb-2">
                                    <span className="text-2xl">✅</span>
                                </div>
                                <p className="text-slate-400 font-medium">All bills paid</p>
                                <p className="text-xs text-slate-500">No pending payments for this week</p>
                            </div>
                        )}

                        {/* Recent History */}
                        {history.length > 0 && (
                            <div className="space-y-2 opacity-80">
                                <div className="text-xs font-bold text-gray-500 uppercase">Recent Activity</div>
                                <div className="bg-slate-800/30 rounded-xl p-1 overflow-hidden">
                                    {history.slice(0, 3).map((payment, idx) => (
                                        <div key={payment.payment_id || idx} className="flex justify-between items-center p-3 hover:bg-slate-700/30 rounded-lg transition-colors">
                                            <div className="flex items-center gap-3">
                                                 <div className={`text-lg ${payment.status === 'paid' ? 'opacity-100' : 'opacity-50'}`}>
                                                    {payment.status === 'paid' ? '✅' : payment.status === 'missed' ? '❌' : '⏳'}
                                                 </div>
                                                 <div className="text-sm text-slate-300">
                                                    {payment.description || `Payment (Week ${payment.due_week})`}
                                                 </div>
                                            </div>
                                            <div className="font-mono text-sm text-slate-400">
                                                ${payment.amount.toFixed(2)}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                );
            })()}
        </div>

        {/* Active Loans */}
        {credit.active_loans && credit.active_loans.length > 0 && (
          <div className="space-y-3 pt-4 border-t border-slate-700/50">
            <h3 className="text-sm font-semibold text-gray-300 uppercase tracking-wide flex items-center gap-2">
              <span>💼</span> Active Financing
            </h3>
            {credit.active_loans.map((loan: LoanInfo) => (
              <LoanCard
                key={loan.loan_id}
                loan={loan}
                isExpanded={selectedLoan === loan.loan_id}
                onToggle={() => setSelectedLoan(selectedLoan === loan.loan_id ? null : loan.loan_id)}
              />
            ))}
          </div>
        )}
      </div>

    </div>
  );
}

// Loan Card Sub-component
function LoanCard({ loan, isExpanded, onToggle }: { 
  loan: LoanInfo; 
  isExpanded: boolean;
  onToggle: () => void;
}) {
  const progressPercent = ((loan.principal - loan.remaining_balance) / loan.principal) * 100;

  return (
    <div 
      className={`bg-slate-800/50 backdrop-blur rounded-xl border transition-all duration-300 cursor-pointer
        ${isExpanded ? 'border-blue-500/50 shadow-lg shadow-blue-500/10' : 'border-slate-700/50 hover:border-slate-600/50'}`}
      onClick={onToggle}
    >
      <div className="p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-gradient-to-r from-blue-500 to-purple-500 flex items-center justify-center">
              <span className="text-lg">🏦</span>
            </div>
            <div>
              <div className="font-semibold text-white">{loan.loan_type || 'SBA Loan'}</div>
              <div className="text-xs text-gray-400">Started Week {loan.start_week}</div>
            </div>
          </div>
          <div className="text-right">
            <div className="text-lg font-bold text-white">${loan.remaining_balance?.toLocaleString()}</div>
            <div className="text-xs text-gray-400">remaining</div>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="relative h-3 bg-slate-700/50 rounded-full overflow-hidden">
          <div 
            className="absolute left-0 top-0 h-full bg-gradient-to-r from-blue-500 to-purple-500 rounded-full transition-all duration-500"
            style={{ width: `${progressPercent}%` }}
          />
          {/* Shimmer Effect */}
          <div className="absolute inset-0 animate-shimmer opacity-30" />
        </div>
        
        <div className="flex justify-between mt-2 text-xs text-gray-400">
          <span>{progressPercent.toFixed(0)}% paid</span>
          <span>${loan.weekly_payment?.toFixed(2)}/week</span>
        </div>
      </div>

      {/* Expanded Details */}
      {isExpanded && (
        <div className="border-t border-slate-700/50 p-4 bg-slate-900/50 space-y-2 animate-fade-in">
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-400">Principal:</span>
              <span className="text-white ml-2">${loan.principal?.toLocaleString()}</span>
            </div>
            <div>
              <span className="text-gray-400">Interest Rate:</span>
              <span className="text-white ml-2">{(loan.interest_rate * 100).toFixed(1)}%</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default CreditDashboard;
