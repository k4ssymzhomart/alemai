'use client';

import { useMemo, useState } from 'react';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import ErrorState from '@/components/ErrorState';
import SeverityChip from '@/components/rules/SeverityChip';
import CodeChip from '@/components/vedomost/CodeChip';
import DeadlineBox from '@/components/vedomost/DeadlineBox';
import StampMark from '@/components/vedomost/StampMark';
import VerdictBlock from '@/components/vedomost/VerdictBlock';
import { downloadFile, downloadFileGet } from '@/lib/api';
import { fmtNumber, fmtTenge, type NumLocale } from '@/lib/format';
import { useObjections, usePrebilling } from '@/lib/hooks';
import type {
  FindingSeverity,
  Objection,
  RuleFindingGroup,
  RunFindings,
} from '@/lib/types';

/** The demo registry the pre-billing check runs over (storyline 5). */
const DEMO_SCOPE = 'period:2025-11';

const SEVERITY_ORDER: Record<FindingSeverity, number> = {
  block: 0,
  warn: 1,
  yellow: 2,
  info: 3,
};

/**
 * Screen 3 — Тексеру (PD2 pre-billing check, beat 4): Кто я → Вердикт («N
 * позиций / ₸ под риском») → Почему (findings by rule, ЕКД chips, StampMark on
 * block rows) → Что делать (export) — then the возражения лента (DF-timers).
 */
export default function PrebillingPage() {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;
  const prebilling = usePrebilling(DEMO_SCOPE);
  const objections = useObjections();

  const groups = useMemo(() => {
    const gs = prebilling.data?.findings.groups ?? [];
    return [...gs].sort(
      (a, b) => SEVERITY_ORDER[a.severity] - SEVERITY_ORDER[b.severity],
    );
  }, [prebilling.data]);

  const totals = prebilling.data?.run.totals;
  const findings = prebilling.data?.findings;

  return (
    <div className="space-y-10">
      <section className="space-y-6">
        <div>
          <h1 className="font-display text-h1 text-ink">{t('nav.prebilling')}</h1>
          <p className="mt-1 label-micro">
            {t('prebilling.who')} · {t('prebilling.registry')}
          </p>
        </div>

        {prebilling.error ? (
          <ErrorState detail={prebilling.error} onRetry={prebilling.retry} />
        ) : prebilling.loading || !totals ? (
          <div className="fill-dots-faint h-24 animate-pulse" />
        ) : (
          <>
            <VerdictBlock critical={totals.block_positions > 0}>
              {totals.block_positions > 0
                ? t('prebilling.verdict_block', {
                    count: totals.block_positions,
                    amount: fmtTenge(totals.block_amount),
                    sanction: fmtTenge(totals.sanction_risk),
                  })
                : t('prebilling.verdict_clean')}
            </VerdictBlock>
            <p className="label-micro">
              {t('prebilling.claims_scanned', {
                n: fmtNumber(totals.claims_scanned),
              })}
            </p>

            <div>
              <p className="mb-3 label-micro">{t('prebilling.sec_findings')}</p>
              <div className="border border-ink/15">
                {groups.map((g, i) => (
                  <RuleRow
                    key={g.rule_code}
                    group={g}
                    findings={findings}
                    locale={locale}
                    last={i === groups.length - 1}
                  />
                ))}
              </div>
            </div>

            <div className="flex flex-wrap gap-3">
              <ExportExceptionsButton />
            </div>
          </>
        )}
      </section>

      <ObjectionsSection state={objections} />
    </div>
  );
}

/** ST-3: the exceptions list Дана hands to врачи for fixing (XLSX). */
function ExportExceptionsButton() {
  const { t } = useTranslation();
  const [busy, setBusy] = useState(false);

  const exportExceptions = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await downloadFileGet(
        '/exports/prebilling.xlsx',
        { scope: DEMO_SCOPE },
        'qalam_prebilling.xlsx',
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <button
      type="button"
      onClick={exportExceptions}
      disabled={busy}
      className="border border-ink/40 px-4 py-2 text-secondary font-medium text-ink transition-colors duration-150 hover:bg-ink/[.03] disabled:opacity-40"
    >
      {t('prebilling.export')}
    </button>
  );
}

