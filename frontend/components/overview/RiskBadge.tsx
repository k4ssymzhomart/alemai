'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import type { RiskClass } from '@/lib/types';

const CLASS_STYLES: Record<RiskClass, string> = {
  critical_under: 'bg-red-50 text-red-700 ring-red-200',
  under: 'bg-amber-50 text-amber-700 ring-amber-200',
  on_track: 'bg-emerald-50 text-emerald-700 ring-emerald-200',
  over: 'bg-amber-50 text-amber-700 ring-amber-200',
  critical_over: 'bg-red-50 text-red-700 ring-red-200',
};

/**
 * Server-computed risk class badge. risk_class is null until P6 → neutral
 * "—" chip (computed-pending, not an error and not a fake value).
 */
export default function RiskBadge({ riskClass }: { riskClass: RiskClass | null }) {
  const { t } = useTranslation();

  if (!riskClass) {
    return (
      <span className="inline-flex rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-400 ring-1 ring-inset ring-slate-200">
        —
      </span>
    );
  }

  return (
    <span
      className={clsx(
        'inline-flex rounded-full px-2 py-0.5 text-xs font-semibold ring-1 ring-inset',
        CLASS_STYLES[riskClass],
      )}
    >
      {t(`risk.class.${riskClass}`)}
    </span>
  );
}
