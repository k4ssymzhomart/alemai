'use client';

import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import EChart from '@/components/charts/EChart';
import {
  baseChartOption,
  chartColors,
  chartLegend,
  monthAxis,
  tengeAxis,
  tengeTooltip,
} from '@/lib/chartTheme';
import { fmtPeriod, type NumLocale } from '@/lib/format';
import type { MonthlyRow } from '@/lib/types';

/**
 * Cumulative plan vs fact curves (C2). The fact curve flattens after the
 * as-of month (fact months are zero-filled) — honest, no extrapolation.
 * "Болжам (P6)" is a disabled legend placeholder until the forecast lands.
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
          lineStyle: {
            width: 2,
            type: 'dashed',
            color: chartColors.cumulativePlan,
          },
          itemStyle: { color: chartColors.cumulativePlan },
        },
        {
          name: cumulativeFactName,
          type: 'line',
          data: months.map((m) => m.cumulative_fact_amount),
          symbol: 'none',
          lineStyle: { width: 2.5, color: chartColors.cumulativeFact },
          itemStyle: { color: chartColors.cumulativeFact },
          areaStyle: { color: 'rgba(14, 124, 102, 0.06)' },
        },
        {
          // Placeholder series only — forecast band arrives in P6.
          name: forecastName,
          type: 'line',
          data: [],
          lineStyle: { type: 'dashed', color: chartColors.forecastPlaceholder },
          itemStyle: { color: chartColors.forecastPlaceholder },
        },
      ],
    };
  }, [months, locale, t]);

  return <EChart option={option} />;
}
