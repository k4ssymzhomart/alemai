'use client';

import { useMemo, useState } from 'react';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import EmptyState from '@/components/EmptyState';
import ErrorState from '@/components/ErrorState';
import RiskBadge from '@/components/overview/RiskBadge';
import { downloadFile } from '@/lib/api';
import { fmtDate, fmtTenge, type NumLocale } from '@/lib/format';
import { useLines } from '@/lib/hooks';
import type { ContractLine, RiskClass } from '@/lib/types';

const YEAR = 2026;
/** Over-execution → обращение о размещении доп. объёмов makes sense. */
const OVER = new Set<RiskClass>(['over', 'critical_over']);

/**
 * Screen — Риски: the risk register (H2 fill-or-kill). Every line whose
 * risk_class ≠ on_track, ranked by ₸ gap, with a G/Y/R chip, burn-out date, the
 * seeded recommendation, and a [Сформировать обращение] action on over-lines.
 * Data comes straight from /metrics/lines — a focused view, not a new API.
 */
export default function RisksPage() {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'ru') as NumLocale;
  const lines = useLines({ year: YEAR });

  const risky = useMemo(() => {
    const items = lines.data?.items ?? [];
    return items
      .filter((l) => l.risk_class && l.risk_class !== 'on_track')
      .sort((a, b) => Math.abs(b.forecast_gap ?? 0) - Math.abs(a.forecast_gap ?? 0));
  }, [lines.data]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-h1 text-ink">{t('nav.risks')}</h1>
        <p className="mt-1 label-micro">{t('risks.lead')}</p>
      </div>

      {lines.error ? (
        <ErrorState detail={lines.error} onRetry={lines.retry} />
      ) : lines.loading ? (
        <div className="fill-dots-faint h-40 animate-pulse" />
      ) : risky.length === 0 ? (
        <EmptyState messageKey="risks.none" />
      ) : (
        <div className="border border-ink/15">
          {risky.map((l, i) => (
            <RiskRow
              key={l.line_key}
              line={l}
              locale={locale}
              last={i === risky.length - 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function RiskRow({
  line,
  locale,
  last,
}: {
  line: ContractLine;
  locale: NumLocale;
  last: boolean;
}) {
  const { t } = useTranslation();
  const lang: 'kk' | 'ru' = locale === 'kk' ? 'kk' : 'ru';
  const [busy, setBusy] = useState(false);
  const name = [
    t(`care_type.${line.care_type}`),
    line.service_group,
    t(`funding.${line.funding_source}`),
  ]
    .filter(Boolean)
    .join(' · ');
  const rec = line.recommendation ? line.recommendation[lang] : null;
  const showObrashenie = line.risk_class != null && OVER.has(line.risk_class);

  const generate = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await downloadFile(
        '/documents/obrashenie',
        { line_key: line.line_key, lang },
        `obrashenie_${lang}.docx`,
      );
    } catch {
      /* offline / not applicable — no unhandled rejection */
    } finally {
      setBusy(false);
    }
  };

  return (
    <div
      className={clsx(
        'flex flex-wrap items-center gap-4 px-4 py-3',
        !last && 'border-b border-ink/[.08]',
      )}
    >
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2">
          <RiskBadge riskClass={line.risk_class} />
          <span className="text-secondary text-ink/80">{name}</span>
        </div>
        {rec ? <p className="mt-1 text-micro text-ink/50">{rec}</p> : null}
      </div>
      <div className="shrink-0 text-right">
        <p className="font-mono text-secondary tabular-nums text-ink">
          {fmtTenge(line.forecast_gap ?? 0)}
        </p>
        {line.burn_out_date ? (
          <p className="label-micro">
            {t('overview.table.burn_out_date')}: {fmtDate(line.burn_out_date)}
          </p>
        ) : null}
      </div>
      {showObrashenie ? (
        <button
          type="button"
          onClick={generate}
          disabled={busy}
          className="shrink-0 border border-accent px-3 py-1.5 text-secondary font-medium text-accent transition-colors duration-150 hover:bg-accent/5 disabled:opacity-40"
        >
          {busy ? t('common.loading') : t('risks.generate_obrashenie')}
        </button>
      ) : null}
    </div>
  );
}
