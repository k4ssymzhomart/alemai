import { NextResponse, type NextRequest } from 'next/server';

/**
 * Route guard (EPIC G1). The session cookie is host-only for `localhost`
 * (port-agnostic), so a cookie set by the API on :8800 is readable here on
 * :3000 — even though it's httponly, middleware runs server-side. We only check
 * PRESENCE; the API verifies the signature on every request, and SessionProvider
 * redirects if /auth/me rejects an expired/forged cookie.
 *
 * SPLIT-DOMAIN DEPLOY CAVEAT: when the API runs on a DIFFERENT hostname than
 * this site (Vercel frontend + Render API), the session cookie is scoped to the
 * API's domain and is INVISIBLE to this middleware. A cookie-presence guard
 * would then bounce every authenticated user back to /login forever. So we only
 * enforce the server guard when the API shares this site's hostname (local dev,
 * docker-compose); otherwise SessionProvider's client-side /auth/me is the guard.
 */
const SESSION_COOKIE = 'qalam_session';
// /s/<code> (share-link resolver, H3) is public so it can resolve before auth;
// it then routes to the target, where the guard applies as usual.
const PUBLIC_PATHS = ['/login', '/s'];

/** True when the API is same-hostname as the site (so its cookie is visible here). */
function apiCookieVisible(request: NextRequest): boolean {
  const apiBase = process.env.NEXT_PUBLIC_API_BASE ?? '';
  if (!apiBase.startsWith('http')) return true; // relative base => same-origin
  try {
    return new URL(apiBase).hostname === request.nextUrl.hostname;
  } catch {
    return true;
  }
}

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = request.cookies.has(SESSION_COOKIE);
  const isPublic = PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`));

  if (apiCookieVisible(request) && !hasSession && !isPublic) {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }
  // NB: we do NOT bounce cookie-holders off /login. Middleware can't verify the
  // signature; a present-but-invalid cookie would ping-pong /login↔/overview
  // forever (adversarial review #8). SessionProvider routes a VALID session
  // away from /login after /auth/me succeeds; an invalid one lands + stays here.
  return NextResponse.next();
}

export const config = {
  // Guard everything except Next internals + static assets.
  matcher: ['/((?!_next/static|_next/image|favicon.ico|icon.svg|brand/).*)'],
};
