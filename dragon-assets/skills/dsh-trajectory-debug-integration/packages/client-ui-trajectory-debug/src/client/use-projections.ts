/**
 * Reactive projection reader for the browser.
 *
 * The host is the only computation site: the session-projection registry folds
 * our `trajectoryDebug/trajectory` and `trajectoryDebug/perf` units and the
 * api-proxy ships finished whole values to the client's per-session
 * `ProjectionValueStore` (history-tail baseline + `session/projection` push
 * frames). This hook binds the per-key observable face straight to React with
 * `useSyncExternalStore` — no client-side folding, no RPC required.
 */

import { useSyncExternalStore } from 'react'

/** Minimal observable face (React-compatible), as provided by the store. */
export interface ObservableFace<T> {
  subscribe(listener: () => void): () => void
  getSnapshot(): T
}

export interface ProjectionStoreLike {
  faceOf(key: string): ObservableFace<unknown>
}

/** Subscribe to one projection key; returns its current value. */
export function useProjectionValue(store: ProjectionStoreLike | undefined, key: string): unknown {
  return useSyncExternalStore(
    (listener) => {
      if (store === undefined) return () => undefined
      const face = store.faceOf(key)
      return face.subscribe(listener)
    },
    () => (store === undefined ? undefined : store.faceOf(key).getSnapshot()),
  )
}

/** Typed projection read with a fallback. */
export function useProjectionValueTyped<T>(
  store: ProjectionStoreLike | undefined,
  key: string,
  fallback: T,
): T {
  const value = useProjectionValue(store, key)
  return value === undefined ? fallback : (value as T)
}
