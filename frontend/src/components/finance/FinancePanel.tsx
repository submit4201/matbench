import { useEffect } from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  CreditCard,
  FileText,
  Building2,
  PiggyBank,
} from 'lucide-react';
import { useGameStore } from '../../stores/gameStore';
import { Card, StatCard, TabGroup, TabContent, Button } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// FinancePanel Component
// Financial suite with bank, bills, taxes
// ═══════════════════════════════════════════════════════════════════════

const tabs = [
  { id: 'overview', label: 'Overview', icon: <TrendingUp className="w-4 h-4" /> },
  { id: 'bank', label: 'Bank', icon: <Building2 className="w-4 h-4" /> },
  { id: 'bills', label: 'Bills', icon: <FileText className="w-4 h-4" /> },
  { id: 'credit', label: 'Credit', icon: <CreditCard className="w-4 h-4" /> },
];

export default function FinancePanel() {
  const { getPlayerLaundromat, creditReport, fetchCreditReport, gameState } = useGameStore();
  const laundromat = getPlayerLaundromat();

  useEffect(() => {
    fetchCreditReport();
  }, [fetchCreditReport, gameState?.week]);

  if (!laundromat) {
    return (
      <Card variant="glass" className="text-center py-12">
        <p className="text-slate-400">No financial data available.</p>
      </Card>
    );
  }

  // Format currency
  const formatCurrency = (amount: number) =>
    new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
    }).format(amount);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          label="Balance"
          value={formatCurrency(laundromat.balance)}
          icon={<DollarSign className="w-5 h-5" />}
        />
        <StatCard
          label="Credit Score"
          value={creditReport?.credit_score ?? '—'}
          icon={<CreditCard className="w-5 h-5" />}
        />
        <StatCard
          label="Total Debt"
          value={creditReport ? formatCurrency(creditReport.total_debt) : '—'}
          icon={<TrendingDown className="w-5 h-5" />}
        />
        <StatCard
          label="Active Loans"
          value={creditReport?.active_loans?.length ?? 0}
          icon={<PiggyBank className="w-5 h-5" />}
        />
      </div>

      {/* Tabbed Content */}
      <TabGroup tabs={tabs} defaultValue="overview">
        {/* Overview Tab */}
        <TabContent value="overview">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card variant="glass">
              <h3 className="text-sm font-medium text-slate-400 mb-4">Revenue Sources</h3>
              <div className="space-y-3">
                {laundromat.revenue_streams ? (
                  Object.entries(laundromat.revenue_streams)
                    .filter(([, stream]) => stream.unlocked)
                    .map(([key, stream]) => (
                      <div
                        key={key}
                        className="flex items-center justify-between p-2 rounded-lg bg-white/5"
                      >
                        <span className="text-sm text-white">{stream.name}</span>
                        <span className="text-emerald-400 font-medium">
                          {formatCurrency(stream.weekly_revenue ?? 0)}/wk
                        </span>
                      </div>
                    ))
                ) : (
                  <p className="text-slate-500 text-sm">No revenue streams active.</p>
                )}
              </div>
            </Card>

            <Card variant="glass">
              <h3 className="text-sm font-medium text-slate-400 mb-4">Weekly Expenses</h3>
              <div className="space-y-3">
                <div className="flex items-center justify-between p-2 rounded-lg bg-white/5">
                  <span className="text-sm text-slate-300">Staff Payroll</span>
                  <span className="text-red-400">
                    -{formatCurrency((laundromat.staff?.length ?? 0) * 300)}
                  </span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-white/5">
                  <span className="text-sm text-slate-300">Utilities</span>
                  <span className="text-red-400">-{formatCurrency(150)}</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded-lg bg-white/5">
                  <span className="text-sm text-slate-300">Supplies</span>
                  <span className="text-red-400">-{formatCurrency(50)}</span>
                </div>
              </div>
            </Card>
          </div>
        </TabContent>

        {/* Bank Tab */}
        <TabContent value="bank">
          <Card variant="glass">
            <h3 className="text-lg font-semibold text-white mb-4">Bank Services</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-gradient-to-r from-blue-500/10 to-indigo-500/10 border border-blue-500/20">
                <h4 className="font-medium text-white mb-2">Business Loan</h4>
                <p className="text-sm text-slate-400 mb-4">
                  Borrow up to $50,000 at competitive rates
                </p>
                <Button variant="secondary" size="sm">
                  Apply Now
                </Button>
              </div>
              <div className="p-4 rounded-lg bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20">
                <h4 className="font-medium text-white mb-2">Equipment Financing</h4>
                <p className="text-sm text-slate-400 mb-4">
                  Finance new machines with 0% down
                </p>
                <Button variant="secondary" size="sm">
                  Learn More
                </Button>
              </div>
            </div>
          </Card>
        </TabContent>

        {/* Bills Tab */}
        <TabContent value="bills">
          <Card variant="glass">
            <h3 className="text-lg font-semibold text-white mb-4">Upcoming Bills</h3>
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border-l-4 border-amber-500">
                <div>
                  <p className="text-white font-medium">Monthly Rent</p>
                  <p className="text-xs text-slate-400">Due: Week {(gameState?.week ?? 0) + 2}</p>
                </div>
                <span className="text-lg font-bold text-white">{formatCurrency(2000)}</span>
              </div>
              {creditReport?.next_payment && (
                <div className="flex items-center justify-between p-3 rounded-lg bg-white/5 border-l-4 border-blue-500">
                  <div>
                    <p className="text-white font-medium">Loan Payment</p>
                    <p className="text-xs text-slate-400">
                      Due: Week {creditReport.next_payment.due_week}
                    </p>
                  </div>
                  <span className="text-lg font-bold text-white">
                    {formatCurrency(creditReport.next_payment.amount)}
                  </span>
                </div>
              )}
            </div>
          </Card>
        </TabContent>

        {/* Credit Tab */}
        <TabContent value="credit">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <Card variant="glow">
              <h3 className="text-lg font-semibold text-white mb-2">Credit Score</h3>
              <div className="flex items-baseline gap-2 mb-4">
                <span className="text-4xl font-bold text-emerald-400">
                  {creditReport?.credit_score ?? '—'}
                </span>
                <span className="text-slate-400 capitalize">{creditReport?.rating ?? ''}</span>
              </div>
              <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-red-500 via-amber-500 to-emerald-500"
                  style={{ width: `${((creditReport?.credit_score ?? 0) / 850) * 100}%` }}
                />
              </div>
            </Card>

            <Card variant="glass">
              <h3 className="text-lg font-semibold text-white mb-4">Active Loans</h3>
              {creditReport?.active_loans && creditReport.active_loans.length > 0 ? (
                <div className="space-y-3">
                  {creditReport.active_loans.map((loan) => (
                    <div key={loan.loan_id} className="p-3 rounded-lg bg-white/5">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-white">{loan.loan_type}</span>
                        <span className="text-emerald-400">
                          {formatCurrency(loan.remaining_balance)}
                        </span>
                      </div>
                      <div className="text-xs text-slate-400">
                        {(loan.interest_rate * 100).toFixed(1)}% APR • {formatCurrency(loan.weekly_payment)}/wk
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500 text-sm">No active loans.</p>
              )}
            </Card>
          </div>
        </TabContent>
      </TabGroup>
    </div>
  );
}
