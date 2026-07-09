"""Normative radar unit tests (EPIC G5 / H0) — the version-marker regex must
take the real «с изменениями на:» marker and NEVER the decoy «Дата обновления:»
that sits above it on the mirror page (official_sources.csv §0)."""

import pytest

from app.services.radar import MRP_VERSION, VERSION_RE

pytestmark = pytest.mark.smoke


def test_marker_wins_over_decoy_date_above_it() -> None:
    # The decoy «Дата обновления: 16.01.2024» appears ABOVE the real marker.
    page = (
        "Состояние базы на 09.07.2026. Дата обновления: 16.01.2024. "
        "Приказ … № ҚР ДСМ-321/2020. Зарегистрирован … № 21904. "
        "Обновленный с изменениями на: 27.02.2026 В соответствии с пунктом …"
    )
    m = VERSION_RE.search(page)
    assert m is not None
    assert m.group(1) == "27.02.2026"  # NOT the decoy 16.01.2024


def test_decoy_only_page_yields_no_version() -> None:
    page = "Дата обновления: 16.01.2024. Статус: Действующий."
    assert VERSION_RE.search(page) is None


def test_marker_kk_form_without_obnovlennyy_prefix() -> None:
    m = VERSION_RE.search("… № 21744. с изменениями на: 05.01.2026 В соответствии …")
    assert m is not None and m.group(1) == "05.01.2026"


def test_marker_is_newline_agnostic() -> None:
    # 09.07 the mirror sometimes renders the whole page as one line.
    m = VERSION_RE.search("...Обновленный с изменениями на: 18.05.2026...")
    assert m is not None and m.group(1) == "18.05.2026"


def test_mrp_thresholds_render_865k_and_3_46m() -> None:
    # 200 × 4325 = 865 000 ; 800 × 4325 = 3 460 000
    assert "865 000" in MRP_VERSION
    assert "3 460 000" in MRP_VERSION
