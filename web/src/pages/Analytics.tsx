import { useState } from "react";
import { Bars, Donut } from "../components/Charts";
import { PageHead } from "../components/PageHead";
import { Icon } from "../components/Icon";
import { BudgetBar } from "../components/BudgetBar";
import { categoryColor } from "../lib/colors";
import { currentMonth, monthLong, monthShort, rupiah } from "../lib/format";
import { useBudgets, useSummary, useTrend } from "../lib/queries";

export function Analytics() {
  const [month, setMonth] = useState(currentMonth());
  const summary = useSummary(month);
  const trend = useTrend(6);
  const budgets = useBudgets(month);
  const budgeted = (budgets.data?.categories ?? []).filter((c) => Number(c.budget) > 0);

  const slices = (summary.data?.per_category ?? []).map((c) => ({
    name: c.name,
    value: Number(c.total),
    color: categoryColor(c.name),
  }));

  const points = (trend.data?.points ?? []).map((p) => ({
    label: monthShort(p.month),
    expense: Number(p.expense),
    income: Number(p.income),
  }));

  const comparison = buildComparison(trend.data?.points ?? [], month);

  return (
    <>
      <PageHead
        eyebrow="lihat pola"
        title="Analitik"
        right={
          <input
            type="month"
            value={month}
            onChange={(e) => setMonth(e.target.value)}
            style={{
              border: "1px solid var(--sand)",
              borderRadius: "var(--radius-control)",
              padding: "8px 10px",
              background: "var(--paper)",
              color: "var(--ink)",
            }}
          />
        }
      />

      <div className="cols">
        <div className="col">
          <div className="card">
            <div className="section-title">Per kategori · {monthLong(month)}</div>
            {slices.length === 0 ? (
              <p className="hint">Belum ada pengeluaran.</p>
            ) : (
              <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
                <Donut data={slices} centerLabel={rupiah(summary.data?.total_expense ?? 0).replace("Rp", "")} size={160} />
                <div className="legend" style={{ flex: 1, minWidth: 150 }}>
                  {slices.map((s) => (
                    <div className="li" key={s.name}>
                      <span className="sw" style={{ background: s.color }} />
                      <span className="nm">{s.name}</span>
                      <span className="vl tabular">{rupiah(s.value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {comparison && (
            <div className="card pad-sm">
              <span className="ico-txt" style={{ color: comparison.up ? "var(--danger)" : "var(--leaf-dark)" }}>
                <Icon name={comparison.up ? "arrow-up" : "arrow-down"} size={16} /> {comparison.text}
              </span>
            </div>
          )}
        </div>

        <div className="col">
          {budgeted.length > 0 && (
            <div className="card">
              <div className="section-title">Budget per kategori</div>
              <div className="bbars">
                {budgeted.map((c) => (
                  <BudgetBar
                    key={c.category_id}
                    label={c.name}
                    spent={Number(c.spent)}
                    budget={Number(c.budget)}
                    pct={c.pct}
                    status={c.status}
                  />
                ))}
              </div>
            </div>
          )}

          <div className="card">
            <div className="section-title">Tren 6 bulan</div>
            <Bars data={points} />
            <div className="legend" style={{ flexDirection: "row", gap: 16, marginTop: 8 }}>
              <div className="li"><span className="sw" style={{ background: "var(--tomato)" }} /><span className="nm">Pengeluaran</span></div>
              <div className="li"><span className="sw" style={{ background: "var(--leaf)" }} /><span className="nm">Pemasukan</span></div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function buildComparison(
  points: { month: string; expense: string }[],
  month: string,
): { up: boolean; text: string } | null {
  const idx = points.findIndex((p) => p.month === month);
  if (idx <= 0) return null;
  const cur = Number(points[idx].expense);
  const prev = Number(points[idx - 1].expense);
  if (prev === 0) return null;
  const pct = Math.round(((cur - prev) / prev) * 100);
  if (pct === 0) return { up: false, text: "Pengeluaran sama dengan bulan lalu." };
  const up = pct > 0;
  return {
    up,
    text: `${Math.abs(pct)}% ${up ? "lebih boros" : "lebih hemat"} dari bulan lalu.`,
  };
}
