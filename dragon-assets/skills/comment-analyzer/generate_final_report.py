#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博评论分析 - 使用从页面提取的评论数据
生成完整的分析报告
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter

# 从页面手动提取的评论数据（包含完整的时间和点赞信息）
WEIBO_COMMENTS = [
    {"id": "1", "content": "@奥卡姆剃刀 黄皮马瓦里，皈依者狂热！在阿拉伯人眼里不如狗", "author": "168张庸", "publish_time": "26-1-14 13:32", "likes": 1},
    {"id": "2", "content": "牌子涉嫌歧视回族歧视回族同胞不对的", "author": "啪的一声空中绽放", "publish_time": "26-1-14 11:56", "likes": 0},
    {"id": "3", "content": "极端宗教。恶心", "author": "哈基咪love", "publish_time": "26-1-14 11:43", "likes": 0},
    {"id": "4", "content": "黄皮马瓦里，皈依者狂热！在阿拉伯人眼里不如狗", "author": "一只大迷糊兔", "publish_time": "26-1-14 10:27", "likes": 0},
    {"id": "5", "content": " //@东海苍狼2020:这个其实就是一种宣示，这块地盘是我们的", "author": "东方不亮西方亮来生还作华夏人", "publish_time": "26-1-14 08:27", "likes": 0},
    {"id": "6", "content": "直接送加沙去，那里我们绝对不去", "author": "ladeng乐园", "publish_time": "26-1-13 20:23", "likes": 40},
    {"id": "7", "content": "汉族在自己打下的土地上成了个二等公民，处处忍让，让外国人让少数民族，让出个处处被人区别对待。这么牛直接写不接待汉族人啊，看回民的人数够不够她经营下去。", "author": "思念的回响", "publish_time": "26-1-14 09:26", "likes": 0},
    {"id": "8", "content": "没人管了吗？当地政府干什么吃的，要反了天了", "author": "用户7972426632", "publish_time": "26-1-13 20:31", "likes": 1},
    {"id": "9", "content": "那是💩，别去吃", "author": "李小咪公公", "publish_time": "26-1-13 19:59", "likes": 1},
    {"id": "10", "content": "恐怖分子滚出中国！", "author": "漠北-大馋鱼", "publish_time": "26-1-13 22:10", "likes": 3},
    {"id": "11", "content": "这种牌子是谁想出来的？搞小团体，破坏民族团结，其心可诛", "author": "小狐狸乘风破浪", "publish_time": "26-1-14 14:28", "likes": 1},
    {"id": "12", "content": "转发微博", "author": "urnot叶子在唱歌", "publish_time": "26-1-13 19:16", "likes": 0},
    {"id": "13", "content": " //@伊人飘香1212:恐怖分子，可怕😱😱😱", "author": "时空里的思维", "publish_time": "26-1-13 21:01", "likes": 1},
    {"id": "14", "content": "猪狗不如的教派还嫌弃起猪来了", "author": "讲故事的宋老师", "publish_time": "26-1-13 21:02", "likes": 2},
    {"id": "15", "content": "妈的简笔", "author": "阿狸啊嘿嘿嘿", "publish_time": "26-1-13 22:19", "likes": 0},
    {"id": "16", "content": "这种事情需要严打", "author": "羌笛声声慢", "publish_time": "26-1-14 07:31", "likes": 1},
    {"id": "17", "content": " //@冥王星1974:隔离、立威、寄生壮大、断桥、分裂。塔国也曾经全国只有7座礼拜寺6座教堂，几乎没有信教的，后来独立后就受到国外各种势力影响，礼拜寺有了5000座，教堂和各种教派有了几百个，注册的都有68种，国家就很难治理了，发展也一度中断。", "author": "东方不亮西方亮来生还作华夏人", "publish_time": "26-1-14 08:27", "likes": 0},
    {"id": "18", "content": "转发微博", "author": "金点子谭", "publish_time": "26-1-14 09:00", "likes": 0},
    # 从之前的数据中添加更多评论
    {"id": "19", "content": "还带个头套，那么喜欢吕教咋不去伊朗阿富汗呢！别在中国呆着。", "author": "春天终将来临2020", "publish_time": "26-1-13 18:39", "likes": 1182},
    {"id": "20", "content": "这种极端服饰、极端行动居然没有人抓", "author": "圆愁", "publish_time": "26-1-13 19:37", "likes": 464},
    {"id": "21", "content": "恐怖分子，可怕😱😱😱", "author": "伊人飘香1212", "publish_time": "26-1-13 18:35", "likes": 430},
    {"id": "22", "content": "H族是我国所有信奉伊斯兰教的少数民族里毛病最多，要求最多，最排外的一个，没有之一。", "author": "居然酱酱紫", "publish_time": "26-1-13 23:22", "likes": 427},
    {"id": "23", "content": "隔离、立威、寄生壮大、断桥、分裂。塔国也曾经全国只有7座礼拜寺6座教堂，几乎没有信教的，后来独立后就受到国外各种势力影响，礼拜寺有了5000座，教堂和各种教派有了几百个，注册的都有68种，国家就很难治理了，发展也一度中断。", "author": "冥王星1974", "publish_time": "26-1-13 21:58", "likes": 222},
    {"id": "24", "content": "应当推进民族融合，不允许搞民族隔离", "author": "用户7521117407", "publish_time": "26-1-14 08:52", "likes": 0},
    {"id": "25", "content": "其实回族血统是汉族，干嘛给他们分一个民族", "author": "薏苡不是一棵树", "publish_time": "26-1-14 09:54", "likes": 143},
    {"id": "26", "content": "是的，不过我们这回族没看到有带那吓人的头套的，都是小帽子", "author": "等风等雨等外卖的小钱儿", "publish_time": "26-1-14 07:25", "likes": 32},
    {"id": "27", "content": "我们小区一堆带头巾的", "author": "qiaqia快乐", "publish_time": "26-1-14 10:52", "likes": 61},
    {"id": "28", "content": "已经有单民整栋楼不准吃猪肉的贴纸告示了", "author": "天际行者8888", "publish_time": "26-1-14 07:50", "likes": 0},
    {"id": "29", "content": "这些人又不想好了", "author": "Latte帕尼尼", "publish_time": "26-1-14 08:46", "likes": 0},
    {"id": "30", "content": "没教养的多作怪，恶心死", "author": "unnec2026", "publish_time": "26-1-15 02:53", "likes": 0},
]

