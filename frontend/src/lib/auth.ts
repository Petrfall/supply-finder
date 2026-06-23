// Frontend-only access gate. This is a demo lock to keep casual visitors out of
// the UI — it is NOT real security: the credentials live in the bundle and the
// /api/* endpoints stay open. For a real deployment, move auth to the backend.
const AUTH_KEY = "sf_auth";

// Default demo credentials. Can be overridden at build time via Vite env.
const USER = import.meta.env.VITE_AUTH_USER ?? "admin";
const PASS = import.meta.env.VITE_AUTH_PASS ?? "12345";

export function isAuthed(): boolean {
  return localStorage.getItem(AUTH_KEY) === "1";
}

/** Check credentials; on success persist the flag. Returns whether it matched. */
export function login(user: string, pass: string): boolean {
  if (user === USER && pass === PASS) {
    localStorage.setItem(AUTH_KEY, "1");
    return true;
  }
  return false;
}

export function logout(): void {
  localStorage.removeItem(AUTH_KEY);
}
