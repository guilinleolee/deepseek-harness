/**
 * The sentiment lexicon evaluation gate: a fixed labeled dataset runs through
 * `classifyByLexicon` and the polarity accuracy must stay at or above the
 * baseline. This is a regression gate over the lexicon itself — it pins the
 * current quality so lexicon edits that drop accuracy fail CI, not users
 * (the Harken `evaluate` pattern). Real-world accuracy beyond this dataset
 * is what the LLM review stage is for.
 */
import { describe, expect, it } from 'vitest'
import { classifyByLexicon } from '../src/sentiment/scan.ts'

interface EvalRow {
  readonly text: string
  readonly label: 'pos' | 'neu' | 'neg'
}

/** Fixed labeled dataset: every row's polarity is grounded in the lexicon terms it contains. */
const DATASET: readonly EvalRow[] = [
  { text: '用了一周来好评，推荐大家购买，性价比很高', label: 'pos' },
  { text: '客服态度很好，值得信赖的品牌', label: 'pos' },
  { text: '这次升级真是惊喜，产品有突破', label: 'pos' },
  { text: '新品发布获得业界认可，销量领先', label: 'pos' },
  { text: '持续回购五年，优秀的产品', label: 'pos' },
  { text: '质量和口碑都是行业标杆，获得冠军', label: 'pos' },
  { text: '大量用户投诉售后推诿，要求退款', label: 'neg' },
  { text: '被曝光虚假宣传，遭监管部门处罚', label: 'neg' },
  { text: '产品出现故障，用户纷纷差评', label: 'neg' },
  { text: '公司陷入诉讼，面临巨额罚款', label: 'neg' },
  { text: '多个批次产品宣布召回', label: 'neg' },
  { text: '消费者怒斥劣质原料，直言失望', label: 'neg' },
  { text: '今日发布会介绍了新品的配置', label: 'neu' },
  { text: '该公司发布公告，说明经营情况', label: 'neu' },
  { text: '新品将于下周开售，价格未公布', label: 'neu' },
  { text: '行业报告统计了年度出货量', label: 'neu' },
  { text: '官方渠道可以查询订单状态', label: 'neu' },
  { text: '评测文章对比了两款机型的参数', label: 'neu' },
  { text: '用户一边吐槽一边点赞，评价两极', label: 'neu' },
  { text: '有网友吐槽包装，也有用户点赞设计', label: 'neu' },
]

/** The gate: lexicon polarity accuracy on the dataset must stay at or above this. */
export const SENTIMENT_EVAL_BASELINE = 0.85

describe('sentiment lexicon evaluation gate', () => {
  it('keeps polarity accuracy at or above the baseline on the fixed dataset', () => {
    let correct = 0
    const misses: string[] = []
    for (const row of DATASET) {
      const verdict = classifyByLexicon(row.text)
      if (verdict.polarity === row.label) correct += 1
      else misses.push(`${verdict.polarity}≠${row.label}: ${row.text}`)
    }
    const accuracy = correct / DATASET.length
    expect(misses, `accuracy ${(accuracy * 100).toFixed(0)}%`).toEqual([])
    expect(accuracy).toBeGreaterThanOrEqual(SENTIMENT_EVAL_BASELINE)
  })
})
