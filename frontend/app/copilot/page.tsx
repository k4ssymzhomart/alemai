'use client';

import { useRef, useState } from 'react';
import { useTranslation } from 'react-i18next';

import CodeChip from '@/components/vedomost/CodeChip';
import api from '@/lib/api';
import type { CopilotAnswer } from '@/lib/types';

interface Turn {
  question: string;
  answer: CopilotAnswer | null;
  error: boolean;
}

const DEMO_QS = ['q1', 'q13', 'q13b', 'qobj', 'qrec', 'q21'] as const;

/**
 * Screen — Көмекші (copilot, beat 6). Receipt-style dock: the question, then a
 * printed «receipt» of what the SYSTEM computed (tool traces), then the answer
 * with citation chips. Numbers never pass through the LLM — the note says so.
 * Canned mode makes this work with the network off.
 */
export default function CopilotPage() {
  const { t } = useTranslation();
  const [turns, setTurns] = useState<Turn[]>([]);
  const [input, setInput] = useState('');
  const [busy, setBusy] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  const ask = async (question: string) => {
    const q = question.trim();
    if (!q || busy) return;
    setInput('');
    setBusy(true);
    setTurns((ts) => [...ts, { question: q, answer: null, error: false }]);
    try {
      const res = await api.post<CopilotAnswer>('/copilot/ask', {
        question: q,
        // The copilot beat is performed in Kazakh regardless of UI locale (docs/25 H1).
        locale: 'kk',
      });
      setTurns((ts) =>
        ts.map((turn, i) =>
          i === ts.length - 1 ? { ...turn, answer: res } : turn,
        ),
      );
    } catch {
      setTurns((ts) =>
        ts.map((turn, i) =>
          i === ts.length - 1 ? { ...turn, error: true } : turn,
        ),
      );
    } finally {
      setBusy(false);
      requestAnimationFrame(() =>
        endRef.current?.scrollIntoView({ behavior: 'smooth' }),
      );
    }
  };

  return (
    <div className="mx-auto flex h-[calc(100vh-9rem)] max-w-3xl flex-col">
      <div>
        <h1 className="font-display text-h1 text-ink">{t('nav.copilot')}</h1>
        <p className="mt-1 label-micro">{t('copilot.lead')}</p>
      </div>

      <div className="mt-6 flex-1 space-y-6 overflow-y-auto pr-1">
        {turns.length === 0 ? (
          <div className="space-y-3">
            <p className="label-micro">{t('copilot.suggested')}</p>
            <div className="flex flex-col items-start gap-2">
              {DEMO_QS.map((k) => (
                <button
                  key={k}
                  type="button"
                  onClick={() => ask(t(`copilot.q.${k}`))}
                  className="border border-ink/15 px-3 py-1.5 text-left text-secondary text-ink/80 transition-colors duration-150 hover:bg-ink/[.03]"
                >
                  {t(`copilot.q.${k}`)}
                </button>
              ))}
            </div>
          </div>
        ) : (
          turns.map((turn, i) => (
            <TurnView key={i} turn={turn} busyLast={busy && i === turns.length - 1} />
          ))
        )}
        <div ref={endRef} />
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
        className="mt-4 flex items-center gap-2 border-t border-ink/15 pt-4"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder={t('copilot.placeholder')}
          className="flex-1 border border-ink/15 bg-paper px-3 py-2 text-body text-ink outline-none focus:border-ink"
        />
        <button
          type="submit"
          disabled={busy || !input.trim()}
          className="bg-ink px-4 py-2 text-secondary font-medium text-paper transition-opacity duration-150 hover:opacity-80 disabled:opacity-30"
        >
          {t('copilot.send')}
        </button>
      </form>
      <p className="mt-2 label-micro">{t('copilot.note')}</p>
    </div>
  );
}

function TurnView({ turn, busyLast }: { turn: Turn; busyLast: boolean }) {
  const { t } = useTranslation();
  return (
    <div className="space-y-2">
      <div className="flex justify-end">
        <p className="max-w-lg border border-ink/15 bg-ink/[.03] px-3 py-2 text-body text-ink">
          {turn.question}
        </p>
      </div>

      {turn.error ? (
        <p className="text-secondary text-ink/50">{t('common.error')}</p>
      ) : turn.answer ? (
        <div className="border-l-2 border-ink pl-4">
          {turn.answer.tool_traces.length > 0 ? (
            <div className="mb-2 border border-dashed border-ink/20 p-2">
              <p className="label-micro mb-1">{t('copilot.trace')}</p>
              {turn.answer.tool_traces.map((tr, j) => (
                <p key={j} className="font-mono text-micro text-ink/60">
                  › {tr.tool}
                  {tr.result_preview ? ` — ${tr.result_preview}` : ''}
                </p>
              ))}
            </div>
          ) : null}
          <p className="text-body text-ink">{turn.answer.answer}</p>
          {turn.answer.citations.length > 0 ? (
            <div className="mt-2 flex flex-wrap items-center gap-2">
              <span className="label-micro">{t('copilot.sources')}:</span>
              {turn.answer.citations.map((c, j) =>
                c.url ? (
                  <a
                    key={j}
                    href={c.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    title={`${c.doc_title} ${c.doc_number}`}
                  >
                    <CodeChip code={`${c.anchor} · ${c.doc_number}`} />
                  </a>
                ) : (
                  <span key={j} title={`${c.doc_title} ${c.doc_number}`}>
                    <CodeChip code={`${c.anchor} · ${c.doc_number}`} />
                  </span>
                ),
              )}
            </div>
          ) : null}
        </div>
      ) : busyLast ? (
        <p className="animate-pulse font-mono text-secondary text-ink/50">
          {t('copilot.thinking')}
        </p>
      ) : null}
    </div>
  );
}
