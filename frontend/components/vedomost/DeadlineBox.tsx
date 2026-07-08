'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

/** Parse "YYYY-MM-DD" as a LOCAL date — new Date(iso) would read it as UTC
 *  midnight and shift the deadline a day early for viewers west of UTC. */
export function parseLocalDate(iso: string): Date {
  const [y, m, d] = iso.split('-').map(Number);
  return new Date(y, (m || 1) - 1, d || 1);
}

/**
 * Working days remaining in [today, deadline] inclusive, Mon–Fri: the
 * deadline day itself is still actionable, so on that day the box reads
 * «остался 1 раб. день», and «мерзім өтті» appears only once it has passed.
 * KZ public holidays are NOT subtracted yet — Epic C wires the holiday
 * calendar when the DF-track lands; until then this errs on the safe
 * (earlier-alarm) side.
 */
export function workingDaysUntil(deadline: Date, from: Date = new Date()): number {
  const day = new Date(from.getFullYear(), from.getMonth(), from.getDate());
  const end = new Date(
    deadline.getFullYear(),
    deadline.getMonth(),
    deadline.getDate(),
  );
  let count = 0;
  while (day <= end) {
    const dow = day.getDay();
    if (dow !== 0 && dow !== 6) count += 1;
    day.setDate(day.getDate() + 1);
  }
  return count;
}

/**
 * DeadlineBox (docs/15 §5): mono countdown in a bordered box with a legal
 * citation caption («п. 26 Правил мониторинга»). ≤2 working days → the box
 * inverts to a solid black block — the loudest thing on a B&W screen.
 */
export default function DeadlineBox({
  deadline,
  citation,
  label,
}: {
  /** ISO date, e.g. "2026-07-13". */
  deadline: string;
  /** Legal basis caption, already localized/cited by the caller. */
  citation: string;
  /** What the deadline is for (already localized). */
  label?: string;
}) {
  const { t } = useTranslation();
  const days = workingDaysUntil(parseLocalDate(deadline));
  const critical = days <= 2;

  return (
    <div
      className={clsx(
        'inline-block border-2 border-ink px-3 py-2',
        critical ? 'bg-ink text-paper' : 'bg-paper text-ink',
      )}
    >
      {label ? (
        <p className="text-caption font-medium uppercase opacity-70">{label}</p>
      ) : null}
      <p className="font-mono text-xl font-semibold tabular-nums">
        {days > 0
          ? t('deadline.days_left', { count: days })
          : t('deadline.expired')}
      </p>
      <p className="font-mono text-caption uppercase opacity-70">{citation}</p>
    </div>
  );
}
