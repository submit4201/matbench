// This file is auto-generated (manually simulated)
// Do not edit manually if possible.

// ═══════════════════════════════════════════════════════════════════════
// Enums
// ═══════════════════════════════════════════════════════════════════════

export enum SocialTier {
  COMMUNITY_HERO = "Community Hero",
  TRUSTED_BUSINESS = "Trusted Business",
  GOOD_STANDING = "Good Standing",
  NEUTRAL_STANDING = "Neutral Standing",
  QUESTIONABLE_REPUTATION = "Questionable Reputation",
  COMMUNITY_CONCERN = "Community Concern",
  NEIGHBORHOOD_PARIAH = "Neighborhood Pariah"
}

export enum TicketType {
  OUT_OF_SOAP = "out_of_soap",
  MACHINE_BROKEN = "machine_broken",
  DIRTY_FLOOR = "dirty_floor",
  LONG_WAIT = "long_wait",
  OTHER = "other"
}

export enum TicketStatus {
  OPEN = "open",
  RESOLVED = "resolved",
  EXPIRED = "expired"
}

export enum PaymentStatus {
  ON_TIME = "on_time",
  LATE_30 = "late_30",
  LATE_60 = "late_60",
  LATE_90 = "late_90",
  MISSED = "missed",
  SCHEDULED = "scheduled"
}

export enum CreditRating {
  EXCEPTIONAL = "exceptional",
  VERY_GOOD = "very_good",
  GOOD = "good",
  FAIR = "fair",
  POOR = "poor"
}

export enum TransactionCategory {
  REVENUE = "revenue",
  EXPENSE = "expense",
  LOAN = "loan",
  REPAYMENT = "repayment",
  TAX = "tax",
  ADJUSTMENT = "adjustment",
  GRANT = "grant",
  CAPITAL = "capital",
  TRANSFER = "transfer",
  REAL_ESTATE = "real_estate"
}

export enum EventCategory {
  TICKET = "ticket",
  DILEMMA = "dilemma",
  MESSAGE = "message",
  TRADE = "trade",
  REGULATOR = "regulator",
  GAME_MASTER = "game_master",
  ALLIANCE = "alliance",
  MARKET = "market",
  ACHIEVEMENT = "achievement",
  SYSTEM = "system"
}

// ═══════════════════════════════════════════════════════════════════════
// API Request Models
// ═══════════════════════════════════════════════════════════════════════

export interface ActionRequest {
  agent_id: string;
  action_type: string;
  parameters: { [key: string]: any };
}

export interface ScenarioRequest {
  scenario_name?: string | null;
}

export interface NegotiateRequest {
  agent_id: string;
  vendor_id: string;
  item: string;
}

export interface ProposalRequest {
  agent_id: string;
  name: string;
  category: string;
  description: string;
  pricing_model: string;
  resource_requirements: string;
}

export interface CreditPaymentRequest {
  payment_id: string;
  amount: number;
}

export interface DiplomacyProposalRequest {
  agent_id: string;
  target_id: string;
  type: string;
}

// ═══════════════════════════════════════════════════════════════════════
// Core Data Models
// ═══════════════════════════════════════════════════════════════════════

export interface RevenueStream {
  name: string;
  category: string;
  price: number;
  cost_per_unit: number;
  demand_multiplier: number;
  unlocked: boolean;
  description: string;
  weekly_revenue: number;
  setup_cost?: number;
}

export interface Loan {
  name: string;
  principal: number;
  balance: number;
  interest_rate_monthly: number;
  term_weeks: number;
  weeks_remaining: number;
  weekly_payment: number;
  is_defaulted: boolean;
  missed_payments: number;
}

export interface TaxRecord {
  quarter: number;
  gross_revenue: number;
  deductible_expenses: number;
  net_profit: number;
  tax_owed: number;
  tax_paid: number;
  is_filed: boolean;
  due_week: number;
  is_overdue: boolean;
}

export interface FinancialReport {
  week: number;
  revenue_wash: number;
  revenue_dry: number;
  revenue_vending: number;
  revenue_premium: number;
  revenue_membership: number;
  revenue_other: number;
  total_revenue: number;
  cogs_supplies: number;
  cogs_vending: number;
  total_cogs: number;
  gross_profit: number;
  expense_rent: number;
  expense_utilities: number;
  expense_labor: number;
  expense_maintenance: number;
  expense_marketing: number;
  expense_insurance: number;
  expense_other: number;
  total_operating_expenses: number;
  operating_income: number;
  income_interest: number;
  expense_interest: number;
  fines: number;
  net_income_before_tax: number;
  tax_provision: number;
  net_income: number;
  cash_beginning: number;
  cash_ending: number;
}

export interface Transaction {
  amount: number;
  category: TransactionCategory | string;
  description: string;
  week: number;
  related_entity_id?: string | null;
  id: string;
  timestamp: string;
}

export interface Bill {
  id: string;
  name: string;
  amount: number;
  due_week: number;
  category: string;
  recipient_id: string;
  is_paid: boolean;
  generated_week: number;
  penalty_applied: boolean;
}

