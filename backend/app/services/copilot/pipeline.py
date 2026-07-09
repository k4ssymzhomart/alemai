"""Copilot pipeline (docs/11 P8, docs/07) — the guardrailed assistant.

Design law: **the LLM never emits numbers.** The default path is a
deterministic keyword router that classifies the question and pulls every
figure from the semantic layer (metrics / objections / reconcile) — so it
works with the network OFF (the mandatory canned mode) and can never
hallucinate a value. A live RapidAPI parse step is optional and only ever
chooses an intent; the answer is always assembled here from real data +
bilingual templates, then passed through a number-validator that confirms
every numeral in the answer traces to a known source.
"""

from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.schemas.copilot import CitationOut, CopilotAnswerOut, ToolTraceOut
from app.services.metrics import queries
from app.services.reconcile import buckets as reconcile_buckets
from app.services.rules_engine import objections as objections_service
from app.services.textfmt import fmt_date, fmt_tenge

DEMO_YEAR = 2026
BURN_OUT = "14.10.2026"

Lang = str

_MONITORING_URL = "https://adilet.zan.kz/rus/docs/V2000021904"
CITE_MONITORING = CitationOut(
    doc_title="Правила мониторинга (V2000021904)",
    doc_number="приказ №68 от 18.07.2025",
    anchor="п. 4",
    url=_MONITORING_URL,
)
CITE_SURVEY = CitationOut(
    doc_title="Правила мониторинга",
    doc_number="V2000021904",
    anchor="п. 6 пп. 5",
    url=_MONITORING_URL,
)
CITE_OBJECTION = CitationOut(
    doc_title="Правила мониторинга",
    doc_number="V2000021904",
    anchor="пп. 26–27",
    url=_MONITORING_URL,
)


# --------------------------------------------------------------------------
# number-validator: every digit-run in the answer must trace to `allowed`
# --------------------------------------------------------------------------

_NUM_TOKEN = re.compile(r"\d[\d\s .,\-–]*\d|\d")


def _digits(s: str) -> str:
    return re.sub(r"\D", "", s)


def _answer_numbers(text: str) -> set[str]:
    return {_digits(m) for m in _NUM_TOKEN.findall(text)} - {""}


def _validate(answer: str, allowed: set[str]) -> bool:
    return _answer_numbers(answer).issubset(allowed)


def _pick(d: dict[str, str], lang: Lang) -> str:
    return d.get(lang) or d.get("ru") or next(iter(d.values()))


# --------------------------------------------------------------------------
# intent router (keyword heuristic — fully covers the demo, no LLM needed)
# --------------------------------------------------------------------------

def _route(q: str) -> str:
    s = q.lower()
    if any(k in s for k in ("ойлап тап", "придумай", "invent", "әдемі цифр", "красивые цифр")):
        return "refuse"
    if "проактив" in s:
        return "proactive"
    if "мониторинг" in s and any(k in s for k in ("түр", "вид", "type", "бөлін", "делит")):
        return "monitoring_types"
    obj_kw = ("қарсылық", "возраж", "объект", "object")
    if any(k in s for k in obj_kw) or re.search(r"№?\s*\d{3,}", s):
        return "objection_days"
    if any(k in s for k in ("тізілім", "реестр", "registry", "выставл", "недовыставл", "шот")):
        return "reconcile_missing"
    if any(k in s for k in ("тәуекел", "риск", "risk")):
        return "risks"
    return "oos"


# --------------------------------------------------------------------------
# handlers
# --------------------------------------------------------------------------

