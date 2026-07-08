'use client';

import CodeChip from '@/components/vedomost/CodeChip';
import DeadlineBox from '@/components/vedomost/DeadlineBox';
import ExecutionBar from '@/components/vedomost/ExecutionBar';
import StampMark from '@/components/vedomost/StampMark';
import VerdictBlock from '@/components/vedomost/VerdictBlock';
import { CANDIDATE_STACKS } from '@/lib/specimenFonts';

/**
 * INTERNAL design-QA page (not in nav, not on the golden path):
 *   §I  — typography specimen gate: 3 candidate stacks side by side, judged
 *          by eye at the lead's gate (any kk-glyph fallback = disqualified);
 *   §II — glyph gate in the APPLIED stack (Literata/Inter/Plex Mono);
 *   §III — QALAM component specimens.
 * Strings here are fixtures, deliberately NOT i18n keys — the gate text and
 * torture string must never be translated.
 */
const HEADLINE = 'Шарттың игерілуі — қаражат жоғалғанға дейін';
const TORTURE = 'ӘҒҚҢӨҰҮҺІ әғқңөұүһі  Сәуле Бақыт дәрігер';
const RU = 'Мониторинг исполнения договора ОСМС/ГОБМП';
const EN = 'Contract execution monitoring — pre-billing firewall';
const NUMBERS = '12 400 000 ₸  ·  14.10.2026  ·  61,4 %';

const APPLIED_FACES: Array<{ label: string; className: string }> = [
  { label: 'Literata 600 · display', className: 'font-display font-semibold' },
  { label: 'Literata 500 · display', className: 'font-display font-medium' },
  { label: 'Inter 400 · ui/body', className: 'font-ui font-normal' },
  { label: 'Inter 500 · ui/body', className: 'font-ui font-medium' },
  { label: 'IBM Plex Mono 400 · figures', className: 'font-mono font-normal' },
];

function isoInDays(days: number): string {
  const d = new Date();
  d.setDate(d.getDate() + days);
  const p = (n: number) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())}`;
}

function SectionTitle({ n, children }: { n: string; children: string }) {
  return (
    <div className="mb-4 flex items-baseline gap-3 border-b border-ink/15 pb-2">
      <span className="label-micro">{n}</span>
      <span className="font-display text-h3 text-ink">{children}</span>
    </div>
  );
}

export default function DesignQaPage() {
  return (
    <div className="space-y-12">
      <h1 className="font-display text-h1 text-ink">Design QA — Qalam</h1>

      {/* §I — candidate typography gate */}
      <section>
        <SectionTitle n="I">Typography gate — pick one stack</SectionTitle>
        <div className="space-y-8">
          {CANDIDATE_STACKS.map((stack) => (
            <div key={stack.id} className="border border-ink/15 p-6">
              <div className="mb-3 flex items-baseline justify-between">
                <span className="label-micro">
                  Stack {stack.id} · {stack.label}
                </span>
                <span className="text-secondary text-ink/50">{stack.note}</span>
              </div>
              <p
                className={stack.displayClass}
                style={{ fontSize: 28, fontWeight: stack.displayWeight, lineHeight: 1.2 }}
              >
                {HEADLINE}
              </p>
              <p className={`${stack.displayClass} mt-2`} style={{ fontSize: 20 }}>
                {TORTURE}
              </p>
              <p className={`${stack.uiClass} mt-3 text-ink/70`} style={{ fontSize: 15 }}>
                {RU}
              </p>
              <p className={`${stack.uiClass} text-ink/70`} style={{ fontSize: 15 }}>
                {EN}
              </p>
              <p className={`${stack.figuresClass} mt-3`} style={{ fontSize: 22 }}>
                {NUMBERS}
              </p>
            </div>
          ))}
        </div>
      </section>

      {/* §II — glyph gate in the applied stack */}
      <section>
        <SectionTitle n="II">Glyph gate — applied stack</SectionTitle>
        <div className="space-y-4 border border-ink/15 p-6">
          {APPLIED_FACES.map((face) => (
            <div key={face.label}>
              <p className="label-micro">{face.label}</p>
              <p className={`${face.className} text-h3`}>{TORTURE}</p>
            </div>
          ))}
          <div>
            <p className="label-micro">Numbers · ₸ (U+20B8)</p>
            <p className="font-mono text-h2">{NUMBERS}</p>
          </div>
        </div>
      </section>

      {/* §III — components */}
      <section>
        <SectionTitle n="III">Components</SectionTitle>
        <div className="space-y-6">
          <VerdictBlock>
            Тәуекел: МРТ көлемі 14.10.2026 таусылады — асыра орындау
          </VerdictBlock>
          <VerdictBlock critical>
            Қарсылық мерзімі: 1 жұмыс күні қалды — үнсіздік автоснятие
          </VerdictBlock>

          <div className="flex flex-wrap items-end gap-10">
            <div className="w-64 space-y-2">
              <p className="label-micro">ExecutionBar · fact 45% / tick 50%</p>
              <ExecutionBar planYear={100} factYtd={45} planYtd={50} />
              <p className="label-micro">fact 60% / forecast 118% / tick 50%</p>
              <ExecutionBar planYear={100} factYtd={60} planYtd={50} forecastYear={118} />
            </div>

            <div className="flex items-end gap-4">
              <DeadlineBox
                deadline={isoInDays(1)}
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
