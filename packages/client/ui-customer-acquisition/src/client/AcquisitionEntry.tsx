/**
 * The sidebar entry occupying the `sidebar.footer.action` hole: a labeled
 * row while the column is wide, a 16px icon on the 56px rail. Clicking opens
 * the frame-wide panel through the shared controller. The entry renders
 * through the shared primitives component so every plugin's entry reads
 * identically.
 */
import { IconSparkle16, SidebarFooterEntry } from '@deepseek-ai/dsh-client-ui-primitives'
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
  return (
    <SidebarFooterEntry
      wide={wide}
      label={t('entry.label')}
      ariaLabel={t('entry.aria')}
      icon={<IconSparkle16 size={wide ? 16 : 18} />}
      onClick={() => { panel.open() }}
    />
  )
}
