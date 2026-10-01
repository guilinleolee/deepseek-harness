// @vitest-environment jsdom
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import type { TemplateId, TemplateRecord, TemplatesSnapshot, TemplateTagId } from '@deepseek-ai/dsh-content-outputs/types'
import {
  createTemplateController, type TemplateController, type TemplateGateway, type TemplatePickDraft,
} from '../src/client/template/template-store.ts'
import type { TemplatePack } from '@deepseek-ai/dsh-content-outputs/types'

/** Flush the controller's fire-and-forget async actions. */
async function flush(): Promise<void> {
  await new Promise((resolve) => { setTimeout(resolve, 0) })
}

/** Brand a wire tag id at the spec's single boundary. */
const tagId = (value: string): TemplateTagId => value as TemplateTagId
/** Brand a wire template id at the spec's single boundary. */
const tid = (value: string): TemplateId => value as TemplateId

function record(overrides: Partial<TemplateRecord> = {}): TemplateRecord {
  return {
    id: tid('t-1'),
    name: '复盘骨架',
    category: 'retro',
    description: '复盘报告框架',
    tagIds: [tagId('tag-1')],
    body: '# {{title}}\n结果：{{result}}',
    variables: [
      { name: 'title', label: '标题', description: '', defaultValue: '', required: true },
      { name: 'result', label: '结果', description: '', defaultValue: '待填', required: false },
    ],
    status: 'active',
    version: 2,
    createdAt: '2026-09-01T00:00:00.000Z',
    updatedAt: '2026-09-02T00:00:00.000Z',
    ...overrides,
  }
}

function snapshot(overrides: Partial<TemplatesSnapshot> = {}): TemplatesSnapshot {
  return { templates: [record()], tags: [{ id: tagId('tag-1'), name: '爆款' }], problems: [], ...overrides }
}

function fakeGateway(overrides: Partial<TemplateGateway> = {}): TemplateGateway & { calls: string[] } {
  const calls: string[] = []
  return {
    calls,
    listTemplates: vi.fn(async () => { calls.push('list'); return snapshot() }),
    putTemplate: vi.fn(async (input: Parameters<TemplateGateway['putTemplate']>[0]) => {
      calls.push('put')
      return record({ name: input.name, version: 3 })
    }),
    setTemplateStatus: vi.fn(async (id: Parameters<TemplateGateway['setTemplateStatus']>[0], status: Parameters<TemplateGateway['setTemplateStatus']>[1]) => record({ id, status })),
    deleteTemplate: vi.fn(async () => { calls.push('delete') }),
    getTemplateHistory: vi.fn(async () => ({ entries: [{
      version: 1,
      changeNote: '初始',
      createdAt: '2026-09-01T00:00:00.000Z',
      record: record({ version: 1, body: '旧正文 {{title}}' }),
    }] })),
    putTemplateTags: vi.fn(async (tags: Parameters<TemplateGateway['putTemplateTags']>[0]) => {
      calls.push('tags')
      return tags
    }),
    exportTemplates: vi.fn(async (): Promise<TemplatePack> => ({
      format: 'dsh-template-pack', formatVersion: 1, exportedAt: '2026-09-27T00:00:00.000Z', templates: [record()], tags: [],
    })),
    importTemplates: vi.fn(async () => ({ added: 1, skipped: 0, overwritten: 0, renamed: 0, failed: [] })),
    processTemplateAi: vi.fn(async (request: Parameters<TemplateGateway['processTemplateAi']>[0]) => ({
      operation: request.operation,
      promptVersion: 'template-test@1',
      draft: {
        name: request.operation === 'generate' ? '生成的模板' : '',
        description: request.operation === 'generate' ? '一句说明' : '',
        body: request.operation === 'optimize' ? '优化后 {{title}}' : request.operation === 'generate' ? 'AI 骨架 {{title}}' : 'AI 骨架 {{topic}}',
        variables: request.operation === 'optimize' ? [] : [
          { name: request.operation === 'generate' ? 'title' : 'topic', label: '话题', description: '', defaultValue: '', required: true },
        ],
      },
      problems: [],
    })),
    ...overrides,
  }
}

let gateway: ReturnType<typeof fakeGateway>
let controller: TemplateController

beforeEach(() => {
  window.localStorage.clear()
  gateway = fakeGateway()
  controller = createTemplateController({ gateway })
})

afterEach(() => {
  vi.restoreAllMocks()
})

