'use client';

import Link from 'next/link';
import { useTranslation } from 'react-i18next';

interface EmptyStateProps {
  /** i18n key for the one-sentence explanation; defaults to common.empty. */
  messageKey?: string;
  /** One action (docs/14 §0: every empty state = 1 sentence + 1 button). */
  actionKey?: string;
  actionHref?: string;
}

/** Designed empty state (Epic A.2): faint dot grid + 1 sentence + 1 action. */
export default function EmptyState({
  messageKey = 'common.empty',
  actionKey = 'common.go_overview',
  actionHref = '/overview',
}: EmptyStateProps) {
  const { t } = useTranslation();

  return (
    <div className="relative flex flex-col items-center justify-center gap-5 border border-ink/15 px-6 py-20 text-center">
      <div className="fill-dots-faint pointer-events-none absolute inset-0" aria-hidden />
      <p className="relative text-body text-ink/60">{t(messageKey)}</p>
      <Link
        href={actionHref}
        className="relative bg-ink px-4 py-2 text-secondary font-medium text-paper transition-opacity duration-150 hover:opacity-80"
      >
        {t(actionKey)}
      </Link>
    </div>
  );
}
