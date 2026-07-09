'use client';

import { useMemo } from 'react';
import Link from 'next/link';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import EmptyState from '@/components/EmptyState';
import ErrorState from '@/components/ErrorState';
import { fmtDate } from '@/lib/format';
import { useDeadlines, useObjections } from '@/lib/hooks';

interface CalItem {
  key: string;
  date: string;
  title: string;
  caption: string;
  critical?: boolean;
  link?: string;
}

/**
 * Screen — Календарь (H2 fill-or-kill): a date-sorted ledger of regulatory
 * deadlines (seeded /deadlines, incl. the 01.01.2027 перечни update) merged
 * with the live возражение timers (/objections). No calendar-grid library —
 * a clean ledger by date. Objection rows link to the pre-billing screen.
 */
export default function CalendarPage() {
  const { t } = useTranslation();
  const deadlines = useDeadlines();
  const objections = useObjections();
  const loading = deadlines.loading || objections.loading;
  const error = deadlines.error ?? objections.error;

  const items = useMemo<CalItem[]>(() => {
    const out: CalItem[] = [];
    for (const d of deadlines.data?.deadlines ?? []) {
      out.push({
        key: `d-${d.id}`,
        date: d.ends,
        title: d.note ?? d.kind,
        caption: t(`calendar.kind.${d.kind}`, { defaultValue: d.kind }),
      });
    }
    for (const o of objections.data?.items ?? []) {
      out.push({
        key: `o-${o.case_ref}`,
        date: o.deadline_date,
        title: t('calendar.objection', { code: o.ekd_code }),
        caption: t('calendar.days_left', { count: o.deadline_working_days }),
        critical: o.deadline_working_days <= 2,
        link: '/prebilling',
      });
    }
    return out.sort((a, b) => a.date.localeCompare(b.date));
  }, [deadlines.data, objections.data, t]);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-h1 text-ink">{t('nav.calendar')}</h1>
        <p className="mt-1 label-micro">{t('calendar.lead')}</p>
      </div>

      {error ? (
        <ErrorState
          detail={error}
          onRetry={() => {
            deadlines.retry();
            objections.retry();
          }}
        />
      ) : loading ? (
        <div className="fill-dots-faint h-40 animate-pulse" />
      ) : items.length === 0 ? (
        <EmptyState messageKey="common.no_data" />
      ) : (
        <div className="border border-ink/15">
          {items.map((it, i) => {
            const row = (
              <div
                className={clsx(
                  'flex items-baseline gap-4 px-4 py-3',
                  i < items.length - 1 && 'border-b border-ink/[.08]',
                )}
              >
                <span
                  className={clsx(
                    'w-24 shrink-0 font-mono text-secondary tabular-nums',
                    it.critical ? 'text-critical' : 'text-ink/70',
                  )}
                >
                  {fmtDate(it.date)}
                </span>
                <div className="min-w-0 flex-1">
                  <p className="text-secondary text-ink/80">{it.title}</p>
                  <p className="mt-0.5 label-micro">{it.caption}</p>
                </div>
                {it.link ? (
                  <span aria-hidden className="text-accent">
                    →
                  </span>
                ) : null}
              </div>
            );
            return it.link ? (
              <Link
                key={it.key}
                href={it.link}
                className="block transition-colors duration-150 hover:bg-ink/[.03]"
              >
                {row}
              </Link>
            ) : (
              <div key={it.key}>{row}</div>
            );
          })}
        </div>
      )}
    </div>
  );
}
