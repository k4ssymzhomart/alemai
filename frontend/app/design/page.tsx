'use client';

import CodeChip from '@/components/vedomost/CodeChip';
import DeadlineBox from '@/components/vedomost/DeadlineBox';
import ExecutionBar from '@/components/vedomost/ExecutionBar';
import StampMark from '@/components/vedomost/StampMark';
import VerdictBlock from '@/components/vedomost/VerdictBlock';

/**
 * INTERNAL design-QA page (not in nav, not part of the golden path):
 * §1 — the blocking KZ glyph gate (docs/15 §2) for every font+weight;
 * §2 — «Ведомость» component specimens. Strings here are test fixtures,
 * deliberately NOT i18n keys — the gate text must never be translated.
 */
const GATE =
  'ӘҒҚҢӨҰҮҺІ әғқңөұүһі — Игерілмеген қаражат жоғалған қаражат. 12 400 000 ₸';

const FACES: Array<{ label: string; className: string }> = [
  { label: 'Unbounded 500 (display)', className: 'font-display font-medium' },
  { label: 'Unbounded 800 (display)', className: 'font-display font-extrabold' },
  { label: 'Inter Tight 400 (ui)', className: 'font-ui font-normal' },
  { label: 'Inter Tight 500 (ui)', className: 'font-ui font-medium' },
  { label: 'Inter Tight 700 (ui)', className: 'font-ui font-bold' },
  { label: 'IBM Plex Mono 400 (mono)', className: 'font-mono font-normal' },
  { label: 'IBM Plex Mono 600 (mono)', className: 'font-mono font-semibold' },
];

function isoInDays(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

export default function DesignQaPage() {
  return (
    <div className="space-y-8">
      <h1 className="font-display text-h1 font-medium uppercase tracking-tight">
        Design QA — «Ведомость»
      </h1>

      <section className="border-2 border-ink">
        <div className="border-b-2 border-ink bg-ink px-4 py-1.5 font-mono text-caption uppercase text-paper">
          I. KZ glyph gate (docs/15 §2)
        </div>
        <div className="space-y-4 p-4">
          {FACES.map((face) => (
            <div key={face.label}>
              <p className="font-mono text-caption uppercase text-ink/40">
                {face.label}
              </p>
              <p className={`${face.className} text-lg`}>{GATE}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="border-2 border-ink">
        <div className="border-b-2 border-ink bg-ink px-4 py-1.5 font-mono text-caption uppercase text-paper">
          II. Components
        </div>
        <div className="space-y-6 p-4">
          <VerdictBlock>ҚАУІП: асыра орындау — объём закончится 14.10.2026</VerdictBlock>

          <div className="flex flex-wrap items-end gap-8">
            <div className="w-64 space-y-2">
              <p className="font-mono text-caption uppercase text-ink/40">
                ExecutionBar: fact 45% / plan-tick 50%
              </p>
              <ExecutionBar planYear={100} factYtd={45} planYtd={50} />
              <p className="font-mono text-caption uppercase text-ink/40">
                fact 60% / forecast 118% / tick 50%
              </p>
              <ExecutionBar planYear={100} factYtd={60} planYtd={50} forecastYear={118} />
            </div>

            <div className="flex items-end gap-4">
              <DeadlineBox
                deadline={isoInDays(2)}
                citation="п. 26 Правил мониторинга"
                label="Возражение"
              />
              <DeadlineBox
                deadline={isoInDays(9)}
                citation="п. 69 Правил оплаты"
                label="ЕПС"
              />
            </div>

            <div className="flex items-center gap-3">
              <CodeChip code="5.1" />
              <CodeChip code="R17" />
              <StampMark text="Төлемнен алынды · код 5.1" />
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}
