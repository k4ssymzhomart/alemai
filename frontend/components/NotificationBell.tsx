'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Bell } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import { useEvents } from '@/components/EventsProvider';
import type { EventItem } from '@/lib/types';

/** Severity glyph — B&W, no color (docs/15 §4). */
const GLYPH: Record<string, string> = { critical: '▲', warn: '!', info: '·' };

function eventTime(ts: string): string {
  const d = new Date(ts);
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

/**
 * Notifications bell (EPIC G3, «қоңырау») — unread badge + dropdown of the last
 * 20 events. Same feed as the ticker, but this is the actionable inbox: each row
 * links to its entity; «Барлығын оқылды» advances the read cursor.
 */
export default function NotificationBell() {
  const { t, i18n } = useTranslation();
  const { events, unread, markAllRead } = useEvents();
  const [open, setOpen] = useState(false);
  const kk = (i18n.resolvedLanguage ?? 'kk') === 'kk';

  const title = (e: EventItem) => (kk ? e.title_kk : e.title_ru);

  return (
    <div className="relative">
      <button
        type="button"
        aria-label={t('notifications.title')}
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className="relative flex h-8 w-8 items-center justify-center border border-ink/15 text-ink/70 transition-colors duration-150 hover:bg-ink/[.03] hover:text-ink"
      >
        <Bell className="h-4 w-4" strokeWidth={1.75} aria-hidden />
        {unread > 0 ? (
          <span className="absolute -right-1.5 -top-1.5 flex h-4 min-w-[16px] items-center justify-center bg-ink px-1 font-mono text-[10px] leading-none text-paper tabular-nums">
            {unread > 99 ? '99+' : unread}
          </span>
        ) : null}
      </button>

      {open ? (
        <>
          <div
            className="fixed inset-0 z-40"
            aria-hidden
            onClick={() => setOpen(false)}
          />
          <div className="absolute right-0 top-full z-50 mt-2 w-96 border border-ink bg-paper shadow-[4px_4px_0_0_var(--ink)]">
            <div className="flex items-center justify-between border-b border-ink/15 px-4 py-2.5">
              <span className="label-micro">{t('notifications.title')}</span>
              {events.length > 0 ? (
                <button
                  type="button"
                  onClick={() => markAllRead()}
                  className="label-micro text-ink/60 transition-colors duration-150 hover:text-ink"
                >
                  {t('notifications.mark_read')}
                </button>
              ) : null}
            </div>

            <div className="max-h-96 overflow-y-auto">
              {events.length === 0 ? (
                <p className="px-4 py-6 text-center text-secondary text-ink/50">
                  {t('notifications.empty')}
                </p>
              ) : (
                events.map((e) => {
                  const row = (
                    <div className="flex gap-3 px-4 py-2.5">
                      <span
                        className="mt-0.5 w-3 shrink-0 text-center font-mono text-ink"
                        aria-hidden
                      >
                        {GLYPH[e.severity] ?? '·'}
                      </span>
                      <div className="min-w-0 flex-1">
                        <p className="text-secondary text-ink/80">{title(e)}</p>
                        <p className="mt-0.5 flex items-center gap-2 label-micro">
                          <span>{e.actor}</span>
                          <span aria-hidden className="text-ink/20">
                            ·
                          </span>
                          <span className="font-mono">{eventTime(e.ts)}</span>
                        </p>
                      </div>
                    </div>
                  );
                  return e.link ? (
                    <Link
                      key={e.id}
                      href={e.link}
                      onClick={() => setOpen(false)}
                      className="block border-b border-ink/[.06] transition-colors duration-150 last:border-0 hover:bg-ink/[.03]"
                    >
                      {row}
                    </Link>
                  ) : (
                    <div key={e.id} className="border-b border-ink/[.06] last:border-0">
                      {row}
                    </div>
                  );
                })
              )}
            </div>
          </div>
        </>
      ) : null}
    </div>
  );
}
