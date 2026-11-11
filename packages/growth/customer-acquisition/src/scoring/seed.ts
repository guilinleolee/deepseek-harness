/**
 * The preset industry template seeds (data contract §5): three industries —
 * brick-and-mortar retail, B2B manufacturing/trade, and software services —
 * each with one ICP profile and one scoring prompt template. Seeding is
 * idempotent by fixed seed id: a record that exists (including one the user
 * has since edited) is never touched. SOP and copy templates belong to P3
 * and are not seeded here.
 * @module @deepseek-ai/dsh-customer-acquisition/scoring/seed
 */

import type { Domain } from '@deepseek-ai/dsh-storage-domain'
import {
  contentTemplateSchema,
  customerAcquisitionDomainSpec,
  icpProfileSchema,
  scoreTemplateSchema,
  sopTemplateSchema,
  type ContentTemplate,
  type IcpProfile,
  type ScoreTemplate,
} from '../domain/spec.ts'

/** One industry's seed: a profile id/template id pair plus their records. */
interface IndustrySeed {
  icp: IcpProfile
  template: ScoreTemplate
}

/** Fixed seed ids (data contract §5): `seed-<套>-<类>`. */
export const SEED_IDS = {  retailIcp: 'seed-retail-icp',
  retailScore: 'seed-retail-score',
  retailSop: 'seed-retail-sop',
  retailContentWecom: 'seed-retail-content-wecom',
  retailContentXhs: 'seed-retail-content-xhs',
  b2bTradeIcp: 'seed-b2b-trade-icp',
  b2bTradeScore: 'seed-b2b-trade-score',
  b2bTradeSop: 'seed-b2b-trade-sop',
  b2bTradeContentWecom: 'seed-b2b-trade-content-wecom',
  b2bTradeContentDrip: 'seed-b2b-trade-content-drip',
  softwareIcp: 'seed-software-icp',
  softwareScore: 'seed-software-score',
  softwareSop: 'seed-software-sop',
  softwareContentIntro: 'seed-software-content-intro',
  softwareContentDrip: 'seed-software-content-drip',
} as const

/** Boot-time timestamp for every seed record written in one process. */
const SEED_TIMESTAMP = Date.now()

/** The scoring template body shared by the seeds; the four placeholders are all provided. */
const SEED_PROMPT_TEXT = [
  '请对以下线索做客户匹配度评估打分。',
  'ICP 画像：{{icp_profile}}',
  '评分维度（权重合计 100）：',
  '{{dimensions}}',
  '线索资料：{{lead}}',
  '线索挂接的补充资料：{{knowledge}}',
  '请结合行业常识逐维度评分：每个维度给 0-100 的整数分和一句话理由，最后给整体理由。',
].join('\n')

function seedOf(
  icpId: string,
  icpName: string,
  industry: string,
  dimensions: { id: string; name: string; description: string; weight: number }[],
  templateId: string,
  templateName: string,
): IndustrySeed {
  const now = Date.now()
  return {
    icp: icpProfileSchema.parse({
      id: icpId,
      name: icpName,
      industry,
      dimensions,
      enabled: true,
      created_at: now,
      updated_at: now,
    }),
    template: scoreTemplateSchema.parse({
      id: templateId,
      name: templateName,
      industry,
      prompt_text: SEED_PROMPT_TEXT,
      enabled: true,
      created_at: now,
      updated_at: now,
    }),
  }
}

