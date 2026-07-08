'use client';

/**
 * ExecutionBar / HatchBar (docs/15 §4): the plan/fact/forecast bar.
 * Filled black = fact, hatched = forecast (P6, optional), dotted = remainder,
 * plan-to-date mark = 2px vertical tick. All values in ₸ against planYear.
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
    <div className="relative h-3 w-full min-w-24 border border-ink bg-paper">
      {/* dotted remainder underlay */}
      <div className="fill-dots-faint absolute inset-0" aria-hidden />
      {/* hatched forecast segment (behind fact) */}
      {forecastPct != null && forecastPct > factPct ? (
        <div
          className="fill-hatch absolute inset-y-0 left-0"
          style={{ width: `${forecastPct}%` }}
          aria-hidden
        />
      ) : null}
      {/* solid fact segment */}
      <div
        className="absolute inset-y-0 left-0 bg-ink"
        style={{ width: `${factPct}%` }}
        aria-hidden
      />
      {/* plan-to-date tick */}
      {tickPct != null ? (
        <div
          className="absolute -inset-y-0.5 w-0.5 bg-ink"
          style={{ left: `${tickPct}%` }}
          aria-hidden
        />
      ) : null}
    </div>
  );
}
