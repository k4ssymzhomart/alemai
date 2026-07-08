/**
 * Deterministic mock fixtures, shaped EXACTLY per the frozen metrics contract.
 * Enabled with NEXT_PUBLIC_API_MOCK=1 (see lib/hooks.ts) — this is the demo
 * contingency (docs/08 §7): the UI must be fully browsable without a backend.
 *
 * Storylines planted for the golden path: КДУ/МРТ over-executing at 118%,
 * стоматология under-executing at 71%, 30 lines, ≈5.2 bn ₸ annual plan
 * (matches datagen's annual_target_amount). Everything is derived from the
 * seeds below via a fixed-seed PRNG — same numbers on every load, no
 * Math.random anywhere.
 */

import type {
  CareType,
  ContractLine,
  FundingSource,
  LineMonthlyResponse,
  LinesQuery,
  LinesResponse,
  MonthlyRow,
  OverviewMetrics,
} from '@/lib/types';

const MOCK_YEAR = 2026;
/** Fact data loaded through June (demo happens in July). */
const AS_OF_MONTH = 6;
const AS_OF = '2026-06';
const CONTRACT_ID = 'C-2026-014';
/** Small artificial latency so loading states are visible/realistic. */
const MOCK_DELAY_MS = 180;

interface LineSeed {
  src: FundingSource;
  care: CareType;
  group: string;
  slug: string;
  qty: number;
  amount: number;
  /** Target fact/plan ratio for the first AS_OF_MONTH months. */
  exec: number;
}

/** 30 lines, Σ amount = 5 185 000 000 ₸ (≈5.2 bn). */
const SEEDS: LineSeed[] = [
  // ГОБМП (ТМККК)
  { src: 'gobmp', care: 'pmsp', group: 'Кешенді жан басына шаққандағы норматив (МСАК)', slug: 'pmsp-capita', qty: 1_236_000, amount: 2_400_000_000, exec: 0.99 },
  { src: 'gobmp', care: 'ambulance', group: 'Жедел медициналық жәрдем', slug: 'ambulance', qty: 62_000, amount: 310_000_000, exec: 1.02 },
  { src: 'gobmp', care: 'day_hosp', group: 'Күндізгі стационар (педиатрия)', slug: 'dayhosp-ped', qty: 3_800, amount: 95_000_000, exec: 0.93 },
  { src: 'gobmp', care: 'dent', group: 'Балаларға стоматологиялық көмек', slug: 'dent-child', qty: 24_000, amount: 72_000_000, exec: 0.71 },
  { src: 'gobmp', care: 'dent', group: 'Шұғыл стоматологиялық көмек', slug: 'dent-urgent', qty: 7_300, amount: 22_000_000, exec: 0.77 },
  { src: 'gobmp', care: 'kdu', group: 'Рентгенография', slug: 'xray', qty: 21_000, amount: 42_000_000, exec: 0.82 },
  { src: 'gobmp', care: 'kdu', group: 'Флюорография', slug: 'fluoro', qty: 30_000, amount: 18_000_000, exec: 0.88 },
  { src: 'gobmp', care: 'screening', group: 'Сүт безі обырының скринингі', slug: 'scr-breast', qty: 6_800, amount: 34_000_000, exec: 0.64 },
  { src: 'gobmp', care: 'screening', group: 'Жатыр мойны обырының скринингі', slug: 'scr-cervical', qty: 8_600, amount: 26_000_000, exec: 0.69 },
  { src: 'gobmp', care: 'screening', group: 'Колоректальды обыр скринингі', slug: 'scr-colorectal', qty: 4_200, amount: 21_000_000, exec: 0.58 },
  { src: 'gobmp', care: 'screening', group: 'Балалар профилактикалық скринингі', slug: 'scr-child', qty: 9_000, amount: 18_000_000, exec: 0.83 },
  // ОСМС (МӘМС)
  { src: 'osms', care: 'pmsp', group: 'Жан басына шаққандағы норматив (МӘМС үлесі)', slug: 'pmsp-capita', qty: 412_000, amount: 800_000_000, exec: 0.97 },
  { src: 'osms', care: 'kdu', group: 'МРТ', slug: 'mrt', qty: 3_400, amount: 118_000_000, exec: 1.18 },
  { src: 'osms', care: 'kdu', group: 'КТ', slug: 'kt', qty: 4_800, amount: 96_000_000, exec: 1.07 },
  { src: 'osms', care: 'kdu', group: 'УДЗ', slug: 'udz', qty: 29_000, amount: 88_000_000, exec: 0.94 },
  { src: 'osms', care: 'kdu', group: 'Эндоскопиялық зерттеулер', slug: 'endoscopy', qty: 5_400, amount: 54_000_000, exec: 0.86 },
  { src: 'osms', care: 'kdu', group: 'Зертханалық зерттеулер', slug: 'lab', qty: 380_000, amount: 230_000_000, exec: 0.92 },
  { src: 'osms', care: 'kdu', group: 'Гистологиялық зерттеулер', slug: 'histology', qty: 7_200, amount: 36_000_000, exec: 0.79 },
  { src: 'osms', care: 'kdu', group: 'Кардиолог консультациясы', slug: 'cardio', qty: 11_000, amount: 44_000_000, exec: 0.96 },
  { src: 'osms', care: 'kdu', group: 'Невролог консультациясы', slug: 'neuro', qty: 10_200, amount: 41_000_000, exec: 0.91 },
  { src: 'osms', care: 'kdu', group: 'Эндокринолог консультациясы', slug: 'endocrino', qty: 9_500, amount: 38_000_000, exec: 1.03 },
  { src: 'osms', care: 'kdu', group: 'Офтальмолог консультациясы', slug: 'ophthalmo', qty: 8_200, amount: 33_000_000, exec: 0.89 },
  { src: 'osms', care: 'kdu', group: 'Оториноларинголог консультациясы', slug: 'lor', qty: 7_200, amount: 29_000_000, exec: 0.84 },
  { src: 'osms', care: 'kdu', group: 'Хирург консультациясы', slug: 'surgeon', qty: 7_700, amount: 31_000_000, exec: 0.98 },
  { src: 'osms', care: 'kdu', group: 'Физиотерапия', slug: 'physio', qty: 18_000, amount: 27_000_000, exec: 0.75 },
  { src: 'osms', care: 'kdu', group: 'Медициналық оңалту', slug: 'rehab', qty: 4_900, amount: 49_000_000, exec: 0.87 },
  { src: 'osms', care: 'day_hosp', group: 'Күндізгі стационар (терапия)', slug: 'dayhosp-ther', qty: 6_300, amount: 190_000_000, exec: 0.95 },
  { src: 'osms', care: 'day_hosp', group: 'Күндізгі стационар (хирургия)', slug: 'dayhosp-surg', qty: 3_200, amount: 130_000_000, exec: 0.89 },
  { src: 'osms', care: 'day_hosp', group: 'Күндізгі стационар (гинекология)', slug: 'dayhosp-gyn', qty: 2_600, amount: 78_000_000, exec: 0.92 },
  { src: 'osms', care: 'dent', group: 'Жүкті әйелдерге стоматологиялық көмек', slug: 'dent-pregnant', qty: 4_100, amount: 15_000_000, exec: 0.68 },
];

