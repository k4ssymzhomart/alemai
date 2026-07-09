"""«Обращение в Фонд о размещении дополнительных объёмов» (P7′, beat 3 ACT).

Real mechanism = п. 19 Правил закупа (ред. №99 от 26.09.2025), NOT a «заявка на
корректировку» (docs/16 §1 C6). Two grounds computed from live data:
  пп. 25) — остаток средств по виду помощи + свободный остаток плана;
  пп. 26) — факт-превышение по данным сверки (виды без линейной шкалы).
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.services import regs_cite
from app.services.docgen import builder
from app.services.docgen.data import (
    ObrashenieContext,
    care_type_name,
    funding_name,
    get_obrashenie_context,
)
from app.services.textfmt import fmt_date, fmt_pct, fmt_tenge

_ADDRESSEE = {
    "ru": "В НАО «Фонд социального медицинского страхования»",
    "kk": "«Әлеуметтік медициналық сақтандыру қоры» КеАҚ-ына",
}
_TITLE = {
    "ru": (
        "ОБРАЩЕНИЕ\nо размещении дополнительных объёмов медицинских услуг\n"
        "(пп. 25)/26) п. 19 Правил закупа)"
    ),
    "kk": (
        "ӨТІНІШ\nмедициналық қызметтердің қосымша көлемін орналастыру туралы\n"
        "(Сатып алу қағидалары 19-т. 25)/26) тармақшалары)"
    ),
}


def _line_label(ctx: ObrashenieContext, lang: str) -> str:
    line = ctx.line
    parts = [care_type_name(line.care_type, lang), funding_name(line.funding_source, lang)]
    if line.service_group:
        parts.append(line.service_group)
    return " / ".join(parts)


def _intro(ctx: ObrashenieContext, lang: str, label: str) -> str:
    exec_str = fmt_pct(ctx.line.execution_pct_ytd)
    if lang == "kk":
        return (
            f"{ctx.year} жылғы сатып алу шарты бойынша «{label}» жолында игерілу "
            f"жоспарланғаннан жоғары қарқынмен жүруде (ағымдағы игерілу — {exec_str}). "
            "Ағымдағы қарқын сақталса, жылдық көлем мерзімінен бұрын таусылады."
        )
    return (
        f"По договору закупа {ctx.year} года по линии «{label}» исполнение идёт с "
        f"превышением планового темпа (текущее исполнение — {exec_str}). При "
        "сохранении темпа годовой объём будет исчерпан до конца периода."
    )


def _rows(ctx: ObrashenieContext, lang: str) -> list[tuple[str, str]]:
    line = ctx.line
    as_of = fmt_date(f"{ctx.as_of}-01") if ctx.as_of else "—"
    forecast = (
        fmt_tenge(line.forecast_amount_year)
        if line.forecast_amount_year is not None
        else "—"
    )
    if lang == "kk":
        return [
            (f"Жоспар ({ctx.year} ж.)", fmt_tenge(line.plan_amount_year)),
            (f"Факт (есеп: {as_of})", fmt_tenge(line.fact_amount_ytd)),
            ("Жыл соңына болжам", forecast),
            ("Жоспардан асу болжамы (26-тш.)", fmt_tenge(ctx.fact_over_plan)),
            ("Шарт бойынша бос қаражат қалдығы (25-тш.)", fmt_tenge(ctx.free_remainder)),
            ("Сұралатын қосымша көлем", fmt_tenge(ctx.requested_amount)),
        ]
    return [
        (f"План ({ctx.year} г.)", fmt_tenge(line.plan_amount_year)),
        (f"Факт (на {as_of})", fmt_tenge(line.fact_amount_ytd)),
        ("Прогноз до конца года", forecast),
        ("Прогнозное превышение плана (пп. 26)", fmt_tenge(ctx.fact_over_plan)),
        ("Свободный остаток средств по договору (пп. 25)", fmt_tenge(ctx.free_remainder)),
        ("Запрашиваемый дополнительный объём", fmt_tenge(ctx.requested_amount)),
    ]


def _grounds(ctx: ObrashenieContext, lang: str) -> list[str]:
    over = fmt_tenge(ctx.fact_over_plan)
    rem = fmt_tenge(ctx.free_remainder)
    if lang == "kk":
        return [
            f"Негіз 26-тш.: салыстыру деректері бойынша факт-жоспардан асу — {over}.",
            f"Негіз 25-тш.: шарт бойынша бос қаражат қалдығы — {rem} "
            "(қайта бөлу көзі).",
        ]
    return [
        f"Основание пп. 26): факт-превышение плана по данным сверки — {over}.",
        f"Основание пп. 25): свободный остаток средств по договору — {rem} "
        "(источник перераспределения).",
    ]


def _request(ctx: ObrashenieContext, lang: str, label: str) -> str:
    amount = fmt_tenge(ctx.requested_amount)
    if lang == "kk":
        return (
            f"Жоғарыда көрсетілген негіздер бойынша «{label}» жолы бойынша "
            f"{amount} сомасына қосымша көлем орналастыруды (қосымша келісім жасауды) "
            "сұраймыз."
        )
    return (
        f"На указанных основаниях просим разместить дополнительный объём по линии "
        f"«{label}» на сумму {amount} (заключить дополнительное соглашение к "
        "договору закупа)."
    )


def build(session: Session, line_key: str, lang: str) -> bytes:
    """Render the обращение .docx for one line in ru or kk."""
    ctx = get_obrashenie_context(session, line_key)
    label = _line_label(ctx, lang)
    date_str = fmt_date(f"{ctx.as_of}-09") if ctx.as_of else fmt_date("2026-07-09")

    doc = builder.new_document()
    builder.add_org_header(doc, lang, date_str)
    builder.add_paragraph(doc, _ADDRESSEE[lang])
    for line in _TITLE[lang].split("\n"):
        builder.add_title(doc, line)
    builder.add_paragraph(doc, "")
    builder.add_paragraph(doc, _intro(ctx, lang, label))
    builder.add_kv_table(doc, _rows(ctx, lang))
    builder.add_paragraph(doc, "")
    for ground in _grounds(ctx, lang):
        builder.add_paragraph(doc, ground)
    builder.add_paragraph(doc, "")
    builder.add_paragraph(doc, _request(ctx, lang, label))
    builder.add_paragraph(doc, "")
    cit = regs_cite.get("zakup.p19")
    builder.add_citation_block(doc, lang, cit.label(lang), cit.snippet_ru)
    builder.add_signature_block(doc, lang)
    builder.add_native_review_footer(doc, lang)
    return builder.render(doc)


def filename(lang: str) -> str:
    return f"obrashenie_p19_{lang}.docx"
