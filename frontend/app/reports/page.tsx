'use client';

import { useState } from 'react';
import { useTranslation } from 'react-i18next';

import { downloadFile } from '@/lib/api';
import type { NumLocale } from '@/lib/format';

const YEARS = [2026, 2025];
const MONTHS = Array.from({ length: 12 }, (_, i) => i + 1);

/** Screen — Есептер (reports): generate the monthly management report (docx),
 *  the real docgen behind /documents/monthly-report. No dead end. */
export default function ReportsPage() {
  const { t, i18n } = useTranslation();
  const locale = (i18n.resolvedLanguage ?? 'kk') as NumLocale;
  const lang: 'kk' | 'ru' = locale === 'kk' ? 'kk' : 'ru';
  const [year, setYear] = useState(2026);
  const [month, setMonth] = useState(6);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(false);

  const generate = async () => {
    if (busy) return;
    setBusy(true);
    setError(false);
    try {
      await downloadFile(
        '/documents/monthly-report',
        { year, month, lang },
        `qalam_report_${year}-${String(month).padStart(2, '0')}_${lang}.docx`,
      );
    } catch {
      setError(true);
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <div>
        <h1 className="font-display text-h1 text-ink">{t('nav.reports')}</h1>
        <p className="mt-1 label-micro">{t('reports.lead')}</p>
      </div>

      <section className="space-y-4 border border-ink/15 p-6">
        <p className="text-secondary text-ink/70">{t('reports.monthly_report')}</p>
        <div className="flex flex-wrap items-end gap-4">
          <label className="flex flex-col gap-1">
            <span className="label-micro">{t('common.year')}</span>
            <select
              value={year}
              onChange={(e) => setYear(Number(e.target.value))}
              className="border border-ink/15 bg-paper px-2 py-1.5 font-mono text-secondary text-ink"
            >
              {YEARS.map((y) => (
                <option key={y} value={y}>
                  {y}
                </option>
              ))}
            </select>
          </label>
          <label className="flex flex-col gap-1">
            <span className="label-micro">{t('common.month')}</span>
            <select
              value={month}
              onChange={(e) => setMonth(Number(e.target.value))}
              className="border border-ink/15 bg-paper px-2 py-1.5 font-mono text-secondary text-ink"
            >
              {MONTHS.map((m) => (
                <option key={m} value={m}>
                  {String(m).padStart(2, '0')}
                </option>
              ))}
            </select>
          </label>
          <button
            type="button"
            onClick={generate}
            disabled={busy}
            className="bg-ink px-5 py-2 text-secondary font-medium text-paper transition-colors duration-150 hover:bg-ink/80 disabled:opacity-40"
          >
            {busy ? t('copilot.thinking') : t('reports.generate')}
          </button>
        </div>
        {error ? <p className="label-micro text-ink/50">{t('common.error')}</p> : null}
        <p className="label-micro text-ink/40">{t('reports.note')}</p>
      </section>
    </div>
  );
}