/** Monthly seasonality weights (Jan..Dec): summer dip, Q4 push. */
const SEASON = [0.82, 0.86, 0.98, 1.0, 1.04, 1.02, 0.9, 0.82, 1.06, 1.12, 1.16, 1.22];

/** Tiny deterministic PRNG (fixed seeds ⇒ identical fixtures every run). */
function mulberry32(seed: number): () => number {
  let a = seed >>> 0;
  return () => {
    a = (a + 0x6d2b79f5) | 0;
    let t = Math.imul(a ^ (a >>> 15), 1 | a);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

const sum = (values: number[]): number => values.reduce((acc, v) => acc + v, 0);

/** Split an integer total by weights; remainder distributed so Σ = total. */
function distribute(total: number, weights: number[]): number[] {
  const wsum = sum(weights);
  const out = weights.map((w) => Math.floor((total * w) / wsum));
  let remainder = total - sum(out);
  for (let i = 0; remainder > 0; i = (i + 1) % out.length) {
    out[i] += 1;
    remainder -= 1;
  }
  return out;
}

const pad2 = (m: number): string => String(m).padStart(2, '0');
const round1 = (v: number): number => Math.round(v * 10) / 10;

interface BuiltLine {
  line: ContractLine;
  months: MonthlyRow[];
}

function buildLine(seed: LineSeed, index: number): BuiltLine {
  const rng = mulberry32(index * 7919 + 101);
  const planAmounts = distribute(seed.amount, SEASON);
  const planQtys = distribute(seed.qty, SEASON);

  // Facts for months 1..AS_OF_MONTH: noisy per month, rescaled so that
  // fact_ytd / plan_ytd lands exactly on seed.exec (МРТ = 118.0%, dent = 71.0%).
  const planYtd = sum(planAmounts.slice(0, AS_OF_MONTH));
  const factYtd = Math.round(planYtd * seed.exec);
  const rawFacts = planAmounts
    .slice(0, AS_OF_MONTH)
    .map((p) => p * (0.9 + rng() * 0.2));
  const rawSum = sum(rawFacts);
  const facts = rawFacts.map((raw) => Math.round((raw / rawSum) * factYtd));
  facts[AS_OF_MONTH - 1] += factYtd - sum(facts);

  const rejectRate = 0.006 + rng() * 0.024; // 0.6%..3% of fact снято

  const months: MonthlyRow[] = [];
  let cumulativePlan = 0;
  let cumulativeFact = 0;
  for (let m = 1; m <= 12; m++) {
    const planAmount = planAmounts[m - 1];
    const factAmount = m <= AS_OF_MONTH ? facts[m - 1] : 0;
    const rejectedAmount =
      m <= AS_OF_MONTH ? Math.round(factAmount * rejectRate * (0.7 + rng() * 0.6)) : 0;
    const factQty =
      m <= AS_OF_MONTH && planAmount > 0
        ? Math.round(planQtys[m - 1] * (factAmount / planAmount))
        : 0;
    cumulativePlan += planAmount;
    cumulativeFact += factAmount;
    months.push({
      month: m,
      period: `${MOCK_YEAR}-${pad2(m)}`,
      plan_qty: planQtys[m - 1],
      plan_amount: planAmount,
      fact_qty: factQty,
      fact_amount: factAmount,
      billed_amount: factAmount + rejectedAmount,
      rejected_amount: rejectedAmount,
      cumulative_plan_amount: cumulativePlan,
      cumulative_fact_amount: cumulativeFact,
    });
  }

  const ytd = months.slice(0, AS_OF_MONTH);
  const line: ContractLine = {
    line_key: `${CONTRACT_ID}:${seed.src}:${seed.care}:${seed.slug}`,
    contract_id: CONTRACT_ID,
    year: MOCK_YEAR,
    care_type: seed.care,
    funding_source: seed.src,
    service_group: seed.group,
    plan_qty_year: seed.qty,
    plan_amount_year: seed.amount,
    plan_amount_ytd: planYtd,
    fact_qty_ytd: sum(ytd.map((r) => r.fact_qty)),
    fact_amount_ytd: factYtd,
    billed_amount_ytd: sum(ytd.map((r) => r.billed_amount)),
    rejected_amount_ytd: sum(ytd.map((r) => r.rejected_amount)),
    execution_pct_ytd: planYtd > 0 ? round1((factYtd / planYtd) * 100) : 0,
    forecast_amount_year: null,
    risk_class: null,
    burn_out_date: null,
  };
  return { line, months };
}

/** Built once at module load; server order = plan_amount_year desc. */
const BUILT: BuiltLine[] = SEEDS.map(buildLine).sort(
  (a, b) => b.line.plan_amount_year - a.line.plan_amount_year,
);

const delay = (): Promise<void> =>
  new Promise((resolve) => setTimeout(resolve, MOCK_DELAY_MS));

function emptyOverview(year: number): OverviewMetrics {
  return {
    year,
    as_of: null,
    plan_amount_year: 0,
    plan_amount_ytd: 0,
    fact_amount_ytd: 0,
    billed_amount_ytd: 0,
    rejected_amount_ytd: 0,
    rejected_amount_mtd: 0,
    execution_pct_ytd: 0,
    forecast_amount_year: null,
    forecast_gap: null,
    risk_count: null,
    lines_total: 0,
  };
}

function zeroMonths(year: number): MonthlyRow[] {
  return Array.from({ length: 12 }, (_, i) => ({
    month: i + 1,
    period: `${year}-${pad2(i + 1)}`,
    plan_qty: 0,
    plan_amount: 0,
    fact_qty: 0,
    fact_amount: 0,
    billed_amount: 0,
    rejected_amount: 0,
    cumulative_plan_amount: 0,
    cumulative_fact_amount: 0,
  }));
}

export async function mockOverview(year: number): Promise<OverviewMetrics> {
  await delay();
  if (year !== MOCK_YEAR) return emptyOverview(year);
  const lines = BUILT.map((b) => b.line);
  const planYtd = sum(lines.map((l) => l.plan_amount_ytd));
  const factYtd = sum(lines.map((l) => l.fact_amount_ytd));
  return {
    year,
    as_of: AS_OF,
    plan_amount_year: sum(lines.map((l) => l.plan_amount_year)),
    plan_amount_ytd: planYtd,
    fact_amount_ytd: factYtd,
    billed_amount_ytd: sum(lines.map((l) => l.billed_amount_ytd)),
    rejected_amount_ytd: sum(lines.map((l) => l.rejected_amount_ytd)),
    rejected_amount_mtd: sum(
      BUILT.map((b) => b.months[AS_OF_MONTH - 1].rejected_amount),
    ),
    execution_pct_ytd: planYtd > 0 ? round1((factYtd / planYtd) * 100) : 0,
    forecast_amount_year: null,
    forecast_gap: null,
    risk_count: null,
    lines_total: lines.length,
  };
}

export async function mockLines(query: LinesQuery): Promise<LinesResponse> {
  await delay();
  if (query.year !== MOCK_YEAR) {
    return { items: [], total: 0, year: query.year, as_of: null };
  }
  const items = BUILT.map((b) => b.line).filter(
    (line) =>
      (!query.funding_source || line.funding_source === query.funding_source) &&
      (!query.care_type || line.care_type === query.care_type) &&
      (!query.contract_id || line.contract_id === query.contract_id),
  );
  return { items, total: items.length, year: query.year, as_of: AS_OF };
}

export async function mockLineMonthly(
  lineKey: string,
  year: number,
): Promise<LineMonthlyResponse> {
  await delay();
  const built =
    year === MOCK_YEAR ? BUILT.find((b) => b.line.line_key === lineKey) : undefined;
  // Unknown key/year → 12 zero rows (the charts must survive all-zero data).
  return {
    line_key: lineKey,
    year,
    months: built ? built.months : zeroMonths(year),
  };
}
