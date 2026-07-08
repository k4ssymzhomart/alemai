import type { Config } from 'tailwindcss';

/**
 * Design system «Ведомость» (docs/15): #000/#FFF ONLY. The full default
 * Tailwind palette is REPLACED (not extended) so a color violation is a
 * class that does not exist — impossible, not just forbidden. Optical grays
 * are black at fixed opacities via the `ink/NN` opacity modifier.
 * border-radius is 0 everywhere: `rounded-none` is the only rounded-* class.
 */
const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    colors: {
      transparent: 'transparent',
      current: 'currentColor',
      inherit: 'inherit',
      ink: '#000000',
      paper: '#ffffff',
    },
    borderRadius: {
      none: '0',
    },
    boxShadow: {
      // Offset block shadows, no blur (docs/15 §3) — the only shadows allowed.
      hard: '4px 4px 0 0 #000000',
      'hard-sm': '2px 2px 0 0 #000000',
      none: 'none',
    },
    extend: {
      fontFamily: {
        display: ['var(--font-display)', 'var(--font-ui)', 'system-ui', 'sans-serif'],
        ui: ['var(--font-ui)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'JetBrains Mono', 'monospace'],
      },
      fontSize: {
        // Type scale px (docs/15 §2): 64/40/28/20/16/14/12.
        hero: ['64px', { lineHeight: '1.05', fontWeight: '600' }],
        verdict: ['40px', { lineHeight: '1.1' }],
        h1: ['28px', { lineHeight: '1.2' }],
        h2: ['20px', { lineHeight: '1.3' }],
        caption: ['12px', { lineHeight: '1.3', letterSpacing: '0.08em' }],
      },
    },
  },
  plugins: [],
};

export default config;