/** The three preset industry seeds, keyed for deterministic seeding order. */
const INDUSTRY_SEEDS: readonly IndustrySeed[] = [
  seedOf(
    SEED_IDS.retailIcp,
    '实体门店获客画像',
    '实体门店',
    [
      { id: 'budget_scale', name: '预算规模', description: '客户表达或暗示的投入预算与门店客单价、套餐档位的匹配程度', weight: 25 },
      { id: 'demand_urgency', name: '需求紧迫度', description: '客户当前经营痛点（客流下滑、新店开业、季节性推广）的紧迫程度', weight: 25 },
      { id: 'business_fit', name: '业态匹配度', description: '客户业态（餐饮、美容、教培、零售等）与我方服务能力的适配度', weight: 20 },
      { id: 'decision_role', name: '决策地位', description: '联系人在门店经营决策中的角色（店主本人、店长、运营负责人）', weight: 15 },
      { id: 'reachability', name: '触达可行性', description: '联系方式完整度与客户对电话/微信/到店沟通的接受度', weight: 15 },
    ],
    SEED_IDS.retailScore,
    '实体门店打分模板',
  ),
  seedOf(
    SEED_IDS.b2bTradeIcp,
    'B2B 工厂商贸获客画像',
    'B2B 工厂商贸',
    [
      { id: 'procurement_budget', name: '采购预算', description: '客户年采购额或单次采购预算与我方产品价位的匹配程度', weight: 25 },
      { id: 'demand_match', name: '需求匹配度', description: '客户采购需求（品类、规格、定制要求）与我方供应能力的匹配', weight: 25 },
      { id: 'company_scale', name: '企业规模', description: '客户企业人数、年产值所处档位及供应链稳定性', weight: 20 },
      { id: 'decision_chain', name: '决策链地位', description: '联系人在采购流程中的角色（老板、采购负责人、技术把关人）', weight: 15 },
      { id: 'repurchase_potential', name: '复购潜力', description: '客户采购频次、行业景气度带来的长期合作空间', weight: 15 },
    ],
    SEED_IDS.b2bTradeScore,
    'B2B 工厂商贸打分模板',
  ),
  seedOf(
    SEED_IDS.softwareIcp,
    '软件服务商获客画像',
    '软件服务商',
    [
      { id: 'tech_fit', name: '技术匹配度', description: '客户现有系统、数据形态与我方方案的技术栈兼容度', weight: 20 },
      { id: 'budget_scale', name: '预算规模', description: '客户信息化预算及付费意愿（SaaS 订阅或项目制）', weight: 20 },
      { id: 'demand_urgency', name: '需求紧迫度', description: '客户数字化痛点（效率、合规、增长）的紧迫程度', weight: 20 },
      { id: 'decision_role', name: '决策地位', description: '联系人在选型中的角色（CEO、CTO、业务负责人、采购）', weight: 15 },
      { id: 'growth_potential', name: '增长潜力', description: '客户业务增速、扩团队/扩产品线带来的用量增长空间', weight: 15 },
      { id: 'cooperation_willingness', name: '合作意愿', description: '客户主动咨询深度、响应速度与配合程度', weight: 10 },
    ],
    SEED_IDS.softwareScore,
    '软件服务商打分模板',
  ),
]

/** SOP follow-up rules for one industry, one per intent level (contract §3.9). */
const RETAIL_SOP = sopTemplateSchema.parse({
  id: SEED_IDS.retailSop,
  name: '实体门店跟进 SOP',
  industry: '实体门店',
  enabled: true,
  created_at: SEED_TIMESTAMP,
  updated_at: SEED_TIMESTAMP,
  rules: [
    {
      intent_level: 'high',
      cadence: 'D+0 微信问候并说明我能做什么，D+1 电话确认对方最想先解决的环节，D+3 发一份同行通用的做法说明并问反馈，D+7 复盘与方案报价',
      points: ['确认店主本人决策身份', '确认最想先解决的环节（线上咨询/到店接待/老客跟进）', '发一份做法说明并约一次沟通'],
      questions: ['店最近客流最大的时段是什么时候？', '之前做过哪些推广？效果如何？', '这次推广最想解决什么问题？'],
      risks: ['店主临时改时间需当天再次确认', '不要承诺效果数字，也不要编造同行案例', '纯线上卖家没有门店，沟通方式按线上走'],
    },
    {
      intent_level: 'mid',
      cadence: 'D+0 微信说明我能做什么，D+2 询问反馈并邀约，D+5 保持朋友圈互动',
      points: ['先给价值再邀约', '记录门店当前客流数据'],
      questions: ['店里现在主推什么产品或套餐？', '目标客群是周边居民还是游客？'],
      risks: ['联系人是店长时推进节奏放慢，留微信长期培育'],
    },
    {
      intent_level: 'low',
      cadence: 'D+0 发送资料后每两周朋友圈触达一次',
      points: ['不强推，以内容种草为主'],
      questions: [],
      risks: ['避免频繁打扰导致删除'],
    },
    {
      intent_level: 'invalid',
      cadence: '不主动跟进，仅朋友圈可见',
      points: ['归档并标注原因'],
      questions: [],
      risks: ['核实是否误判，避免错失'],
    },
  ],
})

