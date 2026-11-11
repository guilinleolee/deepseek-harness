// @vitest-environment jsdom
/**
 * The workbench home over stubbed Remote reads: the today's-todo list
 * merges the due schedule, the unanswered inbox, and the unhandled
 * sentiment alerts; the topic-to-publish funnel counts the topics that
 * produced a draft; the sentiment panel renders the health split; and one
 * failing Remote never blanks the rest of the home.
 */
import { cleanup, fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import type {
  ContentOutputsSnapshot, InteractionsManifestRead, ReviewManifestRead,
  SentimentAlert, SentimentAlertId, SentimentSnapshot, SentimentStats,
} from '@deepseek-ai/dsh-content-outputs/types'
import type { OutputTopic } from '@deepseek-ai/dsh-content-outputs/types'
import type { ContentScheduleSnapshot, ScheduleItemId } from '@deepseek-ai/dsh-content-schedule/types'
import type { ContentTopicsSnapshot, TopicItem, TopicItemId } from '@deepseek-ai/dsh-content-topics/types'
import type { TranslateNS } from '@deepseek-ai/dsh-client-ui-slots'
import { en } from '../src/client/locales.ts'
import { ContentWorkbench, type WorkbenchView } from '../src/client/ContentWorkbench.tsx'

afterEach(cleanup)

const NOW = '2026-10-08T10:00:00.000Z'
// The home resolves "today" as the UTC day, so the fixture must use the
// same clock rather than a frozen date.
const TODAY = new Date().toISOString().slice(0, 10)

function topic(overrides: Partial<TopicItem> = {}): TopicItem {
  return {
    id: 'tp-1' as TopicItemId,
    title: 'A topic',
    oneLiner: null,
    status: 'idea',
    source: { type: 'manual', refId: null, url: null, snapshot: null },
    tags: [],
    description: null,
    score: null,
    planDate: null,
    scheduleItemId: null,
    topicDir: null,
    createdAt: NOW,
    updatedAt: NOW,
    ...overrides,
  }
}

function outputs(overrides: Partial<ContentOutputsSnapshot> = {}): ContentOutputsSnapshot {
  return { root: '/outputs', projects: [], problems: [], ...overrides }
}

function schedule(items: ContentScheduleSnapshot['items'] = []): ContentScheduleSnapshot {
  return { file: '/outputs/_schedule.json', items, problems: [] }
}

function topics(items: TopicItem[] = []): ContentTopicsSnapshot {
  return { file: '/outputs/_topics.json', items, problems: [] }
}

function interactions(summary: { unread: number; pendingReply: number }): InteractionsManifestRead {
  return {
    manifest: {
      formatVersion: 0,
      conversations: [],
      insights: { generatedAt: null, topQuestions: [], painPoints: [], interests: [] },
      summary: { unread: summary.unread, pendingReply: summary.pendingReply, replied: 0, archived: 0, spam: 0 },
    },
    problems: [],
  }
}

function alert(overrides: Partial<SentimentAlert> = {}): SentimentAlert {
  return {
    id: 'sa-1' as SentimentAlertId,
    taskId: 'st-1' as SentimentAlert['taskId'],
    eventKey: 'st-1:2026-10-08',
    level: 2,
    summary: 'A complaint burst',
    reason: 'negative mentions 3',
    mentionIds: [],
    handled: false,
    createdAt: NOW,
    handledAt: null,
    ...overrides,
  }
}

function sentimentSnapshot(alerts: SentimentAlert[] = []): SentimentSnapshot {
  return {
    tasks: [],
    mentions: [],
    alerts,
    settings: {
      negativeHeatThreshold: 300,
      negativeSurgePercent: 50,
      domainBlacklist: [],
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
    },
    problems: [],
    scanning: false,
    lastScan: null,
    report: null,
  }
}

function makeSentimentStats(overrides: Partial<SentimentStats> = {}): SentimentStats {
  return {
    total: 10,
    positive: 6,
    neutral: 3,
    negative: 1,
    highRisk: 1,
    taskCount: 2,
    trend: [],
    platforms: [],
    ...overrides,
  }
}

/** The stubbed read face; each source is overridable per test. */
interface Stubs {
  listOutputs?: () => Promise<ContentOutputsSnapshot>
  listSchedule?: () => Promise<ContentScheduleSnapshot>
  listTopics?: () => Promise<ContentTopicsSnapshot>
  readInteractions?: () => Promise<InteractionsManifestRead>
  readReviewManifest?: (theme: string) => Promise<ReviewManifestRead>
  getSentiment?: () => Promise<SentimentSnapshot>
  sentimentStats?: () => Promise<SentimentStats>
}

function renderHome(stubs: Stubs = {}): { onNavigate: ReturnType<typeof vi.fn> } {
  // Mirrors the framework translate: `{name}` template params get substituted.
  // The namespace key domain also carries the shared `common` vocabulary,
  // which this package's own dictionary does not define — those resolve to
  // an empty string here, exactly as a missing namespace entry would.
  const t: TranslateNS<'content-studio'> = (key, params) => {
    const text = key in en ? en[key as keyof typeof en] : ''
    return text.replace(/\{(\w+)\}/gu, (_all: string, name: string) => {
      const value: unknown = params?.[name]
      return typeof value === 'string' || typeof value === 'number' ? String(value) : ''
    })
  }
  const onNavigate = vi.fn<(view: WorkbenchView) => void>()
  render(
    <ContentWorkbench
      listOutputs={stubs.listOutputs ?? (async () => outputs())}
      listSchedule={stubs.listSchedule ?? (async () => schedule())}
      listTopics={stubs.listTopics ?? (async () => topics())}
      readInteractions={stubs.readInteractions ?? (async () => interactions({ unread: 0, pendingReply: 0 }))}
      readReviewManifest={stubs.readReviewManifest ?? (async () => ({ manifest: null, problems: [] }))}
      sentimentRead={{
        getSentiment: stubs.getSentiment ?? (async () => sentimentSnapshot()),
        sentimentStats: stubs.sentimentStats ?? (async () => makeSentimentStats()),
      }}
      onNavigate={onNavigate}
      onChat={vi.fn()}
      account="通用模式"
      persona=""
      t={t}
    />,
  )
  return { onNavigate }
}

describe('ContentWorkbench', () => {
  it('merges the three todo sources and hops to the owning view', async () => {
    const { onNavigate } = renderHome({
      listSchedule: async () => schedule([
        { id: 'sc-1' as ScheduleItemId, title: 'A post', date: TODAY, time: '09:00', platform: 'xhs', status: 'scheduled', kind: 'content', topic: null, url: null },
        { id: 'sc-2' as ScheduleItemId, title: 'Later', date: '2026-12-01', time: '09:00', platform: 'xhs', status: 'scheduled', kind: 'content', topic: null, url: null },
      ]),
      readInteractions: async () => interactions({ unread: 2, pendingReply: 3 }),
      getSentiment: async () => sentimentSnapshot([alert({ level: 3 })]),
    })
    await waitFor(() => { expect(screen.getByText('To do today')).toBeTruthy() })

    // The counts ride the labels: one due item, five replies, one alert.
    // Scope to the todo panel — the activity feed renders "×1" badges too.
    // Two of the three rows count one each, so "×1" appears twice.
    const todo = screen.getByText('To do today').closest('section')
    if (todo === null) throw new Error('expected the todo panel')
    expect(within(todo).getAllByText('×1')).toHaveLength(2)
    expect(within(todo).getByText('×5')).toBeTruthy()

    fireEvent.click(screen.getByText('Schedule due today'))
    expect(onNavigate).toHaveBeenCalledWith('topicBank')
    fireEvent.click(screen.getByText('Comments awaiting a reply'))
    expect(onNavigate).toHaveBeenCalledWith('interaction')
    fireEvent.click(screen.getByText('Sentiment alerts to handle'))
    expect(onNavigate).toHaveBeenCalledWith('sentiment')
  })

  it('shows the empty state when nothing is due today', async () => {
    renderHome()
    await waitFor(() => {
      expect(screen.getByText('Nothing due today — enjoy the clear day.')).toBeTruthy()
    })
  })

  it('counts the topic-to-publish funnel and its stage rates', async () => {
    renderHome({
      listTopics: async () => topics([
        topic({ id: 'tp-1' as TopicItemId, topicDir: 'alpha' }),
        topic({ id: 'tp-2' as TopicItemId, topicDir: 'beta' }),
        topic({ id: 'tp-3' as TopicItemId, topicDir: null }),
      ]),
      listOutputs: async () => outputs({
        projects: [
          { topic: 'alpha' as OutputTopic, title: 'Alpha', kind: 'article', platform: null, status: 'ready', tags: [], summary: null, updatedAt: NOW, deliverables: [], assetCount: 0, hasMetadata: true },
          { topic: 'beta' as OutputTopic, title: 'Beta', kind: 'article', platform: null, status: 'published', tags: [], summary: null, updatedAt: NOW, deliverables: [], assetCount: 0, hasMetadata: true },
          { topic: 'gamma' as OutputTopic, title: 'Gamma', kind: 'article', platform: null, status: 'draft', tags: [], summary: null, updatedAt: NOW, deliverables: [], assetCount: 0, hasMetadata: true },
        ],
      }),
    })
    await waitFor(() => { expect(screen.getByText('Topic to publish')).toBeTruthy() })
    // The funnel panel is the only place the three stage labels appear
    // together; the stat cards carry their own "Topics" label.
    const funnel = screen.getByText('Topic to publish').closest('section')
    if (funnel === null) throw new Error('expected the funnel panel')
    const stage = within(funnel).getByText('Drafted').closest('div')
    if (stage === null) throw new Error('expected a funnel stage')
    // Three topics; two of them produced a finished draft; one reached published.
    expect(within(stage).getByText('2')).toBeTruthy()
    expect(within(funnel).getByText('Topics')).toBeTruthy()
    expect(within(funnel).getByText('Published')).toBeTruthy()
    expect(within(funnel).getByText('3')).toBeTruthy()
    expect(within(funnel).getByText('1')).toBeTruthy()
    // 2 of 3 topics drafted, then 1 of 2 drafts published.
    expect(within(funnel).getByText('67%')).toBeTruthy()
    expect(within(funnel).getByText('50%')).toBeTruthy()
  })

  it('renders the sentiment health split and the open-alert count', async () => {
    renderHome({
      getSentiment: async () => sentimentSnapshot([alert({ id: 'sa-1' as SentimentAlertId }), alert({ id: 'sa-2' as SentimentAlertId, level: 3 })]),
    })
    await waitFor(() => { expect(screen.getByText('Sentiment health')).toBeTruthy() })
    expect(screen.getByText('Positive share · 60%')).toBeTruthy()
    expect(screen.getByText('Neutral share · 30%')).toBeTruthy()
    expect(screen.getByText('Negative share · 10%')).toBeTruthy()
    expect(screen.getByText('Open alerts · 2')).toBeTruthy()
  })

  it('keeps the rest of the home rendering when one Remote fails', async () => {
    renderHome({
      getSentiment: async () => { throw new Error('sentiment is down') },
      sentimentStats: async () => { throw new Error('sentiment is down') },
    })
    // The failing sentiment faces degrade their own panels only.
    await waitFor(() => { expect(screen.getByText('To do today')).toBeTruthy() })
    expect(screen.getByText('Topic to publish')).toBeTruthy()
    expect(screen.getByText('Nothing due today — enjoy the clear day.')).toBeTruthy()
  })
})
