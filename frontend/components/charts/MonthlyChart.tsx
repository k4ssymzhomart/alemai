'use client';

import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';

import EChart from '@/components/charts/EChart';
import {
  INK,
  INK_40,
  PAPER,
  baseChartOption,
  chartLegend,
  decals,
  monthAxis,
  tengeAxis,
  tengeTooltip,
} from '@/lib/chartTheme';
import { fmtPeriod, type NumLocale } from '@/lib/format';
import type { MonthlyRow } from '@/lib/types';

/**
 * Monthly plan-vs-fact bars (C2), «vedomost»: plan = white bar with ink
 * border, fact = solid ink, rejected (снятия) = hatch decal stacked on fact.
 * The "болжам (P6)" legend entry stays a disabled placeholder — no fake data.
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
        [
          { name: planName, icon: 'rect' },
          { name: factName, icon: 'rect' },
          { name: rejectedName, icon: 'rect' },
          forecastName,
        ],
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
          itemStyle: { color: PAPER, borderColor: INK, borderWidth: 1 },
        },
        {
          name: factName,
          type: 'bar',
          stack: 'fact',
          data: months.map((m) => m.fact_amount),
          barMaxWidth: 18,
          itemStyle: { color: INK },
        },
        {
          name: rejectedName,
          type: 'bar',
          stack: 'fact',
          data: months.map((m) => m.rejected_amount),
          barMaxWidth: 18,
          itemStyle: {
            color: PAPER,
            borderColor: INK,
            borderWidth: 1,
            decal: decals.hatch,
          },
        },
        {
          // Placeholder series only — forecast lands in P6, never fake it.
          name: forecastName,
          type: 'line',
          data: [],
          lineStyle: { type: 'dashed', color: INK_40 },
          itemStyle: { color: INK_40 },
        },
      ],
    };
  }, [months, locale, t]);

  return <EChart option={option} />;
}
