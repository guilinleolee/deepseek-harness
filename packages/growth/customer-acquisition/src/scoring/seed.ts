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
  customerAcquisitionDomainSpec,
  icpProfileSchema,
  scoreTemplateSchema,
  type IcpProfile,
  type ScoreTemplate,
} from '../domain/spec.ts'

/** One industry's seed: a profile id/template id pair plus their records. */
interface IndustrySeed {
  icp: IcpProfile
  template: ScoreTemplate
}

/** Fixed seed ids (data contract §5): `seed-<套>-<类>`. */
export const SEED_IDS = {
  retailIcp: 'seed-retail-icp',
  retailScore: 'seed-retail-score',
  b2bTradeIcp: 'seed-b2b-trade-icp',
  b2bTradeScore: 'seed-b2b-trade-score',
  softwareIcp: 'seed-software-icp',
  softwareScore: 'seed-software-score',
} as const

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
      { id: 'business_fit', name: '业态匹配度', description: '客户业态（餐饮、美容、教培、零售等）与我方服务案例的成功率匹配', weight: 20 },
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
      { id: 'cooperation_willingness', name: '合作意愿', description: '客户主动咨询深度、响应速度与试点开放度', weight: 10 },
    ],
    SEED_IDS.softwareScore,
    '软件服务商打分模板',
  ),
]

/**
 * Seed the preset industry templates once, idempotently: a fixed seed id
 * that already exists is skipped untouched, so user edits survive every
 * restart.
 * @param domain - the opened customer-acquisition domain.
 * @returns resolution after every missing seed record is durable.
 */
export async function seedIndustryTemplates(domain: Domain<typeof customerAcquisitionDomainSpec>): Promise<void> {
  const profiles = domain.table('icp_profiles')
  const templates = domain.table('score_templates')
  for (const seed of INDUSTRY_SEEDS) {
    if (profiles.get(seed.icp.id) === undefined) {
      await profiles.put(seed.icp.id, seed.icp)
    }
    if (templates.get(seed.template.id) === undefined) {
      await templates.put(seed.template.id, seed.template)
    }
  }
}
