// @vitest-environment jsdom
/**
 * The topic-bank view surface: the table and kanban faces over SplitDetail,
 * the detail panel (AI entry disabled, provenance snapshot), create/edit/
 * delete flows with the schedule cascade and one-way plan-date linkage,
 * batch actions, Markdown export, and the versioned localStorage config
 * migration. The gateway is an in-memory fake with the store's upsert
 * semantics so every flow asserts real post-write state.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { ContentTopicsSnapshot, TopicItem, TopicItemInput } from '@deepseek-ai/dsh-content-topics/types'
import type { ScheduleItemInput } from '@deepseek-ai/dsh-content-schedule/types'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import { TopicBankView, type TopicBankGateway, type TopicBankViewProps } from '../src/client/TopicBankView.tsx'
import { todayDate } from '../src/client/calendar.ts'
import { manualTopicInput } from '../src/client/topic-bank.ts'
import type { TemplateController, TemplatePickDraft, TemplatePickTarget } from '../src/client/template/template-store.ts'
import type { TemplateId } from '@deepseek-ai/dsh-content-outputs/types'
import type { PickedTopic } from '../src/client/studio-store.ts'
import { en, zh } from '../src/client/locales.ts'

const CONFIG_KEY = 'dsh-content-studio.topicBank.config'

afterEach(() => {
  cleanup()
  window.localStorage.clear()
})

/** One stored topic with every field overridable. */
function topic(id: string, overrides: Partial<TopicItem> = {}): TopicItem {
  return {
    id: id as TopicItem['id'],
    title: `选题 ${id}`,
    oneLiner: null,
    status: 'idea',
    source: { type: 'manual', refId: null, url: null, snapshot: null },
    tags: [],
    description: null,
    score: null,
    planDate: null,
    scheduleItemId: null,
    topicDir: null,
    createdAt: '2026-09-24T00:00:00.000Z',
    updatedAt: '2026-09-25T00:00:00.000Z',
    ...overrides,
  }
}

/** The default two-topic bank: one bare manual idea, one rich gather topic. */
function defaultBank(today: string): readonly TopicItem[] {
  return [
    topic('t-1'),
    topic('t-2', {
      title: 'AI 工具',
      status: 'todo',
      source: { type: 'gather', refId: 'm-1', url: 'https://a.example/x', snapshot: { title: '素材标题', summary: '素材摘要', capturedAt: '2026-09-20T00:00:00.000Z' } },
      tags: ['AI'],
      score: { total: 7.5, source: 'manual', factors: null, evaluatedAt: '2026-09-25T01:00:00.000Z' },
      planDate: today,
      scheduleItemId: 'sched-9',
      description: '差异点说明',
    }),
  ]
}

/** An in-memory fake of the contentTopics Remote's upsert semantics. */
function fakeTopics(items: readonly TopicItem[]) {
  const state = { items: [...items] }
  const list = vi.fn(async (): Promise<ContentTopicsSnapshot> => ({ file: '_topics.json', items: [...state.items], problems: [] }))
  const put = vi.fn(async (input: TopicItemInput): Promise<ContentTopicsSnapshot> => {
    const now = new Date().toISOString()
    const id = (input.id ?? `t-${state.items.length + 1}`) as TopicItem['id']
    const exists = state.items.some(item => item.id === id)
    const stored: TopicItem = {
      ...input,
      id,
      tags: [...input.tags],
      createdAt: exists ? state.items.find(item => item.id === id)?.createdAt ?? now : now,
      updatedAt: now,
    }
    state.items = exists ? state.items.map(item => item.id === id ? stored : item) : [stored, ...state.items]
    return { file: '_topics.json', items: [...state.items], problems: [] }
  })
  const remove = vi.fn(async (id: string): Promise<ContentTopicsSnapshot> => {
    state.items = state.items.filter(item => item.id !== id)
    return { file: '_topics.json', items: [...state.items], problems: [] }
  })
  return { gateway: { list, put, remove } satisfies TopicBankGateway, list, put, remove, state }
}

/** Localized `t` with `{name}` interpolation, matching the runtime's contract. */
function makeT(): PropsLocale<'content-studio'>['t'] {
  const dict = en as Record<string, string>
  return (key, params) => {
    let text = dict[key] ?? key
    for (const [name, value] of Object.entries(params ?? {})) text = text.replaceAll(`{${name}}`, String(value))
    return text
  }
}

