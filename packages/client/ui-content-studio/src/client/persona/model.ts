/**
 * The persona wizard's editable form model: the browser-side shape between
 * the wire `PersonaEntry` and the four-step form. Every wire round-trip goes
 * through {@link formFromEntry} / {@link inputFromForm}, and every field
 * edit flips its provenance back to `user` — the AI never stays the source
 * of a value the user has touched.
 */

import type {
  PersonaAccountStage, PersonaEntry, PersonaField, PersonaFieldKey, PersonaFieldSource,
  PersonaId, PersonaInput, PersonaLink, PersonaPlatform, PersonaReport, PersonaStylePreset,
  PersonaStyleStrength,
} from '@deepseek-ai/dsh-content-outputs/types'

/**
 * The persona vocabulary the browser owns: the platform, field, and style
 * enum tables for the pickers, the packed prompt preview, and the fill
 * scope. The gateway carries the same keys for wire validation and the
 * digest; the sync between the two sides is pinned by a cross-check test,
 * because the bundle purity gate forbids importing the gateway's tables as
 * values here.
 */

/** Every persona platform, in picker order; the competitor face's word list extended. */
export const PERSONA_PLATFORMS = ['xhs', 'douyin', 'bili', 'zhihu', 'wechat', 'channels', 'weibo', 'toutiao'] as const

/** Chinese label of one persona platform. */
export const PERSONA_PLATFORM_LABELS: Readonly<Record<PersonaPlatform, string>> = {
  xhs: '小红书',
  douyin: '抖音',
  bili: 'B 站',
  zhihu: '知乎',
  wechat: '公众号',
  channels: '视频号',
  weibo: '微博',
  toutiao: '今日头条',
}

/** Every persona field key, in wizard order. */
export const PERSONA_FIELD_KEYS = ['whoAmI', 'audience', 'oneLiner', 'niche', 'goal', 'monetize', 'contentValue', 'cadence', 'phrases'] as const

/** Chinese label of one persona field. */
export const PERSONA_FIELD_LABELS: Readonly<Record<PersonaFieldKey, string>> = {
  whoAmI: '我是谁（主体背景）',
  audience: '目标受众',
  oneLiner: '人设一句话简介',
  niche: '赛道 / 行业',
  goal: '核心目标',
  monetize: '变现方式',
  contentValue: '内容核心价值',
  cadence: '更新节奏',
  phrases: '推荐句式 / 表达习惯',
}

/** Field keys the generic fill operation must never produce: the subject background is a fact only the user or the résumé face supplies. */
export const PERSONA_FILL_PROHIBITED: readonly PersonaFieldKey[] = ['whoAmI']

/**
 * Platforms the browser-session social-capture faces support (the client
 * copy of the gateway's vocabulary; the sync test pins the two tables).
 */
export const SOCIAL_PLATFORMS = ['xhs', 'douyin', 'weibo', 'bili'] as const

/** One social-capture platform. */
export type SocialPlatform = (typeof SOCIAL_PLATFORMS)[number]

/** The four step-3 intent fields; the step's chips and the scoped AI inference address exactly these. */
export const PERSONA_INTENT_FIELDS: readonly ('goal' | 'monetize' | 'contentValue' | 'cadence')[] = ['goal', 'monetize', 'contentValue', 'cadence']

/**
 * Preset answer options of the enumerable intent fields, in chip order:
 * goal and monetize are multi-select, cadence is single-select. Clicking
 * composes the labels into the field's plain string value, so the wire
 * contract stays untouched.
 */
export const PERSONA_INTENT_OPTIONS: Readonly<Record<'goal' | 'monetize' | 'cadence', readonly string[]>> = {
  goal: ['涨粉起号', '获客留资', '品牌曝光', '带货转化', '引流到店', '私域沉淀'],
  monetize: ['广告合作', '知识付费', '直播带货', '电商转化', '到店消费', '咨询服务'],
  cadence: ['每天 1 条', '每周 3 条', '每周 2 条', '每周 1 条', '不定期'],
}

/** Template phrases offered for the content-value free field; clicking one seeds the input for editing. */
export const PERSONA_CONTENT_VALUE_TEMPLATES: readonly string[] = ['教用户怎么做（教程型）', '帮用户少走弯路（避坑型）', '行业资讯与解读（资讯型）']

