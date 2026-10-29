/**
 * The sentiment report engine: one generation renders the stored snapshot
 * (tasks, mentions, alerts, stats) into a Markdown report through the
 * shared LLM face. Two deterministic templates — the routine daily report
 * and the crisis brief (chosen when an unhandled high-level alert exists) —
 * are generated section by section (one model call per section, parallel,
 * each degrading on its own) and bound into both the Markdown document and
 * a structured intermediate representation (`ir`) so reports stay stable
 * and comparable across days. A deterministic data-only fallback covers a
 * fully failed generation — the review column's degraded-report pattern.
 * The gateway stores the returned report; this module never touches disk.
 */

import type { Context } from '@deepseek-ai/cordis'
import type { AiCallPolicy } from '../gather/ai.ts'
import { streamLlmText } from '../gather/ai.ts'
import type { SentimentAlert, SentimentMention, SentimentSettings, SentimentSnapshot, SentimentStats, SentimentTask } from './types.ts'

/** Timeout reason code carried by aborted sentiment report calls. */
export const SENTIMENT_REPORT_TIMEOUT_CODE = 'SENTIMENT_REPORT_TIMEOUT'

/** Prompt version of the sentiment report face. */
export const SENTIMENT_REPORT_PROMPT_VERSION = 'sentiment-report@2'

/** Mentions handed to the model, newest first (cost bound). */
export const SENTIMENT_REPORT_MENTION_CAP = 40

/** Alerts handed to the model, newest first. */
export const SENTIMENT_REPORT_ALERT_CAP = 10

/** Character cap of one mention line in the framed input. */
const MENTION_LINE_CAP = 200

/** Character cap of the whole framed input handed to the model. */
const FRAMED_CAP = 12_000

/** Character cap of one generated section body. */
const SECTION_BODY_CAP = 6_000

/** The unhandled alert level that switches the report to the crisis template. */
export const SENTIMENT_CRISIS_ALERT_LEVEL = 2

const REPORT_PREAMBLE = [
  '你是企业舆情分析助手。基于给定的当日舆情数据撰写报告的一个章节。',
  '要求：',
  '- 只依据给定事实与数字，不要编造数据；',
  '- 只输出该章节的正文，不要输出章节标题，不要解释或前言；',
  '- 用 Markdown 列表或短段落组织，不超过 300 字。',
].join('\n')

/** One section of a report template: stable key, fixed title, section instruction. */
export interface ReportSectionSpec {
  readonly key: string
  readonly title: string
  readonly instruction: string
}

/** The routine daily template, stable across days for comparability. */
const DAILY_TEMPLATE: readonly ReportSectionSpec[] = [
  { key: 'overview', title: '今日概览', instruction: '用 2-3 句话概括总量、情感结构与最重要的事件。' },
  { key: 'risks', title: '负面舆情与风险点', instruction: '按告警等级从高到低展开，引用原文标题与依据短语。' },
  { key: 'highlights', title: '正面声音与亮点', instruction: '提炼可放大的正面信号。' },
  { key: 'actions', title: '建议处置动作', instruction: '输出 3-5 条动词开头、可直接执行的建议，黄金响应窗口内的优先。' },
  { key: 'watchlist', title: '明日关注清单', instruction: '列出 2-4 条需要持续跟踪的事件或关键词。' },
]

/** The crisis brief, chosen when an unhandled high-level alert exists. */
const CRISIS_TEMPLATE: readonly ReportSectionSpec[] = [
  { key: 'panorama', title: '事件全景', instruction: '按时间线概括危机事件的起因、扩散与现状，引用原文标题。' },
  { key: 'spread', title: '舆情走势与传播分析', instruction: '结合平台分布与热度数字，说明传播路径与扩散风险。' },
  { key: 'response', title: '回应口径建议', instruction: '给出 2-3 条可直接使用的对外回应口径要点，先共情后行动。' },
  { key: 'followup', title: '后续观察清单', instruction: '列出 3-4 条未来 48 小时内需持续跟踪的风险点与责任分工建议。' },
]

