/**
 * Shared ECharts theme (docs/04 §2 design language): plan = light gray bars,
 * fact = accent teal (the money earned), rejected = muted red, cumulative
 * curves in the same hues. Thin axes, no gridline clutter, ₸-formatted
 * compact ticks, full fmtTenge in tooltips, animations ≤ 300 ms.
 */

import { fmtTenge, fmtTengeCompact, type NumLocale } from '@/lib/format';

export const chartColors = {
  plan: '#cbd5e1',
  fact: '#0e7c66',
  rejected: '#b3261e',
  cumulativePlan: '#94a3b8',
  cumulativeFact: '#0e7c66',
  forecastPlaceholder: '#94a3b8',
  axisLine: '#e2e8f0',
  splitLine: '#eef2f6',
  label: '#64748b',
} as const;

/** Canvas cannot inherit CSS fonts — mirror the app's system sans stack. */
export const chartFontFamily =
  'ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif';

export const CHART_HEIGHT = 320;
/** Keep ≤ 300 ms (docs/04 §2: no long animations). */
export const ANIMATION_MS = 250;

export function baseChartOption(): Record<string, unknown> {
  return {
    animationDuration: ANIMATION_MS,
    animationDurationUpdate: ANIMATION_MS,
    textStyle: { fontFamily: chartFontFamily, color: chartColors.label },
    grid: { left: 8, right: 8, top: 44, bottom: 4, containLabel: true },
  };
}

export function monthAxis(labels: string[]): Record<string, unknown> {
  return {
    type: 'category',
    data: labels,
    axisLine: { lineStyle: { color: chartColors.axisLine } },
    axisTick: { show: false },
    axisLabel: {
      color: chartColors.label,
      fontFamily: chartFontFamily,
      fontSize: 11,
    },
  };
}

export function tengeAxis(locale: NumLocale): Record<string, unknown> {
  return {
    type: 'value',
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: chartColors.splitLine } },
    axisLabel: {
      color: chartColors.label,
      fontFamily: chartFontFamily,
      fontSize: 11,
      formatter: (value: number) => fmtTengeCompact(value, locale),
    },
  };
}

/**
 * Legend row; names listed in `disabled` render deselected/grayed — used for
 * the "болжам (P6)" placeholder entry (no data behind it until P6).
 */
export function chartLegend(
  names: string[],
  disabled: string[] = [],
): Record<string, unknown> {
  const selected: Record<string, boolean> = {};
  for (const name of disabled) selected[name] = false;
  return {
    top: 0,
    left: 0,
    itemWidth: 14,
    itemHeight: 8,
    icon: 'roundRect',
    data: names,
    selected,
    textStyle: {
      color: chartColors.label,
      fontFamily: chartFontFamily,
      fontSize: 11,
    },
  };
}

interface TooltipParam {
  seriesName?: string;
  marker?: string;
  value?: unknown;
  dataIndex?: number;
}

/** Axis tooltip with full fmtTenge values; titles[i] = "MM.YYYY" per month. */
export function tengeTooltip(
  titles: string[],
  axisPointer: 'shadow' | 'line' = 'shadow',
): Record<string, unknown> {
  return {
    trigger: 'axis',
    axisPointer: { type: axisPointer },
    borderColor: chartColors.axisLine,
    textStyle: { fontFamily: chartFontFamily, fontSize: 12, color: '#0f172a' },
    formatter: (params: TooltipParam | TooltipParam[]) => {
      const items = Array.isArray(params) ? params : [params];
      if (items.length === 0) return '';
      const index = items[0].dataIndex ?? 0;
      const rows = items
        .filter((p) => typeof p.value === 'number')
        .map(
          (p) =>
            `${p.marker ?? ''}${p.seriesName ?? ''}: <b>${fmtTenge(p.value as number)}</b>`,
        );
      return `<div style="color:#64748b;margin-bottom:2px">${titles[index] ?? ''}</div>${rows.join('<br/>')}`;
    },
  };
}