/** Render the view over one fake gateway with stubbed injected faces; the
 * returned handles are the actual stubs the view received. */
function renderView(
  bank: TopicBankGateway,
  overrides: Partial<TopicBankViewProps> = {},
) {
  const schedule = {
    put: vi.fn(async (_input: ScheduleItemInput): Promise<unknown> => undefined),
    remove: vi.fn(async (_id: string): Promise<unknown> => undefined),
  }
  const onStartCreate = vi.fn((_topic: PickedTopic): void => {})
  const props = {
    topics: bank,
    schedule,
    onStartCreate,
    writeExport: vi.fn(async (_theme: string, _file: string, _content: string): Promise<unknown> => ({ truncated: false })),
    listThemes: vi.fn(async (): Promise<readonly string[]> => ['theme-a']),
    pickCapability: vi.fn(),
    t: makeT(),
    ...overrides,
  }
  render(<TopicBankView {...props} />)
  return {
    schedule,
    onStartCreate,
    writeExport: props.writeExport,
    listThemes: props.listThemes,
  }
}

async function renderBank(today: string, overrides: Partial<TopicBankViewProps> = {}) {
  const fake = fakeTopics(defaultBank(today))
  const handles = renderView(fake.gateway, overrides)
  await waitFor(() => {
    expect(screen.getByText('AI 工具')).toBeTruthy()
  })
  return { ...handles, fake }
}

