'use client';

import clsx from 'clsx';
import type { ReactNode } from 'react';

/**
 * VerdictBlock (Epic A.2 — de-brutalized): a white card with a hairline frame
 * and a 2px ink left rule, verdict set in the display serif, sentence case.
 * `critical` is the ONE screen element allowed to go solid black — reserved
 * for a critical status or a ≤2-day objection timer.
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
          ? 'border border-ink border-l-ink bg-ink text-paper'
          : 'border border-ink/15 border-l-ink bg-paper text-ink',
      )}
    >
      <p className="font-display text-h2 leading-snug">{children}</p>
    </div>
  );
}
