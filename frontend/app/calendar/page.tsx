'use client';

import { useMemo, useState } from 'react';
import Link from 'next/link';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import ErrorState from '@/components/ErrorState';
import { fmtDate } from '@/lib/format';
import { useDeadlines, useObjections } from '@/lib/hooks';

type EventKind = 'objection' | 'window' | 'report';

interface CalEvent {
  key: string;
  /** ISO YYYY-MM-DD — the day the chip sits on. */
  date: string;
  kind: EventKind;
  title: string;
  caption: string;
  critical?: boolean;
  link?: string;
  linkLabel?: string;
  note?: string | null;
}

interface WindowRange {
  key: string;
  start: string;
  end: string;
  title: string;
  note: string | null;
  link?: string;
  linkLabel?: string;
}

// ── date helpers (UTC-based so grid math is timezone-independent) ────────────
function pad(n: number): string {
  return String(n).padStart(2, '0');
}
function iso(y: number, m0: number, d: number): string {
  return `${y}-${pad(m0 + 1)}-${pad(d)}`;
}
function daysInMonth(y: number, m0: number): number {
  return new Date(Date.UTC(y, m0 + 1, 0)).getUTCDate();
}
/** Mon-first weekday index (0=Mon … 6=Sun) of the 1st of the month. */
function firstWeekdayMon(y: number, m0: number): number {
  return (new Date(Date.UTC(y, m0, 1)).getUTCDay() + 6) % 7;
}
function addDays(isoDate: string, n: number): string {
  const [y, m, d] = isoDate.split('-').map(Number);
  const t = new Date(Date.UTC(y, m - 1, d + n));
  return iso(t.getUTCFullYear(), t.getUTCMonth(), t.getUTCDate());
}
function daysBetween(a: string, b: string): number {
  const [ay, am, ad] = a.split('-').map(Number);
  const [by, bm, bd] = b.split('-').map(Number);
  return Math.round(
    (Date.UTC(by, bm - 1, bd) - Date.UTC(ay, am - 1, ad)) / 86_400_000,
  );
}

const KIND_DOT: Record<EventKind, string> = {
  objection: 'bg-critical',
  window: 'bg-warn',
  report: 'bg-accent',
};
const KIND_TEXT: Record<EventKind, string> = {
  objection: 'text-critical',
  window: 'text-warn',
  report: 'text-accent',
};

/**
 * Screen — Календарь (H2 fill-or-kill): a real month grid where every
 * regulatory deadline (/deadlines) and live возражение timer (/objections)
 * is placed on its day. Hover a chip for a summary; click a day to open the
 * detail panel with the next-step CTA (возражение → Проверка, окно → Сверка).
 * "Today" is anchored to the demo clock (/objections demo_today).
 */
