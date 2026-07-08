'use client';

/**
 * Typed fetch hooks for the metrics API (plain useState/useEffect — no
 * react-query). Each hook returns { data, loading, error, retry }.
 *
 * NEXT_PUBLIC_API_MOCK=1 switches to deterministic fixtures from lib/mock.ts
 * (demo contingency, docs/08 §7) — the value is inlined at build time.
 */

import { useCallback, useEffect, useState } from 'react';

import api from '@/lib/api';
import { mockLineMonthly, mockLines, mockOverview } from '@/lib/mock';
import type {
  LineMonthlyResponse,
  LinesQuery,
  LinesResponse,
  OverviewMetrics,
} from '@/lib/types';

export const API_MOCK = process.env.NEXT_PUBLIC_API_MOCK === '1';

export interface FetchState<T> {
  data: T | null;
  loading: boolean;
  /** Technical detail for the error card; user-facing copy comes from i18n. */
  error: string | null;
  retry: () => void;
}

function useFetch<T>(fetcher: (signal: AbortSignal) => Promise<T>): FetchState<T> {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const controller = new AbortController();
    let alive = true;
    setLoading(true);
    setError(null);
    fetcher(controller.signal)
      .then((result) => {
        if (!alive) return;
        setData(result);
        setLoading(false);
      })
      .catch((err: unknown) => {
        if (!alive || controller.signal.aborted) return;
        setError(err instanceof Error ? err.message : String(err));
        setLoading(false);
      });
    return () => {
      alive = false;
      controller.abort();
    };
  }, [fetcher, attempt]);

  const retry = useCallback(() => setAttempt((n) => n + 1), []);

  return { data, loading, error, retry };
}

/** GET /metrics/overview?year= */
export function useOverview(year: number): FetchState<OverviewMetrics> {
  const fetcher = useCallback(
    (signal: AbortSignal) =>
      API_MOCK
        ? mockOverview(year)
        : api.get<OverviewMetrics>('/metrics/overview', {
            params: { year },
            signal,
          }),
    [year],
  );
  return useFetch(fetcher);
}

/** GET /metrics/lines?year=&funding_source=&care_type=&contract_id= */
export function useLines(query: LinesQuery): FetchState<LinesResponse> {
  const { year, funding_source, care_type, contract_id } = query;
  const fetcher = useCallback(
    (signal: AbortSignal) =>
      API_MOCK
        ? mockLines({ year, funding_source, care_type, contract_id })
        : api.get<LinesResponse>('/metrics/lines', {
            params: { year, funding_source, care_type, contract_id },
            signal,
          }),
    [year, funding_source, care_type, contract_id],
  );
  return useFetch(fetcher);
}

/** GET /metrics/line/{line_key}/monthly?year= — line_key is URL-encoded here. */
export function useLineMonthly(
  lineKey: string,
  year: number,
): FetchState<LineMonthlyResponse> {
  const fetcher = useCallback(
    (signal: AbortSignal) =>
      API_MOCK
        ? mockLineMonthly(lineKey, year)
        : api.get<LineMonthlyResponse>(
            `/metrics/line/${encodeURIComponent(lineKey)}/monthly`,
            { params: { year }, signal },
          ),
    [lineKey, year],
  );
  return useFetch(fetcher);
}
