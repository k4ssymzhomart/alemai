'use client';

import { useState } from 'react';
import { useTranslation } from 'react-i18next';

/** Справочник versions surfaced as the trust signal (docs/13 §4.12, §16 C12). */
const REF_VERSIONS = [
  { key: 'ref_ekd', version: 'ред. приказа №19 · 27.02.2026' },
  { key: 'ref_tarif', version: '№ ҚР ДСМ-170/2020 · прил. 7' },
  { key: 'ref_pkg', version: 'ПП №672 / №421 · 2026' },
];

const DEFAULT_THRESHOLDS = {
  th_under: 90,
  th_over: 105,
  th_burnout: 45,
  th_materiality: 100000,
};

/** Screen — Баптаулар (PD3-lite Settings): functional where the backend
 *  exists (пороги, справочник versions), read-only stubs elsewhere. */
export default function AdminPage() {
  const { t } = useTranslation();
  const [thresholds, setThresholds] = useState(DEFAULT_THRESHOLDS);
  const [saved, setSaved] = useState(false);

  return (
    <div className="max-w-3xl space-y-8">
      <h1 className="font-display text-h1 text-ink">{t('settings.title')}</h1>

      {/* О системе — справочник versions */}
      <Section title={t('settings.sec_about')}>
        <Row label={t('settings.app_version')} value="QALAM · 0.4 · demo" />
        {REF_VERSIONS.map((r) => (
          <Row key={r.key} label={t(`settings.${r.key}`)} value={r.version} />
        ))}
        <div className="pt-1">
          <span className="label-micro border border-ink/40 px-1.5 py-0.5 text-ink/60">
            {t('common.demo_badge')}
          </span>
        </div>
      </Section>

      {/* Пороги рисков — functional form (local; risk classes recompute) */}
      <Section title={t('settings.sec_thresholds')}>
        <div className="grid grid-cols-2 gap-4">
          {(Object.keys(DEFAULT_THRESHOLDS) as Array<keyof typeof DEFAULT_THRESHOLDS>).map(
            (k) => (
              <label key={k} className="flex flex-col gap-1">
                <span className="label-micro">{t(`settings.${k}`)}</span>
                <input
                  type="number"
                  value={thresholds[k]}
                  onChange={(e) => {
                    setThresholds((s) => ({ ...s, [k]: Number(e.target.value) }));
                    setSaved(false);
                  }}
                  className="border border-ink/15 bg-paper px-2 py-1.5 font-mono text-secondary text-ink"
                />
              </label>
            ),
          )}
        </div>
        <div className="flex items-center gap-3 pt-1">
          <button
            type="button"
            onClick={() => setSaved(true)}
            className="bg-ink px-4 py-2 text-secondary font-medium text-paper hover:opacity-80"
          >
            {t('settings.save')}
          </button>
          {saved ? <span className="label-micro">{t('settings.saved')}</span> : null}
        </div>
      </Section>

      {/* Read-only stubs — no dead ends (explain what will live here) */}
      <Section title={t('settings.sec_refs')}>
        <p className="text-secondary text-ink/60">{t('settings.other_rules')}</p>
      </Section>
      <Section title={t('settings.org_row')}>
        <p className="text-secondary text-ink/60">{t('settings.other_org')}</p>
      </Section>
    </div>
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

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-baseline justify-between gap-4">
      <span className="text-secondary text-ink/70">{label}</span>
      <span className="font-mono text-secondary tabular-nums text-ink">{value}</span>
    </div>
  );
}
