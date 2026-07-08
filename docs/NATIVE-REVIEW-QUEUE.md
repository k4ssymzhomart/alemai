# NEEDS-NATIVE-REVIEW — accumulating kk queue

All agent-written Kazakh strings queue here; presented to the lead in the Epic D batch (key | kk | ru | confidence | question). Rows are removed once approved.

## From P2 (Overview/drill UI, 2026-07-08)

All 70 base UI keys in `frontend/locales/kk.json` were agent-written; spot-check at minimum: `overview.*`, `drilldown.*`, `risk.class.*`, `care_type.*`.

## From Epic A (PD1 reskin, 2026-07-09)

| key | kk | ru | confidence | question |
|---|---|---|---|---|
| app.org | №14 қалалық емхана · демо | ГП №14 · демо | high | official kk short form of «ГП №14»? |
| common.demo_badge | демо-деректер | демо-данные | high | — |
| common.go_overview | Шолуға өту | К обзору | high | — |
| ticker.label | Ескертулер таспасы | Лента предупреждений | medium | natural kk for "alert ticker"? |
| ticker.objection_rule | Қарсылыққа — 5 жұмыс күні · үнсіздік = автоматты түрде алып тастау (Мониторинг қағидалары, 26–27-т.) | Возражение — 5 раб. дней · молчание = автоснятие (пп. 26–27 Правил мониторинга) | medium | legal phrasing of «автоснятие» in kk; «Мониторинг қағидалары» vs official title |
| ticker.eps_deadline | ЕПС: дербестендірілген деректер — есепті кезеңнен кейін 3 жұмыс күнінен кешіктірмей (Төлеу қағидалары, 69-т.) | ЕПС: передача персонифицированных данных — не позднее 3 раб. дней после отчётного периода (п. 69 Правил оплаты) | medium | «дербестендірілген» vs «дербес» for персонифицированные |
| overview.table.execution_bar | Игерілу барысы | Ход исполнения | high | — |
| deadline.days_left | қалды: {{count}} жұм. күні | осталось раб. дней: {{count}} | medium | abbreviation «жұм. күні» acceptable in UI? |
| deadline.expired | мерзім өтті | срок истёк | high | — |
