// Day 10: browser-side auth client.
// Owns: token storage (localStorage), the authenticated fetch wrapper
// (auto-refresh on 401), and the login/register/logout API calls.
//
// SECURITY NOTE (localStorage vs httpOnly cookies): localStorage is readable
// by ANY JavaScript on the page, so an XSS vulnerability means stolen tokens.
// The production pattern is httpOnly cookies (JS cannot read them) set by the
// backend, plus CSRF protection. We accept localStorage here for learning
// simplicity - tradeoff logged in the Learning Sheet backlog ("Token theft").

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const ACCESS_KEY = "access_token";
const REFRESH_KEY = "refresh_token";

// Storage helpers, guarded: modules also execute during server rendering,
// where window/localStorage do not exist.
const store = () =>
  typeof window === "undefined" ? null : window.localStorage;

// The layout (and its AuthNav) stays mounted across page navigations in the
// App Router, so it cannot re-run its own check after we log in/out. Instead,
// token changes broadcast an event; AuthNav listens and re-checks its session.
function notifyAuthChanged(): void {
  if (typeof window !== "undefined") {
    window.dispatchEvent(new Event("auth-changed"));
  }
}

export function getAccessToken(): string | null {
  return store()?.getItem(ACCESS_KEY) ?? null;
}

export function setTokens(access: string, refresh: string): void {
  store()?.setItem(ACCESS_KEY, access);
  store()?.setItem(REFRESH_KEY, refresh);
  notifyAuthChanged();
}

export function clearTokens(): void {
  store()?.removeItem(ACCESS_KEY);
  store()?.removeItem(REFRESH_KEY);
  notifyAuthChanged();
}

// --- Refresh flow ---
// Single in-flight refresh: if three requests 401 at the same moment, naive
// code fires three refreshes - but ROTATION revokes the presented token, so
// two of the three would fail. One shared promise = exactly one refresh,
// and every waiter gets the same result.
let refreshing: Promise<boolean> | null = null;

function refreshTokens(): Promise<boolean> {
  if (!refreshing) {
    refreshing = (async () => {
      const refresh = store()?.getItem(REFRESH_KEY);
      if (!refresh) return false;
      const res = await fetch(`${API}/auth/refresh`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!res.ok) {
        clearTokens(); // refresh revoked/expired - session is over
        return false;
      }
      const data = await res.json();
      setTokens(data.access_token, data.refresh_token);
      return true;
    })().finally(() => {
      refreshing = null;
    });
  }
  return refreshing;
}

// --- Authenticated fetch ---
// Attaches the Bearer header. On 401 (expired access token): refresh once,
// retry the original request once. Callers never think about token expiry;
// a 401 that comes back from here means "session dead, go to login".
export async function authFetch(
  path: string,
  options: RequestInit = {}
): Promise<Response> {
  const makeRequest = () =>
    fetch(`${API}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...(getAccessToken()
          ? { Authorization: `Bearer ${getAccessToken()}` }
          : {}),
        ...options.headers,
      },
    });

  const res = await makeRequest();
  if (res.status !== 401) return res;

  const refreshed = await refreshTokens();
  if (!refreshed) return res; // caller sees the 401
  return makeRequest(); // one retry with the fresh access token
}

// --- Auth API calls ---

export async function login(email: string, password: string): Promise<void> {
  const res = await fetch(`${API}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) {
    throw new Error((await res.json()).detail ?? "Login failed");
  }
  const data = await res.json();
  setTokens(data.access_token, data.refresh_token);
}

export async function register(
  name: string,
  email: string,
  password: string
): Promise<void> {
  const res = await fetch(`${API}/auth/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name, email, password }),
  });
  if (!res.ok) {
    throw new Error((await res.json()).detail ?? "Registration failed");
  }
  // Register returns the user (not tokens), so log in immediately after.
  await login(email, password);
}

export async function logout(): Promise<void> {
  const refresh = store()?.getItem(REFRESH_KEY);
  if (refresh) {
    // Revoke server-side, then clear locally regardless of the outcome.
    await fetch(`${API}/auth/logout`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: refresh }),
    }).catch(() => {});
  }
  clearTokens();
}

// --- Session ---

export interface Me {
  id: number;
  email: string;
  name: string;
  role: string;
  created_at: string;
}

// Returns null when there is no usable session (no token, expired, or revoked).
export async function fetchMe(): Promise<Me | null> {
  if (!getAccessToken()) return null;
  const res = await authFetch("/users/me");
  if (!res.ok) return null;
  return res.json();
}
