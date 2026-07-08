'use client';

import { useState } from 'react';
import { useTranslation } from 'react-i18next';

/** Hardcoded demo roles (docs/13 §2 core four); PD3-lite wires scope in Epic D. */
const ROLES = ['economist', 'statistician', 'head', 'curator'] as const;

export type Role = (typeof ROLES)[number];

/** Role switcher stub: local state only, no RBAC wiring yet. */
export default function RoleSwitcher() {
  const { t } = useTranslation();
  const [role, setRole] = useState<Role>('economist');

  return (
    <label className="flex items-center gap-2 border border-ink bg-paper px-2 py-1">
      <span className="font-mono text-caption uppercase text-ink/40" aria-hidden>
        ✍
      </span>
      <span className="sr-only">{t('roles.label')}</span>
      <select
        value={role}
        onChange={(event) => setRole(event.target.value as Role)}
        className="bg-paper font-mono text-xs font-medium text-ink"
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
