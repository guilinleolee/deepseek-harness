#!/usr/bin/env python3
"""Wiki知识复利仪表盘"""

import sys
from pathlib import Path

# 添加compound_calculator到路径
sys.path.insert(0, str(Path(__file__).parent))

from compound_calculator import dashboard, get_top_notes, get_level

def main():
    print("\n" + "=" * 80)
    print("  📊  Wiki 知识复利引擎  |  Karpathy LLM Wiki Pattern V2")
    print("=" * 80 + "\n")

    dashboard()

    print("\n💡 复利公式: value(N) = initial × (1 + links × 0.1)^N × memory_resonance")
    print("📚 查看帮助: python3 compound_calculator.py --help")

if __name__ == "__main__":
    main()
