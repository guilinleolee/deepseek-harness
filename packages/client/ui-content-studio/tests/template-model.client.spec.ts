import { describe, expect, it } from 'vitest'
import {
  missingRequired, parseTemplatePack, reconcileVariables, renderTemplate, scanTemplateVariables,
  segmentTemplateBody,
} from '../src/client/template/model.ts'

const META = [
  { name: 'title', label: '标题', description: '', defaultValue: '默认标题', required: true },
  { name: 'hook', label: '钩子', description: '', defaultValue: '', required: false },
]

describe('segmentTemplateBody', () => {
  it('splits fenced blocks from text', () => {
    const segments = segmentTemplateBody('前文\n```js\nconst x = "{{v}}"\n```\n后文 {{v}}')
    expect(segments.map(segment => segment.code)).toEqual([false, true, true, true, false])
    expect(segments[4]?.text).toBe('后文 {{v}}')
  })

  it('keeps an unclosed fence as code to the end', () => {
    const segments = segmentTemplateBody('text\n~~~\n{{v}}')
    expect(segments[segments.length - 1]?.code).toBe(true)
  })
})

describe('scanTemplateVariables', () => {
  it('collects names outside code regions, first occurrence, deduplicated', () => {
    const body = '{{title}} 与 {{hook}}，再次 {{ title }}。\n```\n{{ghost}}\n```\n行内 `{{inline}}` 与 {{title}}'
    expect(scanTemplateVariables(body)).toEqual(['title', 'hook'])
  })

  it('treats a backslash-escaped placeholder as literal', () => {
    expect(scanTemplateVariables('\\{{title}} 与 {{hook}}')).toEqual(['hook'])
  })
})

describe('reconcileVariables', () => {
  it('keeps known metadata, synthesizes fresh entries, and parks unused ones', () => {
    const reconciled = reconcileVariables('{{title}} {{extra}}', [
      ...META,
      { name: 'ghost', label: '幽灵', description: '旧变量', defaultValue: '', required: false },
    ])
    expect(reconciled.active.map(variable => variable.name)).toEqual(['title', 'extra'])
    expect(reconciled.active[0]?.label).toBe('标题')
    expect(reconciled.active[1]).toEqual({ name: 'extra', label: 'extra', description: '', defaultValue: '', required: false })
    expect(reconciled.unused.map(variable => variable.name)).toEqual(['hook', 'ghost'])
  })
})

describe('renderTemplate', () => {
  it('substitutes values, falls back to defaults, keeps the rest visible', () => {
    const rendered = renderTemplate('# {{title}}\n{{hook}} {{missing}}', { title: '你好' }, META)
    expect(rendered.output).toBe('# 你好\n{{hook}} {{missing}}')
    expect(rendered.unresolved).toEqual(['hook', 'missing'])
    const withDefault = renderTemplate('{{hook}}', {}, [
      { name: 'hook', label: '钩子', description: '', defaultValue: '默认钩子', required: false },
    ])
    expect(withDefault.output).toBe('默认钩子')
    expect(withDefault.unresolved).toEqual([])
  })

  it('never substitutes inside code regions', () => {
    const rendered = renderTemplate('```\n{{title}}\n```\n{{title}}', { title: 'X' }, META)
    expect(rendered.output).toBe('```\n{{title}}\n```\nX')
  })

  it('renders a backslash-escaped placeholder literally', () => {
    const rendered = renderTemplate('\\{{title}}', { title: 'X' }, META)
    expect(rendered.output).toBe('{{title}}')
    expect(rendered.unresolved).toEqual([])
  })

  it('treats a blank filled value as empty and falls back to the default', () => {
    const rendered = renderTemplate('{{title}}', { title: '  ' }, META)
    expect(rendered.output).toBe('默认标题')
  })
})

describe('missingRequired', () => {
  it('names required variables without a filled value', () => {
    expect(missingRequired('{{title}} {{hook}}', META, { title: '有', hook: '' })).toEqual([])
    expect(missingRequired('{{title}} {{hook}}', META, { hook: '有' })).toEqual(['title'])
  })

  it('ignores required declarations the body no longer uses', () => {
    expect(missingRequired('{{hook}}', META, {})).toEqual([])
  })
})

describe('parseTemplatePack', () => {
  it('parses a valid pack', () => {
    const packDoc = { format: 'dsh-template-pack', formatVersion: 1, exportedAt: '2026-09-27T00:00:00.000Z', templates: [], tags: [] }
    const parsed = parseTemplatePack(JSON.stringify(packDoc))
    expect(parsed.kind).toBe('ok')
    if (parsed.kind === 'ok') expect(parsed.pack.templates).toEqual([])
  })

  it('rejects broken JSON, wrong envelopes, and missing lists', () => {
    expect(parseTemplatePack('{').kind).toBe('invalid')
    const wrongFormat = parseTemplatePack(JSON.stringify({ format: 'other', formatVersion: 1, templates: [], tags: [] }))
    expect(wrongFormat.kind).toBe('invalid')
    if (wrongFormat.kind === 'invalid') expect(wrongFormat.problem).toContain('dsh-template-pack')
    const wrongVersion = parseTemplatePack(JSON.stringify({ format: 'dsh-template-pack', formatVersion: 2, templates: [], tags: [] }))
    if (wrongVersion.kind === 'invalid') expect(wrongVersion.problem).toContain('formatVersion 2')
    const noLists = parseTemplatePack(JSON.stringify({ format: 'dsh-template-pack', formatVersion: 1 }))
    expect(noLists.kind).toBe('invalid')
  })
})