const B2B_TRADE_SOP = sopTemplateSchema.parse({
  id: SEED_IDS.b2bTradeSop,
  name: 'B2B 工厂商贸跟进 SOP',
  industry: 'B2B 工厂商贸',
  enabled: true,
  created_at: SEED_TIMESTAMP,
  updated_at: SEED_TIMESTAMP,
  rules: [
    {
      intent_level: 'high',
      cadence: 'D+0 发送产品册与报价框架，D+1 电话确认需求细节，D+3 寄样（如需实物）或约线上会议，D+7 商务条款洽谈',
      points: ['摸清采购流程与决策链', '确认规格参数与交期', '推动寄样/验厂'],
      questions: ['这次采购是谁最终拍板？', '现有供应商的主要不满是什么？', '交期与付款方式的要求？'],
      risks: ['技术把关人提出参数质疑时拉技术支持介入', '客户压价时用交期与服务换价格'],
    },
    {
      intent_level: 'mid',
      cadence: 'D+0 发送选型资料，D+3 电话回访，D+10 报送行业行情保持联系',
      points: ['进入供应商备选名单', '记录采购时间窗'],
      questions: ['目前的采购周期是按季度还是按单？'],
      risks: ['仅在比价阶段被利用时控制投入深度'],
    },
    {
      intent_level: 'low',
      cadence: 'D+0 资料送达后每月行情简报触达',
      points: ['维持供应商名录在册'],
      questions: [],
      risks: ['采购窗口未到前避免过度推销'],
    },
    {
      intent_level: 'invalid',
      cadence: '不跟进',
      points: ['归档标注'],
      questions: [],
      risks: [],
    },
  ],
})

const SOFTWARE_SOP = sopTemplateSchema.parse({
  id: SEED_IDS.softwareSop,
  name: '软件服务商跟进 SOP',
  industry: '软件服务商',
  enabled: true,
  created_at: SEED_TIMESTAMP,
  updated_at: SEED_TIMESTAMP,
  rules: [
    {
      intent_level: 'high',
      cadence: 'D+0 发送方案概要与预约演示，D+1 确认参会人，D+3 产品演示，D+5 试点方案（周期按客户实际情况谈定），D+10 商务洽谈',
      points: ['锁定演示参会人与成功标准', '准备客户数据形态的演示环境', '商定试点范围与周期（不预设固定天数）'],
      questions: ['现在的工单/数据流跑在哪个系统？', '试点成功的衡量标准是什么？', '预算走 CapEx 还是 OpEx？'],
      risks: ['CTO 提出安全合规问题时带上等保材料', '多方比稿时强调实施周期承诺'],
    },
    {
      intent_level: 'mid',
      cadence: 'D+0 发送做法说明，D+3 邀请 webinar，D+7 跟进互动反馈',
      points: ['争取技术负责人加微', '沉淀客户痛点清单'],
      questions: ['今年数字化的优先级排序？'],
      risks: ['仅停留在资料层面时主动提供诊断报告推进'],
    },
    {
      intent_level: 'low',
      cadence: 'D+0 加入产品通讯，每月产品更新触达',
      points: ['内容培育为主'],
      questions: [],
      risks: [],
    },
    {
      intent_level: 'invalid',
      cadence: '不跟进',
      points: ['归档标注'],
      questions: [],
      risks: [],
    },
  ],
})

