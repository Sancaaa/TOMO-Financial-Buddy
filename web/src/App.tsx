import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./lib/auth";
import { Layout } from "./components/Layout";
import { Login } from "./pages/Login";
import { Dashboard } from "./pages/Dashboard";
import { History } from "./pages/History";
import { Add } from "./pages/Add";
import { Analytics } from "./pages/Analytics";
import { Manage } from "./pages/Manage";
import { Admin } from "./pages/Admin";

export function App() {
  const { authed, user } = useAuth();

  if (!authed) {
    return (
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    );
  }

  return (
    <Routes>
      <Route path="/login" element={<Navigate to="/" replace />} />
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/riwayat" element={<History />} />
        <Route path="/tambah" element={<Add />} />
        <Route path="/analitik" element={<Analytics />} />
        <Route path="/kelola" element={<Manage />} />
        <Route
          path="/admin"
          element={user?.is_admin ? <Admin /> : <Navigate to="/" replace />}
        />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}
