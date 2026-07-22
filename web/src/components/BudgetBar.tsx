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
  hint,
  onClick,
}: {
  label: string;
  spent: number;
  budget: number;
  pct: number;
  status: CategoryBudget["status"];
  hint?: string;
  onClick?: () => void;
}) {
  return (
    <div
      className="bbar"
      onClick={onClick}
      role={onClick ? "button" : undefined}
      style={onClick ? { cursor: "pointer" } : undefined}
    >
      <div className="top">
        <span className="nm">{label}</span>
        <span className="vl">
          {rupiah(spent)} / {rupiah(budget)} · {pct}%
        </span>
      </div>
      <div className="track">
        <div className="fill" style={{ width: Math.min(pct, 100) + "%", background: STATUS_COLOR[status] }} />
      </div>
      {hint && <span className="hint" style={{ marginTop: 2 }}>{hint}</span>}
    </div>
  );
}
