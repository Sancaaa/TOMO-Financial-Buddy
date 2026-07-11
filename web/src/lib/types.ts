export type TxType = "expense" | "income" | "transfer";

export interface Category {
  id: number;
  name: string;
  icon: string | null;
  type: "expense" | "income";
  monthly_budget: string | null;
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
  description: string | null;
  occurred_at: string;
  source: string;
  created_at: string;
  category: Category | null;
  account: Account | null;
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
