'use client';

import { createContext, useContext, useMemo, useState, type ReactNode } from 'react';

/** The 4 demo roles (docs/13 §2 core ring). */
export const ROLES = ['economist', 'statistician', 'head', 'curator'] as const;
export type Role = (typeof ROLES)[number];

/**
 * Which nav screens each role sees (docs/13 §3 permission matrix, simplified
 * for the demo). Switching role visibly transforms the sidebar + data scope —
 * that's the PD3-lite demo trick.
 */
export const ROLE_NAV: Record<Role, string[]> = {
  economist: ['/overview', '/risks', '/reconcile', '/calendar', '/reports', '/copilot', '/imports', '/admin'],
  statistician: ['/overview', '/prebilling', '/reconcile', '/anomalies', '/copilot', '/imports'],
  head: ['/overview', '/risks', '/reports', '/city', '/copilot', '/admin'],
  curator: ['/city', '/overview', '/copilot'],
};

interface RoleCtx {
  role: Role;
  setRole: (r: Role) => void;
  nav: string[];
}

const Ctx = createContext<RoleCtx | null>(null);

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<Role>('economist');
  const value = useMemo<RoleCtx>(
    () => ({ role, setRole, nav: ROLE_NAV[role] }),
    [role],
  );
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useRole(): RoleCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useRole must be used within RoleProvider');
  return ctx;
}
