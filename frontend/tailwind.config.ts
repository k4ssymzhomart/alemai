import type { Config } from 'tailwindcss';

/**
 * QALAM design system (Epic A.2 — «премиальный годовой отчёт»). Still strict
 * monochrome: the full default Tailwind palette is REPLACED so a color
 * violation is a class that does not exist. Optical grays are black at fixed
 * opacities via the `ink/NN` modifier. border-radius stays 0.
 *
 * Weight diet vs the old «ведомость»: no 4px bars, no offset hard shadows,
 * hairline default rules, ONE black element per screen. Hierarchy comes from
 * the serif/sans/mono type roles and whitespace, not from mass.
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
      // Rebrand v3 (docs/25 H1): violet accent + semantic G/Y/R status colors.
      // Accent = CTA / active nav / links / focus / selected / small chart
      // accents ONLY — never backgrounds, statuses, or decorative floods.
      accent: '#5200E0',
      // Status colors carry meaning (color is now the primary severity signal;
      // hatch/glyph stay secondary). In print they degrade to ink via the
      // Tailwind `print:` variant on each usage (keeps the ч/б story honest).
      ok: '#12B76A',
      warn: '#F79009',
      critical: '#D92D20',
    },
    borderRadius: {
      none: '0',
    },
    boxShadow: {
      // Depth, when truly needed, is a single hairline drop — never an offset block.
      soft: '0 1px 0 rgba(0,0,0,0.1)',
      none: 'none',
    },
    extend: {
      fontFamily: {
        display: ['var(--font-display)', 'Georgia', 'serif'],
        ui: ['var(--font-ui)', 'system-ui', 'sans-serif'],
        mono: ['var(--font-mono)', 'JetBrains Mono', 'monospace'],
      },
      fontSize: {
        // Premium diet (Epic A.2): replaces the old 64/40 scale.
        micro: ['11px', { lineHeight: '1.3', letterSpacing: '0.08em' }],
        secondary: ['13px', { lineHeight: '1.4' }],
        body: ['15px', { lineHeight: '1.6' }],
        h3: ['18px', { lineHeight: '1.4' }],
        h2: ['22px', { lineHeight: '1.3' }],
        h1: ['28px', { lineHeight: '1.2' }],
        // Hero numbers: mono 400, calm — not 64, not bold.
        hero: ['38px', { lineHeight: '1.1', fontWeight: '400' }],
      },
      maxWidth: {
        content: '1200px',
      },
      spacing: {
        row: '44px',
      },
    },
  },
  plugins: [],
};

export default config;
