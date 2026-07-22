import { useState } from "react";
import { useSearchParams } from "react-router-dom";
import { TxList } from "../components/TxList";
import { TxEditSheet } from "../components/TxEditSheet";
import { PageHead } from "../components/PageHead";
import { downloadCsv } from "../lib/api";
import { currentMonth } from "../lib/format";
import { useCategories, useTransactions } from "../lib/queries";
import type { Transaction } from "../lib/types";

export function History() {
  const { data: categories } = useCategories();
  const [params] = useSearchParams();
  const [month, setMonth] = useState(params.get("month") || currentMonth());
  const [categoryId, setCategoryId] = useState(params.get("category_id") ?? "");
  const [q, setQ] = useState("");
  const [limit, setLimit] = useState(30);
  const [selected, setSelected] = useState<Transaction | null>(null);

  const list = useTransactions({
    month: month || undefined,
    category_id: categoryId ? Number(categoryId) : undefined,
    q: q || undefined,
    limit,
  });

  const total = list.data?.total ?? 0;
  const items = list.data?.items ?? [];

  return (
    <div className="narrow">
      <PageHead eyebrow="semua catatan" title="Riwayat" />

      <div className="card pad-sm stack">
        <div className="row">
          <div className="field">
            <label>Bulan</label>
            <input type="month" value={month} onChange={(e) => setMonth(e.target.value)} />
          </div>
          <div className="field">
            <label>Kategori</label>
            <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
              <option value="">Semua</option>
              {(categories ?? []).map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="field">
          <label>Cari</label>
          <input placeholder="kata di deskripsi…" value={q} onChange={(e) => setQ(e.target.value)} />
        </div>
      </div>

      <div className="card">
        <div className="between" style={{ marginBottom: 6 }}>
          <div className="section-title" style={{ margin: 0 }}>{total} transaksi</div>
          <button className="btn btn-sm" onClick={() => downloadCsv(month || undefined)}>Export CSV</button>
        </div>
        <TxList items={items} onSelect={setSelected} />
        {items.length < total && (
          <button className="btn btn-block" style={{ marginTop: 12 }} onClick={() => setLimit((l) => l + 30)}>
            Muat lebih
          </button>
        )}
      </div>

      {selected && <TxEditSheet tx={selected} onClose={() => setSelected(null)} />}
    </div>
  );
}
