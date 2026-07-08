'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import type { FindingSeverity } from '@/lib/types';

/**
 * Severity chip (§4 soft variant): block = solid ink (the one heavy mark for
 * a blocker), warn = hatch outline, yellow = dotted (0 ₸ fix-only), info =
 * plain. No color, no directional glyph.
 */
const STYLE: Record<FindingSeverity, string> = {
  block: 'border border-ink bg-ink text-paper',
  warn: 'border-2 border-ink/50 text-ink',
  yellow: 'border border-dashed border-ink/40 text-ink/70',
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
