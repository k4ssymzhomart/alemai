'use client';

import clsx from 'clsx';
import type { ReactNode } from 'react';

/**
 * VerdictBlock (rebrand v3, docs/25 H1): a white card with a hairline frame and
 * a 2px left rule, verdict in the display serif. `critical` now reads as a
 * red-tinted left rule over a light band (not solid black) — the band stays
 * white so the verdict text carries. Print degrades to ink.
 */
export default function VerdictBlock({
  children,
  critical = false,
}: {
  children: ReactNode;
  critical?: boolean;
}) {
  return (
    <div
      className={clsx(
        'border-l-2 px-6 py-4',
        critical
          ? 'border border-critical/30 border-l-critical bg-critical/5 text-ink print:border-ink print:border-l-ink print:bg-paper'
          : 'border border-ink/15 border-l-ink bg-paper text-ink',
      )}
    >
      <p className="font-display text-h2 leading-snug">{children}</p>
    </div>
  );
}
