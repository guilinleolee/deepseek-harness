// @vitest-environment jsdom
/**
 * The sentiment view surface over a stubbed SentimentGateway: the six tabs
 * render live store data, the task dialog round-trips through
 * `putSentimentTask`, the scan button reports the captured count, alert
 * handling rides `handleSentimentAlert`, and the settings form saves through
 * `putSentimentSettings`.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import type { ComponentProps } from 'react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type {
  SentimentAlert, SentimentAlertId, SentimentMention, SentimentSettings,
  SentimentSnapshot, SentimentStats, SentimentTask, SentimentTaskId, SentimentTaskInput,
} from '@deepseek-ai/dsh-content-outputs/types'
import type { TopicItemInput } from '@deepseek-ai/dsh-content-topics/types'
import { en } from '../src/client/locales.ts'
import { SentimentView, type SentimentGateway } from '../src/client/SentimentView.tsx'

afterEach(cleanup)

const NOW = '2026-10-08T10:00:00.000Z'

function settings(overrides: Partial<SentimentSettings> = {}): SentimentSettings {
  return {
    negativeHeatThreshold: 300,
    negativeSurgePercent: 50,
    domainBlacklist: ['spam.example'],
    accountBlacklist: [],
    retentionDays: 90,
    notifyEnabled: false,
    dingtalkWebhook: null,
    wecomWebhook: null,
    email: null,
    smtpHost: null,
    smtpPort: 465,
    smtpUser: null,
    smtpPassword: null,
    smtpFrom: null,
    ...overrides,
  }
}

function task(overrides: Partial<SentimentTask> = {}): SentimentTask {
  return {
    id: 'st-1' as SentimentTaskId,
    name: 'Kabage brand watch',
    group: 'brand',
    enabled: true,
    subjects: ['Kabage'],
    keywordGroups: [{ polarity: 'neg', terms: ['refund'] }],
    sources: ['rss'],
    feedUrls: ['https://news.example/rss'],
    intervalMinutes: 60,
    createdAt: NOW,
    updatedAt: NOW,
    ...overrides,
  }
}

function mention(overrides: Partial<SentimentMention> = {}): SentimentMention {
  return {
    id: 'sm-1' as SentimentMention['id'],
    taskId: 'st-1' as SentimentTaskId,
    source: 'rss',
    platform: 'news.example',
    url: 'https://news.example/a',
    title: 'Kabage refund complaint story',
    summary: 'Angry buyers demand refunds.',
    publishedAt: NOW,
    capturedAt: NOW,
    polarity: 'neg',
    confidence: 0.9,
    evidence: 'refund',
    heat: null,
    author: null,
    ...overrides,
  }
}

function alert(overrides: Partial<SentimentAlert> = {}): SentimentAlert {
  return {
    id: 'sa-1' as SentimentAlertId,
    taskId: 'st-1' as SentimentTaskId,
    eventKey: 'st-1:2026-10-08',
    level: 2,
    summary: 'One negative mention',
    reason: 'negative mentions 1; heat 100',
    mentionIds: ['sm-1' as SentimentMention['id']],
    handled: false,
    createdAt: NOW,
    handledAt: null,
    ...overrides,
  }
}

function stats(overrides: Partial<SentimentStats> = {}): SentimentStats {
  return {
    total: 3,
    positive: 1,
    neutral: 1,
    negative: 1,
    highRisk: 1,
    taskCount: 1,
    trend: [{ day: '2026-10-08', pos: 1, neu: 1, neg: 1 }],
    platforms: [{ platform: 'news.example', count: 3 }],
    ...overrides,
  }
}

function snapshot(overrides: Partial<SentimentSnapshot> = {}): SentimentSnapshot {
  return {
    tasks: [task()],
    mentions: [mention()],
    alerts: [alert()],
    settings: settings(),
    problems: [],
    scanning: false,
    lastScan: { at: NOW, captured: 1, alerts: 1 },
    report: null,
    ...overrides,
  }
}

function gateway(overrides: Partial<SentimentGateway> = {}): SentimentGateway {
  return {
    getSentiment: async () => snapshot(),
    putSentimentTask: async input => ({ ...task(), ...input, id: input.id ?? ('st-new' as SentimentTaskId) }),
    deleteSentimentTask: async () => undefined,
    setSentimentTaskEnabled: async (_id, enabled) => task({ enabled }),
    putSentimentSettings: async () => undefined,
    scanSentiment: async () => ({ captured: 2, alerts: 1, at: NOW }),
    handleSentimentAlert: async () => undefined,
    sentimentStats: async () => stats(),
    generateSentimentReport: async () => ({
      markdown: '# Daily sentiment report', degraded: false, generatedAt: NOW,
      promptVersion: 'sentiment-report@1', mentionCount: 1, alertCount: 1,
    }),
    ...overrides,
  }
}

function renderView(overrides: Partial<SentimentGateway> = {}, topicsPut?: (input: TopicItemInput) => Promise<unknown>): void {
  // Mirrors the framework translate: `{name}` template params get substituted.
  const t = (key: keyof typeof en, params?: Record<string, unknown>): string =>
    en[key].replace(/\{(\w+)\}/gu, (_all, name: string) => {
      const value: unknown = params?.[name]
      return typeof value === 'string' || typeof value === 'number' ? String(value) : ''
    })
  const topics = { put: topicsPut ?? (async () => undefined) }
  render(<SentimentView {...({ sentiment: gateway(overrides), topics, t } as unknown as ComponentProps<typeof SentimentView>)} />)
}

describe('SentimentView', () => {
  it('renders the six tabs with monitor tasks first and live task rows', async () => {
    renderView()
    const tablist = await waitFor(() => screen.getByRole('tablist'))
    expect(within(tablist).getByText('Monitor tasks')).toBeTruthy()
    expect(within(tablist).getByText('Dashboard')).toBeTruthy()
    expect(within(tablist).getByText('AI reports')).toBeTruthy()
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    expect(screen.getByText('Kabage')).toBeTruthy()
    expect(screen.getByText('Enabled')).toBeTruthy()
  })

  it('switches to the dashboard and shows the stat cards, trend, and platforms', async () => {
    renderView()
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    fireEvent.click(screen.getByText('Dashboard'))
    expect(screen.getByText('Total mentions')).toBeTruthy()
    expect(screen.getByText('Mention trend (pos/neu/neg)')).toBeTruthy()
    expect(screen.getByText('news.example — 3')).toBeTruthy()
  })

  it('opens the task dialog, saves through the gateway, and toggles a task', async () => {
    const putSpy = vi.fn(async (input: SentimentTaskInput) => ({ ...task(), ...input }))
    const toggleSpy = vi.fn(async () => task({ enabled: false }))
    renderView({ putSentimentTask: putSpy, setSentimentTaskEnabled: toggleSpy })
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })

    fireEvent.click(screen.getByText('New monitor task'))
    const dialog = screen.getByRole('dialog')
    const textboxes = within(dialog).getAllByRole('textbox')
    const [nameBox] = textboxes
    if (nameBox === undefined) throw new Error('expected a task-name textbox')
    fireEvent.change(nameBox, { target: { value: 'Policy watch' } })
    fireEvent.change(within(dialog).getByRole('textbox', { name: 'Subjects (one per line)' }), { target: { value: 'Acme' } })
    fireEvent.change(within(dialog).getByRole('textbox', { name: 'RSS feed URLs (one per line)' }), { target: { value: 'https://policy.example/rss' } })
    const [saveButton] = within(dialog).getAllByText('Save')
    if (saveButton === undefined) throw new Error('expected a Save button')
    fireEvent.click(saveButton)
    await waitFor(() => { expect(putSpy).toHaveBeenCalledOnce() })
    const [putCall] = putSpy.mock.calls
    if (putCall === undefined) throw new Error('expected one putSentimentTask call')
    expect(putCall[0].name).toBe('Policy watch')

    fireEvent.click(screen.getByText('Disable'))
    await waitFor(() => { expect(toggleSpy).toHaveBeenCalledOnce() })
  })

  it('shows the mention rows with the polarity tag and the source link', async () => {
    renderView()
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    fireEvent.click(screen.getByText('Mentions'))
    expect(screen.getByText('Kabage refund complaint story')).toBeTruthy()
    expect(screen.getByText('Negative')).toBeTruthy()
    expect(screen.getByText('View').getAttribute('href')).toBe('https://news.example/a')
  })

  it('runs a scan and reports the captured count', async () => {
    renderView()
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    fireEvent.click(screen.getByText('Scan now'))
    await waitFor(() => { expect(screen.getByText(/Scan finished: 2 new mentions captured/)).toBeTruthy() })
  })

  it('marks an alert handled from the alerts tab', async () => {
    const handledSpy = vi.fn(async () => undefined)
    renderView({ handleSentimentAlert: handledSpy })
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    fireEvent.click(screen.getByText('Alerts'))
    expect(screen.getByText('One negative mention')).toBeTruthy()
    fireEvent.click(screen.getByText('Mark handled'))
    await waitFor(() => { expect(handledSpy).toHaveBeenCalledOnce() })
  })

  it('renders and saves the settings form', async () => {
    const settingsSpy = vi.fn(async () => undefined)
    renderView({ putSentimentSettings: settingsSpy })
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    fireEvent.click(screen.getByText('Settings'))
    expect(screen.getByText('Notification channels')).toBeTruthy()
    expect(screen.getByText(/Negative heat threshold/)).toBeTruthy()
    fireEvent.click(screen.getByText('Save settings'))
    await waitFor(() => { expect(settingsSpy).toHaveBeenCalledOnce() })
    const settingsCalls = settingsSpy.mock.calls as ReadonlyArray<[SentimentSettings]> | []
    const [settingsCall] = settingsCalls
    if (settingsCall === undefined) throw new Error('expected one putSentimentSettings call')
    expect(settingsCall[0].negativeHeatThreshold).toBe(300)
  })

  it('shows the load-failure notice when the first read fails', async () => {
    renderView({ getSentiment: async () => { throw new Error('disk') } })
    await waitFor(() => { expect(screen.getByText('Failed to load sentiment data; retry later')).toBeTruthy() })
  })

  it('generates a report through the gateway and renders it with a download link', async () => {
    renderView()
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    fireEvent.click(screen.getByText('AI reports'))
    expect(screen.getByText(/No report yet/)).toBeTruthy()
    fireEvent.click(screen.getByText('Generate report'))
    await waitFor(() => { expect(screen.getByText('# Daily sentiment report')).toBeTruthy() })
    const link = screen.getByText('Download Markdown')
    expect(link.getAttribute('download')).toBe('sentiment-report-2026-10-08.md')
  })

  it('flags a degraded report when the engine fell back', async () => {
    renderView({
      generateSentimentReport: async () => ({
        markdown: '# Fallback data report', degraded: true, generatedAt: NOW,
        promptVersion: 'sentiment-report@1', mentionCount: 0, alertCount: 0,
      }),
    })
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    fireEvent.click(screen.getByText('AI reports'))
    fireEvent.click(screen.getByText('Generate report'))
    await waitFor(() => { expect(screen.getByText(/degraded data-only report/)).toBeTruthy() })
    expect(screen.getByText('# Fallback data report')).toBeTruthy()
  })

  it('reflows one alert into the topic bank through the injected face', async () => {
    const put = vi.fn(async (_input: TopicItemInput) => undefined)
    renderView({}, put)
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    fireEvent.click(screen.getByText('Alerts'))
    fireEvent.click(screen.getByText('To topic bank'))
    await waitFor(() => { expect(put).toHaveBeenCalledOnce() })
    const input = put.mock.calls[0]?.[0]
    if (input === undefined) throw new Error('expected one topics.put call')
    expect(input.status).toBe('idea')
    expect(input.tags).toEqual(['舆情'])
    expect(input.title).toContain('Kabage brand watch')
    await waitFor(() => { expect(screen.getByText(/Added to the topic bank/)).toBeTruthy() })
  })

  it('surfaces a topic-bank failure notice', async () => {
    renderView({}, async () => { throw new Error('disk full') })
    await waitFor(() => { expect(screen.getByText('Kabage brand watch')).toBeTruthy() })
    fireEvent.click(screen.getByText('Alerts'))
    fireEvent.click(screen.getByText('To topic bank'))
    await waitFor(() => { expect(screen.getByText(/Failed to add to the topic bank/)).toBeTruthy() })
  })
})
