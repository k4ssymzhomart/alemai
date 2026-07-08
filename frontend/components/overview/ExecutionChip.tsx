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
 * Outline chip (Epic A.2 weight diet): 1px hairline frame, mono figure, a
 * small leading glyph for severity — no solid fills (that mass is reserved
 * for critical risk / ≤2-day timers). Off/under/over share one calm shape.
 */
const STATUS_GLYPH: Record<ExecutionStatus, string> = {
  under: '▽',
  on_track: '',
  over: '△',
};

export default function ExecutionChip({
  pct,
  locale,
}: {
  pct: number;
  locale: NumLocale;
}) {
  const glyph = STATUS_GLYPH[stubExecutionStatus(pct)];
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 border border-ink/40 px-2 py-0.5',
        'font-mono text-secondary tabular-nums text-ink',
      )}
    >
      {glyph ? (
        <span className="text-ink/60" aria-hidden>
          {glyph}
        </span>
      ) : null}
      {fmtPct(pct, locale)}
    </span>
  );
}
