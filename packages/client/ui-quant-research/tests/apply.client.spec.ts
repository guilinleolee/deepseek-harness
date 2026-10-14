import { describe, it } from 'vitest'
import { apply } from '../src/index.ts'

describe('node half', () => {
  it('exposes no host-side behavior', () => {
    apply() // reaching here without throwing is the no-op contract
  })
})

