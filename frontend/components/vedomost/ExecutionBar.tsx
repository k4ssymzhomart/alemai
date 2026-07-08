'use client';

/**
 * ExecutionBar (Epic A.2): a thin plan/fact/forecast bar. Solid ink = fact
 * (data mark), hairline forecast segment, faint remainder, plan-to-date mark
 * = 2px ink tick. Kept slim so 11 stacked rows stay calm, not heavy.
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
    <div className="relative h-1.5 w-full min-w-24 border border-ink/25 bg-paper">
      {forecastPct != null && forecastPct > factPct ? (
        <div
          className="fill-hatch absolute inset-y-0 left-0"
          style={{ width: `${forecastPct}%` }}
          aria-hidden
        />
      ) : null}
      <div
        className="absolute inset-y-0 left-0 bg-ink"
        style={{ width: `${factPct}%` }}
        aria-hidden
      />
      {tickPct != null ? (
        <div
          className="absolute -inset-y-1 w-0.5 bg-ink"
          style={{ left: `${tickPct}%` }}
          aria-hidden
        />
      ) : null}
    </div>
  );
}
