import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import AppShell from '@/components/AppShell';
import I18nProvider from '@/components/I18nProvider';
import { fontClassNames } from '@/lib/fonts';

import './globals.css';

export const metadata: Metadata = {
  title: 'IGERIM',
  description:
    'Шартты игерудің қаржылық автопилоты — clinic-side control loop for ГОБМП/ОСМС contracts.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="kk" className={fontClassNames}>
      <body>
        <I18nProvider>
          <AppShell>{children}</AppShell>
        </I18nProvider>
      </body>
    </html>
  );
}
