/**
 * Candidate font stacks for the /design specimen gate (Epic A.2). The lead
 * picks one by eye; the winner is promoted into lib/fonts.ts. Any candidate
 * whose kk glyphs ( Ә Ғ Қ Ң Ө Ұ Ү Һ І ) jump weight/width — a fallback
 * firing — is disqualified. Loaded ONLY on /design (internal, off golden path).
 */
import {
  Golos_Text,
  IBM_Plex_Mono,
  Inter,
  Literata,
  Manrope,
  PT_Serif,
} from 'next/font/google';

const literata = Literata({
  subsets: ['latin', 'cyrillic'],
  weight: ['500', '600'],
});
const inter = Inter({ subsets: ['latin', 'cyrillic'], weight: ['400', '500'] });
const manrope = Manrope({ subsets: ['latin', 'cyrillic'], weight: ['600', '700'] });
const ptSerif = PT_Serif({ subsets: ['latin', 'cyrillic'], weight: ['700'] });
const golos = Golos_Text({ subsets: ['latin', 'cyrillic'], weight: ['400', '500'] });
const plexMono = IBM_Plex_Mono({ subsets: ['latin', 'cyrillic'], weight: ['400'] });

export interface CandidateStack {
  id: number;
  label: string;
  note: string;
  displayClass: string;
  displayWeight: number;
  uiClass: string;
  figuresClass: string;
}

export const CANDIDATE_STACKS: CandidateStack[] = [
  {
    id: 1,
    label: 'Literata / Inter / IBM Plex Mono',
    note: 'Editorial serif — premium print feel (recommended)',
    displayClass: literata.className,
    displayWeight: 600,
    uiClass: inter.className,
    figuresClass: plexMono.className,
  },
  {
    id: 2,
    label: 'Manrope / Inter / IBM Plex Mono',
    note: 'Modern premium sans',
    displayClass: manrope.className,
    displayWeight: 700,
    uiClass: inter.className,
    figuresClass: plexMono.className,
  },
  {
    id: 3,
    label: 'PT Serif / Golos Text / IBM Plex Mono',
    note: 'Max kk safety (ParaType + Golos — guaranteed Cyrillic)',
    displayClass: ptSerif.className,
    displayWeight: 700,
    uiClass: golos.className,
    figuresClass: plexMono.className,
  },
];
