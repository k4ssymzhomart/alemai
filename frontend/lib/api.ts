/**
 * Typed fetch wrapper for the IGERIM backend (docs/05 §5, REST /api/v1).
 * Base URL comes from NEXT_PUBLIC_API_BASE; defaults to the local FastAPI dev server.
 */

export const API_BASE: string =
  process.env.NEXT_PUBLIC_API_BASE ?? 'http://localhost:8800/api/v1';

export type QueryParams = Record<
  string,
  string | number | boolean | null | undefined
>;

export interface ApiRequestOptions {
  /** Query-string parameters; null/undefined values are omitted. */
  params?: QueryParams;
  /** Extra request headers (merged over defaults). */
  headers?: Record<string, string>;
  /** Abort signal for cancellation. */
  signal?: AbortSignal;
  /** fetch cache mode; defaults to 'no-store' (dashboard data must be fresh). */
  cache?: RequestCache;
}

export class ApiError extends Error {
  readonly status: number;
  readonly statusText: string;
  readonly body: unknown;

  constructor(status: number, statusText: string, body: unknown, url: string) {
    super(`API request failed: ${status} ${statusText} (${url})`);
    this.name = 'ApiError';
    this.status = status;
    this.statusText = statusText;
    this.body = body;
  }
}

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'PUT' | 'DELETE';

function buildUrl(path: string, params?: QueryParams): string {
  const base = API_BASE.replace(/\/+$/, '');
  const suffix = path.startsWith('/') ? path : `/${path}`;
  const url = new URL(`${base}${suffix}`);
  if (params) {
    for (const [key, value] of Object.entries(params)) {
      if (value !== null && value !== undefined) {
        url.searchParams.set(key, String(value));
      }
    }
  }
  return url.toString();
}

async function request<T>(
  method: HttpMethod,
  path: string,
  body?: unknown,
  options: ApiRequestOptions = {},
): Promise<T> {
  const url = buildUrl(path, options.params);
  const headers: Record<string, string> = {
    Accept: 'application/json',
    ...options.headers,
  };

  const init: RequestInit = {
    method,
    headers,
    signal: options.signal,
    cache: options.cache ?? 'no-store',
    credentials: 'include', // send the session cookie (cross-origin :3000→:8800)
  };

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
    init.body = JSON.stringify(body);
  }

  const response = await fetch(url, init);

  if (!response.ok) {
    const errorBody: unknown = await response
      .json()
      .catch(() => response.text().catch(() => null));
    throw new ApiError(response.status, response.statusText, errorBody, url);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

/**
 * POST a JSON body and download the binary response (e.g. a generated .docx)
 * as a file. Throws ApiError on a non-2xx status. The server sets the filename
 * via Content-Disposition; `fallbackName` is used otherwise.
 */
export async function downloadFile(
  path: string,
  body: unknown,
  fallbackName: string,
): Promise<void> {
  const url = buildUrl(path);
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: '*/*' },
    body: JSON.stringify(body),
    cache: 'no-store',
    credentials: 'include',
  });
  if (!response.ok) {
    const errBody: unknown = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, errBody, url);
  }
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const match = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(disposition);
  const name = match ? decodeURIComponent(match[1]) : fallbackName;
  const blob = await response.blob();
  const href = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = href;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(href);
}

/**
 * GET a binary endpoint (the F2 XLSX exports) and save it as a file.
 * Same Content-Disposition handling as {@link downloadFile}.
 */
export async function downloadFileGet(
  path: string,
  params: QueryParams | undefined,
  fallbackName: string,
): Promise<void> {
  const url = buildUrl(path, params);
  const response = await fetch(url, {
    method: 'GET',
    cache: 'no-store',
    credentials: 'include',
  });
  if (!response.ok) {
    const errBody: unknown = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, errBody, url);
  }
  const disposition = response.headers.get('Content-Disposition') ?? '';
  const match = /filename\*?=(?:UTF-8'')?"?([^";]+)"?/i.exec(disposition);
  const name = match ? decodeURIComponent(match[1]) : fallbackName;
  const blob = await response.blob();
  const href = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = href;
  a.download = name;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(href);
}

/**
 * POST one file as multipart/form-data (the F1 import endpoints) and return
 * the parsed JSON response. The browser sets the multipart boundary itself.
 */
export async function uploadFile<T>(path: string, file: File): Promise<T> {
  const url = buildUrl(path);
  const body = new FormData();
  body.append('file', file, file.name);
  const response = await fetch(url, {
    method: 'POST',
    headers: { Accept: 'application/json' },
    body,
    cache: 'no-store',
    credentials: 'include',
  });
  if (!response.ok) {
    const errBody: unknown = await response.json().catch(() => null);
    throw new ApiError(response.status, response.statusText, errBody, url);
  }
  return (await response.json()) as T;
}

export const api = {
  get: <T>(path: string, options?: ApiRequestOptions) =>
    request<T>('GET', path, undefined, options),

  post: <T>(path: string, body?: unknown, options?: ApiRequestOptions) =>
    request<T>('POST', path, body, options),

  patch: <T>(path: string, body?: unknown, options?: ApiRequestOptions) =>
    request<T>('PATCH', path, body, options),

  put: <T>(path: string, body?: unknown, options?: ApiRequestOptions) =>
    request<T>('PUT', path, body, options),

  delete: <T>(path: string, options?: ApiRequestOptions) =>
    request<T>('DELETE', path, undefined, options),
};

export default api;
