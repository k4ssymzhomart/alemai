'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import type { RiskClass } from '@/lib/types';

/**
 * Risk badge (rebrand v3, docs/25 H1): color is the primary signal, the glyph
 * stays as a colour-blind-safe backup. critical = red fill, under/over-risk =
 * amber, on_track = green. Print degrades to ink. risk_class is null until P6.
 */
const CLASS_STYLES: Record<RiskClass, { chip: string; glyph: string }> = {
  critical_under: { chip: 'border border-critical bg-critical text-paper print:border-ink print:bg-ink', glyph: '▲' },
  under: { chip: 'border border-warn bg-warn/10 text-ink print:border-ink print:bg-transparent', glyph: '▽' },
  on_track: { chip: 'border border-ok bg-ok/10 text-ink print:border-ink print:bg-transparent', glyph: '' },
  over: { chip: 'border border-warn bg-warn/10 text-ink print:border-ink print:bg-transparent', glyph: '△' },
  critical_over: { chip: 'border border-critical bg-critical text-paper print:border-ink print:bg-ink', glyph: '▲' },
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
