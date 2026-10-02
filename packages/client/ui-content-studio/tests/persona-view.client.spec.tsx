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
    await waitFor(() => { expect(screen.getByText('Failed to save; please retry')).toBeTruthy() })
    fireEvent.click(screen.getByText('Failed to save; please retry'))
    expect(screen.queryByText('Failed to save; please retry')).toBeNull()
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

    const nameInput = within(dialog).getByPlaceholderText('one persona per identity, reusable across platforms') as HTMLInputElement
    fireEvent.change(nameInput, { target: { value: '老王' } })
    fireEvent.click(within(dialog).getByText('抖音'))
    fireEvent.click(within(dialog).getByText('Existing account'))
    fireEvent.click(within(dialog).getByText('Next'))

    expect(within(dialog).getByText('2 / 4 · Social links')).toBeTruthy()
    fireEvent.click(within(dialog).getByText('Add social link'))
    fireEvent.change(within(dialog).getByPlaceholderText('Profile URL'), { target: { value: 'https://x.example' } })
    fireEvent.change(within(dialog).getByPlaceholderText('Account bio'), { target: { value: '简介' } })
    fireEvent.click(within(dialog).getByText('Remove'))
    fireEvent.click(within(dialog).getByText('Next'))

    expect(within(dialog).getByText('3 / 4 · Intent')).toBeTruthy()
    fireEvent.click(within(dialog).getByText('Next'))

    expect(within(dialog).getByText('4 / 4 · Style & red lines')).toBeTruthy()
    expect(within(dialog).getByText('Persona prompt preview')).toBeTruthy()
    // The save button lands on every step; the gateway receives the form.
    fireEvent.click(within(dialog).getByText('Save persona'))
    await waitFor(() => { expect(putSpy).toHaveBeenCalled() })
    expect(putSpy.mock.calls[0]?.[0].name).toBe('老王')
    expect(putSpy.mock.calls[0]?.[0].platforms).toEqual(['douyin'])
  })

  it('refuses to save without the required name and navigates back', async () => {
    renderView()
    const dialog = await openWizard()
    fireEvent.click(within(dialog).getByText('Save persona'))
    expect(screen.getByText('Enter the persona name first')).toBeTruthy()
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

  it('gates the résumé extraction behind text and consent', async () => {
    renderView({ processPersonaAi: (async () => ({ operation: 'resume', promptVersion: 'persona-resume@1', fields: { whoAmI: '工程师' } })) as unknown as PersonaGateway['processPersonaAi'] })
    const dialog = await openWizard()
    fireEvent.change(within(dialog).getByPlaceholderText(/Paste text or upload/), { target: { value: '简历正文' } })
    fireEvent.click(within(dialog).getByText('AI extract & prefill'))
    expect(screen.getByText('Tick the consent box first')).toBeTruthy()
    fireEvent.click(within(dialog).getByText('I understand the résumé content will be sent to the AI model'))
    fireEvent.click(within(dialog).getByText('AI extract & prefill'))
    await waitFor(() => { expect(screen.getByText(/AI fill preview/)).toBeTruthy() })
    fireEvent.click(screen.getByText('Adopt all'))
    await waitFor(() => { expect(screen.queryByText(/AI fill preview/)).toBeNull() })
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
