import { describe, expect, it } from 'vitest'
import { parseCreateCoverPlan, parseCreateStoryboard } from '../src/create/storyboard.ts'

const STORYBOARD = [
  '## 镜头 1 · 开场钩子（3s）',
  '画面：手机屏幕亮起，桌面前景虚化，特写，冷白光',
  '台词：这条视频只讲一个反常识的事。',
  '时长：3',
  '',
  '## 镜头 2 · 抛出冲突（8s）',
  '画面：手写白板，三分之一构图，暖光',
  '台词：大部分人以为效率工具越用越多越好。',
  '时长：8',
  '',
  '## 镜头 3 · 给出方案（12s）',
  '画面：桌面全景，三分法构图，自然光',
  '台词：真正拉开差距的是你敢不敢删掉一半。',
  '时长：12',
].join('\n')

describe('parseCreateStoryboard', () => {
  it('reads every shot in document order with its label, brief, line, and duration', () => {
    const shots = parseCreateStoryboard(STORYBOARD)
    expect(shots).toHaveLength(3)
    expect(shots[0]).toEqual({
      index: 1,
      label: '开场钩子',
      visual: '手机屏幕亮起，桌面前景虚化，特写，冷白光',
      line: '这条视频只讲一个反常识的事。',
      seconds: 3,
    })
    expect(shots[1]?.label).toBe('抛出冲突')
    expect(shots[1]?.seconds).toBe(8)
    expect(shots[2]?.index).toBe(3)
    expect(shots[2]?.seconds).toBe(12)
  })

  it('falls back to the heading duration when the body states none', () => {
    const shots = parseCreateStoryboard('## 镜头 4 · 结尾引导（6s）\n画面：特写\n台词：关注我，下期讲第二个。')
    expect(shots[0]?.seconds).toBe(6)
    expect(shots[0]?.label).toBe('结尾引导')
  })

  it('reads a shot from its 画面 line when the heading carries no 镜头 marker', () => {
    const shots = parseCreateStoryboard('## 第二段\n画面：俯拍书桌\n台词：先说结论。')
    expect(shots).toHaveLength(1)
    expect(shots[0]?.visual).toBe('俯拍书桌')
    expect(shots[0]?.line).toBe('先说结论。')
    expect(shots[0]?.seconds).toBeNull()
    expect(shots[0]?.label).toBe('')
  })

  it('reads the alternative field labels a model may use', () => {
    const shots = parseCreateStoryboard('## 镜头 1\n画面提示：近景\n旁白：开场白\n时长：5 秒')
    expect(shots[0]?.visual).toBe('近景')
    expect(shots[0]?.line).toBe('开场白')
    expect(shots[0]?.seconds).toBe(5)
  })

  it('returns no shots for a document without shot structure', () => {
    expect(parseCreateStoryboard('# 标题\n\n一段普通的正文。')).toEqual([])
    expect(parseCreateStoryboard('')).toEqual([])
  })

  it('keeps a shot whose fields are all missing rather than dropping it', () => {
    const shots = parseCreateStoryboard('## 镜头 1\n## 镜头 2')
    expect(shots).toHaveLength(2)
    expect(shots[0]?.visual).toBe('')
    expect(shots[0]?.line).toBe('')
    expect(shots[0]?.seconds).toBeNull()
  })
})

const COVER = [
  '## 封面方案',
  '主标题：删掉一半效率工具',
  '副标题：真正拉开差距的是取舍',
  '构图：人物居左，右侧留白放标题，中近景',
  '配色：深蓝主色，暖橙辅色',
  '画面风格：干净的桌面俯拍，极简',
].join('\n')

describe('parseCreateCoverPlan', () => {
  it('reads every field of the cover plan', () => {
    expect(parseCreateCoverPlan(COVER)).toEqual({
      title: '删掉一半效率工具',
      subtitle: '真正拉开差距的是取舍',
      composition: '人物居左，右侧留白放标题，中近景',
      palette: '深蓝主色，暖橙辅色',
      style: '干净的桌面俯拍，极简',
    })
  })

  it('falls back to the heading when the plan states no main title', () => {
    const plan = parseCreateCoverPlan('## 封面方案\n副标题：只有副标题')
    expect(plan.title).toBe('封面方案')
    expect(plan.subtitle).toBe('只有副标题')
  })

  it('reads the empty fields of a partial plan without failing', () => {
    const plan = parseCreateCoverPlan('## 封面方案\n主标题：只有标题')
    expect(plan.title).toBe('只有标题')
    expect(plan.subtitle).toBe('')
    expect(plan.composition).toBe('')
    expect(plan.palette).toBe('')
    expect(plan.style).toBe('')
  })

  it('returns empty fields for a document with no cover structure', () => {
    expect(parseCreateCoverPlan('一段普通正文')).toEqual({
      title: '', subtitle: '', composition: '', palette: '', style: '',
    })
  })
})
