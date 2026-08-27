"""
阶段 42 验证脚本·验证 skill-updater INTEGRATED_SKILLS 集成版识别。
"""
import sys
sys.path.insert(0, 'scripts')
from autofill_source import _is_integrated_skill, INTEGRATED_SKILLS

print('INTEGRATED_SKILLS 列表:')
for s in sorted(INTEGRATED_SKILLS):
    marker = ' <- 阶段 42 NEW' if s == 'dsh-computer-use' else ''
    print(f'  - {s}{marker}')
print()

print('阶段 42 验证(_is_integrated_skill 命中):')
test_names = ['dsh-computer-use', 'dsh-computer-use-bridge', 'computer-use', 'random-other-skill']
for n in test_names:
    hit = _is_integrated_skill(n)
    symbol = '[HIT]' if hit else '[MISS]'
    print(f'  {symbol} {n}')

print()
print('汇总:')
print(f'  - 集成版总数: {len(INTEGRATED_SKILLS)}')
print(f'  - 阶段 42 新增: dsh-computer-use')
print(f'  - 命中测试: dsh-computer-use = {_is_integrated_skill("dsh-computer-use")}')
print(f'  - 命中测试: dsh-computer-use-bridge = {_is_integrated_skill("dsh-computer-use-bridge")}')