import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { api } from "./api";
import type {
  Account,
  BudgetOverview,
  Category,
  NetWorth,
  OCRResult,
  ReconcileResult,
  Recurring,
  SavingGoal,
  Summary,
  Transaction,
  TransactionList,
  Trend,
} from "./types";

export function useCategories() {
  return useQuery({
    queryKey: ["categories"],
    queryFn: () => api.get<Category[]>("/categories"),
  });
}

export function useAccounts() {
  return useQuery({
    queryKey: ["accounts"],
    queryFn: () => api.get<Account[]>("/accounts"),
  });
}

export function useNetWorth() {
  return useQuery({
    queryKey: ["networth"],
    queryFn: () => api.get<NetWorth>("/accounts/net-worth"),
  });
}

export interface TxFilters {
  month?: string;
  category_id?: number;
  type?: string;
  q?: string;
  limit?: number;
  offset?: number;
}

export function useTransactions(filters: TxFilters) {
  const params = new URLSearchParams();
  for (const [k, v] of Object.entries(filters)) {
    if (v !== undefined && v !== "") params.set(k, String(v));
  }
  const qs = params.toString();
  return useQuery({
    queryKey: ["transactions", filters],
    queryFn: () => api.get<TransactionList>(`/transactions${qs ? "?" + qs : ""}`),
  });
}

export function useSummary(month: string) {
  return useQuery({
    queryKey: ["summary", month],
    queryFn: () => api.get<Summary>(`/analytics/summary?month=${month}`),
  });
}

export function useTrend(months: number) {
  return useQuery({
    queryKey: ["trend", months],
    queryFn: () => api.get<Trend>(`/analytics/trend?months=${months}`),
  });
}

function useInvalidateData() {
  const qc = useQueryClient();
  return () => {
    qc.invalidateQueries({ queryKey: ["transactions"] });
    qc.invalidateQueries({ queryKey: ["summary"] });
    qc.invalidateQueries({ queryKey: ["trend"] });
    qc.invalidateQueries({ queryKey: ["accounts"] });
    qc.invalidateQueries({ queryKey: ["networth"] });
    qc.invalidateQueries({ queryKey: ["budgets"] });
  };
}

export function useBudgets(month?: string) {
  return useQuery({
    queryKey: ["budgets", month ?? "current"],
    queryFn: () => api.get<BudgetOverview>(`/budgets${month ? `?period=${month}` : ""}`),
  });
}

export function useSetBudget() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: { category_id: number | null; amount: number | null; period?: string | null }) =>
      api.put<void>("/budgets", body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["budgets"] });
      qc.invalidateQueries({ queryKey: ["categories"] });
    },
  });
}

export function useRecurring() {
  return useQuery({ queryKey: ["recurring"], queryFn: () => api.get<Recurring[]>("/recurring") });
}

export function useSaveRecurring() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) => api.post<Recurring>("/recurring", body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["recurring"] }),
  });
}

export function useDeleteRecurring() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.del(`/recurring/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["recurring"] }),
  });
}

export function useQuickAdd() {
  const invalidate = useInvalidateData();
  return useMutation({
    mutationFn: (text: string) =>
      api.post<Transaction>("/transactions/quick", { text }),
    onSuccess: invalidate,
  });
}

export function useCreateTransaction() {
  const invalidate = useInvalidateData();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      api.post<Transaction>("/transactions", body),
    onSuccess: invalidate,
  });
}

export function useTransfer() {
  const invalidate = useInvalidateData();
  return useMutation({
    mutationFn: (body: Record<string, unknown>) =>
      api.post<Transaction>("/transactions/transfer", body),
    onSuccess: invalidate,
  });
}

export function useGoals() {
  return useQuery({ queryKey: ["goals"], queryFn: () => api.get<SavingGoal[]>("/goals") });
}

export function useSaveGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id?: number; body: Record<string, unknown> }) =>
      id ? api.patch<SavingGoal>(`/goals/${id}`, body) : api.post<SavingGoal>("/goals", body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["goals"] }),
  });
}

export function useContributeGoal() {
  const qc = useQueryClient();
  const invalidate = useInvalidateData();
  return useMutation({
    mutationFn: ({ id, amount, from_account_id }: { id: number; amount: number; from_account_id?: number | null }) =>
      api.post<SavingGoal>(`/goals/${id}/contribute`, { amount, from_account_id: from_account_id ?? null }),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["goals"] });
      invalidate(); // saldo & riwayat berubah bila uang dipindah
    },
  });
}

export function useDeleteGoal() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.del(`/goals/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["goals"] }),
  });
}

export function useUpdateTransaction() {
  const invalidate = useInvalidateData();
  return useMutation({
    mutationFn: ({ id, body }: { id: number; body: Record<string, unknown> }) =>
      api.patch<Transaction>(`/transactions/${id}`, body),
    onSuccess: invalidate,
  });
}

export function useDeleteTransaction() {
  const invalidate = useInvalidateData();
  return useMutation({
    mutationFn: (id: number) => api.del(`/transactions/${id}`),
    onSuccess: invalidate,
  });
}

export function useOcr() {
  return useMutation({
    mutationFn: (file: File) => {
      const form = new FormData();
      form.append("file", file);
      return api.postForm<OCRResult>("/transactions/ocr", form);
    },
  });
}

export function useSaveCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id?: number; body: Record<string, unknown> }) =>
      id
        ? api.patch<Category>(`/categories/${id}`, body)
        : api.post<Category>("/categories", body),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["categories"] }),
  });
}

export function useDeleteCategory() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.del(`/categories/${id}`),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["categories"] }),
  });
}

export function useSaveAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, body }: { id?: number; body: Record<string, unknown> }) =>
      id
        ? api.patch<Account>(`/accounts/${id}`, body)
        : api.post<Account>("/accounts", body),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      qc.invalidateQueries({ queryKey: ["networth"] });
    },
  });
}

export function useDeleteAccount() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => api.del(`/accounts/${id}`),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      qc.invalidateQueries({ queryKey: ["networth"] });
    },
  });
}

export function useReconcile() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: () => api.post<ReconcileResult>("/accounts/reconcile"),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["accounts"] });
      qc.invalidateQueries({ queryKey: ["networth"] });
    },
  });
}
