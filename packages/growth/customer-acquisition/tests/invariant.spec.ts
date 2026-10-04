import { describe, expect, it } from 'vitest'
import InvariantRegistry from '@deepseek-ai/dsh-invariants'
import * as AcquisitionInvariant from '../src/invariant.ts'
import { setupHarness } from './helpers.ts'

describe('customer-acquisition invariant companion', () => {
  it('removes its registry contribution when its fiber is disposed (HMR safety)', async () => {
    const harness = await setupHarness()
    try {
      await harness.ctx.plugin(InvariantRegistry)
      const fiber = await harness.ctx.plugin(AcquisitionInvariant)

      expect(() => {
        harness.ctx.invariants.register('@deepseek-ai/dsh-customer-acquisition', () => {})
      }).toThrow(/already registered/u)

      await fiber.dispose()
      await expect(harness.ctx.plugin(AcquisitionInvariant).await()).resolves.toBeDefined()
    } finally {
      await harness.dispose()
    }
  })
})
