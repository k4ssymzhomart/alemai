'use client';

import { useTranslation } from 'react-i18next';

interface ErrorStateProps {
  /** Technical detail (status/URL) shown small under the localized message. */
  detail?: string | null;
  onRetry: () => void;
}

/** Honest error card: hatched frame, localized message, mono detail, retry. */
export default function ErrorState({ detail, onRetry }: ErrorStateProps) {
  const { t } = useTranslation();

  return (
    <div className="border-2 border-ink">
      <div className="fill-hatch-light border-b-2 border-ink px-4 py-1.5 font-mono text-caption uppercase">
        ! {t('common.error')}
      </div>
      <div className="flex flex-col items-center justify-center gap-3 px-6 py-10 text-center">
        {detail ? (
          <p className="max-w-xl break-all font-mono text-xs text-ink/40">
            {detail}
          </p>
        ) : null}
        <button
          type="button"
          onClick={onRetry}
          className="hover-stamp border-2 border-ink bg-ink px-4 py-1.5 text-sm font-semibold uppercase text-paper hover:bg-paper hover:text-ink"
        >
          {t('common.retry')}
        </button>
      </div>
    </div>
  );
}
