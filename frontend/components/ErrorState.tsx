'use client';

import { AlertTriangle } from 'lucide-react';
import { useTranslation } from 'react-i18next';

interface ErrorStateProps {
  /** Technical detail (status/URL) shown small under the localized message. */
  detail?: string | null;
  onRetry: () => void;
}

/** Honest error card: localized message + technical detail + retry button. */
export default function ErrorState({ detail, onRetry }: ErrorStateProps) {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-red-200 bg-red-50/50 px-6 py-12 text-center">
      <AlertTriangle className="h-7 w-7 text-red-400" aria-hidden />
      <p className="text-sm font-medium text-slate-700">{t('common.error')}</p>
      {detail ? (
        <p className="max-w-xl break-all font-mono text-xs text-slate-400">
          {detail}
        </p>
      ) : null}
      <button
        type="button"
        onClick={onRetry}
        className="rounded-md bg-accent px-4 py-1.5 text-sm font-medium text-white transition-colors hover:bg-accent-700"
      >
        {t('common.retry')}
      </button>
    </div>
  );
}
