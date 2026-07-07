"""Copilot orchestrator — guardrailed LLM assistant (docs/05 §6, docs/07).

Contract:
- Intent router: data | regulation | report | out_of_scope; anything else gets
  a polite refusal listing the three capabilities (docs/04 SPEAK).
- data: Claude tool-use with list_metrics() and run_metric_query() only — the
  LLM never writes SQL; the semantic layer is the single numbers source.
- regulation: pgvector top-k over reg_chunks (kk+ru); answers built ONLY from
  retrieved chunks, every sentence carries citation ids rendered as
  «п. X, приказ Y».
- report: fills the report skeleton with run_metric_query results.
- Hard guardrail: response validator — every number in the output must match a
  number present in tool results (regex + normalization); violation ->
  one stricter regeneration retry -> fallback template answer.
- Answers in the language of the question; kk terminology enforced from
  shared/glossary.csv via the system prompt (docs/07 §5).
- Transport: plain JSON stub today, SSE stream {tokens, tool_traces,
  citations} per docs/05 §5 later. Provider-agnostic thin client
  (Claude primary, OpenAI fallback, local KazLLM roadmap).
"""
