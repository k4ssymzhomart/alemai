"""Recommendations — transparent risk -> action mapping (docs/06 §9, F2/D5).

Contract:
- critical over-execution -> «заявка на увеличение объёма», ₸ = projected
  unpaid overage, deadline = next корректировка window − 3 days.
- critical under-execution -> «заявка на уменьшение/перераспределение» plus
  capacity/campaign suggestions per care type.
- X1 недовыставление -> «довыставить в следующий реестр», ₸ = bucket total.
- block-level findings -> «исключить из счёта до исправления», ₸ = amount at
  risk (fine avoided).
- Reallocation (D5): greedy match of under-execution donors to over-execution
  recipients within the same funding source; outputs the заявка docx table.
Every recommendation = {risk, action_type, ₸ impact, deadline, artifact
generator} (docs/04 ACT).
"""
