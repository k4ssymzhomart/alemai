'use client';

import { useTranslation } from 'react-i18next';

import { fmtPct, type NumLocale } from '@/lib/format';

/**
 * F1 execution cell: the PRIMARY figure is vs YTD plan (fact_ytd/plan_ytd —
 * the server's execution_pct_ytd, which reads sensibly mid-year); the annual
 * figure (fact_ytd/plan_year) is the 11px secondary «жылдық …» so nothing
 * looks catastrophic just because it's June. Severity is NOT encoded here to
 * keep the number crisp — it lives in the dedicated ТӘУЕКЕЛ column (RiskBadge,
 * §4 hatch/outline) driven by the server risk class; no up/down glyph.
 */
export default function ExecutionChip({
  pctYtd,
  pctAnnual,
  locale,
}: {
  pctYtd: number;
  pctAnnual: number;
  locale: NumLocale;
}) {
  const { t } = useTranslation();
  return (
    <span className="inline-flex flex-col items-end">
      <span className="font-mono text-secondary tabular-nums text-ink">
        {fmtPct(pctYtd, locale)}
      </span>
      <span className="font-mono text-micro tabular-nums text-ink/50">
        {t('overview.table.annual_short')} {fmtPct(pctAnnual, locale)}
      </span>
    </span>
  );
}
