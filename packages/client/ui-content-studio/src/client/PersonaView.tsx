/**
 * The persona view: the account-persona card list over the `_personas.json`
 * manifest, the four-step wizard (basics with the résumé and the own-site
 * evidence block, social links, intent, style and red lines), the explicit
 * AI helpers (blank-field fill, résumé extraction with its consent gate,
 * website extraction), and the report panel (generate, edit with the
 * staleness banner, confirmed regeneration). All state and actions live on
 * the injected controller; this file only wires them to the DOM.
 */
import { useEffect, useRef, useState, useSyncExternalStore, type ReactNode } from 'react'
import { DisclosureRow, IconSparkle16, writeClipboard } from '@deepseek-ai/dsh-client-ui-primitives'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import type { PersonaEntry, PersonaFieldKey, PersonaId } from '@deepseek-ai/dsh-content-outputs/types'
import { parseWordList } from './persona/model.ts'
import type { SocialPlatform } from './persona/model.ts'
import {
  joinIntents, parseIntents, PERSONA_CONTENT_VALUE_TEMPLATES, PERSONA_INTENT_FIELDS,
  PERSONA_INTENT_OPTIONS, PERSONA_RED_LINE_PRESETS, PERSONA_STYLE_SAMPLES, SOCIAL_PLATFORMS,
} from './persona/model.ts'
import {
  PERSONA_FIELD_KEYS, PERSONA_FIELD_LABELS, PERSONA_PLATFORMS, PERSONA_PLATFORM_LABELS,
  PERSONA_STYLE_PRESETS, PERSONA_STYLE_PRESET_LABELS,
} from './persona/model.ts'
import type { PersonaController, PersonaNotice, PersonaState } from './persona/persona-store.ts'
import { renderPersonaPrompt } from './persona/prompt.ts'
import type { StudioKey } from './locales.ts'
import css from './PersonaView.module.css'

/** Props: the injected controller plus the locale seat. */
export type PersonaViewProps = {
  personas: PersonaController
} & PropsLocale<'content-studio'>

/** Client-side cap for pasted / uploaded text; the wire rejects beyond this. */
const TEXT_CAP = 100_000

/** The platforms whose step-2 rows carry the browser-session login/capture buttons. */
const SOCIAL_PLATFORM_SET: ReadonlySet<string> = new Set<string>(SOCIAL_PLATFORMS)

/**
 * Render the persona page.
 * @param props - the injected controller and the locale seat.
 * @returns the page element tree.
 */
export function PersonaView({ personas, t }: PersonaViewProps) {
  const state = useSyncExternalStore(listener => personas.subscribe(listener), () => personas.getState())
  const [previewId, setPreviewId] = useState<PersonaId | null>(null)

  useEffect(() => { void personas.ensureLoaded() }, [personas])
  useEffect(() => {
    if (state.wizard !== null) void personas.refreshSocialStatuses()
  }, [state.wizard, personas])

  const previewEntry = previewId === null ? null : state.personas.find(entry => entry.id === previewId) ?? null
  const reportEntry = state.reportId === null ? null : state.personas.find(entry => entry.id === state.reportId) ?? null

  return (
    <div className={css.persona}>
      <div className={css.personaHead}>
        <div>
          <h2 className={css.personaTitle}>{t('persona.title')}</h2>
          <p className={css.personaHint}>{t('persona.hint')}</p>
        </div>
        <button type="button" className={css.personaPrimary} onClick={() => { personas.openNew() }}>
          {t('persona.new')}
        </button>
      </div>

      {state.legacyText !== null && (
        <div className={css.personaBanner} role="status">
          <span>{t('persona.legacy.text')}</span>
          <button type="button" className={css.personaMini} onClick={() => { void personas.importLegacy(t('persona.legacy.name')) }}>
            {t('persona.legacy.import')}
          </button>
          <button type="button" className={css.personaMini} onClick={() => { personas.dismissLegacy() }}>
            {t('persona.legacy.dismiss')}
          </button>
        </div>
      )}
      {state.problems.length > 0 && (
        <div className={css.personaBanner} role="alert">
          {`${t('persona.problems')} ${state.problems.join(' ')}`}
        </div>
      )}
      {state.notice !== null && (
        <button type="button" className={css.personaNotice} role="status" onClick={() => { personas.dismissNotice() }}>
          {t(`persona.notice.${state.notice}`)}
          {state.noticeDetail !== null && <span>{` — ${state.noticeDetail}`}</span>}
        </button>
      )}

      {state.loading ? <p className={css.personaEmpty}>{t('persona.loading')}</p>
        : state.personas.length === 0 ? <p className={css.personaEmpty}>{t('persona.empty')}</p>
          : (
            <div className={css.personaGrid}>
              {state.personas.map(entry => (
                <PersonaCardView
                  key={entry.id}
                  entry={entry}
                  selected={state.selectedId === entry.id}
                  controller={personas}
                  previewOpen={previewId === entry.id}
                  onTogglePreview={() => { setPreviewId(previewId === entry.id ? null : entry.id) }}
                  t={t}
                />
              ))}
            </div>
          )}

      {previewEntry !== null && <PersonaPreviewPanel entry={previewEntry} controller={personas} t={t} />}
      {state.wizard !== null && <PersonaWizard state={state} controller={personas} t={t} />}
      {reportEntry !== null && <PersonaReportPanel entry={reportEntry} controller={personas} t={t} />}
    </div>
  )
}

