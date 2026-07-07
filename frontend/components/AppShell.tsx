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

export default function AppShell({ children }: { children: ReactNode }) {
  const { t } = useTranslation();
  const pathname = usePathname();

  return (
    <div className="flex min-h-screen">
      <aside className="sticky top-0 flex h-screen w-60 shrink-0 flex-col border-r border-slate-200 bg-white">
        <div className="border-b border-slate-200 px-4 py-5">
          <Link href="/overview" className="block">
            <span className="text-xl font-bold uppercase tracking-widest text-accent">
              {t('app.title')}
            </span>
          </Link>
          <p className="mt-1 text-xs leading-snug text-slate-500">
            {t('app.tagline')}
          </p>
        </div>

        <nav className="flex-1 space-y-0.5 overflow-y-auto px-2 py-3">
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
                  'flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors',
                  active
                    ? 'bg-accent-50 text-accent-700'
                    : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900',
                )}
              >
                <Icon
                  className={clsx(
                    'h-4 w-4 shrink-0',
                    active ? 'text-accent-600' : 'text-slate-400',
                  )}
                  aria-hidden
                />
                {t(item.labelKey)}
              </Link>
            );
          })}
        </nav>

        <div className="space-y-2 border-t border-slate-200 px-3 py-3">
          <RoleSwitcher />
          <LocaleSwitcher />
        </div>
      </aside>

      <div className="flex min-w-0 flex-1 flex-col">
        <main className="flex-1 px-8 py-6">{children}</main>
        <footer className="border-t border-slate-200 px-8 py-3 text-xs text-slate-400">
          {t('common.demo_data_note')}
        </footer>
      </div>
    </div>
  );
}
