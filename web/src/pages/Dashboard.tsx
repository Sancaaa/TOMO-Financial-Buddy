import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Donut } from "../components/Charts";
import { TxList } from "../components/TxList";
import { TxEditSheet } from "../components/TxEditSheet";
import { PageHead } from "../components/PageHead";
import { Tomato } from "../components/Tomato";
import { Icon } from "../components/Icon";
import { BudgetBar } from "../components/BudgetBar";
import { categoryColor } from "../lib/colors";
import { currentMonth, monthLong, rupiah } from "../lib/format";
import { useBudgetAlerts, useBudgets, useGoals, useNetWorth, useQuickAdd, useSummary, useTransactions } from "../lib/queries";
import { useAuth } from "../lib/auth";
import type { Transaction } from "../lib/types";

export function Dashboard() {
  const month = currentMonth();
  const summary = useSummary(month);
  const recent = useTransactions({ month, limit: 8 });
  const budgets = useBudgets();
  const alerts = useBudgetAlerts();
  const goals = useGoals();
  const netWorth = useNetWorth();
  const quick = useQuickAdd();
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [text, setText] = useState("");
  const [selected, setSelected] = useState<Transaction | null>(null);
  const [quickErr, setQuickErr] = useState("");
  const [quickFlash, setQuickFlash] = useState("");

  const slices = (summary.data?.per_category ?? []).map((c) => ({
    name: c.name,
    value: Number(c.total),
    color: categoryColor(c.name),
  }));

  async function submitQuick(e: React.FormEvent) {
    e.preventDefault();
    setQuickErr("");
    try {
      const tx = await quick.mutateAsync(text);
      // Umpan balik apa yang tercatat & ditebak kategori apa; safe-to-spend ikut
      // ter-refresh lewat invalidasi query "budgets" di useQuickAdd.
      setQuickFlash(`${rupiah(tx.amount)} — ${tx.category?.name ?? "tercatat"}`);
      setText("");
    } catch (err) {
      setQuickFlash("");
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
        {quickFlash && (
          <div className="ico-txt" style={{ marginTop: 8, color: "var(--leaf-dark)" }}>
            <Icon name="check" size={16} /> {quickFlash}
          </div>
        )}
      </form>

      {(alerts.data?.alerts ?? []).length > 0 && (
        <div className="card pad-sm stack" style={{ gap: 6, borderColor: "var(--danger)" }}>
          {(alerts.data?.alerts ?? []).map((m, i) => (
            <div key={i} className="ico-txt" style={{ color: "var(--danger)" }}>
              <Icon name="alert" size={16} /> {m}
            </div>
          ))}
        </div>
      )}

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

          {budgets.data?.total_budget != null ? (() => {
            const b = budgets.data;
            const spent = Number(b.total_spent);
            const total = Number(b.total_budget);
            const reserved = Number(b.reserved_recurring);
            const unbudgeted = Number(b.unbudgeted_spent);
            const pct = total > 0 ? Math.round((spent / total) * 100) : 0;
            const status = pct >= 100 ? "over" : pct >= 70 ? "warn" : "ok";
            return (
              <div className="card">
                <div className="section-title">Sisa aman dibelanjakan</div>
                <div className="safe">
                  <span className="big">
                    {b.safe_to_spend != null ? rupiah(b.safe_to_spend) + "/hari" : "—"}
                  </span>
                  <span className="hint">
                    {b.days_left} hari lagi
                    {b.exhaust_day ? ` · dengan laju ini, budget habis ~tgl ${b.exhaust_day}` : ""}
                  </span>
                </div>
                {reserved > 0 && (
                  <p className="hint" style={{ marginTop: 6 }}>
                    Sudah disisihkan {rupiah(reserved)} untuk tagihan rutin yang belum jatuh tempo.
                  </p>
                )}
                <div style={{ marginTop: 12 }}>
                  <BudgetBar label="Total bulan ini" spent={spent} budget={total} pct={pct} status={status} />
                </div>
                {!b.total_budget_explicit && unbudgeted > 0 && (
                  <p className="hint" style={{ marginTop: 6 }}>
                    +{rupiah(unbudgeted)} belanja di kategori tanpa budget (di luar hitungan di atas).
                  </p>
                )}
              </div>
            );
          })() : (
            budgets.data?.projected_month_total != null && (
              <div className="card">
                <div className="section-title">Proyeksi bulan ini</div>
                <div className="safe">
                  <span className="big tabular">{rupiah(budgets.data.projected_month_total)}</span>
                  <span className="hint">
                    rata-rata {rupiah(budgets.data.avg_daily_spend)}/hari · perkiraan total akhir bulan
                  </span>
                </div>
                <p className="hint" style={{ marginTop: 8 }}>
                  Set budget total di <strong>Kelola</strong> untuk lihat sisa aman/hari.
                </p>
              </div>
            )
          )}

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
              <div className="section-title ico-txt"><Icon name="target" size={15} /> Target nabung</div>
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
                        <span className="pill ico-txt"><Icon name="trophy" size={13} /> tercapai</span>
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
