import { rupiah } from "../lib/format";
import type { CategoryBudget } from "../lib/types";

const STATUS_COLOR: Record<CategoryBudget["status"], string> = {
  ok: "var(--leaf)",
  warn: "var(--warning)",
  over: "var(--danger)",
};

export function BudgetBar({
  label,
  spent,
  budget,
  pct,
  status,
}: {
  label: string;
  spent: number;
  budget: number;
  pct: number;
  status: CategoryBudget["status"];
}) {
  return (
    <div className="bbar">
      <div className="top">
        <span className="nm">{label}</span>
        <span className="vl">
          {rupiah(spent)} / {rupiah(budget)} · {pct}%
        </span>
      </div>
      <div className="track">
        <div className="fill" style={{ width: Math.min(pct, 100) + "%", background: STATUS_COLOR[status] }} />
      </div>
    </div>
  );
}
