'use client';

import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import { fmtPct, fmtTenge, type NumLocale } from '@/lib/format';
import { useOverview } from '@/lib/hooks';

const YEAR = 2026;

/**
 * Alert ticker (docs/15 §5): exchange-board black band in the header.
 * Content = live /metrics numbers + regulatory constants (cited пункты) —
 * never a number the system didn't compute. Storyline alerts (burn-out,
 * DF-timers) join in Epics B/C when the system actually computes them.
 */
export default function Ticker() {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;
  const overview = useOverview(YEAR);

  const items = useMemo(() => {
    const out: string[] = [];
    const m = overview.data;
    if (m) {
      out.push(
        `${t('overview.kpi.execution_ytd')}: ${fmtPct(m.execution_pct_ytd, locale)}`,
        `${t('overview.kpi.removed_mtd')}: ${fmtTenge(m.rejected_amount_mtd)}`,
      );
    }
    out.push(t('ticker.objection_rule'), t('ticker.eps_deadline'));
    return out;
  }, [overview.data, t, locale]);

  // Trailing separator keeps the loop seam continuous between track copies.
  const line = `${items.join('  ▮  ')}  ▮  `;

  return (
    <div
      className="ticker min-w-0 flex-1 overflow-hidden border-2 border-ink bg-ink text-paper"
      aria-label={t('ticker.label')}
    >
      <div className="ticker-track flex w-max whitespace-nowrap py-1.5 font-mono text-caption uppercase">
        {/* Track duplicated for a seamless loop. */}
        <span className="pl-4">{line}</span>
        <span aria-hidden>{line}</span>
      </div>
    </div>
  );
}
