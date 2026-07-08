'use client';

/**
 * StampMark (Epic A.2): small rotated stamp, ink-60, ONLY on rejected claims
 * and the pre-billing verdict corner — nowhere else. «Төлемнен алынды · код
 * 5.1»; caller passes the already-localized text.
 */
export default function StampMark({ text }: { text: string }) {
  return (
    <span
      className="inline-block -rotate-[7deg] border border-ink/60 px-1.5 py-0.5 font-mono text-micro uppercase tracking-wider text-ink/60"
      aria-label={text}
    >
      {text}
    </span>
  );
}
