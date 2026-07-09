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
  FileUp,
  LayoutDashboard,
  MessageSquare,
  Scale,
  Settings,
  ShieldAlert,
  type LucideIcon,
} from 'lucide-react';
import { useTranslation } from 'react-i18next';

import LocaleSwitcher from '@/components/LocaleSwitcher';
import UserMenu from '@/components/UserMenu';
import { useSession } from '@/components/SessionProvider';
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
  { href: '/imports', labelKey: 'nav.imports', icon: FileUp },
  { href: '/admin', labelKey: 'nav.admin', icon: Settings },
];

/**
 * QALAM shell (Epic A.2): quiet header [Logo · org · wire · role · lang] over
 * a hairline-ruled sidebar and an air-rich, max-width document body. Active
 * nav = 2px left rule + medium weight, no black band. All chrome print-hidden.
 */
export default function AppShell({ children }: { children: ReactNode }) {
  const { t } = useTranslation();
  const pathname = usePathname();
  const { role, nav } = useSession();

  // The login screen renders without the shell (no sidebar/header).
  if (pathname === '/login') {
    return <>{children}</>;
  }

  const scopeKey = role === 'curator' ? 'app.scope_city' : 'app.org';
  const visibleNav = NAV_ITEMS.filter((item) => nav.includes(item.href));

  return (
    <div className="flex min-h-screen flex-col">
      <header className="print-hidden flex items-center gap-4 border-b border-ink/15 bg-paper px-6 py-3">
        <Link href="/overview" className="flex shrink-0 items-center">
          <Logo height={22} />
        </Link>
        <span className="hidden shrink-0 label-micro md:inline-block">
          {t(scopeKey)}
        </span>
        <Ticker />
        <div className="flex shrink-0 items-center gap-2">
          <UserMenu />
          <LocaleSwitcher />
        </div>
      </header>

      <div className="flex min-h-0 flex-1">
        <aside className="print-hidden sticky top-0 flex h-screen w-56 shrink-0 flex-col border-r border-ink/15 bg-paper">
          <nav className="flex-1 overflow-y-auto py-3">
            {visibleNav.map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(`${item.href}/`);
              const Icon = item.icon;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? 'page' : undefined}
                  className={clsx(
                    'flex items-center gap-2.5 border-l-2 px-5 py-2 text-secondary transition-colors duration-150',
                    active
                      ? 'border-ink font-medium text-ink'
                      : 'border-transparent text-ink/60 hover:bg-ink/[.03] hover:text-ink',
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" strokeWidth={1.75} aria-hidden />
                  {t(item.labelKey)}
                </Link>
              );
            })}
          </nav>
          <p className="border-t border-ink/15 px-5 py-3 text-secondary text-ink/40">
            {t('app.tagline')}
          </p>
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <main className="mx-auto w-full max-w-content flex-1 px-8 py-8">
            {children}
          </main>
          {/* NOT print-hidden: printed output must carry the demo-data label. */}
          <footer className="flex items-center gap-2 border-t border-ink/15 px-8 py-3">
            <span className="label-micro border border-ink/40 px-1.5 py-0.5 text-ink/60">
              {t('common.demo_badge')}
            </span>
            <span className="text-secondary text-ink/40">
              {t('common.demo_data_note')}
            </span>
          </footer>
        </div>
      </div>
    </div>
  );
}