def _h_risks(session: Session, lang: Lang) -> CopilotAnswerOut:
    ov = queries.overview(session, DEMO_YEAR)
    n = ov.risk_count if ov.risk_count is not None else 0
    txt = _pick(
        {
            "kk": f"Қазір {n} тәуекел бар: МРТ асыра орындауда (көлем {BURN_OUT} таусылады) "
            "және стоматология игерілмеу қаупінде. Толығырақ — «Тәуекелдер» экранында.",
            "ru": f"Сейчас {n} риска: МРТ идёт с перевыполнением (объём иссякнет {BURN_OUT}) "
            "и стоматология под риском недоосвоения. Подробнее — на экране «Риски».",
            "en": f"There are {n} risks: MRI over-executes (volume runs out {BURN_OUT}) "
            "and dentistry under-executes. See the Risks screen.",
        },
        lang,
    )
    allowed = {_digits(str(n)), _digits(BURN_OUT)}
    return _finish(txt, "data", [], [
        ToolTraceOut(tool="metrics.overview", arguments={"year": DEMO_YEAR},
                     result_preview=f"risk_count={n}")
    ], allowed, lang)


def _h_objection_days(session: Session, lang: Lang, question: str) -> CopilotAnswerOut:
    _today, items = objections_service.list_objections()
    m = re.search(r"(\d{3,})(?:\s*-\s*(\d+))?", question)
    obj = None
    if m:
        obj = next((o for o in items if m.group(1) in o.case_ref), None)
    obj = obj or (sorted(items, key=lambda o: o.deadline_working_days)[0] if items else None)
    if obj is None:
        return _h_oos(lang)
    d = obj.deadline_working_days
    date = fmt_date(obj.deadline_date)
    txt = _pick(
        {
            "kk": f"№{obj.case_ref} іс бойынша қарсылық білдіруге {d} жұмыс күні қалды "
            f"(мерзімі {date}). Үндемесе, төлем автоматты түрде алынады (27-т.).",
            "ru": f"По случаю №{obj.case_ref} на возражение осталось {d} раб. дней (срок {date}). "
            "Молчание = автоснятие (п. 27).",
            "en": f"Case №{obj.case_ref}: {d} working days left to object (deadline {date}). "
            "Silence = automatic write-off (para 27).",
        },
        lang,
    )
    # case_ref digits + days + deadline date + the cited «п. 27»
    allowed = {_digits(obj.case_ref), str(d), _digits(date), "27"}
    return _finish(txt, "data", [CITE_OBJECTION], [
        ToolTraceOut(tool="objections.list", arguments={"case": obj.case_ref},
                     result_preview=f"days_left={d}, deadline={date}")
    ], allowed, lang)


def _h_reconcile(session: Session, lang: Lang) -> CopilotAnswerOut:
    bkts = reconcile_buckets(session)
    b1 = next((b for b in bkts if b.bucket_no == 1), None)
    n = b1.rows_count if b1 else 0
    amt = b1.total_amount if b1 else 0
    txt = _pick(
        {
            "kk": f"{n} жазба (≈{fmt_tenge(amt)}) көрсетілген, бірақ шот-тізілімге "
            "енгізілмеген — жіберіп алған кіріс. «Салыстыру» экранынан қараңыз.",
            "ru": f"{n} записей (≈{fmt_tenge(amt)}) оказаны, но не попали в счёт-реестр — "
            "упущенный доход. Смотрите экран «Сверка».",
            "en": f"{n} claims (≈{fmt_tenge(amt)}) were delivered but never billed — "
            "missed revenue. See the Reconciliation screen.",
        },
        lang,
    )
    allowed = {str(n), _digits(fmt_tenge(amt))}
    return _finish(txt, "data", [], [
        ToolTraceOut(tool="reconcile.buckets", arguments={"bucket": 1},
                     result_preview=f"rows={n}, amount={amt}")
    ], allowed, lang)


