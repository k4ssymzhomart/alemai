"""Monthly management report (P7′, kk/ru) — игерілуі, тәуекелдер, снятия.

Aggregate + per-line figures pulled from the semantic layer (docs/16 §5). Kazakh
is the primary language (state reporting); ru supported via the lang param.
"""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.services.docgen import builder
from app.services.docgen.data import (
    MonthlyReportContext,
    care_type_name,
    funding_name,
    get_monthly_report_context,
)
from app.services.textfmt import fmt_pct, fmt_tenge

_RISK_RU: dict[str, str] = {
    "critical_under": "критическое недоосвоение",
    "under_risk": "риск недоосвоения",
    "on_track": "в графике",
    "over_risk": "риск перевыполнения",
    "critical_over": "критическое перевыполнение",
}
_RISK_KK: dict[str, str] = {
    "critical_under": "аса қауіпті игерілмеу",
    "under_risk": "игерілмеу қаупі",
    "on_track": "кестеде",
    "over_risk": "асып кету қаупі",
    "critical_over": "аса қауіпті асып кету",
}
_TITLE = {
    "ru": "ОТЧЁТ\nоб исполнении договора закупа за отчётный период",
    "kk": "ЕСЕП\nсатып алу шартының орындалуы туралы (есепті кезең)",
}
_MONTHS_KK = [
    "", "қаңтар", "ақпан", "наурыз", "сәуір", "мамыр", "маусым",
    "шілде", "тамыз", "қыркүйек", "қазан", "қараша", "желтоқсан",
]
_MONTHS_RU = [
    "", "январь", "февраль", "март", "апрель", "май", "июнь",
    "июль", "август", "сентябрь", "октябрь", "ноябрь", "декабрь",
]


def _period_label(ctx: MonthlyReportContext, lang: str) -> str:
    names = _MONTHS_KK if lang == "kk" else _MONTHS_RU
    name = names[ctx.month] if 1 <= ctx.month <= 12 else str(ctx.month)
    return f"{name} {ctx.year}"


def _execution_rows(ctx: MonthlyReportContext, lang: str) -> list[tuple[str, str]]:
    o = ctx.overview
    forecast = fmt_tenge(o.forecast_amount_year) if o.forecast_amount_year is not None else "—"
    gap = fmt_tenge(o.forecast_gap) if o.forecast_gap is not None else "—"
    if lang == "kk":
        return [
            ("Жылдық жоспар", fmt_tenge(o.plan_amount_year)),
            ("Факт (жыл басынан)", fmt_tenge(o.fact_amount_ytd)),
            ("Игерілуі", fmt_pct(o.execution_pct_ytd)),
            ("Жыл соңына болжам", forecast),
            ("Жоспар мен болжам айырмасы", gap),
        ]
    return [
        ("Годовой план", fmt_tenge(o.plan_amount_year)),
        ("Факт (с начала года)", fmt_tenge(o.fact_amount_ytd)),
        ("Освоение", fmt_pct(o.execution_pct_ytd)),
        ("Прогноз до конца года", forecast),
        ("Разрыв план/прогноз", gap),
    ]


def _removals_rows(ctx: MonthlyReportContext, lang: str) -> list[tuple[str, str]]:
    o = ctx.overview
    if lang == "kk":
        return [
            ("Төлемнен алынды (жыл басынан)", fmt_tenge(o.rejected_amount_ytd)),
            ("Соңғы айда алынды", fmt_tenge(o.rejected_amount_mtd)),
        ]
    return [
        ("Снято с оплаты (с начала года)", fmt_tenge(o.rejected_amount_ytd)),
        ("Снято за последний месяц", fmt_tenge(o.rejected_amount_mtd)),
    ]


def _risk_line(line, lang: str) -> str:  # noqa: ANN001 - LineData
    rc = line.risk_class.value if line.risk_class is not None else "on_track"
    label = (_RISK_KK if lang == "kk" else _RISK_RU).get(rc, rc)
    parts = [care_type_name(line.care_type, lang), funding_name(line.funding_source, lang)]
    if line.service_group:
        parts.append(line.service_group)
    name = " / ".join(parts)
    exec_str = fmt_pct(line.execution_pct_ytd)
    if lang == "kk":
        return f"• {name}: {label} (игерілуі {exec_str})."
    return f"• {name}: {label} (освоение {exec_str})."


def build(session: Session, year: int, month: int, lang: str) -> bytes:
    """Render the monthly management report .docx in ru or kk."""
    ctx = get_monthly_report_context(session, year, month)
    doc = builder.new_document()
    builder.add_org_header(doc, lang, _period_label(ctx, lang))
    for line in _TITLE[lang].split("\n"):
        builder.add_title(doc, line)
    builder.add_paragraph(doc, "")

    h1 = "1. Игерілуі" if lang == "kk" else "1. Исполнение (освоение)"
    builder.add_heading(doc, h1)
    builder.add_kv_table(doc, _execution_rows(ctx, lang))
    builder.add_paragraph(doc, "")

    h2 = "2. Тәуекелдер" if lang == "kk" else "2. Риски"
    builder.add_heading(doc, h2)
    if ctx.risk_lines:
        for line in ctx.risk_lines:
            builder.add_paragraph(doc, _risk_line(line, lang))
    else:
        builder.add_paragraph(
            doc, "Тәуекел анықталмаған." if lang == "kk" else "Риски не выявлены."
        )
    builder.add_paragraph(doc, "")

    h3 = "3. Төлемнен алу (снятия)" if lang == "kk" else "3. Снятия с оплаты"
    builder.add_heading(doc, h3)
    builder.add_kv_table(doc, _removals_rows(ctx, lang))

    builder.add_signature_block(doc, lang)
    builder.add_native_review_footer(doc, lang)
    return builder.render(doc)


def filename(year: int, month: int, lang: str) -> str:
    return f"monthly_report_{year}-{month:02d}_{lang}.docx"