function RuleRow({
  group,
  findings,
  locale,
  last,
}: {
  group: RuleFindingGroup;
  findings: RunFindings | undefined;
  locale: NumLocale;
  last: boolean;
}) {
  const { t } = useTranslation();
  const sample = findings?.findings.find((f) => f.rule_code === group.rule_code);
  const ekd = sample?.details?.ekd_code;
  const message =
    (locale === 'kk' ? sample?.details?.message_kk : sample?.details?.message_ru) ??
    sample?.details?.message_ru ??
    null;

  return (
    <div
      className={clsx(
        'flex items-center justify-between gap-4 px-4 py-3',
        !last && 'border-b border-ink/[.08]',
      )}
    >
      <div className="flex min-w-0 flex-1 items-center gap-2">
        <CodeChip code={group.rule_code} />
        {ekd ? <CodeChip code={ekd} /> : null}
        <SeverityChip severity={group.severity} />
        {message ? (
          <span className="truncate text-secondary text-ink/70">{message}</span>
        ) : null}
      </div>
      <div className="flex shrink-0 items-center gap-4">
        {group.severity === 'block' ? (
          <StampMark text={`${t('prebilling.stamp_removed')} · ${ekd ?? ''}`} />
        ) : null}
        <span className="font-mono text-secondary tabular-nums text-ink/60">
          {group.count}
        </span>
        <span className="w-28 text-right font-mono text-secondary tabular-nums text-ink">
          {fmtTenge(group.amount_at_risk)}
        </span>
      </div>
    </div>
  );
}

function ObjectionsSection({
  state,
}: {
  state: ReturnType<typeof useObjections>;
}) {
  const { t } = useTranslation();
  return (
    <section className="space-y-4">
      <div>
        <h2 className="font-display text-h2 text-ink">{t('objections.title')}</h2>
        <p className="mt-1 label-micro">{t('objections.lead')}</p>
      </div>
      {state.error ? (
        <ErrorState detail={state.error} onRetry={state.retry} />
      ) : state.loading || !state.data ? (
        <div className="fill-dots-faint h-24 animate-pulse" />
      ) : (
        <>
          <p className="border-l-2 border-ink px-3 py-2 text-secondary text-ink/80">
            ! {t('objections.silence')}
          </p>
          <div className="flex flex-wrap gap-4">
            {state.data.items.map((o) => (
              <ObjectionCard key={o.case_ref} objection={o} />
            ))}
          </div>
        </>
      )}
    </section>
  );
}

function ObjectionCard({ objection: o }: { objection: Objection }) {
  const { t, i18n } = useTranslation();
  const lang = (i18n.resolvedLanguage ?? 'kk') === 'kk' ? 'kk' : 'ru';
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);

  const draft = async () => {
    if (busy) return;
    setBusy(true);
    setError(false);
    try {
      await downloadFile(
        '/documents/vozrazhenie',
        { case_ref: o.case_ref, lang },
        `vozrazhenie_${o.case_ref}_${lang}.docx`,
      );
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="flex w-64 flex-col gap-3 border border-ink/15 p-4">
      <div className="flex items-center gap-2">
        <CodeChip code={o.ekd_code} />
        {o.yellow ? <SeverityChip severity="yellow" /> : null}
        <span className="font-mono text-micro text-ink/50">{o.case_ref}</span>
      </div>
      <p className="text-secondary text-ink/70">
        {t('objections.case')}: {o.ekd_name_ru}
      </p>
      <DeadlineBox
        deadline={o.deadline_date}
        daysLeft={o.deadline_working_days}
        citation={t('objections.citation')}
        label={
          o.amount_at_stake > 0
            ? `${t('objections.at_stake')} ${fmtTenge(o.amount_at_stake)}`
            : t('sev.yellow')
        }
      />
      <button
        type="button"
        onClick={draft}
        disabled={busy}
        className="border border-ink/40 px-3 py-1.5 text-secondary font-medium text-ink transition-colors duration-150 hover:bg-ink/[.03] disabled:opacity-40"
      >
        {busy ? t('copilot.thinking') : t('objections.construct')}
      </button>
      {error ? <span className="label-micro text-ink/50">{t('common.error')}</span> : null}
    </div>
  );
}
