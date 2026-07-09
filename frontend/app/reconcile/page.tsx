'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import ErrorState from '@/components/ErrorState';
import { downloadFileGet } from '@/lib/api';
import { fmtDate, fmtNumber, fmtTenge, type NumLocale } from '@/lib/format';
import { useReconcile, useReconcileRows } from '@/lib/hooks';
import type { ReconcileBucket, ReconcileRow } from '@/lib/types';

const YEAR = 2026;

/** A row picked for the detail card, plus the bucket it belongs to. */
interface Picked {
  row: ReconcileRow;
  bucket: ReconcileBucket;
}

/**
 * Screen 4 — Салыстыру (beat 5): three-way reconciliation into 4 buckets with
 * ₸ totals. Any bucket expands to its claim rows; every row is clickable and
 * opens a record card with the full claim (incl. пациент/ИИН) and the concrete
 * next step (add-to-invoice / возражение / контроль оплаты). Bucket 1
 * (оказано-но-не-выставлено) is the missed-revenue finding and is emphasised.
 */
export default function ReconcilePage() {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;
  const buckets = useReconcile(YEAR);
  const [open, setOpen] = useState<number | null>(1);
  const [picked, setPicked] = useState<Picked | null>(null);

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
              onPick={(row) => setPicked({ row, bucket: b })}
              last={i === buckets.data!.buckets.length - 1}
            />
          ))}
        </div>
      )}

      {picked ? (
        <RecordCard
          picked={picked}
          locale={locale}
          onClose={() => setPicked(null)}
        />
      ) : null}
    </div>
  );
}

