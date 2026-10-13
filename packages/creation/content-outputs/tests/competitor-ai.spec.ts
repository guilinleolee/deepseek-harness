import { describe, expect, it } from 'vitest'
import { parseCompetitorAnalysisOutput, parseCompetitorReportOutput } from '../src/competitor/ai.ts'

const VALID_JSON = JSON.stringify({
  hookType: '痛点钩子：开头直击职场人时间焦虑',
  structure: '痛点引入 → 案例展示 → 方法清单 → 行动引导',
  painPoints: ['没时间做内容'],
  topics: ['效率工具'],
  risks: ['同类选题扎堆'],
  reusable: ['清单式结构'],
  migrationTopics: ['给小团队的工具组合'],
  commentInsight: '高赞评论集中在求模板',
})

describe('parseCompetitorAnalysisOutput', () => {
  it('parses a clean JSON object', () => {
    const result = parseCompetitorAnalysisOutput(VALID_JSON)
    expect(result.hookType).toContain('痛点')
    expect(result.commentInsight).toBe('高赞评论集中在求模板')
    expect(result.painPoints).toEqual(['没时间做内容'])
  })

  it('parses fenced output and extracts the object', () => {
    const result = parseCompetitorAnalysisOutput(`\`\`\`json\n${VALID_JSON}\n\`\`\``)
    expect(result.structure).toContain('方法清单')
  })

  it('defaults a missing comment insight to unavailable', () => {
    const withoutComments = parseCompetitorAnalysisOutput(JSON.stringify({ ...JSON.parse(VALID_JSON), commentInsight: undefined }))
    expect(withoutComments.commentInsight).toBe('unavailable')
  })

  it('rejects output without a JSON object', () => {
    expect(() => parseCompetitorAnalysisOutput('没有 JSON')).toThrow(/no JSON object/)
  })

  it('rejects invalid JSON and missing core fields', () => {
    expect(() => parseCompetitorAnalysisOutput('{broken}')).toThrow(/not valid JSON/)
    expect(() => parseCompetitorAnalysisOutput('{"structure":"x"}')).toThrow(/hookType/)
    expect(() => parseCompetitorAnalysisOutput(JSON.stringify({ ...JSON.parse(VALID_JSON), painPoints: 'not-an-array' }))).toThrow(/invalid string array/)
  })
})

describe('parseCompetitorReportOutput', () => {
  it('returns trimmed markdown', () => {
    expect(parseCompetitorReportOutput('  # 报告\n正文  ')).toEqual({ markdown: '# 报告\n正文' })
  })

  it('rejects empty reports', () => {
    expect(() => parseCompetitorReportOutput('   ')).toThrow(/empty/)
  })
})
