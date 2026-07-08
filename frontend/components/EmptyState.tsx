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

/** Designed empty state (docs/15 §9): dot pattern + 1 sentence + 1 action. */
export default function EmptyState({
  messageKey = 'common.empty',
  actionKey = 'common.go_overview',
  actionHref = '/overview',
}: EmptyStateProps) {
  const { t } = useTranslation();

  return (
    <div className="fill-dots-faint flex flex-col items-center justify-center gap-4 border border-ink px-6 py-16 text-center">
      <p className="text-sm text-ink/70">{t(messageKey)}</p>
      <Link
        href={actionHref}
        className="hover-stamp border-2 border-ink bg-paper px-4 py-1.5 text-sm font-semibold uppercase text-ink shadow-hard-sm hover:bg-ink hover:text-paper"
      >
        {t(actionKey)}
      </Link>
    </div>
  );
}