/** One readable sample line per style preset, shown under the chips when selected: users pick by reading, not by decoding the label. */
export const PERSONA_STYLE_SAMPLES: Readonly<Record<PersonaStylePreset, string>> = {
  professional: '本产品通过国家质检标准，故障率低于 0.1%。',
  friendly: '姐妹们，这家店我真的回购八百次了！',
  humor: '咱就是说，这功能一开，效率直接起飞。',
  concise: '三个要点一分钟看完：先设置，再同步，最后备份。',
  narrative: '去年这个时候我还在为获客发愁，直到遇见了它。',
  hardcore: '实测数据说话：同配置续航提升 23%，附测试方法。',
  empathy: '带娃已经很累了，收拾屋子的事交给我来帮你。',
}

/** Preset red-line choices offered as chips; the field value stays a plain joined string. */
export const PERSONA_RED_LINE_PRESETS: readonly string[] = ['不聊政治', '不提竞品', '不做医疗功效承诺', '不做投资收益承诺', '不使用极限词']

/** One stored intent value split into its preset selections and the hand-written remainder. */
export interface IntentSelection {
  readonly selected: readonly string[]
  readonly custom: string
}

/**
 * Split one stored intent value: preset labels become chip selections (in
 * preset order), every other segment lands in the custom remainder — a
 * hand-written or AI-inferred value keeps displaying without a match.
 * @param value - the stored field value.
 * @param options - the field's preset labels.
 * @returns the selections plus the custom remainder joined by '；'.
 */
export function parseIntents(value: string, options: readonly string[]): IntentSelection {
  const segments = value.split(/[、，,；;\n]/u).map(segment => segment.trim()).filter(segment => segment.length > 0)
  return {
    selected: options.filter(option => segments.includes(option)),
    custom: segments.filter(segment => !options.includes(segment)).join('；'),
  }
}

/**
 * Join one intent value back together: selections first (preset order),
 * then the custom remainder; empty pieces drop.
 * @param selected - the selected preset labels.
 * @param custom - the hand-written remainder.
 * @returns the composed field value ('' when everything is empty).
 */
export function joinIntents(selected: readonly string[], custom: string): string {
  return [...selected, custom.trim()].filter(segment => segment.length > 0).join('；')
}

/** Every style preset, in picker order. */
export const PERSONA_STYLE_PRESETS = ['professional', 'friendly', 'humor', 'concise', 'narrative', 'hardcore', 'empathy'] as const

/** Chinese label of one style preset. */
export const PERSONA_STYLE_PRESET_LABELS: Readonly<Record<PersonaStylePreset, string>> = {
  professional: '专业严谨',
  friendly: '亲切接地气',
  humor: '幽默网感',
  concise: '简洁干练',
  narrative: '故事叙事',
  hardcore: '硬核干货',
  empathy: '温柔共情',
}

/** One editable structured field: the text plus the provenance it keeps. */
export interface PersonaFormField {
  value: string
  source: PersonaFieldSource
  aiMeta: PersonaField['aiMeta']
}

/** The wizard's editable form. Text areas hold raw text; word lists are parsed on save. */
export interface PersonaForm {
  editingId: PersonaId | null
  clonedFrom: PersonaId | null
  name: string
  platforms: PersonaPlatform[]
  accountStage: PersonaAccountStage
  fields: Record<PersonaFieldKey, PersonaFormField>
  links: PersonaLink[]
  siteUrl: string
  sitePastedText: string
  preset: PersonaStylePreset | null
  customText: string
  strength: PersonaStyleStrength
  bannedWordsText: string
  redLinesText: string
  resumeText: string
  resumeName: string | null
  resumeConsent: boolean
  /** The stored report rides the form untouched: editing it is a separate save path. */
  report: PersonaReport | null
  /**
   * Browser-session captures from the step-2 social faces, consumed by the
   * social AI analysis and never persisted on the wire — the adopted fields
   * are the persistence.
   */
  socialProfiles: SocialCaptureBuffer[]
}

/** One captured social profile section (labeled), keyed by its platform. */
export interface SocialCaptureBuffer {
  platform: SocialPlatform
  text: string
}

/**
 * The empty form of a brand-new persona.
 * @returns the form with every field blank, no editing target, and no stored report.
 */
export function emptyForm(): PersonaForm {
  const fields = {} as Record<PersonaFieldKey, PersonaFormField>
  for (const key of PERSONA_FIELD_KEYS) fields[key] = { value: '', source: 'user', aiMeta: null }
  return {
    editingId: null,
    clonedFrom: null,
    name: '',
    platforms: [],
    accountStage: 'fresh',
    fields,
    links: [],
    siteUrl: '',
    sitePastedText: '',
    preset: null,
    customText: '',
    strength: 'light',
    bannedWordsText: '',
    redLinesText: '',
    resumeText: '',
    resumeName: null,
    resumeConsent: false,
    report: null,
    socialProfiles: [],
  }
}

