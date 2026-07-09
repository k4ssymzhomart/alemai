"""Curated regulation citations (Epic D) — verbatim snippets + пункт labels.

Why curated (not live pgvector RAG): the ``api`` container mounts only
``/datagen`` and ``/shared`` — the reg corpus at ``docs/research/regs/`` is NOT
mounted, so these snippets are baked into the image to guarantee the exact
citation text on stage. ``copilot/regs.py`` still keyword-searches the full
corpus when its files are reachable (host / eval runner); this table is the
primary, demo-safe matcher and the single source for the docgen citations.

Every snippet is a trimmed verbatim excerpt from docs/research/regs/ (line
references in comments) or a research-confirmed statement from
docs/16-RESEARCH-INTEGRATION.md §1 (corrections C1/C6/C7). Kazakh labels are
agent-written → NEEDS-NATIVE-REVIEW (see docs/NATIVE-REVIEW-QUEUE.md). Reg
snippet text is kept in Russian (the authoritative published language); the
copilot's own prose answers in the question's language.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class Citation:
    id: str
    label_ru: str
    label_kk: str
    snippet_ru: str
    keywords: tuple[str, ...] = field(default_factory=tuple)

    def label(self, lang: str) -> str:
        return self.label_kk if lang == "kk" else self.label_ru


CITATIONS: dict[str, Citation] = {
    # docs/research/regs/monitoring_amendment_2025.ru.txt L85-90, L158 (C1).
    "monitoring.types": Citation(
        id="monitoring.types",
        label_ru="п. 4 Правил мониторинга (ред. приказа №68 от 18.07.2025)",
        label_kk="Мониторинг қағидаларының 4-тармағы (№68 бұйрық редакциясы, 18.07.2025)",
        snippet_ru=(
            "4. Мониторинг исполнения условий договора закупа включает следующие виды "
            "мониторинга: 1) текущий; 2) внеплановый. Текущий мониторинг осуществляется "
            "на постоянной основе в ИСФ."
        ),
        keywords=(
            "мониторинг", "түрлер", "виды", "бөлін", "какие виды", "текущий",
            "внеплановый", "ағымдағы", "жоспардан тыс", "monitoring",
        ),
    ),
    # docs/16 §1 C1: проактивный/целевой отменены; опрос пациентов остался.
    "monitoring.proactive_repealed": Citation(
        id="monitoring.proactive_repealed",
        label_ru="Правила мониторинга — сравнение редакций 2022–2024 (ред. №68)",
        label_kk="Мониторинг қағидалары — 2022–2024 редакциялар салыстыруы (№68)",
        snippet_ru=(
            "Проактивный и целевой мониторинг существовали в редакциях 2022–2024 годов "
            "и были отменены. Опрос пациентов сохранён как способ мониторинга "
            "(п. 6 подпункт 5)."
        ),
        keywords=(
            "проактивн", "целев", "отмен", "убрали", "остался", "опрос пациент",
            "проактивті", "мақсатты",
        ),
    ),
    # docs/16 §1 C7 (Правила мониторинга ҚР ДСМ-321/2020, пп. 26–27).
    "objection.deadline": Citation(
        id="objection.deadline",
        label_ru="пп. 26–27 Правил мониторинга (приказ ҚР ДСМ-321/2020)",
        label_kk="Мониторинг қағидаларының 26–27-тармақшалары (ҚР ДСМ-321/2020 бұйрық)",
        snippet_ru=(
            "Возражение на потенциальный дефект подаётся в ИСФ в течение 5 рабочих "
            "дней (п. 26); при отсутствии возражения в установленный срок дефект "
            "считается подтверждённым — молчание = автоснятие (п. 27). Повторное "
            "возражение — 3 рабочих дня."
        ),
        keywords=(
            "возраз", "оспор", "срок", "дней осталось", "автоснятие", "молчание",
            "қарсылық", "мерзім", "5 раб", "объекция",
        ),
    ),
    # docs/research/regs/pravila_zakupa.ru.txt L227,277,279 (C6, ред. №99).
    "zakup.p19": Citation(
        id="zakup.p19",
        label_ru="пп. 25)/26) п. 19 Правил закупа (ред. приказа №99 от 26.09.2025)",
        label_kk="Сатып алу қағидалары 19-т. 25)/26) тармақшалары (№99 бұйрық, 26.09.2025)",
        snippet_ru=(
            "19. Объём услуг и (или) средств размещается без проведения процедуры "
            "выбора субъектов здравоохранения в рамках плана закупа: 25) на "
            "увеличение объёмов услуг при наличии остатка средств по соответствующему "
            "виду медицинской помощи и свободного остатка объёмов в плане закупа; "
            "26) в случае увеличения фактического исполнения объёма услуг на "
            "основании данных сверки — по видам помощи без линейной шкалы оценки "
            "исполнения (за исключением ВТМП)."
        ),
        keywords=(
            "размещени", "дополнительн", "объ", "остаток средств", "превышени",
            "п. 19", "п.19", "закуп", "корректиров", "орналастыру",
        ),
    ),
    # docs/research/regs/pravila_monitoringa.ru.txt (ЕКД, Прил. 1) + Правила оплаты.
    "removal.ekd": Citation(
        id="removal.ekd",
        label_ru="ЕКД (Приложение 1 к Правилам мониторинга) + Правила оплаты (п. 4)",
        label_kk="БАЖ (Мониторинг қағидаларына 1-қосымша) + Төлеу қағидалары (4-т.)",
        snippet_ru=(
            "Снятие с оплаты производится по кодам Единого классификатора дефектов "
            "и нарушений (ЕКД); степень снижения оплаты зависит от значимости "
            "дефекта (значительное / незначительное). Коды 2.0 и 7.0 фиксируются "
            "без снятия (0 ₸)."
        ),
        keywords=(
            "снимают с оплаты", "на основании", "снятие", "почему сняли", "екд",
            "дефект", "төлемнен ал", "негізде",
        ),
    ),
    # docs/research/regs/pravila_zakupa.ru.txt (п. 19; доп. соглашение).
    "amendment.def": Citation(
        id="amendment.def",
        label_ru="п. 19 Правил закупа (дополнительное соглашение)",
        label_kk="Сатып алу қағидаларының 19-тармағы (қосымша келісім)",
        snippet_ru=(
            "Дополнительное соглашение (қосымша келісім) — соглашение к договору "
            "закупа, изменяющее объёмы услуг и (или) средств без процедуры выбора "
            "субъектов здравоохранения (размещение по п. 19, протокол по прил. 1-1)."
        ),
        keywords=(
            "қосымша келісім", "дополнительное соглашение", "доп. соглашение",
            "что такое доп", "деген не",
        ),
    ),
    # docs/research/regs/pravila_zakupa.ru.txt L118-135 (этапы закупа).
    "zakup.stages": Citation(
        id="zakup.stages",
        label_ru="Правила закупа (глава 1, порядок закупа услуг)",
        label_kk="Сатып алу қағидалары (1-тарау, қызметтерді сатып алу тәртібі)",
        snippet_ru=(
            "Закуп услуг включает этапы: 1) формирование плана закупа; 2) выбор "
            "субъектов здравоохранения; 3) распределение и размещение объёмов услуг "
            "и (или) средств; 4) заключение и исполнение договора закупа услуг."
        ),
        keywords=("этапы", "стади", "закуп", "кезең", "как проходит закуп"),
    ),
    # ЕКД ред. №19 (docs/16 §1 C3): коды 5.0/5.1 = приписка.
    "pripiska.sanction": Citation(
        id="pripiska.sanction",
        label_ru="ЕКД коды 5.0/5.1 (ред. №19 от 27.02.2026)",
        label_kk="БАЖ 5.0/5.1 кодтары (№19 редакция, 27.02.2026)",
        snippet_ru=(
            "Включение в счёт-реестр неподтверждённого случая (код 5.1) влечёт "
            "снятие 300% стоимости услуги / 100 подушевых нормативов. Неподтверждённые "
            "услуги свыше 200 МРП (≈ 865 000 ₸ в 2026) в месяц передаются в "
            "правоохранительные органы, при повторности (свыше 800 МРП ≈ 3 460 000 ₸) "
            "— расторжение договора."
        ),
        keywords=(
            "приписк", "жауапкершілік", "ответственность", "неподтвержд", "5.1",
            "қосып жаз", "жазба қос",
        ),
    ),
    # docs/research/regs/zakon_206_viii.ru.txt (C: пакеты 2026).
    "law206.packages": Citation(
        id="law206.packages",
        label_ru="Закон №206-VIII (изменения пакетов ГОБМП/ОСМС с 01.01.2026)",
        label_kk="№206-VIII Заң (ТМККК/МӘМС пакеттерінің 2026 жылғы өзгерістері)",
        snippet_ru=(
            "С 1 января 2026 года структура пакетов ГОБМП/ОСМС изменена Законом "
            "№206-VIII: часть услуг перераспределена между ГОБМП и ОСМС; действует "
            "принцип перечней (СЗЗ → ГОБМП, иначе ЗПДН → ОСМС)."
        ),
        keywords=(
            "206", "пакет", "изменилось", "с 2026", "с 1 января", "реформ", "закон",
        ),
    ),
}


def get(cid: str) -> Citation:
    return CITATIONS[cid]
