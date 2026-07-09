'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import type { FindingSeverity } from '@/lib/types';

/**
 * Severity chip (rebrand v3, docs/25 H1): color is now the primary signal.
 * block = red fill, warn = amber outline+tint, yellow (0 ₸ fix-only) = amber
 * dashed, info = plain. Print degrades to ink (keeps the ч/б story honest).
 */
const STYLE: Record<FindingSeverity, string> = {
  block: 'border border-critical bg-critical text-paper print:border-ink print:bg-ink',
  warn: 'border-2 border-warn bg-warn/10 text-ink print:border-ink print:bg-transparent',
  yellow: 'border border-dashed border-warn text-ink/70 print:border-ink',
  info: 'border border-ink/15 text-ink/60',
};

export default function SeverityChip({ severity }: { severity: FindingSeverity }) {
  const { t } = useTranslation();
  return (
    <span
      className={clsx(
        'inline-flex items-center px-2 py-0.5 text-micro uppercase',
        STYLE[severity],
      )}
    >
      {t(`sev.${severity}`)}
    </span>
  );
}
