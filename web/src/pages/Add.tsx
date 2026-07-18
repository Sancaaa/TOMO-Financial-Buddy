import { useRef, useState } from "react";
import { PageHead } from "../components/PageHead";
import { rupiah, todayInput } from "../lib/format";
import {
  useAccounts,
  useCategories,
  useCreateTransaction,
  useOcr,
  useQuickAdd,
  useTransfer,
} from "../lib/queries";
import type { OCRResult } from "../lib/types";

type Mode = "quick" | "form" | "ocr" | "transfer";

export function Add() {
  const [mode, setMode] = useState<Mode>("quick");
  const [flash, setFlash] = useState("");

  return (
    <div className="narrow-sm">
      <PageHead eyebrow="catat pengeluaran" title="Tambah" />
      <div className="seg">
        <button className={mode === "quick" ? "active" : ""} onClick={() => setMode("quick")}>Cepat</button>
        <button className={mode === "form" ? "active" : ""} onClick={() => setMode("form")}>Form</button>
        <button className={mode === "ocr" ? "active" : ""} onClick={() => setMode("ocr")}>Struk 📸</button>
        <button className={mode === "transfer" ? "active" : ""} onClick={() => setMode("transfer")}>Transfer</button>
      </div>

      {flash && <div className="card pad-sm" style={{ color: "var(--leaf-dark)" }}>✅ {flash}</div>}

      {mode === "quick" && <QuickMode onDone={setFlash} />}
      {mode === "form" && <FormMode onDone={setFlash} />}
      {mode === "ocr" && <OcrMode onDone={setFlash} />}
      {mode === "transfer" && <TransferMode onDone={setFlash} />}
    </div>
  );
}

function QuickMode({ onDone }: { onDone: (s: string) => void }) {
  const quick = useQuickAdd();
  const [text, setText] = useState("");
  const [err, setErr] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    try {
      const tx = await quick.mutateAsync(text);
      onDone(`${rupiah(tx.amount)} — ${tx.category?.name ?? "tercatat"}`);
      setText("");
    } catch (e2) {
      setErr(e2 instanceof Error ? e2.message : "Gagal");
    }
  }

  return (
    <form className="card stack" onSubmit={submit}>
      <div className="field">
        <label>Ketik cepat</label>
        <input placeholder="makan 15k / gojek 24rb / dapet 50k" value={text} onChange={(e) => setText(e.target.value)} />
        <span className="hint">Nominal, kategori, dan tanggal ditebak otomatis.</span>
      </div>
      {err && <div className="err">{err}</div>}
      <button className="btn btn-primary btn-block" disabled={quick.isPending || !text.trim()}>
        {quick.isPending ? "Menyimpan…" : "Catat"}
      </button>
    </form>
  );
}

