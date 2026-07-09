# NEEDS-NATIVE-REVIEW — accumulating kk queue

> **REVIEW APPLIED 2026-07-09** (Epic E §1, delegated to the coder; `shared/glossary.csv`
> as law). Calques and glossary violations fixed across the demo-critical strings — the
> 6 copilot canned answers, verdict/objection strings, and the обращение kk letter.
> Key fixes: «проактивный/целевой» → «проактивті/мақсатты»; «ЕКД» → «БАЖ» (kk label);
> «сверка» → «салыстыру»; contract line «желі» → «жол»; «п. 27» → «27-т.»; Fund → ӘМСҚ
> (already correct). Full change list in the Epic E report. Lead spot-checks the 6 spoken
> copilot answers at rehearsal.

All agent-written Kazakh strings queue here (key | kk | ru | confidence | question).

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

## From Epic C backend (rules engine + reconcile + objections, 2026-07-09)

Rule `message_kk` in `backend/rules/catalog.yaml`, reconcile bucket titles in
`backend/app/services/reconcile/__init__.py`, and the short ЕКД `name_kk` in
`backend/app/services/rules_engine/ekd.py` (the long forms in
`docs/research/ekd_codes.csv` are CONFIRMED; these are shortened UI labels). All
kk agent-written — review before the demo.

| key | kk | ru | confidence | question |
|---|---|---|---|---|
| rule.R01 | Қызмет пациент қайтыс болған күннен кейін көрсетілген — расталмаған жағдай | Услуга оказана после даты смерти пациента — неподтверждённый случай | medium | «расталмаған жағдай» = неподтверждённый случай ok? |
| rule.R02 | Қызмет пациенттің жынысына сәйкес келмейді — жағдай расталмайды | Услуга несовместима с полом пациента — случай не может быть подтверждён | medium | — |
| rule.R03 | Скрининг мақсатты жас тобынан тыс — негізсіз көрсету | Скрининг вне целевой возрастной группы — необоснованное оказание | medium | «мақсатты жас тобы» natural for целевая возрастная группа? |
| rule.R04 | Қайталанатын қызмет (бір пациент, қызмет және күн) — қосарлау | Дублирующая услуга (тот же пациент, услуга и дата) — задвоение | medium | «қосарлау» for задвоение? |
| rule.R07 | КДУ жолдамасыз көрсетілген — негізділігін тексеру қажет | КДУ оказана без направления — требует проверки обоснованности | medium | «жолдама» = направление ok? |
| rule.R10 | Дәрігердің тәуліктік жүктемесі шындыққа жанаспайды — орындалмайтын көлем | Нереальная суточная нагрузка врача — физически неоказуемый объём | low | natural kk for «физически неоказуемый объём»? |
| rule.R11 | Дәрігердің бір айдағы демалыс күндердегі қызмет саны аномальды — кестені тексеру | Аномальное число услуг врача в выходные за месяц — требует проверки графика | medium | phrasing of «аномальный» in kk |
| rule.R13 | 30 күн ішінде қайта емдеуге жатқызу — негізсіз (паллиативтен басқа) | Повторная госпитализация в течение 30 дней — необоснованная (кроме паллиатива) | medium | «қайта емдеуге жатқызу» = повторная госпитализация? |
| rule.R16 | МӘМС бойынша қызмет сақтандырылмаған пациентке көрсетілген | Услуга по ОСМС оказана незастрахованному пациенту | high | — |
| rule.R17 | Диабет (E10–E14) ТМККК-ке қойылған — 2026 жылдан көзі МӘМС (ЗПДН) | Диабет (E10–E14) выставлен на ГОБМП — с 2026 источник ОСМС (ЗПДН) | medium | «көзі» for источник финансирования ok? |
| rule.R18 | Айлық қызмет еселігі негізсіз асқан — санды негізсіз ұлғайту | Превышена разумная кратность услуги за месяц — необоснованное увеличение | low | «еселік» = кратность? |
| rule.R20 | Бір кезеңде пациентке қайталанған скрининг — кезеңділіктен тыс | Повторный скрининг пациенту в том же периоде — вне периодичности | medium | «кезеңділік» = периодичность? |
| rule.R25 | Диагноз жоқ (АХЖ-10) — құжаттаманы ресімдеу ақауы | Отсутствует диагноз (МКБ-10) — дефект оформления документации | medium | «АХЖ-10» correct kk abbr for МКБ-10? |
| recon.bucket1 | Көрсетілген, бірақ шот қойылмаған | Оказано, но не выставлено | medium | «шот қойылмаған» for «не выставлено»? |
| recon.bucket2 | Шот қойылған, бірақ алынып тасталды | Выставлено, но снято | medium | «алынып тасталды» for «снято»? |
| recon.bucket3 | Қабылданған, бірақ төленбеген | Принято, но не оплачено | high | — |
| recon.bucket4 | Сәйкес келеді (төленген) | Совпадает (оплачено) | high | — |

