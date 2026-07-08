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

## From Epic B (F2 forecast/risk explanations, 2026-07-09)

Seeded into `forecasts.explanation` / `risk_assessments.recommendation` (JSON `{ru,kk}`) by `datagen/generate.py`. All kk agent-written — review before the demo.

| key | kk | ru | confidence | question |
|---|---|---|---|---|
| forecast.mri | МРТ жоспардан асып орындалуда; ағымдағы қарқында жылдық көлем ≈14.10.2026 таусылады. | МРТ идёт с превышением плана; при текущем темпе годовой объём будет исчерпан ≈14.10.2026. | medium | «таусылады» vs «игеріліп бітеді» for burn-out |
| forecast.dent | Стоматология қарқынның 71%-ымен орындалуда — жыл соңына игерілмеу қаупі. | Стоматология исполняется на 71% темпа — риск недоосвоения к концу года. | medium | «игерілмеу» for недоосвоение correct? |
| forecast.pmsp | МСАК жан басына шаққандағы норматив бойынша төленеді; игеру кестеде. | ПМСП оплачивается по подушевому нормативу; освоение в графике. | medium | «жан басына шаққандағы норматив» = подушевой норматив (КПН)? |
| forecast.baseline | Ағымдағы қарқын бойынша болжам (run-rate); желі кестеде. | Прогноз по текущему темпу (run-rate); линия в графике. | medium | «желі кестеде» for "line on track"? |
| rec.mri | Сатып алу қағидаларының 19-т. 25)/26) тармақшалары бойынша қосымша көлем орналастыру. | Разместить доп. объёмы по пп. 25)/26) п. 19 Правил закупа. | medium | legal citation phrasing in kk |
| rec.dent | Кадр тапшылығын тексеру; шарт бойынша игерілмеу қаупі. | Проверить кадровый дефицит; риск недоосвоения по договору. | medium | «кадр тапшылығы» natural? |
| rec.none | Әрекет қажет емес. | Действий не требуется. | high | — |
