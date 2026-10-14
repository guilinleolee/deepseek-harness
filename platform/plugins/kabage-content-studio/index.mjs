/**
 * 卡巴格内容创作工作台（Content Studio）投放载体。
 *
 * 本体无宿主侧行为：全部内容是 cordis.patch.yml 的四行 insert
 * （content-outputs / content-schedule / content-topics / ui-content-studio，
 * 自 web-app bundle 收编为平台受管投放）。空 apply 仅为让包作为插件被
 * Loader 正常加载与生命周期管理，与 ui-content-studio 的纯 UI 插件形态一致。
 */

/** Host plugin body — no host-side behavior; the payload is the patch layer. */
export function apply() {}
