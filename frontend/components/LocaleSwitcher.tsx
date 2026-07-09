'use client';

import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import { LOCALE_STORAGE_KEY, locales, type Locale } from '@/lib/i18n';

const LABELS: Record<Locale, string> = {
  kk: 'ҚАЗ',
  ru: 'РУС',
  en: 'ENG',
};

/** Locale switcher (Epic A.2): quiet segmented control, active = subtle fill. */
export default function LocaleSwitcher() {
  const { t, i18n } = useTranslation();
  const current = (i18n.resolvedLanguage ?? i18n.language) as Locale;

  const handleChange = (locale: Locale) => {
    void i18n.changeLanguage(locale);
    if (typeof window !== 'undefined') {
      window.localStorage.setItem(LOCALE_STORAGE_KEY, locale); // persist choice over RU default
    }
    if (typeof document !== 'undefined') {
      document.documentElement.lang = locale;
    }
  };

  return (
    <div
      role="group"
      aria-label={t('common.language_label')}
      className="flex border border-ink/15"
    >
      {locales.map((locale) => (
        <button
          key={locale}
          type="button"
          onClick={() => handleChange(locale)}
          aria-pressed={current === locale}
          className={clsx(
            'px-2 py-1 font-mono text-micro transition-colors duration-150',
            current === locale
              ? 'bg-ink text-paper'
              : 'text-ink/60 hover:bg-ink/[.03] hover:text-ink',
          )}
        >
          {LABELS[locale]}
        </button>
      ))}
    </div>
  );
}