/** Nurture-copy seeds for one industry: two templates covering the main channels. */
function contentTemplatesOf(
  industry: string,
  entries: { id: string; name: string; type: string; body: string; variables: { name: string; description: string; example?: string }[] }[],
): ContentTemplate[] {
  return entries.map(entry => contentTemplateSchema.parse({
    id: entry.id,
    name: entry.name,
    industry,
    type: entry.type,
    body: entry.body,
    variables: entry.variables,
    enabled: true,
    created_at: SEED_TIMESTAMP,
    updated_at: SEED_TIMESTAMP,
  }))
}

const CONTACT_VARIABLES = [
  { name: 'contact_name', description: '联系人称呼', example: '王老板' },
  { name: 'company_name', description: '客户公司或门店名', example: '幸福奶茶店' },
  { name: 'sender_name', description: '我方发送人署名', example: '李明' },
]

const RETAIL_CONTENT = contentTemplatesOf('实体门店', [
  {
    id: SEED_IDS.retailContentWecom,
    name: '实体门店企微初次触达',
    type: 'wecom_first_touch',
    body: '{{contact_name}}您好，我是{{sender_name}}，专注帮{{industry}}门店做本地客流增长。{{industry}}门店常见的几个卡点——顾客在美团问了没人回、到店高峰漏消息、老客没人跟进——我们做的是把这些环节的咨询响应和线索承接接住。您店里目前最想先解决哪个环节？我可以针对性发您一份同行都在用的做法说明。',
    variables: [
      ...CONTACT_VARIABLES,
      { name: 'industry', description: '客户业态', example: '奶茶' },
    ],
  },
  {
    id: SEED_IDS.retailContentXhs,
    name: '实体门店小红书图文脚本',
    type: 'xiaohongshu_post',
    body: '标题：{{industry}}店老板必看｜3 个让{{company_name}}式小店少漏顾客的笨办法\n正文：很多{{industry}}老板以为引流要花大钱，其实先把这三件事做对：\n1. 门口 3 米的"黄金视线"每天换一次陈列；\n2. 顾客拍照点固定打灯；\n3. 付款前加一句"加微信下次立减"。\n这三件事不需要额外预算，先把现有顾客接住，比再拉一批新客更划算。\n你是哪个城市的{{industry}}老板？评论区聊聊你的客流难题～\n标签：#{{industry}} #实体店引流 #门店运营',
    variables: [
      ...CONTACT_VARIABLES,
      { name: 'industry', description: '客户业态', example: '美甲' },
    ],
  },
])

const B2B_TRADE_CONTENT = contentTemplatesOf('B2B 工厂商贸', [
  {
    id: SEED_IDS.b2bTradeContentWecom,
    name: 'B2B 企微初次触达',
    type: 'wecom_first_touch',
    body: '{{contact_name}}经理您好，我是{{sender_name}}。看到{{company_name}}在{{industry}}方向的采购需求，我们给同规模工厂供过类似方案（可发案例与检测报告）。不知您这边现有多家供应商在比价，还是已有定点？我可以先发一份选型对比表供您内部参考。',
    variables: [
      ...CONTACT_VARIABLES,
      { name: 'industry', description: '客户所处行业', example: '汽配' },
    ],
  },
  {
    id: SEED_IDS.b2bTradeContentDrip,
    name: 'B2B 三轮邮件培育序列',
    type: 'email_drip',
    body: '## 第 1 轮\n主题：{{company_name}}选型参考｜{{industry}}行业采购对比表\n{{contact_name}}您好，附上{{industry}}行业常用选型对比表，含规格、交期与付款方式三栏，供您内部评估使用。有任何参数问题直接回复本邮件。\n\n## 第 2 轮\n主题：回复：交期与产能怎么排\n{{contact_name}}您好，上周邮件发出后不少客户问到交期。同规模的采购通常需要提前确认产能档期与首批到货时间，具体周期要看规格和起订量。贵司理想的到货时间是什么时候？我可按此倒排生产计划。\n\n## 第 3 轮\n主题：是否需要寄样？\n{{contact_name}}您好，样板间已备好贵司关注规格的样品，顺丰到付寄出，收货后不满意无需任何费用。回复收件信息即可。',
    variables: [
      ...CONTACT_VARIABLES,
      { name: 'industry', description: '客户所处行业', example: '机械制造' },
    ],
  },
])