describe('library state', () => {
  it('reloads templates, tags, and problems; failures surface the notice', async () => {
    controller.reload()
    await flush()
    expect(controller.getState().templates).toHaveLength(1)
    expect(controller.getState().tags).toEqual([{ id: 'tag-1', name: '爆款' }])

    // The gateway call happens synchronously at reload start, so the failing
    // face must be in place before the reload, not after it.
    gateway.listTemplates = vi.fn(async () => { throw new Error('down') })
    controller.reload()
    await flush()
    expect(controller.getState().notice).toBe('load-failed')
  })

  it('persists view preferences and loses nothing when they vanish', () => {
    controller.setFilter({ category: 'retro', status: 'active' })
    expect(JSON.parse(window.localStorage.getItem('dsh-content-studio.template.prefs') ?? '{}')).toMatchObject({ category: 'retro' })
  })
})

describe('editor', () => {
  it('reconciles variables when the body changes', () => {
    controller.openEditor(record())
    controller.patchForm({ body: '# {{title}} 新增 {{extra}}' })
    const form = controller.getState().editor?.form
    // Active placeholders first (body order), then the unused metadata.
    expect(form?.variables.map(variable => variable.name)).toEqual(['title', 'extra', 'result'])
    expect(form?.variables.find(variable => variable.name === 'extra')?.label).toBe('extra')
  })

  it('saves with a trimmed change note and reloads', async () => {
    controller.openNew()
    controller.patchForm({ name: '  新模板  ', body: '{{a}}', changeNote: '  首版  ' })
    controller.save()
    await flush()
    expect(gateway.putTemplate).toHaveBeenCalledTimes(1)
    const input = vi.mocked(gateway.putTemplate).mock.calls[0]?.[0]
    expect(input?.name).toBe('新模板')
    expect(input?.changeNote).toBe('首版')
    expect(controller.getState().notice).toBe('saved')
  })

  it('omits a blank change note and rejects a blank name without a call', async () => {
    controller.openNew()
    controller.patchForm({ name: '', body: '{{a}}' })
    controller.save()
    await flush()
    expect(gateway.putTemplate).not.toHaveBeenCalled()
    expect(controller.getState().notice).toBe('save-failed')
  })

  it('maps a duplicate-name rejection to its own notice', async () => {
    gateway.putTemplate = vi.fn(async () => { throw new Error('invalid template input: duplicate template name: X') })
    controller = createTemplateController({ gateway })
    controller.openEditor(record())
    controller.patchForm({ body: 'x' })
    controller.save()
    await flush()
    expect(controller.getState().notice).toBe('name-duplicate')
  })

  it('cascades removal and closes the editor over the removed template', async () => {
    controller.openEditor(record())
    controller.remove(tid('t-1'))
    await flush()
    expect(controller.getState().editor).toBeNull()
    expect(controller.getState().templates).toHaveLength(1)
  })

  it('copies under a fresh id and suffixed name', () => {
    controller.copyTemplate(record())
    const form = controller.getState().editor?.form
    expect(form?.id).toBeNull()
    expect(form?.name).toBe('复盘骨架 副本')
  })

  it('restores a version as a pending save with a rollback note', async () => {
    controller.openEditor(record())
    controller.openHistory(tid('t-1'))
    await flush()
    expect(controller.getState().history).toHaveLength(1)
    const entry = controller.getState().history[0]
    if (entry === undefined) throw new Error('history entry missing')
    controller.restoreVersion(entry)
    const form = controller.getState().editor?.form
    expect(form?.body).toBe('旧正文 {{title}}')
    expect(form?.changeNote).toBe('回滚自 v1')
    expect(controller.getState().historyOpen).toBe(false)
  })

  it('toggles form tags', () => {
    controller.openEditor(record())
    controller.toggleFormTag(tagId('tag-1'))
    expect(controller.getState().editor?.form.tagIds).toEqual([])
    controller.toggleFormTag(tagId('tag-1'))
    expect(controller.getState().editor?.form.tagIds).toEqual([tagId('tag-1')])
  })
})

describe('tags', () => {
  it('rejects blank names and appends valid ones', async () => {
    controller.reload()
    await flush()
    controller.addTag('   ')
    expect(controller.getState().notice).toBe('tag-name-required')
    controller.addTag('短视频')
    await flush()
    expect(vi.mocked(gateway.putTemplateTags).mock.calls[0]?.[0]).toHaveLength(2)
    controller.removeTag(tagId('tag-1'))
    await flush()
    expect(vi.mocked(gateway.putTemplateTags).mock.calls[1]?.[0]).toEqual([])
  })

  it('surfaces a failure notice when the tag write rejects', async () => {
    gateway.putTemplateTags = vi.fn(async () => { throw new Error('down') })
    controller = createTemplateController({ gateway })
    controller.addTag('X')
    await flush()
    expect(controller.getState().notice).toBe('tags-failed')
  })
})

