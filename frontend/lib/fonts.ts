/**
 * QALAM applied type stack (Epic A.2, stack 2 — lead's gate pick):
 *   display — Manrope (headings, verdicts, sentence-case)
 *   ui/body — Inter
 *   mono    — IBM Plex Mono (ALL numbers, ₸, dates, timers, codes)
 * Swapping the display face is a one-line change here. The kk glyph gate
 * (/design) is the blocking check that Ә Ғ Қ Ң Ө Ұ Ү Һ І render without a
 * fallback weight/width jump; if Manrope misbehaves, fall back to stack 3
 * (PT Serif + Golos Text).
 */
import { IBM_Plex_Mono, Inter, Manrope } from 'next/font/google';

export const fontDisplay = Manrope({
  subsets: ['latin', 'cyrillic'],
  weight: ['500', '600', '700'],
  variable: '--font-display',
  display: 'swap',
});

export const fontUi = Inter({
  subsets: ['latin', 'cyrillic', 'cyrillic-ext'],
  weight: ['400', '500'],
  variable: '--font-ui',
  display: 'swap',
});

export const fontMono = IBM_Plex_Mono({
  subsets: ['latin', 'cyrillic', 'cyrillic-ext'],
  weight: ['400', '600'],
  variable: '--font-mono',
  display: 'swap',
});

export const fontClassNames = `${fontDisplay.variable} ${fontUi.variable} ${fontMono.variable}`;
