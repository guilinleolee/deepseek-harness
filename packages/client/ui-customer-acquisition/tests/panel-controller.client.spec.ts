import { describe, expect, it, vi } from 'vitest'
import { createPanelController } from '../src/client/panel-controller.ts'

describe('panel controller', () => {
  it('opens, closes, and notifies subscribers only on change', () => {
    const controller = createPanelController()
    const listener = vi.fn()
    const unsubscribe = controller.subscribe(listener)

    expect(controller.isOpen()).toBe(false)
    controller.open()
    expect(controller.isOpen()).toBe(true)
    controller.open()
    expect(listener).toHaveBeenCalledTimes(1)

    controller.close()
    expect(controller.isOpen()).toBe(false)
    controller.close()
    expect(listener).toHaveBeenCalledTimes(2)

    unsubscribe()
    controller.open()
    expect(listener).toHaveBeenCalledTimes(2)
  })
})
