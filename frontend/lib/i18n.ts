import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

import kk from '@/locales/kk.json';
import ru from '@/locales/ru.json';
import en from '@/locales/en.json';

export const locales = ['kk', 'ru', 'en'] as const;
export type Locale = (typeof locales)[number];

// Rebrand v3 (docs/25 H1): Russian is the base language on load. kk + en stay
// switchable; the copilot beat is still performed in kk, glossary + all kk
// strings unchanged.
export const defaultLocale: Locale = 'ru';
export const fallbackLocale: Locale = 'ru';
export const LOCALE_STORAGE_KEY = 'qalam.lng';

/** RU default on first visit, but a user's switch persists across reloads. */
function initialLocale(): Locale {
  if (typeof window !== 'undefined') {
    const saved = window.localStorage.getItem(LOCALE_STORAGE_KEY);
    if (saved === 'kk' || saved === 'ru' || saved === 'en') return saved;
  }
  return defaultLocale;
}

/**
 * i18next singleton (docs/04 §5): resources bundled from locales/*.json.
 * Russian is the default UI language (rebrand v3); a persisted kk/en choice
 * wins over it. Initialized synchronously (inline resources, no async
 * backends) so the same instance works during SSR prerender and the browser.
 */
if (!i18n.isInitialized) {
  void i18n.use(initReactI18next).init({
    resources: {
      kk: { translation: kk },
      ru: { translation: ru },
      en: { translation: en },
    },
    lng: initialLocale(),
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
