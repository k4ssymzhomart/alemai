'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import type { RiskClass } from '@/lib/types';

/**
 * Severity without color (docs/15 §4): critical → inverted black block with
 * ▲ glyph; risk → hatch + ◤; on-track → plain 1px chip. Weight + pattern +
 * glyph carry the hierarchy — never hue, never icon-only.
 */
const CLASS_STYLES: Record<RiskClass, { chip: string; glyph: string }> = {
  critical_under: { chip: 'border-4 border-ink bg-ink text-paper', glyph: '▲' },
  under: { chip: 'fill-hatch-light border-2 border-ink text-ink', glyph: '◤' },
  on_track: { chip: 'border border-ink text-ink', glyph: '' },
  over: { chip: 'fill-hatch-light border-2 border-ink text-ink', glyph: '◤' },
  critical_over: { chip: 'border-4 border-ink bg-ink text-paper', glyph: '▲' },
};

/**
 * Server-computed risk class badge. risk_class is null until P6 → neutral
 * "—" chip (computed-pending, not an error and not a fake value).
 */
export default function RiskBadge({ riskClass }: { riskClass: RiskClass | null }) {
  const { t } = useTranslation();

  if (!riskClass) {
    return (
      <span className="inline-flex border border-ink/40 px-2 py-0.5 font-mono text-xs text-ink/40">
        —
      </span>
    );
  }

  const { chip, glyph } = CLASS_STYLES[riskClass];
  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1 px-2 py-0.5 text-xs font-semibold uppercase',
        chip,
      )}
    >
      {glyph ? <span aria-hidden>{glyph}</span> : null}
      {t(`risk.class.${riskClass}`)}
    </span>
  );
}
