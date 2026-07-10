'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useEffect, useState, type ReactNode } from 'react';
import clsx from 'clsx';
import {
  Activity,
  BookText,
  CalendarDays,
  ChevronsLeft,
  ChevronsRight,
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
import NotificationBell from '@/components/NotificationBell';
import ProviderBadge from '@/components/ProviderBadge';
import ShareButton from '@/components/ShareButton';
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
  { href: '/regs', labelKey: 'nav.regs', icon: BookText },
  { href: '/reports', labelKey: 'nav.reports', icon: FileText },
  // /city stays killed (docs/25 H2 fill-or-kill) — tracked as a roadmap issue.
  { href: '/imports', labelKey: 'nav.imports', icon: FileUp },
  { href: '/admin', labelKey: 'nav.admin', icon: Settings },
];

/**
 * QALAM shell (Epic A.2): quiet header [Logo · org · wire · role · lang] over
 * a hairline-ruled sidebar and an air-rich, max-width document body. Active
 * nav = 2px left rule + medium weight, no black band. All chrome print-hidden.
 */
const SIDEBAR_KEY = 'qalam.sidebar.collapsed';

export default function AppShell({ children }: { children: ReactNode }) {
  const { t } = useTranslation();
  const pathname = usePathname();
  const { role, nav } = useSession();
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    setCollapsed(localStorage.getItem(SIDEBAR_KEY) === '1');
  }, []);

  const toggleSidebar = () =>
    setCollapsed((c) => {
      const next = !c;
      localStorage.setItem(SIDEBAR_KEY, next ? '1' : '0');
      return next;
    });

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
        <ProviderBadge />
        <Ticker />
        <div className="flex shrink-0 items-center gap-2">
          <ShareButton />
          <NotificationBell />
          <UserMenu />
          <LocaleSwitcher />
        </div>
      </header>

      <div className="flex min-h-0 flex-1">
        <aside
          className={clsx(
            'print-hidden sticky top-0 flex h-screen shrink-0 flex-col border-r border-ink/15 bg-paper transition-[width] duration-[160ms] ease-out motion-reduce:transition-none',
            collapsed ? 'w-14' : 'w-56',
          )}
        >
          <nav className="flex-1 overflow-y-auto py-3">
            {visibleNav.map((item) => {
              const active =
                pathname === item.href || pathname.startsWith(`${item.href}/`);
              const Icon = item.icon;
              const label = t(item.labelKey);
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? 'page' : undefined}
                  title={collapsed ? label : undefined}
                  className={clsx(
                    'flex items-center border-l-2 py-2 text-secondary transition-colors duration-150',
                    collapsed ? 'justify-center px-0' : 'gap-2.5 px-5',
                    active
                      ? 'border-accent font-medium text-accent'
                      : 'border-transparent text-ink/60 hover:bg-ink/[.03] hover:text-ink',
                  )}
                >
                  <Icon className="h-4 w-4 shrink-0" strokeWidth={1.75} aria-hidden />
                  {collapsed ? null : <span className="truncate">{label}</span>}
                </Link>
              );
            })}
          </nav>

          <button
            type="button"
            onClick={toggleSidebar}
            aria-label={t(collapsed ? 'nav.expand' : 'nav.collapse')}
            title={t(collapsed ? 'nav.expand' : 'nav.collapse')}
            className={clsx(
              'flex items-center border-t border-ink/15 py-2.5 text-ink/50 transition-colors duration-150 hover:bg-ink/[.03] hover:text-ink',
              collapsed ? 'justify-center px-0' : 'gap-2.5 px-5',
            )}
          >
            {collapsed ? (
              <ChevronsRight className="h-4 w-4 shrink-0" strokeWidth={1.75} aria-hidden />
            ) : (
              <ChevronsLeft className="h-4 w-4 shrink-0" strokeWidth={1.75} aria-hidden />
            )}
            {collapsed ? null : <span className="label-micro">{t('nav.collapse')}</span>}
          </button>

          {collapsed ? null : (
            <p className="border-t border-ink/15 px-5 py-3 text-secondary text-ink/40">
              {t('app.tagline')}
            </p>
          )}
        </aside>

        <div className="flex min-w-0 flex-1 flex-col">
          <main className="mx-auto w-full max-w-content flex-1 px-8 py-8">
            {children}
          </main>
        </div>
      </div>
    </div>
  );
}