## From Epic D (copilot canned answers + docgen + screens, 2026-07-09)

**Highest priority — the copilot answers are SPOKEN/SHOWN at the pitch (beat 6).**
Copilot templates live in `backend/app/services/copilot/pipeline.py`; docgen kk
in `backend/app/services/docgen/*.py`; screen labels in `frontend/locales/kk.json`
(namespaces `copilot.* prebilling.* objections.* reconcile.* sev.* passport.*
verdict.* action.* settings.*`). All kk agent/coordinator-written.

| key | kk | ru | confidence | question |
|---|---|---|---|---|
| cp.q1_risks | Қазір {n} тәуекел бар: МРТ асыра орындауда (көлем 14.10.2026 таусылады) және стоматология игерілмеу қаупінде. Толығырақ — «Тәуекелдер» экранында. | Сейчас {n} риска: МРТ с перевыполнением (объём иссякнет 14.10.2026) и стоматология под риском недоосвоения. Подробнее — на экране «Риски». | medium | «асыра орындауда»/«игерілмеу қаупінде» natural? |
| cp.q13_types | Мониторинг екі түрге бөлінеді: ағымдағы (әр жұмыс күні ИСФ-те) және жоспардан тыс. Проактивный/целевой түрлері 2022–2024 редакцияларда болған, қазір жоқ. | Мониторинг делится на два вида: текущий (каждый рабочий день в ИСФ) и внеплановый. Проактивный/целевой были в редакциях 2022–2024, отменены. | medium | «жоспардан тыс» = внеплановый; keep ru «проактивный/целевой» or translate? |
| cp.q13b_proactive | Проактивный мониторинг 2022–2024 жылдардағы редакцияларда болды, қазір жойылған. Пациенттерге сауалнама тәсіл ретінде қалды (п. 6 пп. 5). | Проактивный мониторинг был в редакциях 2022–2024, отменён. Опрос пациентов остался как способ (п. 6 пп. 5). | medium | «сауалнама тәсіл ретінде қалды» phrasing |
| cp.q_obj | №{case} іс бойынша қарсылыққа {d} жұмыс күні қалды (мерзім {date}). Үнсіздік — автоматты түрде алып тастау (п. 27). | По случаю №{case} на возражение осталось {d} раб. дней (срок {date}). Молчание = автоснятие (п. 27). | medium | «автоматты түрде алып тастау» for автоснятие |
| cp.q_rec | {n} жазба (≈{amt}) көрсетілген, бірақ шот-тізілімге енгізілмеген — жоғалған кіріс. «Салыстыру» экранынан қараңыз. | {n} записей (≈{amt}) оказаны, но не попали в счёт-реестр — упущенный доход. Смотрите «Сверку». | medium | «жоғалған кіріс» = упущенный доход? |
| cp.q21_refuse | Мен ойдан цифр құрастырмаймын. Барлық сандар жүйеде деректерден есептеледі — тілдік модель арқылы өтпейді. | Я не придумываю цифры. Все числа считаются системой из данных и не проходят через языковую модель. | medium | tone ok for a refusal? |
| cp.note | Цифрлар тілдік модель арқылы өтпейді — оларды жүйе есептейді | Цифры не проходят через языковую модель — их считает система | high | the pitch's key line — must be crisp kk |
| prebilling.verdict_block | БЛОКЕРЛЕР: {count} позиция · {amount} тәуекел астында | БЛОКЕРЫ: {count} позиций · {amount} под риском | high | «тәуекел астында» = под риском |
| objections.silence | Үнсіздік = автоматты түрде алып тастау (п. 27) | Молчание = автоснятие (п. 27) | medium | — |
| settings.ref_ekd | ЕКД (Мониторинг қағидаларының 1-қосымшасы) | ЕКД (Приложение 1 Правил мониторинга) | high | official kk name of «Правила мониторинга»? |
| docgen.obrashenie_kk | (see backend/app/services/docgen/obrashenie.py — full letter body kk) | — | low | full-letter native review before printing for the jury |

<!-- EPIC G (2026-07-09) — glossary law applied; these are the calque-prone ones -->
| radar.title | Дереккөз тексерісі (нормативтік радар) | Проверка источников (нормативный радар) | medium | «нормативтік радар» is a coined term — confirm reads naturally |
| ops.live_note | Санақтар оқиғалар бойынша нақты уақытта жаңарады | Счётчики обновляются в реальном времени по событиям | medium | «нақты уақытта» (real-time) — calque; ok? |
| ops.sanctions_prevented | Алдын алынған санкциялар | Предотвращено санкций | medium | «алдын алынған» = предотвращённый — confirm |
| reports.note | Барлық сандарды жүйе есептейді — тілдік модель емес | Все числа считает система — не языковая модель | high | echoes the pitch line; must be crisp |
| radar.status_stale | жаңасы бар | доступна новее | low | terse chip label |
| auth.error | Қате логин немесе құпиясөз | Неверный логин или пароль | low | «логин» loanword — acceptable |
