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
import { useRefreshEpoch } from '@/lib/refresh';
import { mockLineMonthly, mockLines, mockOverview } from '@/lib/mock';
import type {
  AnomaliesResponse,
  DeadlinesResponse,
  LineMonthlyResponse,
  LinesQuery,
  LinesResponse,
  OpsDashboard,
  OverviewMetrics,
  PrebillingResult,
  ReconcileBuckets,
  ReconcileRows,
  RuleRunResult,
  RunFindings,
  ObjectionsResult,
} from '@/lib/types';

export const API_MOCK = process.env.NEXT_PUBLIC_API_MOCK === '1';

export interface FetchState<T> {
  data: T | null;
  loading: boolean;
  /** Technical detail for the error card; user-facing copy comes from i18n. */
  error: string | null;
  retry: () => void;
}

function useFetch<T>(
  fetcher: (signal: AbortSignal) => Promise<T>,
  opts: { live?: boolean } = {},
): FetchState<T> {
  const { live = true } = opts;
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  // Events-driven revalidation (G2): a bump re-runs this effect so the screen
  // reflects another session's mutation within one poll cycle. Hooks whose
  // fetcher MUTATES (usePrebilling POSTs /rules/run) opt out with live:false —
  // otherwise the run emits an event that bumps the epoch that re-runs the
  // fetcher → a self-sustaining loop (adversarial-review CRITICAL).
  const liveEpoch = useRefreshEpoch();
  const epoch = live ? liveEpoch : 0;

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
  }, [fetcher, attempt, epoch]);

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

// ─── Epic C: pre-billing / reconcile / objections ──────────────────────────

/**
 * Pre-billing check: POST a rules run over the scope, then GET its findings.
 * Chained in one fetcher so the screen binds to a single { run, findings }.
 */
export function usePrebilling(scope: string): FetchState<PrebillingResult> {
  const fetcher = useCallback(
    async (signal: AbortSignal): Promise<PrebillingResult> => {
      const run = await api.post<RuleRunResult>(
        '/rules/run',
        { scope },
        { signal },
      );
      const findings = await api.get<RunFindings>(
        `/rules/runs/${run.run_id}/findings`,
        { params: { group_by: 'rule' }, signal },
      );
      return { run, findings };
    },
    [scope],
  );
  // live:false — the fetcher POSTs a rules run (mutation); must NOT re-run on
  // the event epoch or it self-triggers every poll cycle.
  return useFetch(fetcher, { live: false });
}

/** GET /reconcile/buckets?year= */
export function useReconcile(year: number): FetchState<ReconcileBuckets> {
  const fetcher = useCallback(
    (signal: AbortSignal) =>
      api.get<ReconcileBuckets>('/reconcile/buckets', {
        params: { year },
        signal,
      }),
    [year],
  );
  return useFetch(fetcher);
}

/** GET /objections — the DF-track defect list with working-day deadlines. */
export function useObjections(): FetchState<ObjectionsResult> {
  const fetcher = useCallback(
    (signal: AbortSignal) => api.get<ObjectionsResult>('/objections', { signal }),
    [],
  );
  return useFetch(fetcher);
}

/** GET /ops/dashboard — live ops counters; auto-revalidates on the event epoch. */
export function useOps(): FetchState<OpsDashboard> {
  const fetcher = useCallback(
    (signal: AbortSignal) => api.get<OpsDashboard>('/ops/dashboard', { signal }),
    [],
  );
  return useFetch(fetcher);
}

/** GET /reconcile/bucket/{n}/rows — drill-down rows for one bucket. */
export function useReconcileRows(
  bucketNo: number,
  year: number,
  enabled: boolean,
): FetchState<ReconcileRows> {
  const fetcher = useCallback(
    (signal: AbortSignal) =>
      enabled
        ? api.get<ReconcileRows>(`/reconcile/bucket/${bucketNo}/rows`, {
            params: { year, limit: 20 },
            signal,
          })
        : Promise.resolve({ bucket_no: bucketNo, rows: [] }),
    [bucketNo, year, enabled],
  );
  return useFetch(fetcher);
}

/** GET /deadlines — the seeded regulatory deadline calendar (H2 Календарь). */
export function useDeadlines(): FetchState<DeadlinesResponse> {
  const fetcher = useCallback(
    (signal: AbortSignal) => api.get<DeadlinesResponse>('/deadlines', { signal }),
    [],
  );
  return useFetch(fetcher);
}

/** GET /anomalies — doctor-workload outliers from claims (H2 Аномалии). */
export function useAnomalies(): FetchState<AnomaliesResponse> {
  const fetcher = useCallback(
    (signal: AbortSignal) => api.get<AnomaliesResponse>('/anomalies', { signal }),
    [],
  );
  return useFetch(fetcher);
}
