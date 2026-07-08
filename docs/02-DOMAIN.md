# 02 — DOMAIN PRIMER: OSMS/GOBMP CONTRACTS & MONITORING

Purpose: give every team member enough domain fluency to design correctly and survive jury Q&A. Terms are given as RU (КЗ) since data and regulations use them. Glossary in §10. Items marked ⚠️VERIFY must be re-checked against current rules / mentors at the hackathon — regulations change frequently and 2026 amendments are fresh.

---

## 1. The two packages and the 2026 reform

- **ГОБМП (ТМККК — тегін медициналық көмектің кепілдік берілген көлемі)** — guaranteed volume of free medical care for **everyone** regardless of insurance status. Budget-funded. Core: скорая помощь, ПМСП, socially significant diseases, emergencies, vaccination; **from 01.01.2026 also onco-screenings for all**.
- **ОСМС (МӘМС — міндетті әлеуметтік медициналық сақтандыру)** — insurance package for the **insured** (contributors + state-paid exempt categories). Funded via ФСМС from payroll contributions and state transfers. Core: КДУ by referral, planned hospitalization, day hospital, rehabilitation, some dentistry/drugs.
- **Единый пакет (reform, Law №206-VIII of 14.07.2025, in force 01.01.2026):** services redistributed between packages. **25 chronic diseases moved to the OSMS package** (diabetes ~414k patients, ДЦП ~26k, rheumatism ~13k); onco-screenings → ГОБМП; diagnostics for suspected socially-significant diseases available to all regardless of status; ~1M additional insured expected. **Consequence for us:** the ГОБМП/ОСМС source attribution of a claim now depends on diagnosis + patient insurance status + date, per the new mapping — a fresh, high-value automation target (rule R17 in 06-DATA-ANALYTICS §7).
- Insurance status of a patient is checked against Fund systems (статус застрахованности). Uninsured → only ГОБМП scope. ⚠️VERIFY current status-check API/exports available in the MedHub sandbox.

## 2. The money flow (single-payer model)

```
Взносы работодателей/работников + госвзносы за 15 льготных категорий
        │                                   │
        ▼                                   ▼
   ФСМС (единый плательщик; с дек.2025 под контролем Минфина) ◄── республиканский бюджет (ГОБМП)
        │  договоры закупа услуг (годовые, с помесячными объёмами)
        ▼
   Поставщики (поликлиники, стационары, частные центры)
        │  ежемесячные счета-реестры за пролеченные случаи/услуги
        ▼
   ФЛК → автоматизированный мониторинг → экспертиза → оплата (минус снятия/штрафы по ЕКД)
```

Scale 2026 (per Fund chair Гульмира Сабденбек, May 2026 interview): **≈3.4 трлн ₸ total (≈1.7T ГОБМП + 1.7T ОСМС)**; earlier press (Dec 2025) cited 2.7 трлн planned purchases — use the chair's fresher figure, cite the interview. Fund contested **38 млрд ₸** of billed services in 2025 monitoring, 8 млрд in early 2026. Status: НАО «ФСМС», name unchanged, **under Ministry of Finance management since 16.01.2026** (audit fallout); chair Сабденбек since 23.01.2026; antifraud platform **Qalqan** piloted 16.03.2026 (see 16-RESEARCH-INTEGRATION C9 for our positioning).

## 3. Contract lifecycle (Правила закупа — приказ МЗ РК, adilet V2000021744 ⚠️VERIFY current redaction)

1. **Планирование объёмов** — regional health administrations + Fund plan volumes per care type.
2. **Выбор поставщиков** — providers apply via Fund portal; commission selects.
3. **Заключение договора** — annual «договор закупа медицинских услуг» with annexes: line items = вид помощи × источник финансирования (ГОБМП/ОСМС) × месяц, in natural units (случаи, услуги, прикреплённые) and ₸.
4. **Исполнение** — monthly billing, monitoring, and **корректировка объёмов**: the Fund periodically redistributes volumes based on actual execution (freeing money from under-executors, adding to over-executors); provider submits **заявка** through the portal; changes formalized as **доп. соглашения**. Deadlines are windows — miss one, wait for the next period. ⚠️VERIFY current корректировка windows/dates with mentors — this drives our deadline calendar (F1).

