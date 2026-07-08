'use client';

/** CodeChip (Epic A.2): ЕКД/rule codes in a hairline mono chip: 5.1, R17. */
export default function CodeChip({ code }: { code: string }) {
  return (
    <span className="inline-flex border border-ink/40 bg-paper px-1.5 py-0.5 font-mono text-micro text-ink">
      {code}
    </span>
  );
}
