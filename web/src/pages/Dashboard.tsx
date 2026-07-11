import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { Donut } from "../components/Charts";
import { TxList } from "../components/TxList";
import { TxEditSheet } from "../components/TxEditSheet";
import { categoryColor } from "../lib/colors";
import { currentMonth, monthLong, rupiah } from "../lib/format";
import { useQuickAdd, useSummary, useTransactions } from "../lib/queries";
import { useAuth } from "../lib/auth";
import type { Transaction } from "../lib/types";

export function Dashboard() {
  const month = currentMonth();
  const summary = useSummary(month);
  const recent = useTransactions({ month, limit: 8 });
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
      <div className="topbar">
        <img src="/tomo.svg" width={28} height={28} alt="" />
        <div className="grow">
          <h1>TOMO</h1>
        </div>
        <button className="btn btn-sm" onClick={logout}>Keluar</button>
      </div>

      <form className="card pad-sm" onSubmit={submitQuick}>
        <div className="row" style={{ gap: 8 }}>
          <input
            className="grow"
            placeholder="Catat cepat, mis. makan 15k"
            value={text}
            onChange={(e) => setText(e.target.value)}
            style={{ flex: 3, border: "0.5px solid var(--border-strong)", borderRadius: "var(--radius-control)", padding: "10px 12px", background: "var(--surface)", color: "var(--ink)" }}
          />
          <button className="btn btn-primary" style={{ flex: 1 }} disabled={quick.isPending || !text.trim()}>
            {quick.isPending ? "…" : "Catat"}
          </button>
        </div>
        {quickErr && <div className="err" style={{ marginTop: 8 }}>{quickErr}</div>}
      </form>

      <div className="metrics">
        <div className="metric">
          <div className="label">Pengeluaran {monthLong(month)}</div>
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
          <p className="hint">Belum ada pengeluaran bulan ini.</p>
        ) : (
          <div style={{ display: "flex", gap: 16, alignItems: "center" }}>
            <Donut data={slices} centerLabel={String(summary.data?.count ?? 0) + " tx"} size={150} />
            <div className="legend grow" style={{ flex: 1 }}>
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

      <div className="card">
        <div className="between" style={{ marginBottom: 6 }}>
          <div className="section-title" style={{ margin: 0 }}>Terbaru</div>
          <button className="btn btn-sm" onClick={() => navigate("/riwayat")}>Semua</button>
        </div>
        <TxList items={recent.data?.items ?? []} onSelect={setSelected} />
      </div>

      {selected && <TxEditSheet tx={selected} onClose={() => setSelected(null)} />}
    </>
  );
}
