import { useState } from "react";
import { login } from "../lib/api";

export function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(username, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal login");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="login">
      <form className="box" onSubmit={submit}>
        <div className="brand">
          <img src="/tomo.svg" width={64} height={64} alt="TOMO" />
          <span className="name">TOMO</span>
          <span className="hint">teman catat keuangan · 友</span>
        </div>
        <div className="field">
          <label>Username</label>
          <input value={username} onChange={(e) => setUsername(e.target.value)} autoComplete="username" />
        </div>
        <div className="field">
          <label>Password</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            autoComplete="current-password"
          />
        </div>
        {error && <div className="err">{error}</div>}
        <button className="btn btn-primary btn-block" disabled={busy || !username || !password}>
          {busy ? "Masuk…" : "Masuk"}
        </button>
      </form>
    </div>
  );
}