/** One persona card: identity chips, the digest line, and the six actions. */
function PersonaCardView(props: {
  entry: PersonaEntry
  selected: boolean
  previewOpen: boolean
  controller: PersonaController
  onTogglePreview: () => void
  t: PropsLocale<'content-studio'>['t']
}) {
  const { entry, selected, previewOpen, controller, onTogglePreview, t } = props
  const stale = entry.report !== null && entry.revision > entry.report.sourceRevision
  return (
    <article className={css.personaCard}>
      <div className={css.personaCardHead}>
        <h3 className={css.personaCardName}>{entry.name}</h3>
        {selected && <span className={css.personaBadgeActive}>{t('persona.card.selected')}</span>}
        {entry.report !== null && (
          <span className={stale ? css.personaBadgeStale : css.personaBadge}>{stale ? t('persona.card.stale') : t('persona.card.report')}</span>
        )}
      </div>
      <div className={css.personaChips}>
        {entry.platforms.map(platform => <span key={platform} className={css.personaChip}>{PERSONA_PLATFORM_LABELS[platform]}</span>)}
        {entry.fields.niche.value !== null && <span className={css.personaChip}>{entry.fields.niche.value}</span>}
      </div>
      <p className={css.personaDigest}>{entry.digest}</p>
      <div className={css.personaActions}>
        <button type="button" className={css.personaMini} onClick={() => { controller.select(selected ? null : entry.id) }}>
          {t(selected ? 'persona.card.deselect' : 'persona.card.select')}
        </button>
        <button type="button" className={css.personaMini} onClick={onTogglePreview}>
          {t(previewOpen ? 'persona.card.hide' : 'persona.card.preview')}
        </button>
        <button type="button" className={css.personaMini} onClick={() => { controller.openEdit(entry.id) }}>{t('persona.card.edit')}</button>
        <button type="button" className={css.personaMini} onClick={() => { controller.openReport(entry.id) }}>{t('persona.card.reportView')}</button>
        <button type="button" className={css.personaMini} onClick={() => { controller.openClone(entry.id) }}>{t('persona.card.clone')}</button>
        <button
          type="button"
          className={css.personaMini}
          onClick={() => {
            if (window.confirm(t('persona.delete.confirm').replace('{name}', entry.name))) void controller.remove(entry.id)
          }}
        >
          {t('persona.card.delete')}
        </button>
      </div>
    </article>
  )
}

