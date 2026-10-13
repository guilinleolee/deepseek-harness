#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
报告生成器模块
Report Generator Module

生成交互式HTML分析报告。
"""

import json
from pathlib import Path
from datetime import datetime


class ReportGenerator:
    """报告生成器类"""

    def __init__(self):
        self.template_dir = Path(__file__).parent.parent / "assets" / "html"

    def generate_html(self, results: Dict, output_dir: Path) -> Path:
        """
        生成HTML报告

        Args:
            results: 分析结果
            output_dir: 输出目录

        Returns:
            报告文件路径
        """
        # 读取模板
        template_path = self.template_dir / "dashboard.html"

        if not template_path.exists():
            # 如果模板不存在，创建一个基础模板
            self._create_default_template(template_path)

        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()

        # 准备数据
        data_json = json.dumps(results, ensure_ascii=False, indent=2)

        # 渲染模板
        html_content = template_content.replace(
            "{{ANALYSIS_DATA}}",
            data_json
        ).replace(
            "{{GENERATED_TIME}}",
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ).replace(
            "{{PLATFORM}}",
            results["meta"]["platform"]
        ).replace(
            "{{TOTAL_COMMENTS}}",
            str(results["meta"]["total_comments"])
        )

        # 保存文件
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        platform = results["meta"]["platform"]
        filename = f"{platform}-{timestamp}.html"
        output_path = output_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

        return output_path

    def _create_default_template(self, template_path: Path):
        """创建默认HTML模板"""
        template_path.parent.mkdir(parents=True, exist_ok=True)

        html_template = '''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>评论分析报告 - {{PLATFORM}}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: #f5f5f5;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            padding: 30px;
        }
        .header {
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .stat-card {
            background: #f9f9f9;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .stat-value {
            font-size: 32px;
            font-weight: bold;
            color: #2196F3;
        }
        .section {
            margin-bottom: 40px;
        }
        .section h2 {
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 1px solid #e0e0e0;
        }
        .keyword-list {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .keyword-tag {
            background: #e3f2fd;
            color: #1976d2;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
        }
        .viewpoint-item {
            background: #f9f9f9;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #2196F3;
        }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e0e0e0;
            color: #666;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>评论分析报告</h1>
            <p style="color: #666; margin-top: 10px;">
                平台：{{PLATFORM}} |
                评论数：{{TOTAL_COMMENTS}}条 |
                生成时间：{{GENERATED_TIME}}
            </p>
        </div>

        <div id="app">
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value" id="total-comments">-</div>
                    <div>评论总数</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="overall-sentiment">-</div>
                    <div>整体情感</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="top-keyword">-</div>
                    <div>核心话题</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value" id="high-quality-ratio">-</div>
                    <div>高质量评论占比</div>
                </div>
            </div>

            <div class="section">
                <h2>情感分析</h2>
                <canvas id="sentiment-chart" style="max-width: 400px; margin: 0 auto;"></canvas>
            </div>

            <div class="section">
                <h2>高频话题</h2>
                <div class="keyword-list" id="keyword-list"></div>
            </div>

            <div class="section">
                <h2>核心观点</h2>
                <div id="viewpoint-list"></div>
            </div>

            <div class="section">
                <h2>高质量评论</h2>
                <div id="quality-comments"></div>
            </div>
        </div>

        <div class="footer">
            <p>由 Claude Code 评论分析SKILL 生成</p>
        </div>
    </div>

    <script>
        // 分析数据
        const analysisData = {{ANALYSIS_DATA}};

        // 更新统计卡片
        document.getElementById('total-comments').textContent = analysisData.meta.total_comments;
        document.getElementById('overall-sentiment').textContent = analysisData.sentiment.overall || '中性';

        const topKeyword = analysisData.topics?.keywords?.[0];
        document.getElementById('top-keyword').textContent = topKeyword ? `${topKeyword.word} (${topKeyword.count})` : '-';

        const qualityRatio = Math.round(analysisData.quality?.high_quality_ratio * 100) || 0;
        document.getElementById('high-quality-ratio').textContent = qualityRatio + '%';

        // 情感分布饼图
        const sentimentCtx = document.getElementById('sentiment-chart').getContext('2d');
        const sentimentData = analysisData.sentiment.distribution || {};
        new Chart(sentimentCtx, {
            type: 'doughnut',
            data: {
                labels: ['正面', '建议', '中性', '负面'],
                datasets: [{
                    data: [
                        sentimentData.positive || 0,
                        sentimentData.suggestion || 0,
                        sentimentData.neutral || 0,
                        sentimentData.negative || 0
                    ],
                    backgroundColor: ['#4CAF50', '#2196F3', '#FFC107', '#F44336']
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });

        // 关键词列表
        const keywordList = document.getElementById('keyword-list');
        const keywords = analysisData.topics?.keywords?.slice(0, 20) || [];
        keywords.forEach(kw => {
            const tag = document.createElement('div');
            tag.className = 'keyword-tag';
            tag.textContent = `${kw.word} (${kw.count})`;
            keywordList.appendChild(tag);
        });

        // 核心观点
        const viewpointList = document.getElementById('viewpoint-list');
        const viewpoints = analysisData.viewpoints?.viewpoints?.slice(0, 5) || [];
        viewpoints.forEach(vp => {
            const item = document.createElement('div');
            item.className = 'viewpoint-item';
            item.innerHTML = `
                <p style="font-weight: bold; margin-bottom: 10px;">${vp.viewpoint}</p>
                <p style="color: #666; font-size: 14px;">支持度：${vp.support_count}条评论</p>
            `;
            viewpointList.appendChild(item);
        });

        // 高质量评论
        const qualityComments = document.getElementById('quality-comments');
        const highQuality = analysisData.quality?.high_quality_comments?.slice(0, 5) || [];
        highQuality.forEach(c => {
            const item = document.createElement('div');
            item.style.cssText = 'background: #f9f9f9; padding: 15px; margin-bottom: 10px; border-radius: 8px;';
            item.innerHTML = `
                <p style="margin-bottom: 5px;">${c.content}</p>
                <p style="color: #666; font-size: 12px;">— ${c.author || '匿名'} | 点赞 ${c.likes || 0}</p>
            `;
            qualityComments.appendChild(item);
        });
    </script>
</body>
</html>'''

        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(html_template)
