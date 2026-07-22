import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Bars, Donut } from "../components/Charts";
import { PageHead } from "../components/PageHead";
import { Icon } from "../components/Icon";
import { BudgetBar } from "../components/BudgetBar";
import { categoryColor } from "../lib/colors";
import { currentMonth, monthLong, monthShort, rupiah } from "../lib/format";
import { useBudgets, useCategories, useComparison, useSummary, useTrend } from "../lib/queries";

export function Analytics() {
  const [month, setMonth] = useState(currentMonth());
  const summary = useSummary(month);
  const trend = useTrend(6, month);
  const budgets = useBudgets(month);
  const comparison = useComparison(month);
  const { data: categories } = useCategories();
  const navigate = useNavigate();
  const budgeted = (budgets.data?.categories ?? []).filter((c) => Number(c.budget) > 0);

  const catMap = new Map((categories ?? []).map((c) => [c.name, c.id]));
  function drilldown(name: string) {
    const id = catMap.get(name);
    navigate(`/riwayat?month=${month}${id ? `&category_id=${id}` : ""}`);
  }

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

  const cmp = comparison.data;

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
                    <div
                      className="li"
                      key={s.name}
                      role="button"
                      style={{ cursor: "pointer" }}
                      onClick={() => drilldown(s.name)}
                    >
                      <span className="sw" style={{ background: s.color }} />
                      <span className="nm">{s.name}</span>
                      <span className="vl tabular">{rupiah(s.value)}</span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>

          {cmp && cmp.pct != null && (
            <div className="card pad-sm">
              <span className="ico-txt" style={{ color: cmp.up ? "var(--danger)" : "var(--leaf-dark)" }}>
                <Icon name={cmp.up ? "arrow-up" : "arrow-down"} size={16} />
                {" "}
                {Math.abs(cmp.pct)}% {cmp.up ? "lebih boros" : "lebih hemat"} dari bulan lalu
                {cmp.driver_category ? `, terutama di ${cmp.driver_category}` : ""}.
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
                    hint={c.exhaust_day ? `dengan laju ini, habis ~tgl ${c.exhaust_day}` : undefined}
                    onClick={() => navigate(`/riwayat?month=${month}&category_id=${c.category_id}`)}
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
