'use client';

import { useState } from 'react';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import ErrorState from '@/components/ErrorState';
import KpiTile from '@/components/overview/KpiTile';
import LinesTable from '@/components/overview/LinesTable';
import { fmtPct, fmtPeriod, fmtTenge, type NumLocale } from '@/lib/format';
import { useLines, useOverview } from '@/lib/hooks';
import type { CareType, FundingSource } from '@/lib/types';

const DEFAULT_YEAR = 2026;
const YEARS = [2026, 2025];
const FUNDING_FILTERS: Array<FundingSource | 'all'> = ['all', 'gobmp', 'osms'];
/** 'hosp' joins later — not offered as a filter yet. */
const CARE_TYPE_FILTERS: CareType[] = [
  'pmsp',
  'kdu',
  'day_hosp',
  'dent',
  'screening',
  'ambulance',
];

/** Screen 1 — Обзор договора (C1): hero KPIs + contract lines table. */
export default function OverviewPage() {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;

  const [year, setYear] = useState(DEFAULT_YEAR);
  const [funding, setFunding] = useState<FundingSource | 'all'>('all');
  const [careType, setCareType] = useState<CareType | 'all'>('all');

  const overview = useOverview(year);
  const lines = useLines({
    year,
    funding_source: funding === 'all' ? undefined : funding,
    care_type: careType === 'all' ? undefined : careType,
  });

  const m = overview.data;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-slate-900">
            {t('overview.title')}
          </h1>
          {m?.as_of ? (
            <p className="mt-1 text-xs text-slate-500">
              {t('overview.as_of', { period: fmtPeriod(m.as_of) })}
            </p>
          ) : null}
        </div>
        <label className="flex items-center gap-2 text-xs font-medium text-slate-500">
          {t('common.year')}
          <select
            value={year}
            onChange={(event) => setYear(Number(event.target.value))}
            className="rounded-md border border-slate-200 bg-white px-2 py-1.5 text-xs font-medium text-slate-700 outline-none focus:border-accent"
          >
            {YEARS.map((y) => (
              <option key={y} value={y}>
                {y}
              </option>
            ))}
          </select>
        </label>
      </div>

      {overview.error ? (
        <ErrorState detail={overview.error} onRetry={overview.retry} />
      ) : (
        <div className="grid grid-cols-2 gap-3 lg:grid-cols-3 xl:grid-cols-5">
          <KpiTile
            big
            label={t('overview.kpi.execution_ytd')}
            loading={overview.loading}
            value={m ? fmtPct(m.execution_pct_ytd, locale) : null}
          />
          <KpiTile
            label={t('overview.kpi.plan_fact_ytd')}
            loading={overview.loading}
            value={m ? fmtTenge(m.fact_amount_ytd) : null}
            sub={m ? `${t('common.plan')}: ${fmtTenge(m.plan_amount_ytd)}` : null}
          />
          <KpiTile
            label={t('overview.kpi.removed_mtd')}
            loading={overview.loading}
            value={m ? fmtTenge(m.rejected_amount_mtd) : null}
          />
          {/* forecast_gap / risk_count are null until P6 → computed-pending tiles */}
          <KpiTile
            label={t('overview.kpi.forecast_gap')}
            loading={overview.loading}
            pending={m?.forecast_gap == null}
            value={m?.forecast_gap != null ? fmtTenge(m.forecast_gap) : null}
          />
          <KpiTile
            label={t('overview.kpi.risk_count')}
            loading={overview.loading}
            pending={m?.risk_count == null}
            value={m?.risk_count != null ? String(m.risk_count) : null}
          />
        </div>
      )}

      <section className="rounded-lg border border-slate-200 bg-white">
        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-200 px-4 py-3">
          <h2 className="text-sm font-semibold text-slate-900">
            {t('overview.table.title')}
            {lines.data ? (
              <span className="ml-2 rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium tabular-nums text-slate-500">
                {lines.data.total}
              </span>
            ) : null}
          </h2>
          <div className="flex flex-wrap items-center gap-2">
            <div
              role="group"
              aria-label={t('common.source')}
              className="flex rounded-md border border-slate-200 bg-slate-50 p-0.5"
            >
              {FUNDING_FILTERS.map((value) => (
                <button
                  key={value}
                  type="button"
                  onClick={() => setFunding(value)}
                  aria-pressed={funding === value}
                  className={clsx(
                    'rounded px-2.5 py-1 text-xs font-medium transition-colors',
                    funding === value
                      ? 'bg-white text-accent-700 shadow-sm ring-1 ring-slate-200'
                      : 'text-slate-500 hover:text-slate-900',
                  )}
                >
                  {value === 'all' ? t('common.all') : t(`funding.${value}`)}
                </button>
              ))}
            </div>
            <select
              value={careType}
              onChange={(event) =>
                setCareType(event.target.value as CareType | 'all')
              }
              aria-label={t('overview.table.care_type')}
              className="rounded-md border border-slate-200 bg-white px-2 py-1.5 text-xs font-medium text-slate-700 outline-none focus:border-accent"
            >
              <option value="all">{t('common.all')}</option>
              {CARE_TYPE_FILTERS.map((value) => (
                <option key={value} value={value}>
                  {t(`care_type.${value}`)}
                </option>
              ))}
            </select>
          </div>
        </div>

        {lines.error ? (
          <div className="p-4">
            <ErrorState detail={lines.error} onRetry={lines.retry} />
          </div>
        ) : lines.loading ? (
          <div className="space-y-2 p-4">
            {Array.from({ length: 8 }).map((_, i) => (
              <div key={i} className="h-8 animate-pulse rounded bg-slate-100" />
            ))}
          </div>
        ) : lines.data && lines.data.items.length > 0 ? (
          <LinesTable lines={lines.data.items} year={year} />
        ) : (
          <p className="px-4 py-10 text-center text-sm text-slate-500">
            {t('common.no_data')}
          </p>
        )}
      </section>
    </div>
  );
}
