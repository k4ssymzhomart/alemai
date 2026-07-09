'use client';

import { createContext, useContext } from 'react';

/**
 * Revalidation epoch (EPIC G2) — the drop-in analog of SWR's `mutate()` for the
 * app's plain useState/useEffect data layer. EventsProvider bumps it when a new
 * domain event arrives; every useFetch hook lists it as an effect dependency, so
 * all mounted screens refetch. Default 0 for any usage outside the provider.
 */
export const RefreshContext = createContext<number>(0);

export function useRefreshEpoch(): number {
  return useContext(RefreshContext);
}
