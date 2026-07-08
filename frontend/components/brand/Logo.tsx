'use client';

import { useEffect, useRef, useState } from 'react';

/**
 * Swappable logo slot (docs/15 §8, renamed Epic A.2): shows the wordmark
 * «Qalam» (lowercase, Literata display, sentence case, thin rule under) until
 * /brand/logo.svg loads. A hidden probe <img> flips the state, re-checked on
 * mount so a cached drop-in never misses; uploads are grayscale-forced.
 * Dropping a file into frontend/public/brand/logo.svg swaps it, zero code.
 */
export default function Logo({ height = 22 }: { height?: number }) {
  const [fileExists, setFileExists] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = imgRef.current;
    if (img?.complete && img.naturalWidth > 0) setFileExists(true);
  }, []);

  return (
    <>
      {/* eslint-disable-next-line @next/next/no-img-element -- local swappable asset, no optimizer */}
      <img
        ref={imgRef}
        src="/brand/logo.svg"
        alt="Qalam"
        style={
          fileExists
            ? { height, filter: 'grayscale(1) contrast(9)' }
            : { display: 'none' }
        }
        onLoad={() => setFileExists(true)}
      />
      {!fileExists ? (
        <span
          className="font-display leading-none text-ink"
          style={{ fontSize: height, fontWeight: 600 }}
        >
          Qalam
        </span>
      ) : null}
    </>
  );
}
