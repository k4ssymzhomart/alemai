"""ЕКД — Единый классификатор дефектов и нарушений (code table + sanctions).

Source of truth: ``docs/research/ekd_codes.csv`` + ``ekd_notes.md`` §2-§4
(CONFIRMED). The ЕКД is Приложение 1 к Правилам мониторинга (приказ ҚР
ДСМ-321/2020, V2000021904) — NOT the Правила оплаты.

Editions our synthetic period (2024-07…2026-06) crosses (ekd_notes.md §2):
  - ред. № 68 (приказ 18.07.2025) — 29 кодов, включая 1.3.
  - ред. № 19 (приказ 27.02.2026, рег. 03.03.2026) — 28 кодов; 1.3 исключён.

The edition applied to a defect is chosen by the claim's service date. Codes
2.0 (документация) and 7.0 (ожидание > 15 раб. дней) carry кратность 0 by every
column — «жёлтые»: фиксируется без снятия (ekd_notes.md §3).

Sanction mechanics (ekd_notes.md §3): the снятие base differs by care type —
КДУ/скрининг/стационар = % of service (case) cost; АПП/ПМСП = кратность
подушевого норматива (КПН/ПН), which is NOT a % of the service tariff. We
therefore compute a ₸ sanction only for cost-priced care types and expose the
ПМСП penalty as a descriptor string (no fabricated ₸ — «no number the system
didn't compute»).
"""

from __future__ import annotations

import datetime
import re
from dataclasses import dataclass

# Ред. № 19 в силе через 10 кал. дней после первого офиц. опубликования
# (рег. 03.03.2026) → оценка 2026-03-14 (ekd_notes.md §2 + mentor-question #4).
EDITION_19_EFFECTIVE = datetime.date(2026, 3, 14)

# Finding-level source (EPIC G5): the ЕКД is Приложение 1 к Правилам мониторинга
# (приказ ҚР ДСМ-321/2020, V2000021904). Every ЕКД finding links here.
EKD_SOURCE_URL = "https://adilet.zan.kz/rus/docs/V2000021904"
EKD_SOURCE_LABEL = "ЕКД — прил. 1 к Правилам мониторинга (приказ ҚР ДСМ-321/2020)"

# Care types priced per service/case (снятие = % стоимости). ПМСП is подушевик.
_COST_PRICED = frozenset({"kdu", "day_hosp", "hosp", "dent", "screening", "ambulance"})


@dataclass(frozen=True, slots=True)
class EkdCode:
    """One ЕКД row, reduced to what the rules engine needs to compute money."""

    code: str
    name_ru: str
    name_kk: str
    significance: str  # "значительное" | "не значительное"
    # Fraction of service/case cost removed for cost-priced care (КДУ/стационар).
    # None where the code applies only to the ПМСП подушевик column.
    cost_multiplier: float | None
    # Human descriptor of the ПМСП/АПП penalty column (КПН/ПН) — no ₸ derived.
    app_penalty: str | None
    yellow: bool = False  # кратность 0 (2.0/7.0) — фиксируется без снятия
    removed_after_ed19: bool = False  # 1.3 — исключён с ред. № 19


# Subset of the classifier actually referenced by rules/*.yaml. Multipliers are
# the КДУ column (amb_kdu_pct) from ekd_codes.csv; app_penalty is the АПП column.
_CODES: dict[str, EkdCode] = {
    "1.0": EkdCode("1.0", "Необоснованное оказание медицинской помощи",
                   "Медициналық көмекті негізсіз көрсету", "значительное", 1.0, "20 КПН/ПН"),
    "1.2": EkdCode("1.2", "Необоснованное направление/оказание КДУ",
                   "Консультациялық-диагностикалық қызметтерге негізсіз жіберу/көрсету",
                   "значительное", 1.0, "20 КПН/ПН"),
    "1.3": EkdCode("1.3", "Отсутствие документов разрешительного порядка",
                   "Рұқсат беру тәртібіндегі құжаттардың болмауы", "значительное", 1.0,
                   "20 КПН/ПН", removed_after_ed19=True),
    "2.0": EkdCode("2.0", "Дефекты оформления медицинской документации",
                   "Медициналық құжаттаманы ресімдеу ақаулары", "не значительное", 0.0, "0",
                   yellow=True),
    "3.0": EkdCode("3.0", "Необоснованное завышение объёма услуги",
                   "Көрсетілген қызмет көлемін негізсіз асыру", "значительное", 1.0, "10 КПН/ПН"),
    "3.1": EkdCode("3.1", "Необоснованное увеличение количества услуг",
                   "Қызметтер санын негізсіз ұлғайту", "значительное", 1.0, "10 КПН/ПН"),
    "4.0": EkdCode("4.0", "Необоснованная повторная госпитализация (30 кал. дней)",
                   "Негізсіз қайта емдеуге жатқызу (күнтізбелік 30 күн)", "значительное", 1.0,
                   None),
    "5.0": EkdCode("5.0", "Неподтверждённый случай оказания услуг",
                   "Медициналық көмек көрсетудің расталмаған жағдайы", "значительное", 3.0,
                   "100 КПН/ПН"),
    "5.1": EkdCode("5.1", "Включение в счёт-реестр неподтверждённого случая",
                   "Расталмаған жағдайды шот-тіркелімге қосу", "значительное", 3.0, "100 КПН/ПН"),
    "5.2": EkdCode("5.2", "Прикрепление к ПМСП без согласия потребителя",
                   "Тұтынушының келісімінсіз МСАК-қа бекіту", "значительное", None, "100 КПН/ПН"),
    "6.2": EkdCode("6.2", "Несоблюдение НПА при оказании помощи",
                   "Көмек көрсету кезінде НҚА сақтамау", "значительное", 0.3, "5 КПН/ПН"),
    "7.0": EkdCode("7.0", "Длительность ожидания услуг более 15 рабочих дней",
                   "Қызметтерді күту ұзақтығы 15 жұмыс күнінен асады", "не значительное", 0.0, "0",
                   yellow=True),
    "11.0": EkdCode("11.0", "Услуги, не включённые в договор закупа",
                    "Сатып алу шартына енгізілмеген қызметтер", "значительное", 1.0, "30 КПН/ПН"),
    "12.0": EkdCode("12.0", "Оказание платно услуг, входящих в ГОБМП/ОСМС",
                    "ТМККК/МӘМС қызметтерін ақылы көрсету", "значительное", 1.0, "50 КПН/ПН"),
}


