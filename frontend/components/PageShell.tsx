'use client';

import { useTranslation } from 'react-i18next';

import EmptyState from '@/components/EmptyState';

interface PageShellProps {
  /** i18n key for the page h1, e.g. "nav.overview". */
  titleKey: string;
}

/** Standard skeleton screen: display-serif h1 (sentence case) + empty state. */
export default function PageShell({ titleKey }: PageShellProps) {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      <h1 className="font-display text-h1 text-ink">{t(titleKey)}</h1>
      <EmptyState />
    </div>
  );
}
