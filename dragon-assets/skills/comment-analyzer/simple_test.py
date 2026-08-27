#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简单测试 - 验证SKILL基础功能
"""

# 测试情感词典加载
def test_sentiment_dict():
    print("测试情感词典...")
    from pathlib import Path

    dict_path = Path("data/sentiment_dict.txt")
    if dict_path.exists():
        with open(dict_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # 过滤掉注释和空行
            words = [l.strip().split()[0] for l in lines if l.strip() and not l.startswith('#') and len(l.split()) >= 2]
            print(f"✅ 情感词典加载成功：{len(words)}个词条")
            return True
    else:
        print("❌ 情感词典文件不存在")
        return False


# 测试停用词加载
def test_stop_words():
    print("\n测试停用词表...")
    from pathlib import Path

    stop_path = Path("data/stop_words.txt")
    if stop_path.exists():
        with open(stop_path, 'r', encoding='utf-8') as f:
            words = [l.strip() for l in f if l.strip() and not l.startswith('#')]
            print(f"✅ 停用词表加载成功：{len(words)}个词条")
            return True
    else:
        print("❌ 停用词表文件不存在")
        return False


# 测试配置文件
def test_config():
    print("\n测试配置文件...")
    import json
    from pathlib import Path

    config_path = Path("config/comment-analyzer.json")
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            print(f"✅ 配置文件加载成功")
            print(f"   - 抓取模式：{config.get('scraper', {}).get('mode', 'N/A')}")
            print(f"   - 最大评论数：{config.get('analysis', {}).get('max_comments', 'N/A')}")
            return True
    else:
        print("❌ 配置文件不存在")
        return False


# 测试平台规则
def test_platform_rules():
    print("\n测试平台规则...")
    import json
    from pathlib import Path

    rules_path = Path("config/platform_rules.json")
    if rules_path.exists():
        with open(rules_path, 'r', encoding='utf-8') as f:
            rules = json.load(f)
            print(f"✅ 平台规则加载成功：{len(rules)}个平台")
            for platform, info in rules.items():
                api_intercept = "API拦截" if info.get('use_api_intercept') else "DOM选择器"
                print(f"   - {info['name']}：{api_intercept}")
            return True
    else:
        print("❌ 平台规则文件不存在")
        return False


# 测试SKILL文件
def test_skill_file():
    print("\n测试SKILL文件...")
    from pathlib import Path

    skill_path = Path("SKILL.md")
    if skill_path.exists():
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()
            if "comment-analyzer" in content:
                print(f"✅ SKILL.md文件存在且包含正确内容")
                return True
            else:
                print("❌ SKILL.md内容不完整")
                return False
    else:
        print("❌ SKILL.md文件不存在")
        return False


# 测试命令文件
def test_command_file():
    print("\n测试Slash命令文件...")
    from pathlib import Path

    # 检查全局commands目录
    command_path = Path("../commands/评论分析.md")
    if command_path.exists():
        print(f"✅ Slash命令文件存在：{command_path}")
        return True
    else:
        print(f"❌ Slash命令文件不存在：{command_path}")
        return False


if __name__ == "__main__":
    print("="*60)
    print("🧪 评论分析SKILL - 基础功能测试")
    print("="*60 + "\n")

    results = []
    results.append(test_sentiment_dict())
    results.append(test_stop_words())
    results.append(test_config())
    results.append(test_platform_rules())
    results.append(test_skill_file())
    results.append(test_command_file())

    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"测试结果：{passed}/{total} 通过")
    print("="*60)

    if passed == total:
        print("\n🎉 所有测试通过！SKILL基础功能正常。")
    else:
        print(f"\n⚠️  有{total-passed}项测试失败，请检查相关文件。")
