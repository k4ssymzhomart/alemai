'use client';

import { useTranslation } from 'react-i18next';

import { ROLES, useRole, type Role } from '@/components/RoleProvider';

/** Role switcher (PD3-lite): drives nav + data scope via RoleProvider. */
export default function RoleSwitcher() {
  const { t } = useTranslation();
  const { role, setRole } = useRole();

  return (
    <label className="flex items-center gap-2 border border-ink/15 px-2 py-1">
      <span className="sr-only">{t('roles.label')}</span>
      <select
        value={role}
        onChange={(event) => setRole(event.target.value as Role)}
        className="bg-paper font-mono text-micro normal-case tracking-normal text-ink/70"
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
