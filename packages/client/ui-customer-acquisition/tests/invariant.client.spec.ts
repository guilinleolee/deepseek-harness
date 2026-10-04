import { describe, expect, it } from 'vitest'
import InvariantRegistry from '@deepseek-ai/dsh-invariants'
import * as AcquisitionInvariant from '../src/invariant.ts'
import { setupPanelBench } from './helpers.client.ts'

describe('ui-customer-acquisition invariant companion', () => {
  it('removes its registry contribution when its fiber is disposed (HMR safety)', async () => {
    const harness = await setupPanelBench()
    try {
      await harness.ctx.plugin(InvariantRegistry)
      const fiber = await harness.ctx.plugin(AcquisitionInvariant)

      expect(() => {
        harness.ctx.invariants.register('@deepseek-ai/dsh-client-ui-customer-acquisition', () => {})
      }).toThrow(/already registered/u)

      await fiber.dispose()
      await expect(harness.ctx.plugin(AcquisitionInvariant).await()).resolves.toBeDefined()
    } finally {
      await harness.dispose()
    }
  })
})
