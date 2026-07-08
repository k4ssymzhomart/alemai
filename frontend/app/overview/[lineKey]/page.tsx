'use client';

import { Suspense, useMemo } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import ErrorState from '@/components/ErrorState';
import CumulativeChart from '@/components/charts/CumulativeChart';
import MonthlyChart from '@/components/charts/MonthlyChart';
import KpiTile from '@/components/overview/KpiTile';
import { fmtDate, fmtPct, fmtTenge, type NumLocale } from '@/lib/format';
import { useLineMonthly, useLines } from '@/lib/hooks';

const DEFAULT_YEAR = 2026;

/**
 * Screen 1 drill-down (C2): line header + monthly plan/fact bars +
 * cumulative curves. Forecast band & burn-out stay computed-pending until
 * P6; the full Passport IA (Кто я → Вердикт → …) lands with PD2 in Epic C.
 */
export default function LineDrilldownPage({
  params,
}: {
  params: { lineKey: string };
}) {
  // Next keeps dynamic segments percent-encoded; line_key contains ':'.
  const lineKey = decodeURIComponent(params.lineKey);
  return (
    <Suspense fallback={null}>
      <LineDrilldown lineKey={lineKey} />
    </Suspense>
  );
}

function LineDrilldown({ lineKey }: { lineKey: string }) {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;

  const searchParams = useSearchParams();
  const yearParam = Number(searchParams.get('year'));
  const year =
    Number.isInteger(yearParam) && yearParam > 2000 ? yearParam : DEFAULT_YEAR;

  // Line meta (name, plan/fact/execution) comes from /metrics/lines;
  // the chart series from /metrics/line/{key}/monthly.
  const lines = useLines({ year });
  const monthly = useLineMonthly(lineKey, year);

  const line = useMemo(
    () => lines.data?.items.find((item) => item.line_key === lineKey) ?? null,
    [lines.data, lineKey],
  );

  const backLink = (
    <Link
      href="/overview"
      className="hover-stamp inline-flex items-center gap-1.5 border border-ink bg-paper px-2 py-1 font-mono text-caption font-medium uppercase text-ink hover:bg-ink hover:text-paper"
    >
      <span aria-hidden>←</span>
      {t('drilldown.back')}
    </Link>
  );

  if (lines.error) {
    return (
      <div className="space-y-4">
        {backLink}
        <ErrorState detail={lines.error} onRetry={lines.retry} />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {backLink}

      {lines.loading ? (
        <div className="space-y-2">
          <div className="fill-dots-faint h-8 w-72 animate-pulse" />
          <div className="fill-dots-faint h-4 w-96 animate-pulse" />
        </div>
      ) : line ? (
        <div>
          <h1 className="font-display text-h1 font-medium uppercase tracking-tight text-ink">
            {line.service_group || t(`care_type.${line.care_type}`)}
          </h1>
          {/* Breadcrumb-style meta line (full breadcrumbs land with PD2). */}
          <p className="mt-1 flex flex-wrap items-center gap-x-2 gap-y-1 font-mono text-caption uppercase text-ink/70">
            <span>{t(`care_type.${line.care_type}`)}</span>
            <span aria-hidden>/</span>
            <span>{t(`funding.${line.funding_source}`)}</span>
            <span aria-hidden>/</span>
            <span className="tabular-nums">{line.contract_id}</span>
            <span aria-hidden>/</span>
            <span className="tabular-nums">{year}</span>
          </p>
        </div>
      ) : (
        <div className="fill-dots-faint flex flex-col items-center gap-4 border border-ink px-6 py-10 text-center text-sm text-ink/70">
          <p>{t('drilldown.not_found', { key: lineKey })}</p>
          <Link
            href="/overview"
            className="hover-stamp border-2 border-ink bg-paper px-4 py-1.5 text-sm font-semibold uppercase text-ink shadow-hard-sm hover:bg-ink hover:text-paper"
          >
            {t('common.go_overview')}
          </Link>
        </div>
      )}

      {line ? (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-5">
          <KpiTile
            label={t('drilldown.plan_year')}
            value={fmtTenge(line.plan_amount_year)}
          />
          <KpiTile
            label={t('drilldown.fact_ytd')}
            value={fmtTenge(line.fact_amount_ytd)}
            sub={`${t('common.plan')}: ${fmtTenge(line.plan_amount_ytd)}`}
          />
          <KpiTile
            label={t('overview.kpi.execution_ytd')}
            value={fmtPct(line.execution_pct_ytd, locale)}
          />
          <KpiTile
            label={t('drilldown.rejected_ytd')}
            value={fmtTenge(line.rejected_amount_ytd)}
          />
          {/* burn_out_date is null until P6 → computed-pending tile */}
          <KpiTile
            label={t('overview.table.burn_out_date')}
            pending={line.burn_out_date == null}
            value={line.burn_out_date ? fmtDate(line.burn_out_date) : null}
          />
        </div>
      ) : null}

      {monthly.error ? (
        <ErrorState detail={monthly.error} onRetry={monthly.retry} />
      ) : (
        <div className="grid gap-4 xl:grid-cols-2">
          <section className="border-2 border-ink bg-paper p-4">
            <h2 className="mb-3 font-display text-h2 font-medium uppercase text-ink">
              {t('drilldown.monthly_title')}
            </h2>
            {monthly.loading || !monthly.data ? (
              <div className="fill-dots-faint h-80 animate-pulse" />
            ) : (
              <MonthlyChart months={monthly.data.months} />
            )}
          </section>
          <section className="border-2 border-ink bg-paper p-4">
            <h2 className="mb-3 font-display text-h2 font-medium uppercase text-ink">
              {t('drilldown.cumulative_title')}
            </h2>
            {monthly.loading || !monthly.data ? (
              <div className="fill-dots-faint h-80 animate-pulse" />
            ) : (
              <CumulativeChart months={monthly.data.months} />
            )}
          </section>
        </div>
      )}
    </div>
  );
}
