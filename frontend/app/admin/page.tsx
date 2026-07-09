'use client';

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import ErrorState from '@/components/ErrorState';
import api from '@/lib/api';
import { fmtNumber, fmtTenge } from '@/lib/format';
import { useOps } from '@/lib/hooks';
import type { Thresholds } from '@/lib/types';

const THRESHOLD_FIELDS: Array<{ key: keyof Thresholds; labelKey: string }> = [
  { key: 'under_pct', labelKey: 'settings.th_under' },
  { key: 'over_pct', labelKey: 'settings.th_over' },
  { key: 'burnout_days', labelKey: 'settings.th_burnout' },
  { key: 'materiality_tenge', labelKey: 'settings.th_materiality' },
];

function fmtReset(iso: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  const p = (n: number) => String(n).padStart(2, '0');
  return `${p(d.getDate())}.${p(d.getMonth() + 1)}.${d.getFullYear()} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

/** Screen — Баптаулар (Settings) + Операциялық панель (G4): live ops counters,
 *  система/справочник versions, and a real (persisted) thresholds form. */
export default function AdminPage() {
  const { t } = useTranslation();
  const ops = useOps();
  const d = ops.data;

  return (
    <div className="max-w-4xl space-y-8">
      <h1 className="font-display text-h1 text-ink">{t('settings.title')}</h1>

      {/* Операциялық панель — live counters (G4) */}
      <Section title={t('ops.title')}>
        {ops.error ? (
          <ErrorState detail={ops.error} onRetry={ops.retry} />
        ) : !d ? (
          <div className="fill-dots-faint h-24 animate-pulse" />
        ) : (
          <>
            <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
              <Stat label={t('ops.registries')} value={fmtNumber(d.registries_checked)} />
              <Stat label={t('ops.positions')} value={fmtNumber(d.positions_scanned)} />
              <Stat
                label={t('ops.findings')}
                value={fmtNumber(d.findings_total)}
                sub={d.findings_by_severity
                  .map((s) => `${t(`sev.${s.key}`)} ${s.count}`)
                  .join(' · ')}
              />
              <Stat
                label={t('ops.sanctions_prevented')}
                value={fmtTenge(d.sanctions_prevented_tenge)}
                strong
              />
              <Stat label={t('ops.objections')} value={fmtNumber(d.objections_filed)} />
              <Stat
                label={t('ops.documents')}
                value={fmtNumber(d.documents_generated)}
                sub={d.documents_by_kind.map((k) => `${k.key} ${k.count}`).join(' · ')}
              />
              <Stat
                label={t('ops.imports')}
                value={fmtNumber(d.imports_count)}
                sub={`${t('ops.ok')} ${fmtNumber(d.import_rows_ok)} · ${t('ops.quarantine')} ${fmtNumber(d.import_rows_quarantined)}`}
              />
              <Stat
                label={t('ops.reconcile')}
                value={fmtNumber(d.reconcile_cases)}
                sub={fmtTenge(d.reconcile_tenge)}
              />
              <Stat label={t('ops.active_users')} value={fmtNumber(d.active_users)} />
            </div>
            <p className="pt-1 label-micro text-ink/40">{t('ops.live_note')}</p>
          </>
        )}
      </Section>

      {/* Жүйе туралы — версии справочников (trust signal) */}
      <Section title={t('settings.sec_about')}>
        <Row label={t('settings.app_version')} value={d?.app_version ?? '—'} />
        {(d?.ref_versions ?? []).map((r) => (
          <Row key={r.key} label={r.label} value={r.version} />
        ))}
        <Row label={t('ops.last_reset')} value={fmtReset(d?.last_demo_reset ?? null)} />
        <div className="pt-1">
          <span className="label-micro border border-ink/40 px-1.5 py-0.5 text-ink/60">
            {t('common.demo_badge')}
          </span>
        </div>
      </Section>

      <ThresholdsSection />

      <Section title={t('settings.sec_refs')}>
        <p className="text-secondary text-ink/60">{t('settings.other_rules')}</p>
      </Section>
    </div>
  );
}

/** Пороги рисков — persisted via PUT /admin/thresholds (emits a realtime event). */
function ThresholdsSection() {
  const { t } = useTranslation();
  const [values, setValues] = useState<Thresholds | null>(null);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    api
      .get<Thresholds>('/admin/thresholds')
      .then(setValues)
      .catch(() => setValues(null));
  }, []);

  const save = async () => {
    if (!values || saving) return;
    setSaving(true);
    setSaved(false);
    try {
      await api.put<Thresholds>('/admin/thresholds', values);
      setSaved(true);
    } finally {
      setSaving(false);
    }
  };

  return (
    <Section title={t('settings.sec_thresholds')}>
      {!values ? (
        <div className="fill-dots-faint h-20 animate-pulse" />
      ) : (
        <>
          <div className="grid grid-cols-2 gap-4">
            {THRESHOLD_FIELDS.map(({ key, labelKey }) => (
              <label key={key} className="flex flex-col gap-1">
                <span className="label-micro">{t(labelKey)}</span>
                <input
                  type="number"
                  value={values[key]}
                  onChange={(e) => {
                    setValues((v) => (v ? { ...v, [key]: Number(e.target.value) } : v));
                    setSaved(false);
                  }}
                  className="border border-ink/15 bg-paper px-2 py-1.5 font-mono text-secondary text-ink"
                />
              </label>
            ))}
          </div>
          <div className="flex items-center gap-3 pt-1">
            <button
              type="button"
              onClick={save}
              disabled={saving}
              className="bg-ink px-4 py-2 text-secondary font-medium text-paper transition-colors duration-150 hover:bg-ink/80 disabled:opacity-40"
            >
              {saving ? t('common.loading') : t('settings.save')}
            </button>
            {saved ? <span className="label-micro">{t('settings.saved')}</span> : null}
          </div>
        </>
      )}
    </Section>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="border border-ink/15">
      <div className="border-b border-ink/15 px-4 py-2 label-micro">{title}</div>
      <div className="space-y-3 p-4">{children}</div>
    </section>
  );
}

function Stat({
  label,
  value,
  sub,
  strong,
}: {
  label: string;
  value: string;
  sub?: string;
  strong?: boolean;
}) {
  return (
    <div className="border border-ink/15 px-4 py-3">
      <p className="label-micro">{label}</p>
      <p className={`mt-1 font-mono text-h3 tabular-nums ${strong ? 'text-ink' : 'text-ink/80'}`}>
        {value}
      </p>
      {sub ? <p className="mt-0.5 label-micro text-ink/40">{sub}</p> : null}
    </div>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4">
      <span className="text-secondary text-ink/70">{label}</span>
      <span className="font-mono text-secondary tabular-nums text-ink">{value}</span>
    </div>
  );
}