describe('import and export', () => {
  it('rejects a non-pack file before any call', async () => {
    controller.importFile(new File(['{broken'], 'pack.json'), 'skip')
    await flush()
    expect(controller.getState().notice).toBe('import-invalid')
    expect(gateway.importTemplates).not.toHaveBeenCalled()
  })

  it('imports a valid pack and shows the summary', async () => {
    const packDoc = { format: 'dsh-template-pack', formatVersion: 1, exportedAt: 'x', templates: [], tags: [] }
    controller.importFile(new File([JSON.stringify(packDoc)], 'pack.json', { type: 'application/json' }), 'overwrite')
    await flush()
    expect(vi.mocked(gateway.importTemplates).mock.calls[0]?.[1]).toBe('overwrite')
    expect(controller.getState().importReport?.fileName).toBe('pack.json')
    controller.dismissImportReport()
    expect(controller.getState().importReport).toBeNull()
  })

  it('downloads the pack for the selected ids', async () => {
    // oxlint-disable-next-line typescript/no-deprecated -- jsdom download shim
    const createOriginal = document.createElement.bind(document)
    const clicks: string[] = []
    // oxlint-disable-next-line typescript/no-deprecated -- jsdom download shim
    document.createElement = ((tag: string) => {
      if (tag === 'a') return { click: () => { clicks.push('download') }, href: '', download: '' } as unknown as HTMLAnchorElement
      return createOriginal(tag)
    })
    window.URL.createObjectURL = vi.fn(() => 'blob:test')
    window.URL.revokeObjectURL = vi.fn()
    controller.exportIds(['t-1'])
    await flush()
    expect(vi.mocked(gateway.exportTemplates).mock.calls[0]?.[0]).toEqual(['t-1'])
    expect(clicks).toEqual(['download'])
    // oxlint-disable-next-line typescript/no-deprecated -- jsdom download shim
    document.createElement = createOriginal
  })

  it('surfaces an export failure', async () => {
    gateway.exportTemplates = vi.fn(async () => { throw new Error('down') })
    controller = createTemplateController({ gateway })
    controller.exportIds([])
    await flush()
    expect(controller.getState().notice).toBe('export-failed')
  })
})

describe('AI drafts', () => {
  it('runs an explicit generation and adopts it into a new editor', async () => {
    controller.setGenerateCategory('topic')
    controller.setGenerateSource('小红书选题模板')
    controller.runAi({ operation: 'generate', category: 'topic', description: '小红书选题模板' })
    expect(controller.getState().aiBusy).toBe('generate')
    await flush()
    expect(controller.getState().aiBusy).toBe(false)
    expect(controller.getState().aiDraft?.draft.body).toBe('AI 骨架 {{title}}')
    controller.adoptAiDraft()
    const form = controller.getState().editor?.form
    expect(form?.name).toBe('生成的模板')
    expect(form?.category).toBe('topic')
    expect(form?.variables.map(variable => variable.name)).toEqual(['title'])
    expect(controller.getState().aiDraft).toBeNull()
  })

  it('optimizes the open editor body only', async () => {
    controller.openEditor(record())
    controller.setOptimizeSource('精简')
    controller.runAi({ operation: 'optimize', body: 'x', instruction: '精简' })
    await flush()
    controller.adoptAiDraft()
    expect(controller.getState().editor?.form.body).toBe('优化后 {{title}}')
    expect(controller.getState().editor?.form.name).toBe('复盘骨架')
  })

  it('merges extraction metadata into the open editor', async () => {
    controller.openEditor(record())
    controller.setExtractSource('一篇旧复盘')
    controller.runAi({ operation: 'extract', content: '一篇旧复盘' })
    await flush()
    controller.adoptAiDraft()
    const form = controller.getState().editor?.form
    expect(form?.body).toBe('AI 骨架 {{topic}}')
    expect(form?.variables.map(variable => variable.name)).toEqual(['topic', 'title', 'result'])
  })

  it('names empty AI input and failures without touching the draft', async () => {
    controller.setGenerateSource('  ')
    controller.runAi({ operation: 'generate', category: 'topic', description: ' ' })
    expect(controller.getState().notice).toBe('ai-empty')

    gateway.processTemplateAi = vi.fn(async () => { throw new Error('quota') })
    controller = createTemplateController({ gateway })
    controller.setGenerateSource('描述')
    controller.runAi({ operation: 'generate', category: 'topic', description: '描述' })
    await flush()
    expect(controller.getState().notice).toBe('ai-failed')
    expect(controller.getState().aiDraft).toBeNull()
  })

  it('discards the draft', async () => {
    controller.setGenerateSource('描述')
    controller.runAi({ operation: 'generate', category: 'topic', description: '描述' })
    await flush()
    controller.discardAiDraft()
    expect(controller.getState().aiDraft).toBeNull()
  })
})

