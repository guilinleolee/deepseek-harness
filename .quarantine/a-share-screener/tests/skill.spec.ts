/**
 * Skill registration test. The plugin's `apply` registers the
 * `stock-screener` skill; this spec asserts the exact registered payload
 * against the README contract.
 *
 * @module @deepseek-ai/dsh-a-share-screener/tests/skill
 */

import { describe, expect, it, vi } from 'vitest'
import { registerStockScreenerSkill } from '../src/skill/stock-screener.ts'

describe('registerStockScreenerSkill', () => {
  it('registers the documented skill payload', () => {
    const register = vi.fn()
    registerStockScreenerSkill({ skills: { register } } as never)
    expect(register).toHaveBeenCalledTimes(1)
    const [payload] = register.mock.calls[0]
    expect(payload).toMatchObject({
      name: 'stock-screener',
      source: 'runtime',
      modelInvocable: true,
      userInvocable: false,
    })
    expect(payload.content).toContain('low-flat-limit-up')
    expect(payload.content).toContain('oversold-rebound')
    expect(payload.content).toContain('momentum-breakout')
    expect(payload.content).toContain('value-play')
  })
})
