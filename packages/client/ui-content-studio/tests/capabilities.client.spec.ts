import { describe, expect, it } from 'vitest'
import { CAPABILITY_ITEMS, STUDIO_TABS, capabilityGroups } from '../src/client/capabilities.ts'
import { en, zh } from '../src/client/locales.ts'

describe('capability catalog', () => {
  it('declares both intent tabs with their group order', () => {
    expect(STUDIO_TABS.map(tab => tab.id)).toEqual(['create', 'operate'])
  })

  it('keeps item ids unique across both tabs', () => {
    const ids = CAPABILITY_ITEMS.map(item => item.id)
    expect(new Set(ids).size).toBe(ids.length)
  })

  it('places every item in a group its tab declares', () => {
    const declaredGroups = new Set(STUDIO_TABS.flatMap(tab => tab.groups))
    for (const item of CAPABILITY_ITEMS) {
      expect(declaredGroups.has(item.group), item.id).toBe(true)
    }
  })

  it('gives every item a structured clipboard prompt with fill-in markers', () => {
    for (const item of CAPABILITY_ITEMS) {
      expect(item.prompt.length, item.id).toBeGreaterThan(20)
      expect(item.prompt, item.id).toContain('【')
    }
  })

  it('renders each declared tab with non-empty groups', () => {
    for (const tab of STUDIO_TABS) {
      const groups = capabilityGroups(tab.id)
      expect(groups.length, tab.id).toBeGreaterThan(0)
      for (const group of groups) expect(group.items.length).toBeGreaterThan(0)
      expect(groups.map(group => group.id)).toEqual([...tab.groups])
    }
  })

  it('omits an unknown tab entirely', () => {
    expect(capabilityGroups('nonexistent' as never)).toEqual([])
  })

  it('has title and detail dictionary entries for every item, in both locales', () => {
    const zhDict = zh as Record<string, string | undefined>
    const enDict = en as Record<string, string | undefined>
    for (const item of CAPABILITY_ITEMS) {
      expect(zhDict[`cap.${item.id}.title`], item.id).toBeDefined()
      expect(zhDict[`cap.${item.id}.detail`], item.id).toBeDefined()
      expect(enDict[`cap.${item.id}.title`], item.id).toBeDefined()
      expect(enDict[`cap.${item.id}.detail`], item.id).toBeDefined()
    }
  })
})
