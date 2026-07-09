'use client';

import { useState } from 'react';
import { Share2 } from 'lucide-react';
import { useTranslation } from 'react-i18next';

import api from '@/lib/api';

interface ShareResp {
  code: string;
}

/**
 * «Поделиться» (EPIC H3): mints a share code for the current route+state and
 * copies https://<host>/s/<code> to the clipboard, with a violet toast. Combined
 * with the realtime event feed this is the collaborative «смотрим на одно и то же».
 */
export default function ShareButton() {
  const { t, i18n } = useTranslation();
  const [busy, setBusy] = useState(false);
  const [toast, setToast] = useState(false);

  const share = async () => {
    if (busy) return;
    setBusy(true);
    try {
      const resp = await api.post<ShareResp>('/share', {
        url_state: {
          path: window.location.pathname,
          query: window.location.search,
          locale: i18n.resolvedLanguage ?? 'ru',
        },
      });
      const url = `${window.location.origin}/s/${resp.code}`;
      try {
        await navigator.clipboard.writeText(url);
      } catch {
        window.prompt(t('share.copy_manual'), url);
      }
      setToast(true);
      window.setTimeout(() => setToast(false), 2200);
    } catch {
      /* offline — no unhandled rejection */
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={share}
        disabled={busy}
        aria-label={t('share.button')}
        title={t('share.button')}
        className="flex h-8 w-8 items-center justify-center border border-ink/15 text-ink/70 transition-colors duration-150 hover:border-accent hover:text-accent disabled:opacity-40"
      >
        <Share2 className="h-4 w-4" strokeWidth={1.75} aria-hidden />
      </button>
      {toast ? (
        <span className="absolute right-0 top-full z-50 mt-2 whitespace-nowrap bg-accent px-2 py-1 text-micro text-paper">
          {t('share.copied')}
        </span>
      ) : null}
    </div>
  );
}
