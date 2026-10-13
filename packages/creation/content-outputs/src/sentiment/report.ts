/**
 * The sentiment report engine: one generation call renders the stored
 * snapshot (tasks, mentions, alerts, stats) into a Markdown daily report
 * through the shared LLM face, with a deterministic data-only fallback when
 * the model call fails — the review column's degraded-report pattern. The
 * gateway stores the returned report; this module never touches the disk.
 */

import type { Context } from '@deepseek-ai/cordis'
import type { AiCallPolicy } from '../gather/ai.ts'
import { streamLlmText } from '../gather/ai.ts'
import type { SentimentAlert, SentimentMention, SentimentSettings, SentimentSnapshot, SentimentStats, SentimentTask } from './types.ts'

/** Timeout reason code carried by aborted sentiment report calls. */
export const SENTIMENT_REPORT_TIMEOUT_CODE = 'SENTIMENT_REPORT_TIMEOUT'

/** Prompt version of the sentiment report face. */
export const SENTIMENT_REPORT_PROMPT_VERSION = 'sentiment-report@1'

/** Mentions handed to the model, newest first (cost bound). */
export const SENTIMENT_REPORT_MENTION_CAP = 40

/** Alerts handed to the model, newest first. */
export const SENTIMENT_REPORT_ALERT_CAP = 10

/** Character cap of one mention line in the framed input. */
const MENTION_LINE_CAP = 200

/** Character cap of the whole framed input handed to the model. */
const FRAMED_CAP = 12_000

const REPORT_SYSTEM_PROMPT = [
  '你是企业舆情分析助手。基于给定的当日舆情数据，输出一份结构化舆情日报（Markdown）。',
  '报告必须严格按以下五个二级标题组织，标题原文照抄：',
  '1. ## 今日概览',
  '2. ## 负面舆情与风险点',
  '3. ## 正面声音与亮点',
  '4. ## 建议处置动作',
  '5. ## 明日关注清单',
  '「今日概览」用 2-3 句话概括总量、情感结构与最重要的事件；',
  '「负面舆情与风险点」按告警等级从高到低展开，引用原文标题与依据短语；',
  '「正面声音与亮点」提炼可放大的正面信号；',
  '「建议处置动作」输出 3-5 条动词开头、可直接执行的建议，黄金响应窗口内的优先；',
  '「明日关注清单」列出 2-4 条需要持续跟踪的事件或关键词。',
  '只依据给定事实与数字，不要编造数据；只输出报告本身，不要解释或前言。',
].join('\n')

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

/**
 * Generate one sentiment report: one model call over the framed snapshot,
 * degrading to the deterministic template on any failure.
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
  try {
    const markdown = await streamLlmText(ctx, policy, REPORT_SYSTEM_PROMPT, frame, SENTIMENT_REPORT_TIMEOUT_CODE)
    return { markdown, degraded: false, ...base }
  } catch {
    return { markdown: degradedSentimentReport(frame), degraded: true, ...base }
  }
}
