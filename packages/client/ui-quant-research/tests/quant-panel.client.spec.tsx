// @vitest-environment jsdom

import { afterEach, describe, expect, it } from 'vitest'
import { act, cleanup, fireEvent, render } from '@testing-library/react'
import { Context } from '@deepseek-ai/cordis'
import { SlotRegistry } from '@deepseek-ai/dsh-client-runtime/client'
import { apply, inject } from '../src/client/index.ts'
import { createPanelController } from '../src/client/panel-controller.ts'
import { apply as nodeApply } from '../src/index.ts'
import { QuantEntry } from '../src/client/QuantEntry.tsx'
import { QuantPanel } from '../src/client/QuantPanel.tsx'

afterEach(cleanup)

describe('QuantEntry', () => {
  it('opens the panel on click in both column states', () => {
    const panel = createPanelController()
    const wide = render(<QuantEntry wide={true} panel={panel} />)
    expect(wide.getByRole('button', { name: '打开量化研究面板' }).textContent).toContain('量化研究')
    fireEvent.click(wide.getByRole('button'))
    expect(panel.isOpen()).toBe(true)
    wide.unmount()

    const rail = render(<QuantEntry wide={false} panel={panel} />)
    expect(rail.getByRole('button', { name: '打开量化研究面板' })).toBeDefined()
    rail.unmount()
  })
})

describe('QuantPanel', () => {
  it('renders null while closed and the disclaimer surface while open', () => {
    const panel = createPanelController()
    const view = render(<QuantPanel panel={panel} />)
    expect(view.container.firstElementChild).toBeNull()

    act(() => { panel.open() })
    const dialog = view.getByRole('dialog', { name: '量化研究' })
    expect(dialog.textContent).toContain('仅供研究参考，不构成投资建议')
    expect(dialog.textContent).toContain('不包含任何实盘交易通道')
    expect(dialog.textContent).toContain('Phase 1')
  })

  it('renders the open surface when the controller starts open', () => {
    const panel = createPanelController()
    panel.open()
    const view = render(<QuantPanel panel={panel} />)
    expect(view.getByRole('dialog', { name: '量化研究' }).textContent).toContain('Phase 1')
  })

  it('closes through the button and through Escape', () => {
    const panel = createPanelController()
    const view = render(<QuantPanel panel={panel} />)
    act(() => { panel.open() })
    fireEvent.click(view.getByRole('button', { name: '关闭' }))
    expect(panel.isOpen()).toBe(false)

    act(() => { panel.open() })
    fireEvent.keyDown(window, { key: 'Tab' })
    expect(panel.isOpen()).toBe(true)
    fireEvent.keyDown(window, { key: 'Escape' })
    expect(panel.isOpen()).toBe(false)
  })
})

describe('node half', () => {
  it('node-half apply is a no-op host placeholder', () => {
    nodeApply() // reaching here without throwing is the no-op contract
  })
})

describe('panel controller', () => {
  it('ignores redundant open and close transitions', () => {
    const panel = createPanelController()
    let notifications = 0
    panel.subscribe(() => { notifications += 1 })
    panel.open()
    panel.open()
    expect(panel.isOpen()).toBe(true)
    panel.close()
    panel.close()
    expect(panel.isOpen()).toBe(false)
    expect(notifications).toBe(2)
  })
})

describe('client apply', () => {
  function declare(slots: SlotRegistry): () => void {
    return slots.register({
      name: 'root',
      children: {
        'sidebar.footer.action': { kind: 'list', scope: 'root' },
        'shell.overlay': { kind: 'list', scope: 'root' },
      },
    } as never, () => null)
  }

  async function bench() {
    const ctx = new Context()
    await ctx.plugin(SlotRegistry).await()
    return { ctx, slots: ctx.get('slots') as SlotRegistry }
  }

  it('declares the slot service only', () => {
    expect(inject).toEqual(['slots'])
  })

  it('registers the sidebar entry and the overlay surface atomically', async () => {
    const { ctx, slots } = await bench()
    const dispose = declare(slots)
    const fiber = await ctx.plugin({ inject: [...inject], apply }).await()
    const entry = slots.entries('sidebar.footer.action')[0]
    const surface = slots.entries('shell.overlay')[0]
    expect(entry?.options.id).toBe('quant-research-entry')
    expect(entry?.component).toBe(QuantEntry)
    expect((entry?.inject?.() as { panel: { isOpen(): boolean } }).panel.isOpen()).toBe(false)
    expect(surface?.options.id).toBe('quant-research')
    expect(surface?.component).toBe(QuantPanel)
    const surfaceFace = surface?.inject?.() as { panel: { isOpen(): boolean; open(): void } }
    expect(surfaceFace.panel.isOpen()).toBe(false)
    surfaceFace.panel.open()
    expect(surfaceFace.panel.isOpen()).toBe(true)
    dispose()
    await Promise.resolve()
    expect(slots.entries('sidebar.footer.action')).toEqual([])
    expect(slots.entries('shell.overlay')).toEqual([])

    // The plugin disposer resolves (a no-op while the generator owns the
    // registrations' lifetime) and the fiber unwinds cleanly.
    await fiber.dispose()
  })
})