function FormMode({ onDone }: { onDone: (s: string) => void }) {
  const { data: categories } = useCategories();
  const { data: accounts } = useAccounts();
  const create = useCreateTransaction();

  const [type, setType] = useState<"expense" | "income">("expense");
  const [amount, setAmount] = useState("");
  const [categoryId, setCategoryId] = useState("");
  const [accountId, setAccountId] = useState("");
  const [date, setDate] = useState(todayInput());
  const [description, setDescription] = useState("");

  const catOptions = (categories ?? []).filter((c) => c.type === type);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    await create.mutateAsync({
      type,
      amount: Number(amount),
      category_id: categoryId ? Number(categoryId) : null,
      account_id: accountId ? Number(accountId) : null,
      description: description || null,
      occurred_at: new Date(date + "T12:00:00").toISOString(),
      source: "web",
    });
    onDone(`${rupiah(amount)} tercatat`);
    setAmount("");
    setDescription("");
  }

  return (
    <form className="card stack" onSubmit={submit}>
      <div className="seg">
        <button type="button" className={type === "expense" ? "active" : ""} onClick={() => setType("expense")}>Pengeluaran</button>
        <button type="button" className={type === "income" ? "active" : ""} onClick={() => setType("income")}>Pemasukan</button>
      </div>
      <div className="field">
        <label>Jumlah (Rp)</label>
        <input inputMode="numeric" value={amount} onChange={(e) => setAmount(e.target.value.replace(/\D/g, ""))} />
      </div>
      <div className="row">
        <div className="field">
          <label>Kategori</label>
          <select value={categoryId} onChange={(e) => setCategoryId(e.target.value)}>
            <option value="">— tanpa —</option>
            {catOptions.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div className="field">
          <label>Akun</label>
          <select value={accountId} onChange={(e) => setAccountId(e.target.value)}>
            <option value="">— tanpa —</option>
            {(accounts ?? []).map((a) => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>
        </div>
      </div>
      <div className="row">
        <div className="field">
          <label>Tanggal</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        </div>
        <div className="field">
          <label>Deskripsi</label>
          <input value={description} onChange={(e) => setDescription(e.target.value)} />
        </div>
      </div>
      <button className="btn btn-primary btn-block" disabled={create.isPending || !amount}>
        {create.isPending ? "Menyimpan…" : "Simpan"}
      </button>
    </form>
  );
}

function OcrMode({ onDone }: { onDone: (s: string) => void }) {
  const ocr = useOcr();
  const create = useCreateTransaction();
  const { data: accounts } = useAccounts();
  const fileRef = useRef<HTMLInputElement>(null);
  const [result, setResult] = useState<OCRResult | null>(null);
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [accountId, setAccountId] = useState("");
  const [err, setErr] = useState("");

  async function onFile(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    setErr("");
    setResult(null);
    try {
      const res = await ocr.mutateAsync(file);
      setResult(res);
      if (res.draft) {
        setAmount(res.draft.amount ? String(Math.round(Number(res.draft.amount))) : "");
        setDescription(res.draft.description ?? "");
        setCategoryId(res.draft.category_id);
      }
    } catch (e2) {
      setErr(e2 instanceof Error ? e2.message : "Gagal membaca struk");
    }
  }

  async function confirm() {
    if (!result?.draft) return;
    // account_id wajib ada agar saldo ikut berkurang (tanpa akun, apply_balance no-op).
    const resolvedAccount = accountId ? Number(accountId) : accounts?.[0]?.id ?? null;
    await create.mutateAsync({
      type: "expense",
      amount: Number(amount),
      category_id: categoryId,
      account_id: resolvedAccount,
      description: description || null,
      occurred_at: result.draft.occurred_at,
      source: "ocr",
      receipt_id: result.receipt_id,
    });
    onDone(`${rupiah(amount)} dari struk`);
    setResult(null);
    if (fileRef.current) fileRef.current.value = "";
  }

  return (
    <div className="card stack">
      <input ref={fileRef} type="file" accept="image/*" capture="environment" onChange={onFile} hidden />
      <button className="btn btn-primary btn-block" onClick={() => fileRef.current?.click()} disabled={ocr.isPending}>
        {ocr.isPending ? "Membaca struk…" : "📸 Pilih / foto struk"}
      </button>
      {ocr.isPending && <div className="center"><span className="spinner" /><span className="hint">Tomo lagi baca strukmu…</span></div>}
      {err && <div className="err">{err}</div>}

      {result && !result.draft && (
        <p className="hint">Struk belum terbaca jelas. Coba foto lebih terang, atau pakai tab Form.</p>
      )}

      {result?.draft && (
        <>
          <div className="between">
            <span className="hint">{result.merchant ?? "Struk"}</span>
            <span className="pill">yakin {Math.round(result.confidence * 100)}%</span>
          </div>
          <div className="field">
            <label>Jumlah (Rp)</label>
            <input inputMode="numeric" value={amount} onChange={(e) => setAmount(e.target.value.replace(/\D/g, ""))} />
          </div>
          <div className="field">
            <label>Deskripsi</label>
            <input value={description} onChange={(e) => setDescription(e.target.value)} />
          </div>
          <div className="field">
            <label>Akun</label>
            <select
              value={accountId || (accounts?.[0] ? String(accounts[0].id) : "")}
              onChange={(e) => setAccountId(e.target.value)}
            >
              {(accounts ?? []).map((a) => (
                <option key={a.id} value={a.id}>{a.name}</option>
              ))}
            </select>
            <span className="hint">Saldo akun ini yang akan berkurang.</span>
          </div>
          <button className="btn btn-primary btn-block" onClick={confirm} disabled={create.isPending || !amount}>
            {create.isPending ? "Menyimpan…" : "Simpan transaksi"}
          </button>
        </>
      )}
    </div>
  );
}

function TransferMode({ onDone }: { onDone: (s: string) => void }) {
  const { data: accounts } = useAccounts();
  const transfer = useTransfer();
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const [amount, setAmount] = useState("");
  const [description, setDescription] = useState("");
  const [err, setErr] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    if (from === to) {
      setErr("Akun asal dan tujuan harus beda.");
      return;
    }
    try {
      await transfer.mutateAsync({
        amount: Number(amount),
        account_id: Number(from),
        dest_account_id: Number(to),
        description: description || null,
      });
      const names = (accounts ?? []).reduce<Record<string, string>>((m, a) => ((m[a.id] = a.name), m), {});
      onDone(`${rupiah(amount)} dipindah ${names[from]} → ${names[to]}`);
      setAmount("");
      setDescription("");
    } catch (e2) {
      setErr(e2 instanceof Error ? e2.message : "Gagal");
    }
  }

  return (
    <form className="card stack" onSubmit={submit}>
      <div className="row">
        <div className="field">
          <label>Dari akun</label>
          <select value={from} onChange={(e) => setFrom(e.target.value)}>
            <option value="">— pilih —</option>
            {(accounts ?? []).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        </div>
        <div className="field">
          <label>Ke akun</label>
          <select value={to} onChange={(e) => setTo(e.target.value)}>
            <option value="">— pilih —</option>
            {(accounts ?? []).map((a) => <option key={a.id} value={a.id}>{a.name}</option>)}
          </select>
        </div>
      </div>
      <div className="field">
        <label>Jumlah (Rp)</label>
        <input inputMode="numeric" value={amount} onChange={(e) => setAmount(e.target.value.replace(/\D/g, ""))} />
      </div>
      <div className="field">
        <label>Catatan</label>
        <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="opsional" />
      </div>
      {err && <div className="err">{err}</div>}
      <button className="btn btn-primary btn-block" disabled={transfer.isPending || !amount || !from || !to}>
        {transfer.isPending ? "Memindahkan…" : "Pindahkan"}
      </button>
    </form>
  );
}
