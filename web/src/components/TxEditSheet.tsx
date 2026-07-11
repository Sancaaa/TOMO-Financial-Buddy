import { useState } from "react";
import { Sheet } from "./Sheet";
import { useCategories, useDeleteTransaction, useUpdateTransaction } from "../lib/queries";
import type { Transaction } from "../lib/types";

export function TxEditSheet({ tx, onClose }: { tx: Transaction; onClose: () => void }) {
  const { data: categories } = useCategories();
  const update = useUpdateTransaction();
  const remove = useDeleteTransaction();

  const [type, setType] = useState(tx.type);
  const [amount, setAmount] = useState(String(Math.round(Number(tx.amount))));
  const [description, setDescription] = useState(tx.description ?? "");
  const [categoryId, setCategoryId] = useState<string>(tx.category_id ? String(tx.category_id) : "");
  const [date, setDate] = useState(tx.occurred_at.slice(0, 10));

  const catOptions = (categories ?? []).filter(
    (c) => c.type === (type === "income" ? "income" : "expense"),
  );

  async function save() {
    await update.mutateAsync({
      id: tx.id,
      body: {
        type,
        amount: Number(amount),
        description: description || null,
        category_id: categoryId ? Number(categoryId) : null,
        occurred_at: new Date(date + "T12:00:00").toISOString(),
      },
    });
    onClose();
  }

  async function del() {
    await remove.mutateAsync(tx.id);
    onClose();
  }

  return (
    <Sheet title="Ubah transaksi" onClose={onClose}>
      <div className="seg">
        <button className={type === "expense" ? "active" : ""} onClick={() => setType("expense")}>
          Pengeluaran
        </button>
        <button className={type === "income" ? "active" : ""} onClick={() => setType("income")}>
          Pemasukan
        </button>
      </div>
      <div className="field">
        <label>Jumlah (Rp)</label>
        <input inputMode="numeric" value={amount} onChange={(e) => setAmount(e.target.value.replace(/\D/g, ""))} />
      </div>
      <div className="field">
        <label>Deskripsi</label>
        <input value={description} onChange={(e) => setDescription(e.target.value)} />
      </div>
      <div className="row">
        <div className="field">
          <label>Kategori</label>
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
            <option value="">— tanpa —</option>
            {catOptions.map((c) => (
              <option key={c.id} value={c.id}>
                {c.name}
              </option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Tanggal</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
      </div>
      <button className="btn btn-primary btn-block" onClick={save} disabled={update.isPending || !amount}>
        {update.isPending ? "Menyimpan…" : "Simpan"}
      </button>
      <button className="btn btn-danger btn-block" onClick={del} disabled={remove.isPending}>
        Hapus transaksi
      </button>
    </Sheet>
  );
}
