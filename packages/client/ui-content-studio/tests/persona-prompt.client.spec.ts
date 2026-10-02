/**
 * The packed persona prompt (`persona-prompt@1`): deterministic rendering,
 * provenance marks, hard-constraint sections, and empty-line drops.
 */
import { describe, expect, it } from 'vitest'
import type { PersonaEntry, PersonaField, PersonaFieldKey } from '@deepseek-ai/dsh-content-outputs/types'
import { PERSONA_FIELD_KEYS } from '@deepseek-ai/dsh-content-outputs/types'
import { PERSONA_PROMPT_VERSION, renderEntryPrompt, renderPersonaPrompt } from '../src/client/persona/prompt.ts'

function fields(overrides: Partial<Record<PersonaFieldKey, { value: string | null; source: 'user' | 'ai' }>> = {}): PersonaEntry['fields'] {
  const fields = {} as Record<PersonaFieldKey, PersonaField>
  for (const key of PERSONA_FIELD_KEYS) {
    const override = overrides[key]
    fields[key] = override === undefined
      ? { value: null, source: 'user', aiMeta: null }
      : override.source === 'ai'
        ? { value: override.value, source: 'ai', aiMeta: { promptVersion: 'persona-fill@1', at: '2026-09-25T00:00:00.000Z' } }
        : { value: override.value, source: 'user', aiMeta: null }
  }
  return fields
}

const base = {
  name: '老李',
  revision: 3,
  fields: fields({
    whoAmI: { value: '前大厂工程师', source: 'user' },
    audience: { value: '25-40 岁职场人群', source: 'ai' },
    goal: { value: '涨粉', source: 'user' },
    monetize: { value: '带货', source: 'user' },
  }),
  style: { preset: 'humor', customText: null, strength: 'light', bannedWords: ['最好'], redLines: ['医疗', '金融'] },
} as const

describe('renderPersonaPrompt', () => {
  it('renders the packed prompt with provenance marks and hard constraints', () => {
    const prompt = renderPersonaPrompt(base)
    expect(prompt).toContain('【账号人设 · 老李（v3）】')
    expect(prompt).toContain('身份/背景：前大厂工程师')
    expect(prompt).toContain('目标受众：25-40 岁职场人群（AI 推断，供参考）')
    expect(prompt).toContain('运营目标/变现：涨粉；带货')
    expect(prompt).toContain('表达风格：幽默网感（遵循强度：轻度遵循：倾向参考，允许自然偏离）')
    expect(prompt).toContain('禁用词（硬约束，输出中不得出现）：最好')
    expect(prompt).toContain('内容红线（触线即不合格）：医疗；金融')
    // Empty fields drop their whole line.
    expect(prompt).not.toContain('更新节奏')
    expect(prompt).not.toContain('赛道')
  })

  it('prefers the custom style text and renders the strict wording', () => {
    const prompt = renderPersonaPrompt({ ...base, style: { ...base.style, preset: null, customText: '像朋友聊天', strength: 'strict' } })
    expect(prompt).toContain('表达风格：像朋友聊天（遵循强度：严格遵循：硬约束，输出前逐条自检）')
  })

  it('is byte-for-byte deterministic', () => {
    expect(renderPersonaPrompt(base)).toBe(renderPersonaPrompt(base))
    expect(PERSONA_PROMPT_VERSION).toBe('persona-prompt@1')
  })
})

describe('renderEntryPrompt', () => {
  it('renders a stored entry from its saved revision', () => {
    const entry = {
      id: 'p-1', name: '老李', platforms: [], accountStage: 'fresh', revision: 2, digest: '',
      fields: fields(), links: [], site: { url: null, pastedText: null },
      style: { preset: null, customText: null, strength: 'light', bannedWords: [], redLines: [] },
      assets: { resumeText: null, resumeName: null }, report: null, clonedFrom: null,
      createdAt: '', updatedAt: '',
    } as unknown as PersonaEntry
    const prompt = renderEntryPrompt(entry)
    expect(prompt).toContain('【账号人设 · 老李（v2）】')
    // An entry with nothing filled renders just the header line.
    expect(prompt.split('\n')).toHaveLength(1)
  })
})