/** Stored field → editable text; nulls become empty strings. */
function fieldText(field: PersonaField): PersonaFormField {
  return { value: field.value ?? '', source: field.source, aiMeta: field.aiMeta }
}

/**
 * Build the form from a stored entry.
 * @param entry - the stored persona.
 * @param options - `clone: true` builds a clone draft: no editing id, the
 *   source recorded as `clonedFrom`, and the report remapped to the clone's
 *   revision 1 so the staleness banner stays correct.
 * @returns the editable form.
 */
export function formFromEntry(entry: PersonaEntry, options: { clone?: boolean } = {}): PersonaForm {
  const base = emptyForm()
  return {
    ...base,
    editingId: options.clone === true ? null : entry.id,
    clonedFrom: options.clone === true ? entry.id : null,
    name: entry.name,
    platforms: [...entry.platforms],
    accountStage: entry.accountStage,
    fields: Object.fromEntries(
      PERSONA_FIELD_KEYS.map(key => [key, fieldText(entry.fields[key])]),
    ) as Record<PersonaFieldKey, PersonaFormField>,
    links: entry.links.map(link => ({ ...link })),
    siteUrl: entry.site.url ?? '',
    sitePastedText: entry.site.pastedText ?? '',
    preset: entry.style.preset,
    customText: entry.style.customText ?? '',
    strength: entry.style.strength,
    bannedWordsText: entry.style.bannedWords.join('；'),
    redLinesText: entry.style.redLines.join('；'),
    resumeText: entry.assets.resumeText ?? '',
    resumeName: entry.assets.resumeName,
    report: options.clone === true && entry.report !== null
      ? { ...entry.report, sourceRevision: 1 }
      : entry.report,
  }
}

/**
 * Parse one textarea's word list: entries separated by newlines, Chinese or
 * ASCII commas and semicolons (the join separator on the way back into the
 * form); blanks drop.
 * @param text - the raw textarea text.
 * @returns the trimmed, non-empty entries.
 */
export function parseWordList(text: string): string[] {
  return text.split(/\n|，|,|；|;/u).map(word => word.trim()).filter(word => word.length > 0)
}

/**
 * Build the upsert payload from the form. Empty field texts become `null`
 * values; a touched field keeps `user` provenance and loses any AI metadata.
 * Links without a URL drop — the step-2 list renders a row per platform and
 * unfilled rows are not links.
 * @param form - the wizard form.
 * @returns the gateway upsert payload (digest, revision, timestamps are gateway-owned).
 */
export function inputFromForm(form: PersonaForm): PersonaInput {
  const fields = {} as Record<PersonaFieldKey, PersonaField>
  for (const key of PERSONA_FIELD_KEYS) {
    const field = form.fields[key]
    const value = field.value.trim()
    fields[key] = {
      value: value.length === 0 ? null : value,
      source: field.source,
      aiMeta: field.source === 'ai' ? field.aiMeta : null,
    }
  }
  return {
    ...(form.editingId === null ? {} : { id: form.editingId }),
    name: form.name.trim(),
    platforms: [...form.platforms],
    accountStage: form.accountStage,
    fields,
    links: form.links.filter(link => link.url.trim().length > 0).map(link => ({ ...link })),
    site: {
      url: form.siteUrl.trim().length === 0 ? null : form.siteUrl.trim(),
      pastedText: form.sitePastedText.trim().length === 0 ? null : form.sitePastedText,
    },
    style: {
      preset: form.preset,
      customText: form.customText.trim().length === 0 ? null : form.customText.trim(),
      strength: form.strength,
      bannedWords: parseWordList(form.bannedWordsText),
      redLines: parseWordList(form.redLinesText),
    },
    assets: { resumeText: form.resumeText.trim().length === 0 ? null : form.resumeText, resumeName: form.resumeName },
    report: form.report,
    clonedFrom: form.clonedFrom,
  }
}

/**
 * Adopt one AI candidate into the form: the value lands with `ai` source
 * and the prompt's provenance stamped at the adoption instant.
 * @param form - the wizard form (mutated copy returned).
 * @param key - the field to fill.
 * @param value - the adopted text.
 * @param promptVersion - the AI prompt that produced the value.
 * @returns the next form.
 */
export function adoptField(form: PersonaForm, key: PersonaFieldKey, value: string, promptVersion: string): PersonaForm {
  return {
    ...form,
    fields: {
      ...form.fields,
      [key]: { value, source: 'ai', aiMeta: { promptVersion, at: new Date().toISOString() } },
    },
  }
}
