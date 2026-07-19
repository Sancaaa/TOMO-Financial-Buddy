import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { api, getToken, onTokenChange, setToken } from "./api";
import type { CurrentUser } from "./types";

interface AuthCtx {
  authed: boolean;
  user: CurrentUser | null;
  refreshUser: () => void;
  logout: () => void;
}

const Ctx = createContext<AuthCtx>({
  authed: false,
  user: null,
  refreshUser: () => {},
  logout: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authed, setAuthed] = useState(() => Boolean(getToken()));
  const [user, setUser] = useState<CurrentUser | null>(null);

  function loadUser() {
    if (!getToken()) {
      setUser(null);
      return;
    }
    api.get<CurrentUser>("/auth/me").then(setUser).catch(() => setUser(null));
  }

  useEffect(() => {
    loadUser();
    return onTokenChange((t) => {
      setAuthed(Boolean(t));
      loadUser();
    });
  }, []);

  return (
    <Ctx.Provider
      value={{ authed, user, refreshUser: loadUser, logout: () => setToken(null) }}
    >
      {children}
    </Ctx.Provider>
  );
}

export function useAuth(): AuthCtx {
  return useContext(Ctx);
}
