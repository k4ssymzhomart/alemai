"""Document generation — docx artifacts (docs/05 §1, docs/04 ACT, G4).

Contract:
- python-docx + docxtpl (jinja placeholders) over ``backend/templates/*.docx``:
  zayavka_kk, zayavka_ru, report_kk, report_ru.
- RU and KK variants for every artifact; terminology from shared/glossary.csv.
- All numbers are pulled from the DB at generation time — never from the LLM.
- Filename conventions: ``zayavka_korrektirovka_YYYY-MM-DD.docx``,
  ``report_YYYY-MM_<lang>.docx``.
"""