describe('TopicBankView', () => {
  it('renders the table with both topics, the count, and the detail placeholder', async () => {
    await renderBank(todayDate())
    expect(screen.getByText(en['topicBank.count'].replace('{n}', '2'))).toBeTruthy()
    // The score header reads twice (column head plus filter label).
    expect(screen.getAllByText(en['topicBank.column.score']).length).toBeGreaterThanOrEqual(1)
    expect(screen.getByText(en['topicBank.detail.empty'])).toBeTruthy()
    // Unscored topic says so; the scored one shows its total.
    expect(screen.getByText(en['topic.score.none'])).toBeTruthy()
    expect(screen.getByText('7.5')).toBeTruthy()
  })

  it('renders the error state with a working retry', async () => {
    const fake = fakeTopics(defaultBank(todayDate()))
    fake.gateway.list.mockRejectedValueOnce(new Error('disk gone'))
    renderView(fake.gateway)
    await waitFor(() => {
      expect(screen.getByText(`${en['topicBank.error']}: disk gone`)).toBeTruthy()
    })
    await act(async () => {
      fireEvent.click(screen.getByText(en['library.retry']))
    })
    await waitFor(() => {
      expect(screen.getByText('AI 工具')).toBeTruthy()
    })
  })

  it('opens the guide page with the inherited capability cards and a working create flow', async () => {
    const fake = fakeTopics([])
    renderView(fake.gateway)
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.guide.hint'])).toBeTruthy()
    })
    // The two cards inherited from the retired 选题规划 view.
    expect(screen.getByText(en['cap.hotspot.title'])).toBeTruthy()
    expect(screen.getByText(en['cap.calendar-plan.title'])).toBeTruthy()
    fireEvent.click(screen.getByText(en['topicBank.new']))
    // Title-only create: an empty title is named, a filled one creates into idea.
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.save']))
    })
    expect(screen.getByText(en['topicBank.error.titleRequired'])).toBeTruthy()
    fireEvent.change(screen.getByLabelText(en['topicBank.field.title']), { target: { value: '全新选题' } })
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.save']))
    })
    expect(fake.gateway.put).toHaveBeenCalledWith(manualTopicInput('全新选题'))
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.notice.created'])).toBeTruthy()
      expect(screen.getByText('全新选题')).toBeTruthy()
    })
  })

  it('prefills the create form from a template pick and carries the optional fields on save', async () => {
    // The picker modal lives at the workbench surface; the view's side of the
    // contract is the captured target, which the test applies a structured
    // draft to — exactly what a confirmed pick hands over.
    const targets: TemplatePickTarget[] = []
    const templateLibrary = {
      openPicker: vi.fn((target: TemplatePickTarget): void => { targets.push(target) }),
    } as unknown as TemplateController
    const fake = fakeTopics([])
    renderView(fake.gateway, { templateLibrary })
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.guide.hint'])).toBeTruthy()
    })
    fireEvent.click(screen.getByText(en['topicBank.useTemplate']))
    expect(targets).toHaveLength(1)
    const target = targets[0]
    if (target === undefined) throw new Error('picker target missing')
    expect(target.category).toBe('topic')
    const apply = target.apply
    if (apply === undefined) throw new Error('picker target has no apply')
    const draft: TemplatePickDraft = {
      title: '模板化选题',
      body: '核心切入：{{angle}}',
      tags: ['爆款', '小红书'],
      values: {},
      template: {
        id: 'tpl-1' as TemplateId, name: '选题模板', category: 'topic', description: '', tagIds: [],
        body: '核心切入：{{angle}}',
        variables: [], status: 'active', version: 1,
        createdAt: '2026-09-27T00:00:00.000Z', updatedAt: '2026-09-27T00:00:00.000Z',
      },
    }
    act(() => { apply(draft) })
    // The prefilled fields surface in the create form for review.
    const title = screen.getByLabelText(en['topicBank.field.title']) as HTMLInputElement
    expect(title.value).toBe('模板化选题')
    const description = screen.getByLabelText(en['topicBank.field.description']) as HTMLTextAreaElement
    expect(description.value).toBe('核心切入：{{angle}}')
    // Saving carries the optional fields, not just the title.
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.save']))
    })
    expect(fake.gateway.put).toHaveBeenCalledWith(expect.objectContaining({
      title: '模板化选题',
      description: '核心切入：{{angle}}',
      tags: ['爆款', '小红书'],
      oneLiner: null,
    }))
  })

  it('shows the detail panel with the disabled AI entry, snapshot, and create handoff', async () => {
    const { onStartCreate } = await renderBank(todayDate())
    fireEvent.click(screen.getByText('AI 工具'))
    const detail = screen.getByRole('region', { name: en['topicBank.detail.label'] })
    // The AI entry renders disabled with its pending-version title.
    const ai = within(detail).getByText(en['topicBank.aiOptimize']).closest('button')
    expect(ai?.disabled).toBe(true)
    expect(ai?.title).toBe(en['topicBank.aiPending'])
    // Provenance: the source family, the external link, the read-only snapshot.
    expect(detail.textContent).toContain(en['topic.source.gather'])
    expect(within(detail).getByText(en['topicBank.snapshotLabel'])).toBeTruthy()
    expect(within(detail).getByText('素材标题')).toBeTruthy()
    expect(within(detail).getByText('素材摘要')).toBeTruthy()
    const link = within(detail).getByRole('link', { name: en['topicBank.openOriginal'] }) as HTMLAnchorElement
    expect(link.href).toBe('https://a.example/x')
    // Start creating hands the brief fields over.
    await act(async () => {
      fireEvent.click(within(detail).getByText(en['topicBank.startCreate']))
    })
    expect(onStartCreate).toHaveBeenCalledWith({
      id: 't-2', title: 'AI 工具', oneLiner: null, description: '差异点说明',
    })
  })

  it('edits a topic via the edit form', async () => {
    const { fake } = await renderBank(todayDate())
    fireEvent.click(screen.getByText('AI 工具'))
    const detail = screen.getByRole('region', { name: en['topicBank.detail.label'] })
    fireEvent.click(within(detail).getByText(en['topicBank.edit']))
    const score = screen.getByLabelText(en['topicBank.field.score']) as HTMLInputElement
    expect(score.value).toBe('7.5')
    // Out of range: named in the form, nothing written.
    fireEvent.change(score, { target: { value: '12' } })
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.save']))
    })
    expect(screen.getByText(en['topicBank.error.scoreRange'])).toBeTruthy()
    expect(fake.gateway.put).not.toHaveBeenCalled()
    // In range: a manual score with no factors.
    fireEvent.change(score, { target: { value: '9' } })
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.save']))
    })
    expect(fake.gateway.put).toHaveBeenCalledTimes(1)
    const input = fake.put.mock.calls[0]![0]
    expect(input.score).toMatchObject({ total: 9, source: 'manual', factors: null })
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.notice.saved'])).toBeTruthy()
    })
  })

  it('deletes with the schedule cascade default-checked and honored', async () => {
    const { schedule } = await renderBank(todayDate())
    fireEvent.click(screen.getByText('AI 工具'))
    fireEvent.click(within(screen.getByRole('region', { name: en['topicBank.detail.label'] })).getByText(en['topicBank.delete']))
    const confirm = screen.getByRole('alertdialog', { name: en['topicBank.confirmDelete'] })
    const checkbox = within(confirm).getByLabelText(en['topicBank.deleteAlsoSchedule']) as HTMLInputElement
    expect(checkbox.checked).toBe(true)
    await act(async () => {
      fireEvent.click(within(confirm).getByText(en['topicBank.deleteConfirm']))
    })
    expect(schedule.remove).toHaveBeenCalledWith('sched-9')
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.notice.deleted'])).toBeTruthy()
    })
    expect(screen.queryByText('AI 工具')).toBeNull()
  })

  it('deletes without touching the calendar when the cascade is unchecked', async () => {
    const { schedule } = await renderBank(todayDate())
    fireEvent.click(screen.getByText('AI 工具'))
    fireEvent.click(within(screen.getByRole('region', { name: en['topicBank.detail.label'] })).getByText(en['topicBank.delete']))
    const confirm = screen.getByRole('alertdialog', { name: en['topicBank.confirmDelete'] })
    fireEvent.click(within(confirm).getByLabelText(en['topicBank.deleteAlsoSchedule']))
    await act(async () => {
      fireEvent.click(within(confirm).getByText(en['topicBank.deleteConfirm']))
    })
    expect(schedule.remove).not.toHaveBeenCalled()
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.notice.deleted'])).toBeTruthy()
    })
  })

  it('links a new plan date through the schedule gateway and stores the id', async () => {
    const today = todayDate()
    const { fake, schedule } = await renderBank(todayDate())
    fireEvent.click(screen.getByText('选题 t-1'))
    fireEvent.click(within(screen.getByRole('region', { name: en['topicBank.detail.label'] })).getByText(en['topicBank.edit']))
    fireEvent.change(screen.getByLabelText(en['topicBank.field.planDate']), { target: { value: today } })
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.save']))
    })
    expect(schedule.put).toHaveBeenCalledTimes(1)
    const scheduleInput = schedule.put.mock.calls[0]![0]
    expect(scheduleInput).toMatchObject({ date: today, time: null, status: 'idea', kind: 'content', topic: null })
    expect(fake.gateway.put).toHaveBeenCalledTimes(1)
    const topicInput = fake.put.mock.calls[0]![0]
    expect(topicInput.scheduleItemId).toBe(scheduleInput.id)
    expect(topicInput.planDate).toBe(today)
  })

  it('drags a kanban card across columns, rolling back on a failed write', async () => {
    const today = todayDate()
    const first = renderBank(today)
    const { fake } = await first
    fireEvent.change(screen.getByLabelText(en['topicBank.view.aria']), { target: { value: 'kanban' } })
    expect(screen.getByText(en['topicBank.kanbanHint'])).toBeTruthy()
    // Column heads are the only SPANs carrying a status label in kanban view;
    // the select options render the same words but are OPTION elements.
    const columnOf = (status: string): HTMLElement => {
      const head = screen.getAllByText(status).find(candidate => candidate.tagName === 'SPAN')
      if (head === undefined) throw new Error(`column not found: ${status}`)
      return head.parentElement!.parentElement as HTMLElement
    }
    const ideaColumn = columnOf(en['topic.status.idea'])
    const todoColumn = columnOf(en['topic.status.todo'])
    const card = screen.getByRole('button', { name: '选题 t-1' })
    expect(within(ideaColumn).getByRole('button', { name: '选题 t-1' })).toBeTruthy()

    // A failed write rolls the card back and toasts.
    fake.put.mockRejectedValueOnce(new Error('locked'))
    await act(async () => {
      fireEvent.dragStart(card)
      fireEvent.dragOver(todoColumn)
      fireEvent.drop(todoColumn)
    })
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.notice.failed'].replace('{detail}', 'locked'))).toBeTruthy()
    })
    expect(within(ideaColumn).getByRole('button', { name: '选题 t-1' })).toBeTruthy()

    // A successful write moves it.
    await act(async () => {
      fireEvent.dragStart(card)
      fireEvent.drop(todoColumn)
    })
    expect(fake.put).toHaveBeenLastCalledWith(expect.objectContaining({ id: 't-1', status: 'todo' }))
    await waitFor(() => {
      expect(within(todoColumn).getByRole('button', { name: '选题 t-1' })).toBeTruthy()
    })
  })

  it('runs the batch status edit, tag append, selection export, and clear', async () => {
    const today = todayDate()
    const { writeExport, fake } = await renderBank(today)
    fireEvent.click(screen.getByLabelText(`${en['topicBank.batch.select']}: 选题 t-1`))
    fireEvent.click(screen.getByLabelText(`${en['topicBank.batch.select']}: AI 工具`))
    expect(screen.getByText(en['topicBank.batch.selected'].replace('{n}', '2'))).toBeTruthy()
    // Batch status.
    fireEvent.change(screen.getByLabelText(en['topicBank.batch.setStatus']), { target: { value: 'shelved' } })
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.batch.apply']))
    })
    expect(fake.put).toHaveBeenCalledTimes(2)
    expect(fake.put.mock.calls[0]?.[0].status).toBe('shelved')
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.notice.batchDone'])).toBeTruthy()
    })
    // Selection cleared after the batch.
    expect(screen.queryByText(en['topicBank.batch.selected'].replace('{n}', '2'))).toBeNull()
    // Batch tag append re-checks and appends a deduplicated union.
    fireEvent.click(screen.getByLabelText(`${en['topicBank.batch.select']}: AI 工具`))
    fireEvent.change(screen.getByLabelText(en['topicBank.batch.tagsPlaceholder']), { target: { value: '职场, AI' } })
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.batch.applyTags']))
    })
    const tagInput = fake.put.mock.calls[2]![0]
    expect(tagInput.tags).toEqual(['AI', '职场'])
    // Batch export writes one document naming both selected titles.
    fireEvent.click(screen.getByLabelText(`${en['topicBank.batch.select']}: 选题 t-1`))
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.batch.export']))
    })
    expect(writeExport).toHaveBeenCalledWith('theme-a', `topics-${today}.md`, expect.stringContaining('选题 t-1'))
    // Clear selection empties the bar.
    fireEvent.click(screen.getByLabelText(`${en['topicBank.batch.select']}: AI 工具`))
    fireEvent.click(screen.getByLabelText(`${en['topicBank.batch.select']}: 选题 t-1`))
    fireEvent.click(screen.getByText(en['topicBank.batch.clear']))
    expect(screen.queryByText(en['topicBank.batch.clear'])).toBeNull()
  })

  it('exports the visible list and disables the export without themes', async () => {
    const today = todayDate()
    const { writeExport } = await renderBank(today)
    await act(async () => {
      fireEvent.click(screen.getByText(en['topicBank.export.button']))
    })
    expect(writeExport).toHaveBeenCalledWith('theme-a', `topics-${today}.md`, expect.stringContaining('AI 工具'))
    // No theme directories: the button is disabled and says why.
    cleanup()
    const withoutThemes = fakeTopics(defaultBank(today))
    renderView(withoutThemes.gateway, { listThemes: vi.fn(async () => []) })
    await waitFor(() => {
      expect(screen.getByText('AI 工具')).toBeTruthy()
    })
    const button = screen.getByText(en['topicBank.export.button']).closest('button') as HTMLButtonElement
    expect(button.disabled).toBe(true)
    expect(button.title).toBe(en['topicBank.export.noTheme'])
  })

  it('filters by keyword and persists the configuration with its version', async () => {
    await renderBank(todayDate())
    fireEvent.change(screen.getByLabelText(en['topicBank.filter.search']), { target: { value: 'AI' } })
    expect(screen.queryByText('选题 t-1')).toBeNull()
    expect(screen.getByText('AI 工具')).toBeTruthy()
    const stored = window.localStorage.getItem(CONFIG_KEY)
    expect(stored).toContain('"search":"AI"')
    expect(stored).toContain('"version":1')
  })

  it('migrates the stored configuration: garbage falls back whole, a kanban view loads', async () => {
    window.localStorage.setItem(CONFIG_KEY, '{broken json')
    const first = await renderBank(todayDate())
    expect(screen.getByText('选题 t-1')).toBeTruthy()
    cleanup()
    window.localStorage.setItem(CONFIG_KEY, JSON.stringify({
      version: 1,
      view: 'kanban',
      filters: { source: 'all', status: 'all', scoreMin: 0, scoreMax: 10, tag: null, planWindow: 'all', search: '' },
    }))
    renderView(first.fake.gateway)
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.kanbanHint'])).toBeTruthy()
    })
  })

  it('names dropped records in the problems bar instead of hiding them', async () => {
    const fake = fakeTopics(defaultBank(todayDate()))
    fake.gateway.list.mockResolvedValueOnce({ file: '_topics.json', items: [...fake.state.items], problems: ['dropped one invalid topic record: {}'] })
    renderView(fake.gateway)
    await waitFor(() => {
      expect(screen.getByText(en['topicBank.problems'].replace('{n}', '1'))).toBeTruthy()
    })
  })
})

