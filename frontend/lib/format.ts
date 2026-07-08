/**
 * Pure number/date formatters (docs/04 §2: `12 480 500 ₸` — space thousands,
 * ₸ after; comma decimals for kk/ru; dates `07.07.2026`).
 *
 * Grouping is done manually with non-breaking spaces — NOT via Intl locale
 * grouping — so the output is byte-identical across browsers/Node versions.
 * All functions are pure; keep them that way.
 */

export type NumLocale = 'kk' | 'ru' | 'en';

/** Non-breaking space: used as the thousands separator and before ₸/%. */
const NBSP = '\u00a0';

function groupDigits(digits: string): string {
  return digits.replace(/\B(?=(\d{3})+(?!\d))/g, NBSP);
}

function decimalSep(locale: NumLocale): string {
  return locale === 'en' ? '.' : ',';
}

/** 12480500 → "12 480 500 ₸" (rounded to integer ₸). */
export function fmtTenge(n: number): string {
  const rounded = Math.round(n);
  const sign = rounded < 0 ? '−' : '';
  return `${sign}${groupDigits(String(Math.abs(rounded)))}${NBSP}₸`;
}

/** 20955 → "20 955" (integer, space thousands, no unit). */
export function fmtNumber(n: number): string {
  const rounded = Math.round(n);
  const sign = rounded < 0 ? '−' : '';
  return `${sign}${groupDigits(String(Math.abs(rounded)))}`;
}

/** 61.38 → "61,4 %" for kk/ru, "61.4 %" for en (always 1 decimal). */
export function fmtPct(x: number, locale: NumLocale = 'kk'): string {
  const rounded = Math.round(x * 10) / 10;
  const sign = rounded < 0 ? '−' : '';
  const abs = Math.abs(rounded);
  const intPart = Math.trunc(abs);
  const frac = Math.round((abs - intPart) * 10);
  return `${sign}${groupDigits(String(intPart))}${decimalSep(locale)}${frac}${NBSP}%`;
}

/** "2026-03" → "03.2026". Unparseable input is returned as-is. */
export function fmtPeriod(period: string): string {
  const [year, month] = period.split('-');
  if (!year || !month) return period;
  return `${month}.${year}`;
}

/** "2026-10-14" → "14.10.2026" (docs/04 §5 date style). */
export function fmtDate(isoDate: string): string {
  const [year, month, day] = isoDate.split('-');
  if (!year || !month || !day) return isoDate;
  return `${day}.${month}.${year}`;
}

const COMPACT_UNITS: Record<NumLocale, { bn: string; mn: string; k: string }> = {
  kk: { bn: 'млрд', mn: 'млн', k: 'мың' },
  ru: { bn: 'млрд', mn: 'млн', k: 'тыс.' },
  en: { bn: 'bn', mn: 'mn', k: 'k' },
};

/**
 * Compact ₸ for chart ticks: 5_200_000_000 → "5,2 млрд ₸" (kk/ru).
 * One decimal max; trailing ",0" is dropped ("500 млн ₸", not "500,0 млн ₸").
 */
export function fmtTengeCompact(n: number, locale: NumLocale = 'kk'): string {
  const sign = n < 0 ? '−' : '';
  const abs = Math.abs(n);
  const units = COMPACT_UNITS[locale];

  const withUnit = (value: number, unit: string): string => {
    const rounded = Math.round(value * 10) / 10;
    const intPart = Math.trunc(rounded);
    const frac = Math.round((rounded - intPart) * 10);
    const num =
      frac === 0 ? String(intPart) : `${intPart}${decimalSep(locale)}${frac}`;
    return `${sign}${num}${NBSP}${unit}${NBSP}₸`;
  };

  if (abs >= 1e9) return withUnit(abs / 1e9, units.bn);
  if (abs >= 1e6) return withUnit(abs / 1e6, units.mn);
  if (abs >= 1e3) return withUnit(abs / 1e3, units.k);
  return `${sign}${Math.round(abs)}${NBSP}₸`;
}