/** The structured side preview: every field with its provenance badge, plus style and constraints. */
function PersonaPreviewPanel(props: {
  entry: PersonaEntry
  controller: PersonaController
  t: PropsLocale<'content-studio'>['t']
}) {
  const { entry, controller, t } = props
  const sourceBadge = (source: 'user' | 'ai' | 'template'): string =>
    source === 'ai' ? t('persona.preview.source.ai') : source === 'template' ? t('persona.preview.source.template') : t('persona.preview.source.user')
  return (
    <section className={css.personaPreview} aria-label={t('persona.preview.title')}>
      <div className={css.personaPreviewHead}>
        <h3>{t('persona.preview.title')}</h3>
        {entry.id !== controller.getState().selectedId && (
          <button type="button" className={css.personaMini} onClick={() => { controller.select(entry.id) }}>
            {t('persona.preview.use')}
          </button>
        )}
      </div>
      <dl className={css.personaFacts}>
        {PERSONA_FIELD_KEYS.map((key) => {
          const field = entry.fields[key]
          if (field.value === null) return null
          return (
            <div key={key} className={css.personaFact}>
              <dt>{PERSONA_FIELD_LABELS[key]} <span className={css.personaSource}>{sourceBadge(field.source)}</span></dt>
              <dd>{field.value}</dd>
            </div>
          )
        })}
      </dl>
      <p className={css.personaFactLine}>
        {`${t('persona.preview.digest')}：${entry.digest}`}
      </p>
      {entry.style.bannedWords.length > 0 && (
        <p className={css.personaFactLine}>{`${t('persona.preview.banned')}：${entry.style.bannedWords.join('；')}`}</p>
      )}
      {entry.style.redLines.length > 0 && (
        <p className={css.personaFactLine}>{`${t('persona.preview.red')}：${entry.style.redLines.join('；')}`}</p>
      )}
    </section>
  )
}

/** Shared label+control row for the wizard's fields; the optional hint line tells the user how to fill it. */
function FieldRow(props: { label: string; hint?: string; children: ReactNode }) {
  return (
    <label className={css.personaField}>
      <span className={css.personaFieldLabel}>{props.label}</span>
      {props.hint !== undefined && <span className={css.personaFieldHint}>{props.hint}</span>}
      {props.children}
    </label>
  )
}

/**
 * The one-step outcome notice. The page-level bar sits behind the wizard and
 * report overlays (`position: fixed`), so each modal renders its own copy —
 * without it, every action's feedback ("no blank fields", "AI call failed")
 * would be invisible while a modal is open.
 */
function NoticeBar(props: {
  notice: PersonaNotice | null
  noticeDetail: string | null
  controller: PersonaController
  t: PropsLocale<'content-studio'>['t']
}) {
  if (props.notice === null) return null
  return (
    <button type="button" className={css.personaNotice} role="status" onClick={() => { props.controller.dismissNotice() }}>
      {props.t(`persona.notice.${props.notice}`)}
      {props.noticeDetail !== null && <span>{` — ${props.noticeDetail}`}</span>}
    </button>
  )
}

