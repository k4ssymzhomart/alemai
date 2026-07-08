# 15 — DESIGN SYSTEM «ВЕДОМОСТЬ» (B&W BRUTALIST)

Direction chosen and named: **«Ведомость»** — the aesthetics of a state financial ledger: Swiss grid discipline × Kazakh state-document gravitas × terminal precision. White paper, black ink, sharp corners, stamps, mono numbers, running ticker. It photographs beautifully, prints on the poliklinika's laser printer, works for color-blind jurors, and looks like NOTHING else in the room (everyone else: purple gradients and rounded SaaS cards).

Pitch line this buys us: «Интерфейс печатается на чёрно-белом принтере поликлиники без потери смысла — потому что смысл не закодирован цветом.»

---

## 1. Non-negotiables (the lead's directive, codified)

1. Colors: **#000000 and #FFFFFF only.** No hues, ever. Hierarchy comes from: size, weight, inversion (black blocks with white text), borders, and **pattern fills** (hatching/dots — pure black on white). Optical grays permitted ONLY as black at fixed opacities — tokens below — never as gray hex hues.
2. **border-radius: 0 everywhere.** Tailwind `--radius: 0rem`; audit shadcn components (they default rounded) — override in theme.
3. Strong, non-ordinary type (KZ-glyph-safe, see §2). Numbers always in mono.
4. Visual effects: yes, but mechanical/print-inspired (§6) — no glows, no gradients, no springy bounces.
5. Logo: swappable slot (§8). Current wordmark until the lead's logo lands.

## 2. Typography

| Use | Font | Fallback chain |
|---|---|---|
| Display: page titles, verdicts, hero numbers' labels | **Unbounded** (Google Fonts, weights 500/800) | 'Golos Text', 'Inter Tight', system-ui |
| UI/body | **Inter Tight** (400/500/700) | 'Golos Text', system-ui |
| ALL numbers, ₸, dates, timers, tables, codes | **IBM Plex Mono** (400/600) | 'JetBrains Mono', monospace |

**KZ GLYPH GATE (blocking, do before adopting):** render this string in every font+weight in the browser: `ӘҒҚҢӨҰҮҺІ әғқңөұүһі — Игерілмеген қаражат жоғалған қаражат. 12 400 000 ₸` — if Unbounded misses any glyph (know issue: some display faces lack Ә/Ғ/Қ/Ң/Ө/Ұ/Ү/Һ/І), demote it to Latin+digits-only decorative use and promote **Golos Text Black** for kk/ru display. Screenshot the gate result into the PR. Also verify ₸ (U+20B8) in Plex Mono; if missing, use a local @font-face subset or draw ₸ as styled `<span>`.

Type scale (px): 64 (hero number) / 40 (verdict) / 28 (h1) / 20 (h2) / 16 (body) / 14 (table) / 12 (caption, uppercase, letter-spacing 0.08em). Numbers: `font-variant-numeric: tabular-nums`.

## 3. Tokens (CSS)

```css
:root {
  --ink: #000; --paper: #fff;
  --ink-70: rgba(0,0,0,.7);   /* secondary text */
  --ink-40: rgba(0,0,0,.4);   /* disabled, captions */
  --ink-12: rgba(0,0,0,.12);  /* hairline grid, chart gridlines */
  --border-hair: 1px solid var(--ink);
  --border-strong: 2px solid var(--ink);
  --border-heavy: 4px solid var(--ink);
  --shadow-hard: 4px 4px 0 0 var(--ink);      /* offset block shadow, no blur */
  --shadow-hard-sm: 2px 2px 0 0 var(--ink);
  --radius: 0; --space-unit: 8px;
  --font-display: 'Unbounded'; --font-ui: 'Inter Tight'; --font-mono: 'IBM Plex Mono';
}
```

Spacing: strict 8px grid. Page gutter 24. Card padding 16/24. Section dividers: 2px black rules, occasionally full-bleed 8px black bars with white uppercase labels (document-header style: «ІІ. ТӘУЕКЕЛДЕР»).

## 4. Severity without color (the signature system)

SVG pattern fills (defs shared app-wide) + weight + glyph. Never color, never icons-only:

