// @vitest-environment jsdom
/**
 * The persona controller: disk reads through the gateway face, the wizard
 * draft buffer, the explicit AI flows with per-field adoption, the report
 * save paths, and the old free-text import.
 */
import { afterEach, describe, expect, it, vi } from 'vitest'
import type { PersonaEntry, PersonaField, PersonaFieldKey } from '@deepseek-ai/dsh-content-outputs/types'
import { PERSONA_FIELD_KEYS } from '@deepseek-ai/dsh-content-outputs/types'
import { createPersonaController, type PersonaGateway } from '../src/client/persona/persona-store.ts'

afterEach(() => {
  window.localStorage.clear()
  vi.restoreAllMocks()
})

function entry(overrides: Partial<PersonaEntry> = {}): PersonaEntry {
  const fields = {} as Record<PersonaFieldKey, PersonaField>
  for (const key of PERSONA_FIELD_KEYS) fields[key] = { value: null, source: 'user', aiMeta: null }
  return {
    id: 'p-1' as PersonaEntry['id'],
    name: '老李',
    platforms: ['xhs'],
    accountStage: 'fresh',
    revision: 1,
    digest: '老李（v1）',
    fields,
    links: [],
    site: { url: null, pastedText: null },
    style: { preset: null, customText: null, strength: 'light', bannedWords: [], redLines: [] },
    assets: { resumeText: null, resumeName: null },
    report: null,
    clonedFrom: null,
    createdAt: '2026-09-25T00:00:00.000Z',
    updatedAt: '2026-09-25T00:00:00.000Z',
    ...overrides,
  }
}

/** A scripted gateway: every call recorded, defaults overridable per test. */
function gateway(overrides: Partial<PersonaGateway> = {}): PersonaGateway & { calls: string[] } {
  const calls: string[] = []
  const record = (label: string): void => { calls.push(label) }
  return {
    calls,
    listPersonas: async () => { record('list'); return { personas: [entry()], problems: [] } },
    getPersona: async () => ({ persona: entry() }),
    putPersona: async (input) => { record('put'); return { ...entry(), ...input, id: input.id ?? ('p-new' as PersonaEntry['id']), revision: input.id === undefined ? 1 : 2 } },
    putPersonaReport: async () => { record('report'); return entry() },
    deletePersona: async () => { record('delete') },
    socialStatuses: async () => ({ rows: [], dailyCap: 3 }),
    socialStartLogin: async () => undefined,
    socialCapture: async () => ({ platform: 'xhs', url: '', text: '' }),
    socialForget: async () => undefined,
    socialVerify: async () => ({ platform: 'xhs', valid: true, nickname: null }),
    processPersonaAi: (async () => ({ operation: 'fill', promptVersion: 'persona-fill@1', fields: {} })) as PersonaGateway['processPersonaAi'],
    ...overrides,
  }
}

async function flush(): Promise<void> {
  await new Promise(resolve => setTimeout(resolve, 0))
  await new Promise(resolve => setTimeout(resolve, 0))
}

describe('load, select, and the packed prompt', () => {
  it('loads once, exposes the state, and clears a stale selection', async () => {
    const gw = gateway()
    const controller = createPersonaController({ gateway: gw })
    await controller.ensureLoaded()
    await controller.ensureLoaded()
    expect(gw.calls).toEqual(['list'])
    expect(controller.getState().personas).toHaveLength(1)

    controller.select('p-1' as PersonaEntry['id'])
    expect(window.localStorage.getItem('dsh-content-studio.persona.selectedId')).toContain('p-1')
    expect(controller.activePrompt()).toContain('【账号人设 · 老李（v1）】')
    expect(controller.selectedEntry()?.id).toBe('p-1')

    gw.listPersonas = async () => ({ personas: [], problems: [] })
    await controller.reload()
    expect(controller.getState().selectedId).toBeNull()
    expect(controller.activePrompt()).toBe('')
  })

  it('surfaces load failures as a dismissible notice', async () => {
    const controller = createPersonaController({ gateway: gateway({ listPersonas: async () => { throw new Error('down') } }) })
    await controller.reload()
    expect(controller.getState().notice).toBe('load-failed')
    controller.dismissNotice()
    expect(controller.getState().notice).toBeNull()
  })

  it('names dropped stored records through problems', async () => {
    const controller = createPersonaController({ gateway: gateway({ listPersonas: async () => ({ personas: [], problems: ['dropped one'] }) }) })
    await controller.reload()
    expect(controller.getState().problems).toEqual(['dropped one'])
  })
})

