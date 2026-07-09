import type { Metadata } from 'next';
import type { ReactNode } from 'react';

import AppShell from '@/components/AppShell';
import { EventsProvider } from '@/components/EventsProvider';
import I18nProvider from '@/components/I18nProvider';
import { SessionProvider } from '@/components/SessionProvider';
import { fontClassNames } from '@/lib/fonts';

import './globals.css';

export const metadata: Metadata = {
  title: 'Qalam',
  description:
    'Шартты игерудің қаржылық автопилоты — clinic-side control loop for ГОБМП/ОСМС contracts.',
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="ru" className={fontClassNames}>
      <body>
        <I18nProvider>
          <SessionProvider>
            <EventsProvider>
              <AppShell>{children}</AppShell>
            </EventsProvider>
          </SessionProvider>
        </I18nProvider>
      </body>
    </html>
  );
}