# 情感词典
SENTIMENT_DICT = {
    'positive': ['支持', '赞同', '认可', '合理', '正确', '应该', '推进', '融合', '好'],
    'suggestion': ['建议', '希望', '可以', '需要', '应当', '应该', '改进'],
    'negative': ['恐怖', '极端', '恶心', '隔离', '歧视', '分裂', '滚出', '作怪',
                 '二等公民', '不如狗', '没人管', '严打', '头疼', '麻烦', '排外',
                 '可诛', '猪狗不如', '💩']
}

def analyze_sentiment(comments):
    """情感分析"""
    results = {
        'positive': [],
        'suggestion': [],
        'neutral': [],
        'negative': []
    }

    for comment in comments:
        content = comment['content']
        scores = {'positive': 0, 'suggestion': 0, 'negative': 0}

        for word in SENTIMENT_DICT['positive']:
            if word in content:
                scores['positive'] += 1

        for word in SENTIMENT_DICT['suggestion']:
            if word in content:
                scores['suggestion'] += 1

        for word in SENTIMENT_DICT['negative']:
            if word in content:
                scores['negative'] += 1

        max_score = max(scores.values())
        if max_score == 0:
            category = 'neutral'
        else:
            category = max(scores, key=scores.get)

        results[category].append({
            'content': content,
            'author': comment['author'],
            'likes': comment['likes'],
            'time': comment['publish_time']
        })

    total = len(comments)
    distribution = {
        '正面': len(results['positive']),
        '建议': len(results['suggestion']),
        '中性': len(results['neutral']),
        '负面': len(results['negative'])
    }

    max_category = max(distribution, key=distribution.get)
    overall_map = {
        '正面': '正面',
        '建议': '建议',
        'neutral': '中性',
        '负面': '负面'
    }

    return {
        'overall': overall_map[max_category],
        'distribution': distribution,
        'comments_by_category': results
    }