/** The stored report document; `formatVersion 0` has no compatibility promise. */
export interface SentimentReport {
  readonly markdown: string
  /** True when the model call failed and the deterministic template rendered instead. */
  readonly degraded: boolean
  readonly generatedAt: string
  readonly promptVersion: string
  /** How many mentions and alerts the report covered. */
  readonly mentionCount: number
  readonly alertCount: number
  /** The structured section representation behind the Markdown, absent on the legacy one-shot shape. */
  readonly ir?: SentimentReportIr
}

/** The structured intermediate representation of one generated report. */
export interface SentimentReportIr {
  /** Which template produced the report. */
  readonly template: 'daily' | 'crisis'
  /** The generated sections in render order. */
  readonly sections: readonly { readonly key: string; readonly title: string; readonly body: string }[]
}

/** One framed mention line: platform, polarity, title, evidence. */
function mentionLine(mention: SentimentMention): string {
  const evidence = mention.evidence === null ? '' : `（依据：${mention.evidence}）`
  const text = `[${mention.platform}] ${mention.polarity} ${mention.title}${evidence}`
  return text.length > MENTION_LINE_CAP ? `${text.slice(0, MENTION_LINE_CAP)}…` : text
}

/** One framed alert line: level, summary, reason. */
function alertLine(alert: SentimentAlert, taskName: string): string {
  return `[L${String(alert.level)}] ${taskName}：${alert.summary}（${alert.reason}）`
}

/**
 * Frame the stored snapshot into the model's user prompt.
 * @param mentions - the snapshot's mentions (any order).
 * @param alerts - the snapshot's alerts (any order).
 * @param tasks - the snapshot's tasks (id → name lookup).
 * @param stats - the dashboard projection.
 * @param settings - the module settings (thresholds feed the narrative).
 * @returns the complete user-prompt text.
 */
export function frameSentimentReport(
  mentions: readonly SentimentMention[],
  alerts: readonly SentimentAlert[],
  tasks: readonly SentimentTask[],
  stats: SentimentStats,
  settings: SentimentSettings,
): string {
  const taskName = (id: string): string => tasks.find(task => task.id === id)?.name ?? id
  const newestMentions = [...mentions].slice(0, SENTIMENT_REPORT_MENTION_CAP)
  const newestAlerts = [...alerts].slice(0, SENTIMENT_REPORT_ALERT_CAP)
  const lines = [
    '当日舆情数据如下：',
    `- 总提及 ${String(stats.total)} 条：正面 ${String(stats.positive)}、中性 ${String(stats.neutral)}、负面 ${String(stats.negative)}；`,
    `- 高风险（负面）提及 ${String(stats.negative)} 条，负面热度阈值 ${String(settings.negativeHeatThreshold)}；`,
    `- 监控任务 ${String(stats.taskCount)} 个：${tasks.map(task => task.name).join('、') || '（无）'}；`,
    `- 平台分布：${stats.platforms.map(entry => `${entry.platform} ${String(entry.count)}`).join('、') || '（无）'}；`,
    '',
    `告警（最新 ${String(newestAlerts.length)} 条，未处理优先）：`,
    ...(newestAlerts.length === 0 ? ['  （无）'] : newestAlerts.map(alert => `  ${alertLine(alert, taskName(alert.taskId))}${alert.handled ? '〔已处理〕' : ''}`)),
    '',
    `提及明细（最新 ${String(newestMentions.length)} 条）：`,
    ...(newestMentions.length === 0 ? ['  （无）'] : newestMentions.map(mention => `  ${mentionLine(mention)}`)),
  ]
  return lines.join('\n').slice(0, FRAMED_CAP)
}

/**
 * Choose the report template deterministically: the crisis brief when an
 * unhandled alert sits at the crisis level or above, the routine daily
 * report otherwise.
 */
