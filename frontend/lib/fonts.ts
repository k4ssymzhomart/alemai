/**
 * QALAM applied type stack (Epic A.2, candidate 1 — «премиальный годовой
 * отчёт»): editorial serif display + neutral sans body + mono figures.
 *   display — Literata (headings, verdicts, sentence-case)
 *   ui/body — Inter
 *   mono    — IBM Plex Mono (ALL numbers, ₸, dates, timers, codes)
 * Swapping the stack the lead picks at the gate is a one-line change here.
 * The kk glyph gate (/design) is the blocking check that Ә Ғ Қ Ң Ө Ұ Ү Һ І
 * render without a fallback weight/width jump.
 */
import { IBM_Plex_Mono, Inter, Literata } from 'next/font/google';

export const fontDisplay = Literata({
  subsets: ['latin', 'cyrillic', 'cyrillic-ext'],
  weight: ['500', '600'],
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
