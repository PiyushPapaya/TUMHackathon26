"use client";

import { useEffect, useState } from "react";

// Lädt Daten für einen Schlüssel (z. B. Szenario-ID) und liefert data/error/loading.
// loading wird aus dem Schlüssel abgeleitet, so braucht es kein setState im Effect.
export function useLoad<T>(key: string, fetcher: () => Promise<T>) {
  const [state, setState] = useState<{ key: string; data: T | null; error: string | null }>({ key: "", data: null, error: null });

  useEffect(() => {
    let cancelled = false;
    fetcher()
      .then((data) => !cancelled && setState({ key, data, error: null }))
      .catch((e: Error) => !cancelled && setState({ key, data: null, error: e.message }));
    return () => {
      cancelled = true;
    };
    // fetcher ist pro key stabil gedacht, darum hängt der Effect nur am Schlüssel.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [key]);

  const ready = state.key === key;
  return { data: ready ? state.data : null, error: ready ? state.error : null, loading: !ready };
}
