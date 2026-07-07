'use client';

import { Inbox } from 'lucide-react';
import { useTranslation } from 'react-i18next';

export default function EmptyState() {
  const { t } = useTranslation();

  return (
    <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed border-slate-300 bg-white px-6 py-16 text-center">
      <Inbox className="h-8 w-8 text-slate-300" aria-hidden />
      <p className="text-sm text-slate-500">{t('common.empty')}</p>
    </div>
  );
}
