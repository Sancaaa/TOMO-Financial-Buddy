import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { getToken, onTokenChange, setToken } from "./api";

interface AuthCtx {
  authed: boolean;
  logout: () => void;
}

const Ctx = createContext<AuthCtx>({ authed: false, logout: () => {} });

export function AuthProvider({ children }: { children: ReactNode }) {
  const [authed, setAuthed] = useState(() => Boolean(getToken()));

  useEffect(() => onTokenChange((t) => setAuthed(Boolean(t))), []);

  return (
    <Ctx.Provider value={{ authed, logout: () => setToken(null) }}>
      {children}
    </Ctx.Provider>
  );
}

export function useAuth(): AuthCtx {
  return useContext(Ctx);
}
