'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import type { ReactNode } from 'react';
import clsx from 'clsx';
import {
  Activity,
  Building2,
  CalendarDays,
  ClipboardCheck,
  FileText,
  LayoutDashboard,
  MessageSquare,
  Scale,
  Settings,
  ShieldAlert,
  type LucideIcon,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';

import LocaleSwitcher from '@/components/LocaleSwitcher';
import RoleSwitcher from '@/components/RoleSwitcher';
import Ticker from '@/components/Ticker';
import Logo from '@/components/brand/Logo';

interface NavItem {
  href: string;
  labelKey: string;
  icon: LucideIcon;
}

/** The 10 screens (docs/04 §2). */
const NAV_ITEMS: NavItem[] = [
  { href: '/overview', labelKey: 'nav.overview', icon: LayoutDashboard },
  { href: '/risks', labelKey: 'nav.risks', icon: ShieldAlert },
  { href: '/prebilling', labelKey: 'nav.prebilling', icon: ClipboardCheck },
  { href: '/reconcile', labelKey: 'nav.reconcile', icon: Scale },
  { href: '/anomalies', labelKey: 'nav.anomalies', icon: Activity },
  { href: '/calendar', labelKey: 'nav.calendar', icon: CalendarDays },
  { href: '/copilot', labelKey: 'nav.copilot', icon: MessageSquare },
  { href: '/reports', labelKey: 'nav.reports', icon: FileText },
  { href: '/city', labelKey: 'nav.city', icon: Building2 },
  { href: '/admin', labelKey: 'nav.admin', icon: Settings },
];

/**
 * «Ведомость» shell (docs/15 §8): header [Logo · org · ticker · role · lang]
 * over a bordered sidebar + document body. All chrome is print-hidden.
 */
export default function AppShell({ children }: { children: ReactNode }) {
  const { t } = useTranslation();
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen flex-col">
      <header className="print-hidden flex items-center gap-3 border-b-2 border-ink bg-paper px-4 py-2">
        <Link href="/overview" className="flex shrink-0 items-center">
          <Logo height={28} />
        </Link>
        <span className="hidden shrink-0 border border-ink px-2 py-1 font-mono text-caption uppercase md:inline-block">
          {t('app.org')}
        </span>
        <Ticker />
        <div className="flex shrink-0 items-center gap-2">
          <RoleSwitcher />
          <LocaleSwitcher />
        </div>
      </header>

      <div className="flex min-h-0 flex-1">
        <aside className="print-hidden sticky top-0 flex h-screen w-56 shrink-0 flex-col border-r-2 border-ink bg-paper">
          <nav className="flex-1 overflow-y-auto py-2">
            {NAV_ITEMS.map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(`${item.href}/`);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? 'page' : undefined}
                  className={clsx(
                    'hover-stamp flex items-center gap-2.5 border-b border-ink/[.12] px-4 py-2.5 text-sm font-medium uppercase tracking-wide',
                    active
                      ? 'bg-ink text-paper'
                      : 'text-ink hover:bg-ink hover:text-paper',
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" strokeWidth={2.25} aria-hidden />
                  {t(item.labelKey)}
                </Link>
              );
            })}
          </nav>
          <p className="border-t-2 border-ink px-4 py-3 text-caption uppercase text-ink/40">
            {t('app.tagline')}
          </p>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <main className="flex-1 px-8 py-6">{children}</main>
          <footer className="print-hidden flex items-center gap-2 border-t-2 border-ink px-8 py-2.5">
            <span className="bg-ink px-1.5 py-0.5 font-mono text-caption uppercase text-paper">
              {t('common.demo_badge')}
            </span>
            <span className="text-caption uppercase text-ink/40">
              {t('common.demo_data_note')}
            </span>
          </footer>
        </div>
      </div>
    </div>
  );
}
