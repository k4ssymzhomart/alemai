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
const STATUS_STYLES: Record<ExecutionStatus, { chip: string; glyph: string }> = {
  under: { chip: 'fill-hatch-light border-2 border-ink text-ink', glyph: '◤' },
  on_track: { chip: 'border border-ink text-ink', glyph: '' },
  over: { chip: 'border-4 border-ink bg-ink text-paper', glyph: '▲' },
};

/** Execution % chip for the lines table (stub thresholds until P6). */
export default function ExecutionChip({
  pct,
  locale,
}: {
  pct: number;
  locale: NumLocale;
}) {
  const { chip, glyph } = STATUS_STYLES[stubExecutionStatus(pct)];
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 px-2 py-0.5 font-mono text-xs font-semibold tabular-nums',
        chip,
      )}
    >
      {glyph ? <span aria-hidden>{glyph}</span> : null}
      {fmtPct(pct, locale)}
    </span>
  );
}
