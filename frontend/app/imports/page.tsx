'use client';

import { useRef, useState, type DragEvent } from 'react';
import { useRouter } from 'next/navigation';
import clsx from 'clsx';
import { useTranslation } from 'react-i18next';

import { API_BASE, downloadFileGet, uploadFile } from '@/lib/api';
import { fmtNumber, fmtTenge } from '@/lib/format';
import type { AnnexPreview, RegistryImportResult } from '@/lib/types';

/**
 * Screen «Импорт» (EPIC F1) — the answer to «как данные попадают в систему?».
 * Dropzone → 3-step reveal: Файл танылды → Маппинг → Нәтиже → «Тексеруді іске
 * қосу» routes to the pre-billing verdict. The import is idempotent server-side,
 * so a live demo upload can never corrupt the seeded numbers.
 */
export default function ImportsPage() {
  const { t } = useTranslation();
  const [result, setResult] = useState<RegistryImportResult | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onFile = async (file: File) => {
    if (busy) return;
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(
        await uploadFile<RegistryImportResult>('/imports/mis-registry', file),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-10">
      <div>
        <h1 className="font-display text-h1 text-ink">{t('nav.imports')}</h1>
        <p className="mt-1 label-micro">{t('imports.lead')}</p>
      </div>

      <Dropzone busy={busy} onFile={onFile} />

      {error ? (
        <p className="border-l-2 border-ink px-3 py-2 text-secondary text-ink/80">
          ! {t('imports.error')}{' '}
          <span className="font-mono text-micro text-ink/50">{error}</span>
        </p>
      ) : null}

      {result ? <ImportSteps result={result} /> : null}

      <AnnexSection />
    </div>
  );
}

/**
 * F3 — contract annex, PREVIEW ONLY: diff «line: was → becomes, Δ₸»; commit
 * is deliberately absent in the demo («қолдану — пилотта»).
 */
function AnnexSection() {
  const { t } = useTranslation();
  const [preview, setPreview] = useState<AnnexPreview | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const onFile = async (file: File) => {
    if (busy) return;
    setBusy(true);
    setError(null);
    try {
      setPreview(
        await uploadFile<AnnexPreview>('/imports/contract-annex?preview=1', file),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setBusy(false);
    }
  };

  return (
    <section className="space-y-4 border-t-2 border-ink pt-6">
      <div>
        <h2 className="font-display text-h2 text-ink">{t('imports.annex_title')}</h2>
        <p className="mt-1 label-micro">{t('imports.annex_pilot_note')}</p>
      </div>

      <div className="flex flex-wrap items-center gap-4">
        <button
          type="button"
          disabled={busy}
          onClick={() => inputRef.current?.click()}
          className="border border-dashed border-ink/40 px-4 py-2 text-secondary font-medium text-ink transition-colors duration-150 hover:border-ink disabled:opacity-40"
        >
          {busy ? t('common.loading') : t('imports.dropzone_hint')}
        </button>
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.csv"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) onFile(file);
            event.target.value = '';
          }}
        />
        <a
          href={`${API_BASE}/imports/samples/annex_2026.xlsx`}
          className="font-mono text-micro lowercase text-ink/60 underline decoration-ink/30 underline-offset-2 hover:text-ink"
        >
          annex_2026.xlsx
        </a>
      </div>

      {error ? (
        <p className="border-l-2 border-ink px-3 py-2 text-secondary text-ink/80">
          ! {t('imports.error')}{' '}
          <span className="font-mono text-micro text-ink/50">{error}</span>
        </p>
      ) : null}

      {preview ? <AnnexDiff preview={preview} /> : null}
    </section>
  );
}