function BucketRow({
  bucket,
  locale,
  open,
  onToggle,
  onPick,
  last,
}: {
  bucket: ReconcileBucket;
  locale: NumLocale;
  open: boolean;
  onToggle: () => void;
  onPick: (row: ReconcileRow) => void;
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
          <span aria-hidden className="text-ink/40">
            {open ? '▾' : '▸'}
          </span>
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
        <div className="border-t border-ink/15 bg-ink/[.02]">
          <div className="flex items-center justify-between gap-3 px-4 pt-3">
            <p className="label-micro">{t('reconcile.hint')}</p>
            <button
              type="button"
              onClick={() =>
                void downloadFileGet(
                  `/exports/reconcile-bucket/${bucket.bucket_no}.xlsx`,
                  undefined,
                  `qalam_reconcile_bucket${bucket.bucket_no}.xlsx`,
                )
              }
              className="shrink-0 border border-ink/40 px-2.5 py-1 text-secondary font-medium text-ink transition-colors duration-150 hover:bg-ink/[.03]"
            >
              {t('reconcile.export')}
            </button>
          </div>
          <div className="overflow-x-auto">
            {rows.loading ? (
              <div className="fill-dots-faint m-4 h-20 animate-pulse" />
            ) : rows.data && rows.data.rows.length > 0 ? (
              <>
                <table className="w-full border-collapse text-secondary">
                  <thead>
                    <tr className="border-b border-ink/[.08] text-left label-micro">
                      <th className="px-4 py-2 font-normal">{t('reconcile.col.service')}</th>
                      <th className="px-4 py-2 font-normal">{t('reconcile.col.patient')}</th>
                      <th className="px-4 py-2 font-normal">{t('reconcile.col.date')}</th>
                      <th className="px-4 py-2 text-right font-normal">{t('reconcile.col.amount')}</th>
                      <th className="w-8 px-2 py-2" aria-hidden />
                    </tr>
                  </thead>
                  <tbody>
                    {rows.data.rows.map((r) => (
                      <tr
                        key={r.claim_id}
                        onClick={() => onPick(r)}
                        className="cursor-pointer border-b border-ink/[.06] transition-colors duration-150 last:border-0 hover:bg-accent/[.05]"
                      >
                        <td className="px-4 py-1.5">
                          {r.service_name}
                          <span className="ml-2 font-mono text-micro text-ink/40">
                            {r.service_code}
                          </span>
                        </td>
                        <td className="px-4 py-1.5 font-mono tabular-nums text-ink/60">
                          {r.patient_id}
                        </td>
                        <td className="px-4 py-1.5 font-mono tabular-nums text-ink/60">
                          {fmtDate(r.date_start)}
                        </td>
                        <td className="px-4 py-1.5 text-right font-mono tabular-nums">
                          {fmtTenge(r.amount)}
                        </td>
                        <td className="px-2 py-1.5 text-right text-accent">→</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                <p className="px-4 py-2 label-micro">
                  {t('reconcile.showing', {
                    n: fmtNumber(rows.data.rows.length),
                    total: fmtNumber(bucket.rows_count),
                  })}
                </p>
              </>
            ) : (
              <p className="px-4 py-4 text-secondary text-ink/50">{t('common.no_data')}</p>
            )}
          </div>
        </div>
      ) : null}
    </div>
  );
}

function RecordCard({
  picked,
  locale,
  onClose,
}: {
  picked: Picked;
  locale: NumLocale;
  onClose: () => void;
}) {
  const { t } = useTranslation();
  const { row, bucket } = picked;
  const status = locale === 'kk' ? bucket.title_kk : bucket.title_ru;
  const actionText = t(`reconcile.action.${bucket.bucket_no}`, { defaultValue: '' });
  const ctaLabel = t(`reconcile.cta.${bucket.bucket_no}`, { defaultValue: '' });

  // Escape-to-close.
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-ink/40 p-0 sm:items-center sm:p-4"
      onClick={onClose}
      role="presentation"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={t('reconcile.record')}
        onClick={(e) => e.stopPropagation()}
        className="max-h-[90vh] w-full max-w-md overflow-y-auto border border-ink/15 bg-paper shadow-soft"
      >
        <div className="flex items-center justify-between border-b border-ink/15 px-4 py-3">
          <div className="flex items-center gap-2">
            <span className="font-mono text-micro text-ink/40">{bucket.code}</span>
            <h2 className="text-body font-medium text-ink">{t('reconcile.record')}</h2>
          </div>
          <button
            type="button"
            onClick={onClose}
            aria-label={t('reconcile.close')}
            className="border border-ink/20 px-2 py-0.5 text-ink transition-colors duration-150 hover:bg-ink/[.04]"
          >
            ✕
          </button>
        </div>

        <dl className="divide-y divide-ink/[.08]">
          <Field label={t('reconcile.field.service')}>
            {row.service_name}
            <span className="ml-2 font-mono text-micro text-ink/40">{row.service_code}</span>
          </Field>
          <Field label={t('reconcile.field.patient')} mono>
            {row.patient_id}
          </Field>
          <Field label={t('reconcile.field.date')} mono>
            {fmtDate(row.date_start)}
          </Field>
          <Field label={t('reconcile.field.amount')} mono>
            {fmtTenge(row.amount)}
          </Field>
          <Field label={t('reconcile.field.bucket')}>{status}</Field>
          <Field label={t('reconcile.field.claim')} mono>
            <span className="break-all text-ink/50">{row.claim_id}</span>
          </Field>
        </dl>

        {actionText ? (
          <div className="border-t border-ink/15 bg-ink/[.02] px-4 py-4">
            <p className="label-micro">{t('reconcile.action_label')}</p>
            <p className="mt-1.5 text-secondary text-ink/80">{actionText}</p>
            {ctaLabel ? (
              <Link
                href="/prebilling"
                className="mt-3 inline-block border border-accent px-3 py-1.5 text-secondary font-medium text-accent transition-colors duration-150 hover:bg-accent/[.06]"
              >
                {ctaLabel}
              </Link>
            ) : null}
          </div>
        ) : null}
      </div>
    </div>
  );
}

function Field({
  label,
  children,
  mono,
}: {
  label: string;
  children: React.ReactNode;
  mono?: boolean;
}) {
  return (
    <div className="flex items-baseline gap-4 px-4 py-2.5">
      <dt className="w-32 shrink-0 label-micro">{label}</dt>
      <dd className={clsx('min-w-0 flex-1 text-secondary text-ink/90', mono && 'font-mono tabular-nums')}>
        {children}
      </dd>
    </div>
  );
}