/** The four-step wizard modal, driven entirely by the controller's form state. */
function PersonaWizard(props: {
  state: PersonaState
  controller: PersonaController
  t: PropsLocale<'content-studio'>['t']
}) {
  const { state, controller, t } = props
  const wizard = state.wizard
  // The advanced disclosure resets to collapsed on every wizard open: the
  // first screen stays one decision (pick a style).
  const [advancedOpen, setAdvancedOpen] = useState(false)
  // The phrases field lives in the advanced block; when the scoped inference
  // targets it (candidates arrived) or reports it already filled, open the
  // block so the value and the message are never hidden behind the fold.
  const advancedRelevant = state.notice === 'scope-filled'
    || (state.fillPreview !== null && 'phrases' in state.fillPreview.fields)
  useEffect(() => {
    if (advancedRelevant) setAdvancedOpen(true)
  }, [advancedRelevant])
  if (wizard === null) return null
  const { step, form } = wizard
  const redLineSelection = parseIntents(form.redLinesText, PERSONA_RED_LINE_PRESETS)
  const toggleRedLine = (option: string): void => {
    const { selected, custom } = redLineSelection
    const next = selected.includes(option) ? selected.filter(candidate => candidate !== option) : [...selected, option]
    // Canonical preset order keeps the stored value stable regardless of click order.
    const ordered = PERSONA_RED_LINE_PRESETS.filter(candidate => next.includes(candidate))
    controller.updateForm({ redLinesText: joinIntents(ordered, custom) })
  }
  const changeRedLineCustom = (text: string): void => {
    controller.updateForm({ redLinesText: joinIntents(redLineSelection.selected, text) })
  }
  const setField = (key: PersonaFieldKey) => (value: string) => { controller.setField(key, value) }
  const intentSelection = (key: 'goal' | 'monetize' | 'cadence') => parseIntents(form.fields[key].value, PERSONA_INTENT_OPTIONS[key])
  const intentChipClass = (key: 'goal' | 'monetize' | 'cadence', option: string): string | undefined =>
    intentSelection(key).selected.includes(option) ? css.personaChipOn : css.personaChip
  /** Toggle one intent chip: multi-select composes, single-select replaces; the custom remainder survives either way. */
  const toggleIntentOption = (key: 'goal' | 'monetize' | 'cadence', option: string, multi: boolean) => {
    const { selected, custom } = intentSelection(key)
    const next = multi
      ? (selected.includes(option) ? selected.filter(candidate => candidate !== option) : [...selected, option])
      : (selected[0] === option ? [] : [option])
    controller.setField(key, joinIntents(next, custom))
  }
  /** Rewrite only the custom remainder of one intent value, keeping the chip selections. */
  const changeIntentCustom = (key: 'goal' | 'monetize' | 'cadence', text: string) => {
    const { selected } = intentSelection(key)
    controller.setField(key, joinIntents(selected, text))
  }
  const revision = form.editingId === null
    ? 1
    : (state.personas.find(entry => entry.id === form.editingId)?.revision ?? 0) + 1
  const prompt = renderPersonaPrompt({
    name: form.name.trim().length > 0 ? form.name : t('persona.preview.unnamed'),
    revision,
    fields: form.fields,
    style: {
      preset: form.preset,
      customText: form.customText.trim().length === 0 ? null : form.customText,
      strength: form.strength,
      bannedWords: parseWordList(form.bannedWordsText),
      redLines: parseWordList(form.redLinesText),
    },
  })
  return (
    <div className={css.personaModal} role="dialog" aria-modal="true" aria-label={t('persona.wizard.title')}>
      <div className={css.personaModalCard}>
        <div className={css.personaModalHead}>
          <h3>{t('persona.wizard.title')}</h3>
          <span className={css.personaStepLabel}>{`${String(step)} / 4 · ${t(`persona.wizard.step${String(step)}` as StudioKey)}`}</span>
          <button type="button" className={css.personaMini} onClick={() => { controller.closeWizard() }} aria-label={t('persona.wizard.close')}>
            {t('persona.wizard.close')}
          </button>
        </div>

        <NoticeBar notice={state.notice} noticeDetail={state.noticeDetail} controller={controller} t={t} />

        {step === 1 && (
          <div className={css.personaStepBody}>
            <FieldRow label={t('persona.name.label')}>
              <input value={form.name} placeholder={t('persona.name.placeholder')} onChange={(event) => { controller.updateForm({ name: event.currentTarget.value }) }} />
            </FieldRow>
            <div className={css.personaField}>
              <span className={css.personaFieldLabel}>{t('persona.platforms.label')}</span>
              <div className={css.personaChips}>
                {PERSONA_PLATFORMS.map(platform => (
                  <button
                    key={platform}
                    type="button"
                    className={form.platforms.includes(platform) ? css.personaChipOn : css.personaChip}
                    onClick={() => { controller.togglePlatform(platform) }}
                  >
                    {PERSONA_PLATFORM_LABELS[platform]}
                  </button>
                ))}
              </div>
            </div>
            <div className={css.personaField}>
              <span className={css.personaFieldLabel}>{t('persona.stage.label')}</span>
              <div className={css.personaChips}>
                {(['fresh', 'existing'] as const).map(stage => (
                  <button
                    key={stage}
                    type="button"
                    className={form.accountStage === stage ? css.personaChipOn : css.personaChip}
                    onClick={() => { controller.setAccountStage(stage) }}
                  >
                    {t(stage === 'fresh' ? 'persona.stage.fresh' : 'persona.stage.existing')}
                  </button>
                ))}
              </div>
            </div>
            <FieldRow label={PERSONA_FIELD_LABELS.niche}>
              <input value={form.fields.niche.value} onChange={(event) => { setField('niche')(event.currentTarget.value) }} />
            </FieldRow>
            <div className={css.personaResume}>
              <FieldRow label={t('persona.resume.title')}>
                <textarea
                  rows={3}
                  placeholder={t('persona.resume.paste')}
                  value={form.resumeText}
                  onChange={(event) => { controller.updateForm({ resumeText: event.currentTarget.value.slice(0, TEXT_CAP) }) }}
                />
              </FieldRow>
              <div className={css.personaResumeRow}>
                <input
                  type="file"
                  accept=".txt,.md"
                  onChange={(event) => {
                    const file = event.currentTarget.files?.[0]
                    void (async () => {
                      if (file === undefined) return
                      const text = (await file.text()).slice(0, TEXT_CAP)
                      controller.updateForm({ resumeText: text, resumeName: file.name })
                    })()
                  }}
                />
                <label className={css.personaConsent}>
                  <input
                    type="checkbox"
                    checked={form.resumeConsent}
                    onChange={(event) => { controller.updateForm({ resumeConsent: event.currentTarget.checked }) }}
                  />
                  {t('persona.resume.consent')}
                </label>
                <button type="button" className={css.personaMini} disabled={state.aiBusy !== false} onClick={() => { void controller.runResume() }}>
                  {state.aiBusy === 'resume' ? t('persona.busy') : t('persona.resume.parse')}
                </button>
              </div>
            </div>
            <FieldRow label={t('persona.site.url.label')}>
              <input placeholder={t('persona.site.url.placeholder')} value={form.siteUrl} onChange={(event) => { controller.updateForm({ siteUrl: event.currentTarget.value }) }} />
            </FieldRow>
            <FieldRow label={t('persona.site.paste.label')}>
              <textarea
                rows={4}
                value={form.sitePastedText}
                onChange={(event) => { controller.updateForm({ sitePastedText: event.currentTarget.value.slice(0, TEXT_CAP) }) }}
              />
            </FieldRow>
            <button type="button" className={css.personaMini} disabled={state.aiBusy !== false} onClick={() => { void controller.runSite() }}>
              {state.aiBusy === 'site' ? t('persona.busy') : t('persona.site.parse')}
            </button>
          </div>
        )}

        {step === 2 && (
          <div className={css.personaStepBody}>
            <p className={css.personaFieldLabel}>{t('persona.links.hint')}</p>
            {PERSONA_PLATFORMS.map((platform) => {
              const socialPlatform: SocialPlatform | null = SOCIAL_PLATFORM_SET.has(platform) ? (platform as SocialPlatform) : null
              const status = socialPlatform === null ? undefined : state.socialStatuses[socialPlatform]
              const sessionReady = status?.hasSession === true
              return (
                <div key={platform} className={css.personaField}>
                  <span className={css.personaFieldLabel}>
                    {PERSONA_PLATFORM_LABELS[platform]}
                    {socialPlatform !== null && sessionReady && (
                      <span className={css.personaFieldHint}>{`（${t('persona.social.sessionOk')}）`}</span>
                    )}
                  </span>
                  <div className={css.personaSocialRow}>
                    <input
                      aria-label={PERSONA_PLATFORM_LABELS[platform]}
                      placeholder={t('persona.links.url')}
                      value={form.links.find(link => link.platform === platform)?.url ?? ''}
                      onChange={(event) => { controller.setLinkUrl(platform, event.currentTarget.value) }}
                    />
                    {socialPlatform !== null && (
                      <button
                        type="button"
                        className={css.personaMini}
                        disabled={state.aiBusy !== false || state.socialLoginPending !== null}
                        title={sessionReady ? t('persona.social.read') : t('persona.social.login')}
                        onClick={() => {
                          if (sessionReady) void controller.captureSocial(socialPlatform)
                          else void controller.startSocialLogin(socialPlatform)
                        }}
                      >
                        {state.socialLoginPending === socialPlatform || state.aiBusy === 'social'
                          ? t('persona.busy')
                          : sessionReady ? t('persona.social.read') : t('persona.social.login')}
                      </button>
                    )}
                  </div>
                </div>
              )
            })}
            <div className={css.personaIntentHead}>
              <span className={css.personaFieldHint}>{t('persona.social.hint')}</span>
              <button type="button" className={css.personaMini} disabled={state.aiBusy !== false} onClick={() => { void controller.runSocial() }}>
                {state.aiBusy === 'social' ? t('persona.busy') : t('persona.social.analyze')}
              </button>
            </div>
          </div>
        )}

        {step === 3 && (
          <div className={css.personaStepBody}>
            <div className={css.personaIntentHead}>
              <span className={css.personaFieldHint}>{t('persona.intent.hint')}</span>
              <button
                type="button"
                className={css.personaMini}
                disabled={state.aiBusy !== false}
                title={t('persona.fill.hint')}
                onClick={() => { void controller.runFill(PERSONA_INTENT_FIELDS) }}
              >
                {state.aiBusy === 'fill' ? t('persona.busy') : t('persona.intent.infer')}
              </button>
            </div>
            <FieldRow label={`${PERSONA_FIELD_LABELS.goal}（可多选）`} hint={t('persona.field.goal.hint')}>
              <div className={css.personaChips}>
                {PERSONA_INTENT_OPTIONS.goal.map(option => (
                  <button
                    key={option}
                    type="button"
                    className={intentChipClass('goal', option)}
                    onClick={() => { toggleIntentOption('goal', option, true) }}
                  >
                    {option}
                  </button>
                ))}
              </div>
              <input
                value={parseIntents(form.fields.goal.value, PERSONA_INTENT_OPTIONS.goal).custom}
                placeholder={t('persona.intent.custom')}
                onChange={(event) => { changeIntentCustom('goal', event.currentTarget.value) }}
              />
            </FieldRow>
            <FieldRow label={`${PERSONA_FIELD_LABELS.monetize}（可多选）`} hint={t('persona.field.monetize.hint')}>
              <div className={css.personaChips}>
                {PERSONA_INTENT_OPTIONS.monetize.map(option => (
                  <button
                    key={option}
                    type="button"
                    className={intentChipClass('monetize', option)}
                    onClick={() => { toggleIntentOption('monetize', option, true) }}
                  >
                    {option}
                  </button>
                ))}
              </div>
              <input
                value={parseIntents(form.fields.monetize.value, PERSONA_INTENT_OPTIONS.monetize).custom}
                placeholder={t('persona.intent.custom')}
                onChange={(event) => { changeIntentCustom('monetize', event.currentTarget.value) }}
              />
            </FieldRow>
            <FieldRow label={PERSONA_FIELD_LABELS.contentValue} hint={t('persona.field.contentValue.hint')}>
              <div className={css.personaChips}>
                {PERSONA_CONTENT_VALUE_TEMPLATES.map(template => (
                  <button key={template} type="button" className={css.personaChip} onClick={() => { setField('contentValue')(template) }}>
                    {template}
                  </button>
                ))}
              </div>
              <input
                value={form.fields.contentValue.value}
                placeholder={t('persona.field.contentValue.placeholder')}
                onChange={(event) => { setField('contentValue')(event.currentTarget.value) }}
              />
            </FieldRow>
            <FieldRow label={PERSONA_FIELD_LABELS.cadence} hint={t('persona.field.cadence.hint')}>
              <div className={css.personaChips}>
                {PERSONA_INTENT_OPTIONS.cadence.map(option => (
                  <button
                    key={option}
                    type="button"
                    className={intentChipClass('cadence', option)}
                    onClick={() => { toggleIntentOption('cadence', option, false) }}
                  >
                    {option}
                  </button>
                ))}
              </div>
              <input
                value={parseIntents(form.fields.cadence.value, PERSONA_INTENT_OPTIONS.cadence).custom}
                placeholder={t('persona.field.cadence.placeholder')}
                onChange={(event) => { changeIntentCustom('cadence', event.currentTarget.value) }}
              />
            </FieldRow>
          </div>
        )}

        {step === 4 && (
          <div className={css.personaStepBody}>
            <div className={css.personaIntentHead}>
              <span className={css.personaFieldHint}>{t('persona.style.hint')}</span>
              <button
                type="button"
                className={css.personaMini}
                disabled={state.aiBusy !== false}
                title={t('persona.fill.hint')}
                onClick={() => { void controller.runFill(['phrases']) }}
              >
                {state.aiBusy === 'fill' ? t('persona.busy') : t('persona.intent.infer')}
              </button>
            </div>
            <div className={css.personaField}>
              <span className={css.personaFieldLabel}>{t('persona.style.preset.label')}</span>
              <div className={css.personaChips}>
                {PERSONA_STYLE_PRESETS.map(preset => (
                  <button
                    key={preset}
                    type="button"
                    className={form.preset === preset ? css.personaChipOn : css.personaChip}
                    onClick={() => { controller.updateForm({ preset: form.preset === preset ? null : preset }) }}
                  >
                    {PERSONA_STYLE_PRESET_LABELS[preset]}
                  </button>
                ))}
              </div>
              {form.preset !== null && <p className={css.personaStyleSample}>{`${t('persona.style.samplePrefix')}${PERSONA_STYLE_SAMPLES[form.preset]}`}</p>}
            </div>
            <FieldRow label={t('persona.style.red.label')} hint={t('persona.style.red.hint')}>
              <div className={css.personaChips}>
                {PERSONA_RED_LINE_PRESETS.map(option => (
                  <button
                    key={option}
                    type="button"
                    className={redLineSelection.selected.includes(option) ? css.personaChipOn : css.personaChip}
                    onClick={() => { toggleRedLine(option) }}
                  >
                    {option}
                  </button>
                ))}
              </div>
              <textarea
                rows={2}
                value={redLineSelection.custom}
                placeholder={t('persona.intent.custom')}
                onChange={(event) => { changeRedLineCustom(event.currentTarget.value) }}
              />
            </FieldRow>
            <FieldRow label={t('persona.style.banned.label')}>
              <textarea
                rows={2}
                placeholder={t('persona.style.banned.placeholder')}
                value={form.bannedWordsText}
                onChange={(event) => { controller.updateForm({ bannedWordsText: event.currentTarget.value }) }}
              />
            </FieldRow>
            <DisclosureRow
              icon={<IconSparkle16 size={14} />}
              title={t('persona.style.advanced')}
              open={advancedOpen}
              expandable
              expandOnRowClick
              onToggle={() => { setAdvancedOpen(!advancedOpen) }}
            >
              <div className={css.personaAdvancedBody}>
                <FieldRow label={t('persona.style.custom.label')}>
                  <textarea
                    rows={2}
                    placeholder={t('persona.style.custom.placeholder')}
                    value={form.customText}
                    onChange={(event) => { controller.updateForm({ customText: event.currentTarget.value }) }}
                  />
                </FieldRow>
                <div className={css.personaField}>
                  <span className={css.personaFieldLabel}>{t('persona.style.strength.label')}</span>
                  <div className={css.personaChips}>
                    {(['light', 'strict'] as const).map(strength => (
                      <button
                        key={strength}
                        type="button"
                        className={form.strength === strength ? css.personaChipOn : css.personaChip}
                        onClick={() => { controller.updateForm({ strength }) }}
                      >
                        {t(strength === 'strict' ? 'persona.style.strict' : 'persona.style.light')}
                      </button>
                    ))}
                  </div>
                </div>
                <FieldRow label={PERSONA_FIELD_LABELS.phrases} hint={t('persona.field.phrases.hint')}>
                  <input value={form.fields.phrases.value} placeholder={t('persona.field.phrases.placeholder')} onChange={(event) => { setField('phrases')(event.currentTarget.value) }} />
                </FieldRow>
              </div>
            </DisclosureRow>
            <div className={css.personaPromptBox}>
              <div className={css.personaPromptHead}>
                <strong>{t('persona.prompt.preview')}</strong>
                <button
                  type="button"
                  className={css.personaMini}
                  onClick={() => { void writeClipboard(prompt) }}
                >
                  {t('persona.prompt.copy')}
                </button>
              </div>
              <pre className={css.personaPromptText}>{prompt}</pre>
            </div>
          </div>
        )}

        {state.fillPreview !== null && <FillPreviewPanel state={state} controller={controller} t={t} />}

        <div className={css.personaModalFoot}>
          {step > 1 && <button type="button" className={css.personaMini} onClick={() => { controller.setStep((step - 1) as 1 | 2 | 3) }}>{t('persona.prev')}</button>}
          {step < 4 && <button type="button" className={css.personaPrimary} onClick={() => { controller.setStep((step + 1) as 2 | 3 | 4) }}>{t('persona.next')}</button>}
          <button
            type="button"
            className={css.personaPrimary}
            disabled={state.saving}
            onClick={() => { void controller.saveWizard() }}
          >
            {state.saving ? t('persona.saving') : t('persona.save')}
          </button>
          {step === 4 && (
            <button
              type="button"
              className={css.personaMini}
              disabled={state.aiBusy !== false}
              title={t('persona.fill.hint')}
              onClick={() => { void controller.runFill() }}
            >
              {state.aiBusy === 'fill' ? t('persona.busy') : t('persona.fill.run')}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}

/** The AI fill preview: per-field textareas the user can adjust before adopting. */
function FillPreviewPanel(props: {
  state: PersonaState
  controller: PersonaController
  t: PropsLocale<'content-studio'>['t']
}) {
  const { state, controller, t } = props
  const preview = state.fillPreview
  const panelRef = useRef<HTMLDivElement | null>(null)
  // The panel lands below the step body; scrolling it into view makes the
  // "results live here" moment unmissable.
  useEffect(() => {
    // jsdom (tests) lacks scrollIntoView; guard instead of crashing the mount.
    if (typeof panelRef.current?.scrollIntoView === 'function') {
      panelRef.current.scrollIntoView({ block: 'nearest', behavior: 'smooth' })
    }
  }, [])
  if (preview === null) return null
  return (
    <div ref={panelRef} className={css.personaFill} role="status">
      <div className={css.personaFillHead}>
        <strong>{t('persona.fill.title')}</strong>
        <button type="button" className={css.personaMini} onClick={() => { controller.adoptAllFill() }}>
          {t('persona.fill.adoptAll')}
        </button>
        <button type="button" className={css.personaMini} onClick={() => { controller.discardFill() }}>
          {t('persona.fill.discard')}
        </button>
      </div>
      <p className={css.personaFieldHint}>{t('persona.fill.explain')}</p>
      {(Object.keys(preview.fields) as PersonaFieldKey[]).map(key => (
        <FillRow key={key} fieldKey={key} value={preview.fields[key] ?? ''} controller={controller} t={t} />
      ))}
    </div>
  )
}

/** One candidate row: editable in place, adopted with its edited text. */
function FillRow(props: {
  fieldKey: PersonaFieldKey
  value: string
  controller: PersonaController
  t: PropsLocale<'content-studio'>['t']
}) {
  const { fieldKey, value, controller, t } = props
  const [draft, setDraft] = useState(value)
  return (
    <div className={css.personaFillRow}>
      <span className={css.personaFieldLabel}>{PERSONA_FIELD_LABELS[fieldKey]}</span>
      <textarea rows={2} value={draft} onChange={(event) => { setDraft(event.currentTarget.value) }} />
      <button type="button" className={css.personaMini} onClick={() => { controller.adoptFillField(fieldKey, draft) }}>
        {t('persona.fill.adopt')}
      </button>
    </div>
  )
}

/** The report panel: generate, edit with the staleness banner, confirmed regeneration. */
function PersonaReportPanel(props: {
  entry: PersonaEntry
  controller: PersonaController
  t: PropsLocale<'content-studio'>['t']
}) {
  const { entry, controller, t } = props
  const report = entry.report
  const [draft, setDraft] = useState(report?.markdown ?? '')
  useEffect(() => { setDraft(report?.markdown ?? '') }, [report])
  const stale = report !== null && entry.revision > report.sourceRevision
  const generate = (): void => {
    if (report !== null && report.editedByUser && !window.confirm(t('persona.report.confirmRegen'))) return
    void controller.generateReport(entry.id)
  }
  return (
    <div className={css.personaModal} role="dialog" aria-modal="true" aria-label={t('persona.report.title')}>
      <div className={css.personaModalCard}>
        <div className={css.personaModalHead}>
          <h3>{`${t('persona.report.title')} · ${entry.name}`}</h3>
          <button type="button" className={css.personaMini} onClick={() => { controller.closeReport() }} aria-label={t('persona.report.close')}>
            {t('persona.report.close')}
          </button>
        </div>

        <NoticeBar notice={controller.getState().notice} noticeDetail={controller.getState().noticeDetail} controller={controller} t={t} />

        {report === null ? (
          <p className={css.personaEmpty}>{t('persona.report.empty')}</p>
        ) : (
          <>
            {stale && <div className={css.personaBanner} role="status">{t('persona.report.stale')}</div>}
            {report.editedByUser && <p className={css.personaReportEdited}>{t('persona.report.edited')}</p>}
            <textarea
              className={css.personaReportText}
              rows={14}
              value={draft}
              onChange={(event) => { setDraft(event.currentTarget.value) }}
            />
          </>
        )}
        <div className={css.personaModalFoot}>
          <button
            type="button"
            className={css.personaMini}
            disabled={controller.getState().aiBusy !== false || report === null || draft.trim().length === 0 || draft === report.markdown}
            onClick={() => { void controller.saveReportEdit(entry.id, draft) }}
          >
            {t('persona.report.edit.save')}
          </button>
          <button
            type="button"
            className={css.personaPrimary}
            disabled={controller.getState().aiBusy === 'report'}
            onClick={generate}
          >
            {controller.getState().aiBusy === 'report' ? t('persona.busy') : report === null ? t('persona.report.generate') : t('persona.report.regenerate')}
          </button>
        </div>
      </div>
    </div>
  )
}
