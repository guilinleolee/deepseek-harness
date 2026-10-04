/**
 * The frame-wide placeholder surface occupying the `shell.overlay` hole: it
 * states the plugin's research-only scope and what ships in later phases.
 * Escape closes; the closed state renders null while the slot entry stays
 * mounted. The Remote face and the real panel arrive with phase 2.
 */
import { useCallback, useEffect, useSyncExternalStore } from 'react'
import type { PanelController } from './panel-controller.ts'
import css from './QuantPanel.module.css'

/** Injected face of the overlay surface: the shared controller. */
export interface QuantPanelInjected {
  panel: PanelController
}

/** Full surface props: the injected face. */
export type QuantPanelProps = QuantPanelInjected

/**
 * Render the placeholder quant-research panel.
 * @param props - the shared controller.
 * @returns the overlay element tree, or `null` while closed.
 */
export function QuantPanel({ panel }: QuantPanelProps) {
  /* jscpd:ignore-start -- shared panel scaffold (subscribe + Escape), not cloned logic. */
  const subscribe = useCallback((listener: () => void) => panel.subscribe(listener), [panel])
  const getOpenState = useCallback(() => panel.isOpen(), [panel])
  const open = useSyncExternalStore(subscribe, getOpenState)

  useEffect(() => {
    if (!open) return
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') panel.close()
    }
    window.addEventListener('keydown', onKey)
    return () => { window.removeEventListener('keydown', onKey) }
  }, [open, panel])

  /* jscpd:ignore-end */

  if (!open) return null
  return (
    <div className={css.overlay} role="dialog" aria-label="量化研究">
      <div className={css.card}>
        <div className={css.header}>
          <span className={css.title}>量化研究</span>
          <span className={css.phase}>Phase 1</span>
        </div>
        <p className={css.intro}>
          本面板提供量化投研工具：行情获取、技术指标与模拟回测。所有输出仅供研究参考，不构成投资建议；
          插件不包含任何实盘交易通道。绩效报告与图表卡片将在后续阶段加入。
        </p>
        <button type="button" className={css.close} onClick={() => { panel.close() }}>关闭</button>
      </div>
    </div>
  )
}