| Level | Fill | Border | Chip | Glyph |
|---|---|---|---|---|
| Критично (крит. недоосвоение/перевыполнение, дефект block) | **solid black**, white text | 4px | inverted `▮ ҚАУІП` | ▲ |
| Риск (warn) | diagonal hatch 45°, 3px step | 2px | hatched `⚠ ТӘУЕКЕЛ`-style text chip (no emoji — use `!`) | ◤ |
| Наблюдение (info/жёлтые дефекты 2.0, 7.0 = 0 ₸) | dot pattern 15% | 1px | dotted chip `· БАҚЫЛАУ` | ● |
| Норма | white | 1px | plain chip `OK` | — |

Progress/execution bars: block characters style — filled black segment, hatched forecast segment, dotted remainder, plan mark as 2px vertical tick. Timers (возражение 5 раб. дней): mono countdown in a bordered box; ≤2 days → inverts to black block (white digits) — the most alarming thing on a B&W screen is a solid black rectangle.

## 5. Components (shadcn/ui as base, restyled; 21st.dev shopping list)

Base: keep shadcn primitives (Table, Dialog, Tabs, Command, Popover, Sheet) — override theme: radius 0, borders 1–2px black, focus ring = 2px offset black outline, no soft shadows anywhere.

**Ask the lead to pull from 21st.dev (names to search; all B&W-compatible):**
1. **Number Ticker / NumberFlow** (magicui) — hero KPIs count up on load; mono font.
2. **Marquee** (magicui) — the top **alert ticker** («БЕГУЩАЯ СТРОКА»): `МРТ: объём иссякнет 14.10 ▮ Возражение по случаю №… — осталось 2 раб. дня ▮ Сверка ЕПС: до 23:59` — exchange-board vibe, pause on hover.
3. **Data Table** (shadcn + TanStack) — the workhorse; sticky header, row hover = invert.
4. **Command / ⌘K palette** (shadcn cmdk) — «перейти к строке МРТ», «сформировать отчёт» — impresses IT-jurors.
5. **Dot Pattern / Grid Pattern background** (magicui) — faint dot grid (ink-12) on empty states and login-less landing.
6. **Typing Animation / Text Reveal** (magicui) — copilot answers typewriter-render with block cursor ▮.
7. **Animated List** (magicui) — alert feed insertions.
8. **Bento Grid** (magicui/aceternity) — director's verdict screen layout (3 цифры / 3 риска / 3 действия).
9. **Scroll Progress** thin black bar — long registers.
10. **Kbd** component — shortcuts on hover.
Skip anything with gradients/glow/3D (Border Beam, Meteors, Globe) — off-brand.

Custom components to build (not on any registry):
- **StampMark** — rotated (-8°) double-border stamp: `СНЯТО С ОПЛАТЫ · КОД 5.1` / `ТӨЛЕМНЕН АЛЫНДЫ`, applied to rejected claims and on the pre-billing verdict; subtle ink-texture via SVG turbulence, black only.
- **VerdictBlock** — full-width black band, white Unbounded text, one sentence.
- **LedgerRow** — table row that expands into passport preview (no navigation surprise).
- **DeadlineBox** — mono countdown, working-days aware, legal citation caption («п. 26 Правил мониторинга»).
- **HatchBar / ExecutionBar** — the plan/fact/forecast bar per §4.
- **CodeChip** — ЕКД/rule codes in mono bordered chips: `5.1`, `R17`.
- **SignatureQueue** — director's подписной центр line items with ✍ box.

## 6. Motion & effects (mechanical, ≤200ms, `prefers-reduced-motion` respected)

- Hover on interactive rows/cards: **full invert** (black↔white) with 120ms steps(2) — feels like a stamp, not a fade.
- Numbers: count-up once on mount (Number Ticker), никогда not on every rerender.
- Page transitions: none (instant, document-like). Section reveals: 1-frame slide of the black bar.
- Copilot: typewriter + blinking ▮ cursor; tool-trace lines print like a receipt.
- Charts draw-in: bars rise with steps(4) easing — dot-matrix printer feel.
- Print stylesheet: @media print — hide nav/ticker, passports print as A4 documents with header/footer (org name, date, page) — hand the jury a printed Паспорт строки. Free wow.