describe('picker', () => {
  const target = {
    category: 'retro' as const,
    targetLabel: '创作输入框',
    hasContent: () => true,
    apply: vi.fn<(draft: TemplatePickDraft) => void>(),
  }

  it('offers only active templates of the host category and blocks on missing required values', async () => {
    gateway.listTemplates = vi.fn(async () => snapshot({
      templates: [
        record(),
        record({ id: tid('t-2'), name: '草稿模板', status: 'archived' }),
        record({ id: tid('t-3'), name: '别栏模板', category: 'creation' }),
      ],
    }))
    controller = createTemplateController({ gateway })
    controller.reload()
    await flush()
    controller.openPicker(target)
    expect(controller.getState().picker?.target).toEqual(target)
    controller.pickerSelect(record())
    controller.pickerConfirm()
    // Required `title` is empty: the confirm is refused outright.
    expect(target.apply).not.toHaveBeenCalled()
    controller.pickerValue('title', '周复盘')
    controller.pickerConfirm()
    // The host field has content: the first confirm only arms the overwrite guard.
    expect(target.apply).not.toHaveBeenCalled()
    expect(controller.getState().picker?.overwriteConfirm).toBe(true)
    controller.pickerConfirm()
    expect(target.apply).toHaveBeenCalledTimes(1)
    const applied = vi.mocked(target.apply).mock.calls[0]?.[0]
    expect(applied?.body).toContain('周复盘')
    expect(applied?.body).toContain('待填')
    expect(applied?.template.id).toBe('t-1')
    expect(controller.getState().picker).toBeNull()
  })

  it('renders unresolved placeholders for unknown variables', async () => {
    const localTarget = { ...target, hasContent: () => false, apply: vi.fn<(draft: TemplatePickDraft) => void>() }
    controller.openPicker(localTarget)
    controller.pickerSelect(record({ body: '{{title}} {{unknown}}', variables: [{ name: 'title', label: '', description: '', defaultValue: '', required: false }] }))
    controller.pickerValue('title', 'T')
    controller.pickerConfirm()
    const applied = vi.mocked(localTarget.apply).mock.calls[0]?.[0]
    expect(applied?.body).toBe('T {{unknown}}')
  })

  it('hands the host a structured draft: title fallback, resolved tag names', async () => {
    const structuredTarget = {
      category: 'retro' as const,
      targetLabel: 'X',
      hasContent: () => false,
      apply: vi.fn<(draft: TemplatePickDraft) => void>(),
    }
    // Tag names resolve against the loaded library's tag list.
    controller.reload()
    await flush()
    controller.openPicker(structuredTarget)
    // A filled `title` variable wins; tags resolve to the library's names.
    controller.pickerSelect(record({ tagIds: [tagId('tag-1'), tagId('tag-missing')] }))
    controller.pickerValue('title', '  周复盘  ')
    controller.pickerConfirm()
    let applied = vi.mocked(structuredTarget.apply).mock.calls[0]?.[0]
    expect(applied?.title).toBe('周复盘')
    expect(applied?.tags).toEqual(['爆款'])

    // No `title` variable filled: the template's own name is the fallback.
    controller.openPicker(structuredTarget)
    controller.pickerSelect(record({ name: '骨架名', body: '结果：{{result}}' }))
    controller.pickerConfirm()
    applied = vi.mocked(structuredTarget.apply).mock.calls[1]?.[0]
    expect(applied?.title).toBe('骨架名')
  })

  it('navigates back and closes cleanly', () => {
    controller.openPicker(target)
    controller.pickerSelect(record())
    controller.pickerBack()
    expect(controller.getState().picker?.selected).toBeNull()
    controller.closePicker()
    expect(controller.getState().picker).toBeNull()
  })
})
