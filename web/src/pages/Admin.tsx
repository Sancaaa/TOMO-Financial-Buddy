import { useState } from "react";
import { PageHead } from "../components/PageHead";
import { Icon } from "../components/Icon";
import {
  useAdminUsers,
  useCreateUser,
  useDeleteUser,
  useUpdateUser,
} from "../lib/queries";
import { useAuth } from "../lib/auth";
import type { AdminUser } from "../lib/types";

export function Admin() {
  const { user: me } = useAuth();
  const { data: users } = useAdminUsers();
  const create = useCreateUser();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [isAdmin, setIsAdmin] = useState(false);
  const [err, setErr] = useState("");
  const [flash, setFlash] = useState("");

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr("");
    setFlash("");
    try {
      await create.mutateAsync({ username, password, is_admin: isAdmin });
      setFlash(`User "${username}" dibuat.`);
      setUsername("");
      setPassword("");
      setIsAdmin(false);
    } catch (e2) {
      setErr(e2 instanceof Error ? e2.message : "Gagal membuat user");
    }
  }

  return (
    <div className="narrow">
      <PageHead eyebrow="admin" title="Kelola User" />

      {flash && (
        <div
          className="card pad-sm ico-txt"
          style={{ color: "var(--leaf-dark)" }}
        >
          <Icon name="check" size={18} /> {flash}
        </div>
      )}

      <form className="card stack" onSubmit={submit}>
        <p className="eyebrow-sm">tambah user baru</p>
        <div className="row">
          <div className="field">
            <label>Username</label>
            <input
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="off"
            />
          </div>
          <div className="field">
            <label>Password (min 8)</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="new-password"
            />
          </div>
        </div>
        <label className="ico-txt" style={{ fontSize: 14 }}>
          <input
            type="checkbox"
            checked={isAdmin}
            onChange={(e) => setIsAdmin(e.target.checked)}
          />
          Jadikan admin
        </label>
        {err && <div className="err">{err}</div>}
        <button
          className="btn btn-primary btn-block"
          disabled={create.isPending || !username || password.length < 8}
        >
          {create.isPending ? "Membuat…" : "Buat user"}
        </button>
      </form>

      <div className="card">
        <div className="section-title">{(users ?? []).length} user</div>
        <div className="txlist">
          {(users ?? []).map((u) => (
            <UserRow key={u.id} u={u} selfId={me?.id} />
          ))}
        </div>
      </div>
    </div>
  );
}

function UserRow({ u, selfId }: { u: AdminUser; selfId?: number }) {
  const update = useUpdateUser();
  const remove = useDeleteUser();
  const [busy, setBusy] = useState(false);

  async function resetPassword() {
    const pw = prompt(`Password baru untuk "${u.username}" (min 8):`);
    if (!pw) return;
    if (pw.length < 8) return alert("Minimal 8 karakter.");
    setBusy(true);
    try {
      await update.mutateAsync({ id: u.id, body: { password: pw } });
      alert("Password direset.");
    } catch (e) {
      alert(e instanceof Error ? e.message : "Gagal");
    } finally {
      setBusy(false);
    }
  }

  async function del() {
    if (
      !confirm(
        `Hapus user "${u.username}" beserta semua datanya? Proses ini tidak bisa dibatalkan.`,
      )
    )
      return;
    setBusy(true);
    try {
      await remove.mutateAsync(u.id);
    } catch (e) {
      alert(e instanceof Error ? e.message : "Gagal");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="tx" style={{ cursor: "default" }}>
      <span
        className="cat-badge"
        style={
          {
            "--c": u.is_admin ? "var(--tomato)" : "var(--ink-muted)",
          } as React.CSSProperties
        }
      >
        <Icon name={u.is_admin ? "award" : "wallet"} size={18} />
      </span>
      <span className="body">
        <span className="desc ico-txt">
          {u.username}
          {u.id === selfId && <span className="pill">kamu</span>}
        </span>
        <span className="meta">
          {u.is_admin ? "Admin · " : ""}
          {u.tx_count} transaksi · Telegram{" "}
          {u.telegram_linked ? "tertaut" : "belum"}
        </span>
      </span>
      <span style={{ display: "flex", gap: 6 }}>
        <button className="btn btn-sm" onClick={resetPassword} disabled={busy}>
          Reset PW
        </button>
        {u.id !== selfId && (
          <button
            className="btn btn-sm btn-danger"
            onClick={del}
            disabled={busy}
          >
            Hapus
          </button>
        )}
      </span>
    </div>
  );
}
