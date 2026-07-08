'use client';

/**
 * ExecutionBar (Epic C · F5): one glance = ahead or behind.
 *   track  — 6px, ink/10 background = the full annual plan
 *   fill   — solid ink = fact YTD
 *   marker — 1px ink vertical tick = «сегодня должно быть» (YTD-expected plan)
 *   dots   — hatch extension fact→forecast when a year-end forecast exists
 */
export default function ExecutionBar({
  planYear,
  factYtd,
  planYtd,
  forecastYear,
}: {
  planYear: number;
  factYtd: number;
  planYtd?: number;
  forecastYear?: number | null;
}) {
  if (planYear <= 0) return null;
  const clamp = (x: number) => Math.max(0, Math.min(100, x));
  const factPct = clamp((factYtd / planYear) * 100);
  const forecastPct =
    forecastYear != null ? clamp((forecastYear / planYear) * 100) : null;
  const tickPct = planYtd != null ? clamp((planYtd / planYear) * 100) : null;

  return (
    <div className="relative h-1.5 w-full min-w-24 bg-ink/10">
      {/* dotted extension fact → forecast */}
      {forecastPct != null && forecastPct > factPct ? (
        <div
          className="fill-hatch absolute inset-y-0"
          style={{ left: `${factPct}%`, width: `${forecastPct - factPct}%` }}
          aria-hidden
        />
      ) : null}
      {/* solid fact segment */}
      <div
        className="absolute inset-y-0 left-0 bg-ink"
        style={{ width: `${factPct}%` }}
        aria-hidden
      />
      {/* YTD-expected marker */}
      {tickPct != null ? (
        <div
          className="absolute -inset-y-1 w-px bg-ink"
          style={{ left: `${tickPct}%` }}
          aria-hidden
        />
      ) : null}
    </div>
  );
}