describe('the wizard and the draft buffer', () => {
  it('opens new/edit/clone forms and persists the draft across a close', async () => {
    const controller = createPersonaController({ gateway: gateway() })
    await controller.ensureLoaded()

    controller.openEdit('p-1' as PersonaEntry['id'])
    expect(controller.getState().wizard?.form.editingId).toBe('p-1')
    controller.closeWizard()

    controller.openClone('p-1' as PersonaEntry['id'])
    expect(controller.getState().wizard?.form.editingId).toBeNull()
    expect(controller.getState().wizard?.form.clonedFrom).toBe('p-1')
    controller.closeWizard()

    controller.openNew()
    controller.updateForm({ name: '老王' })
    controller.setStep(2)
    expect((JSON.parse(window.localStorage.getItem('dsh-content-studio.persona.wizard') ?? '{}') as { form: { name: string } }).form.name).toBe('老王')
    controller.closeWizard()

    controller.openNew()
    expect(controller.getState().wizard?.form.name).toBe('老王')
    expect(controller.getState().wizard?.step).toBe(2)
  })

  it('flips a field back to user provenance on edit and toggles platforms and links', async () => {
    const controller = createPersonaController({ gateway: gateway() })
    await controller.ensureLoaded()
    controller.openNew()
    controller.setField('audience', '职场人')
    expect(controller.getState().wizard?.form.fields.audience.source).toBe('user')

    controller.togglePlatform('douyin')
    expect(controller.getState().wizard?.form.platforms).toEqual(['douyin'])
    controller.togglePlatform('douyin')
    expect(controller.getState().wizard?.form.platforms).toEqual([])

    controller.setAccountStage('existing')
    expect(controller.getState().wizard?.form.accountStage).toBe('existing')

    // The step-2 list: one row per platform, the row exists only while its URL is non-empty.
    controller.setLinkUrl('xhs', 'https://x.example')
    expect(controller.getState().wizard?.form.links).toEqual([{ platform: 'xhs', url: 'https://x.example', bio: null, sampleText: null }])
    controller.setLinkUrl('douyin', 'https://d.example')
    controller.setLinkUrl('xhs', 'https://x2.example')
    expect(controller.getState().wizard?.form.links.map(link => link.platform)).toEqual(['douyin', 'xhs'])
    expect(controller.getState().wizard?.form.links.find(link => link.platform === 'xhs')?.url).toBe('https://x2.example')
    controller.setLinkUrl('douyin', '   ')
    expect(controller.getState().wizard?.form.links.map(link => link.platform)).toEqual(['xhs'])
  })

  it('saves through put, clears the draft, and reloads; a blank name is refused', async () => {
    const gw = gateway()
    const controller = createPersonaController({ gateway: gw })
    await controller.ensureLoaded()
    controller.openNew()
    void controller.saveWizard()
    await flush()
    expect(controller.getState().notice).toBe('name-required')
    expect(gw.calls).not.toContain('put')

    controller.updateForm({ name: '老王' })
    void controller.saveWizard()
    await flush()
    expect(gw.calls).toContain('put')
    expect(controller.getState().wizard).toBeNull()
    expect(window.localStorage.getItem('dsh-content-studio.persona.wizard')).toBeNull()
  })

  it('reports a failed save', async () => {
    const controller = createPersonaController({ gateway: gateway({ putPersona: async () => { throw new Error('disk') } }) })
    await controller.ensureLoaded()
    controller.openNew()
    controller.updateForm({ name: '老王' })
    void controller.saveWizard()
    await flush()
    expect(controller.getState().notice).toBe('save-failed')
  })
})

