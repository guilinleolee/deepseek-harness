import { describe, expect, it } from 'vitest'
import {
  parseTemplateExtractOutput, parseTemplateGenerateOutput, parseTemplateOptimizeOutput,
  parseTemplateVariablesOutput,
} from '../src/template/ai.ts'

describe('parseTemplateVariablesOutput', () => {
  it('parses valid entries and defaults required to true', () => {
    const parsed = parseTemplateVariablesOutput([
      { name: 'title', label: '标题', description: '笔记标题', defaultValue: '默认', required: false },
      { name: 'hook', label: '钩子' },
    ])
    expect(parsed.variables).toEqual([
      { name: 'title', label: '标题', description: '笔记标题', defaultValue: '默认', required: false },
      { name: 'hook', label: '钩子', description: '', defaultValue: '', required: true },
    ])
    expect(parsed.problems).toEqual([])
  })

  it('drops unusable names into problems and dedupes by name', () => {
    const parsed = parseTemplateVariablesOutput([
      { name: '9bad' },
      { name: 'title' },
      { name: 'title', label: '重复' },
      'not-an-object',
    ])
    expect(parsed.variables.map(variable => variable.name)).toEqual(['title'])
    expect(parsed.variables[0]?.label).toBe('title')
    expect(parsed.problems).toHaveLength(2)
  })

  it('names a non-array value as one problem', () => {
    const parsed = parseTemplateVariablesOutput('nope')
    expect(parsed.variables).toEqual([])
    expect(parsed.problems).toEqual(['variables is not an array'])
  })
})

describe('parseTemplateGenerateOutput', () => {
  it('parses a fenced full draft', () => {
    const text = '```json\n{"name":"爆款骨架","description":"三段式","body":"# {{title}}","variables":[{"name":"title","label":"标题"}]}\n```'
    const parsed = parseTemplateGenerateOutput(text)
    expect(parsed.draft.name).toBe('爆款骨架')
    expect(parsed.draft.body).toBe('# {{title}}')
    expect(parsed.draft.variables).toHaveLength(1)
    expect(parsed.problems).toEqual([])
  })

  it('cuts prose-wrapped JSON between the outermost braces', () => {
    const text = '好的，这是模板：\n{"body":"{{a}}","variables":[]}\n请查收'
    expect(parseTemplateGenerateOutput(text).draft.body).toBe('{{a}}')
  })

  it('rejects an answer without a body', () => {
    expect(() => parseTemplateGenerateOutput('{"name":"x"}')).toThrow(/no body/)
  })
})

describe('parseTemplateOptimizeOutput', () => {
  it('returns a body-only draft', () => {
    const parsed = parseTemplateOptimizeOutput('{"body":"精简后"}')
    expect(parsed.draft).toEqual({ name: '', description: '', body: '精简后', variables: [] })
    expect(parsed.problems).toEqual([])
  })

  it('rejects an empty body', () => {
    expect(() => parseTemplateOptimizeOutput('{"body":"  "}')).toThrow(/no body/)
  })
})

describe('parseTemplateExtractOutput', () => {
  it('parses the skeleton and its proposed variables', () => {
    const parsed = parseTemplateExtractOutput('{"body":"复盘：{{theme}}","variables":[{"name":"theme","description":"复盘主题"}]}')
    expect(parsed.draft.body).toBe('复盘：{{theme}}')
    expect(parsed.draft.variables[0]?.required).toBe(true)
  })

  it('rejects an answer without a body', () => {
    expect(() => parseTemplateExtractOutput('{"variables":[]}')).toThrow(/no body/)
  })
})
