'use client';

import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import EChart from '@/components/charts/EChart';
import {
  INK,
  INK_40,
  baseChartOption,
  chartLegend,
  monthAxis,
  tengeAxis,
  tengeTooltip,
} from '@/lib/chartTheme';
import { fmtPeriod, type NumLocale } from '@/lib/format';
import type { MonthlyRow } from '@/lib/types';

/**
 * Cumulative plan vs fact curves (C2), «vedomost»: plan = dashed 2px ink,
 * fact = solid 2.5px ink with a faint ink-wash area. The fact curve flattens
 * after the as-of month — honest, no extrapolation. "Болжам (P6)" stays a
 * disabled legend placeholder until the forecast lands.
 */
export default function CumulativeChart({ months }: { months: MonthlyRow[] }) {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;

  const option = useMemo(() => {
    const labels = months.map((m) => String(m.month).padStart(2, '0'));
    const titles = months.map((m) => fmtPeriod(m.period));
    const cumulativePlanName = t('chart.cumulative_plan');
    const cumulativeFactName = t('chart.cumulative_fact');
    const forecastName = t('chart.forecast_p6');
    return {
      ...baseChartOption(),
      legend: chartLegend(
        [cumulativePlanName, cumulativeFactName, forecastName],
        [forecastName],
      ),
      tooltip: tengeTooltip(titles, 'line'),
      xAxis: monthAxis(labels),
      yAxis: tengeAxis(locale),
      series: [
        {
          name: cumulativePlanName,
          type: 'line',
          data: months.map((m) => m.cumulative_plan_amount),
          symbol: 'none',
          lineStyle: { width: 1, type: 'dashed', color: INK },
          itemStyle: { color: INK },
        },
        {
          name: cumulativeFactName,
          type: 'line',
          data: months.map((m) => m.cumulative_fact_amount),
          symbol: 'none',
          lineStyle: { width: 2, color: INK },
          itemStyle: { color: INK },
          areaStyle: { color: 'rgba(0, 0, 0, 0.04)' },
        },
        {
          // Placeholder series only — forecast band arrives in P6.
          name: forecastName,
          type: 'line',
          data: [],
          lineStyle: { type: 'dotted', color: INK_40 },
          itemStyle: { color: INK_40 },
        },
      ],
    };
  }, [months, locale, t]);

  return <EChart option={option} />;
}
