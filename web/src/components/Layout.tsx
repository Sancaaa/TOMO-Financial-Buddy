import { useState } from "react";
import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";
import { Tomato } from "./Tomato";
import { Icon, type IconName } from "./Icon";
import { Sheet } from "./Sheet";
import { useAuth } from "../lib/auth";

type Tab = { to: string; label: string; icon: IconName; end: boolean; add?: boolean };

// Bottom-nav utama (mobile): tepat 4 + burger = 5 tombol, "Tambah" di tengah.
const PRIMARY: Tab[] = [
  { to: "/", label: "Beranda", icon: "home", end: true },
  { to: "/riwayat", label: "Riwayat", icon: "list", end: false },
  { to: "/tambah", label: "Tambah", icon: "plus", add: true, end: false },
  { to: "/analitik", label: "Analitik", icon: "chart", end: false },
];

// Item sekunder — di desktop tampil di sidebar, di mobile masuk burger.
const MENU: Tab[] = [{ to: "/kelola", label: "Kelola", icon: "settings", end: false }];
const ADMIN_TAB: Tab = { to: "/admin", label: "Admin", icon: "award", end: false };

export function Layout() {
  const { logout, user } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const menuTabs = user?.is_admin ? [...MENU, ADMIN_TAB] : MENU;
  const sideTabs = [...PRIMARY, ...menuTabs]; // sidebar desktop: semua
  const menuActive = menuTabs.some((t) => location.pathname.startsWith(t.to));

  function goMenu(to: string) {
    setMenuOpen(false);
    navigate(to);
  }

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
        {PRIMARY.map((t) => (
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
        <button
          type="button"
          className={"navitem" + (menuActive ? " active" : "")}
          onClick={() => setMenuOpen(true)}
          aria-label="Menu lainnya"
        >
          <span className="ic"><Icon name="menu" size={22} /></span>
          <span>Menu</span>
        </button>
      </nav>

      {menuOpen && (
        <Sheet title="Menu" onClose={() => setMenuOpen(false)}>
          <div className="menu-list">
            {menuTabs.map((t) => (
              <button
                key={t.to}
                className={"menu-row" + (location.pathname.startsWith(t.to) ? " active" : "")}
                onClick={() => goMenu(t.to)}
              >
                <span className="ic"><Icon name={t.icon} size={20} /></span>
                <span>{t.label}</span>
              </button>
            ))}
            <button
              className="menu-row divide"
              onClick={() => {
                setMenuOpen(false);
                logout();
              }}
            >
              <span className="ic"><Icon name="logout" size={20} /></span>
              <span>Keluar</span>
            </button>
          </div>
        </Sheet>
      )}
    </>
  );
}
