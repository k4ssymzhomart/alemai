'use client';

import { useState } from 'react';

/**
 * Swappable logo slot (docs/15 §8): shows the wordmark IGERIM▮ (Unbounded
 * 800, tight tracking, terminal block as mark) until /brand/logo.svg loads —
 * a hidden probe <img> flips the state, so a missing file never flashes a
 * broken-image icon. Uploads are grayscale-forced to stay monochrome.
 * Dropping a file into frontend/public/brand/logo.svg swaps it, zero code.
 */
export default function Logo({ height = 28 }: { height?: number }) {
  const [fileExists, setFileExists] = useState(false);

  return (
    <>
      {/* eslint-disable-next-line @next/next/no-img-element -- local swappable asset, no optimizer */}
      <img
        src="/brand/logo.svg"
        alt="IGERIM"
        style={
          fileExists
            ? { height, filter: 'grayscale(1) contrast(9)' }
            : { display: 'none' }
        }
        onLoad={() => setFileExists(true)}
      />
      {!fileExists ? (
        <span
          className="font-display font-extrabold uppercase leading-none tracking-tight text-ink"
          style={{ fontSize: height * 0.72 }}
        >
          IGERIM<span aria-hidden>▮</span>
        </span>
      ) : null}
    </>
  );
}
