'use client';

import { useEffect, useRef, useState } from 'react';

/**
 * Brand logo slot (rebrand v3, docs/25 H1): renders the real Qalam logo from
 * /brand/logo.png (in colour — the violet mark is the brand now), with the
 * wordmark «Qalam» as fallback until it loads. A hidden probe <img> flips the
 * state, re-checked on mount so a cached drop-in never misses.
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
      {/* eslint-disable-next-line @next/next/no-img-element -- local brand asset, no optimizer */}
      <img
        ref={imgRef}
        src="/brand/logo.png"
        alt="Qalam"
        style={fileExists ? { height } : { display: 'none' }}
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