describe('topic-bank locale pins', () => {
  // Every dictionary stem the view and the frame reference. Catalog ids are
  // locale stems by convention; the nav id is `nav.topicBank`.
  const PINS = [
    'nav.topicBank',
    'topicBank.title', 'topicBank.subtitle', 'topicBank.loading', 'topicBank.error', 'topicBank.problems',
    'topicBank.guide.hint', 'topicBank.new', 'topicBank.view.table', 'topicBank.view.kanban', 'topicBank.view.aria',
    'topicBank.count', 'topicBank.noMatch', 'topicBank.kanbanHint',
    'topicBank.column.title', 'topicBank.column.source', 'topicBank.column.score', 'topicBank.column.tags',
    'topicBank.column.status', 'topicBank.column.planDate', 'topicBank.column.updatedAt',
    'topic.score.none', 'topic.source.manual', 'topic.source.gather', 'topic.source.benchmark', 'topic.source.interaction',
    'topic.status.idea', 'topic.status.todo', 'topic.status.creating', 'topic.status.done', 'topic.status.shelved',
    'topicBank.filter.all', 'topicBank.filter.source', 'topicBank.filter.status', 'topicBank.filter.plan',
    'topicBank.filter.tag', 'topicBank.filter.allTags', 'topicBank.filter.score', 'topicBank.filter.scoreMin',
    'topicBank.filter.scoreMax', 'topicBank.filter.search',
    'topicBank.plan.all', 'topicBank.plan.week', 'topicBank.plan.month',
    'topicBank.openOriginal', 'topicBank.snapshotLabel', 'topicBank.snapshotNoSummary', 'topicBank.snapshotCaptured',
    'topicBank.linkedSchedule', 'topicBank.updatedAt', 'topicBank.detail.label', 'topicBank.detail.empty',
    'topicBank.startCreate', 'topicBank.aiOptimize', 'topicBank.aiPending',
    'topicBank.edit', 'topicBank.save', 'topicBank.cancel', 'topicBank.delete', 'topicBank.deleteConfirm',
    'topicBank.confirmDelete', 'topicBank.deleteAlsoSchedule',
    'topicBank.field.title', 'topicBank.field.titlePlaceholder', 'topicBank.field.oneLiner', 'topicBank.field.status',
    'topicBank.field.tags', 'topicBank.field.tagsPlaceholder', 'topicBank.field.description',
    'topicBank.field.descriptionPlaceholder', 'topicBank.field.sourceUrl', 'topicBank.field.sourceUrlPlaceholder',
    'topicBank.field.planDate', 'topicBank.field.score', 'topicBank.field.scorePlaceholder',
    'topicBank.error.titleRequired', 'topicBank.error.scoreRange',
    'topicBank.batch.select', 'topicBank.batch.selected', 'topicBank.batch.setStatus', 'topicBank.batch.apply',
    'topicBank.batch.tagsPlaceholder', 'topicBank.batch.applyTags', 'topicBank.batch.export', 'topicBank.batch.clear',
    'topicBank.export.theme', 'topicBank.export.noTheme', 'topicBank.export.button',
    'topicBank.notice.created', 'topicBank.notice.saved', 'topicBank.notice.deleted', 'topicBank.notice.batchDone',
    'topicBank.notice.exported', 'topicBank.notice.failed',
    'gather.notice.topicBankAdded', 'gather.notice.topicBankFailed', 'gather.notice.topicBankMissing',
  ] as const

  it('carries every topic-bank stem in both dictionaries', () => {
    const zhDict = zh as Record<string, string | undefined>
    const enDict = en as Record<string, string | undefined>
    for (const key of PINS) {
      expect(zhDict[key], key).toBeDefined()
      expect(enDict[key], key).toBeDefined()
    }
  })

  it('retires the removed 选题规划 nav vocabulary', () => {
    const zhDict = zh as Record<string, string | undefined>
    const enDict = en as Record<string, string | undefined>
    expect(zhDict['nav.topics']).toBeUndefined()
    expect(zhDict['topics.title']).toBeUndefined()
    expect(enDict['nav.topics']).toBeUndefined()
    expect(enDict['topics.title']).toBeUndefined()
  })
})
