'use client';

import { useState } from 'react';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import ErrorState from '@/components/ErrorState';
import { downloadFileGet } from '@/lib/api';
import { fmtDate, fmtNumber, fmtTenge, type NumLocale } from '@/lib/format';
import { useReconcile, useReconcileRows } from '@/lib/hooks';
import type { ReconcileBucket } from '@/lib/types';

const YEAR = 2026;

/**
 * Screen 4 — Салыстыру (beat 5): three-way reconciliation into 4 buckets with
 * ₸ totals. Bucket 1 (оказано-но-не-выставлено) is the missed-revenue finding
 * and is emphasised; any bucket expands to its claim rows (drill-down).
 */
export default function ReconcilePage() {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;
  const buckets = useReconcile(YEAR);
  const [open, setOpen] = useState<number | null>(1);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-h1 text-ink">{t('nav.reconcile')}</h1>
        <p className="mt-1 label-micro">{t('reconcile.lead')}</p>
      </div>

      {buckets.error ? (
        <ErrorState detail={buckets.error} onRetry={buckets.retry} />
      ) : buckets.loading || !buckets.data ? (
        <div className="fill-dots-faint h-40 animate-pulse" />
      ) : (
        <div className="border border-ink/15">
          {buckets.data.buckets.map((b, i) => (
            <BucketRow
              key={b.bucket_no}
              bucket={b}
              locale={locale}
              open={open === b.bucket_no}
              onToggle={() =>
                setOpen((cur) => (cur === b.bucket_no ? null : b.bucket_no))
              }
              last={i === buckets.data!.buckets.length - 1}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function BucketRow({
  bucket,
  locale,
  open,
  onToggle,
  last,
}: {
  bucket: ReconcileBucket;
  locale: NumLocale;
  open: boolean;
  onToggle: () => void;
  last: boolean;
}) {
  const { t } = useTranslation();
  const rows = useReconcileRows(bucket.bucket_no, YEAR, open);
  const title = locale === 'kk' ? bucket.title_kk : bucket.title_ru;
  const highlight = bucket.bucket_no === 1;

  return (
    <div className={clsx(!last && 'border-b border-ink/15')}>
      <button
        type="button"
        onClick={onToggle}
        aria-expanded={open}
        className={clsx(
          'flex w-full items-center justify-between gap-4 px-4 py-4 text-left transition-colors duration-150 hover:bg-ink/[.03]',
          highlight && 'border-l-2 border-ink',
        )}
      >
        <div className="flex min-w-0 items-center gap-3">
          <span className="font-mono text-micro text-ink/40">{bucket.code}</span>
          <span className={clsx('text-body', highlight ? 'font-medium text-ink' : 'text-ink/80')}>
            {title}
          </span>
        </div>
        <div className="flex shrink-0 items-center gap-6">
          <span className="font-mono text-secondary tabular-nums text-ink/60">
            {t('reconcile.rows', { n: fmtNumber(bucket.rows_count) })}
          </span>
          <span className="w-36 text-right font-mono text-secondary tabular-nums text-ink">
            {fmtTenge(bucket.total_amount)}
          </span>
        </div>
      </button>

      {open ? (
        <div className="overflow-x-auto border-t border-ink/15 bg-ink/[.02]">
          <div className="flex justify-end px-4 pt-3">
            <button
              type="button"
              onClick={() =>
                void downloadFileGet(
                  `/exports/reconcile-bucket/${bucket.bucket_no}.xlsx`,
                  undefined,
                  `qalam_reconcile_bucket${bucket.bucket_no}.xlsx`,
                )
              }
              className="border border-ink/40 px-2.5 py-1 text-secondary font-medium text-ink transition-colors duration-150 hover:bg-ink/[.03]"
            >
              {t('reconcile.export')}
            </button>
          </div>
          {rows.loading ? (
            <div className="fill-dots-faint h-20 animate-pulse" />
          ) : rows.data && rows.data.rows.length > 0 ? (
            <table className="w-full border-collapse text-secondary">
              <thead>
                <tr className="border-b border-ink/[.08] text-left label-micro">
                  <th className="px-4 py-2 font-normal">{t('overview.table.line')}</th>
                  <th className="px-4 py-2 font-normal">{t('common.year')}</th>
                  <th className="px-4 py-2 text-right font-normal">{t('common.fact')}</th>
                </tr>
              </thead>
              <tbody>
                {rows.data.rows.map((r) => (
                  <tr key={r.claim_id} className="border-b border-ink/[.06] last:border-0">
                    <td className="px-4 py-1.5">
                      {r.service_name}
                      <span className="ml-2 font-mono text-micro text-ink/40">
                        {r.service_code}
                      </span>
                    </td>
                    <td className="px-4 py-1.5 font-mono tabular-nums text-ink/60">
                      {fmtDate(r.date_start)}
                    </td>
                    <td className="px-4 py-1.5 text-right font-mono tabular-nums">
                      {fmtTenge(r.amount)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="px-4 py-4 text-secondary text-ink/50">{t('common.no_data')}</p>
          )}
        </div>
      ) : null}
    </div>
  );
}
