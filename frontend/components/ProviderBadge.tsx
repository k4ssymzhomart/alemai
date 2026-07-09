'use client';

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import api from '@/lib/api';

interface ProviderStatus {
  url: string;
  reachable: boolean;
  in_registry: boolean;
  checked_at: string;
}

const REGISTRY_URL = 'https://fms.ecc.kz/ru/fsms/healthcare_subjects';

/**
 * ФСМС provider-registry badge (docs/25 H0.4). Live-checks fms.ecc.kz; when the
 * org is confirmed in the registry it shows a green ✓, otherwise it degrades to
 * a plain quick-link (venue-offline law). Always links to the registry.
 */
export default function ProviderBadge() {
  const { t } = useTranslation();
  const [status, setStatus] = useState<ProviderStatus | null>(null);

  useEffect(() => {
    let alive = true;
    api
      .get<ProviderStatus>('/radar/provider-status')
      .then((s) => alive && setStatus(s))
      .catch(() => alive && setStatus(null));
    return () => {
      alive = false;
    };
  }, []);

  const confirmed = Boolean(status?.reachable && status?.in_registry);

  return (
    <a
      href={status?.url ?? REGISTRY_URL}
      target="_blank"
      rel="noopener noreferrer"
      title={t('app.fsms_registry')}
      className={`hidden shrink-0 items-center gap-1 label-micro md:inline-flex ${
        confirmed ? 'text-ok' : 'text-ink/50'
      } transition-colors duration-150 hover:text-accent`}
    >
      <span aria-hidden className="font-mono">
        {confirmed ? '✓' : '↗'}
      </span>
      {t('app.fsms_registry')}
    </a>
  );
}
