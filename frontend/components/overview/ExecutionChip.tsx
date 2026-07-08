'use client';

import clsx from 'clsx';

import { fmtPct, type NumLocale } from '@/lib/format';

export type ExecutionStatus = 'under' | 'on_track' | 'over';

/**
 * TODO(P6): STUB thresholds for the P2 traffic light ONLY. The real risk
 * classification (D2) is computed server-side against the FORECAST (not the
 * YTD plan) with configurable thresholds, and arrives as `risk_class`. Every
 * threshold lives in this one function so P6 replaces it in one place.
 */
export function stubExecutionStatus(pct: number): ExecutionStatus {
  if (pct < 90) return 'under';
  if (pct > 105) return 'over';
  return 'on_track';
}

const STATUS_STYLES: Record<ExecutionStatus, string> = {
  under: 'bg-amber-50 text-amber-700 ring-amber-200',
  on_track: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  over: 'bg-red-50 text-red-700 ring-red-200',
};

/** Traffic-light % chip for the lines table (stub thresholds until P6). */
export default function ExecutionChip({
  pct,
  locale,
}: {
  pct: number;
  locale: NumLocale;
}) {
  return (
    <span
      className={clsx(
        'inline-flex rounded-full px-2 py-0.5 text-xs font-semibold tabular-nums ring-1 ring-inset',
        STATUS_STYLES[stubExecutionStatus(pct)],
      )}
    >
      {fmtPct(pct, locale)}
    </span>
  );
}
