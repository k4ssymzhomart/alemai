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
   * burn-out). Renders "есептелуде…" in a dotted tile — never fake numbers.
   */
  pending?: boolean;
}

/** Ledger KPI tile (docs/15): ink border, uppercase caption, mono number. */
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
        'bg-paper px-4 py-3',
        pending && !loading
          ? 'border border-dashed border-ink/40'
          : big
            ? 'border-2 border-ink shadow-hard'
            : 'border border-ink',
      )}
    >
      <p className="text-caption font-medium uppercase text-ink/70">{label}</p>
      {loading ? (
        <div
          className={clsx(
            'fill-dots-faint mt-2 animate-pulse',
            big ? 'h-10 w-32' : 'h-6 w-24',
          )}
        />
      ) : pending ? (
        <p className="mt-1.5 font-mono text-lg text-ink/40">
          {t('common.computed_pending')}
        </p>
      ) : (
        <p
          className={clsx(
            'mt-1 font-mono font-semibold tabular-nums text-ink',
            big ? 'text-hero' : 'text-xl',
          )}
        >
          {value}
        </p>
      )}
      {sub && !loading && !pending ? (
        <p className="mt-0.5 font-mono text-xs tabular-nums text-ink/70">{sub}</p>
      ) : null}
    </div>
  );
}