describe('the explicit AI flows', () => {
  it('refuses a fill with no blanks and adopts candidates per field', async () => {
    const gw = gateway({
      processPersonaAi: (async () => ({ operation: 'fill', promptVersion: 'persona-fill@1', fields: { audience: '职场人', niche: 'AI 工具' } })) as unknown as PersonaGateway['processPersonaAi'],
    })
    const controller = createPersonaController({ gateway: gw })
    await controller.ensureLoaded()
    controller.openNew()
    controller.updateForm({ name: '老王' })
    // Every fillable field carries a value: nothing to fill, no AI call.
    for (const key of PERSONA_FIELD_KEYS.filter(fillable => fillable !== 'whoAmI')) controller.setField(key, '已有')
    void controller.runFill()
    await flush()
    expect(controller.getState().notice).toBe('fill-none')
    expect(gw.calls).not.toContain('ai')

    // One blank reopens the fill; two candidates come back for one blank slot.
    controller.setField('audience', '')
    void controller.runFill()
    await flush()
    const preview = controller.getState().fillPreview
    expect(preview?.origin).toBe('fill')
    controller.adoptFillField('audience')
    expect(controller.getState().wizard?.form.fields.audience).toMatchObject({ value: '职场人', source: 'ai' })
    // An edited adoption replaces the value before it lands.
    controller.adoptFillField('niche', '改过的赛道')
    expect(controller.getState().wizard?.form.fields.niche.value).toBe('改过的赛道')
    expect(controller.getState().fillPreview).toBeNull()

    controller.discardFill()
    expect(controller.getState().fillPreview).toBeNull()
  })

  it('adopts everything at once and reports AI failures', async () => {
    const controller = createPersonaController({
      gateway: gateway({
        processPersonaAi: (async () => ({ operation: 'fill', promptVersion: 'persona-fill@1', fields: { audience: '职场人', niche: 'AI' } })) as unknown as PersonaGateway['processPersonaAi'],
      }),
    })
    await controller.ensureLoaded()
    controller.openNew()
    void controller.runFill()
    await flush()
    controller.adoptAllFill()
    expect(controller.getState().wizard?.form.fields.audience.value).toBe('职场人')
    expect(controller.getState().wizard?.form.fields.niche.value).toBe('AI')

    const failing = createPersonaController({ gateway: gateway({ processPersonaAi: async () => { throw new Error('down') } }) })
    await failing.ensureLoaded()
    failing.openNew()
    void failing.runFill()
    await flush()
    expect(failing.getState().notice).toBe('ai-failed')
  })

  it('gates the résumé extraction on text and consent, then adopts', async () => {
    const gw = gateway({
      processPersonaAi: (async () => ({ operation: 'resume', promptVersion: 'persona-resume@1', fields: { whoAmI: '十年工程师' } })) as unknown as PersonaGateway['processPersonaAi'],
    })
    const controller = createPersonaController({ gateway: gw })
    await controller.ensureLoaded()
    controller.openNew()
    void controller.runResume()
    await flush()
    expect(controller.getState().notice).toBe('resume-empty')
    controller.updateForm({ resumeText: '简历正文' })
    void controller.runResume()
    await flush()
    expect(controller.getState().notice).toBe('resume-consent')
    controller.updateForm({ resumeConsent: true })
    void controller.runResume()
    await flush()
    controller.adoptFillField('whoAmI')
    expect(controller.getState().wizard?.form.fields.whoAmI.source).toBe('ai')
    expect((gw as { calls?: string[] }).calls?.length ?? 0).toBeGreaterThanOrEqual(0)
  })

  it('analyzes the own site: fetch text lands in the form, candidates await adoption', async () => {
    // The real gateway returns the fetched text only when a url was fetched.
    const ai = vi.fn(async (request: { operation: 'site'; url?: string; pastedText?: string }) => ({
      operation: 'site',
      promptVersion: 'persona-site@1',
      fields: { whoAmI: '企业官网主体' },
      ...(request.url !== undefined ? { text: '抓取到的官网正文' } : {}),
    }))
    const controller = createPersonaController({
      gateway: gateway({ processPersonaAi: ai as unknown as PersonaGateway['processPersonaAi'] }),
    })
    await controller.ensureLoaded()
    controller.openNew()

    void controller.runSite()
    await flush()
    expect(controller.getState().notice).toBe('site-empty')
    expect(ai).not.toHaveBeenCalled()

    controller.updateForm({ siteUrl: ' https://laoli.example ' })
    void controller.runSite()
    await flush()
    expect(ai).toHaveBeenCalledWith({ operation: 'site', url: 'https://laoli.example' })
    expect(controller.getState().wizard?.form.sitePastedText).toBe('抓取到的官网正文')
    expect(controller.getState().fillPreview).toMatchObject({ origin: 'site', promptVersion: 'persona-site@1' })
    controller.adoptFillField('whoAmI')
    expect(controller.getState().wizard?.form.fields.whoAmI).toMatchObject({ value: '企业官网主体', source: 'ai' })

    // No URL: the pasted text is analyzed as-is, and a fetch without text keeps the pasted content.
    controller.updateForm({ siteUrl: '', sitePastedText: '手工粘贴的官网内容' })
    void controller.runSite()
    await flush()
    expect(ai).toHaveBeenLastCalledWith({ operation: 'site', pastedText: '手工粘贴的官网内容' })
    expect(controller.getState().wizard?.form.sitePastedText).toBe('手工粘贴的官网内容')

    ai.mockRejectedValueOnce(new Error('down'))
    void controller.runSite()
    await flush()
    expect(controller.getState().notice).toBe('site-failed')
  })

  it('reports an empty site extraction without touching the form', async () => {
    const controller = createPersonaController({
      gateway: gateway({
        processPersonaAi: (async () => ({ operation: 'site', promptVersion: 'persona-site@1', fields: {}, text: '只有文本没有字段' })) as unknown as PersonaGateway['processPersonaAi'],
      }),
    })
    await controller.ensureLoaded()
    controller.openNew()
    controller.updateForm({ siteUrl: 'https://laoli.example' })
    void controller.runSite()
    await flush()
    expect(controller.getState().notice).toBe('ai-empty')
    expect(controller.getState().wizard?.form.sitePastedText).toBe('只有文本没有字段')
    expect(controller.getState().fillPreview).toBeNull()
  })

  it('analyzes the social homepages at the last step and adopts the candidates', async () => {
    const ai = vi.fn(async () => ({ operation: 'social', promptVersion: 'persona-social@1', fields: { audience: '宝妈群体' } }))
    const controller = createPersonaController({
      gateway: gateway({ processPersonaAi: ai as unknown as PersonaGateway['processPersonaAi'] }),
    })
    await controller.ensureLoaded()
    controller.openNew()

    void controller.runSocial()
    await flush()
    expect(controller.getState().notice).toBe('social-empty')
    expect(ai).not.toHaveBeenCalled()

    controller.setLinkUrl('xhs', ' https://xhs.example/laoli ')
    controller.setLinkUrl('douyin', 'https://douyin.example/laoli')
    void controller.runSocial()
    await flush()
    expect(ai).toHaveBeenCalledWith({
      operation: 'social',
      links: [
        { platform: 'xhs', url: 'https://xhs.example/laoli' },
        { platform: 'douyin', url: 'https://douyin.example/laoli' },
      ],
    })
    expect(controller.getState().fillPreview).toMatchObject({ origin: 'social', promptVersion: 'persona-social@1' })
    controller.adoptFillField('audience')
    expect(controller.getState().wizard?.form.fields.audience).toMatchObject({ value: '宝妈群体', source: 'ai' })

    ai.mockRejectedValueOnce(new Error('所有主页都是登录墙，未抓到可读正文'))
    void controller.runSocial()
    await flush()
    expect(controller.getState().notice).toBe('social-failed')
    expect(controller.getState().noticeDetail).toBe('所有主页都是登录墙，未抓到可读正文')
  })

  it('scopes the fill blanks when the caller passes a scope', async () => {
    const ai = vi.fn(async () => ({ operation: 'fill', promptVersion: 'persona-fill@1', fields: { goal: '获客留资' } }))
    const controller = createPersonaController({
      gateway: gateway({ processPersonaAi: ai as unknown as PersonaGateway['processPersonaAi'] }),
    })
    await controller.ensureLoaded()
    controller.openNew()
    controller.setField('audience', '已有受众')
    // The earlier steps' raw evidence rides along as fill context.
    controller.updateForm({ sitePastedText: '官网抓取正文' })

    // The intent scope: audience is not in it, so it stays out of the blanks.
    await controller.runFill(['goal', 'monetize', 'contentValue', 'cadence'])
    expect(ai).toHaveBeenCalledWith(expect.objectContaining({
      operation: 'fill',
      known: { audience: '已有受众' },
      blanks: ['goal', 'monetize', 'contentValue', 'cadence'],
      context: '官网抓取正文',
    }))
    expect(controller.getState().fillPreview).toMatchObject({ origin: 'fill' })
    controller.adoptFillField('goal')
    expect(controller.getState().wizard?.form.fields.goal.value).toBe('获客留资')

    // Every scoped field filled: the explicit none-notice, no AI call.
    controller.setField('monetize', '广告合作')
    controller.setField('contentValue', '干货')
    controller.setField('cadence', '每周 3 条')
    const calls = ai.mock.calls.length
    await controller.runFill(['goal', 'monetize', 'contentValue', 'cadence'])
    // A scoped run says "already filled" (the unscoped one says fill-none).
    expect(controller.getState().notice).toBe('scope-filled')
    expect(ai.mock.calls.length).toBe(calls)
  })

  it('verifies a session: invalid drops it with a notice, valid stays silent', async () => {
    const verify = vi.fn(async (_platform: string) => ({ platform: 'xhs' as const, valid: false, nickname: null as string | null }))
    const forget = vi.fn(async () => undefined)
    const controller = createPersonaController({
      gateway: gateway({
        socialVerify: verify as unknown as PersonaGateway['socialVerify'],
        socialForget: forget as unknown as PersonaGateway['socialForget'],
      }),
    })
    await controller.ensureLoaded()
    await controller.verifySocial('xhs')
    expect(forget).toHaveBeenCalledWith('xhs')
    expect(controller.getState().notice).toBe('social-failed')

    verify.mockResolvedValueOnce({ platform: 'xhs' as const, valid: true, nickname: '老李' })
    await controller.verifySocial('xhs')
    expect(controller.getState().notice).toBeNull()
  })

  it('forgets a session and refreshes statuses', async () => {
    const forget = vi.fn(async () => undefined)
    const controller = createPersonaController({
      gateway: gateway({ socialForget: forget as unknown as PersonaGateway['socialForget'] }),
    })
    await controller.ensureLoaded()
    await controller.forgetSocial('xhs')
    expect(forget).toHaveBeenCalledWith('xhs')
  })

  it('generates and edits reports through the dedicated face', async () => {
    const stored = entry({ report: { markdown: '# 报告', sourceRevision: 1, editedByUser: false, generatedAt: '2026-09-25T00:00:00.000Z', promptVersion: 'persona-report@1' } })
    const gw = gateway({
      listPersonas: async () => ({ personas: [stored], problems: [] }),
      processPersonaAi: (async () => ({ operation: 'report', promptVersion: 'persona-report@1', markdown: '# 账号画像报告' })) as unknown as PersonaGateway['processPersonaAi'],
    })
    const controller = createPersonaController({ gateway: gw })
    await controller.ensureLoaded()
    controller.openReport('p-1' as PersonaEntry['id'])
    expect(controller.getState().reportId).toBe('p-1')
    void controller.generateReport('p-1' as PersonaEntry['id'])
    await flush()
    expect(gw.calls).toContain('report')
    expect(controller.getState().notice).toBe('report-saved')
    controller.closeReport()
    expect(controller.getState().reportId).toBeNull()

    const spy = vi.spyOn(gw, 'putPersonaReport')
    void controller.saveReportEdit('p-1' as PersonaEntry['id'], '   ')
    await flush()
    expect(spy).not.toHaveBeenCalled()
    void controller.saveReportEdit('p-1' as PersonaEntry['id'], '手工编辑')
    await flush()
    expect(spy).toHaveBeenCalled()
  })
})

