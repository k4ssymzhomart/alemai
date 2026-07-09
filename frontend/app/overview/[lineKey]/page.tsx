'use client';

import { Suspense, useMemo, useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import ErrorState from '@/components/ErrorState';
import CumulativeChart from '@/components/charts/CumulativeChart';
import MonthlyChart from '@/components/charts/MonthlyChart';
import KpiTile from '@/components/overview/KpiTile';
import VerdictBlock from '@/components/vedomost/VerdictBlock';
import { downloadFile } from '@/lib/api';
import { fmtDate, fmtPct, fmtPeriod, fmtTenge, type NumLocale } from '@/lib/format';
import { useLineMonthly, useLines } from '@/lib/hooks';
import type { ContractLine, LocalizedText } from '@/lib/types';

/** Docgen supports kk/ru only; en falls back to ru. */
function docLang(locale: NumLocale): 'kk' | 'ru' {
  return locale === 'kk' ? 'kk' : 'ru';
}

const DEFAULT_YEAR = 2026;

export default function LineDrilldownPage({
  params,
}: {
  params: { lineKey: string };
}) {
  const lineKey = decodeURIComponent(params.lineKey);
  return (
    <Suspense fallback={null}>
      <LineDrilldown lineKey={lineKey} />
    </Suspense>
  );
}

/** Pick localized text; en falls back to ru (Epic B seeds ru+kk only). */
function pickText(txt: LocalizedText | null, locale: NumLocale): string | null {
  if (!txt) return null;
  return locale === 'en' ? (txt.ru ?? txt.kk) : (txt[locale] ?? txt.ru ?? null);
}

const CRITICAL = new Set(['critical_over', 'critical_under']);
const OVER = new Set(['over', 'critical_over']);
const UNDER = new Set(['under', 'critical_under']);

/**
 * Line Passport (PD2, docs/14 §0): every drill-down lands on the 5-block order
 * Кто я → Вердикт → Почему → Что делать → Данные, so a non-expert can read it
 * aloud. Verdict/why/action fill from the server forecast+risk (F2); until
 * those arrive they degrade to neutral «есептелуде» states, never fake values.
 */
function LineDrilldown({ lineKey }: { lineKey: string }) {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;

  const searchParams = useSearchParams();
  const yearParam = Number(searchParams.get('year'));
  const year =
    Number.isInteger(yearParam) && yearParam > 2000 ? yearParam : DEFAULT_YEAR;

  const lines = useLines({ year });
  const monthly = useLineMonthly(lineKey, year);

  const line = useMemo(
    () => lines.data?.items.find((item) => item.line_key === lineKey) ?? null,
    [lines.data, lineKey],
  );

  const breadcrumb = line ? (
    <nav className="flex flex-wrap items-center gap-x-2 label-micro" aria-label="breadcrumb">
      <Link href="/overview" className="hover:text-ink">
        {t('overview.title')}
      </Link>
      <span aria-hidden>/</span>
      <span>{t(`care_type.${line.care_type}`)}</span>
      <span aria-hidden>/</span>
      <span className="text-ink/60">
        {line.service_group || t(`care_type.${line.care_type}`)}
      </span>
    </nav>
  ) : (
    <Link href="/overview" className="label-micro hover:text-ink">
      ← {t('drilldown.back')}
    </Link>
  );

  if (lines.error) {
    return (
      <div className="space-y-4">
        {breadcrumb}
        <ErrorState detail={lines.error} onRetry={lines.retry} />
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {breadcrumb}

      {lines.loading ? (
        <div className="space-y-2">
          <div className="fill-dots-faint h-8 w-72 animate-pulse" />
          <div className="fill-dots-faint h-4 w-96 animate-pulse" />
        </div>
      ) : line ? (
        <PassportBody line={line} year={year} locale={locale} monthly={monthly} />
      ) : (
        <div className="relative flex flex-col items-center gap-5 border border-ink/15 px-6 py-16 text-center">
          <div className="fill-dots-faint pointer-events-none absolute inset-0" aria-hidden />
          <p className="relative text-body text-ink/60">
            {t('drilldown.not_found', { key: lineKey })}
          </p>
          <Link
            href="/overview"
            className="relative bg-ink px-4 py-2 text-secondary font-medium text-paper hover:opacity-80"
          >
            {t('common.go_overview')}
          </Link>
        </div>
      )}
    </div>
  );
}

function PassportBody({
  line,
  year,
  locale,
  monthly,
}: {
  line: ContractLine;
  year: number;
  locale: NumLocale;
  monthly: ReturnType<typeof useLineMonthly>;
}) {
  const { t } = useTranslation();
  const name = line.service_group || t(`care_type.${line.care_type}`);
  const risk = line.risk_class;
  const [docBusy, setDocBusy] = useState(false);
  const [docError, setDocError] = useState(false);

  const generateObrashenie = async () => {
    if (docBusy) return;
    setDocBusy(true);
    setDocError(false);
    try {
      await downloadFile(
        '/documents/obrashenie',
        { line_key: line.line_key, lang: docLang(locale) },
        `obrashenie_${docLang(locale)}.docx`,
      );
    } catch {
      setDocError(true);
    } finally {
      setDocBusy(false);
    }
  };

  // ── Вердикт ────────────────────────────────────────────────────────────
  const verdictKey = risk ?? 'pending';
  const critical = risk != null && CRITICAL.has(risk);
  let suffix = '';
  if (risk && OVER.has(risk) && line.burn_out_date) {
    suffix = t('verdict.burn_suffix', { date: fmtDate(line.burn_out_date) });
  } else if (risk && UNDER.has(risk) && line.forecast_gap != null) {
    suffix = t('verdict.gap_suffix', { gap: fmtTenge(Math.abs(line.forecast_gap)) });
  }
  const verdictText =
    t(`verdict.${verdictKey}`) + (suffix ? ` — ${suffix}` : '');

  const explanation = pickText(line.forecast_explanation, locale);
  const recommendation = pickText(line.recommendation, locale);
  const isRisk = risk != null && risk !== 'on_track';

  return (
    <div className="space-y-8">
      {/* 1 · Кто я */}
      <div>
        <h1 className="font-display text-h1 text-ink">{name}</h1>
        <p className="mt-1 flex flex-wrap items-center gap-x-2 label-micro">
          <span>{t(`care_type.${line.care_type}`)}</span>
          <span aria-hidden>·</span>
          <span>{t(`funding.${line.funding_source}`)}</span>
          <span aria-hidden>·</span>
          <span className="tabular-nums">
            {t('drilldown.plan_year')} {fmtTenge(line.plan_amount_year)}
          </span>
          <span aria-hidden>·</span>
          <span className="tabular-nums">{year}</span>
        </p>
      </div>

      {/* 2 · Вердикт — the only heavy element on the screen */}
      <VerdictBlock critical={critical}>{verdictText}</VerdictBlock>

      {/* 3 · Почему */}
      <section className="space-y-4">
        <p className="label-micro">{t('passport.sec_why')}</p>
        <p className="max-w-3xl text-body text-ink/80">
          {explanation ?? t('passport.explain_pending')}
        </p>
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
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
            label={t('overview.kpi.forecast_gap')}
            pending={line.forecast_gap == null}
            value={line.forecast_gap != null ? fmtTenge(line.forecast_gap) : null}
          />
          <KpiTile
            label={t('overview.table.burn_out_date')}
            pending={line.burn_out_date == null}
            value={line.burn_out_date ? fmtDate(line.burn_out_date) : null}
          />
        </div>
        {monthly.error ? (
          <ErrorState detail={monthly.error} onRetry={monthly.retry} />
        ) : (
          <div className="grid gap-6 xl:grid-cols-2">
            <div className="border border-ink/15 bg-paper p-5">
              <h2 className="mb-4 font-display text-h3 text-ink">
                {t('drilldown.monthly_title')}
              </h2>
              {monthly.loading || !monthly.data ? (
                <div className="fill-dots-faint h-72 animate-pulse" />
              ) : (
                <MonthlyChart months={monthly.data.months} />
              )}
            </div>
            <div className="border border-ink/15 bg-paper p-5">
              <h2 className="mb-4 font-display text-h3 text-ink">
                {t('drilldown.cumulative_title')}
              </h2>
              {monthly.loading || !monthly.data ? (
                <div className="fill-dots-faint h-72 animate-pulse" />
              ) : (
                <CumulativeChart months={monthly.data.months} />
              )}
            </div>
          </div>
        )}
      </section>

      {/* 4 · Что делать */}
      <section className="space-y-3">
        <p className="label-micro">{t('passport.sec_action')}</p>
        {isRisk ? (
          <div className="flex flex-wrap items-start justify-between gap-4 border-l-2 border-ink bg-paper px-5 py-4">
            <div className="max-w-2xl">
              <p className="text-body text-ink">
                {recommendation ?? t('passport.explain_pending')}
              </p>
              {line.forecast_gap != null ? (
                <p className="mt-1 font-mono text-secondary tabular-nums text-ink/60">
                  {t('passport.gap_label')}: {fmtTenge(line.forecast_gap)}
                </p>
              ) : null}
            </div>
            <div className="flex shrink-0 flex-col items-end gap-1">
              <button
                type="button"
                onClick={generateObrashenie}
                disabled={docBusy}
                className="bg-ink px-4 py-2 text-secondary font-medium text-paper transition-opacity duration-150 hover:opacity-80 disabled:opacity-40"
              >
                {docBusy ? t('copilot.thinking') : t('action.generate')}
              </button>
              {docError ? (
                <span className="label-micro text-ink/50">{t('common.error')}</span>
              ) : null}
            </div>
          </div>
        ) : (
          <p className="text-body text-ink/60">
            {risk === 'on_track' ? t('passport.no_action') : t('verdict.pending')}
          </p>
        )}
      </section>

      {/* 5 · Данные (collapsed) */}
      <section>
        <details className="border border-ink/15">
          <summary className="cursor-pointer px-5 py-3 label-micro hover:bg-ink/[.03]">
            {t('passport.sec_data')}
          </summary>
          <div className="overflow-x-auto border-t border-ink/15">
            {monthly.data ? (
              <table className="w-full border-collapse text-secondary">
                <thead>
                  <tr className="border-b border-ink/15 text-left label-micro">
                    <th className="px-4 py-2 font-normal">{t('common.year')}</th>
                    <th className="px-4 py-2 text-right font-normal">{t('common.plan')}</th>
                    <th className="px-4 py-2 text-right font-normal">{t('common.fact')}</th>
                    <th className="px-4 py-2 text-right font-normal">{t('chart.rejected')}</th>
                  </tr>
                </thead>
                <tbody>
                  {monthly.data.months.map((m) => (
                    <tr key={m.period} className="border-b border-ink/[.08] last:border-0">
                      <td className="px-4 py-1.5 font-mono tabular-nums">{fmtPeriod(m.period)}</td>
                      <td className="px-4 py-1.5 text-right font-mono tabular-nums text-ink/70">
                        {fmtTenge(m.plan_amount)}
                      </td>
                      <td className="px-4 py-1.5 text-right font-mono tabular-nums">
                        {fmtTenge(m.fact_amount)}
                      </td>
                      <td className="px-4 py-1.5 text-right font-mono tabular-nums text-ink/70">
                        {fmtTenge(m.rejected_amount)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="fill-dots-faint h-24 animate-pulse" />
            )}
          </div>
        </details>
      </section>
    </div>
  );
}
