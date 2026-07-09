import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import AppShell from '@/components/AppShell';
import I18nProvider from '@/components/I18nProvider';
import { RoleProvider } from '@/components/RoleProvider';
import { fontClassNames } from '@/lib/fonts';

import './globals.css';

export const metadata: Metadata = {
  title: 'Qalam',
  description:
    'Шартты игерудің қаржылық автопилоты — clinic-side control loop for ГОБМП/ОСМС contracts.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="kk" className={fontClassNames}>
      <body>
        <I18nProvider>
          <RoleProvider>
            <AppShell>{children}</AppShell>
          </RoleProvider>
        </I18nProvider>
      </body>
    </html>
  );
}
