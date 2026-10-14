/**
 * The sidebar entry occupying the `sidebar.footer.action` hole: a labeled
 * row while the column is wide, an icon on the 56px rail (tooltip via the
 * native title). Clicking opens the frame-wide panel through the shared
 * controller. Placeholder styling until the shared footer-entry primitive
 * ships its package-root export; phase 2 adopts it for visual parity.
 */
import { IconGlobeOutlineMedium } from '@deepseek-ai/dsh-client-ui-primitives'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import type { PanelController } from './panel-controller.ts'
import css from './QuantEntry.module.css'

/** Injected face of the sidebar entry: the shared open/close controller. */
export interface QuantEntryInjected {
  panel: PanelController
}

/** Full entry props: the wide/rail column state, the injected face, and the locale seat. */
export type QuantEntryProps = QuantEntryInjected & { wide: boolean } & PropsLocale<'quant-research'>

/**
 * Render the quant-research sidebar entry.
 * @param props - the column state, the shared controller, and the locale seat.
 * @returns the entry button element tree.
 */
export function QuantEntry({ wide, panel, t }: QuantEntryProps) {
  return (
    <button
      type="button"
      className={wide ? css.entryWide : css.entryRail}
      aria-label={t('entry.aria')}
      title={wide ? undefined : t('entry.label')}
      onClick={() => { panel.open() }}
    >
      <IconGlobeOutlineMedium size={wide ? 16 : 18} />
      {wide && <span className={css.entryLabel}>{t('entry.label')}</span>}
    </button>
  )
}
