'use client';

/** CodeChip (docs/15 §5): ЕКД/rule codes in a mono bordered chip: 5.1, R17. */
export default function CodeChip({ code }: { code: string }) {
  return (
    <span className="inline-flex border border-ink bg-paper px-1.5 py-0.5 font-mono text-xs font-semibold text-ink">
      {code}
    </span>
  );
}
