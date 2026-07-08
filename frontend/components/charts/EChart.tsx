'use client';

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

/** Thin wrapper: shared height, responsive width, no option merging. */
export default function EChart({ option }: { option: Record<string, unknown> }) {
  return (
    <ReactECharts
      option={option}
      notMerge
      style={{ height: CHART_HEIGHT, width: '100%' }}
    />
  );
}
