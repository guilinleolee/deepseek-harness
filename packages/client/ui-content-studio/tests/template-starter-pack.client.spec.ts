// @vitest-environment jsdom
import { describe, expect, it } from 'vitest'
import { TEMPLATE_CATEGORIES, scanTemplateVariables } from '../src/client/template/model.ts'
import { STARTER_PACK_NAME, STARTER_TEMPLATE_PACK } from '../src/client/template/starter-pack.ts'

describe('starter pack', () => {
  it('carries the pack envelope and readable stable ids', () => {
    expect(STARTER_TEMPLATE_PACK.format).toBe('dsh-template-pack')
    expect(STARTER_TEMPLATE_PACK.formatVersion).toBe(1)
    expect(STARTER_TEMPLATE_PACK.templates.length).toBeGreaterThanOrEqual(8)
    const ids = STARTER_TEMPLATE_PACK.templates.map(record => record.id)
    expect(new Set(ids).size).toBe(ids.length)
    for (const id of ids) {
      expect(id.startsWith('starter-')).toBe(true)
      expect(id.length).toBeLessThanOrEqual(64)
    }
  })

  it('stays inside the category list and references only pack tags', () => {
    const tagIds = new Set(STARTER_TEMPLATE_PACK.tags.map(tag => tag.id))
    for (const record of STARTER_TEMPLATE_PACK.templates) {
      expect(TEMPLATE_CATEGORIES).toContain(record.category)
      for (const tagId of record.tagIds) expect(tagIds.has(tagId)).toBe(true)
    }
  })

  it('declares metadata for every placeholder the bodies introduce', () => {
    for (const record of STARTER_TEMPLATE_PACK.templates) {
      const declared = new Set(record.variables.map(variable => variable.name))
      for (const name of scanTemplateVariables(record.body)) {
        expect(declared.has(name)).toBe(true)
      }
    }
  })

  it('covers at least six categories so the picker demonstrates each column', () => {
    const categories = new Set(STARTER_TEMPLATE_PACK.templates.map(record => record.category))
    expect(categories.size).toBeGreaterThanOrEqual(6)
  })

  it('names the pack for the import report', () => {
    expect(STARTER_PACK_NAME).toBe('starter-pack')
  })
})
