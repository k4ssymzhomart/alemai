'use client';

import { useTranslation } from 'react-i18next';

interface ErrorStateProps {
  /** Technical detail (status/URL) shown small under the localized message. */
  detail?: string | null;
  onRetry: () => void;
}

/** Honest error card (Epic A.2): hairline frame, calm label, mono detail. */
export default function ErrorState({ detail, onRetry }: ErrorStateProps) {
  const { t } = useTranslation();

  return (
    <div className="border border-ink/15">
      <div className="border-b border-ink/15 px-4 py-2 label-micro">
        {t('common.error')}
      </div>
      <div className="flex flex-col items-center justify-center gap-4 px-6 py-10 text-center">
        {detail ? (
          <p className="max-w-xl break-all font-mono text-secondary text-ink/40">
            {detail}
          </p>
        ) : null}
        <button
          type="button"
          onClick={onRetry}
          className="border border-ink/40 px-4 py-2 text-secondary font-medium text-ink transition-colors duration-150 hover:bg-ink/[.03]"
        >
          {t('common.retry')}
        </button>
      </div>
    </div>
  );
}
