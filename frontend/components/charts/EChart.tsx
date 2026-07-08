'use client';

import { useMemo } from 'react';
import dynamic from 'next/dynamic';

import { CHART_HEIGHT } from '@/lib/chartTheme';

/** ECharts touches the DOM — load client-side only, skeleton while loading. */
const ReactECharts = dynamic(() => import('echarts-for-react'), {
  ssr: false,
  loading: () => (
    <div
      style={{ height: CHART_HEIGHT }}
      className="fill-dots-faint animate-pulse"
    />
  ),
});

/**
 * Thin wrapper: shared height, responsive width, no option merging.
 * Draw-in animation is dropped entirely under prefers-reduced-motion
 * (docs/15 §6) — CSS can't reach canvas, so it's handled here.
 */
export default function EChart({ option }: { option: Record<string, unknown> }) {
  const finalOption = useMemo(() => {
    const reduced =
      typeof window !== 'undefined' &&
      window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    return reduced ? { ...option, animation: false } : option;
  }, [option]);

  return (
    <ReactECharts
      option={finalOption}
      notMerge
      style={{ height: CHART_HEIGHT, width: '100%' }}
    />
  );
}
