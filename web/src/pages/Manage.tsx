import { useState } from "react";
import { Sheet } from "../components/Sheet";
import { PageHead } from "../components/PageHead";
import { BudgetBar } from "../components/BudgetBar";
import { Tomato } from "../components/Tomato";
import { categoryColor } from "../lib/colors";
import { rupiah } from "../lib/format";
import {
  useAccounts,
  useBudgets,
  useCategories,
  useContributeGoal,
  useDeleteAccount,
  useDeleteCategory,
  useDeleteGoal,
  useDeleteRecurring,
  useGoals,
  useReconcile,
  useRecurring,
  useSaveAccount,
  useSaveCategory,
  useSaveGoal,
  useSaveRecurring,
  useSetBudget,
} from "../lib/queries";
import type { Account, Category, SavingGoal } from "../lib/types";

export function Manage() {
  const { data: categories } = useCategories();
  const { data: accounts } = useAccounts();
  const reconcile = useReconcile();
  const [editCat, setEditCat] = useState<Partial<Category> | null>(null);
  const [editAcc, setEditAcc] = useState<Partial<Account> | null>(null);
  const [reconMsg, setReconMsg] = useState("");

  async function doReconcile() {
    setReconMsg("");
    const r = await reconcile.mutateAsync();
    setReconMsg(
      r.corrected === 0
        ? "Saldo semua akun sudah cocok ✓"
        : `${r.corrected} akun disesuaikan dengan riwayat transaksi.`,
    );
  }

  return (
    <>
      <PageHead eyebrow="atur" title="Kelola" />

      <div className="cols">
        <div className="col">
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
        </div>
        <div className="col">
      <div className="card">
        <div className="between" style={{ marginBottom: 8 }}>
          <div className="section-title" style={{ margin: 0 }}>Akun</div>
          <div style={{ display: "flex", gap: 6 }}>
            <button className="btn btn-sm" onClick={doReconcile} disabled={reconcile.isPending}>
              {reconcile.isPending ? "…" : "Cocokkan saldo"}
            </button>
            <button className="btn btn-sm" onClick={() => setEditAcc({ type: "cash" })}>+ Tambah</button>
          </div>
        </div>
        {reconMsg && <p className="hint" style={{ marginBottom: 8 }}>{reconMsg}</p>}
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
        <p className="hint" style={{ marginTop: 6 }}>
          "Cocokkan saldo" menghitung ulang saldo dari riwayat transaksi.
        </p>
      </div>
        </div>
      </div>

      <div className="cols">
        <div className="col">
          <BudgetTotalCard />
        </div>
        <div className="col">
          <RecurringCard />
        </div>
      </div>

      <GoalsCard />

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
  const [rollover, setRollover] = useState(cat.budget_rollover ?? false);

  async function submit() {
    await save.mutateAsync({
      id: cat.id,
      body: {
        name,
        type,
        monthly_budget: budget ? Number(budget) : null,
        budget_rollover: rollover,
      },
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
      {type === "expense" && (
        <label style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 14, color: "var(--ink-soft)" }}>
          <input type="checkbox" checked={rollover} onChange={(e) => setRollover(e.target.checked)} style={{ width: "auto" }} />
          Rollover — sisa budget bulan lalu ditambah ke bulan ini
        </label>
      )}
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

function BudgetTotalCard() {
  const { data } = useBudgets();
  const set = useSetBudget();
  const [amount, setAmount] = useState("");
  const current = data?.total_budget_explicit ? data.total_budget : null;

  async function save() {
    await set.mutateAsync({ category_id: null, amount: Number(amount) });
    setAmount("");
  }

  return (
    <div className="card stack">
      <div className="section-title">Budget total bulanan</div>
      <p className="hint">
        Dipakai menghitung "sisa aman/hari".{current ? ` Sekarang: ${rupiah(current)}.` : ""}
      </p>
      <div className="row" style={{ gap: 8, alignItems: "flex-end" }}>
        <div className="field" style={{ flex: 3 }}>
          <input
            inputMode="numeric"
            placeholder={current ? String(Math.round(Number(current))) : "mis. 2000000"}
            value={amount}
            onChange={(e) => setAmount(e.target.value.replace(/\D/g, ""))}
          />
        </div>
        <button className="btn btn-primary" onClick={save} disabled={set.isPending || !amount}>
          Simpan
        </button>
      </div>
    </div>
  );
}

function RecurringCard() {
  const { data } = useRecurring();
  const del = useDeleteRecurring();
  const [open, setOpen] = useState(false);

  return (
    <div className="card">
      <div className="between" style={{ marginBottom: 8 }}>
        <div className="section-title" style={{ margin: 0 }}>Transaksi berulang</div>
        <button className="btn btn-sm" onClick={() => setOpen(true)}>+ Tambah</button>
      </div>
      <div className="txlist">
        {(data ?? []).map((r) => (
          <div key={r.id} className="tx">
            <span className="body">
              <span className="desc">{r.description || "(tanpa nama)"}</span>
              <span className="meta">tiap tgl {r.day_of_month} · berikutnya {r.next_run}</span>
            </span>
            <span className="amt tabular">{rupiah(r.amount)}</span>
            <button className="btn btn-sm btn-danger" onClick={() => del.mutate(r.id)}>Hapus</button>
          </div>
        ))}
        {(data ?? []).length === 0 && <p className="hint">Belum ada. Mis. kos, langganan.</p>}
      </div>
      {open && <RecurringSheet onClose={() => setOpen(false)} />}
    </div>
  );
}

function RecurringSheet({ onClose }: { onClose: () => void }) {
  const save = useSaveRecurring();
  const { data: categories } = useCategories();
  const { data: accounts } = useAccounts();
  const [amount, setAmount] = useState("");
  const [type, setType] = useState<"expense" | "income">("expense");
  const [categoryId, setCategoryId] = useState("");
  const [accountId, setAccountId] = useState("");
  const [day, setDay] = useState("1");
  const [description, setDescription] = useState("");

  const catOptions = (categories ?? []).filter((c) => c.type === type);

  async function submit() {
    await save.mutateAsync({
      amount: Number(amount),
      type,
      category_id: categoryId ? Number(categoryId) : null,
      account_id: accountId ? Number(accountId) : null,
      description: description || null,
      day_of_month: Math.min(28, Math.max(1, Number(day) || 1)),
    });
    onClose();
  }

  return (
    <Sheet title="Transaksi berulang" onClose={onClose}>
      <div className="seg">
        <button className={type === "expense" ? "active" : ""} onClick={() => setType("expense")}>Pengeluaran</button>
        <button className={type === "income" ? "active" : ""} onClick={() => setType("income")}>Pemasukan</button>
      </div>
      <div className="row">
        <div className="field">
          <label>Jumlah (Rp)</label>
          <input inputMode="numeric" value={amount} onChange={(e) => setAmount(e.target.value.replace(/\D/g, ""))} />
        </div>
        <div className="field">
          <label>Tiap tanggal (1–28)</label>
          <input inputMode="numeric" value={day} onChange={(e) => setDay(e.target.value.replace(/\D/g, ""))} />
        </div>
      </div>
      <div className="row">
        <div className="field">
          <label>Kategori</label>
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
            <option value="">— tanpa —</option>
            {catOptions.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Akun</label>
          <select value={accountId} onChange={(e) => setAccountId(e.target.value)}>
            <option value="">— tanpa —</option>
            {(accounts ?? []).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        </div>
      </div>
      <div className="field">
        <label>Deskripsi</label>
        <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="mis. Kos, Spotify" />
      </div>
      <button className="btn btn-primary btn-block" onClick={submit} disabled={save.isPending || !amount}>Simpan</button>
    </Sheet>
  );
}

function GoalsCard() {
  const { data } = useGoals();
  const del = useDeleteGoal();
  const [editGoal, setEditGoal] = useState<Partial<SavingGoal> | null>(null);
  const [contribute, setContribute] = useState<SavingGoal | null>(null);

  return (
    <div className="card">
      <div className="between" style={{ marginBottom: 8 }}>
        <div className="section-title" style={{ margin: 0 }}>Target nabung 🎯</div>
        <button className="btn btn-sm" onClick={() => setEditGoal({})}>+ Tambah</button>
      </div>
      {(data ?? []).length === 0 && <p className="hint">Belum ada target. Mis. laptop, liburan.</p>}
      <div className="bbars">
        {(data ?? []).map((g) => (
          <div key={g.id} className="stack" style={{ gap: 6 }}>
            <BudgetBar
              label={g.name}
              spent={Number(g.saved_amount)}
              budget={Number(g.target_amount)}
              pct={g.pct}
              status="ok"
            />
            <div style={{ display: "flex", gap: 6, alignItems: "center" }}>
              {g.achieved && <Tomato size={22} face />}
              {g.achieved && <span className="pill">tercapai 🎉</span>}
              {g.target_date && <span className="hint">target {g.target_date}</span>}
              <div style={{ flex: 1 }} />
              <button className="btn btn-sm" onClick={() => setContribute(g)}>Nabung</button>
              <button className="btn btn-sm" onClick={() => setEditGoal(g)}>Edit</button>
              <button className="btn btn-sm btn-danger" onClick={() => del.mutate(g.id)}>Hapus</button>
            </div>
          </div>
        ))}
      </div>
      {editGoal && <GoalSheet goal={editGoal} onClose={() => setEditGoal(null)} />}
      {contribute && <ContributeSheet goal={contribute} onClose={() => setContribute(null)} />}
    </div>
  );
}

function GoalSheet({ goal, onClose }: { goal: Partial<SavingGoal>; onClose: () => void }) {
  const save = useSaveGoal();
  const { data: accounts } = useAccounts();
  const [name, setName] = useState(goal.name ?? "");
  const [target, setTarget] = useState(goal.target_amount ? String(Math.round(Number(goal.target_amount))) : "");
  const [date, setDate] = useState(goal.target_date ?? "");
  const [accountId, setAccountId] = useState(goal.account_id != null ? String(goal.account_id) : "");

  async function submit() {
    await save.mutateAsync({
      id: goal.id,
      body: {
        name,
        target_amount: Number(target),
        target_date: date || null,
        account_id: accountId ? Number(accountId) : null,
      },
    });
    onClose();
  }

  return (
    <Sheet title={goal.id ? "Ubah target" : "Target baru"} onClose={onClose}>
      <div className="field">
        <label>Nama</label>
        <input value={name} onChange={(e) => setName(e.target.value)} placeholder="mis. Laptop baru" />
      </div>
      <div className="row">
        <div className="field">
          <label>Target (Rp)</label>
          <input inputMode="numeric" value={target} onChange={(e) => setTarget(e.target.value.replace(/\D/g, ""))} />
        </div>
        <div className="field">
          <label>Tenggat (opsional)</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
      </div>
      <div className="field">
        <label>Akun tabungan (opsional)</label>
        <select value={accountId} onChange={(e) => setAccountId(e.target.value)}>
          <option value="">— hanya catatan —</option>
          {(accounts ?? []).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
        </select>
        <span className="hint">Kalau dipilih, uang beneran dipindah ke sini saat nabung.</span>
      </div>
      <button className="btn btn-primary btn-block" onClick={submit} disabled={save.isPending || !name || !target}>Simpan</button>
    </Sheet>
  );
}

function ContributeSheet({ goal, onClose }: { goal: SavingGoal; onClose: () => void }) {
  const contribute = useContributeGoal();
  const { data: accounts } = useAccounts();
  const [amount, setAmount] = useState("");
  const [err, setErr] = useState("");
  // sumber tidak boleh sama dengan akun tabungan target
  const sources = (accounts ?? []).filter((a) => a.id !== goal.account_id);
  const [fromId, setFromId] = useState("");
  const linked = goal.account_id != null;
  const savingsAcc = (accounts ?? []).find((a) => a.id === goal.account_id);

  async function go(sign: number) {
    setErr("");
    try {
      await contribute.mutateAsync({
        id: goal.id,
        amount: sign * Number(amount),
        from_account_id: linked && fromId ? Number(fromId) : null,
      });
      onClose();
    } catch (e) {
      setErr(e instanceof Error ? e.message : "Gagal");
    }
  }

  return (
    <Sheet title={`Nabung: ${goal.name}`} onClose={onClose}>
      <p className="hint">Terkumpul {rupiah(goal.saved_amount)} dari {rupiah(goal.target_amount)}.</p>
      {linked ? (
        <div className="field">
          <label>Ambil dari akun</label>
          <select value={fromId} onChange={(e) => setFromId(e.target.value)}>
            <option value="">— hanya catat progres —</option>
            {sources.map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
          <span className="hint">Uang dipindah {savingsAcc ? `ke ${savingsAcc.name}` : "ke akun tabungan"}.</span>
        </div>
      ) : (
        <p className="hint">Target ini belum terhubung akun tabungan — progres cuma dicatat. Hubungkan lewat "Edit" untuk memindah uang beneran.</p>
      )}
      <div className="field">
        <label>Jumlah (Rp)</label>
        <input inputMode="numeric" value={amount} onChange={(e) => setAmount(e.target.value.replace(/\D/g, ""))} />
      </div>
      {err && <div className="err">{err}</div>}
      <div className="row">
        <button className="btn btn-primary" onClick={() => go(1)} disabled={contribute.isPending || !amount}>+ Nabung</button>
        <button className="btn" onClick={() => go(-1)} disabled={contribute.isPending || !amount}>− Tarik</button>
      </div>
    </Sheet>
  );
}
