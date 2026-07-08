/**
 * ECharts theme «qalam» (Epic A.2): #000 only, weight-diet calm. Series are
 * distinguished by DECAL PATTERNS (hatch/dots) only where the pattern carries
 * meaning, never by hue. Hairline gridlines, 11px mono axis labels, tooltips
 * as quiet hairline cards, 200ms fade draw-in (no stepped dot-matrix motion).
 */

import { fmtTenge, fmtTengeCompact, type NumLocale } from '@/lib/format';

export const INK = '#000';
export const PAPER = '#fff';
export const INK_70 = 'rgba(0,0,0,0.7)';
export const INK_60 = 'rgba(0,0,0,0.6)';
export const INK_40 = 'rgba(0,0,0,0.4)';
export const INK_LINE = 'rgba(0,0,0,0.1)'; // hairline gridlines

/** Canvas cannot inherit CSS vars — resolve the mono stack explicitly. */
export const chartFontFamily = '"IBM Plex Mono", "JetBrains Mono", monospace';

export const CHART_HEIGHT = 300;
/** Calm motion budget (Epic A.2): 200ms fade, no steps easing. */
export const ANIMATION_MS = 200;

/** Decal patterns — used only where a pattern MEANS something (снятия etc.). */
export const decals = {
  hatch: {
    symbol: 'rect',
    dashArrayX: [1, 0],
    dashArrayY: [2, 4],
    rotation: Math.PI / 4,
    color: INK_60,
    symbolSize: 1,
  },
  dots: {
    symbol: 'circle',
    dashArrayX: [
      [6, 6],
      [0, 6, 6, 0],
    ],
    dashArrayY: [6, 0],
    symbolSize: 0.5,
    color: INK_60,
  },
} as const;

export function baseChartOption(): Record<string, unknown> {
  return {
    // Pin the palette so a series without explicit itemStyle can never fall
    // back to ECharts' default hues.
    color: [INK],
    animationDuration: ANIMATION_MS,
    animationDurationUpdate: ANIMATION_MS,
    animationEasing: 'cubicOut',
    animationEasingUpdate: 'cubicOut',
    textStyle: { fontFamily: chartFontFamily, color: INK_60 },
    grid: { left: 8, right: 8, top: 40, bottom: 4, containLabel: true },
  };
}

export function monthAxis(labels: string[]): Record<string, unknown> {
  return {
    type: 'category',
    data: labels,
    axisLine: { lineStyle: { color: INK_LINE, width: 1 } },
    axisTick: { show: false },
    axisLabel: { color: INK_60, fontFamily: chartFontFamily, fontSize: 11 },
  };
}

export function tengeAxis(locale: NumLocale): Record<string, unknown> {
  return {
    type: 'value',
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: INK_LINE } },
    axisLabel: {
      color: INK_60,
      fontFamily: chartFontFamily,
      fontSize: 11,
      formatter: (value: number) => fmtTengeCompact(value, locale),
    },
  };
}

/** Legend entry: bar series pass icon 'rect' (default 'roundRect' is off-spec). */
export type LegendEntry = string | { name: string; icon?: string };

/**
 * Quiet legend row; names in `disabled` render deselected (the "болжам (P6)"
 * placeholder). Markers inherit each series' style — pattern/dash, not hue.
 */
export function chartLegend(
  entries: LegendEntry[],
  disabled: string[] = [],
): Record<string, unknown> {
  const selected: Record<string, boolean> = {};
  for (const name of disabled) selected[name] = false;
  return {
    top: 0,
    left: 0,
    itemWidth: 14,
    itemHeight: 8,
    itemGap: 16,
    data: entries,
    selected,
    inactiveColor: INK_40,
    inactiveBorderColor: INK_40,
    textStyle: { color: INK_60, fontFamily: chartFontFamily, fontSize: 11 },
  };
}

interface TooltipParam {
  seriesName?: string;
  value?: unknown;
  dataIndex?: number;
}

/** Quiet tooltip: paper card, hairline frame, mono, no hue pointer. */
export function tengeTooltip(
  titles: string[],
  axisPointer: 'shadow' | 'line' = 'shadow',
): Record<string, unknown> {
  return {
    trigger: 'axis',
    axisPointer: {
      type: axisPointer,
      lineStyle: { color: INK_40, width: 1, type: 'dashed' },
      shadowStyle: { color: 'rgba(0,0,0,0.04)' },
    },
    transitionDuration: 0,
    backgroundColor: PAPER,
    borderColor: INK,
    borderWidth: 1,
    borderRadius: 0,
    extraCssText: 'box-shadow: 0 1px 0 rgba(0,0,0,0.1);',
    textStyle: { fontFamily: chartFontFamily, fontSize: 12, color: INK },
    formatter: (params: TooltipParam | TooltipParam[]) => {
      const items = Array.isArray(params) ? params : [params];
      if (items.length === 0) return '';
      const index = items[0].dataIndex ?? 0;
      const rows = items
        .filter((p) => typeof p.value === 'number')
        .map(
          (p) => `${p.seriesName ?? ''}: <b>${fmtTenge(p.value as number)}</b>`,
        );
      return `<div style="color:rgba(0,0,0,0.4);margin-bottom:2px">${titles[index] ?? ''}</div>${rows.join('<br/>')}`;
    },
  };
}
