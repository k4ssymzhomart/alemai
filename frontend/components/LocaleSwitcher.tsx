'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import { locales, type Locale } from '@/lib/i18n';

const LABELS: Record<Locale, string> = {
  kk: 'ҚАЗ',
  ru: 'РУС',
  en: 'ENG',
};

/** Locale switcher stub: in-memory language change, no persistence yet. */
export default function LocaleSwitcher() {
  const { i18n } = useTranslation();
  const current = (i18n.resolvedLanguage ?? i18n.language) as Locale;

  const handleChange = (locale: Locale) => {
    void i18n.changeLanguage(locale);
    if (typeof document !== 'undefined') {
      document.documentElement.lang = locale;
    }
  };

  return (
    <div
      role="group"
      aria-label="Language"
      className="flex rounded-md border border-slate-200 bg-slate-50 p-0.5"
    >
      {locales.map((locale) => (
        <button
          key={locale}
          type="button"
          onClick={() => handleChange(locale)}
          aria-pressed={current === locale}
          className={clsx(
            'flex-1 rounded px-2 py-1 text-xs font-semibold transition-colors',
            current === locale
              ? 'bg-accent text-white shadow-sm'
              : 'text-slate-500 hover:text-slate-900',
          )}
        >
          {LABELS[locale]}
        </button>
      ))}
    </div>
  );
}
