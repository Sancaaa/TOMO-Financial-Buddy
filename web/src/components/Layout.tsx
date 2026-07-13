import { NavLink, Outlet } from "react-router-dom";
import { Tomato } from "./Tomato";
import { useAuth } from "../lib/auth";

const TABS = [
  { to: "/", label: "Beranda", icon: "🏠", end: true },
  { to: "/riwayat", label: "Riwayat", icon: "📋", end: false },
  { to: "/tambah", label: "Tambah", icon: "＋", add: true, end: false },
  { to: "/analitik", label: "Analitik", icon: "📊", end: false },
  { to: "/kelola", label: "Kelola", icon: "⚙️", end: false },
];

export function Layout() {
  const { logout } = useAuth();

  return (
    <>
      <div className="grain" aria-hidden="true" />
      <div className="shell">
        <aside className="sidebar">
          <div className="brand">
            <Tomato size={34} face />
            <span className="wordmark">TOMO</span>
          </div>
          <nav className="sidenav">
            {TABS.map((t) => (
              <NavLink
                key={t.to}
                to={t.to}
                end={t.end}
                className={({ isActive }) => "sidelink" + (isActive ? " active" : "")}
              >
                <span className="ic">{t.icon}</span>
                <span>{t.label}</span>
              </NavLink>
            ))}
          </nav>
          <div className="side-footer">
            <Tomato size={52} className="deco-t" />
            <span className="hint">teman catat keuangan · 友</span>
            <button className="logout" onClick={logout}>
              Keluar
            </button>
          </div>
        </aside>

        <main className="main">
          <Outlet />
        </main>
      </div>

      <nav className="bottomnav">
        {TABS.map((t) => (
          <NavLink
            key={t.to}
            to={t.to}
            end={t.end}
            className={({ isActive }) =>
              "navitem" + (t.add ? " add" : "") + (isActive ? " active" : "")
            }
          >
            {t.add ? (
              <span className="badge">{t.icon}</span>
            ) : (
              <>
                <span className="ic">{t.icon}</span>
                <span>{t.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </>
  );
}
