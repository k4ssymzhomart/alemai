/**
 * TypeScript types for the FROZEN metrics API contract (P2).
 * Backend is built to exactly these shapes in parallel — do not "improve" them.
 *
 * GET /metrics/overview?year=
 * GET /metrics/lines?year=&funding_source=&care_type=&contract_id=
 * GET /metrics/line/{line_key}/monthly?year=
 *
 * Amounts are integer ₸. forecast_* / risk_class / burn_out_date stay null
 * until P6 — the UI renders them as computed-pending, never fakes them.
 */

export const FUNDING_SOURCES = ['gobmp', 'osms'] as const;
export type FundingSource = (typeof FUNDING_SOURCES)[number];

/** 'hosp' possible later — keep it in the type so P3+ data doesn't break the UI. */
export const CARE_TYPES = [
  'pmsp',
  'kdu',
  'day_hosp',
  'dent',
  'screening',
  'ambulance',
  'hosp',
] as const;
export type CareType = (typeof CARE_TYPES)[number];

/** D2 classes (docs/03 §6); null until the P6 forecast pipeline lands. */
export type RiskClass =
  | 'critical_under'
  | 'under'
  | 'on_track'
  | 'over'
  | 'critical_over';

export interface OverviewMetrics {
  year: number;
  /** "YYYY-MM" of the last loaded fact month, or null when no data. */
  as_of: string | null;
  plan_amount_year: number;
  plan_amount_ytd: number;
  fact_amount_ytd: number;
  billed_amount_ytd: number;
  rejected_amount_ytd: number;
  rejected_amount_mtd: number;
  execution_pct_ytd: number;
  forecast_amount_year: number | null;
  forecast_gap: number | null;
  risk_count: number | null;
  lines_total: number;
}

export interface ContractLine {
  /** Contains ':' and possibly '-' — URL-encode when used in a path. */
  line_key: string;
  contract_id: string;
  year: number;
  care_type: CareType;
  funding_source: FundingSource;
  service_group: string;
  plan_qty_year: number;
  plan_amount_year: number;
  plan_amount_ytd: number;
  fact_qty_ytd: number;
  fact_amount_ytd: number;
  billed_amount_ytd: number;
  rejected_amount_ytd: number;
  execution_pct_ytd: number;
  forecast_amount_year: number | null;
  forecast_gap: number | null;
  risk_class: RiskClass | null;
  burn_out_date: string | null;
  /** Seeded bilingual text (Epic C F2 read-side); null until the API exposes it. */
  forecast_explanation: LocalizedText | null;
  recommendation: LocalizedText | null;
}

/** {ru, kk} text seeded server-side (forecasts.explanation / risk.recommendation). */
export interface LocalizedText {
  ru: string;
  kk: string;
}

export interface LinesResponse {
  items: ContractLine[];
  total: number;
  year: number;
  as_of: string | null;
}

export interface MonthlyRow {
  month: number;
  /** "YYYY-MM" */
  period: string;
  plan_qty: number;
  plan_amount: number;
  fact_qty: number;
  fact_amount: number;
  billed_amount: number;
  rejected_amount: number;
  cumulative_plan_amount: number;
  cumulative_fact_amount: number;
}

export interface LineMonthlyResponse {
  line_key: string;
  year: number;
  /** Always 12 rows (future months zero-filled). */
  months: MonthlyRow[];
}

/** Query params for GET /metrics/lines. */
export interface LinesQuery {
  year: number;
  funding_source?: FundingSource;
  care_type?: CareType;
  contract_id?: string;
}
