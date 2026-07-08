'use client';

/**
 * StampMark (docs/15 §5): rotated double-border stamp — «СНЯТО С ОПЛАТЫ ·
 * КОД 5.1» / «ТӨЛЕМНЕН АЛЫНДЫ». Black only; the caller passes the (already
 * localized) text. Applied to rejected claims and pre-billing block rows.
 */
export default function StampMark({ text }: { text: string }) {
  return (
    <span
      className="inline-block -rotate-[8deg] border-2 border-ink p-0.5 opacity-70"
      aria-label={text}
    >
      <span className="block border border-ink px-2 py-0.5 font-mono text-xs font-semibold uppercase tracking-widest text-ink">
        {text}
      </span>
    </span>
  );
}
