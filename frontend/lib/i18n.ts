import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import kk from '@/locales/kk.json';
import ru from '@/locales/ru.json';
import en from '@/locales/en.json';

export const locales = ['kk', 'ru', 'en'] as const;
export type Locale = (typeof locales)[number];

export const defaultLocale: Locale = 'kk';
export const fallbackLocale: Locale = 'ru';

/**
 * i18next singleton (docs/04 §5): resources bundled from locales/*.json,
 * Kazakh is the default UI language, Russian the fallback.
 * Initialized synchronously (inline resources, no async backends) so the
 * same instance works during SSR prerender and in the browser.
 */
if (!i18n.isInitialized) {
  void i18n.use(initReactI18next).init({
    resources: {
      kk: { translation: kk },
      ru: { translation: ru },
      en: { translation: en },
    },
    lng: defaultLocale,
    fallbackLng: fallbackLocale,
    supportedLngs: [...locales],
    initImmediate: false,
    interpolation: {
      // React already escapes rendered strings.
      escapeValue: false,
    },
    react: {
      useSuspense: false,
    },
  });
}

export default i18n;
