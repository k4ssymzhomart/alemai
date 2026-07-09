'use client';

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';

import { useSession } from '@/components/SessionProvider';
import api from '@/lib/api';
import { RefreshContext } from '@/lib/refresh';
import type { EventItem, EventsResponse } from '@/lib/types';

const POLL_MS = 4000;

interface EventsCtx {
  events: EventItem[];
  unread: number;
  markAllRead: () => Promise<void>;
}

const Ctx = createContext<EventsCtx | null>(null);

/**
 * Realtime feed (EPIC G2/G3). Polls GET /events every 4s while authenticated;
 * when the newest event id changes, bumps the refresh epoch (→ all screens
 * refetch) and updates the notification bell. Cross-session: one window's action
 * lands in another window within ≤5s.
 */
export function EventsProvider({ children }: { children: ReactNode }) {
  const { me } = useSession();
  const [events, setEvents] = useState<EventItem[]>([]);
  const [unread, setUnread] = useState(0);
  const [epoch, setEpoch] = useState(0);
  const newestRef = useRef<string | null>(null);

  const poll = useCallback(async () => {
    try {
      const data = await api.get<EventsResponse>('/events', { params: { limit: 20 } });
      const newest = data.items[0]?.id ?? null;
      if (newest !== newestRef.current) {
        newestRef.current = newest;
        setEpoch((n) => n + 1); // new event → invalidate every screen's cache
      }
      setEvents(data.items);
      setUnread(data.unread);
    } catch {
      /* transient (offline / not yet authed) — next tick retries */
    }
  }, []);

  useEffect(() => {
    if (!me) {
      setEvents([]);
      setUnread(0);
      newestRef.current = null;
      return;
    }
    void poll();
    const id = window.setInterval(() => void poll(), POLL_MS);
    return () => window.clearInterval(id);
  }, [me, poll]);

  const markAllRead = useCallback(async () => {
    try {
      await api.post('/events/read');
      setUnread(0);
    } catch {
      /* ignore */
    }
  }, []);

  const value = useMemo<EventsCtx>(
    () => ({ events, unread, markAllRead }),
    [events, unread, markAllRead],
  );

  return (
    <Ctx.Provider value={value}>
      <RefreshContext.Provider value={epoch}>{children}</RefreshContext.Provider>
    </Ctx.Provider>
  );
}

export function useEvents(): EventsCtx {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error('useEvents must be used within EventsProvider');
  return ctx;
}
