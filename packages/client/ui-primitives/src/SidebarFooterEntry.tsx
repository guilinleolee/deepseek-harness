// SidebarFooterEntry: the `sidebar.footer.action` entry button every plugin
// shares — a labeled row while the column is wide, a 36px rail icon with a
// delayed tooltip. One component so side-by-side entries read identically
// (font, size, frame) regardless of which plugin owns them.

import type { ReactNode } from 'react'
import css from './SidebarFooterEntry.module.css'
import { Tooltip } from './Tooltip.tsx'

/**
 * Render one sidebar footer entry.
 * @param props.wide - the sidebar column's wide state: labeled row when true, rail icon otherwise.
 * @param props.label - the visible label (also the tooltip text and the accessible name fallback).
 * @param props.ariaLabel - the button's accessible name.
 * @param props.icon - the 16px-class icon element; size selection stays with the caller.
 * @param props.onClick - opens the plugin's surface.
 * @returns the entry button element tree.
 */
export function SidebarFooterEntry({ wide, label, ariaLabel, icon, onClick }: {
  wide: boolean
  label: string
  ariaLabel: string
  icon: ReactNode
  onClick: () => void
}) {
  const button = (
    <button
      type="button"
      className={wide ? css.entryWide : css.entryRail}
      aria-label={ariaLabel}
      onClick={onClick}
    >
      {icon}
      {wide && <span className={css.entryLabel}>{label}</span>}
    </button>
  )
  return wide ? button : <Tooltip label={label} delayMs={500}>{button}</Tooltip>
}