export interface PaymentRecord {
  id: string;
  loan_id: string;
  amount_due: number;
  amount_paid: number;
  due_week: number;
  paid_week?: number | null;
  status: PaymentStatus | string;
  // Computed properties
  is_paid: boolean;
  days_late: number;
}

export interface CreditAccount {
  id: string;
  account_type: string;
  original_amount: number;
  current_balance: number;
  credit_limit: number;
  interest_rate: number;
  weekly_payment: number;
  opened_week: number;
  term_weeks: number;
  payments: PaymentRecord[];
  is_active: boolean;
  is_defaulted: boolean;
}

export interface CreditScore {
  payment_history_score: number;
  utilization_score: number;
  history_length_score: number;
  credit_mix_score: number;
  new_credit_score: number;
  // Computed
  total_score: number;
  rating: CreditRating;
}

export interface SocialScore {
  customer_satisfaction: number;
  community_standing: number;
  ethical_conduct: number;
  employee_relations: number;
  environmental_responsibility: number;
  // Computed
  total_score: number;
  tier: SocialTier;
  tier_info: {
    tier_name: string;
    badge: string;
    benefits: string[];
    penalties: string[];
  };
}

export interface Ticket {
  id: string;
  type: TicketType | string;
  description: string;
  customer_id: string;
  laundromat_id: string;
  created_week: number;
  severity: string;
  status: TicketStatus | string;
  resolution_week: number;
}

export interface Machine {
  id: string;
  type: string;
  condition: number;
  is_broken: boolean;
  age_weeks: number;
  location_id?: string | null;
}

export interface StaffMember {
  id: string;
  name: string;
  role: string;
  skill_level: number;
  morale: number;
  wage: number;
}

export interface InventoryMetrics {
  stock_level: number;
  burn_rate: number;
  days_of_supply: number;
  status: string;
  recommendation: string;
}

// ═══════════════════════════════════════════════════════════════════════
// DTOs (Data Transfer Objects) - Matching API Response
// ═══════════════════════════════════════════════════════════════════════

export interface Laundromat {
  name: string;
  id: string;
  balance: number;
  reputation: number; // calculated from social score
  price: number;

  // Collections
  machines: number; // Flattened in serialization
  broken_machines: number;

  inventory: { [key: string]: number };
  inventory_metrics?: InventoryMetrics;

  tickets: Ticket[];
  staff: StaffMember[];
  bills: Bill[];
  active_events: string[];

  // Financials
  revenue_streams: { [key: string]: RevenueStream };
  loans: Loan[];
  financial_reports: FinancialReport[];
  tax_records: TaxRecord[];

  // Social
  social_score: SocialScore; // Serialized fully

  // Operational
  marketing_boost: number;
  cleanliness: number;
  security_level: number;
  avg_daily_burn_rate: number;

  // Realtime
  active_customers: number;

  // Supply Chain
  pending_deliveries: {
    item: string;
    quantity: number;
    arrival_week: number;
    vendor_name: string;
  }[];
}

export interface Vendor {
  id: string;
  name: string;
  slogan: string;
  tier: string;
  prices: { [key: string]: number };
  special_offer: { item_name: string; price: number; description: string } | null;
  reliability: number;
  delivery_days: number;
}

export interface Message {
  id: string;
  sender_id: string;
  recipient_id: string;
  channel: string;
  content: string;
  week: number;
  day: number;
  intent: string;
  is_read: boolean;
  attachments: any[];
}

export interface AIThought {
  name: string;
  thinking: string[];
  actions: string[];
  raw_response?: string;
  [key: string]: any;
}

export interface GameState {
  week: number;
  day: string;
  phase: string;
  season: string;
  laundromats: { [key: string]: Laundromat };
  events: string[]; // Descriptions? Or full events? API says: [e.description for e in active_events]
  messages: Message[];
  market: {
    vendors: Vendor[];
    supply_chain_events: any[];
  };
  customer_thoughts: string[];
  scenario?: string | null;
  ai_thoughts: { [key: string]: AIThought };
  ai_thoughts_history: any[];
  alliances: string[];
}

// ═══════════════════════════════════════════════════════════════════════
// Restored Manual Types
// ═══════════════════════════════════════════════════════════════════════

export interface CreditReport {
  credit_score: number;
  rating: string;
  active_loans: Loan[];
  payment_history: PaymentRecord[];
  total_debt: number;
  next_payment?: {
    amount: number;
    due_week: number;
  };
}

export interface ZoneInfo {
  zone_id: string;
  zone_name: string;
  base_foot_traffic: number;
  rent_cost: number;
  competition_level: number;
  demographic: string;
}

export interface CalendarStats {
  total_scheduled: number;
  completed: number;
  overdue: number;
  upcoming: number;
}

export interface ScheduledAction {
  id: string;
  category: string;
  title: string;
  description: string;
  week: number;
  day: number;
  priority: string;
  is_recurring: boolean;
  status: string;
}
