'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import Logo from '@/components/brand/Logo';
import { useSession } from '@/components/SessionProvider';
import api from '@/lib/api';
import { ROLE_LABEL_KEY, type Role } from '@/lib/roles';
import type { Me } from '@/lib/types';

const DEMO_PASSWORD = 'qalam2026';

/** The 5 живых demo users (mirrors backend SEED_USERS) for 2-click quick login. */
const QUICK_USERS: Array<{ username: string; name: string; role: Role }> = [
  { username: 'director', name: 'Ерлан', role: 'chief' },
  { username: 'economist', name: 'Айгерім', role: 'economist' },
  { username: 'statistician', name: 'Дана', role: 'statistician' },
  { username: 'curator', name: 'Марат', role: 'curator' },
  { username: 'admin', name: 'Админ', role: 'admin' },
];

/**
 * Login (EPIC G1) — Qalam style: white, logo, one 1px-framed card, kk-first.
 * Rendered outside AppShell (no sidebar). Real password field (wrong password →
 * 401 message) plus five quick-login buttons for fast demo user-switching.
 */
export default function LoginPage() {
  const { t } = useTranslation();
  const router = useRouter();
  const { refresh } = useSession();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);

  const doLogin = async (u: string, p: string) => {
    if (busy) return;
    setBusy(true);
    setError(false);
    try {
      await api.post<Me>('/auth/login', { username: u, password: p });
      await refresh();
      router.replace('/overview');
    } catch {
      setError(true);
      setBusy(false);
    }
  };

  return (
    <div className="relative flex min-h-screen items-center justify-center bg-paper px-6">
      <span aria-hidden className="fill-dots-faint pointer-events-none absolute inset-0" />
      <div className="relative w-full max-w-sm">
        <div className="mb-8 flex flex-col items-center gap-2">
          <Logo height={28} />
          <p className="label-micro">{t('app.org')}</p>
        </div>

        <form
          onSubmit={(e) => {
            e.preventDefault();
            void doLogin(username, password);
          }}
          className="space-y-4 border border-ink p-6"
        >
          <h1 className="font-display text-h3 text-ink">{t('auth.sign_in')}</h1>

          <label className="block space-y-1">
            <span className="label-micro">{t('auth.username')}</span>
            <input
              autoFocus
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              autoComplete="username"
              className="w-full border border-ink/40 bg-paper px-3 py-2 font-mono text-secondary text-ink focus:border-ink focus:outline-none"
            />
          </label>

          <label className="block space-y-1">
            <span className="label-micro">{t('auth.password')}</span>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              autoComplete="current-password"
              className="w-full border border-ink/40 bg-paper px-3 py-2 font-mono text-secondary text-ink focus:border-ink focus:outline-none"
            />
          </label>

          {error ? (
            <p className="border-l-2 border-ink px-3 py-1.5 text-secondary text-ink/80">
              ! {t('auth.error')}
            </p>
          ) : null}

          <button
            type="submit"
            disabled={busy}
            className="w-full bg-ink px-4 py-2.5 text-secondary font-medium text-paper transition-colors duration-150 hover:bg-ink/80 disabled:opacity-40"
          >
            {busy ? t('common.loading') : t('auth.sign_in')}
          </button>
        </form>

        <div className="mt-6 space-y-2">
          <p className="label-micro">{t('auth.quick_login')}</p>
          <div className="border border-ink/15">
            {QUICK_USERS.map((u, i) => (
              <button
                key={u.username}
                type="button"
                disabled={busy}
                onClick={() => void doLogin(u.username, DEMO_PASSWORD)}
                className={`flex w-full items-center justify-between px-4 py-2.5 text-left transition-colors duration-150 hover:bg-ink/[.03] disabled:opacity-40 ${
                  i > 0 ? 'border-t border-ink/[.08]' : ''
                }`}
              >
                <span className="text-secondary text-ink">{u.name}</span>
                <span className="label-micro">{t(ROLE_LABEL_KEY[u.role])}</span>
              </button>
            ))}
          </div>
          <p className="label-micro text-ink/40">{t('auth.demo_hint')}</p>
        </div>
      </div>
    </div>
  );
}