function AnnexDiff({ preview }: { preview: AnnexPreview }) {
  const { t } = useTranslation();
  return (
    <div className="space-y-3">
      <p className="text-body font-medium text-ink">
        {t('imports.annex_lead')} ·{' '}
        <span className="font-mono tabular-nums">
          Δ {fmtTenge(preview.total_delta)}
        </span>
      </p>
      <div className="overflow-x-auto border border-ink/15">
        <table className="w-full border-collapse text-secondary">
          <thead>
            <tr className="border-b border-ink/15 text-left label-micro">
              <th className="px-4 py-2 font-normal">{t('imports.annex_line')}</th>
              <th className="px-4 py-2 text-right font-normal">
                {t('imports.annex_was')}
              </th>
              <th className="px-4 py-2 text-right font-normal">
                {t('imports.annex_becomes')}
              </th>
              <th className="px-4 py-2 text-right font-normal">Δ ₸</th>
            </tr>
          </thead>
          <tbody>
            {preview.lines.map((line) => {
              const changed = line.status !== 'unchanged';
              const name = [
                t(`care_type.${line.care_type}`),
                line.service_group,
                t(`funding.${line.funding_source}`),
              ]
                .filter(Boolean)
                .join(' · ');
              return (
                <tr
                  key={`${line.care_type}:${line.funding_source}:${line.service_group}`}
                  className={clsx(
                    'border-b border-ink/[.06] last:border-0',
                    changed && 'border-l-2 border-l-ink font-medium',
                  )}
                >
                  <td className="px-4 py-1.5 text-ink/80">{name}</td>
                  <td className="px-4 py-1.5 text-right font-mono tabular-nums text-ink/60">
                    {fmtTenge(line.plan_current)}
                  </td>
                  <td className="px-4 py-1.5 text-right font-mono tabular-nums text-ink">
                    {changed ? '→ ' : ''}
                    {fmtTenge(line.plan_annex)}
                  </td>
                  <td className="px-4 py-1.5 text-right font-mono tabular-nums">
                    {line.delta === 0 ? '—' : fmtTenge(line.delta)}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <p className="label-micro">{t('imports.annex_pilot_note')}</p>
    </div>
  );
}

function Dropzone({
  busy,
  onFile,
}: {
  busy: boolean;
  onFile: (file: File) => void;
}) {
  const { t } = useTranslation();
  const inputRef = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);

  const onDrop = (event: DragEvent<HTMLButtonElement>) => {
    event.preventDefault();
    setOver(false);
    const file = event.dataTransfer.files?.[0];
    if (file) onFile(file);
  };

  return (
    <div className="space-y-2">
      <button
        type="button"
        disabled={busy}
        onClick={() => inputRef.current?.click()}
        onDragOver={(event) => {
          event.preventDefault();
          setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={onDrop}
        className={clsx(
          'relative block w-full border border-dashed px-6 py-14 text-center transition-colors duration-150',
          over ? 'border-ink bg-ink/[.03]' : 'border-ink/40 hover:border-ink',
          busy && 'opacity-60',
        )}
      >
        <span
          aria-hidden
          className="fill-dots-faint pointer-events-none absolute inset-0"
        />
        <span className="relative block text-body text-ink">
          {busy ? t('common.loading') : t('imports.dropzone')}
        </span>
        <span className="relative mt-2 block label-micro">
          {t('imports.dropzone_hint')}
        </span>
        <input
          ref={inputRef}
          type="file"
          accept=".xlsx,.csv"
          className="hidden"
          onChange={(event) => {
            const file = event.target.files?.[0];
            if (file) onFile(file);
            event.target.value = '';
          }}
        />
      </button>

      <p className="label-micro">
        {t('imports.samples')}:{' '}
        {['registry_2025-11.xlsx', 'registry_broken.xlsx'].map((name, i) => (
          <a
            key={name}
            href={`${API_BASE}/imports/samples/${name}`}
            className={clsx(
              'font-mono lowercase text-ink/60 underline decoration-ink/30 underline-offset-2 hover:text-ink',
              i > 0 && 'ml-3',
            )}
          >
            {name}
          </a>
        ))}
      </p>
    </div>
  );
}

function StepBar({ no, titleKey }: { no: string; titleKey: string }) {
  const { t } = useTranslation();
  return (
    <div className="flex items-center gap-3 border-b-2 border-ink pb-2">
      <span className="font-mono text-micro text-ink/40">{no}</span>
      <h2 className="font-display text-h3 text-ink">{t(titleKey)}</h2>
    </div>
  );
}

function Stat({
  labelKey,
  value,
  strong,
}: {
  labelKey: string;
  value: string;
  strong?: boolean;
}) {
  const { t } = useTranslation();
  return (
    <div className="border border-ink/15 px-4 py-3">
      <p className="label-micro">{t(labelKey)}</p>
      <p
        className={clsx(
          'mt-1 font-mono text-h3 tabular-nums',
          strong ? 'text-ink' : 'text-ink/80',
        )}
      >
        {value}
      </p>
    </div>
  );
}

function ImportSteps({ result }: { result: RegistryImportResult }) {
  const { t } = useTranslation();
  const router = useRouter();
  const totals = result.rule_totals;

  return (
    <div className="space-y-10">
      {/* 01 — Файл танылды */}
      <section className="space-y-4">
        <StepBar no="01" titleKey="imports.step_file" />
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Stat labelKey="imports.file" value={result.filename} />
          <Stat labelKey="imports.rows_total" value={fmtNumber(result.rows_total)} />
          <Stat labelKey="common.period" value={result.period_detected ?? '—'} />
          <Stat labelKey="imports.preset" value={result.preset} />
        </div>
      </section>

      {/* 02 — Маппинг */}
      <section className="space-y-4">
        <StepBar no="02" titleKey="imports.step_mapping" />
        <div className="border border-ink/15">
          <table className="w-full border-collapse text-secondary">
            <thead>
              <tr className="border-b border-ink/15 text-left label-micro">
                <th className="px-4 py-2 font-normal">{t('imports.file_column')}</th>
                <th className="px-4 py-2 font-normal">{t('imports.system_field')}</th>
                <th className="px-4 py-2 font-normal">{t('imports.map_status')}</th>
              </tr>
            </thead>
            <tbody>
              {result.mapping.map((m) => (
                <tr
                  key={m.column}
                  className="border-b border-ink/[.06] last:border-0"
                >
                  <td className="px-4 py-1.5 text-ink/80">{m.column}</td>
                  <td className="px-4 py-1.5 font-mono text-ink">
                    {m.field ?? '—'}
                  </td>
                  <td className="px-4 py-1.5">
                    {m.status === 'auto' ? (
                      <span className="border border-ink px-1.5 py-0.5 font-mono text-micro text-ink">
                        auto
                      </span>
                    ) : (
                      <span className="font-mono text-micro text-ink/40">
                        {t('imports.ignored')}
                        {m.note ? ` · ${m.note}` : ''}
                      </span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* 03 — Нәтиже */}
      <section className="space-y-4">
        <StepBar no="03" titleKey="imports.step_result" />
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
          <Stat labelKey="imports.rows_ok" value={fmtNumber(result.rows_ok)} strong />
          <Stat labelKey="imports.matched" value={fmtNumber(result.matched)} />
          <Stat labelKey="imports.updated" value={fmtNumber(result.updated)} />
          <Stat labelKey="imports.new" value={fmtNumber(result.new)} />
          <Stat
            labelKey="imports.quarantined"
            value={fmtNumber(result.quarantined)}
            strong={result.quarantined > 0}
          />
        </div>
        <p className="label-micro">{t('imports.idempotent_note')}</p>

        {result.quarantine.length > 0 ? (
          <QuarantineBlock result={result} />
        ) : null}

        <div className="flex flex-wrap items-center gap-4 border-t border-ink/15 pt-4">
          <button
            type="button"
            onClick={() => router.push('/prebilling')}
            className="bg-ink px-5 py-2.5 text-secondary font-medium text-paper transition-colors duration-150 hover:bg-ink/80"
          >
            {t('imports.run_check')} →
          </button>
          {totals ? (
            <span className="font-mono text-secondary tabular-nums text-ink/70">
              {t('imports.check_done')}: {fmtNumber(totals.block_positions)} ·{' '}
              {fmtTenge(totals.block_amount)} ·{' '}
              {fmtTenge(totals.sanction_risk)}
            </span>
          ) : null}
        </div>
      </section>
    </div>
  );
}

function QuarantineBlock({ result }: { result: RegistryImportResult }) {
  const { t } = useTranslation();
  const [busy, setBusy] = useState(false);

  const exportQuarantine = async () => {
    if (busy) return;
    setBusy(true);
    try {
      await downloadFileGet(
        `/exports/quarantine/${result.file_id}.xlsx`,
        undefined,
        `qalam_quarantine.xlsx`,
      );
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="space-y-3">
      <div className="border border-ink/15">
        <table className="w-full border-collapse text-secondary">
          <thead>
            <tr className="border-b border-ink/15 text-left label-micro">
              <th className="w-24 px-4 py-2 font-normal">{t('imports.row_no')}</th>
              <th className="px-4 py-2 font-normal">
                {t('imports.quarantine_reasons')}
              </th>
            </tr>
          </thead>
          <tbody>
            {result.quarantine.map((q) => (
              <tr key={q.row_no} className="border-b border-ink/[.06] last:border-0">
                <td className="px-4 py-1.5 font-mono tabular-nums text-ink/60">
                  {q.row_no}
                </td>
                <td className="px-4 py-1.5 text-ink/80">{q.errors.join('; ')}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button
        type="button"
        onClick={exportQuarantine}
        disabled={busy}
        className="border border-ink/40 px-4 py-2 text-secondary font-medium text-ink transition-colors duration-150 hover:bg-ink/[.03] disabled:opacity-40"
      >
        {t('imports.export_quarantine')}
      </button>
    </div>
  );
}
