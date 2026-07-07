import type { Config } from 'tailwindcss';

/**
 * Design language (docs/04 §2): clean, data-dense, dark-on-light.
 * Accent = teal #0e7c66 (health + finance), exposed as `accent` with a full shade scale.
 */
const config: Config = {
  content: [
    './app/**/*.{ts,tsx}',
    './components/**/*.{ts,tsx}',
    './lib/**/*.{ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        accent: {
          DEFAULT: '#0e7c66',
          50: '#f0faf7',
          100: '#d5f2e9',
          200: '#abe4d4',
          300: '#79cfba',
          400: '#4bb49d',
          500: '#2d9a83',
          600: '#0e7c66',
          700: '#0c6454',
          800: '#0b5044',
          900: '#0a4239',
          950: '#04251f',
        },
      },
    },
  },
  plugins: [],
};

export default config;
