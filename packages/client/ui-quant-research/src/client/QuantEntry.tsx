/**
 * The sidebar entry occupying the `sidebar.footer.action` hole: a labeled
 * row while the column is wide, an icon on the 56px rail (tooltip via the
 * native title). Clicking opens the frame-wide panel through the shared
 * controller. Placeholder styling until the shared footer-entry primitive
 * ships its package-root export; phase 2 adopts it for visual parity.
 */
import { IconGlobeOutline14 } from '@deepseek-ai/dsh-client-ui-primitives'
import type { PanelController } from './panel-controller.ts'
import css from './QuantEntry.module.css'

/** Injected face of the sidebar entry: the shared open/close controller. */
export interface QuantEntryInjected {
  panel: PanelController
}

/** Full entry props: the wide/rail column state plus the injected face. */
export type QuantEntryProps = QuantEntryInjected & { wide: boolean }

/**
 * Render the quant-research sidebar entry.
 * @param props - the column state and the shared controller.
 * @returns the entry button element tree.
 */
export function QuantEntry({ wide, panel }: QuantEntryProps) {
  return (
    <button
      type="button"
      className={wide ? css.entryWide : css.entryRail}
      aria-label="打开量化研究面板"
      title={wide ? undefined : '量化研究'}
      onClick={() => { panel.open() }}
    >
      <IconGlobeOutline14 size={wide ? 16 : 18} />
      {wide && <span className={css.entryLabel}>量化研究</span>}
    </button>
  )
}
