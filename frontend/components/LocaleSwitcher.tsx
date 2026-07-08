'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import { locales, type Locale } from '@/lib/i18n';

const LABELS: Record<Locale, string> = {
  kk: 'ҚАЗ',
  ru: 'РУС',
  en: 'ENG',
};

/** Locale switcher: segmented mono control, active segment inverted. */
export default function LocaleSwitcher() {
  const { t, i18n } = useTranslation();
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
      aria-label={t('common.language_label')}
      className="flex border border-ink"
    >
      {locales.map((locale) => (
        <button
          key={locale}
          type="button"
          onClick={() => handleChange(locale)}
          aria-pressed={current === locale}
          className={clsx(
            'hover-stamp flex-1 px-2 py-1 font-mono text-xs font-semibold',
            current === locale
              ? 'bg-ink text-paper'
              : 'bg-paper text-ink hover:bg-ink hover:text-paper',
          )}
        >
          {LABELS[locale]}
        </button>
      ))}
    </div>
  );
}
