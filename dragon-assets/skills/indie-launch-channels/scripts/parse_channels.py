#!/usr/bin/env python3
"""
解析 1000UserGuide README.md 为结构化 JSON 数据库
"""

import re
import json
import urllib.request
import urllib.error

def fetch_readme():
    """获取 README.md 内容"""
    url = "https://raw.githubusercontent.com/naxiaoduo/1000UserGuide/main/README.md"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        print(f"获取失败: {e}")
        return None

def parse_channels(content):
    """解析 Markdown 内容为渠道列表"""
    channels = []
    current_category = None

    # 分类映射
    category_map = {
        "国内网站": "cn_website",
        "国内网址导航站": "cn_directory",
        "国内社区论坛": "cn_community",
        "海外网站": "overseas_website",
        "海外AI导航网站": "ai_directory",
        "海外目录站点": "overseas_directory",
        "海外社区": "overseas_community",
        "Reddit子版块": "reddit"
    }

    # 分类描述
    category_desc = {
        "cn_website": "国内网站渠道",
        "cn_directory": "国内网址导航站",
        "cn_community": "国内社区论坛",
        "overseas_website": "海外网站渠道",
        "ai_directory": "海外AI导航网站",
        "overseas_directory": "海外目录站点",
        "overseas_community": "海外社区",
        "reddit": "Reddit子版块"
    }

    lines = content.split('\n')

    for line in lines:
        line = line.strip()

        # 检测分类标题
        if line.startswith('#### ') or line.startswith('### '):
            header = line.replace('#### ', '').replace('### ', '').strip()
            for cat_name, cat_id in category_map.items():
                if cat_name in header:
                    current_category = cat_id
                    break
            continue

        # 解析渠道条目 - 格式: - [名称](URL) 描述 [链接文字](URL2)
        if line.startswith('- [') and '](' in line and current_category:
            # 提取名称和URL
            match = re.match(r'- \[([^\]]+)\]\(([^)]+)\)', line)
            if match:
                name = match.group(1).strip()
                url = match.group(2).strip()

                # 用 match.end() 精确定位URL闭括号后的位置
                # match.end() 指向 URL 闭括号 ')' 之后的位置
                pos = match.end()

                # 跳过空格
                rest = line[pos:].lstrip()

                # 如果接下来是 ')'（markdown链接的闭括号），跳过它
                if rest.startswith(')'):
                    rest = rest[1:].lstrip()

                # 提取描述：遇到下一个 '[' 链接或行尾为止
                desc = ""
                if rest:
                    # 找下一个 '[' 的位置（第二个链接的开始）
                    bracket_pos = rest.find('[')
                    if bracket_pos == -1:
                        # 没有第二个链接，描述到行尾
                        desc = rest
                    else:
                        # 描述在第一个 '[' 之前
                        desc = rest[:bracket_pos]

                    # 清理描述末尾的 markdown 残留（如尾部括号、空格）
                    desc = re.sub(r'\s*[\])].*$', '', desc).strip()

                channel = {
                    "name": name,
                    "url": url,
                    "category": current_category,
                    "category_cn": category_desc.get(current_category, ""),
                    "description": desc,
                    "source": "1000UserGuide"
                }
                channels.append(channel)

    return channels

def main():
    print("正在获取 1000UserGuide README.md...")
    content = fetch_readme()

    if not content:
        print("获取失败，退出")
        return

    print("正在解析渠道数据...")
    channels = parse_channels(content)

    print(f"共解析到 {len(channels)} 个渠道")

    # 统计各类别数量
    stats = {}
    for ch in channels:
        cat = ch['category']
        stats[cat] = stats.get(cat, 0) + 1

    print("\n各类别渠道数量:")
    for cat, count in sorted(stats.items()):
        print(f"  {cat}: {count}")

    # 生成 JSON
    output = {
        "source": "1000UserGuide",
        "total_count": len(channels),
        "categories": list(stats.keys()),
        "channels": channels
    }

    output_file = "C:/Users/li/.claude/skills/indie-launch-channels/data/channels.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n已保存到 {output_file}")

if __name__ == "__main__":
    main()