const SOFTWARE_CONTENT = contentTemplatesOf('软件服务商', [
  {
    id: SEED_IDS.softwareContentIntro,
    name: '软件服务商官网产品介绍',
    type: 'website_product_intro',
    body: '{{company_name}}数字化增长方案\n\n为{{industry}}团队打造的一体化工作台：把散落在表格、群聊和邮件里的业务流收进一个系统。\n\n核心能力：\n- 全渠道接入：客服、销售、交付一个工作台闭环；\n- 数据看板：老板视角的实时经营指标；\n- 开放集成：与现有系统通过 API 无缝打通。\n\n{{contact_name}}关注的技术兼容性我们提供免费评估，具体上线周期与贵司的数据量、集成范围和内部配合节奏相关，可以在需求沟通后给出排期。立即预约演示，获取同行业实施案例包。',
    variables: [
      { name: 'company_name', description: '客户公司名', example: '北京云维科技' },
      { name: 'contact_name', description: '联系人称呼', example: '张总监' },
      { name: 'industry', description: '客户所处行业', example: 'IT 服务' },
    ],
  },
  {
    id: SEED_IDS.softwareContentDrip,
    name: '软件服务商三轮邮件培育序列',
    type: 'email_drip',
    body: '## 第 1 轮\n主题：{{company_name}}的效率诊断：三个最常见的流失点\n{{contact_name}}您好，服务同规模{{industry}}团队时我们几乎都看到同样的三个流失点：需求口头传达、进度靠问、数据滞后。这份自查清单帮您 10 分钟定位问题环节。\n\n## 第 2 轮\n主题：实施路径：看板替代周报怎么落地\n{{contact_name}}您好，上一封清单里若您勾选了"进度靠问"，这篇正对应：把周报换成看板、交付节点固定到人，这套落地路径图我整理了一份，附实施步骤与需要提前准备的字段。\n\n## 第 3 轮\n主题：免费试点名额申请\n{{contact_name}}您好，本期面向{{industry}}团队开放免费试点名额（含数据迁移协助）。回复"试点"即可锁位，或直接回复您最想解决的场景。',
    variables: [
      { name: 'company_name', description: '客户公司名', example: '北京云维科技' },
      { name: 'contact_name', description: '联系人称呼', example: '张总监' },
      { name: 'industry', description: '客户所处行业', example: 'IT 服务' },
    ],
  },
])

/**
 * Seed the preset industry templates once, idempotently: a fixed seed id
 * that already exists is skipped untouched, so user edits survive every
 * restart. Each industry carries its ICP profile, scoring prompt template,
 * follow-up SOP, and nurture-copy templates (data contract §5).
 * @param domain - the opened customer-acquisition domain.
 * @returns resolution after every missing seed record is durable.
 */
export async function seedIndustryTemplates(domain: Domain<typeof customerAcquisitionDomainSpec>): Promise<void> {
  const profiles = domain.table('icp_profiles')
  const templates = domain.table('score_templates')
  const sopTemplates = domain.table('sop_templates')
  const contentTemplates = domain.table('content_templates')
  for (const seed of INDUSTRY_SEEDS) {
    if (profiles.get(seed.icp.id) === undefined) {
      await profiles.put(seed.icp.id, seed.icp)
    }
    if (templates.get(seed.template.id) === undefined) {
      await templates.put(seed.template.id, seed.template)
    }
  }
  for (const sop of [RETAIL_SOP, B2B_TRADE_SOP, SOFTWARE_SOP]) {
    if (sopTemplates.get(sop.id) === undefined) {
      await sopTemplates.put(sop.id, sop)
    }
  }
  for (const template of [...RETAIL_CONTENT, ...B2B_TRADE_CONTENT, ...SOFTWARE_CONTENT]) {
    if (contentTemplates.get(template.id) === undefined) {
      await contentTemplates.put(template.id, template)
    }
  }
}
