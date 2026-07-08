'use client';

import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import ExecutionChip from '@/components/overview/ExecutionChip';
import RiskBadge from '@/components/overview/RiskBadge';
import ExecutionBar from '@/components/vedomost/ExecutionBar';
import { fmtDate, fmtTenge, type NumLocale } from '@/lib/format';
import type { ContractLine } from '@/lib/types';

interface LinesTableProps {
  /** Server order (plan_amount_year desc) is kept as-is. */
  lines: ContractLine[];
  year: number;
}

/**
 * Contract lines ledger (Epic A.2): hairline dividers, roomy 44px rows, micro
 * caps headers; row hover = faint wash + underlined primary cell (no invert);
 * row click → drill-down (C2).
 */
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
      <table className="w-full border-collapse text-secondary">
        <thead>
          <tr className="border-b border-ink/15 text-left label-micro">
            <th className="px-3 py-2 font-normal">{t('overview.table.line')}</th>
            <th className="px-3 py-2 font-normal">{t('overview.table.source')}</th>
            <th className="px-3 py-2 text-right font-normal">{t('overview.table.plan')}</th>
            <th className="px-3 py-2 text-right font-normal">{t('overview.table.fact')}</th>
            <th className="w-40 px-3 py-2 font-normal">
              {t('overview.table.execution_bar')}
            </th>
            <th className="px-3 py-2 text-right font-normal">
              {t('overview.table.execution_pct')}
            </th>
            <th className="px-3 py-2 font-normal">{t('overview.table.risk')}</th>
            <th className="px-3 py-2 font-normal">
              {t('overview.table.burn_out_date')}
            </th>
          </tr>
        </thead>
        <tbody>
          {lines.map((line) => (
            <tr
              key={line.line_key}
              tabIndex={0}
              aria-label={line.service_group || t(`care_type.${line.care_type}`)}
              onClick={() => open(line)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault();
                  open(line);
                }
              }}
              className="group h-row cursor-pointer border-b border-ink/[.08] transition-colors duration-150 last:border-0 hover:bg-ink/[.03] focus:bg-ink/[.03] focus:outline-none"
            >
              <td className="max-w-xs px-3 font-medium text-ink group-hover:underline group-focus:underline">
                {line.service_group || t(`care_type.${line.care_type}`)}
              </td>
              <td className="whitespace-nowrap px-3 text-ink/70">
                {t(`funding.${line.funding_source}`)}
              </td>
              <td className="whitespace-nowrap px-3 text-right font-mono tabular-nums text-ink/70">
                {fmtTenge(line.plan_amount_year)}
              </td>
              <td className="whitespace-nowrap px-3 text-right font-mono tabular-nums text-ink">
                {fmtTenge(line.fact_amount_ytd)}
              </td>
              <td className="px-3">
                <ExecutionBar
                  planYear={line.plan_amount_year}
                  factYtd={line.fact_amount_ytd}
                  planYtd={line.plan_amount_ytd}
                />
              </td>
              <td className="whitespace-nowrap px-3 text-right">
                <ExecutionChip pct={line.execution_pct_ytd} locale={locale} />
              </td>
              <td className="whitespace-nowrap px-3">
                <RiskBadge riskClass={line.risk_class} />
              </td>
              <td className="whitespace-nowrap px-3 font-mono tabular-nums text-ink/60">
                {line.burn_out_date ? fmtDate(line.burn_out_date) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
