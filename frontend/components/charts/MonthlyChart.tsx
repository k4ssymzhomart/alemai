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
 * Monthly plan-vs-fact bars (C2): plan = light gray, fact = teal, rejected
 * (снятия) stacked as a small red segment on top of fact. The "болжам (P6)"
 * legend entry is a disabled placeholder — no forecast data is faked.
 */
export default function MonthlyChart({ months }: { months: MonthlyRow[] }) {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;

  const option = useMemo(() => {
    const labels = months.map((m) => String(m.month).padStart(2, '0'));
    const titles = months.map((m) => fmtPeriod(m.period));
    const planName = t('common.plan');
    const factName = t('common.fact');
    const rejectedName = t('chart.rejected');
    const forecastName = t('chart.forecast_p6');
    return {
      ...baseChartOption(),
      legend: chartLegend(
        [planName, factName, rejectedName, forecastName],
        [forecastName],
      ),
      tooltip: tengeTooltip(titles),
      xAxis: monthAxis(labels),
      yAxis: tengeAxis(locale),
      series: [
        {
          name: planName,
          type: 'bar',
          data: months.map((m) => m.plan_amount),
          barMaxWidth: 18,
          itemStyle: { color: chartColors.plan, borderRadius: [3, 3, 0, 0] },
        },
        {
          name: factName,
          type: 'bar',
          stack: 'fact',
          data: months.map((m) => m.fact_amount),
          barMaxWidth: 18,
          itemStyle: { color: chartColors.fact },
        },
        {
          name: rejectedName,
          type: 'bar',
          stack: 'fact',
          data: months.map((m) => m.rejected_amount),
          barMaxWidth: 18,
          itemStyle: {
            color: chartColors.rejected,
            borderRadius: [3, 3, 0, 0],
          },
        },
        {
          // Placeholder series only — forecast lands in P6, never fake it.
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
