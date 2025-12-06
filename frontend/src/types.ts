export interface Ticket {
  id: string;
  type: string;
  description: string;
  status: 'open' | 'resolved';
  severity: 'low' | 'medium' | 'high';
  customer_id?: string;
}

export interface SocialScore {
  total_score: number;
  components: {
    customer_satisfaction: number;
    community_standing: number;
    ethical_conduct: number;
    employee_relations: number;
    environmental_responsibility: number;
  };
  tier_info: {
    tier_name: string;
    badge: string;
    benefits?: string[];
    penalties?: string[];
  };
}

export interface InventoryMetrics {
  stock_level: number;
  burn_rate: number;
  days_of_supply: number;
  status: string;
  recommendation: string;
}

export interface Laundromat {
  id: string;
  name: string;
  balance: number;
  reputation: number;
  inventory: { [key: string]: number };
  tickets: Ticket[];
  machines: number;
  broken_machines: number;
  price: number;
  social_score: SocialScore | number;
  inventory_metrics?: InventoryMetrics;
  revenue_streams?: { [key: string]: RevenueStream };
  active_customers?: number;
}

export interface AIThought {
  name: string;
  thinking: string[];
  actions: string[];
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

export interface SupplyChainEvent {
  type: string;
  vendor_id: string | null;
  description: string;
  severity: string;
}

export interface GameState {
  week: number;
  season: string;
  laundromats: { [key: string]: Laundromat };
  events: string[];
  market: {
    vendors: Vendor[];
    supply_chain_events: SupplyChainEvent[];
  };
  customer_thoughts: string[];
  messages: string[];
  scenario?: string;
  ai_thoughts?: { [key: string]: AIThought };
}

export interface RevenueStream {
  name: string;
  category: string;
  description: string;
  price: number;
  cost_per_unit: number;
  unlocked: boolean;  // 'unlocked' is used by backend, not 'active'
  weekly_revenue?: number;
  setup_cost?: number;
}

