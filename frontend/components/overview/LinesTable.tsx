'use client';

import { Fragment, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import ExecutionChip from '@/components/overview/ExecutionChip';
import RiskBadge from '@/components/overview/RiskBadge';
import ExecutionBar from '@/components/vedomost/ExecutionBar';
import { fmtDate, fmtTenge, type NumLocale } from '@/lib/format';
import type { ContractLine } from '@/lib/types';

interface LinesTableProps {
  /** Server order (plan_amount_year desc) is kept within each group. */
  lines: ContractLine[];
  year: number;
}

interface LineGroup {
  key: string;
  careType: string;
  serviceGroup: string;
  rows: ContractLine[];
}

/**
 * Contract lines ledger (Epic C · F4): grouped by care type / service group so
 * the two funding-source rows sit under one human-named header instead of
 * reading as duplicate «МСАК / МСАК» lines. Each source row carries the F1
 * execution cell + F5 bar and is independently clickable to its drill-down.
 */
export default function LinesTable({ lines, year }: LinesTableProps) {
  const { t, i18n } = useTranslation();
  const router = useRouter();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;

  const groups = useMemo<LineGroup[]>(() => {
    const map = new Map<string, LineGroup>();
    for (const line of lines) {
      const key = `${line.care_type}|${line.service_group}`;
      let g = map.get(key);
      if (!g) {
        g = {
          key,
          careType: line.care_type,
          serviceGroup: line.service_group,
          rows: [],
        };
        map.set(key, g);
      }
      g.rows.push(line);
    }
    return [...map.values()];
  }, [lines]);

  const open = (line: ContractLine) => {
    router.push(`/overview/${encodeURIComponent(line.line_key)}?year=${year}`);
  };

  const annualPct = (line: ContractLine) =>
    line.plan_amount_year > 0
      ? (line.fact_amount_ytd / line.plan_amount_year) * 100
      : 0;

  return (
    <div className="overflow-x-auto">
      <table className="w-full border-collapse text-secondary">
        <thead>
          <tr className="border-b border-ink/15 text-left label-micro">
            <th className="px-3 py-2 font-normal">{t('overview.table.line')}</th>
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
          {groups.map((group) => {
            const short = group.serviceGroup || t(`care_type.${group.careType}`);
            const full = t(`care_type_full.${group.careType}`);
            return (
              <Fragment key={group.key}>
                <tr className="border-t border-ink/15 bg-ink/[.02]">
                  <td colSpan={7} className="px-3 py-1.5">
                    <span className="font-medium text-ink">{short}</span>
                    {full && full !== short ? (
                      <span className="ml-2 text-secondary text-ink/50">
                        · {full}
                      </span>
                    ) : null}
                  </td>
                </tr>
                {group.rows.map((line) => (
                  <tr
                    key={line.line_key}
                    tabIndex={0}
                    aria-label={`${short} · ${t(`funding.${line.funding_source}`)}`}
                    onClick={() => open(line)}
                    onKeyDown={(event) => {
                      if (event.key === 'Enter' || event.key === ' ') {
                        event.preventDefault();
                        open(line);
                      }
                    }}
                    className="group h-row cursor-pointer border-b border-ink/[.08] transition-colors duration-150 hover:bg-ink/[.03] focus:bg-ink/[.03] focus:outline-none"
                  >
                    <td className="px-3 pl-6">
                      <span className="inline-flex border border-ink/25 px-1.5 py-0.5 font-mono text-micro text-ink/70">
                        {t(`funding.${line.funding_source}`)}
                      </span>
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
                        forecastYear={line.forecast_amount_year}
                      />
                    </td>
                    <td className="whitespace-nowrap px-3 text-right">
                      <ExecutionChip
                        pctYtd={line.execution_pct_ytd}
                        pctAnnual={annualPct(line)}
                        locale={locale}
                      />
                    </td>
                    <td className="whitespace-nowrap px-3">
                      <RiskBadge riskClass={line.risk_class} />
                    </td>
                    <td className="whitespace-nowrap px-3 font-mono tabular-nums text-ink/60">
                      {line.burn_out_date ? fmtDate(line.burn_out_date) : '—'}
                    </td>
                  </tr>
                ))}
              </Fragment>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
