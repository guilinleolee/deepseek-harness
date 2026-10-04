/**
 * The sidebar entry occupying the `sidebar.footer.action` hole: a labeled row
 * while the column is wide, a 16px icon on the 56px rail. Clicking opens the
 * frame-wide panel through the shared controller.
 */
import { IconSparkle16, Tooltip } from '@deepseek-ai/dsh-client-ui-primitives'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import type { PanelController } from './panel-controller.ts'

/** Injected face of the sidebar entry: the shared open/close controller. */
export interface AcquisitionEntryInjected {
  panel: PanelController
}

/** Full entry props: the wide/rail column state plus the injected face and locale seat. */
export type AcquisitionEntryProps = AcquisitionEntryInjected & { wide: boolean } & PropsLocale<'customer-acquisition'>

/**
 * Render the acquisition sidebar entry.
 * @param props - the column state, the shared controller, and the locale seat.
 * @returns the entry button element tree.
 */
export function AcquisitionEntry({ wide, panel, t }: AcquisitionEntryProps) {
  const button = (
    <button
      type="button"
      aria-label={t('entry.aria')}
      onClick={() => { panel.open() }}
    >
      <IconSparkle16 size={wide ? 16 : 18} />
      {wide && <span>{t('entry.label')}</span>}
    </button>
  )
  return wide ? button : <Tooltip label={t('entry.label')} delayMs={500}>{button}</Tooltip>
}
