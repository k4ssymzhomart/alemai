'use client';

import type { ReactNode } from 'react';

/**
 * VerdictBlock (docs/15 §5): full-width black band, white display type,
 * ONE sentence. The only black band allowed on a screen — it IS the verdict.
 */
export default function VerdictBlock({ children }: { children: ReactNode }) {
  return (
    <div className="border-2 border-ink bg-ink px-6 py-4">
      <p className="font-display text-verdict font-medium uppercase leading-tight text-paper">
        {children}
      </p>
    </div>
  );
}
