import { NextResponse, type NextRequest } from 'next/server';

/**
 * Route guard (EPIC G1). The session cookie is host-only for `localhost`
 * (port-agnostic), so a cookie set by the API on :8800 is readable here on
 * :3000 — even though it's httponly, middleware runs server-side. We only check
 * PRESENCE; the API verifies the signature on every request, and SessionProvider
 * redirects if /auth/me rejects an expired/forged cookie.
 */
const SESSION_COOKIE = 'qalam_session';
const PUBLIC_PATHS = ['/login'];

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const hasSession = request.cookies.has(SESSION_COOKIE);
  const isPublic = PUBLIC_PATHS.some((p) => pathname === p || pathname.startsWith(`${p}/`));

  if (!hasSession && !isPublic) {
    const url = request.nextUrl.clone();
    url.pathname = '/login';
    return NextResponse.redirect(url);
  }
  if (hasSession && isPublic) {
    const url = request.nextUrl.clone();
    url.pathname = '/overview';
    return NextResponse.redirect(url);
  }
  return NextResponse.next();
}

export const config = {
  // Guard everything except Next internals + static assets.
  matcher: ['/((?!_next/static|_next/image|favicon.ico|icon.svg|brand/).*)'],
};
