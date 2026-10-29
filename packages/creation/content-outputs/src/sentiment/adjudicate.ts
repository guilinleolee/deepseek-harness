/**
 * The alert adjudication engine: one on-demand debate over one high-level
 * alert. Two model calls with opposed stances — the optimistic reader
 * hunting mitigating factors and false-positive arguments, the cautious
 * reader hunting escalation risks — run in parallel, and one synthesis call
 * weighs both readings into a verdict. Every call degrades on its own: an
 * unusable stance renders as its failure note, the synthesis falls back to
 * a deterministic join of the two stances. Never runs inside the scheduled
 * scan — the user triggers it per alert from the alert center.
 */

import type { Context } from '@deepseek-ai/cordis'
import type { AiCallPolicy } from '../gather/ai.ts'
import { streamLlmText } from '../gather/ai.ts'
import type { SentimentAlert, SentimentAlertAdjudication, SentimentMention, SentimentTask } from './types.ts'

/** Timeout reason code carried by aborted sentiment adjudication calls. */
export const SENTIMENT_ADJUDICATE_TIMEOUT_CODE = 'SENTIMENT_ADJUDICATE_TIMEOUT'

/** Prompt version of the adjudication face. */
export const SENTIMENT_ADJUDICATE_PROMPT_VERSION = 'sentiment-adjudicate@1'

/** Mentions handed to the debaters, newest first (cost bound). */
export const SENTIMENT_ADJUDICATE_MENTION_CAP = 12

/** Character cap of one stance output. */
export const SENTIMENT_ADJUDICATE_STANCE_CAP = 400

const DEBATE_PREAMBLE = [
  '你是企业舆情研判专家。针对一条舆情告警，从指定立场输出一段 100 字以内的判断。',
  '要求：',
  '- 只依据给定的事实与数字，不要编造；',
  '- 只输出判断本身，不要标题、解释或前言。',
].join('\n')

const OPTIMISTIC_PROMPT = `${DEBATE_PREAMBLE}\n你的立场是「乐观审读」：寻找可缓释因素与误报可能——例如正面语境、历史误报模式、小样本放大、竞品水军等；如果证据确实充分，就明确说证据充分。`

const CAUTIOUS_PROMPT = `${DEBATE_PREAMBLE}\n你的立场是「审慎审读」：寻找升级风险与最坏情形——例如扩散路径、关联事件、媒体转载风险、历史相似危机；如果风险有限，就明确说风险有限。`

const SYNTHESIS_PROMPT = [
  '你是企业舆情研判主持人。综合乐观与审慎两段判断，输出一段 120 字以内的最终结论。',
  '要求：给出倾向性判断（高危属实 / 部分属实 / 大概率误报）与理由，并给出一条首要处置建议。',
  '只依据给定内容，不要编造；只输出结论本身。',
].join('\n')

/** Failure note replacing an unusable stance output. */
const STANCE_FALLBACK = '（本视角生成失败）'

/** The framed alert + related mentions handed to both debaters. */
function frameAdjudication(alert: SentimentAlert, task: SentimentTask | undefined, mentions: readonly SentimentMention[]): string {
  const related = mentions
    .filter(mention => alert.mentionIds.includes(mention.id))
    .slice(0, SENTIMENT_ADJUDICATE_MENTION_CAP)
  return [
    `告警：[L${String(alert.level)}] ${alert.summary}`,
    `依据：${alert.reason}`,
    `所属任务：${task?.name ?? alert.taskId}（分组：${task?.group ?? '未知'}）`,
    '',
    '相关提及：',
    ...(related.length === 0 ? ['  （无）'] : related.map(mention => `  [${mention.platform}] ${mention.polarity} ${mention.title}`)),
  ].join('\n')
}

/** Clean one stance output: trimmed, capped, empty→failure note. */
function stanceOf(output: string): string {
  const trimmed = output.trim()
  return trimmed.length === 0 ? STANCE_FALLBACK : trimmed.slice(0, SENTIMENT_ADJUDICATE_STANCE_CAP)
}

/**
 * Deterministic synthesis used when the synthesis call fails: join both
 * stances so the verdict always carries the debate.
 */
function joinStances(optimistic: string, cautious: string): string {
  return `乐观视角：${optimistic}；审慎视角：${cautious}。`
}

/**
 * Run one dual-perspective adjudication of one alert.
 * @param ctx - context exposing the registered llm service.
 * @param policy - the resolved AI call policy.
 * @param alert - the alert to adjudicate.
 * @param task - the alert's owning task (name/group context).
 * @param mentions - the snapshot's mentions (related ones are filtered out).
 * @param now - the adjudication instant.
 * @returns the verdict to attach to the alert.
 */
export async function adjudicateSentimentAlert(
  ctx: Context,
  policy: AiCallPolicy,
  alert: SentimentAlert,
  task: SentimentTask | undefined,
  mentions: readonly SentimentMention[],
  now: Date,
): Promise<SentimentAlertAdjudication> {
  const frame = frameAdjudication(alert, task, mentions)
  const [optimisticRead, cautiousRead] = await Promise.all([
    streamLlmText(ctx, policy, OPTIMISTIC_PROMPT, frame, SENTIMENT_ADJUDICATE_TIMEOUT_CODE).catch(() => STANCE_FALLBACK),
    streamLlmText(ctx, policy, CAUTIOUS_PROMPT, frame, SENTIMENT_ADJUDICATE_TIMEOUT_CODE).catch(() => STANCE_FALLBACK),
  ])
  const optimistic = stanceOf(optimisticRead)
  const cautious = stanceOf(cautiousRead)
  let conclusion: string
  try {
    const synthesis = await streamLlmText(ctx, policy, SYNTHESIS_PROMPT, `${frame}\n\n乐观判断：${optimistic}\n审慎判断：${cautious}`, SENTIMENT_ADJUDICATE_TIMEOUT_CODE)
    const trimmed = synthesis.trim()
    conclusion = trimmed.length === 0 ? joinStances(optimistic, cautious) : trimmed.slice(0, SENTIMENT_ADJUDICATE_STANCE_CAP)
  } catch {
    conclusion = joinStances(optimistic, cautious)
  }
  return { optimistic, cautious, conclusion, at: now.toISOString() }
}
