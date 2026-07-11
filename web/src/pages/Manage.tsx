import { useState } from "react";
import { Sheet } from "../components/Sheet";
import { categoryColor } from "../lib/colors";
import { rupiah } from "../lib/format";
import {
  useAccounts,
  useCategories,
  useDeleteAccount,
  useDeleteCategory,
  useSaveAccount,
  useSaveCategory,
} from "../lib/queries";
import type { Account, Category } from "../lib/types";

export function Manage() {
  const { data: categories } = useCategories();
  const { data: accounts } = useAccounts();
  const [editCat, setEditCat] = useState<Partial<Category> | null>(null);
  const [editAcc, setEditAcc] = useState<Partial<Account> | null>(null);

  return (
    <>
      <div className="topbar">
        <h1 className="grow">Kelola</h1>
      </div>

      <div className="card">
        <div className="between" style={{ marginBottom: 8 }}>
          <div className="section-title" style={{ margin: 0 }}>Kategori</div>
          <button className="btn btn-sm" onClick={() => setEditCat({ type: "expense" })}>+ Tambah</button>
        </div>
        <div className="txlist">
          {(categories ?? []).map((c) => (
            <button key={c.id} className="tx" onClick={() => setEditCat(c)}>
              <span className="dot" style={{ background: categoryColor(c.name) }} />
              <span className="body">
                <span className="desc">{c.name}</span>
                <span className="meta">{c.type === "income" ? "Pemasukan" : "Pengeluaran"}{c.monthly_budget ? ` · budget ${rupiah(c.monthly_budget)}` : ""}</span>
              </span>
            </button>
          ))}
        </div>
      </div>

      <div className="card">
        <div className="between" style={{ marginBottom: 8 }}>
          <div className="section-title" style={{ margin: 0 }}>Akun</div>
          <button className="btn btn-sm" onClick={() => setEditAcc({ type: "cash" })}>+ Tambah</button>
        </div>
        <div className="txlist">
          {(accounts ?? []).map((a) => (
            <button key={a.id} className="tx" onClick={() => setEditAcc(a)}>
              <span className="body">
                <span className="desc">{a.name}</span>
                <span className="meta">{a.type}</span>
              </span>
              <span className="amt tabular">{rupiah(a.balance)}</span>
            </button>
          ))}
        </div>
      </div>

      {editCat && <CategorySheet cat={editCat} onClose={() => setEditCat(null)} />}
      {editAcc && <AccountSheet acc={editAcc} onClose={() => setEditAcc(null)} />}
    </>
  );
}

function CategorySheet({ cat, onClose }: { cat: Partial<Category>; onClose: () => void }) {
  const save = useSaveCategory();
  const remove = useDeleteCategory();
  const [name, setName] = useState(cat.name ?? "");
  const [type, setType] = useState<"expense" | "income">(cat.type ?? "expense");
  const [budget, setBudget] = useState(cat.monthly_budget ? String(Math.round(Number(cat.monthly_budget))) : "");

  async function submit() {
    await save.mutateAsync({
      id: cat.id,
      body: { name, type, monthly_budget: budget ? Number(budget) : null },
    });
    onClose();
  }

  return (
    <Sheet title={cat.id ? "Ubah kategori" : "Kategori baru"} onClose={onClose}>
      <div className="field">
        <label>Nama</label>
        <input value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className="seg">
        <button className={type === "expense" ? "active" : ""} onClick={() => setType("expense")}>Pengeluaran</button>
        <button className={type === "income" ? "active" : ""} onClick={() => setType("income")}>Pemasukan</button>
      </div>
      <div className="field">
        <label>Budget bulanan (Rp, opsional)</label>
        <input inputMode="numeric" value={budget} onChange={(e) => setBudget(e.target.value.replace(/\D/g, ""))} />
      </div>
      <button className="btn btn-primary btn-block" onClick={submit} disabled={save.isPending || !name}>Simpan</button>
      {cat.id && (
        <button className="btn btn-danger btn-block" onClick={async () => { await remove.mutateAsync(cat.id!); onClose(); }}>
          Hapus
        </button>
      )}
    </Sheet>
  );
}

function AccountSheet({ acc, onClose }: { acc: Partial<Account>; onClose: () => void }) {
  const save = useSaveAccount();
  const remove = useDeleteAccount();
  const [name, setName] = useState(acc.name ?? "");
  const [type, setType] = useState<Account["type"]>(acc.type ?? "cash");
  const [balance, setBalance] = useState(acc.balance ? String(Math.round(Number(acc.balance))) : "");

  async function submit() {
    await save.mutateAsync({
      id: acc.id,
      body: { name, type, balance: balance ? Number(balance) : 0 },
    });
    onClose();
  }

  return (
    <Sheet title={acc.id ? "Ubah akun" : "Akun baru"} onClose={onClose}>
      <div className="field">
        <label>Nama</label>
        <input value={name} onChange={(e) => setName(e.target.value)} />
      </div>
      <div className="field">
        <label>Jenis</label>
        <select value={type} onChange={(e) => setType(e.target.value as Account["type"])}>
          <option value="cash">Cash</option>
          <option value="bank">Bank</option>
          <option value="ewallet">E-wallet</option>
        </select>
      </div>
      <div className="field">
        <label>Saldo (Rp)</label>
        <input inputMode="numeric" value={balance} onChange={(e) => setBalance(e.target.value.replace(/\D/g, ""))} />
      </div>
      <button className="btn btn-primary btn-block" onClick={submit} disabled={save.isPending || !name}>Simpan</button>
      {acc.id && (
        <button className="btn btn-danger btn-block" onClick={async () => { await remove.mutateAsync(acc.id!); onClose(); }}>
          Hapus
        </button>
      )}
    </Sheet>
  );
}
