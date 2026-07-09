"""«Возражение на потенциальный дефект» (P7′ / DF-3, beat 4-5).

Cites the concrete case + its ЕКД code and п. 26 Правил мониторинга (возражение
в 5 рабочих дней; молчание = автоснятие, п. 27). Case figures come from the same
storyline-8 source as GET /objections — no invented numbers.
"""

from __future__ import annotations

from app.services import regs_cite
from app.services.docgen import builder
from app.services.rules_engine import objections
from app.services.rules_engine.objections import Objection
from app.services.textfmt import fmt_date, fmt_tenge

_ADDRESSEE = {
    "ru": "В НАО «Фонд социального медицинского страхования»",
    "kk": "«Әлеуметтік медициналық сақтандыру қоры» КеАҚ-ына",
}
_TITLE = {
    "ru": "ВОЗРАЖЕНИЕ\nна потенциальный дефект (п. 26 Правил мониторинга)",
    "kk": "ҚАРСЫЛЫҚ\nықтимал ақауға (Мониторинг қағидаларының 26-т.)",
}


class CaseNotFoundError(ValueError):
    """No потенциальный дефект matches the requested case_ref."""


def _find(case_ref: str) -> tuple[Objection, str]:
    demo_today, items = objections.list_objections()
    for obj in items:
        if obj.case_ref == case_ref:
            return obj, demo_today.isoformat()
    raise CaseNotFoundError(case_ref)


def _body(obj: Objection, lang: str) -> list[str]:
    name = obj.ekd_name_kk if lang == "kk" else obj.ekd_name_ru
    deadline = fmt_date(obj.deadline_date)
    amount = fmt_tenge(obj.amount_at_stake)
    if lang == "kk":
        return [
            f"Іс №: {obj.case_ref}. БАЖ коды: {obj.ekd_code} — {name}.",
            f"Даулы сома: {amount}. Қарсылық мерзімі: "
            f"{obj.deadline_working_days} жұмыс күні (соңғы күн — {deadline}).",
            "Медициналық ұйым көрсетілген ықтимал ақаумен келіспейді және "
            "растайтын медициналық құжаттама негізінде оны алып тастамауды сұрайды.",
        ]
    return [
        f"Дело №: {obj.case_ref}. Код ЕКД: {obj.ekd_code} — {name}.",
        f"Сумма на риске: {amount}. Срок возражения: "
        f"{obj.deadline_working_days} раб. дн. (последний день — {deadline}).",
        "Медицинская организация не согласна с указанным потенциальным дефектом "
        "и на основании подтверждающей медицинской документации просит не "
        "производить снятие с оплаты.",
    ]


def build(case_ref: str, lang: str) -> bytes:
    """Render the возражение .docx for one case in ru or kk."""
    obj, demo_today = _find(case_ref)
    doc = builder.new_document()
    builder.add_org_header(doc, lang, fmt_date(demo_today))
    builder.add_paragraph(doc, _ADDRESSEE[lang])
    for line in _TITLE[lang].split("\n"):
        builder.add_title(doc, line)
    builder.add_paragraph(doc, "")
    for para in _body(obj, lang):
        builder.add_paragraph(doc, para)
    builder.add_paragraph(doc, "")
    cit = regs_cite.get("objection.deadline")
    builder.add_citation_block(doc, lang, cit.label(lang), cit.snippet_ru)
    builder.add_signature_block(doc, lang)
    builder.add_native_review_footer(doc, lang)
    return builder.render(doc)


def filename(case_ref: str, lang: str) -> str:
    return f"vozrazhenie_{case_ref}_{lang}.docx"
