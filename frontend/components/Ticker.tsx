'use client';

import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { fmtPct, fmtTenge, type NumLocale } from '@/lib/format';
import { useOverview } from '@/lib/hooks';

const YEAR = 2026;
const ROTATE_MS = 5000;

/**
 * Alert wire (Epic A.2): a single quiet line under the header that crossfades
 * through its items — NOT a scrolling marquee. Content = live /metrics numbers
 * + regulatory constants (cited пункты); never a number the system didn't
 * compute. Storyline alerts (burn-out, DF-timers) join in Epics B/C.
 */
export default function Ticker() {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;
  const overview = useOverview(YEAR);
  const [idx, setIdx] = useState(0);

  const items = useMemo(() => {
    const out: string[] = [];
    const m = overview.data;
    if (m) {
      out.push(
        `${t('overview.kpi.execution_ytd')} · ${fmtPct(m.execution_pct_ytd, locale)}`,
        `${t('overview.kpi.removed_mtd')} · ${fmtTenge(m.rejected_amount_mtd)}`,
      );
    }
    out.push(t('ticker.objection_rule'), t('ticker.eps_deadline'));
    return out;
  }, [overview.data, t, locale]);

  useEffect(() => {
    if (items.length <= 1) return;
    const id = window.setInterval(
      () => setIdx((i) => (i + 1) % items.length),
      ROTATE_MS,
    );
    return () => window.clearInterval(id);
  }, [items.length]);

  const current = items[idx % items.length] ?? '';

  return (
    <div
      className="min-w-0 flex-1 overflow-hidden"
      aria-label={t('ticker.label')}
      aria-live="polite"
    >
      <p
        key={idx}
        className="wire-item truncate font-mono text-secondary text-ink/60"
      >
        {current}
      </p>
    </div>
  );
}
