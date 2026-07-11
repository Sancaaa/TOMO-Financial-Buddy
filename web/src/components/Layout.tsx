import { NavLink, Outlet } from "react-router-dom";

const TABS = [
  { to: "/", label: "Beranda", icon: "🏠", end: true },
  { to: "/riwayat", label: "Riwayat", icon: "📋", end: false },
  { to: "/tambah", label: "Tambah", icon: "＋", add: true, end: false },
  { to: "/analitik", label: "Analitik", icon: "📊", end: false },
  { to: "/kelola", label: "Kelola", icon: "⚙️", end: false },
];

export function Layout() {
  return (
    <div className="app">
      <div className="main">
        <Outlet />
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
    </div>
  );
}
