/**
 * Role model (EPIC G1) — the 5 backend UserRole values and per-role sidebar nav.
 * Role now comes from the server session (/auth/me), not a client toggle.
 */

export const ROLES = [
  'economist',
  'statistician',
  'chief',
  'curator',
  'admin',
] as const;
export type Role = (typeof ROLES)[number];

/** i18n key for the spoken role label (login card, header). */
export const ROLE_LABEL_KEY: Record<Role, string> = {
  economist: 'roles.economist',
  statistician: 'roles.statistician',
  chief: 'roles.chief',
  curator: 'roles.curator',
  admin: 'roles.admin',
};

/**
 * Which screens each role sees (docs/13 §3, simplified for the demo). Admin (IT)
 * sees everything; curator sees only aggregate/city surfaces.
 */
export const ROLE_NAV: Record<Role, string[]> = {
  economist: [
    '/overview', '/risks', '/reconcile', '/calendar',
    '/reports', '/copilot', '/regs', '/imports', '/admin',
  ],
  statistician: [
    '/overview', '/prebilling', '/reconcile', '/anomalies', '/copilot', '/regs', '/imports',
  ],
  chief: ['/overview', '/risks', '/reports', '/city', '/copilot', '/regs', '/admin'],
  curator: ['/city', '/overview', '/copilot', '/regs'],
  admin: [
    '/overview', '/risks', '/prebilling', '/reconcile', '/anomalies',
    '/calendar', '/copilot', '/regs', '/reports', '/city', '/imports', '/admin',
  ],
};

export function navForRole(role: string | undefined): string[] {
  return ROLE_NAV[(role ?? '') as Role] ?? [];
}

export function isRole(value: string | undefined): value is Role {
  return (ROLES as readonly string[]).includes(value ?? '');
}