export default function CalendarPage() {
  const { t } = useTranslation();
  const deadlines = useDeadlines();
  const objections = useObjections();
  const loading = deadlines.loading || objections.loading;
  const error = deadlines.error ?? objections.error;

  const monthsObj = t('calendar.months', { returnObjects: true }) as Record<string, string>;
  const weekdaysObj = t('calendar.weekdays', { returnObjects: true }) as Record<string, string>;
  const months = Array.from({ length: 12 }, (_, i) => monthsObj[String(i + 1)]);
  const weekdays = Array.from({ length: 7 }, (_, i) => weekdaysObj[String(i + 1)]);

  // Demo "today" comes from the objection clock; fall back to the real date.
  const today = objections.data?.demo_today ?? iso(
    new Date().getFullYear(),
    new Date().getMonth(),
    new Date().getDate(),
  );
  const [ty, tm] = [Number(today.slice(0, 4)), Number(today.slice(5, 7)) - 1];

  const [view, setView] = useState<{ y: number; m: number }>({ y: ty, m: tm });
  const [selected, setSelected] = useState<string | null>(today);

  // ── build events ──────────────────────────────────────────────────────────
  const { pointByDate, windows, upcoming } = useMemo(() => {
    const pts: CalEvent[] = [];
    const wins: WindowRange[] = [];

    for (const d of deadlines.data?.deadlines ?? []) {
      const isWindow = d.kind === 'korrektirovka_window' && d.starts !== d.ends;
      if (isWindow) {
        wins.push({
          key: `w-${d.id}`,
          start: d.starts,
          end: d.ends,
          title: d.note ?? t(`calendar.kind.${d.kind}`, { defaultValue: d.kind }),
          note: d.note,
          link: '/reconcile',
          linkLabel: t('calendar.go_reconcile'),
        });
      } else {
        pts.push({
          key: `d-${d.id}`,
          date: d.ends,
          kind: d.kind === 'korrektirovka_window' ? 'window' : 'report',
          title: d.note ?? t(`calendar.kind.${d.kind}`, { defaultValue: d.kind }),
          caption: t(`calendar.kind.${d.kind}`, { defaultValue: d.kind }),
          note: d.note,
        });
      }
    }

    for (const o of objections.data?.items ?? []) {
      pts.push({
        key: `o-${o.case_ref}`,
        date: o.deadline_date,
        kind: 'objection',
        title: t('calendar.objection', { code: o.ekd_code }),
        caption: t('calendar.days_left', { count: o.deadline_working_days }),
        critical: o.deadline_working_days <= 2,
        link: '/prebilling',
        linkLabel: t('calendar.go_prebilling'),
        note: o.ekd_name_ru,
      });
    }

    const pointByDate = new Map<string, CalEvent[]>();
    for (const e of pts) {
      const arr = pointByDate.get(e.date) ?? [];
      arr.push(e);
      pointByDate.set(e.date, arr);
    }

    // upcoming rail: point events + window starts, on/after today, soonest first
    const upcomingRaw: CalEvent[] = [
      ...pts.filter((e) => e.date >= today),
      ...wins
        .filter((w) => w.end >= today)
        .map<CalEvent>((w) => ({
          key: `wu-${w.key}`,
          date: w.start >= today ? w.start : today,
          kind: 'window',
          title: w.title,
          caption: t('calendar.window_active', { date: fmtDate(w.end) }),
          link: w.link,
          linkLabel: w.linkLabel,
          note: w.note,
        })),
    ]
      .sort((a, b) => a.date.localeCompare(b.date))
      .slice(0, 6);

    return { pointByDate, windows: wins, upcoming: upcomingRaw };
  }, [deadlines.data, objections.data, today, t]);

  // events for a specific day = point events on it + any window covering it
  function eventsForDay(dayIso: string): CalEvent[] {
    const out = [...(pointByDate.get(dayIso) ?? [])];
    for (const w of windows) {
      if (dayIso >= w.start && dayIso <= w.end) {
        out.push({
          key: `${w.key}-${dayIso}`,
          date: dayIso,
          kind: 'window',
          title: w.title,
          caption: t('calendar.window_active', { date: fmtDate(w.end) }),
          link: w.link,
          linkLabel: w.linkLabel,
          note: w.note,
        });
      }
    }
    return out;
  }

  // ── grid cells for the viewed month ─────────────────────────────────────────
  const cells = useMemo(() => {
    const lead = firstWeekdayMon(view.y, view.m);
    const total = daysInMonth(view.y, view.m);
    const out: ({ day: number; date: string } | null)[] = [];
    for (let i = 0; i < lead; i++) out.push(null);
    for (let d = 1; d <= total; d++) out.push({ day: d, date: iso(view.y, view.m, d) });
    while (out.length % 7 !== 0) out.push(null);
    return out;
  }, [view]);

  function shiftMonth(delta: number): void {
    setView((v) => {
      const m = v.m + delta;
      return { y: v.y + Math.floor(m / 12), m: ((m % 12) + 12) % 12 };
    });
  }
  function goToday(): void {
    setView({ y: ty, m: tm });
    setSelected(today);
  }

  const selectedEvents = selected ? eventsForDay(selected) : [];

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
        <div className="fill-dots-faint h-96 animate-pulse" />
      ) : (
        <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_20rem]">
          {/* ── month grid ─────────────────────────────────────────────── */}
          <div className="min-w-0">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <button
                  type="button"
                  aria-label={t('calendar.prev')}
                  onClick={() => shiftMonth(-1)}
                  className="border border-ink/20 px-2.5 py-1 text-ink transition-colors duration-150 hover:bg-ink/[.04]"
                >
                  ‹
                </button>
                <h2 className="min-w-[10rem] text-center font-display text-h3 text-ink">
                  {months[view.m]} {view.y}
                </h2>
                <button
                  type="button"
                  aria-label={t('calendar.next')}
                  onClick={() => shiftMonth(1)}
                  className="border border-ink/20 px-2.5 py-1 text-ink transition-colors duration-150 hover:bg-ink/[.04]"
                >
                  ›
                </button>
              </div>
              <button
                type="button"
                onClick={goToday}
                className="border border-accent px-3 py-1 text-secondary font-medium text-accent transition-colors duration-150 hover:bg-accent/[.06]"
              >
                {t('calendar.today')}
              </button>
            </div>

            <div className="grid grid-cols-7 border-l border-t border-ink/15">
              {weekdays.map((w, i) => (
                <div
                  key={i}
                  className="border-b border-r border-ink/15 bg-ink/[.02] px-2 py-1.5 text-center label-micro"
                >
                  {w}
                </div>
              ))}
              {cells.map((cell, i) => {
                if (!cell) {
                  return (
                    <div
                      key={`b-${i}`}
                      className="min-h-[5.5rem] border-b border-r border-ink/15 bg-ink/[.015]"
                    />
                  );
                }
                const evs = eventsForDay(cell.date);
                const isToday = cell.date === today;
                const isSelected = cell.date === selected;
                const shown = evs.slice(0, 2);
                const extra = evs.length - shown.length;
                return (
                  <button
                    type="button"
                    key={cell.date}
                    onClick={() => setSelected(cell.date)}
                    className={clsx(
                      'min-h-[5.5rem] border-b border-r border-ink/15 px-1.5 py-1 text-left align-top transition-colors duration-150 hover:bg-ink/[.03]',
                      isSelected && 'bg-accent/[.06] ring-1 ring-inset ring-accent',
                    )}
                  >
                    <div className="flex items-center justify-between">
                      <span
                        className={clsx(
                          'font-mono text-micro tabular-nums',
                          isToday
                            ? 'inline-flex h-5 min-w-5 items-center justify-center bg-accent px-1 text-paper'
                            : 'text-ink/60',
                        )}
                      >
                        {cell.day}
                      </span>
                      {evs.length > 0 ? (
                        <span className="flex gap-0.5">
                          {evs.slice(0, 4).map((e) => (
                            <span
                              key={e.key}
                              className={clsx('h-1.5 w-1.5', KIND_DOT[e.kind])}
                            />
                          ))}
                        </span>
                      ) : null}
                    </div>
                    <div className="mt-1 space-y-0.5">
                      {shown.map((e) => (
                        <span
                          key={e.key}
                          title={`${e.title} — ${e.caption}`}
                          className={clsx(
                            'block truncate border-l-2 pl-1 text-micro leading-tight',
                            e.critical
                              ? 'border-critical text-critical'
                              : e.kind === 'window'
                                ? 'border-warn text-ink/70'
                                : e.kind === 'objection'
                                  ? 'border-critical text-ink/70'
                                  : 'border-accent text-ink/70',
                          )}
                        >
                          {e.title}
                        </span>
                      ))}
                      {extra > 0 ? (
                        <span className="block pl-1 text-micro text-ink/45">
                          {t('calendar.more', { count: extra })}
                        </span>
                      ) : null}
                    </div>
                  </button>
                );
              })}
            </div>

            {/* legend */}
            <div className="mt-3 flex flex-wrap items-center gap-x-5 gap-y-1.5 label-micro">
              <span className="text-ink/40">{t('calendar.legend_title')}:</span>
              {(['objection', 'window', 'report'] as EventKind[]).map((k) => (
                <span key={k} className="flex items-center gap-1.5">
                  <span className={clsx('h-2 w-2', KIND_DOT[k])} />
                  {t(`calendar.legend.${k}`)}
                </span>
              ))}
            </div>
          </div>

          {/* ── side rail: selected day + upcoming ──────────────────────── */}
          <div className="min-w-0 space-y-6">
            <section className="border border-ink/15">
              <div className="border-b border-ink/15 bg-ink/[.02] px-4 py-2.5">
                <p className="text-secondary font-medium text-ink">
                  {selected
                    ? t('calendar.selected', { date: fmtDate(selected) })
                    : t('calendar.pick_day')}
                </p>
              </div>
              <div className="divide-y divide-ink/[.08]">
                {selected && selectedEvents.length === 0 ? (
                  <p className="px-4 py-4 text-secondary text-ink/50">
                    {t('calendar.empty_day')}
                  </p>
                ) : (
                  selectedEvents.map((e) => (
                    <DetailRow key={e.key} ev={e} />
                  ))
                )}
              </div>
            </section>

            <section className="border border-ink/15">
              <div className="border-b border-ink/15 bg-ink/[.02] px-4 py-2.5">
                <p className="text-secondary font-medium text-ink">
                  {t('calendar.upcoming')}
                </p>
              </div>
              <div className="divide-y divide-ink/[.08]">
                {upcoming.length === 0 ? (
                  <p className="px-4 py-4 text-secondary text-ink/50">
                    {t('common.no_data')}
                  </p>
                ) : (
                  upcoming.map((e) => {
                    const d = daysBetween(today, e.date);
                    return (
                      <button
                        type="button"
                        key={e.key}
                        onClick={() => {
                          setView({ y: Number(e.date.slice(0, 4)), m: Number(e.date.slice(5, 7)) - 1 });
                          setSelected(e.date);
                        }}
                        className="flex w-full items-baseline gap-3 px-4 py-2.5 text-left transition-colors duration-150 hover:bg-ink/[.03]"
                      >
                        <span className={clsx('mt-1.5 h-1.5 w-1.5 shrink-0', KIND_DOT[e.kind])} />
                        <span className="min-w-0 flex-1">
                          <span className="block truncate text-secondary text-ink/80">
                            {e.title}
                          </span>
                          <span className="label-micro">
                            {fmtDate(e.date)} ·{' '}
                            {d <= 0
                              ? t('calendar.today_badge')
                              : t('calendar.in_days', { count: d })}
                          </span>
                        </span>
                      </button>
                    );
                  })
                )}
              </div>
            </section>
          </div>
        </div>
      )}
    </div>
  );
}

function DetailRow({ ev }: { ev: CalEvent }) {
  return (
    <div className="px-4 py-3">
      <div className="flex items-baseline gap-2">
        <span className={clsx('shrink-0 text-micro', KIND_TEXT[ev.kind])}>●</span>
        <div className="min-w-0 flex-1">
          <p className="text-secondary text-ink/90">{ev.title}</p>
          <p className="mt-0.5 label-micro">{ev.caption}</p>
          {ev.note && ev.note !== ev.title ? (
            <p className="mt-1 text-micro text-ink/50">{ev.note}</p>
          ) : null}
          {ev.link ? (
            <Link
              href={ev.link}
              className="mt-2 inline-block text-secondary font-medium text-accent transition-colors duration-150 hover:underline"
            >
              {ev.linkLabel}
            </Link>
          ) : null}
        </div>
      </div>
    </div>
  );
}
