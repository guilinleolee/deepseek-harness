/**
 * The persona wizard's form model: entry round-trips, clone remapping,
 * provenance flips, and the save-payload shaping.
 */
import { describe, expect, it } from 'vitest'
import type { PersonaEntry, PersonaField, PersonaFieldKey } from '@deepseek-ai/dsh-content-outputs/types'
import {
  PERSONA_FIELD_KEYS as GATEWAY_FIELDS, PERSONA_FIELD_LABELS as GATEWAY_FIELD_LABELS,
  PERSONA_PLATFORMS as GATEWAY_PLATFORMS, PERSONA_PLATFORM_LABELS as GATEWAY_PLATFORM_LABELS,
  PERSONA_STYLE_PRESETS as GATEWAY_PRESETS, PERSONA_STYLE_PRESET_LABELS as GATEWAY_PRESET_LABELS,
} from '@deepseek-ai/dsh-content-outputs/types'
import {
  PERSONA_FIELD_KEYS, PERSONA_FIELD_LABELS, PERSONA_PLATFORMS, PERSONA_PLATFORM_LABELS,
  PERSONA_STYLE_PRESETS, PERSONA_STYLE_PRESET_LABELS,
  adoptField, emptyForm, formFromEntry, inputFromForm, parseWordList,
} from '../src/client/persona/model.ts'

function entry(): PersonaEntry {
  const fields = {} as Record<PersonaFieldKey, PersonaField>
  for (const key of PERSONA_FIELD_KEYS) fields[key] = { value: null, source: 'user', aiMeta: null }
  fields.niche = { value: 'AI 工具', source: 'ai', aiMeta: { promptVersion: 'persona-fill@1', at: '2026-09-25T00:00:00.000Z' } }
  return {
    id: 'p-1' as PersonaEntry['id'],
    name: '老李',
    platforms: ['xhs'],
    accountStage: 'existing',
    revision: 5,
    digest: '老李（v5）',
    fields,
    links: [{ platform: 'xhs', url: 'https://x.example', bio: '简介', sampleText: null }],
    site: { url: 'https://example.com', pastedText: '官网文本' },
    style: { preset: 'humor', customText: '自定义', strength: 'strict', bannedWords: ['最好'], redLines: ['医疗'] },
    assets: { resumeText: '简历', resumeName: '简历.txt' },
    report: { markdown: '# 报告', sourceRevision: 4, editedByUser: true, generatedAt: '2026-09-25T00:00:00.000Z', promptVersion: 'persona-report@1' },
    clonedFrom: null,
    createdAt: '2026-09-24T00:00:00.000Z',
    updatedAt: '2026-09-25T00:00:00.000Z',
  }
}

describe('the client and gateway vocabulary tables stay in sync', () => {
  it('carries the same platforms, fields, and presets as the wire contract', () => {
    // The bundle purity gate forbids value-importing the gateway tables in
    // client code, so the two tables drift apart silently unless pinned here.
    expect([...PERSONA_PLATFORMS]).toEqual([...GATEWAY_PLATFORMS])
    expect(PERSONA_PLATFORM_LABELS).toEqual(GATEWAY_PLATFORM_LABELS)
    expect([...PERSONA_FIELD_KEYS]).toEqual([...GATEWAY_FIELDS])
    expect(PERSONA_FIELD_LABELS).toEqual(GATEWAY_FIELD_LABELS)
    expect([...PERSONA_STYLE_PRESETS]).toEqual([...GATEWAY_PRESETS])
    expect(PERSONA_STYLE_PRESET_LABELS).toEqual(GATEWAY_PRESET_LABELS)
  })
})

describe('emptyForm and formFromEntry', () => {
  it('starts a fresh form with every field user-sourced', () => {
    const form = emptyForm()
    expect(form.editingId).toBeNull()
    expect(form.fields.audience).toEqual({ value: '', source: 'user', aiMeta: null })
    expect(Object.keys(form.fields)).toHaveLength(PERSONA_FIELD_KEYS.length)
  })

  it('round-trips a stored entry into the form and back', () => {
    const form = formFromEntry(entry())
    expect(form.editingId).toBe(entry().id)
    expect(form.clonedFrom).toBeNull()
    expect(form.fields.niche).toEqual({ value: 'AI 工具', source: 'ai', aiMeta: entry().fields.niche.aiMeta })
    expect(form.bannedWordsText).toBe('最好')
    expect(form.siteUrl).toBe('https://example.com')
    const payload = inputFromForm(form)
    expect(payload.id).toBe(entry().id)
    expect(payload.style).toEqual(entry().style)
    expect(payload.report).toEqual(entry().report)
    expect(payload.fields.niche).toEqual(entry().fields.niche)
    expect(payload.fields.audience).toEqual({ value: null, source: 'user', aiMeta: null })
  })

  it('builds a clone draft: fresh id, recorded source, report remapped to revision 1', () => {
    const form = formFromEntry(entry(), { clone: true })
    expect(form.editingId).toBeNull()
    expect(form.clonedFrom).toBe(entry().id)
    expect(form.report?.sourceRevision).toBe(1)
    expect(form.report?.editedByUser).toBe(true)
    const payload = inputFromForm(form)
    expect(payload.id).toBeUndefined()
    expect(payload.clonedFrom).toBe(entry().id)
  })
})

describe('inputFromForm', () => {
  it('trims values, drops empty ones to null, and clears AI metadata from touched fields', () => {
    const form = emptyForm()
    form.name = '  老李  '
    form.fields.audience = { value: '  ', source: 'ai', aiMeta: { promptVersion: 'persona-fill@1', at: 'x' } }
    form.fields.niche = { value: ' AI 工具 ', source: 'ai', aiMeta: { promptVersion: 'persona-fill@1', at: 'x' } }
    form.siteUrl = '  https://example.com  '
    form.bannedWordsText = '最好，第一\n，绝无仅有'
    const payload = inputFromForm(form)
    expect(payload.name).toBe('老李')
    // An AI field the user left empty keeps its provenance but carries no value.
    expect(payload.fields.audience).toEqual({ value: null, source: 'ai', aiMeta: { promptVersion: 'persona-fill@1', at: 'x' } })
    expect(payload.fields.niche).toEqual({ value: 'AI 工具', source: 'ai', aiMeta: { promptVersion: 'persona-fill@1', at: 'x' } })
    expect(payload.site.url).toBe('https://example.com')
    expect(payload.style.bannedWords).toEqual(['最好', '第一', '绝无仅有'])
  })

  it('joins and re-parses the word lists through the same separators', () => {
    const form = formFromEntry(entry())
    form.bannedWordsText = '最好；第一'
    expect(inputFromForm(form).style.bannedWords).toEqual(['最好', '第一'])
  })
})

describe('adoptField and parseWordList', () => {
  it('stamps the adoption instant and prompt version onto the adopted field', () => {
    const form = adoptField(emptyForm(), 'audience', '职场人群', 'persona-fill@1')
    expect(form.fields.audience.source).toBe('ai')
    expect(form.fields.audience.aiMeta?.promptVersion).toBe('persona-fill@1')
    expect(form.fields.audience.value).toBe('职场人群')
    expect(form.fields.niche.aiMeta).toBeNull()
  })

  it('splits word lists on newlines, commas, and semicolons', () => {
    expect(parseWordList('最好，第一\n绝无仅有, 别迟到；；别熬夜')).toEqual(['最好', '第一', '绝无仅有', '别迟到', '别熬夜'])
    expect(parseWordList('  ；  ')).toEqual([])
  })
})
