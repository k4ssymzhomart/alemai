'use client';

import { useEffect, useMemo, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { fmtDate, fmtPct, fmtTenge, type NumLocale } from '@/lib/format';
import { useLines, useOverview } from '@/lib/hooks';

const YEAR = 2026;
const ROTATE_MS = 5000;

/**
 * Alert wire (Epic C · F7): a single quiet line that crossfades through REAL
 * risk signals computed from the live seed — burn-out lines, execution, снятия
 * — plus cited regulatory constants. Never a number the system didn't compute.
 * Objection/reconcile alerts join when those APIs land (Epic C backend).
 */
export default function Ticker() {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;
  const overview = useOverview(YEAR);
  const lines = useLines({ year: YEAR });
  const [idx, setIdx] = useState(0);

  const items = useMemo(() => {
    const out: string[] = [];
    // Burn-out lines first — the sharpest risk (F2 fills burn_out_date).
    for (const line of lines.data?.items ?? []) {
      if (line.burn_out_date) {
        const name = line.service_group || t(`care_type.${line.care_type}`);
        out.push(
          t('ticker.burn_out', { line: name, date: fmtDate(line.burn_out_date) }),
        );
      }
    }
    const m = overview.data;
    if (m) {
      out.push(
        `${t('overview.kpi.execution_ytd')} · ${fmtPct(m.execution_pct_ytd, locale)}`,
      );
      if (m.rejected_amount_mtd > 0) {
        out.push(
          `${t('overview.kpi.removed_mtd')} · ${fmtTenge(m.rejected_amount_mtd)}`,
        );
      }
    }
    out.push(t('ticker.objection_rule'), t('ticker.eps_deadline'));
    return out;
  }, [lines.data, overview.data, t, locale]);

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
