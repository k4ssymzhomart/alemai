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

/**
 * Severity without color (docs/15 §4): critical = inverted black block,
 * risk = 45° hatch + 2px border, normal = plain 1px chip. `over` maps to
 * critical here because overshoot burns the contract fastest.
 */
const STATUS_STYLES: Record<ExecutionStatus, string> = {
  under: 'fill-hatch-light border-2 border-ink text-ink',
  on_track: 'border border-ink text-ink',
  over: 'border-2 border-ink bg-ink text-paper',
};

/** Execution % chip for the lines table (stub thresholds until P6). */
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
        'inline-flex px-2 py-0.5 font-mono text-xs font-semibold tabular-nums',
        STATUS_STYLES[stubExecutionStatus(pct)],
      )}
    >
      {fmtPct(pct, locale)}
    </span>
  );
}
