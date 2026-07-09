'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { usePathname, useRouter } from 'next/navigation';

import api from '@/lib/api';
import { navForRole } from '@/lib/roles';
import type { Me } from '@/lib/types';

interface SessionCtx {
  me: Me | null;
  role: string | undefined;
  name: string | undefined;
  nav: string[];
  loading: boolean;
  refresh: () => Promise<void>;
  logout: () => Promise<void>;
}

const Ctx = createContext<SessionCtx | null>(null);

/**
 * Server session (EPIC G1) — hydrates identity from GET /auth/me and exposes
 * role/nav to the shell. Replaces the old client-side RoleProvider toggle. If
 * the session is missing/expired on a protected route, it redirects to /login
 * (belt-and-suspenders with middleware.ts, which only checks cookie presence).
 */
export function SessionProvider({ children }: { children: ReactNode }) {
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  const refresh = useCallback(async () => {
    try {
      setMe(await api.get<Me>('/auth/me'));
    } catch {
      setMe(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void refresh();
  }, [refresh]);

  // Client-side guard: authenticated pages need a valid session.
  useEffect(() => {
    if (!loading && me === null && pathname !== '/login') {
      router.replace('/login');
    }
  }, [loading, me, pathname, router]);

  const logout = useCallback(async () => {
    try {
      await api.post('/auth/logout');
    } catch {
      /* ignore — clear locally regardless */
    }
    setMe(null);
    router.replace('/login');
  }, [router]);

  const value = useMemo<SessionCtx>(
    () => ({
      me,
      role: me?.role,
      name: me?.name,
      nav: navForRole(me?.role),
      loading,
      refresh,
      logout,
    }),
    [me, loading, refresh, logout],
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useSession(): SessionCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useSession must be used within SessionProvider');
  return ctx;
}