**Contract structure a polyclinic typically has (our data model must handle):** ПМСП (подушевой), КДУ/КДП (fee-for-service by tariff), стационарозамещающая помощь (дневной стационар, за пролеченный случай), стоматология (отдельные категории), скрининги, вакцинация, патронаж; sometimes стационар if merged org. Multiple amendments per year — versioning is mandatory in our schema.

## 4. Payment methods per care type (Правила оплаты — приказ №ҚР ДСМ-291/2020, adilet V2000021831 ⚠️VERIFY)

| Care type | Payment method | Key variables |
|---|---|---|
| ПМСП | **Подушевой норматив (КПН)**: прикреплённое население × норматив × половозрастной поправочный коэффициент (ПВК) | attachment registry accuracy = money; monthly recalc |
| КДУ (консультативно-диагностические услуги) | Fee-for-service по тарификатору, **по направлению** | tariff codes, referral validity — top defect zone |
| Круглосуточный стационар | **КЗГ (клинико-затратные группы)** — DRG-like, за пролеченный случай | coding of diagnosis/complexity drives ₸ |
| Дневной стационар (стационарозамещающая) | За пролеченный случай | length/completeness rules |
| Скорая/неотложная | Per norms/calls | — |
| Screenings/programs | Per service, target-group gated | sex/age eligibility — the 2025 audit disaster zone |

