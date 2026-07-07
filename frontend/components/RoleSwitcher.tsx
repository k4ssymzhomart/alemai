'use client';

import { useState } from 'react';
import { UserRound } from 'lucide-react';
import { useTranslation } from 'react-i18next';

/** Hardcoded demo roles (docs/04 §1): role switch in header, great for demo narration. */
const ROLES = ['economist', 'statistician', 'head', 'curator'] as const;

export type Role = (typeof ROLES)[number];

/** Role switcher stub: local state only, no RBAC wiring yet. */
export default function RoleSwitcher() {
  const { t } = useTranslation();
  const [role, setRole] = useState<Role>('economist');

  return (
    <label className="flex items-center gap-2 rounded-md border border-slate-200 bg-slate-50 px-2 py-1.5">
      <UserRound className="h-4 w-4 shrink-0 text-slate-400" aria-hidden />
      <span className="sr-only">{t('roles.label')}</span>
      <select
        value={role}
        onChange={(event) => setRole(event.target.value as Role)}
        className="w-full bg-transparent text-xs font-medium text-slate-700 outline-none"
      >
        {ROLES.map((value) => (
          <option key={value} value={value}>
            {t(`roles.${value}`)}
          </option>
        ))}
      </select>
    </label>
  );
}
