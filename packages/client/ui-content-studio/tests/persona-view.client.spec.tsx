// @vitest-environment jsdom
/**
 * The persona view surface: card list states, the four-step wizard with its
 * prompt preview and AI fill panel, and the report panel with the staleness
 * banner and confirmed regeneration.
 */
import { act, cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import type { ComponentProps } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { PersonaEntry, PersonaField, PersonaFieldKey, PersonaInput } from '@deepseek-ai/dsh-content-outputs/types'
import { PERSONA_FIELD_KEYS } from '@deepseek-ai/dsh-content-outputs/types'
import { en } from '../src/client/locales.ts'
import { createPersonaController, type PersonaGateway } from '../src/client/persona/persona-store.ts'
import { PersonaView } from '../src/client/PersonaView.tsx'

vi.mock('@deepseek-ai/dsh-client-ui-primitives', () => ({
  writeClipboard: vi.fn(async () => true),
  // The wizard's advanced block: a minimal controlled disclosure mirror.
  DisclosureRow: ({ title, open, expandOnRowClick, onToggle, children }: {
    title: string
    open: boolean
    expandOnRowClick?: boolean
    onToggle: () => void
    children?: React.ReactNode
  }) => (
    <div>
      <button type="button" onClick={expandOnRowClick === true ? onToggle : undefined}>{title}</button>
      {open && children}
    </div>
  ),
  IconSparkle16: () => <svg data-testid="sparkle" />,
}))

afterEach(() => {
  cleanup()
  window.localStorage.clear()
  vi.restoreAllMocks()
})

function entry(overrides: Partial<PersonaEntry> = {}): PersonaEntry {
  // A mutable local for construction; PersonaEntry.fields is the readonly view.
  const fields = {} as Record<PersonaFieldKey, PersonaField>
  for (const key of PERSONA_FIELD_KEYS) fields[key] = { value: null, source: 'user', aiMeta: null }
  fields.niche = { value: 'AI 工具', source: 'ai', aiMeta: { promptVersion: 'persona-fill@1', at: '2026-09-25T00:00:00.000Z' } }
  fields.audience = { value: '25-40 岁职场人群', source: 'user', aiMeta: null }
  return {
    id: 'p-1' as PersonaEntry['id'],
    name: '老李',
    platforms: ['xhs', 'douyin'],
    accountStage: 'fresh',
    revision: 2,
    digest: '老李的人设摘要（v2）',
    fields,
    links: [],
    site: { url: null, pastedText: null },
    style: { preset: null, customText: null, strength: 'light', bannedWords: ['最好'], redLines: ['医疗'] },
    assets: { resumeText: null, resumeName: null },
    report: { markdown: '# 报告正文', sourceRevision: 2, editedByUser: false, generatedAt: '2026-09-25T00:00:00.000Z', promptVersion: 'persona-report@1' },
    clonedFrom: null,
    createdAt: '2026-09-25T00:00:00.000Z',
    updatedAt: '2026-09-25T00:00:00.000Z',
    ...overrides,
  }
}

function gateway(overrides: Partial<PersonaGateway> = {}): PersonaGateway {
  return {
    listPersonas: async () => ({ personas: [entry()], problems: [] }),
    getPersona: async () => ({ persona: entry() }),
    putPersona: async input => ({ ...entry(), ...input, id: input.id ?? ('p-new' as PersonaEntry['id']), revision: input.id === undefined ? 1 : 3, digest: '新摘要（v3）' }),
    putPersonaReport: async (_id, report) => entry({ report }),
    deletePersona: async () => undefined,
    socialStatuses: async () => ({ rows: [], dailyCap: 3 }),
    socialStartLogin: async () => undefined,
    socialCapture: async () => ({ platform: 'xhs', url: '', text: '' }),
    socialForget: async () => undefined,
    socialVerify: async () => ({ platform: 'xhs', valid: true, nickname: null }),
    processPersonaAi: (async () => ({ operation: 'fill', promptVersion: 'persona-fill@1', fields: { audience: '职场人群' } })) as unknown as PersonaGateway['processPersonaAi'],
    ...overrides,
  }
}

function renderView(overrides: Partial<PersonaGateway> = {}): void {
  const controller = createPersonaController({ gateway: gateway(overrides) })
  const t = (key: keyof typeof en) => en[key]
  render(<PersonaView {...({ personas: controller, t } as unknown as ComponentProps<typeof PersonaView>)} />)
}

async function openWizard(): Promise<HTMLElement> {
  await act(async () => { await Promise.resolve() })
  fireEvent.click(screen.getByText('New persona'))
  await act(async () => { await Promise.resolve() })
  return screen.getByRole('dialog')
}

describe('the card list', () => {
  it('renders loading, then the cards with chips, digest, badges, and actions', async () => {
    renderView()
    expect(screen.getByText('Loading personas…')).toBeTruthy()
    await waitFor(() => { expect(screen.getByText('老李')).toBeTruthy() })
    expect(screen.getByText('AI 工具')).toBeTruthy()
    expect(screen.getByText('小红书')).toBeTruthy()
    expect(screen.getByText('has report')).toBeTruthy()
    expect(screen.getByText('老李的人设摘要（v2）')).toBeTruthy()
    expect(screen.getByText('Use')).toBeTruthy()
    expect(screen.getByText('Preview')).toBeTruthy()
  })

  it('shows the empty state and names dropped records', async () => {
    renderView({ listPersonas: async () => ({ personas: [], problems: ['dropped one'] }) })
    await waitFor(() => { expect(screen.getByText(/No personas yet/)).toBeTruthy() })
    expect(screen.getByText(/dropped one/)).toBeTruthy()
  })

  it('renders notices as a dismissible bar', async () => {
    renderView({ putPersona: async () => { throw new Error('disk') } })
    const dialog = await openWizard()
    fireEvent.change(within(dialog).getByPlaceholderText('one persona per identity, reusable across platforms'), { target: { value: '老王' } })
    fireEvent.click(within(dialog).getByText('Save persona'))
    // The notice renders inside the modal overlay, which hides the page-level bar.
    await waitFor(() => { expect(within(dialog).getByText('Failed to save; please retry')).toBeTruthy() })
    fireEvent.click(within(dialog).getByText('Failed to save; please retry'))
    expect(within(dialog).queryByText('Failed to save; please retry')).toBeNull()
  })

  it('shows the legacy import banner and clears it on import', async () => {
    window.localStorage.setItem('dsh-content-studio.persona', '旧文本')
    const putSpy = vi.fn(async (_input: PersonaInput) => entry())
    renderView({ putPersona: putSpy })
    await waitFor(() => { expect(screen.getByText(/old free-text persona/i)).toBeTruthy() })
    fireEvent.click(screen.getByText('Import'))
    await waitFor(() => { expect(putSpy).toHaveBeenCalled() })
    expect(screen.queryByText(/old free-text persona/i)).toBeNull()
  })

  it('dismisses the legacy banner', async () => {
    window.localStorage.setItem('dsh-content-studio.persona', '旧文本')
    renderView()
    await waitFor(() => { expect(screen.getByText('Dismiss')).toBeTruthy() })
    fireEvent.click(screen.getByText('Dismiss'))
    expect(screen.queryByText('Dismiss')).toBeNull()
  })

  it('deletes with confirmation and toggles the in-use selection', async () => {
    const deleteSpy = vi.fn(async () => undefined)
    renderView({ deletePersona: deleteSpy })
    await waitFor(() => { expect(screen.getByText('老李')).toBeTruthy() })
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
    fireEvent.click(screen.getByText('Delete'))
    expect(confirm).toHaveBeenCalled()
    expect(deleteSpy).not.toHaveBeenCalled()
    confirm.mockReturnValue(true)
    fireEvent.click(screen.getByText('Delete'))
    await waitFor(() => { expect(deleteSpy).toHaveBeenCalledWith('p-1') })

    fireEvent.click(screen.getByText('Use'))
    expect(screen.getByText('in use')).toBeTruthy()
    fireEvent.click(screen.getByText('Stop using'))
    expect(screen.queryByText('in use')).toBeNull()
  })

  it('toggles the structured preview panel with provenance badges', async () => {
    renderView()
    await waitFor(() => { expect(screen.getByText('老李')).toBeTruthy() })
    fireEvent.click(screen.getByText('Preview'))
    expect(screen.getByText('Persona preview')).toBeTruthy()
    expect(screen.getByText('AI-inferred')).toBeTruthy()
    expect(screen.getByText(/Banned words：?最好/)).toBeTruthy()
    expect(screen.getByText(/Red lines：?医疗/)).toBeTruthy()
    fireEvent.click(screen.getByText('Hide'))
    expect(screen.queryByText('Persona preview')).toBeNull()
  })
})

describe('the four-step wizard', () => {
  it('walks all four steps, edits fields, and saves through the gateway', async () => {
    const putSpy = vi.fn(async (_input: PersonaInput) => entry())
    renderView({ putPersona: putSpy })
    const dialog = await openWizard()
    expect(within(dialog).getByText('1 / 4 · Basics')).toBeTruthy()
    // whoAmI / audience / oneLiner have no manual inputs in step 1; the AI
    // faces infer them and the preview shows the adopted values.
    expect(within(dialog).queryByText('我是谁（主体背景）')).toBeNull()
    expect(within(dialog).queryByText('目标受众')).toBeNull()
    expect(within(dialog).queryByText('人设一句话简介')).toBeNull()

    const nameInput = within(dialog).getByPlaceholderText('one persona per identity, reusable across platforms') as HTMLInputElement
    fireEvent.change(nameInput, { target: { value: '老王' } })
    fireEvent.click(within(dialog).getByText('抖音'))
    fireEvent.click(within(dialog).getByText('Existing account'))
    fireEvent.click(within(dialog).getByText('Next'))

    expect(within(dialog).getByText('2 / 4 · Social links')).toBeTruthy()
    // The fixed platform list: one labeled URL row per platform (labels come
    // from the shared model table), no dropdown, no bio.
    expect(within(dialog).getByText('抖音')).toBeTruthy()
    expect(within(dialog).queryByPlaceholderText('Account bio')).toBeNull()
    fireEvent.change(within(dialog).getByLabelText('小红书'), { target: { value: 'https://xhs.example/laoli' } })
    fireEvent.click(within(dialog).getByText('Next'))

    expect(within(dialog).getByText('3 / 4 · Intent')).toBeTruthy()
    // The intent step: chips to tick, a custom remainder input, and the scoped AI-infer button.
    expect(within(dialog).getByText('What should this account achieve: followers, influence, or conversion?')).toBeTruthy()
    fireEvent.click(within(dialog).getByText('带货转化'))
    expect(within(dialog).getByPlaceholderText('e.g. every Tuesday & Friday at 8pm')).toBeTruthy()
    expect(within(dialog).getByText('AI-infer this step')).toBeTruthy()
    fireEvent.click(within(dialog).getByText('Next'))

    expect(within(dialog).getByText('4 / 4 · Style & red lines')).toBeTruthy()
    expect(within(dialog).getByText('Persona prompt preview')).toBeTruthy()
    // The style presets are a checkable chip list with a readable sample line.
    fireEvent.click(within(dialog).getByText('幽默网感'))
    expect(within(dialog).getByText('e.g. 咱就是说，这功能一开，效率直接起飞。')).toBeTruthy()
    // The save button lands on every step; the gateway receives the form.
    fireEvent.click(within(dialog).getByText('Save persona'))
    await waitFor(() => { expect(putSpy).toHaveBeenCalled() })
    expect(putSpy.mock.calls[0]?.[0].name).toBe('老王')
    expect(putSpy.mock.calls[0]?.[0].platforms).toEqual(['douyin'])
    expect(putSpy.mock.calls[0]?.[0].style.preset).toBe('humor')
  })

  it('refuses to save without the required name and navigates back', async () => {
    renderView()
    const dialog = await openWizard()
    fireEvent.click(within(dialog).getByText('Save persona'))
    expect(within(dialog).getByText('Enter the persona name first')).toBeTruthy()
    fireEvent.click(within(dialog).getByText('Next'))
    fireEvent.click(within(dialog).getByText('Back'))
    expect(within(dialog).getByText('1 / 4 · Basics')).toBeTruthy()
    fireEvent.click(within(dialog).getByText('Close'))
    expect(screen.queryByText('1 / 4 · Basics')).toBeNull()
  })

  it('previews the packed prompt from the live form', async () => {
    renderView()
    const dialog = await openWizard()
    const nameInput = within(dialog).getByPlaceholderText('one persona per identity, reusable across platforms') as HTMLInputElement
    fireEvent.change(nameInput, { target: { value: '老王' } })
    fireEvent.click(within(dialog).getByText('Next'))
    fireEvent.click(within(dialog).getByText('Next'))
    fireEvent.click(within(dialog).getByText('Next'))
    expect(within(dialog).getByText(/【账号人设 · 老王（v1）】/)).toBeTruthy()
    fireEvent.click(within(dialog).getByText('Copy'))
  })

  it('fills blank fields through the explicit AI button and adopts per field', async () => {
    renderView()
    const dialog = await openWizard()
    const nameInput = within(dialog).getByPlaceholderText('one persona per identity, reusable across platforms') as HTMLInputElement
    fireEvent.change(nameInput, { target: { value: '老王' } })
    for (let at = 0; at < 3; at += 1) fireEvent.click(within(dialog).getByText('Next'))
    fireEvent.click(within(dialog).getByText('AI-fill blank fields'))
    await waitFor(() => { expect(screen.getByText(/AI fill preview/)).toBeTruthy() })
    fireEvent.change(screen.getByDisplayValue('职场人群'), { target: { value: '改过的受众' } })
    fireEvent.click(screen.getByText('Adopt'))
    await waitFor(() => { expect(screen.queryByText(/AI fill preview/)).toBeNull() })
  })

  it('analyzes the social homepages from step 2 and adopts the candidates', async () => {
    const processSocial = (async () => ({ operation: 'social', promptVersion: 'persona-social@1', fields: { audience: '宝妈群体' } })) as unknown as PersonaGateway['processPersonaAi']
    renderView({ processPersonaAi: processSocial })
    const dialog = await openWizard()
    fireEvent.click(within(dialog).getByText('Next'))
    // The analyze action lives on the social-links step itself.
    expect(within(dialog).getByText('Analyze social profiles')).toBeTruthy()
    fireEvent.change(within(dialog).getByLabelText('小红书'), { target: { value: 'https://xhs.example/laoli' } })
    fireEvent.click(within(dialog).getByText('Analyze social profiles'))
    await waitFor(() => { expect(screen.getByText(/AI fill preview/)).toBeTruthy() })
    fireEvent.click(screen.getByText('Adopt all'))
    await waitFor(() => { expect(screen.queryByText(/AI fill preview/)).toBeNull() })

    // With no link at all: the explicit notice instead of a gateway call.
    fireEvent.change(within(dialog).getByLabelText('小红书'), { target: { value: '' } })
    fireEvent.click(within(dialog).getByText('Analyze social profiles'))
    expect(within(dialog).getByText('Fill at least one profile URL in the social-links step first')).toBeTruthy()
  })

  it('composes the intent chips into the values and infers only the intent blanks', async () => {
    const processSpy = vi.fn(async () => ({ operation: 'fill', promptVersion: 'persona-fill@1', fields: { cadence: '每周 3 条' } }))
    const putSpy = vi.fn(async (_input: PersonaInput) => entry())
    renderView({ processPersonaAi: processSpy as unknown as PersonaGateway['processPersonaAi'], putPersona: putSpy })
    const dialog = await openWizard()
    fireEvent.change(within(dialog).getByPlaceholderText('one persona per identity, reusable across platforms'), { target: { value: '老王' } })
    fireEvent.click(within(dialog).getByText('Next'))
    fireEvent.click(within(dialog).getByText('Next'))

    // Multi-select goal chips compose into one value; the template seeds the content value.
    fireEvent.click(within(dialog).getByText('带货转化'))
    fireEvent.click(within(dialog).getByText('引流到店'))
    fireEvent.click(within(dialog).getByText('教用户怎么做（教程型）'))
    expect(within(dialog).getByDisplayValue('教用户怎么做（教程型）')).toBeTruthy()

    // The scoped inference fills only the still-blank intent fields.
    fireEvent.click(within(dialog).getByText('AI-infer this step'))
    await waitFor(() => { expect(processSpy).toHaveBeenCalled() })
    const firstCall = processSpy.mock.calls[0] as [{ operation: string; blanks?: string[] }?] | []
    const request = firstCall[0]
    if (request === undefined) throw new Error('expected one processPersonaAi call')
    expect(request.blanks).toEqual(['monetize', 'cadence'])
    await waitFor(() => { expect(screen.getByText(/AI fill preview/)).toBeTruthy() })
    fireEvent.click(screen.getByText('Adopt all'))
    await waitFor(() => { expect(screen.queryByText(/AI fill preview/)).toBeNull() })

    fireEvent.click(within(dialog).getByText('Save persona'))
    await waitFor(() => { expect(putSpy).toHaveBeenCalled() })
    const payload = putSpy.mock.calls[0]?.[0]
    expect(payload?.fields.goal.value).toBe('带货转化；引流到店')
    expect(payload?.fields.contentValue.value).toBe('教用户怎么做（教程型）')
    expect(payload?.fields.cadence.value).toBe('每周 3 条')
  })

  it('keeps the advanced fields behind a disclosure and composes red-line presets', async () => {
    const putSpy = vi.fn(async (_input: PersonaInput) => entry())
    renderView({ putPersona: putSpy })
    const dialog = await openWizard()
    fireEvent.change(within(dialog).getByPlaceholderText('one persona per identity, reusable across platforms'), { target: { value: '老王' } })
    for (let at = 0; at < 3; at += 1) fireEvent.click(within(dialog).getByText('Next'))

    // First screen: pick a style, see the sample; the advanced block stays collapsed.
    fireEvent.click(within(dialog).getByText('幽默网感'))
    expect(within(dialog).getByText('e.g. 咱就是说，这功能一开，效率直接起飞。')).toBeTruthy()
    expect(within(dialog).queryByPlaceholderText(/Extra style description/)).toBeNull()

    // Red-line presets live on the first screen and compose into the value.
    fireEvent.click(within(dialog).getByText('不提竞品'))
    fireEvent.click(within(dialog).getByText('不聊政治'))

    fireEvent.click(within(dialog).getByText('Advanced (optional)'))
    expect(within(dialog).getByPlaceholderText(/Extra style description/)).toBeTruthy()
    expect(within(dialog).getByText('Follow strictly (self-check every line)')).toBeTruthy()

    fireEvent.click(within(dialog).getByText('Save persona'))
    await waitFor(() => { expect(putSpy).toHaveBeenCalled() })
    const payload = putSpy.mock.calls[0]?.[0]
    expect(payload?.style.preset).toBe('humor')
    expect(payload?.style.redLines).toEqual(['不聊政治', '不提竞品'])
  })

  it('gates the résumé extraction behind text and consent', async () => {
    renderView({ processPersonaAi: (async () => ({ operation: 'resume', promptVersion: 'persona-resume@1', fields: { whoAmI: '工程师' } })) as unknown as PersonaGateway['processPersonaAi'] })
    const dialog = await openWizard()
    fireEvent.change(within(dialog).getByPlaceholderText(/Paste text or upload/), { target: { value: '简历正文' } })
    fireEvent.click(within(dialog).getByText('AI extract & prefill'))
    // The notice renders inside the modal overlay — the page-level bar is hidden behind it.
    expect(within(dialog).getByText('Tick the consent box first')).toBeTruthy()
    fireEvent.click(within(dialog).getByText('I understand the résumé content will be sent to the AI model'))
    fireEvent.click(within(dialog).getByText('AI extract & prefill'))
    await waitFor(() => { expect(screen.getByText(/AI fill preview/)).toBeTruthy() })
    fireEvent.click(screen.getByText('Adopt all'))
    await waitFor(() => { expect(screen.queryByText(/AI fill preview/)).toBeNull() })
  })

  it('fetches and parses the own site from step 1 and adopts the candidates', async () => {
    renderView({ processPersonaAi: (async () => ({ operation: 'site', promptVersion: 'persona-site@1', fields: { niche: '效率工具' }, text: '抓取到的官网正文' })) as unknown as PersonaGateway['processPersonaAi'] })
    const dialog = await openWizard()
    expect(within(dialog).getByText('Website / blog')).toBeTruthy()
    fireEvent.change(within(dialog).getByPlaceholderText(/fill it in to fetch and parse/), { target: { value: 'https://laoli.example' } })
    fireEvent.click(within(dialog).getByText('Fetch & parse'))
    await waitFor(() => { expect(screen.getByText(/AI fill preview/)).toBeTruthy() })
    expect(screen.getByDisplayValue('抓取到的官网正文')).toBeTruthy()
    fireEvent.click(screen.getByText('Adopt all'))
    await waitFor(() => { expect(screen.queryByText(/AI fill preview/)).toBeNull() })

    // Empty URL and paste: the explicit notice, no AI call.
    fireEvent.change(within(dialog).getByPlaceholderText(/fill it in to fetch and parse/), { target: { value: '' } })
    fireEvent.change(screen.getByDisplayValue('抓取到的官网正文'), { target: { value: '' } })
    fireEvent.click(within(dialog).getByText('Fetch & parse'))
    expect(within(dialog).getByText('Enter the URL, or paste the site content first')).toBeTruthy()
  })

  it('shows a failed site fetch inside the dialog instead of silently doing nothing', async () => {
    renderView({ processPersonaAi: (async () => { throw new Error('fetch blocked') }) as unknown as PersonaGateway['processPersonaAi'] })
    const dialog = await openWizard()
    fireEvent.change(within(dialog).getByPlaceholderText(/fill it in to fetch and parse/), { target: { value: 'https://laoli.example' } })
    fireEvent.click(within(dialog).getByText('Fetch & parse'))
    await waitFor(() => { expect(within(dialog).getByText('Fetching or parsing the site failed; please retry later')).toBeTruthy() })
  })
})

describe('the report panel', () => {
  /** A gateway whose list reflects report writes, like the disk would. */
  function renderReportView(initial: PersonaEntry, ai: Partial<PersonaGateway> = {}): { list: () => PersonaEntry } {
    let current = initial
    renderView({
      listPersonas: async () => ({ personas: [current], problems: [] }),
      putPersonaReport: async (_id, report) => { current = entry({ report }); return current },
      processPersonaAi: (async () => ({ operation: 'report', promptVersion: 'persona-report@1', markdown: '# 新报告' })) as unknown as PersonaGateway['processPersonaAi'],
      ...ai,
    })
    return { list: () => current }
  }

  it('opens with the staleness tracking, saves edits, and closes', async () => {
    renderReportView(entry())
    await waitFor(() => { expect(screen.getByText('老李')).toBeTruthy() })
    fireEvent.click(screen.getByText('Report'))
    expect(screen.getByText(/Persona report · 老李/)).toBeTruthy()
    const textarea = screen.getByDisplayValue('# 报告正文') as HTMLTextAreaElement
    fireEvent.change(textarea, { target: { value: '# 手工编辑的报告' } })
    fireEvent.click(screen.getByText('Save edits'))
    await waitFor(() => { expect(screen.getByText(/edited by hand/)).toBeTruthy() })
    fireEvent.click(screen.getByText('Close'))
    expect(screen.queryByText(/Persona report · 老李/)).toBeNull()
  })

  it('shows the empty state and generates the first report', async () => {
    renderReportView(entry({ report: null }))
    await waitFor(() => { expect(screen.getByText('老李')).toBeTruthy() })
    fireEvent.click(screen.getByText('Report'))
    expect(screen.getByText(/No report yet/)).toBeTruthy()
    fireEvent.click(screen.getByText('Generate report'))
    await waitFor(() => { expect(screen.getByDisplayValue('# 新报告')).toBeTruthy() })
  })

  it('confirms before regenerating an edited report', async () => {
    const confirm = vi.spyOn(window, 'confirm').mockReturnValue(false)
    renderReportView(entry({ report: { markdown: '# 报告', sourceRevision: 1, editedByUser: true, generatedAt: '2026-09-25T00:00:00.000Z', promptVersion: 'persona-report@1' } }))
    await waitFor(() => { expect(screen.getByText('老李')).toBeTruthy() })
    fireEvent.click(screen.getByText('Report'))
    const dialog = screen.getByRole('dialog')
    expect(within(dialog).getByText(/may be stale/)).toBeTruthy()
    fireEvent.click(within(dialog).getByText('Regenerate'))
    expect(confirm).toHaveBeenCalled()
    confirm.mockReturnValue(true)
    fireEvent.click(within(dialog).getByText('Regenerate'))
    await waitFor(() => { expect(screen.getByDisplayValue('# 新报告')).toBeTruthy() })
  })
})
