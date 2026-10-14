/**
 * The workbench's shared Remote-read plumbing: one hook owns the
 * loading/ok/failed state machine so every page stays branch-free, and one
 * fallback renders the two non-ok states identically everywhere.
 * @module @deepseek-ai/dsh-client-ui-customer-acquisition/client/read
 */

import { useEffect, useState } from 'react'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import css from './panel.module.css'

/** The lifecycle of one Remote read; `ok` carries the unwrapped value. */
export type ReadState<T> =
  | { state: 'loading' }
  | { state: 'failed'; detail: string }
  | { state: 'ok'; value: T }

/**
 * Run one Remote read for as long as the hook is mounted. The read closure
 * must be stable (the workbench builds the wrappers once); a change reruns
 * the read, and an unmount mid-flight drops the late result.
 * @param read - the unwrapped Remote call.
 * @returns the read's lifecycle state.
 */
export function useRemoteRead<T>(read: () => Promise<T>): ReadState<T> {
  const [state, setState] = useState<ReadState<T>>({ state: 'loading' })
  useEffect(() => {
    let cancelled = false
    void read().then(
      value => { if (!cancelled) setState({ state: 'ok', value }) },
      (error: unknown) => {
        if (!cancelled) setState({ state: 'failed', detail: error instanceof Error ? error.message : String(error) })
      },
    )
    return () => { cancelled = true }
  }, [read])
  return state
}

/**
 * The shared non-ok fallback: the loading line, or the failure with its
 * detail; renders nothing once the page has its value.
 * @param props - the read state and the locale seat.
 * @returns the fallback element, or `null` on success.
 */
export function ReadFallback<T>(props: { state: ReadState<T> } & PropsLocale<'customer-acquisition'>) {
  if (props.state.state === 'loading') return <p className={css.reading}>{props.t('read.loading')}</p>
  if (props.state.state === 'failed') {
    return <p className={css.error}>{props.t('panel.load.failed')}: {props.state.detail}</p>
  }
  return null
}