def get(code: str) -> EkdCode:
    """Look up a ЕКД code; raises KeyError for an unknown code (catalog bug)."""
    return _CODES[code]


def edition_for(claim_date: datetime.date) -> str:
    """Which ЕКД edition governs a defect on ``claim_date`` (ekd_notes.md §2)."""
    return "№19" if claim_date >= EDITION_19_EFFECTIVE else "№68"


def is_active(code: str, claim_date: datetime.date) -> bool:
    """False only for 1.3 on/after the ред. № 19 cut-over (archived code)."""
    ekd = _CODES[code]
    if ekd.removed_after_ed19 and claim_date >= EDITION_19_EFFECTIVE:
        return False
    return True


def sanction_amount(code: str, care_type: str, billed: int) -> int | None:
    """Potential снятие in ₸ for a cost-priced claim; None for ПМСП (КПН base).

    ``billed`` is the claim's предъявлено amount (qty × tariff). Returns
    ``billed × cost_multiplier`` for КДУ/стационар/скрининг; None for ПМСП or
    for codes without a cost column (we do not fabricate a КПН ₸ value).
    """
    ekd = _CODES[code]
    if care_type not in _COST_PRICED or ekd.cost_multiplier is None:
        return None
    return int(round(billed * ekd.cost_multiplier))


def kpn_multiple(code: str) -> int:
    """Leading integer of the АПП column («100 КПН/ПН» → 100); 0 if none/yellow."""
    ekd = _CODES[code]
    if ekd.yellow or not ekd.app_penalty:
        return 0
    m = re.match(r"\d+", ekd.app_penalty)
    return int(m.group()) if m else 0


def sanction_total(code: str, care_type: str, billed: int, kpn_tenge: int) -> int:
    """Full penalty exposure per finding, ₸: снятие (% стоимости, cost-priced) +
    the АПП fine (кратность подушевого норматива × КПН). E.g. код 5.1 on a
    cost-priced service = 300 % × billed + 100 × КПН. Yellow codes = 0."""
    ekd = _CODES[code]
    if ekd.yellow:
        return 0
    cost_part = sanction_amount(code, care_type, billed) or 0
    kpn_part = kpn_multiple(code) * kpn_tenge
    return cost_part + kpn_part


def descriptor(
    code: str, care_type: str, billed: int, claim_date: datetime.date
) -> dict[str, object]:
    """Full ЕКД evidence blob stored in ``Finding.details`` (bilingual + sanction)."""
    ekd = _CODES[code]
    edition = edition_for(claim_date)
    sanction = sanction_amount(code, care_type, billed)
    if ekd.yellow:
        sanction_ru = f"код {code} — фиксируется без снятия (0 ₸, {ekd.significance} нарушение)"
    elif sanction is not None:
        pct = int(round(ekd.cost_multiplier * 100)) if ekd.cost_multiplier is not None else 0
        sanction_ru = f"код {code} — снятие {pct}% стоимости ({sanction:,} ₸)".replace(",", " ")
    else:
        sanction_ru = f"код {code} — снятие {ekd.app_penalty} (ПМСП, подушевой норматив)"
    return {
        "ekd_code": code,
        "ekd_edition": edition,
        "ekd_name_ru": ekd.name_ru,
        "ekd_name_kk": ekd.name_kk,
        "significance": ekd.significance,
        "yellow": ekd.yellow,
        "cost_multiplier": ekd.cost_multiplier,
        "app_penalty": ekd.app_penalty,
        "sanction_amount": sanction,
        "sanction_ru": sanction_ru,
        # Finding-level source link (EPIC G5): «покажите, откуда это правило».
        "source_url": EKD_SOURCE_URL,
        "source_label": EKD_SOURCE_LABEL,
    }
