/**
 * ECharts theme «vedomost» (docs/15 §7): #000 only. Series are distinguished
 * by DECAL PATTERNS (solid / 45° hatch / dots / crosshatch), never by hue.
 * Plan = dashed 2px black; fact = solid; rejected = hatch; forecast (P6) =
 * white with dashed border + dotted CI. Gridlines ink-12, labels Plex Mono,
 * tooltips white with 1px black border + hard shadow, draw-in ≤200ms with
 * steps easing — dot-matrix printer feel.
 */

import { fmtTenge, fmtTengeCompact, type NumLocale } from '@/lib/format';

export const INK = '#000';
export const PAPER = '#fff';
export const INK_70 = 'rgba(0,0,0,0.7)';
export const INK_40 = 'rgba(0,0,0,0.4)';
export const INK_12 = 'rgba(0,0,0,0.12)';

/** Canvas cannot inherit CSS vars — resolve the mono stack explicitly. */
export const chartFontFamily = '"IBM Plex Mono", "JetBrains Mono", monospace';

export const CHART_HEIGHT = 320;
/** Mechanical motion budget (docs/15 §6): ≤200ms. */
export const ANIMATION_MS = 200;

/** Decal patterns for monochrome series distinction (docs/15 §7). */
export const decals = {
  hatch: {
    symbol: 'rect',
    dashArrayX: [1, 0],
    dashArrayY: [2, 4],
    rotation: Math.PI / 4,
    color: INK,
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
    color: INK,
  },
  crosshatch: {
    symbol: 'rect',
    dashArrayX: [1, 0],
    dashArrayY: [1, 3],
    rotation: -Math.PI / 4,
    color: INK,
    symbolSize: 1,
  },
} as const;

/** steps(4) — the §6 dot-matrix draw-in. */
const steps4 = (k: number) => Math.ceil(k * 4) / 4;

export function baseChartOption(): Record<string, unknown> {
  return {
    // Pin the palette so a series without explicit itemStyle can never fall
    // back to ECharts' default hues (docs/15 §11: violations impossible).
    color: [INK],
    animationDuration: ANIMATION_MS,
    animationDurationUpdate: ANIMATION_MS,
    animationEasing: steps4,
    animationEasingUpdate: steps4,
    textStyle: { fontFamily: chartFontFamily, color: INK_70 },
    grid: { left: 8, right: 8, top: 44, bottom: 4, containLabel: true },
  };
}

export function monthAxis(labels: string[]): Record<string, unknown> {
  return {
    type: 'category',
    data: labels,
    axisLine: { lineStyle: { color: INK, width: 1 } },
    axisTick: { show: false },
    axisLabel: {
      color: INK_70,
      fontFamily: chartFontFamily,
      fontSize: 12,
    },
  };
}

export function tengeAxis(locale: NumLocale): Record<string, unknown> {
  return {
    type: 'value',
    axisLine: { show: false },
    axisTick: { show: false },
    splitLine: { lineStyle: { color: INK_12 } },
    axisLabel: {
      color: INK_70,
      fontFamily: chartFontFamily,
      fontSize: 12,
      formatter: (value: number) => fmtTengeCompact(value, locale),
    },
  };
}

/** Legend entry: bar series pass icon 'rect' (default 'roundRect' is off-spec). */
export type LegendEntry = string | { name: string; icon?: string };

/**
 * Legend row; names in `disabled` render deselected — used for the
 * "болжам (P6)" placeholder (no data behind it until P6). Legend markers
 * inherit each series' decal/line style, so patterns (not hues) tell them
 * apart; bar entries must pass icon 'rect' to kill the rounded default.
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
    itemWidth: 16,
    itemHeight: 10,
    data: entries,
    selected,
    inactiveColor: INK_40,
    inactiveBorderColor: INK_40,
    textStyle: {
      color: INK_70,
      fontFamily: chartFontFamily,
      fontSize: 11,
    },
  };
}

interface TooltipParam {
  seriesName?: string;
  value?: unknown;
  dataIndex?: number;
}

/** Document-style tooltip: paper bg, 1px ink border, hard shadow, mono. */
export function tengeTooltip(
  titles: string[],
  axisPointer: 'shadow' | 'line' = 'shadow',
): Record<string, unknown> {
  return {
    trigger: 'axis',
    // Style the pointer explicitly — ECharts defaults are blue-gray hues.
    axisPointer: {
      type: axisPointer,
      lineStyle: { color: INK, width: 1, type: 'dashed' },
      shadowStyle: { color: INK_12 },
    },
    transitionDuration: 0,
    backgroundColor: PAPER,
    borderColor: INK,
    borderWidth: 1,
    borderRadius: 0,
    extraCssText: 'box-shadow: 4px 4px 0 0 #000;',
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
