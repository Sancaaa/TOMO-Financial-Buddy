import { NavLink, Outlet } from "react-router-dom";
import { Tomato } from "./Tomato";
import { Icon, type IconName } from "./Icon";
import { useAuth } from "../lib/auth";

type Tab = { to: string; label: string; icon: IconName; end: boolean; add?: boolean };

const TABS: Tab[] = [
  { to: "/", label: "Beranda", icon: "home", end: true },
  { to: "/riwayat", label: "Riwayat", icon: "list", end: false },
  { to: "/tambah", label: "Tambah", icon: "plus", add: true, end: false },
  { to: "/analitik", label: "Analitik", icon: "chart", end: false },
  { to: "/kelola", label: "Kelola", icon: "settings", end: false },
];

const ADMIN_TAB: Tab = { to: "/admin", label: "Admin", icon: "award", end: false };

export function Layout() {
  const { logout, user } = useAuth();
  const sideTabs = user?.is_admin ? [...TABS, ADMIN_TAB] : TABS;

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
            {sideTabs.map((t) => (
              <NavLink
                key={t.to}
                to={t.to}
                end={t.end}
                className={({ isActive }) => "sidelink" + (isActive ? " active" : "")}
              >
                <span className="ic"><Icon name={t.icon} size={20} /></span>
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
              <span className="badge"><Icon name={t.icon} size={26} stroke={2.2} /></span>
            ) : (
              <>
                <span className="ic"><Icon name={t.icon} size={22} /></span>
                <span>{t.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </>
  );
}
