'use client';

import { useTranslation } from 'react-i18next';

import { useSession } from '@/components/SessionProvider';
import { ROLE_LABEL_KEY, type Role } from '@/lib/roles';

/**
 * Header identity (EPIC G1) — «Айгерім · экономист» + Шығу (logout) and Сменить
 * пользователя (→ login). Replaces the old client-side role switcher; role now
 * comes from the server session.
 */
export default function UserMenu() {
  const { t } = useTranslation();
  const { me, logout } = useSession();
  if (!me) return null;

  const roleLabel = ROLE_LABEL_KEY[me.role as Role];

  return (
    <div className="flex items-center gap-2 border border-ink/15 px-2.5 py-1">
      <span className="text-secondary text-ink" title={me.username}>
        {me.name}
      </span>
      {roleLabel ? <span className="label-micro">{t(roleLabel)}</span> : null}
      <span aria-hidden className="text-ink/20">
        ·
      </span>
      <button
        type="button"
        onClick={() => logout()}
        className="label-micro text-ink/60 transition-colors duration-150 hover:text-ink"
      >
        {t('auth.logout')}
      </button>
    </div>
  );
}
