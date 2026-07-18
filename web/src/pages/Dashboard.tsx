import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Donut } from "../components/Charts";
import { TxList } from "../components/TxList";
import { TxEditSheet } from "../components/TxEditSheet";
import { PageHead } from "../components/PageHead";
import { Tomato } from "../components/Tomato";
import { BudgetBar } from "../components/BudgetBar";
import { categoryColor } from "../lib/colors";
import { currentMonth, monthLong, rupiah } from "../lib/format";
import { useBudgets, useGoals, useNetWorth, useQuickAdd, useSummary, useTransactions } from "../lib/queries";
import { useAuth } from "../lib/auth";
import type { Transaction } from "../lib/types";

export function Dashboard() {
  const month = currentMonth();
  const summary = useSummary(month);
  const recent = useTransactions({ month, limit: 8 });
  const budgets = useBudgets();
  const goals = useGoals();
  const netWorth = useNetWorth();
  const quick = useQuickAdd();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [text, setText] = useState("");
  const [selected, setSelected] = useState<Transaction | null>(null);
  const [quickErr, setQuickErr] = useState("");

  const slices = (summary.data?.per_category ?? []).map((c) => ({
    name: c.name,
    value: Number(c.total),
    color: categoryColor(c.name),
  }));

  async function submitQuick(e: React.FormEvent) {
    e.preventDefault();
    setQuickErr("");
    try {
      await quick.mutateAsync(text);
      setText("");
    } catch (err) {
      setQuickErr(err instanceof Error ? err.message : "Gagal");
    }
  }

  return (
    <>
      <PageHead
        eyebrow="catatan bulan ini"
        title={monthLong(month)}
        right={<button className="btn btn-sm" onClick={logout}>Keluar</button>}
      />

      <form className="card tilt" onSubmit={submitQuick}>
        <p className="eyebrow-sm" style={{ marginBottom: 8 }}>catat cepat</p>
        <div className="row" style={{ gap: 8, alignItems: "flex-end" }}>
          <div className="field" style={{ flex: 3 }}>
            <input placeholder="mis. makan 15k" value={text} onChange={(e) => setText(e.target.value)} />
          </div>
          <button className="btn btn-primary" style={{ flex: 1 }} disabled={quick.isPending || !text.trim()}>
            {quick.isPending ? "…" : "Catat"}
          </button>
        </div>
        {quickErr && <div className="err" style={{ marginTop: 8 }}>{quickErr}</div>}
      </form>

      <div className="cols">
        <div className="col">
          {netWorth.data && (
            <div className="card">
              <div className="section-title">Total saldo</div>
              <div className="safe">
                <span className="big tabular">{rupiah(netWorth.data.total)}</span>
                <span className="hint">di {netWorth.data.accounts.length} akun</span>
              </div>
              {netWorth.data.accounts.length > 0 && (
                <div className="legend" style={{ marginTop: 10 }}>
                  {netWorth.data.accounts.map((a) => (
                    <div className="li" key={a.id}>
                      <span className="nm">{a.name}</span>
                      <span className="vl tabular">{rupiah(a.balance)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {budgets.data?.total_budget != null && (() => {
            const spent = Number(budgets.data.total_spent);
            const total = Number(budgets.data.total_budget);
            const pct = total > 0 ? Math.round((spent / total) * 100) : 0;
            const status = pct >= 100 ? "over" : pct >= 70 ? "warn" : "ok";
            return (
              <div className="card">
                <div className="section-title">Sisa aman dibelanjakan</div>
                <div className="safe">
                  <span className="big">
                    {budgets.data.safe_to_spend != null ? rupiah(budgets.data.safe_to_spend) + "/hari" : "—"}
                  </span>
                  <span className="hint">
                    {budgets.data.days_left} hari lagi
                    {budgets.data.exhaust_day ? ` · dengan laju ini, budget habis ~tgl ${budgets.data.exhaust_day}` : ""}
                  </span>
                </div>
                <div style={{ marginTop: 12 }}>
                  <BudgetBar label="Total bulan ini" spent={spent} budget={total} pct={pct} status={status} />
                </div>
              </div>
            );
          })()}

          <div className="metrics">
            <div className="metric">
              <div className="label">Pengeluaran</div>
              <div className="value exp tabular">{rupiah(summary.data?.total_expense ?? 0)}</div>
            </div>
            <div className="metric">
              <div className="label">Pemasukan</div>
              <div className="value inc tabular">{rupiah(summary.data?.total_income ?? 0)}</div>
            </div>
          </div>

          <div className="card">
            <div className="section-title">Pengeluaran per kategori</div>
            {slices.length === 0 ? (
              <div className="center">
                <Tomato size={56} face />
                <p className="hint">Belum ada pengeluaran bulan ini. Yuk mulai, ketik aja <code>kopi 18k</code>.</p>
              </div>
            ) : (
              <div style={{ display: "flex", gap: 16, alignItems: "center", flexWrap: "wrap" }}>
                <Donut data={slices} centerLabel={String(summary.data?.count ?? 0) + " tx"} size={150} />
                <div className="legend" style={{ flex: 1, minWidth: 150 }}>
                  {slices.slice(0, 6).map((s) => (
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
        </div>

        <div className="col">
          <div className="card">
            <div className="between" style={{ marginBottom: 6 }}>
              <div className="section-title" style={{ margin: 0 }}>Terbaru</div>
              <button className="btn btn-sm" onClick={() => navigate("/riwayat")}>Semua</button>
            </div>
            <TxList items={recent.data?.items ?? []} onSelect={setSelected} />
          </div>

          {(goals.data ?? []).length > 0 && (
            <div className="card">
              <div className="section-title">Target nabung 🎯</div>
              <div className="bbars">
                {(goals.data ?? []).map((g) => (
                  <div key={g.id} className="stack" style={{ gap: 6 }}>
                    <BudgetBar
                      label={g.name}
                      spent={Number(g.saved_amount)}
                      budget={Number(g.target_amount)}
                      pct={g.pct}
                      status="ok"
                    />
                    {g.achieved && (
                      <span style={{ display: "flex", alignItems: "center", gap: 6 }}>
                        <Tomato size={20} face />
                        <span className="pill">tercapai 🎉</span>
                      </span>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {selected && <TxEditSheet tx={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