export function selectReportTemplate(alerts: readonly SentimentAlert[]): readonly ReportSectionSpec[] {
  const crisis = alerts.some(alert => !alert.handled && alert.level <= SENTIMENT_CRISIS_ALERT_LEVEL)
  return crisis ? CRISIS_TEMPLATE : DAILY_TEMPLATE
}

/**
 * Render the deterministic data-only report every generation falls back to
 * when the model call fails — the report still lands, named as degraded.
 * @param frame - the same framed text the model would have read.
 * @returns the Markdown fallback.
 */
export function degradedSentimentReport(frame: string): string {
  return [
    '# 舆情日报（数据版降级）',
    '',
    '本次 AI 总结调用失败，以下为未经模型加工的数据快照；点击「生成报告」可重试。',
    '',
    frame,
  ].join('\n')
}

/** Deterministic fallback body for one failed section. */
function degradedSectionBody(spec: ReportSectionSpec, stats: SentimentStats): string {
  if (spec.key === 'overview' || spec.key === 'panorama') {
    return `本次 AI 生成失败。数据快照：总提及 ${String(stats.total)} 条（正面 ${String(stats.positive)}、中性 ${String(stats.neutral)}、负面 ${String(stats.negative)}），告警 ${String(stats.highRisk)} 条。`
  }
  return '（本节生成失败，点击「生成报告」可重试。）'
}

/**
 * Generate one sentiment report: template selection, per-section model
 * calls (parallel), each section degrading independently; a fully failed
 * generation falls back to the deterministic data-only report.
 * @param ctx - context exposing the registered llm service.
 * @param policy - the resolved AI call policy.
 * @param snapshot - the stored snapshot the report covers.
 * @param stats - the dashboard projection over the same mentions.
 * @param now - the generation instant.
 * @returns the report document to persist.
 */
export async function generateSentimentReport(
  ctx: Context,
  policy: AiCallPolicy,
  snapshot: SentimentSnapshot,
  stats: SentimentStats,
  now: Date,
): Promise<SentimentReport> {
  const frame = frameSentimentReport(snapshot.mentions, snapshot.alerts, snapshot.tasks, stats, snapshot.settings)
  const base = {
    generatedAt: now.toISOString(),
    promptVersion: SENTIMENT_REPORT_PROMPT_VERSION,
    mentionCount: Math.min(snapshot.mentions.length, SENTIMENT_REPORT_MENTION_CAP),
    alertCount: Math.min(snapshot.alerts.length, SENTIMENT_REPORT_ALERT_CAP),
  }
  const template = selectReportTemplate(snapshot.alerts)
  const generated = await Promise.all(template.map(async spec => {
    const system = `${REPORT_PREAMBLE}\n本章节是「${spec.title}」：${spec.instruction}`
    try {
      const body = (await streamLlmText(ctx, policy, system, frame, SENTIMENT_REPORT_TIMEOUT_CODE)).trim().slice(0, SECTION_BODY_CAP)
      return { spec, body, ok: body.length > 0 }
    } catch {
      return { spec, body: degradedSectionBody(spec, stats), ok: false }
    }
  }))
  if (generated.every(section => !section.ok)) {
    return { markdown: degradedSentimentReport(frame), degraded: true, ...base }
  }
  const ir: SentimentReportIr = {
    template: template === CRISIS_TEMPLATE ? 'crisis' : 'daily',
    sections: generated.map(({ spec, body }) => ({ key: spec.key, title: spec.title, body })),
  }
  const markdown = [
    ir.template === 'crisis' ? '# 舆情专项报告（危机版）' : '# 舆情日报',
    '',
    ...ir.sections.flatMap(section => [`## ${section.title}`, '', section.body, '']),
  ].join('\n')
  return { markdown, degraded: generated.some(section => !section.ok), ir, ...base }
}
