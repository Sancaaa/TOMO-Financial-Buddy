import { useState } from "react";
import { login } from "../lib/api";
import { Tomato } from "../components/Tomato";

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
      <div className="grain" aria-hidden="true" />
      <Tomato size={90} className="deco-float deco-1" />
      <Tomato size={64} className="deco-float deco-2" />
      <div className="box">
        <div className="brand-hero">
          <Tomato size={72} face />
          <p className="eyebrow">teman keuanganmu · 友</p>
          <h1 className="title">
            <em>Tomo</em> di sini.
          </h1>
        </div>
        <form className="card" onSubmit={submit}>
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
    </div>
  );
}
