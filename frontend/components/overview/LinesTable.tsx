'use client';

import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import ExecutionChip from '@/components/overview/ExecutionChip';
import RiskBadge from '@/components/overview/RiskBadge';
import { fmtDate, fmtTenge, type NumLocale } from '@/lib/format';
import type { ContractLine } from '@/lib/types';

interface LinesTableProps {
  /** Server order (plan_amount_year desc) is kept as-is. */
  lines: ContractLine[];
  year: number;
}

/** Contract lines table (QA Beat 1 columns); row click → drill-down (C2). */
export default function LinesTable({ lines, year }: LinesTableProps) {
  const { t, i18n } = useTranslation();
  const router = useRouter();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;

  const open = (line: ContractLine) => {
    // line_key contains ':' / '-' — always URL-encode it in paths.
    router.push(`/overview/${encodeURIComponent(line.line_key)}?year=${year}`);
  };

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-xs uppercase tracking-wide text-slate-500">
            <th className="px-3 py-2 font-medium">{t('overview.table.line')}</th>
            <th className="px-3 py-2 font-medium">{t('overview.table.care_type')}</th>
            <th className="px-3 py-2 font-medium">{t('overview.table.source')}</th>
            <th className="px-3 py-2 text-right font-medium">{t('overview.table.plan')}</th>
            <th className="px-3 py-2 text-right font-medium">{t('overview.table.fact')}</th>
            <th className="px-3 py-2 text-right font-medium">
              {t('overview.table.execution_pct')}
            </th>
            <th className="px-3 py-2 font-medium">{t('overview.table.risk')}</th>
            <th className="px-3 py-2 font-medium">
              {t('overview.table.burn_out_date')}
            </th>
          </tr>
        </thead>
        <tbody>
          {lines.map((line) => (
            <tr
              key={line.line_key}
              tabIndex={0}
              onClick={() => open(line)}
              onKeyDown={(event) => {
                if (event.key === 'Enter') open(line);
              }}
              className="cursor-pointer border-b border-slate-100 transition-colors last:border-0 hover:bg-accent-50/60 focus:bg-accent-50/60 focus:outline-none"
            >
              <td className="max-w-xs px-3 py-2 font-medium text-slate-800">
                {line.service_group || t(`care_type.${line.care_type}`)}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-slate-600">
                {t(`care_type.${line.care_type}`)}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-slate-600">
                {t(`funding.${line.funding_source}`)}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-right tabular-nums text-slate-800">
                {fmtTenge(line.plan_amount_year)}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-right tabular-nums text-slate-800">
                {fmtTenge(line.fact_amount_ytd)}
              </td>
              <td className="whitespace-nowrap px-3 py-2 text-right">
                <ExecutionChip pct={line.execution_pct_ytd} locale={locale} />
              </td>
              <td className="whitespace-nowrap px-3 py-2">
                <RiskBadge riskClass={line.risk_class} />
              </td>
              <td className="whitespace-nowrap px-3 py-2 tabular-nums text-slate-500">
                {line.burn_out_date ? fmtDate(line.burn_out_date) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
