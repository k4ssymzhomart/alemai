'use client';

import { useTranslation } from 'react-i18next';

import EmptyState from '@/components/EmptyState';

interface PageShellProps {
  /** i18n key for the page h1, e.g. "nav.overview". */
  titleKey: string;
}

/** Standard skeleton screen: localized h1 + empty-state card. */
export default function PageShell({ titleKey }: PageShellProps) {
  const { t } = useTranslation();

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
        {t(titleKey)}
      </h1>
      <EmptyState />
    </div>
  );
}
