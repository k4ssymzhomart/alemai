'use client';

import { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import api from '@/lib/api';
import type { RadarCheckResult, RadarResponse, RadarRow } from '@/lib/types';

/** Status glyph + colour (rebrand v3): ✓ актуально / ! новее / — недоступно. */
const STATUS_STYLE: Record<RadarRow['status'], { glyph: string; chip: string; dot: string }> = {
  ok: { glyph: '✓', chip: 'text-ok', dot: 'text-ok' },
  stale: { glyph: '!', chip: 'border border-warn bg-warn/10 px-1.5 py-0.5 text-ink', dot: 'text-warn' },
  unreachable: { glyph: '—', chip: 'text-ink/50', dot: 'text-ink/50' },
  manual: { glyph: '·', chip: 'text-ink/60', dot: 'text-ink/60' },
};

function checkedTime(iso: string | null): string {
  if (!iso) return '—';
  const d = new Date(iso);
  const p = (n: number) => String(n).padStart(2, '0');
  return `${p(d.getDate())}.${p(d.getMonth() + 1)} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

/**
 * Нормативный радар (EPIC G5) — «Дереккөз тексерісі». Validates our stored
 * reference versions against official sources; «Тексеру» runs a live check
 * (mirror fetch), stale rows offer «Открыть источник» + «Отметить обновлённым».
 * No auto-apply — application is pilot scope.
 */
export default function RadarPanel() {
  const { t, i18n } = useTranslation();
  const kk = (i18n.resolvedLanguage ?? 'kk') === 'kk';
  const [rows, setRows] = useState<RadarRow[] | null>(null);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    api
      .get<RadarResponse>('/radar')
      .then((d) => setRows(d.rows))
      .catch(() => setRows([]));
  }, []);

  const runCheck = async () => {
    if (busy) return;
    setBusy(true);
    try {
      const res = await api.post<RadarCheckResult>('/radar/check');
      setRows(res.rows);
    } catch {
      /* offline / blocked — rows keep their last state, no unhandled rejection */
    } finally {
      setBusy(false);
    }
  };

  const confirm = async (id: string) => {
    try {
      const updated = await api.post<RadarRow>(`/radar/${id}/confirm`);
      setRows((rs) => (rs ? rs.map((r) => (r.source_id === id ? updated : r)) : rs));
    } catch {
      /* ignore — no unhandled rejection */
    }
  };

  return (
    <section className="border border-ink/15">
      <div className="flex items-center justify-between border-b border-ink/15 px-4 py-2">
        <span className="label-micro">{t('radar.title')}</span>
        <button
          type="button"
          onClick={runCheck}
          disabled={busy}
          className="border border-accent px-3 py-1 label-micro text-accent transition-colors duration-150 hover:bg-accent/5 disabled:opacity-40"
        >
          {busy ? t('radar.checking') : t('radar.check')}
        </button>
      </div>

      <div className="overflow-x-auto">
        {!rows ? (
          <div className="fill-dots-faint m-4 h-24 animate-pulse" />
        ) : (
          <table className="w-full border-collapse text-secondary">
            <thead>
              <tr className="border-b border-ink/15 text-left label-micro">
                <th className="px-4 py-2 font-normal">{t('radar.source')}</th>
                <th className="px-4 py-2 font-normal">{t('radar.our_version')}</th>
                <th className="px-4 py-2 font-normal">{t('radar.official_version')}</th>
                <th className="px-4 py-2 font-normal">{t('radar.status')}</th>
                <th className="px-4 py-2 font-normal">{t('radar.actions')}</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.source_id} className="border-b border-ink/[.06] last:border-0">
                  <td className="px-4 py-2.5 text-ink/80">
                    {kk ? r.name_kk : r.name_ru}
                    <span className="ml-2 block label-micro text-ink/40">
                      {t('radar.checked')}: {checkedTime(r.checked_at)}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 font-mono tabular-nums text-ink">
                    {r.our_version}
                  </td>
                  <td className="px-4 py-2.5 font-mono tabular-nums text-ink/70">
                    {r.detected_version ?? '—'}
                  </td>
                  <td className="px-4 py-2.5">
                    <span
                      className={`inline-flex items-center gap-1 label-micro ${STATUS_STYLE[r.status].chip}`}
                    >
                      <span aria-hidden className={`font-mono ${STATUS_STYLE[r.status].dot}`}>
                        {STATUS_STYLE[r.status].glyph}
                      </span>
                      {t(`radar.status_${r.status}`)}
                    </span>
                  </td>
                  <td className="px-4 py-2.5">
                    <div className="flex flex-wrap items-center gap-3">
                      <a
                        href={r.quick_link}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="label-micro text-ink/60 underline decoration-ink/30 underline-offset-2 hover:text-ink"
                      >
                        {t('radar.open_source')}
                      </a>
                      {r.status === 'stale' ? (
                        <button
                          type="button"
                          onClick={() => confirm(r.source_id)}
                          className="border border-ink/40 px-2 py-0.5 label-micro text-ink transition-colors duration-150 hover:bg-ink/[.03]"
                        >
                          {t('radar.mark_updated')}
                        </button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
      <p className="border-t border-ink/15 px-4 py-2 label-micro text-ink/40">
        {t('radar.pilot_note')}
      </p>
    </section>
  );
}
