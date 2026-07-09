'use client';

import { useTranslation } from 'react-i18next';

import EmptyState from '@/components/EmptyState';
import ErrorState from '@/components/ErrorState';
import { fmtDate } from '@/lib/format';
import { useAnomalies } from '@/lib/hooks';
import type { Anomaly } from '@/lib/types';

/**
 * Screen — Аномалии (H2): doctor-workload outliers from /anomalies (day-volume +
 * weekend services, the R10/R11 signals). Neutral language — «требует проверки»,
 * never an accusation. Curator is scoped out server-side.
 */
export default function AnomaliesPage() {
  const { t } = useTranslation();
  const anomalies = useAnomalies();
  const items = anomalies.data?.items ?? [];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-h1 text-ink">{t('nav.anomalies')}</h1>
        <p className="mt-1 label-micro">{t('anomalies.lead')}</p>
      </div>

      {anomalies.error ? (
        <ErrorState detail={anomalies.error} onRetry={anomalies.retry} />
      ) : anomalies.loading ? (
        <div className="fill-dots-faint h-40 animate-pulse" />
      ) : items.length === 0 ? (
        <EmptyState messageKey="anomalies.none" />
      ) : (
        <div className="overflow-x-auto border border-ink/15">
          <table className="w-full border-collapse text-secondary">
            <thead>
              <tr className="border-b border-ink/15 text-left label-micro">
                <th className="px-4 py-2 font-normal">{t('anomalies.col_doctor')}</th>
                <th className="px-4 py-2 font-normal">{t('anomalies.col_type')}</th>
                <th className="px-4 py-2 font-normal">{t('anomalies.col_period')}</th>
                <th className="px-4 py-2 text-right font-normal">{t('anomalies.col_count')}</th>
                <th className="px-4 py-2 font-normal">{t('anomalies.col_status')}</th>
              </tr>
            </thead>
            <tbody>
              {items.map((a, i) => (
                <AnomalyRow key={`${a.type}-${a.doctor}-${a.period}-${i}`} anomaly={a} />
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

function AnomalyRow({ anomaly: a }: { anomaly: Anomaly }) {
  const { t } = useTranslation();
  const period = a.type === 'day_volume' ? fmtDate(a.period) : a.period;
  return (
    <tr className="border-b border-ink/[.06] last:border-0">
      <td className="px-4 py-2.5 text-ink/80">
        {a.doctor}
        <span className="ml-2 label-micro text-ink/40">{a.specialty}</span>
      </td>
      <td className="px-4 py-2.5">{t(`anomalies.type_${a.type}`)}</td>
      <td className="px-4 py-2.5 font-mono tabular-nums text-ink/60">{period}</td>
      <td className="px-4 py-2.5 text-right font-mono tabular-nums text-ink">
        {a.count}
        <span className="text-ink/40"> / {a.threshold}</span>
      </td>
      <td className="px-4 py-2.5">
        <span className="inline-flex items-center gap-1 border border-warn bg-warn/10 px-1.5 py-0.5 label-micro text-ink">
          {t('anomalies.requires_review')}
        </span>
      </td>
    </tr>
  );
}