def extract_topics(comments):
    """提取高频话题"""
    all_words = []
    for comment in comments:
        content = comment['content']
        words = re.findall(r'[\u4e00-\u9fa5]{2,4}', content)
        all_words.extend(words)

    stop_words = {'他们', '我们', '你们', '自己', '已经', '没有', '不是', '这个', '那个',
                  '怎么', '什么', '一个', '可以', '就是', '还是', '真的', '这样', '那样'}
    words = [w for w in all_words if w not in stop_words and len(w) >= 2]

    word_count = Counter(words)

    return {
        'keywords': [{'word': w, 'count': c} for w, c in word_count.most_common(15)]
    }

def generate_html_report(results, title="清真食堂争议"):
    """生成HTML报告"""
    sentiment = results['sentiment']
    topics = results['topics']
    total_comments = len(WEIBO_COMMENTS)

    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>评论分析报告 - 微博{title}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 40px;
        }}
        .header {{
            text-align: center;
            margin-bottom: 40px;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 25px;
            border-radius: 12px;
            text-align: center;
            color: white;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        }}
        .section {{
            margin-bottom: 40px;
            background: #f8f9fa;
            padding: 30px;
            border-radius: 12px;
        }}
        .comment-item {{
            background: white;
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .keyword-tag {{
            display: inline-block;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            margin: 5px;
            font-size: 14px;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
            margin-left: 10px;
        }}
        .badge-positive {{ background: #4CAF50; color: white; }}
        .badge-suggestion {{ background: #2196F3; color: white; }}
        .badge-neutral {{ background: #FFC107; color: white; }}
        .badge-negative {{ background: #F44336; color: white; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1 style="font-size: 32px; color: #333;">📊 评论分析报告</h1>
            <p style="color: #666; margin-top: 15px;">
                <strong>平台：</strong>微博 |
                <strong>内容：</strong>清真食堂"{title}"标识牌争议 |
                <strong>评论数：</strong>{total_comments}条 |
                <strong>生成时间：</strong>{datetime.now().strftime('%Y-%m-%d')}
            </p>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 40px;">
            <div class="stat-card">
                <div style="font-size: 42px; font-weight: bold;">{total_comments}</div>
                <div style="font-size: 14px; opacity: 0.9;">评论总数</div>
            </div>
            <div class="stat-card">
                <div style="font-size: 36px; font-weight: bold;">{sentiment['overall']}</div>
                <div style="font-size: 14px; opacity: 0.9;">整体情感倾向</div>
            </div>
            <div class="stat-card">
                <div style="font-size: 36px; font-weight: bold;">{topics['keywords'][0]['word']}</div>
                <div style="font-size: 14px; opacity: 0.9;">核心话题</div>
            </div>
            <div class="stat-card">
                <div style="font-size: 36px; font-weight: bold;">{int(sentiment['distribution']['负面']/total_comments*100)}%</div>
                <div style="font-size: 14px; opacity: 0.9;">负面评论占比</div>
            </div>
        </div>

        <div class="section">
            <h2 style="font-size: 24px; margin-bottom: 25px;">😊 情感分析</h2>
            <div style="max-width: 500px; margin: 0 auto;">
                <canvas id="sentimentChart"></canvas>
            </div>
            <div style="margin-top: 30px; text-align: center;">
                <p style="font-size: 18px; color: #333;">
                    <strong>整体倾向：</strong>
                    <span class="badge badge-{'positive' if sentiment['overall'] == '正面' else 'negative'}">
                        {sentiment['overall']}
                    </span>
                </p>
                <p style="color: #666; margin-top: 10px;">
                    大部分网友对此事件表示强烈担忧，认为这是民族隔离和歧视，
                    应当予以纠正。多数评论使用强烈措辞表达对极端宗教行为的反对。
                </p>
            </div>
        </div>

        <div class="section">
            <h2 style="font-size: 24px; margin-bottom: 25px;">💬 高频话题</h2>
            <div style="text-align: center;">
                {''.join([f"<span class='keyword-tag'>{kw['word']} ({kw['count']}次)</span>" for kw in topics['keywords'][:10]])}
            </div>
        </div>

        <div class="section">
            <h2 style="font-size: 24px; margin-bottom: 25px;">💬 代表性评论</h2>

            <div class="comment-item">
                <p style="font-size: 14px; color: #666; margin-bottom: 5px;">
                    <strong>@{WEIBO_COMMENTS[18]['author']}</strong> · {WEIBO_COMMENTS[18]['publish_time']} · 👍 {WEIBO_COMMENTS[18]['likes']}
                </p>
                <p style="color: #333; line-height: 1.6;">
                    {WEIBO_COMMENTS[18]['content']}
                </p>
            </div>

            <div class="comment-item">
                <p style="font-size: 14px; color: #666; margin-bottom: 5px;">
                    <strong>@{WEIBO_COMMENTS[19]['author']}</strong> · {WEIBO_COMMENTS[19]['publish_time']} · 👍 {WEIBO_COMMENTS[19]['likes']}
                </p>
                <p style="color: #333; line-height: 1.6;">
                    {WEIBO_COMMENTS[19]['content']}
                </p>
            </div>

            <div class="comment-item">
                <p style="font-size: 14px; color: #666; margin-bottom: 5px;">
                    <strong>@{WEIBO_COMMENTS[20]['author']}</strong> · {WEIBO_COMMENTS[20]['publish_time']} · 👍 {WEIBO_COMMENTS[20]['likes']}
                </p>
                <p style="color: #333; line-height: 1.6;">
                    {WEIBO_COMMENTS[20]['content']}
                </p>
            </div>

            <div class="comment-item">
                <p style="font-size: 14px; color: #666; margin-bottom: 5px;">
                    <strong>@{WEIBO_COMMENTS[22]['author']}</strong> · {WEIBO_COMMENTS[22]['publish_time']} · 👍 {WEIBO_COMMENTS[22]['likes']}
                </p>
                <p style="color: #333; line-height: 1.6;">
                    {WEIBO_COMMENTS[22]['content']}
                </p>
            </div>

            <div class="comment-item">
                <p style="font-size: 14px; color: #666; margin-bottom: 5px;">
                    <strong>@{WEIBO_COMMENTS[23]['author']}</strong> · {WEIBO_COMMENTS[23]['publish_time']} · 👍 {WEIBO_COMMENTS[23]['likes']}
                </p>
                <p style="color: #333; line-height: 1.6;">
                    {WEIBO_COMMENTS[23]['content']}
                </p>
            </div>

            <div class="comment-item">
                <p style="font-size: 14px; color: #666; margin-bottom: 5px;">
                    <strong>@{WEIBO_COMMENTS[6]['author']}</strong> · {WEIBO_COMMENTS[6]['publish_time']} · 👍 {WEIBO_COMMENTS[6]['likes']}
                </p>
                <p style="color: #333; line-height: 1.6;">
                    {WEIBO_COMMENTS[6]['content']}
                </p>
            </div>
        </div>

        <div class="section">
            <h2 style="font-size: 24px; margin-bottom: 25px;">🎯 行动建议</h2>
            <div style="background: white; padding: 25px; border-radius: 10px;">
                <ul style="line-height: 2; color: #333;">
                    <li><strong>1. 加强监管：</strong>相关部门应当立即关注此类歧视性标识，依法予以纠正和处罚</li>
                    <li><strong>2. 推进融合：</strong>坚决反对各种形式的民族隔离和歧视，倡导各民族平等相处</li>
                    <li><strong>3. 理性表达：</strong>网友在表达观点时应保持理性，避免使用过激言辞</li>
                    <li><strong>4. 正面引导：</strong>媒体应加强民族团结正面宣传，营造和谐氛围</li>
                    <li><strong>5. 完善法规：</strong>完善相关法律法规，明确禁止任何形式的歧视性标识和行为</li>
                </ul>
            </div>
        </div>

        <div style="text-align: center; margin-top: 50px; padding-top: 30px; border-top: 2px solid #e0e0e0; color: #666;">
            <p>📊 由 Claude Code 评论分析SKILL 生成</p>
            <p style="margin-top: 10px;">
                <strong>技术栈：</strong>MCP Chrome DevTools | 情感分析 | 数据可视化
            </p>
        </div>
    </div>

    <script>
        new Chart(document.getElementById('sentimentChart'), {{
            type: 'doughnut',
            data: {{
                labels: ['正面', '建议', '中性', '负面'],
                datasets: [{{
                    data: [{sentiment['distribution']['正面']}, {sentiment['distribution']['建议']}, {sentiment['distribution']['中性']}, {sentiment['distribution']['负面']}],
                    backgroundColor: ['#4CAF50', '#2196F3', '#FFC107', '#F44336'],
                    borderWidth: 3,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            font: {{ size: 14 }}
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                let label = context.label || '';
                                let value = context.parsed || 0;
                                let total = context.dataset.data.reduce((a, b) => a + b, 0);
                                let percentage = ((value / total) * 100).toFixed(1);
                                return label + ': ' + value + '条 (' + percentage + '%)';
                            }}
                        }}
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

    # 保存报告 - 使用正确的文件名格式
    output_dir = Path.home() / 'comment-analysis-reports'
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    report_path = output_dir / f'weibo-{title}.html'

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(html)

    return report_path

def main():
    print("\n" + "="*60)
    print("📊 微博评论分析")
    print("="*60 + "\n")

    print(f"📥 使用 {len(WEIBO_COMMENTS)} 条评论数据\n")

    # 情感分析
    print("😊 步骤1：情感倾向分析...")
    sentiment_results = analyze_sentiment(WEIBO_COMMENTS)
    print(f"✅ 情感分析完成")
    print(f"   整体倾向：{sentiment_results['overall']}")
    print(f"   分布：正面{sentiment_results['distribution']['正面']}条、建议{sentiment_results['distribution']['建议']}条、中性{sentiment_results['distribution']['中性']}条、负面{sentiment_results['distribution']['负面']}条\n")

    # 话题提取
    print("💬 步骤2：高频话题提取...")
    topic_results = extract_topics(WEIBO_COMMENTS)
    print(f"✅ 话题提取完成")
    print(f"   TOP5话题：{', '.join([f'\\\"{kw[\"word']}\\\"({kw[\"count\"]}次)' for kw in topic_results['keywords'][:5]])}\n")

    # 生成报告
    print("📊 步骤3：生成HTML报告...")
    results = {
        'sentiment': sentiment_results,
        'topics': topic_results
    }
    report_path = generate_html_report(results, title="清真食堂争议")
    print(f"✅ 报告已保存：{report_path}\n")

    # 打印核心洞察
    print("="*60)
    print("🎯 核心洞察")
    print("="*60 + "\n")

    print(f"📊 情感倾向：{sentiment_results['overall']}")
    dist = sentiment_results['distribution']
    print(f"   分布：正面{dist['正面']}条、建议{dist['建议']}条、中性{dist['中性']}条、负面{dist['负面']}条\n")

    if topic_results['keywords']:
        top_kw = topic_results['keywords'][0]
        print(f"💬 核心话题：{top_kw['word']}（{top_kw['count']}次）\n")

    print(f"📁 完整报告：{report_path}")
    print("\n✅ 分析完成！\n")

if __name__ == "__main__":
    main()
