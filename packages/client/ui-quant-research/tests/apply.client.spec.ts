import { describe, expect, it, vi } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import { apply } from '../src/index.ts'
import { apply as invariantApply } from '@deepseek-ai/dsh-client-ui-quant-research/invariant'

describe('node half', () => {
  it('exposes no host-side behavior', () => {
    apply() // reaching here without throwing is the no-op contract
  })
})

describe('invariant companion', () => {
  it('reserves package ownership through the invariants service', async () => {
    const ctx = new Context()
    const register = vi.fn(() => () => {})
    ctx.provide('invariants', { register } as never)
    const disposer = await invariantApply(ctx)
    expect(register).toHaveBeenCalledWith('@deepseek-ai/dsh-client-ui-quant-research', expect.anything())
    expect(typeof disposer).toBe('function')
  })
})
