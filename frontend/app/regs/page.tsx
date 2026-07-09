'use client';

import { Suspense, useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useSearchParams } from 'next/navigation';
import { useTranslation } from 'react-i18next';
import { ExternalLink, Search, X } from 'lucide-react';
import clsx from 'clsx';

import api from '@/lib/api';

// ── API shapes (mirror backend/app/schemas/regs.py) ────────────────────────
interface RegDoc {
  id: string;
  title: string;
  title_kk: string | null;
  langs: string[];
  redaction: string | null;
  source_url: string | null;
  lines: number;
}
interface TocNode {
  kind: string;
  num: string;
  title: string;
  anchor: string;
  line: number;
  children: TocNode[];
}
interface RegToc {
  doc_id: string;
  lang: string;
  title: string;
  redaction: string | null;
  source_url: string | null;
  langs: string[];
  total_lines: number;
  toc: TocNode[];
}
interface RegLine {
  n: number;
  text: string;
  kind: string;
  num: string | null;
  anchor: string | null;
}
interface RegContent {
  doc_id: string;
  lang: string;
  from_: number;
  to: number;
  total_lines: number;
  lines: RegLine[];
}
interface RegHit {
  line: number;
  punkt: string | null;
  anchor: string | null;
  snippet: string;
}
interface RegSearch {
  doc_id: string;
  lang: string;
  q: string;
  count: number;
  hits: RegHit[];
}

type ViewerLang = 'ru' | 'kk';

function uiToViewer(lng: string): ViewerLang {
  return lng === 'kk' ? 'kk' : 'ru';
}

export default function RegsPage() {
  return (
    <Suspense fallback={null}>
      <RegsReader />
    </Suspense>
  );
}

