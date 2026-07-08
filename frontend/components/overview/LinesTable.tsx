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
 * Contract lines ledger (QA Beat 1 columns + ExecutionBar per docs/15 §9);
 * row click → drill-down (C2); row hover = full invert — stamp, not fade.
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
      <table className="w-full border-collapse text-sm">
        <thead>
          <tr className="border-b-2 border-ink text-left font-mono text-caption uppercase text-ink/70">
            <th className="px-3 py-2 font-medium">{t('overview.table.line')}</th>
            <th className="px-3 py-2 font-medium">{t('overview.table.source')}</th>
            <th className="px-3 py-2 text-right font-medium">{t('overview.table.plan')}</th>
            <th className="px-3 py-2 text-right font-medium">{t('overview.table.fact')}</th>
            <th className="w-40 px-3 py-2 font-medium">
              {t('overview.table.execution_bar')}
            </th>
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
              className="hover-stamp group cursor-pointer border-b border-ink/[.12] last:border-b-2 last:border-ink hover:bg-ink hover:text-paper focus:bg-ink focus:text-paper focus:outline-none"
            >
              <td className="max-w-xs px-3 py-2.5 font-medium">
                {line.service_group || t(`care_type.${line.care_type}`)}
              </td>
              <td className="whitespace-nowrap px-3 py-2.5">
                {t(`funding.${line.funding_source}`)}
              </td>
              <td className="whitespace-nowrap px-3 py-2.5 text-right font-mono tabular-nums">
                {fmtTenge(line.plan_amount_year)}
              </td>
              <td className="whitespace-nowrap px-3 py-2.5 text-right font-mono tabular-nums">
                {fmtTenge(line.fact_amount_ytd)}
              </td>
              <td className="px-3 py-2.5 group-hover:invert group-focus:invert">
                <ExecutionBar
                  planYear={line.plan_amount_year}
                  factYtd={line.fact_amount_ytd}
                  planYtd={line.plan_amount_ytd}
                />
              </td>
              <td className="whitespace-nowrap px-3 py-2.5 text-right group-hover:invert group-focus:invert">
                <ExecutionChip pct={line.execution_pct_ytd} locale={locale} />
              </td>
              <td className="whitespace-nowrap px-3 py-2.5 group-hover:invert group-focus:invert">
                <RiskBadge riskClass={line.risk_class} />
              </td>
              <td className="whitespace-nowrap px-3 py-2.5 font-mono tabular-nums">
                {line.burn_out_date ? fmtDate(line.burn_out_date) : '—'}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
