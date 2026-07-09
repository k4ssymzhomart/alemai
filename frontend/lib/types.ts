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

// ─── Epic C: rules / pre-billing / reconcile / objections ──────────────────

export type FindingSeverity = 'block' | 'warn' | 'info' | 'yellow';

export interface RuleFindingGroup {
  rule_code: string;
  severity: FindingSeverity;
  count: number;
  amount_at_risk: number;
}

export interface RuleFinding {
  id: string;
  run_id: string;
  rule_code: string;
  claim_id: string | null;
  amount_at_risk: number;
  status: string;
  details: {
    ekd_code?: string;
    yellow?: boolean;
    severity?: FindingSeverity;
    care_type?: string;
    message_kk?: string;
    message_ru?: string;
    evidence?: Record<string, unknown>;
  } | null;
}

export interface RuleRunTotals {
  scope: string;
  claims_scanned: number;
  total_findings: number;
  total_amount_at_risk: number;
  block_positions: number;
  block_amount: number;
  sanction_risk: number;
  duration_ms: number;
  by_rule: Record<
    string,
    { count: number; amount_at_risk: number; severity: FindingSeverity; ekd_code?: string }
  >;
}

export interface RuleRunResult {
  run_id: string;
  scope: string;
  status: string;
  totals: RuleRunTotals;
}

export interface RunFindings {
  run_id: string;
  group_by: string | null;
  groups: RuleFindingGroup[];
  findings: RuleFinding[];
}

/** Combined pre-billing result: the run (verdict + by_rule) + its findings. */
export interface PrebillingResult {
  run: RuleRunResult;
  findings: RunFindings;
}

export interface ReconcileBucket {
  bucket_no: number;
  code: string;
  title_kk: string;
  title_ru: string;
  rows_count: number;
  total_amount: number;
}

export interface ReconcileBuckets {
  buckets: ReconcileBucket[];
}

export interface Objection {
  case_ref: string;
  ekd_code: string;
  ekd_name_ru: string;
  ekd_name_kk: string;
  significance: string;
  yellow: boolean;
  amount_at_stake: number;
  deadline_working_days: number;
  /** ISO date "YYYY-MM-DD". */
  deadline_date: string;
}

export interface ObjectionsResult {
  demo_today: string;
  defect_count: number;
  total_amount_at_stake: number;
  items: Objection[];
}

export interface ReconcileRow {
  claim_id: string;
  patient_id: string;
  service_code: string;
  service_name: string;
  date_start: string;
  amount: number;
  detail: string;
}

export interface ReconcileRows {
  bucket_no: number;
  rows: ReconcileRow[];
}

// ─── Epic D: copilot ───────────────────────────────────────────────────────

export interface CopilotCitation {
  doc_title: string;
  doc_number: string;
  anchor: string;
  lang?: string;
  url?: string | null;
}

export interface CopilotToolTrace {
  tool: string;
  arguments?: Record<string, unknown>;
  result_preview?: string | null;
}

export interface CopilotAnswer {
  answer: string;
  intent: 'data' | 'regulation' | 'report' | 'out_of_scope';
  locale: string;
  citations: CopilotCitation[];
  tool_traces: CopilotToolTrace[];
}

// ─── EPIC F: ingest & exchange ──────────────────────────────────────────────

export interface ImportColumnMap {
  column: string;
  field: string | null;
  status: 'auto' | 'ignored' | 'unknown';
  confidence: string | null;
  note: string | null;
}

export interface ImportQuarantineRow {
  row_no: number;
  raw: Record<string, unknown>;
  errors: string[];
}

export interface RegistryImportResult {
  file_id: string;
  filename: string;
  preset: string;
  period_detected: string | null;
  rows_total: number;
  rows_ok: number;
  matched: number;
  updated: number;
  new: number;
  quarantined: number;
  control_sum: number;
  claims_in_period: number;
  mapping: ImportColumnMap[];
  quarantine: ImportQuarantineRow[];
  rule_run_id: string | null;
  rule_totals: RuleRunTotals | null;
}

export interface AnnexLineDiff {
  care_type: string;
  funding_source: string;
  service_group: string;
  plan_current: number;
  plan_annex: number;
  delta: number;
  status: 'changed' | 'unchanged' | 'new' | 'missing';
}

export interface AnnexPreview {
  filename: string;
  year: number;
  lines: AnnexLineDiff[];
  changed: number;
  total_current: number;
  total_annex: number;
  total_delta: number;
  preview_only: boolean;
}

// ─── EPIC G: ecosystem (auth, events, ops, radar) ───────────────────────────

export interface Me {
  user_id: string | null;
  username: string;
  name: string;
  role: string;
  is_service: boolean;
}

export interface EventItem {
  id: string;
  ts: string;
  type: string;
  severity: 'info' | 'warn' | 'critical';
  actor: string;
  role: string | null;
  entity_ref: string | null;
  link: string | null;
  title_kk: string;
  title_ru: string;
  payload: Record<string, unknown> | null;
}

export interface EventsResponse {
  items: EventItem[];
  unread: number;
  cursor: string | null;
}

export interface OpsCounter { key: string; count: number }
export interface RefVersion { key: string; label: string; version: string }
export interface OpsDashboard {
  registries_checked: number;
  positions_scanned: number;
  findings_total: number;
  findings_by_severity: OpsCounter[];
  sanctions_prevented_tenge: number;
  objections_filed: number;
  documents_generated: number;
  documents_by_kind: OpsCounter[];
  reconcile_cases: number;
  reconcile_tenge: number;
  imports_count: number;
  import_rows_ok: number;
  import_rows_quarantined: number;
  active_users: number;
  events_total: number;
  last_demo_reset: string | null;
  app_version: string;
  ref_versions: RefVersion[];
}
export interface Thresholds {
  under_pct: number;
  over_pct: number;
  burnout_days: number;
  materiality_tenge: number;
}

export interface RadarRow {
  source_id: string;
  name_ru: string;
  name_kk: string;
  our_version: string;
  detected_version: string | null;
  status: 'ok' | 'stale' | 'unreachable' | 'manual';
  message: string | null;
  checked_at: string | null;
  official_url: string;
  mirror_url: string | null;
  quick_link: string;
  fetchable: boolean;
}
export interface RadarResponse { rows: RadarRow[]; checked_any: boolean }
export interface RadarCheckResult { summary: Record<string, number>; rows: RadarRow[] }
