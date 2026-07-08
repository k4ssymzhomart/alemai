'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import type { RiskClass } from '@/lib/types';

/**
 * Risk badge (Epic A.2): outline chips carry severity by a leading glyph +
 * 11px caps label. Solid black is reserved for CRITICAL classes only — the
 * one allowed heavy mark, per the weight diet. risk_class is null until P6.
 */
const CLASS_STYLES: Record<RiskClass, { chip: string; glyph: string }> = {
  critical_under: { chip: 'border border-ink bg-ink text-paper', glyph: '▲' },
  under: { chip: 'border border-ink/40 text-ink', glyph: '▽' },
  on_track: { chip: 'border border-ink/40 text-ink/70', glyph: '' },
  over: { chip: 'border border-ink/40 text-ink', glyph: '△' },
  critical_over: { chip: 'border border-ink bg-ink text-paper', glyph: '▲' },
};

export default function RiskBadge({ riskClass }: { riskClass: RiskClass | null }) {
  const { t } = useTranslation();

  if (!riskClass) {
    return (
      <span className="inline-flex border border-dashed border-ink/30 px-2 py-0.5 font-mono text-micro text-ink/40">
        —
      </span>
    );
  }

  const { chip, glyph } = CLASS_STYLES[riskClass];
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 px-2 py-0.5 text-micro uppercase',
        chip,
      )}
    >
      {glyph ? <span aria-hidden>{glyph}</span> : null}
      {t(`risk.class.${riskClass}`)}
    </span>
  );
}
