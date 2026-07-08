'use client';

import clsx from 'clsx';
import type { ReactNode } from 'react';
import { useTranslation } from 'react-i18next';

interface KpiTileProps {
  label: string;
  value?: ReactNode;
  /** Secondary line under the value (e.g. "Жоспар: 2 592 383 156 ₸"). */
  sub?: ReactNode;
  /** Hero-sized value (the % игерілуі tile). */
  big?: boolean;
  loading?: boolean;
  /**
   * Computed-pending style: value arrives with P6 (forecast gap, risk count,
   * burn-out). Renders "есептелуде…" in a dashed tile — never fake numbers.
   */
  pending?: boolean;
}

export default function KpiTile({
  label,
  value,
  sub,
  big = false,
  loading = false,
  pending = false,
}: KpiTileProps) {
  const { t } = useTranslation();

  return (
    <div
      className={clsx(
        'rounded-lg border bg-white px-4 py-3',
        pending && !loading ? 'border-dashed border-slate-300' : 'border-slate-200',
      )}
    >
      <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
        {label}
      </p>
      {loading ? (
        <div
          className={clsx(
            'mt-2 animate-pulse rounded bg-slate-100',
            big ? 'h-8 w-28' : 'h-6 w-24',
          )}
        />
      ) : pending ? (
        <p className="mt-1.5 text-lg italic leading-7 text-slate-400">
          {t('common.computed_pending')}
        </p>
      ) : (
        <p
          className={clsx(
            'mt-1 font-semibold tabular-nums text-slate-900',
            big ? 'text-3xl' : 'text-xl',
          )}
        >
          {value}
        </p>
      )}
      {sub && !loading && !pending ? (
        <p className="mt-0.5 text-xs tabular-nums text-slate-500">{sub}</p>
      ) : null}
    </div>
  );
}
