const BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? "";
const TOKEN_KEY = "tomo_token";

let token: string | null = localStorage.getItem(TOKEN_KEY);
const listeners = new Set<(t: string | null) => void>();

export function getToken(): string | null {
  return token;
}

export function setToken(t: string | null): void {
  token = t;
  if (t) localStorage.setItem(TOKEN_KEY, t);
  else localStorage.removeItem(TOKEN_KEY);
  listeners.forEach((fn) => fn(t));
}

export function onTokenChange(fn: (t: string | null) => void): () => void {
  listeners.add(fn);
  return () => listeners.delete(fn);
}

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

async function req<T>(path: string, opts: RequestInit = {}): Promise<T> {
  const headers = new Headers(opts.headers);
  if (token) headers.set("Authorization", `Bearer ${token}`);
  if (opts.body && !(opts.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(BASE + path, { ...opts, headers });
  if (res.status === 401) {
    setToken(null);
    throw new ApiError(401, "Sesi berakhir, silakan login lagi.");
  }
  if (!res.ok) {
    let detail: string = res.statusText;
    try {
      const body = await res.json();
      if (typeof body.detail === "string") detail = body.detail;
    } catch {
      /* ignore */
    }
    throw new ApiError(res.status, detail);
  }
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

export const api = {
  get: <T>(path: string) => req<T>(path),
  post: <T>(path: string, body?: unknown) =>
    req<T>(path, {
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
    }),
  postForm: <T>(path: string, form: FormData) =>
    req<T>(path, { method: "POST", body: form }),
  put: <T>(path: string, body: unknown) =>
    req<T>(path, { method: "PUT", body: JSON.stringify(body) }),
  patch: <T>(path: string, body: unknown) =>
    req<T>(path, { method: "PATCH", body: JSON.stringify(body) }),
  del: (path: string) => req<void>(path, { method: "DELETE" }),
};

export async function downloadCsv(month?: string): Promise<void> {
  const qs = month ? `?month=${month}` : "";
  const res = await fetch(BASE + `/export${qs}`, {
    headers: token ? { Authorization: `Bearer ${token}` } : {},
  });
  if (!res.ok) throw new ApiError(res.status, "Gagal export");
  const blob = await res.blob();
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = `tomo-${month || "semua"}.csv`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

export async function login(username: string, password: string): Promise<void> {
  const body = new URLSearchParams({ username, password });
  const res = await fetch(BASE + "/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body,
  });
  if (!res.ok) throw new ApiError(res.status, "Username atau password salah.");
  const data = (await res.json()) as { access_token: string };
  setToken(data.access_token);
}