function RegsReader() {
  const { t, i18n } = useTranslation();
  const params = useSearchParams();

  const [docs, setDocs] = useState<RegDoc[]>([]);
  const [docId, setDocId] = useState<string | null>(params.get('doc'));
  const [lang, setLang] = useState<ViewerLang>(
    (params.get('lang') as ViewerLang) || uiToViewer(i18n.language),
  );
  const [toc, setToc] = useState<RegToc | null>(null);
  const [content, setContent] = useState<RegContent | null>(null);
  const [active, setActive] = useState<string | null>(
    params.get('p') ? `p-${params.get('p')}` : null,
  );

  const [query, setQuery] = useState(params.get('q') ?? '');
  const [hits, setHits] = useState<RegSearch | null>(null);

  const bodyRef = useRef<HTMLDivElement>(null);
  const pendingAnchor = useRef<string | null>(active);

  // Load the corpus registry once; resolve the initial document.
  useEffect(() => {
    let alive = true;
    api
      .get<RegDoc[]>('/regs')
      .then((rows) => {
        if (!alive) return;
        setDocs(rows);
        if (!docId && rows.length) setDocId(rows[0].id);
      })
      .catch(() => alive && setDocs([]));
    return () => {
      alive = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const selectedDoc = useMemo(
    () => docs.find((d) => d.id === docId) ?? null,
    [docs, docId],
  );

  // A document without the chosen lang falls back to its first available one.
  const effLang: ViewerLang = useMemo(() => {
    if (!selectedDoc) return lang;
    return (selectedDoc.langs.includes(lang) ? lang : selectedDoc.langs[0]) as ViewerLang;
  }, [selectedDoc, lang]);

  // Load TOC + content whenever the document or language changes.
  useEffect(() => {
    if (!docId) return;
    let alive = true;
    setContent(null);
    Promise.all([
      api.get<RegToc>(`/regs/${docId}/toc`, { params: { lang: effLang } }),
      api.get<RegContent>(`/regs/${docId}/content`, { params: { lang: effLang } }),
    ])
      .then(([tc, ct]) => {
        if (!alive) return;
        setToc(tc);
        setContent(ct);
      })
      .catch(() => {
        if (!alive) return;
        setToc(null);
        setContent(null);
      });
    return () => {
      alive = false;
    };
  }, [docId, effLang]);

  const scrollTo = useCallback((anchor: string) => {
    const el = bodyRef.current?.querySelector<HTMLElement>(`#${CSS.escape(anchor)}`);
    if (el) {
      el.scrollIntoView({ behavior: 'smooth', block: 'start' });
      setActive(anchor);
    }
  }, []);

  // After content renders, honour a pending deep-link anchor (?p= / citation).
  useEffect(() => {
    if (!content || !pendingAnchor.current) return;
    const anchor = pendingAnchor.current;
    pendingAnchor.current = null;
    requestAnimationFrame(() => scrollTo(anchor));
  }, [content, scrollTo]);

  const runSearch = useCallback(
    async (q: string) => {
      const term = q.trim();
      if (!docId || term.length < 2) {
        setHits(null);
        return;
      }
      try {
        const res = await api.get<RegSearch>(`/regs/${docId}/search`, {
          params: { q: term, lang: effLang },
        });
        setHits(res);
      } catch {
        setHits(null);
      }
    },
    [docId, effLang],
  );

  const docTitle = (d: RegDoc) => (effLang === 'kk' && d.title_kk ? d.title_kk : d.title);

  return (
    <div className="space-y-5">
      <header>
        <h1 className="font-display text-h1 text-ink">{t('regs.title')}</h1>
        <p className="mt-1 label-micro">{t('regs.lead')}</p>
      </header>

      {/* Document selector */}
      <div className="flex flex-wrap gap-2 border-b border-ink/15 pb-3">
        {docs.map((d) => (
          <button
            key={d.id}
            type="button"
            onClick={() => {
              setDocId(d.id);
              setHits(null);
              setQuery('');
              setActive(null);
            }}
            className={clsx(
              'border px-3 py-1.5 text-left text-secondary transition-colors duration-150',
              d.id === docId
                ? 'border-accent font-medium text-accent'
                : 'border-ink/15 text-ink/70 hover:bg-ink/[.03]',
            )}
          >
            {docTitle(d)}
          </button>
        ))}
      </div>

      {selectedDoc ? (
        <div className="grid grid-cols-1 gap-6 md:grid-cols-[minmax(0,16rem)_minmax(0,1fr)]">
          {/* Left — TOC or search results */}
          <aside className="md:sticky md:top-4 md:max-h-[calc(100vh-8rem)] md:self-start md:overflow-y-auto">
            <form
              onSubmit={(e) => {
                e.preventDefault();
                void runSearch(query);
              }}
              className="mb-3 flex items-center gap-1.5 border border-ink/15 px-2 py-1.5"
            >
              <Search className="h-3.5 w-3.5 shrink-0 text-ink/40" strokeWidth={1.75} aria-hidden />
              <input
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={t('regs.search')}
                className="w-full bg-transparent text-secondary text-ink outline-none"
              />
              {query ? (
                <button
                  type="button"
                  aria-label="clear"
                  onClick={() => {
                    setQuery('');
                    setHits(null);
                  }}
                >
                  <X className="h-3.5 w-3.5 text-ink/40 hover:text-ink" strokeWidth={1.75} />
                </button>
              ) : null}
            </form>

            {hits ? (
              <div>
                <p className="label-micro mb-2">
                  {t('regs.found')}: {hits.count}
                </p>
                {hits.count === 0 ? (
                  <p className="text-secondary text-ink/50">{t('regs.noResults')}</p>
                ) : (
                  <ul className="space-y-1">
                    {hits.hits.map((h, i) => (
                      <li key={i}>
                        <button
                          type="button"
                          onClick={() => h.anchor && scrollTo(h.anchor)}
                          className="w-full border-l-2 border-transparent px-2 py-1 text-left text-micro text-ink/70 hover:border-accent hover:bg-ink/[.03]"
                        >
                          {h.punkt ? (
                            <span className="font-mono text-accent">
                              {t('regs.punkt')} {h.punkt}
                            </span>
                          ) : (
                            <span className="font-mono text-ink/40">·{h.line}</span>
                          )}{' '}
                          {h.snippet.slice(0, 90)}…
                        </button>
                      </li>
                    ))}
                  </ul>
                )}
              </div>
            ) : (
              <nav>
                <p className="label-micro mb-2">{t('regs.contents')}</p>
                <ul className="space-y-0.5">
                  {toc?.toc.map((node) => (
                    <TocItem key={node.anchor} node={node} active={active} onJump={scrollTo} />
                  ))}
                </ul>
              </nav>
            )}
          </aside>

          {/* Right — sticky doc header + body */}
          <section className="min-w-0">
            <div className="sticky top-0 z-10 -mx-1 mb-3 border-b border-ink/15 bg-paper px-1 pb-2.5 pt-1">
              <div className="flex flex-wrap items-baseline justify-between gap-x-4 gap-y-1">
                <h2 className="font-display text-h3 text-ink">{docTitle(selectedDoc)}</h2>
                <div className="flex items-center gap-3">
                  {selectedDoc.langs.length > 1 ? (
                    <div className="flex gap-1">
                      {selectedDoc.langs.map((l) => (
                        <button
                          key={l}
                          type="button"
                          onClick={() => setLang(l as ViewerLang)}
                          className={clsx(
                            'px-1.5 py-0.5 font-mono text-micro uppercase transition-colors',
                            l === effLang
                              ? 'text-accent'
                              : 'text-ink/40 hover:text-ink',
                          )}
                        >
                          {l}
                        </button>
                      ))}
                    </div>
                  ) : null}
                  {selectedDoc.source_url ? (
                    <a
                      href={selectedDoc.source_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      title={t('regs.openSource')}
                      className="flex items-center gap-1 text-micro text-ink/50 hover:text-accent"
                    >
                      <ExternalLink className="h-3 w-3" strokeWidth={1.75} aria-hidden />
                      {t('regs.source')}
                    </a>
                  ) : null}
                </div>
              </div>
              {selectedDoc.redaction ? (
                <p className="label-micro mt-0.5">
                  {t('regs.revision')} {selectedDoc.redaction}
                </p>
              ) : null}
            </div>

            <div
              ref={bodyRef}
              className="max-w-prose text-body leading-relaxed text-ink/90"
            >
              {content ? (
                content.lines.map((li) => <Line key={li.n} li={li} active={active} />)
              ) : (
                <p className="animate-pulse font-mono text-secondary text-ink/40">
                  {t('regs.loading')}
                </p>
              )}
            </div>
          </section>
        </div>
      ) : (
        <p className="text-secondary text-ink/50">{t('regs.selectDoc')}</p>
      )}
    </div>
  );
}

function TocItem({
  node,
  active,
  onJump,
  depth = 0,
}: {
  node: TocNode;
  active: string | null;
  onJump: (a: string) => void;
  depth?: number;
}) {
  return (
    <li>
      <button
        type="button"
        onClick={() => onJump(node.anchor)}
        style={{ paddingLeft: `${0.5 + depth * 0.75}rem` }}
        className={clsx(
          'w-full border-l-2 py-1 pr-2 text-left text-secondary transition-colors duration-150',
          active === node.anchor
            ? 'border-accent font-medium text-accent'
            : 'border-transparent text-ink/70 hover:bg-ink/[.03] hover:text-ink',
        )}
      >
        <span className="font-mono text-ink/40">{node.num}.</span> {node.title}
      </button>
      {node.children.length ? (
        <ul>
          {node.children.map((c) => (
            <TocItem key={c.anchor} node={c} active={active} onJump={onJump} depth={depth + 1} />
          ))}
        </ul>
      ) : null}
    </li>
  );
}

function Line({ li, active }: { li: RegLine; active: string | null }) {
  const isActive = li.anchor != null && li.anchor === active;
  const common = 'scroll-mt-24';
  if (li.text === '') return <div className="h-2.5" aria-hidden />;

  if (li.kind === 'chapter' || li.kind === 'article') {
    return (
      <h3
        id={li.anchor ?? undefined}
        className={clsx(common, 'mt-6 mb-1 font-display text-h3 text-ink')}
      >
        {li.text}
      </h3>
    );
  }
  if (li.kind === 'paragraph') {
    return (
      <h4
        id={li.anchor ?? undefined}
        className={clsx(common, 'mt-4 mb-1 font-medium text-ink')}
      >
        {li.text}
      </h4>
    );
  }
  if (li.kind === 'punkt') {
    return (
      <p
        id={li.anchor ?? undefined}
        className={clsx(
          common,
          'mt-2 border-l-2 pl-3 transition-colors duration-300',
          isActive ? 'border-accent bg-accent/[.07]' : 'border-transparent',
        )}
      >
        <span className="font-medium text-ink">{li.num}.</span>{' '}
        {li.text.replace(/^\d+(?:-\d+)?\.\s*/, '')}
      </p>
    );
  }
  // sub-point / plain text — indented slightly
  return <p className={clsx(common, 'pl-3 text-ink/80')}>{li.text}</p>;
}
