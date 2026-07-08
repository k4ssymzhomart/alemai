/**
 * «Ведомость» type stack (docs/15 §2), self-hosted at build via next/font:
 *   display  — Unbounded (page titles, verdicts, hero labels)
 *   ui/body  — Inter Tight
 *   mono     — IBM Plex Mono (ALL numbers, ₸, dates, timers, codes)
 * cyrillic-ext is the kk glyph carrier — the /design glyph gate (15 §2) is
 * the blocking check that Ә Ғ Қ Ң Ө Ұ Ү Һ І render in every face.
 */
import { IBM_Plex_Mono, Inter_Tight, Unbounded } from 'next/font/google';

export const fontDisplay = Unbounded({
  subsets: ['latin', 'cyrillic', 'cyrillic-ext'],
  weight: ['500', '800'],
  variable: '--font-display',
  display: 'swap',
});

export const fontUi = Inter_Tight({
  subsets: ['latin', 'cyrillic', 'cyrillic-ext'],
  weight: ['400', '500', '700'],
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
