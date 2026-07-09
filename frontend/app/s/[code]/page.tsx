'use client';

import { useEffect, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { useTranslation } from 'react-i18next';

import Logo from '@/components/brand/Logo';
import api from '@/lib/api';
import { LOCALE_STORAGE_KEY } from '@/lib/i18n';

interface ShareState {
  code: string;
  url_state: { path?: string; query?: string; locale?: string };
}

/**
 * Share-link resolver (EPIC H3): /s/<code> → look up the saved route+state →
 * redirect there. The opener sees the same screen through THEIR own permissions
 * (a curator lands on the aggregate view of the same context). If not logged
 * in, the target's guard sends them through /login first.
 */
export default function ShareResolverPage() {
  const { t, i18n } = useTranslation();
  const router = useRouter();
  const params = useParams<{ code: string }>();
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    const code = params?.code;
    if (!code) return;
    let alive = true;
    api
      .get<ShareState>(`/share/${code}`)
      .then((s) => {
        if (!alive) return;
        const { path = '/overview', query = '', locale } = s.url_state ?? {};
        if (locale && (locale === 'kk' || locale === 'ru' || locale === 'en')) {
          window.localStorage.setItem(LOCALE_STORAGE_KEY, locale);
          void i18n.changeLanguage(locale);
        }
        router.replace(`${path}${query || ''}`);
      })
      .catch(() => alive && setFailed(true));
    return () => {
      alive = false;
    };
  }, [params, router, i18n]);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-3 bg-paper">
      <Logo height={28} />
      <p className="label-micro">
        {failed ? t('share.not_found') : t('share.opening')}
      </p>
    </div>
  );
}