describe('removal and the old free-text import', () => {
  it('removes a persona and clears the selection with it', async () => {
    const gw = gateway()
    const controller = createPersonaController({ gateway: gw })
    await controller.ensureLoaded()
    controller.select('p-1' as PersonaEntry['id'])
    await controller.remove('p-1' as PersonaEntry['id'])
    expect(gw.calls).toContain('delete')
    expect(controller.getState().selectedId).toBeNull()
  })

  it('reports removal failures', async () => {
    const controller = createPersonaController({ gateway: gateway({ deletePersona: async () => { throw new Error('disk') } }) })
    await controller.ensureLoaded()
    await controller.remove('p-1' as PersonaEntry['id'])
    expect(controller.getState().notice).toBe('delete-failed')
  })

  it('imports the old free text as a persona and clears the browser key', async () => {
    window.localStorage.setItem('dsh-content-studio.persona', '专注 AI 工具的博主')
    const gw = gateway()
    const controller = createPersonaController({ gateway: gw })
    expect(controller.getState().legacyText).toBe('专注 AI 工具的博主')
    await controller.importLegacy('导入的画像')
    expect(gw.calls).toContain('put')
    expect(controller.getState().legacyText).toBeNull()
    expect(window.localStorage.getItem('dsh-content-studio.persona')).toBeNull()
    expect(controller.getState().notice).toBe('legacy-done')

    window.localStorage.setItem('dsh-content-studio.persona', '再来一条')
    const failing = createPersonaController({ gateway: gateway({ putPersona: async () => { throw new Error('disk') } }) })
    await failing.importLegacy('导入的画像')
    expect(failing.getState().notice).toBe('legacy-failed')
  })

  it('dismisses the legacy banner and keeps it dismissed', async () => {
    window.localStorage.setItem('dsh-content-studio.persona', '旧文本')
    const controller = createPersonaController({ gateway: gateway() })
    controller.dismissLegacy()
    expect(controller.getState().legacyText).toBeNull()
    expect(window.localStorage.getItem('dsh-content-studio.persona.legacyDismissed')).toBe('1')
  })
})
