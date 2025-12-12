import { useEffect, useState } from 'react';
import {
  DollarSign,
  TrendingUp,
  TrendingDown,
  CreditCard,
  FileText,
  Building2,
  PiggyBank,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend
} from 'recharts';
import { toast } from 'sonner';
import { useGameStore } from '../../stores/gameStore';
import { Card, StatCard, TabGroup, TabContent, Button } from '../shared';

// ═══════════════════════════════════════════════════════════════════════
// FinancePanel Component
// Financial suite with bank, bills, taxes
// ═══════════════════════════════════════════════════════════════════════

const tabs = [
  { id: 'overview', label: 'Overview', icon: <TrendingUp className="w-4 h-4" /> },
  { id: 'pnl', label: 'P&L', icon: <FileText className="w-4 h-4" /> },
  { id: 'bank', label: 'Bank', icon: <Building2 className="w-4 h-4" /> },
  { id: 'bills', label: 'Bills', icon: <DollarSign className="w-4 h-4" /> },
  { id: 'credit', label: 'Credit', icon: <CreditCard className="w-4 h-4" /> },
];

export default function FinancePanel() {
  const { getPlayerLaundromat, creditReport, fetchCreditReport, gameState, sendAction, isLoading } = useGameStore();
  const laundromat = getPlayerLaundromat();

  // Local state for loan application
  const [loanAmount, setLoanAmount] = useState(5000);

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

  // ! Loan application handler with detailed feedback
  const handleApplyForLoan = async (loanType: string, amount: number) => {
    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/action`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agent_id: 'p1',
          action_type: 'APPLY_FOR_LOAN',
          parameters: { loan_type: loanType, amount: amount }
        })
      });

      if (!response.ok) {
        toast.error('Loan application failed');
        return;
      }

      toast.success(`Loan application submitted for ${formatCurrency(amount)}!\nCheck your messages for approval status.`);

      // Refresh credit report
      await fetchCreditReport();
    } catch (err) {
      toast.error('Failed to apply for loan');
    }
  };

  // ! Bill payment handler
  const handlePayBill = async (billId: string, amount: number) => {
    const success = await sendAction('MAKE_PAYMENT', { payment_id: billId, amount: amount });
    if (success) toast.success(`Paid bill: ${formatCurrency(amount)}`);
  };

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

          {/* Financial Chart */}
          <Card variant="glass" className="mb-4">
            <h3 className="text-sm font-medium text-slate-400 mb-4">Financial Trends</h3>
            <div className="h-64 w-full">
              {laundromat.financial_reports && laundromat.financial_reports.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={laundromat.financial_reports}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                    <XAxis
                      dataKey="week"
                      stroke="#94a3b8"
                      tick={{ fontSize: 12 }}
                      tickFormatter={(val) => `W${val}`}
                    />
                    <YAxis
                      stroke="#94a3b8"
                      tick={{ fontSize: 12 }}
                      tickFormatter={(val) => `$${val}`}
                    />
                    <Tooltip
                      contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#f8fafc' }}
                      formatter={(val: number) => [`$${val}`, '']}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="total_revenue" name="Revenue" stroke="#10b981" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="total_operating_expenses" name="Expenses" stroke="#ef4444" strokeWidth={2} dot={false} />
                    <Line type="monotone" dataKey="net_income" name="Net Income" stroke="#3b82f6" strokeWidth={2} dot={false} />
                  </LineChart>
                </ResponsiveContainer>
              ) : (
                <div className="flex items-center justify-center h-full text-slate-500">
                  Not enough data for financial reports.
                </div>
              )}
            </div>
          </Card>

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

        {/* P&L Tab */}
        <TabContent value="pnl">
          <Card variant="glass">
            <h3 className="text-lg font-semibold text-white mb-4">Profit & Loss Statement</h3>
            {laundromat.financial_reports && laundromat.financial_reports.length > 0 ? (
              (() => {
                const report = laundromat.financial_reports[laundromat.financial_reports.length - 1];

                // Calculate aggregated values from report fields
                const serviceRevenue = (report.revenue_wash || 0) + (report.revenue_dry || 0) + (report.revenue_premium || 0) + (report.revenue_membership || 0) + (report.revenue_other || 0);
                const vendingRevenue = (report.revenue_vending || 0);

                const Row = ({ label, value, intent = 'neutral', indent = false, bold = false }: any) => (
                  <div className={`flex justify-between items-center py-2 border-b border-slate-700/50 ${bold ? 'font-bold' : ''}`}>
                    <span className={`${indent ? 'pl-4 text-slate-400' : 'text-slate-200'}`}>{label}</span>
                    <span className={`${intent === 'positive' ? 'text-emerald-400' : intent === 'negative' ? 'text-red-400' : 'text-white'}`}>
                      {value < 0 ? '-' : ''}{formatCurrency(Math.abs(value))}
                    </span>
                  </div>
                );

                return (
                  <div className="space-y-1">
                    <div className="text-xs text-slate-500 mb-2 uppercase tracking-wide">Revenue</div>
                    <Row label="Total Revenue" value={report.total_revenue} intent="neutral" bold />
                    <Row label="Service Revenue" value={serviceRevenue} indent />
                    <Row label="Vending Revenue" value={vendingRevenue} indent />

                    <div className="text-xs text-slate-500 mt-6 mb-2 uppercase tracking-wide">Cost of Goods Sold</div>
                    <Row label="Supplies" value={-report.cogs_supplies} intent="negative" indent />
                    <Row label="Vending Cost" value={-report.cogs_vending} intent="negative" indent />
                    <Row label="Gross Profit" value={report.gross_profit} intent="positive" bold />

                    <div className="text-xs text-slate-500 mt-6 mb-2 uppercase tracking-wide">Operating Expenses</div>
                    <Row label="Rent" value={-report.expense_rent} intent="negative" indent />
                    <Row label="Utilities" value={-report.expense_utilities} intent="negative" indent />
                    <Row label="Labor" value={-report.expense_labor} intent="negative" indent />
                    <Row label="Maintenance" value={-report.expense_maintenance} intent="negative" indent />
                    <Row label="Insurance & Other" value={-(report.expense_insurance + report.expense_other)} intent="negative" indent />
                    <Row label="Total Operating Expenses" value={-report.total_operating_expenses} intent="negative" bold />

                    <div className="text-xs text-slate-500 mt-6 mb-2 uppercase tracking-wide">Net Income</div>
                    <Row label="Operating Income" value={report.operating_income} intent={report.operating_income >= 0 ? 'positive' : 'negative'} />
                    <Row label="Interest Expense" value={-report.expense_interest} intent="negative" indent />
                    <Row label="Taxes" value={-report.tax_provision} intent="negative" indent />
                    <div className="pt-2 mt-2 border-t border-slate-600">
                      <Row label="Net Profit / (Loss)" value={report.net_income} intent={report.net_income >= 0 ? 'positive' : 'negative'} bold />
                    </div>
                  </div>
                );
              })()
            ) : (
              <p className="text-slate-500 text-center py-8">
                No financial reports available yet for P&L analysis.
                <br />
                <span className="text-xs">Complete one full week of operations to generate a report.</span>
              </p>
            )}
          </Card>
        </TabContent>

        {/* Bank Tab */}
        <TabContent value="bank">
          <Card variant="glass">
            <h3 className="text-lg font-semibold text-white mb-4">Bank Services</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-gradient-to-r from-blue-500/10 to-indigo-500/10 border border-blue-500/20">
                <h4 className="font-medium text-white mb-2">Equipment Loan</h4>
                <p className="text-sm text-slate-400 mb-3">
                  Finance machines and equipment. Up to $10,000.
                </p>
                <div className="flex items-center gap-2 mb-3">
                  <input
                    type="number"
                    min="1000"
                    max="10000"
                    step="500"
                    value={loanAmount}
                    onChange={(e) => setLoanAmount(parseInt(e.target.value) || 1000)}
                    className="w-24 px-2 py-1 text-sm rounded bg-slate-800 border border-slate-600 text-white"
                  />
                  <span className="text-xs text-slate-400">Amount</span>
                </div>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleApplyForLoan('equipment_loan', loanAmount)}
                  loading={isLoading}
                >
                  Apply Now
                </Button>
              </div>
              <div className="p-4 rounded-lg bg-gradient-to-r from-emerald-500/10 to-teal-500/10 border border-emerald-500/20">
                <h4 className="font-medium text-white mb-2">Operating Credit Line</h4>
                <p className="text-sm text-slate-400 mb-3">
                  Short-term credit for day-to-day operations. Up to $5,000.
                </p>
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={() => handleApplyForLoan('operating_credit', 2500)}
                  loading={isLoading}
                >
                  Apply for $2,500
                </Button>
              </div>
            </div>
          </Card>
        </TabContent>

        {/* Bills Tab */}
        <TabContent value="bills">
          <Card variant="glass">
            <h3 className="text-lg font-semibold text-white mb-4">Bills & Payments</h3>
            <div className="space-y-3">
              {/* Display actual bills from laundromat state */}
              {laundromat.bills && laundromat.bills.length > 0 ? (
                laundromat.bills
                  .filter((bill) => !bill.is_paid)
                  .map((bill) => {
                    // Color-code by category
                    const borderColor =
                      bill.category === 'tax' ? 'border-red-500' :
                        bill.category === 'loan_repayment' ? 'border-blue-500' :
                          bill.category === 'rent' ? 'border-amber-500' :
                            'border-slate-500';

                    const isOverdue = (gameState?.week ?? 0) > bill.due_week;

                    return (
                      <div
                        key={bill.id}
                        className={`flex items-center justify-between p-3 rounded-lg bg-white/5 border-l-4 ${borderColor}`}
                      >
                        <div className="flex-1">
                          <p className="text-white font-medium">
                            {bill.name}
                            {isOverdue && <span className="text-red-400 text-xs ml-2">OVERDUE</span>}
                            {bill.penalty_applied && <span className="text-red-400 text-xs ml-2">+Penalty</span>}
                          </p>
                          <p className="text-xs text-slate-400">
                            Due: Week {bill.due_week} • {bill.category.replace(/_/g, ' ')}
                          </p>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className={`text-lg font-bold ${isOverdue ? 'text-red-400' : 'text-white'}`}>
                            {formatCurrency(bill.amount)}
                          </span>
                          <Button
                            variant={isOverdue ? "danger" : "primary"}
                            size="sm"
                            onClick={() => handlePayBill(bill.id, bill.amount)}
                            loading={isLoading}
                            disabled={laundromat.balance < bill.amount}
                          >
                            Pay
                          </Button>
                        </div>
                      </div>
                    );
                  })
              ) : (
                <p className="text-slate-500 text-sm">No bills due at this time.</p>
              )}

              {/* Show paid bills count */}
              {laundromat.bills && laundromat.bills.filter(b => b.is_paid).length > 0 && (
                <p className="text-xs text-slate-500 mt-4">
                  {laundromat.bills.filter(b => b.is_paid).length} bill(s) paid this period
                </p>
              )}
            </div>
          </Card>

          {/* Tax Summary */}
          <Card variant="glass" className="mt-4">
            <h4 className="text-sm font-medium text-slate-400 mb-3">Tax Information</h4>
            <div className="grid grid-cols-2 gap-4 text-sm">
              <div>
                <span className="text-slate-500">Tax Rate</span>
                <p className="text-white font-medium">8%</p>
              </div>
              <div>
                <span className="text-slate-500">Next Tax Due</span>
                <p className="text-white font-medium">
                  Week {[6, 12, 18, 24].find(w => w > (gameState?.week ?? 0)) ?? 'N/A'}
                </p>
              </div>
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
                  {creditReport.active_loans.map((account: any) => (
                    <div key={account.id} className="p-3 rounded-lg bg-white/5">
                      <div className="flex justify-between mb-1">
                        <span className="text-sm text-white capitalize">{account.type.replace(/_/g, ' ')}</span>
                        <span className="text-emerald-400">
                          {formatCurrency(account.current_balance)}
                          <span className="text-slate-500 text-xs ml-1">
                            / {formatCurrency(account.original_amount)}
                          </span>
                        </span>
                      </div>
                      <div className="text-xs text-slate-400">
                        {(account.interest_rate * 100).toFixed(1)}% rate • {formatCurrency(account.weekly_payment)}/wk
                        {account.is_defaulted && <span className="text-red-400 ml-2">⚠ Defaulted</span>}
                      </div>
                      {/* Progress bar showing repayment */}
                      <div className="mt-2 h-1 bg-slate-700 rounded-full overflow-hidden">
                        <div
                          className="h-full bg-emerald-500"
                          style={{ width: `${((account.original_amount - account.current_balance) / account.original_amount) * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-slate-500 text-sm">No active loans.</p>
              )}
            </Card>
          </div>

          {/* Score Breakdown */}
          {creditReport?.score_breakdown && (
            <Card variant="glass" className="mt-4">
              <h4 className="text-sm font-medium text-slate-400 mb-3">Credit Score Breakdown</h4>
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-sm">
                <div>
                  <span className="text-slate-500">Payment History</span>
                  <p className="text-white font-medium">{creditReport.score_breakdown.payment_history}%</p>
                </div>
                <div>
                  <span className="text-slate-500">Utilization</span>
                  <p className="text-white font-medium">{creditReport.score_breakdown.utilization}%</p>
                </div>
                <div>
                  <span className="text-slate-500">History Length</span>
                  <p className="text-white font-medium">{creditReport.score_breakdown.history_length}%</p>
                </div>
                <div>
                  <span className="text-slate-500">Credit Mix</span>
                  <p className="text-white font-medium">{creditReport.score_breakdown.credit_mix}%</p>
                </div>
                <div>
                  <span className="text-slate-500">New Credit</span>
                  <p className="text-white font-medium">{creditReport.score_breakdown.new_credit}%</p>
                </div>
              </div>
            </Card>
          )}
        </TabContent>
      </TabGroup>
    </div>
  );
}