## 7. Charts (ECharts B&W theme `vedomost.ts`)

- Palette: ['#000'] only; series distinguished by **decal patterns** — ECharts native `aria: {enabled: true, decal: {show: true}}` gives hatch/dot/cross decals designed exactly for monochrome; customize decal set: solid, 45° hatch, dots, crosshatch.
- Plan line: dashed 2px black. Fact bars: solid/hatched. Forecast: white bars with dashed border + dotted CI band (area with dot decal at 20%).
- Gridlines ink-12; axis labels Plex Mono 12; no legends with colored dots — legends use pattern swatches (custom legend renderer).
- Burn-out date: vertical 2px line + rotated mono label `14.10.2026 ▲`.
- Tooltips: white, 1px black border, hard shadow, mono numbers. No animations >200ms.

## 8. Logo & brand slot

`components/brand/Logo.tsx`: renders `/public/brand/logo.svg` if present else wordmark `IGERIM▮` (Unbounded 800, tracking tight, the terminal block as brand mark). Enforce monochrome on any uploaded logo: CSS `filter: grayscale(1) contrast(9)`; height 28px in sidebar, 20px in print header. Favicon auto-derived. Settings §Брендинг uploads to that path — **when the lead's own logo arrives, it's a file drop, zero code.** Header layout: [Logo] [Организация: ГП №14 · демо] [ticker] [role switcher] [kk|ru|en].

## 9. Screen redlines (apply pattern §14-doc §0)

- **Overview:** hero band: игерілуі % (64px mono) + ₸ gap + risk count; then ExecutionBar table of lines (LedgerRow); ticker on top. No pie charts, ever.
- **Line Passport:** exactly the 5-block order (Кто я → Вердикт → Почему → Что делать → Данные). Verdict is the only black band on screen.
- **Pre-billing:** verdict header «БЛОКЕРЫ: 12 · 2,1 МЛН ₸ ПОД РИСКОМ», findings grouped, StampMark preview on block-level rows, CodeChips for ЕКД.
- **Возражения:** DeadlineBox column — the wall of countdowns is the screen's drama.
- **Director:** Bento verdict (3/3/3), SignatureQueue, one chart max.
- **City:** 14 rows, normalized bars (сн/1000 прикр.), no map (map = color temptation + time sink).
- **Copilot:** right dock 400px, receipt-style; citations as bordered footnote chips `[п. 4]`.
- **Empty states:** dot-pattern background + one sentence + one button. Never blank.

## 10. Accessibility & quality gates

- Contrast: trivially AAA (pure B&W); focus outline 2px offset — keyboard path through golden demo tested.
- Patterns readable at 100% zoom on the venue projector — test hatch step ≥3px; verify on 1366×768.
- Locale QA: longest-string test (kk labels are long: «Қаржыландыру көзі бойынша игерілуі») — no truncation in nav/chips; numbers `12 400 000 ₸` (NBSP thousands).
- The glyph gate (§2) screenshot attached to design PR.
- Design acceptance = golden path click-through: zero rounded corners (`grep -r 'rounded' frontend/ | grep -v 'rounded-none'` returns nothing unexpected), zero non-B&W colors (`grep -rE '#[0-9a-f]{3,6}' frontend/app frontend/components` whitelist check), print of Line Passport looks like a document.

## 11. Implementation notes for the coding agent

- Tailwind: set full color palette to only ink/paper tokens (no default palette leakage — remove default colors from config to make violations impossible, not just forbidden).
- shadcn theme: radius 0; replace ring/shadow tokens with hard variants.
- ECharts theme file registered once; decals shared.
- Fonts: `next/font/google` (Unbounded, Inter Tight, IBM Plex Mono) with `subsets: ['latin','cyrillic','cyrillic-ext']` — cyrillic-ext is the kk glyph carrier; self-host fallback if venue offline (fonts bundled at build).
- Marquee ticker content = live alerts endpoint (falls back to seeded).
- Do the restyle as ONE packet (PD1) BEFORE building new screens — retrofitting brutalism later costs double.
