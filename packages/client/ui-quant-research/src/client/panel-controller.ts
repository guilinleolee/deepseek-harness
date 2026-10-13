/**
 * The shared open/close controller for the quant-research surface: the
 * sidebar entry calls `open()`, the overlay panel renders `isOpen()` and
 * calls `close()`. One plain observable store; React reads it through
 * `useSyncExternalStore`.
 * @module @deepseek-ai/dsh-client-ui-quant-research/client/panel-controller
 */

/* jscpd:ignore-start */
/** Minimal open/close controller shared by both slot registrations. */
export interface PanelController {
  /** Open the panel. */
  open(): void
  /** Close the panel. */
  close(): void
  /** Whether the panel is open. */
  isOpen(): boolean
  /** Subscribe to open-state changes; returns the unsubscriber. */
  subscribe(listener: () => void): () => void
}

/**
 * Create the panel controller.
 * @returns the controller instance.
 */
export function createPanelController(): PanelController {
  let open = false
  const listeners = new Set<() => void>()
  const emit = () => { for (const listener of listeners) listener() }
  return {
    open() {
      if (open) return
      open = true
      emit()
    },
    close() {
      if (!open) return
      open = false
      emit()
    },
    isOpen: () => open,
    subscribe(listener: () => void): () => void {
      listeners.add(listener)
      return () => { listeners.delete(listener) }
    },
  }
}
/* jscpd:ignore-end */
