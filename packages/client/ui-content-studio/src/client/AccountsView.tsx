/**
 * The accounts view: the platform login manager (browser-session cards per
 * platform — log in with your own account, the session stays on this
 * machine) plus the creation-account selector that injects the active
 * account name into every copied instruction.
 */
import { IconTrashOutline16 } from '@deepseek-ai/dsh-client-ui-primitives'
import type { PropsLocale } from '@deepseek-ai/dsh-client-ui-slots'
import type { SocialPlatform } from '@deepseek-ai/dsh-content-outputs/types'
import { AccountSelect } from './AccountSelect.tsx'
import type { PersonaController } from './persona/persona-store.ts'
import css from './ContentStudio.module.css'

/** One card row of the login grid: display facts plus the capture binding. */
interface AccountPlatformCard {
  readonly id: string
  readonly label: string
  readonly backend: string
  /** The supported platform behind the card; null = manual-paste only. */
  readonly capture: SocialPlatform | null
}

/** Display order follows the product mockup; capture-backed cards stay interactive. */
const ACCOUNT_PLATFORM_CARDS: readonly AccountPlatformCard[] = [
  { id: 'xhs', label: '小红书', backend: 'xhs', capture: 'xhs' },
  { id: 'kuaishou', label: '快手', backend: 'kuaishou', capture: null },
  { id: 'channels', label: '微信视频号', backend: 'channels', capture: null },
  { id: 'zhihu', label: '知乎', backend: 'web', capture: null },
  { id: 'bili', label: 'B 站', backend: 'bili', capture: 'bili' },
  { id: 'douyin', label: '抖音', backend: 'douyin', capture: 'douyin' },
  { id: 'wechat', label: '微信公众号', backend: 'wechat-oa', capture: null },
]

/** Props: the personas controller (login/capture faces) plus the controlled account state and locale seat. */
export type AccountsViewProps = {
  personas: PersonaController
  account: string
  accounts: readonly string[]
  onSelect: (account: string) => void
  onAdd: (account: string) => void
  onRemove: (account: string) => void
} & PropsLocale<'content-studio'>

/**
 * Render the accounts page: the platform login card grid over the
 * social-capture faces, then the creation-account selector.
 * @param props - the personas controller, controlled account state, mutators, and the locale seat.
 * @returns the page element tree.
 */
export function AccountsView({ personas, account, accounts, onSelect, onAdd, onRemove, t }: AccountsViewProps) {
  const state = personas.getState()
  return (
    <div className={css.workbench}>
      <div className={css.accountsLoginHead}>
        <div>
          <h2 className={css.pageTitle}>{t('accounts.login.title')}</h2>
          <p className={css.helloSub}>{t('accounts.login.hint')}</p>
          <p className={css.accountsLoginRisk}>⚠️ {t('accounts.login.risk')}</p>
        </div>
        <button
          type="button"
          className={css.accountsRefresh}
          onClick={() => { void personas.refreshSocialStatuses() }}
        >
          {t('accounts.refresh')}
        </button>
      </div>

      <div className={css.accountsLoginGrid}>
        {ACCOUNT_PLATFORM_CARDS.map((card) => {
          const status = card.capture === null ? undefined : state.socialStatuses[card.capture]
          const supported = card.capture !== null
          const loggedIn = status?.hasSession === true
          const pending = state.socialLoginPending === card.capture
          const remaining = status === undefined ? null : Math.max(0, (state.socialDailyCap ?? 3) - status.captureCountToday)
          return (
            <div key={card.id} className={css.accountsLoginCard}>
              <div className={css.accountsLoginCardHead}>
                <span className={css.accountsLoginCardTitle}>{card.label}</span>
                <span className={loggedIn ? css.accountsLoginBadgeOn : css.accountsLoginBadge}>
                  {supported
                    ? (loggedIn ? t('accounts.badge.in') : t('accounts.badge.out'))
                    : t('accounts.badge.manual')}
                </span>
              </div>
              <div className={css.accountsLoginCardBody}>
                {loggedIn
                  ? (
                    <span className={css.accountsLoginAvatar}>{card.label.slice(0, 1)}</span>
                  )
                  : null}
                <span className={css.accountsLoginBackend}>{`${t('accounts.backend')}: ${card.backend}`}</span>
                {loggedIn && (
                  <span className={css.accountsLoginBackend}>{t('accounts.remaining', { n: remaining ?? 0 })}</span>
                )}
              </div>
              {supported ? (
                <div className={css.accountsLoginActions}>
                  {loggedIn ? (
                    <>
                      <button
                        type="button"
                        className={css.accountsLoginAction}
                        disabled={state.aiBusy !== false || state.socialLoginPending !== null}
                        onClick={() => { void personas.verifySocial(card.capture as SocialPlatform) }}
                      >
                        {t('accounts.verify')}
                      </button>
                      <button
                        type="button"
                        className={css.accountsLoginAction}
                        disabled={state.socialLoginPending !== null}
                        onClick={() => { void personas.forgetSocial(card.capture as SocialPlatform) }}
                      >
                        {t('accounts.forget')}
                      </button>
                    </>
                  ) : (
                    <button
                      type="button"
                      className={css.accountsLoginButton}
                      disabled={state.socialLoginPending !== null}
                      title={t('accounts.login.buttonTitle')}
                      onClick={() => { void personas.startSocialLogin(card.capture as SocialPlatform) }}
                    >
                      {pending ? t('persona.busy') : t('accounts.login.button')}
                    </button>
                  )}
                </div>
              ) : (
                <p className={css.accountsLoginManualHint}>{t('accounts.manualHint')}</p>
              )}
            </div>
          )
        })}
      </div>

      <h3 className={css.pageTitle}>{t('accounts.title')}</h3>
      <p className={css.helloSub}>{t('accounts.hint')}</p>
      <div className={css.accountsPane}>
        <AccountSelect
          account={account}
          accounts={accounts}
          onSelect={onSelect}
          onAdd={onAdd}
          t={t}
        />
        <div className={css.accountsList}>
          {accounts.map(name => (
            <div key={name} className={css.listRow}>
              <span className={css.listTitle}>
                {name}
                {name === account && <span className={css.accountActiveTag}>{t('account.active')}</span>}
              </span>
              {name !== '通用模式' && (
                <button
                  type="button"
                  className={css.calendarChipAction}
                  aria-label={t('accounts.delete')}
                  onClick={() => { onRemove(name) }}
                >
                  <IconTrashOutline16 size={12} />
                </button>
              )}
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