Exact 2026 КПН value: treat as **config parameter** (calibrate from real data; don't hardcode).

## 5. The monthly billing & monitoring cycle (the heart of our product)

1. Clinic renders services; MIS (Damumed etc.) records cases; data flows to national systems (ЭРСБ — стационар registry, АПП portal — outpatient, etc.).
2. Monthly the clinic forms **счёт-реестр** (invoice + case registry) to the Fund.
3. Fund runs **ФЛК** (форматно-логический контроль) → rejections for format errors.
4. **Мониторинг исполнения договора** (Правила — приказ №ҚР ДСМ-321/2020, adilet V2000021904; полная новая редакция — приказ №68 от 18.07.2025 (V2500036470), точечные правки + новый ЕКД — приказ №19 от 27.02.2026 (V2600038088)). **CORRECTED per research: only TWO types now — текущий (каждый рабочий день в ИСФ, п. 21) and внеплановый (triggers п. 51, incl. обращение самого поставщика о доп. объёме).** Проактивный/целевой existed in 2022–2024 redactions and are GONE; patient polling survives as a *method* (п. 6 пп. 5). Defects classify as общие (no money impact) / потенциальные / дополнительные; the Fund's algorithms are **classified** (п. 15 — служебная информация).
5. Confirmed defects → **снятие с оплаты**: auto-reduced via ИСФ per **ЕКД — «Единый классификатор дефектов и нарушений», Приложение 1 к Правилам МОНИТОРИНГА** (not оплаты; Правила оплаты п. 4 only reference it). Key АПП sanctions (ред. №19): **5.0/5.1 неподтверждённый случай (приписка) = 100 КПН / 300% стоимости**; 1.0 = 20 КПН/100%; 12.0 (платно за ГОБМП/ОСМС-услугу) = 50 КПН/100%; **2.0 (документация) и 7.0 (ожидание >15 раб. дней) = 0 ₸** — фиксируются без снятия. Отдельно: неустойка (условия договора; без лицензии = 10% суммы договора), возврат средств за скрытые недостатки (≤6 мес., п. 53-1).
6. **Возражения (пп. 26–38): 5 раб. дней на возражение в ИСФ; молчание = дефект подтверждён и деньги сняты автоматически (п. 27); повторное возражение — 3 раб. дня; заключение внепланового мониторинга — подписать за 3 раб. дня.** Критично: **п. 24 — после присвоения дефекта корректировки в МИС не принимаются** → защита возможна только ДО подачи счёта. Пороги эскалации: неподтверждённые случаи >200 МРП/мес → материалы в правоохранительные органы (п. 19); повторность → расторжение договора (п. 20); совокупно >800 МРП — то же. Обжалование вне Фонда — госорган в сфере оказания медуслуг (п. 60).

**Known scale of the problem (use in pitch, sourced):** Fund experts reported **882k+ defects** found in monitoring (Ashuev, ФСМС); **28k unconfirmed cases (приписки) worth 214.2 mln ₸, 99% in outpatient care**; Dec-2025 Minfin IT-audit: 769,446 sex-mismatched screenings (~1.8 bn ₸), 3,640 services to 996 deceased patients, 68,717 child drug приписки. On 18.12.2025 the government transferred ФСМС under Minfin control.

## 6. The clinic's three loss channels (our product = one per pillar)

1. **Недоосвоение (under-execution):** actual < plan → money not earned, clawed back at корректировка, and next-year volumes cut. Politically painful (год-end "release of funds" reviews).
2. **Перевыполнение (over-execution):** services above contracted volume are **not paid** («сверхдоговорные объёмы»). The clinic literally works for free unless it wins a volume increase at корректировка — which requires noticing the trend early and filing the заявка before the window closes.
3. **Дефекты/снятия:** every rejected case is earned-but-lost revenue + fine risk + reputational risk (приписки make national news).

Plus a hidden fourth: **недовыставление** — services recorded in MIS but never billed (human error in registry formation). Nobody watches this; автосверка МИС↔выставлено↔оплачено finds it. Easy demo "wow."

## 7. Who does this work today (as-is)

- **Экономист** (planning/finance): keeps contract annexes + amendments in Excel; monthly план/факт by hand; prepares заявки на корректировку; answers to главврач and the health administration.
- **Статистик / мед. информатика:** forms счёт-реестр from MIS exports, fights ФЛК rejections, re-submits.
- **Зам. главврача по лечебной работе:** answers for volumes and quality; needs early warning, not post-mortems.
- **Главврач:** monthly reporting upward (управление здравоохранения, Fund), in Kazakh and Russian.
- Tools: MIS exports → Excel → manual reconciliation vs Fund portal statements. Cycle time: days. Error rate: human.

## 8. IT landscape (integration story)

- **МИС:** Damumed dominates Astana ambulatory care (⚠️VERIFY at №14); others: iSalem/Salem, АИС Поликлиника, private MIS in private clinics.
- **National systems:** ЕИСЗ ecosystem operated around МЗ РК / РЦЭЗ: ЭРСБ (stationary cases), АПП portal (outpatient), РПН (прикреплённое население registry), drug systems; Fund portal for contracts/счета/statements.
- **Practical hackathon posture:** we ingest **exports** (CSV/XLSX/XML) via adapters + the MedHub sandbox dataset; live API integration is a pilot-phase promise, not a demo claim. Ask mentors day-1: exact export formats available from №14 (see 06-DATA-ANALYTICS §2 triage protocol).

## 9. Regulatory corpus for the copilot RAG (fetch onsite, adilet.zan.kz)

1. Правила закупа услуг (V2000021744) — contracting, корректировка.
2. Правила оплаты услуг (V2000021831, №ҚР ДСМ-291/2020) — payment methods, ЕКД annexes.
3. Правила мониторинга исполнения договора (V2000021904, №ҚР ДСМ-321/2020 + 2025 amendment V2500036470) — monitoring types, procedures.
4. Закон №206-VIII от 14.07.2025 — the 2026 reform.
5. Кодекс «О здоровье народа и системе здравоохранения» (base definitions).
6. Тарификатор (current) + КЗГ справочник. ⚠️Get machine-readable versions via mentors/MedHub.

Kazakh versions exist for all (adilet has kk/ru) → **bilingual RAG corpus for free** — feeds pillar SPEAK.

## 10. Glossary (KZ / RU / EN) — also the copilot terminology source of truth

| KZ | RU | EN / meaning |
|---|---|---|
| ТМККК | ГОБМП | Guaranteed volume of free care |
| МӘМС | ОСМС | Mandatory social health insurance |
| Әлеуметтік медициналық сақтандыру қоры (ӘМСҚ) | ФСМС / Фонд | Social Health Insurance Fund (single payer) |
| шарт | договор закупа | procurement contract |
| қосымша келісім | доп. соглашение | contract amendment |
| көлемдерді түзету | корректировка объёмов | volume adjustment |
| өтінім | заявка | application/request |
| шот-тізілім | счёт-реестр | invoice-registry of cases |
| игеру / игерілуі | освоение | utilization/execution of contracted funds |
| игерілмеу | недоосвоение | under-execution |
| асыра орындау | перевыполнение | over-execution |
| ақаулар | дефекты | defects |
| төлемнен алу | снятие с оплаты | payment deduction/removal |
| айыппұл санкциялары | штрафные санкции | penalties |
| жазба қосу / қосып жазу | приписки | false claims (unconfirmed services) |
| бекітілген халық | прикреплённое население | attached population |
| жан басына шаққандағы норматив (ЖБШН) | подушевой норматив (КПН) | per-capita rate |
| жынысы-жасы бойынша түзету коэффициенті | половозрастной поправочный коэффициент (ПВК) | sex-age adjustment coefficient |
| МСАК | ПМСП | primary healthcare (PHC) |
| КДҚ (консультациялық-диагностикалық қызметтер) | КДУ | consultative-diagnostic services |
| жолдама | направление | referral |
| КШТ (клиникалық-шығындық топтар) | КЗГ | clinical-cost groups (DRG analog) |
| тәуліктік стационар | круглосуточный стационар | inpatient hospital |
| күндізгі стационар | дневной стационар | day hospital |
| скринингтер | скрининги | screenings |
| сақтандыру мәртебесі | статус застрахованности | insurance status |
| Бірыңғай ақаулар жіктеуіші (БАЖ) | ЕКД (Единый классификатор дефектов) | Unified defect classifier |
| ФЛК | ФЛК | format-logic control (schema validation) |
| ағымдағы мониторинг | текущий мониторинг | current monitoring |
| проактивті мониторинг | проактивный мониторинг | proactive monitoring |
| Бірыңғай пакет | Единый пакет | Unified package (2026 reform) |
| болжам | прогноз | forecast |
| тәуекел | риск | risk |
| есеп | отчёт | report |

## 11. Sources

- Reform 2026: [zakon.kz — ОСМС-2026](https://www.zakon.kz/obshestvo/6502128-osms2026-chto-izmenitsya-dlya-kazakhstantsev.html), [tengrinews — главные изменения](https://tengrinews.kz/tengri-health/article/osms-kazaxstane-glavnye-izmeneniia-medstraxovanii-2026-godu-3538/), [pharmreviews — пакеты ГОБМП и ОСМС, обзор](https://pharmreviews.kz/stati/sobytiya/pakety-gobmp-i-osms-obzor-izmenenij), [mgdb-3.kz](https://www.mgdb-3.kz/index.php/ru/novosti/564-vazhnye-izmeneniya-v-sisteme-osms-s-1-yanvarya-2026-goda)
- Monitoring rules: [adilet V2000021904](https://adilet.zan.kz/rus/docs/V2000021904), [2025 amendment V2500036470](https://adilet.zan.kz/rus/docs/V2500036470); закуп: [adilet V2000021744](https://adilet.zan.kz/rus/docs/V2000021744); оплата/ЕКД: [adilet V2000021831](https://adilet.zan.kz/rus/docs/V2000021831)
- Defect/приписки scale: [msqory.kz — 882 тыс. дефектов (Ашуев)](https://msqory.kz/ru/eshche/press-tsentr/novosti/bolee-882-tys-defektov-bylo-vyyavleno-ekspertami-fsms-pri-provedenii-monitoringa-aydyn-ashuev/), [24.kz — 23 тыс. приписок на 208 млн ₸](https://24.kz/ru/news/social/item/683181-falshivye-meduslugi-23-tysyachi-pripisok-na-208-mln-vyyavili-v-kazakhstane)
- Dec-2025 ФСМС→Минфин + audit findings: [kt.kz](https://www.kt.kz/rus/state/pripiski_dvoynoe_finansirovanie_i_uslugi_umershim_fsms_1377986548.html), [pkzsk.info](https://pkzsk.info/fsms-peredadut-na-kontrol-minfina-rk-pravitelstvo-vyyavilo-mnogo-narushenijj-v-finansirovanii-medorganizacijj/), [azattyq-ruhy](https://rus.azattyq-ruhy.kz/news/101356-iz-za-mnozhestva-narushenii-fsms-peredadut-v-minfin-kazakhstana)
- Budget 2026: [lada.kz — 2.7 трлн ₸](https://www.lada.kz/kazakhstan-news/149910-skolko-deneg-fsms-kazakhstana-potratit-na-zdorove-zhitelei-v-2026-godu.html), [tengrinews — по регионам](https://tengrinews.kz/tengri-health/skolko-deneg-fsms-potratit-meduslugi-raznyih-regionah-593332/)
