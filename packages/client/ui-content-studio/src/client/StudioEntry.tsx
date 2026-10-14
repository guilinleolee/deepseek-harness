/**
 * The sidebar entry occupying the `sidebar.footer.action` hole: a labeled
 * row while the column is wide, a 16px icon on the 56px rail. Clicking opens
 * the frame-wide workbench surface through the shared controller. The entry
 * renders through the shared primitives component so every plugin's entry
 * reads identically.
 */
import { IconSparkleRegular, SidebarFooterEntry } from '@deepseek-ai/dsh-client-ui-primitives'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import type { ContentStudioController } from './studio-store.ts'

/** Injected face of the sidebar entry: the shared open/close controller. */
export interface StudioEntryInjected {
  studio: ContentStudioController
}

/** Full entry props: the footer-action owner share plus the injected face and locale seat. */
export type StudioEntryProps = StudioEntryInjected & { wide: boolean } & PropsLocale<'content-studio'>

/**
 * Render the Content Studio sidebar entry.
 * @param props - the column state, the shared controller, and the locale seat.
 * @returns the entry button element tree.
 */
export function StudioEntry({ wide, studio, t }: StudioEntryProps) {
  return (
    <SidebarFooterEntry
      wide={wide}
      label={t('entry.label')}
      ariaLabel={t('entry.aria')}
      icon={<IconSparkleRegular size={wide ? 16 : 18} />}
      onClick={() => { studio.open() }}
    />
  )
}
