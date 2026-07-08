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

/** KPI tile (Epic A.2): hairline card, micro caption, calm mono figure. */
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
        'bg-paper px-5 py-4',
        pending && !loading
          ? 'border border-dashed border-ink/30'
          : 'border border-ink/15',
      )}
    >
      <p className="label-micro">{label}</p>
      {loading ? (
        <div
          className={clsx(
            'fill-dots-faint mt-3 animate-pulse',
            big ? 'h-10 w-32' : 'h-6 w-24',
          )}
        />
      ) : pending ? (
        <p className="mt-2 font-mono text-h3 text-ink/40">
          {t('common.computed_pending')}
        </p>
      ) : (
        <p
          className={clsx(
            'mt-2 font-mono tabular-nums text-ink',
            big ? 'text-hero' : 'text-h2',
          )}
        >
          {value}
        </p>
      )}
      {sub && !loading && !pending ? (
        <p className="mt-1 font-mono text-secondary tabular-nums text-ink/60">
          {sub}
        </p>
      ) : null}
    </div>
  );
}
