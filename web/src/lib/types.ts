export type TxType = "expense" | "income" | "transfer";

export interface Category {
  id: number;
  name: string;
  icon: string | null;
  type: "expense" | "income";
  monthly_budget: string | null;
  budget_rollover: boolean;
  parent_id: number | null;
}

export interface Account {
  id: number;
  name: string;
  type: "cash" | "bank" | "ewallet";
  balance: string;
}

export interface Transaction {
  id: number;
  amount: string;
  type: TxType;
  category_id: number | null;
  account_id: number | null;
  dest_account_id: number | null;
  description: string | null;
  occurred_at: string;
  source: string;
  created_at: string;
  category: Category | null;
  account: Account | null;
  dest_account: Account | null;
}

export interface SavingGoal {
  id: number;
  name: string;
  target_amount: string;
  saved_amount: string;
  target_date: string | null;
  pct: number;
  achieved: boolean;
}

export interface TransactionList {
  items: Transaction[];
  total: number;
  limit: number;
  offset: number;
}

export interface Summary {
  month: string;
  total_expense: string;
  total_income: string;
  count: number;
  per_category: { name: string; total: string }[];
}

export interface Trend {
  points: { month: string; expense: string; income: string }[];
}

export interface CategoryBudget {
  category_id: number;
  name: string;
  budget: string;
  spent: string;
  remaining: string;
  pct: number;
  status: "ok" | "warn" | "over";
}

export interface BudgetOverview {
  period: string;
  total_budget: string | null;
  total_budget_explicit: boolean;
  total_spent: string;
  total_remaining: string | null;
  safe_to_spend: string | null;
  days_left: number;
  day_today: number;
  days_in_month: number;
  exhaust_day: number | null;
  categories: CategoryBudget[];
}

export interface Recurring {
  id: number;
  amount: string;
  type: "expense" | "income";
  category_id: number | null;
  account_id: number | null;
  description: string | null;
  day_of_month: number;
  active: boolean;
  next_run: string;
  last_run: string | null;
}

export interface OCRResult {
  receipt_id: number;
  ocr_status: string;
  merchant: string | null;
  confidence: number;
  items: { name: string; qty: string | null; price: string | null }[];
  draft: {
    amount: string | null;
    type: TxType;
    category_id: number | null;
    category_name: string | null;
    description: string | null;
    occurred_at: string;
  } | null;
}
