import { describe, expect, it, vi } from 'vitest'
import { Context } from '@deepseek-ai/cordis'
import { apply } from '../src/index.ts'

describe('node half', () => {
  it('exposes no host-side behavior', () => {
    apply() // reaching here without throwing is the no-op contract
  })
})