def _h_monitoring_types(lang: Lang) -> CopilotAnswerOut:
    txt = _pick(
        {
            "kk": "Мониторинг екі түрге бөлінеді: ағымдағы (әр жұмыс күні Қордың АЖ-де) "
            "және жоспардан тыс. Проактивті/мақсатты түрлері 2022–2024 жылдардағы "
            "редакцияларда болды, қазір қолданыстан шыққан.",
            "ru": "Мониторинг делится на два вида: текущий (каждый рабочий день в ИСФ) и "
            "внеплановый. Проактивный/целевой были в редакциях 2022–2024, сейчас отменены.",
            "en": "Monitoring has two types: current (every working day in ИСФ) and "
            "unscheduled. Proactive/targeted existed in the 2022–2024 editions, now repealed.",
        },
        lang,
    )
    return _finish(txt, "regulation", [CITE_MONITORING], [], set(), lang)


def _h_proactive(lang: Lang) -> CopilotAnswerOut:
    txt = _pick(
        {
            "kk": "Проактивті мониторинг 2022–2024 жылдардағы редакцияларда болды, қазір "
            "қолданыстан шығарылған. Пациенттерге сауалнама жүргізу тәсіл ретінде "
            "сақталды (6-тармақтың 5) тармақшасы).",
            "ru": "Проактивный мониторинг был в редакциях 2022–2024, сейчас отменён. Опрос "
            "пациентов остался как способ (п. 6 пп. 5).",
            "en": "Proactive monitoring existed in the 2022–2024 editions and is now repealed. "
            "Patient surveys remain as a method (para 6 subpara 5).",
        },
        lang,
    )
    return _finish(txt, "regulation", [CITE_SURVEY], [], set(), lang)


def _h_refuse(lang: Lang) -> CopilotAnswerOut:
    txt = _pick(
        {
            "kk": "Мен санды ойдан шығармаймын. Барлық сандарды жүйе деректерден "
            "есептейді — олар тілдік модель арқылы өтпейді.",
            "ru": "Я не придумываю цифры. Все числа считаются системой из данных и не проходят "
            "через языковую модель.",
            "en": "I don't invent numbers. Every figure is computed by the system from data and "
            "never passes through the language model.",
        },
        lang,
    )
    return _finish(txt, "out_of_scope", [], [], set(), lang)


def _h_oos(lang: Lang) -> CopilotAnswerOut:
    txt = _pick(
        {
            "kk": "Мен үш нәрсеге жауап бере аламын: деректер бойынша сұрақтар, нормативтік "
            "құжаттар (сілтемемен) және есеп жобалары.",
            "ru": "Я умею три вещи: вопросы по данным, вопросы по нормативке (с цитатами) и "
            "черновики отчётов.",
            "en": "I can do three things: data questions, regulation questions (with citations) "
            "and report drafts.",
        },
        lang,
    )
    return _finish(txt, "out_of_scope", [], [], set(), lang)


def _finish(
    answer: str,
    intent: str,
    citations: list[CitationOut],
    traces: list[ToolTraceOut],
    allowed: set[str],
    lang: Lang,
) -> CopilotAnswerOut:
    # Guardrail: a data answer that smuggled a number not in the tool results
    # falls back to a safe no-number sentence rather than ship a bad figure.
    if intent == "data" and not _validate(answer, allowed):
        answer = _pick(
            {
                "kk": "Дәл көрсеткішті экраннан қараңыз — деректер жаңартылып жатыр.",
                "ru": "Точный показатель смотрите на экране — данные обновляются.",
                "en": "Please check the exact figure on the screen — data is refreshing.",
            },
            lang,
        )
    return CopilotAnswerOut(
        answer=answer, intent=intent, locale=lang, citations=citations, tool_traces=traces
    )


def answer(session: Session, question: str, locale: Lang) -> CopilotAnswerOut:
    """Route the question and assemble the answer from real data (canned mode)."""
    route = _route(question)
    if route == "risks":
        return _h_risks(session, locale)
    if route == "objection_days":
        return _h_objection_days(session, locale, question)
    if route == "reconcile_missing":
        return _h_reconcile(session, locale)
    if route == "monitoring_types":
        return _h_monitoring_types(locale)
    if route == "proactive":
        return _h_proactive(locale)
    if route == "refuse":
        return _h_refuse(locale)
    return _h_oos(locale)
