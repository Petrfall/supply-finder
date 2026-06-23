import { useState } from "react";
import { login } from "../lib/auth";
import { t, type Lang } from "../lib/i18n";

export function LoginPage({
  lang,
  onLogin,
}: {
  lang: Lang;
  onLogin: () => void;
}) {
  const tr = t[lang];
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [error, setError] = useState(false);

  function submit(e: React.FormEvent) {
    e.preventDefault();
    if (login(user, pass)) {
      onLogin();
    } else {
      setError(true);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center px-4">
      <form onSubmit={submit} className="card w-full max-w-sm p-6">
        <span className="font-mono text-sm font-semibold text-white">
          supplier<span className="text-brand">.finder</span>
        </span>
        <h1 className="mt-4 text-xl font-bold text-white">{tr.loginTitle}</h1>
        <p className="mt-1 text-sm text-muted">{tr.loginSubtitle}</p>

        <label className="mt-5 block">
          <span className="mb-1 block text-xs text-muted">{tr.loginUser}</span>
          <input
            className="input"
            value={user}
            onChange={(e) => {
              setUser(e.target.value);
              setError(false);
            }}
            autoFocus
            autoComplete="username"
          />
        </label>

        <label className="mt-3 block">
          <span className="mb-1 block text-xs text-muted">{tr.loginPass}</span>
          <input
            className="input"
            type="password"
            value={pass}
            onChange={(e) => {
              setPass(e.target.value);
              setError(false);
            }}
            autoComplete="current-password"
          />
        </label>

        {error && (
          <div className="mt-3 rounded-lg border border-red-500/40 bg-red-500/10 p-2 text-sm text-red-300">
            {tr.loginError}
          </div>
        )}

        <button type="submit" className="btn mt-5 w-full">
          {tr.loginBtn}
        </button>
      </form>
    </div>
  );
}
