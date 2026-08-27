#!/usr/bin/env python3
"""
HTML Slides Generator - 零依赖演示文稿生成器
从JSON规划生成单文件HTML演示文稿
"""

import json
import argparse
import os
from pathlib import Path
from datetime import datetime

# 主题配置
THEMES = {
    "bold-signal": {
        "name": "Bold Signal",
        "type": "dark",
        "bg_gradient": "linear-gradient(135deg, #0f0f23 0%, #1a1a3e 50%, #0d0d1a 100%)",
        "accent": "#ff6b35",
        "text": "#ffffff",
        "description": "大胆信号风格 - 科技产品发布"
    },
    "electric-studio": {
        "name": "Electric Studio",
        "type": "dark",
        "bg_gradient": "linear-gradient(135deg, #0a0a0a 0%, #1a1a2e 50%, #16213e 100%)",
        "accent": "#00d4ff",
        "text": "#ffffff",
        "description": "电子工作室 - 创意工作室"
    },
    "creative-voltage": {
        "name": "Creative Voltage",
        "type": "dark",
        "bg_gradient": "linear-gradient(135deg, #1a0a2e 0%, #2d1b4e 50%, #1a0a2e 100%)",
        "accent": "#ff00ff",
        "text": "#ffffff",
        "description": "创意电压 - 设计提案"
    },
    "dark-botanical": {
        "name": "Dark Botanical",
        "type": "dark",
        "bg_gradient": "linear-gradient(135deg, #0a1a0a 0%, #1a2e1a 50%, #0d1f0d 100%)",
        "accent": "#4ade80",
        "text": "#ffffff",
        "description": "暗色植物 - 自然/环保主题"
    },
    "notebook-tabs": {
        "name": "Notebook Tabs",
        "type": "light",
        "bg_gradient": "linear-gradient(135deg, #fefce8 0%, #fff7ed 50%, #fef3c7 100%)",
        "accent": "#f59e0b",
        "text": "#1f2937",
        "description": "笔记标签 - 教育/笔记"
    },
    "pastel-geometry": {
        "name": "Pastel Geometry",
        "type": "light",
        "bg_gradient": "linear-gradient(135deg, #fce7f3 0%, #ddd6fe 50%, #e0e7ff 100%)",
        "accent": "#ec4899",
        "text": "#1f2937",
        "description": "柔和几何 - 轻松/生活化"
    },
    "split-pastel": {
        "name": "Split Pastel",
        "type": "light",
        "bg_gradient": "linear-gradient(90deg, #fef3c7 0%, #fef3c7 50%, #e0e7ff 50%, #e0e7ff 100%)",
        "accent": "#8b5cf6",
        "text": "#1f2937",
        "description": "分割柔和 - 对比分析"
    },
    "vintage-editorial": {
        "name": "Vintage Editorial",
        "type": "light",
        "bg_gradient": "linear-gradient(135deg, #fef3c7 0%, #fde68a 50%, #fcd34d 100%)",
        "accent": "#92400e",
        "text": "#1f2937",
        "description": "复古编辑 - 历史/文化"
    },
    "neon-cyber": {
        "name": "Neon Cyber",
        "type": "special",
        "bg_gradient": "linear-gradient(135deg, #0f0f23 0%, #1a0a2e 50%, #0f0f23 100%)",
        "accent": "#00ff88",
        "text": "#00ff88",
        "description": "霓虹赛博 - 赛博朋克/游戏"
    },
    "terminal-green": {
        "name": "Terminal Green",
        "type": "special",
        "bg_gradient": "linear-gradient(135deg, #000000 0%, #0a0a0a 50%, #000000 100%)",
        "accent": "#00ff00",
        "text": "#00ff00",
        "description": "终端绿色 - 开发者/技术"
    },
    "swiss-modern": {
        "name": "Swiss Modern",
        "type": "special",
        "bg_gradient": "#ffffff",
        "accent": "#000000",
        "text": "#000000",
        "description": "瑞士现代 - 极简/商务"
    },
    "paper-ink": {
        "name": "Paper & Ink",
        "type": "special",
        "bg_gradient": "linear-gradient(135deg, #fefce8 0%, #fffbeb 50%, #fef3c7 100%)",
        "accent": "#1c1917",
        "text": "#1c1917",
        "description": "纸墨风格 - 文艺/出版物"
    }
}

def generate_html(plan_path: str, theme_name: str, output_dir: str):
    """生成HTML演示文稿"""

    # 读取规划
    with open(plan_path, 'r', encoding='utf-8') as f:
        plan = json.load(f)

    theme = THEMES.get(theme_name, THEMES["bold-signal"])

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # 生成HTML
    html_content = generate_html_content(plan, theme)

    # 写入文件
    html_file = output_path / "index.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"✅ HTML演示文稿生成成功！")
    print(f"📄 文件路径: {html_file}")
    print(f"🎨 主题: {theme['name']}")
    print(f"📊 总页数: {plan.get('total_slides', len(plan.get('slides', [])))}")

    return str(html_file)

def generate_html_content(plan: dict, theme: dict) -> str:
    """生成完整的HTML内容"""

    slides = plan.get('slides', [])
    title = plan.get('title', '演示文稿')

    # CSS样式
    css = f"""
    * {{
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: {theme['bg_gradient']};
      color: {theme['text']};
      min-height: 100vh;
      overflow: hidden;
    }}

    .slide-container {{
      width: 100vw;
      height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
    }}

    .slide {{
      width: 100%;
      height: 100%;
      display: none;
      padding: 60px;
      animation: fadeIn 0.5s ease-out;
    }}

    .slide.active {{
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
    }}

    @keyframes fadeIn {{
      from {{ opacity: 0; transform: translateY(20px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}

    h1 {{
      font-size: 4rem;
      font-weight: 700;
      margin-bottom: 1rem;
      text-align: center;
    }}

    h2 {{
      font-size: 3rem;
      font-weight: 600;
      margin-bottom: 2rem;
      color: {theme['accent']};
    }}

    p, li {{
      font-size: 1.5rem;
      line-height: 1.8;
      max-width: 900px;
    }}

    .subtitle {{
      font-size: 2rem;
      opacity: 0.8;
      text-align: center;
    }}

    .content {{
      text-align: center;
    }}

    .nav {{
      position: fixed;
      bottom: 40px;
      left: 50%;
      transform: translateX(-50%);
      display: flex;
      gap: 10px;
      z-index: 100;
    }}

    .nav-dot {{
      width: 12px;
      height: 12px;
      border-radius: 50%;
      background: rgba(255,255,255,0.3);
      cursor: pointer;
      transition: all 0.3s ease;
    }}

    .nav-dot.active {{
      background: {theme['accent']};
      transform: scale(1.3);
    }}

    .slide-counter {{
      position: fixed;
      bottom: 40px;
      right: 40px;
      font-size: 1rem;
      opacity: 0.6;
    }}

    @media (max-width: 768px) {{
      h1 {{ font-size: 2.5rem; }}
      h2 {{ font-size: 2rem; }}
      p, li {{ font-size: 1.2rem; }}
      .slide {{ padding: 30px; }}
    }}
    """

    # 生成幻灯片HTML
    slides_html = ""
    for i, slide in enumerate(slides):
        active_class = "active" if i == 0 else ""
        slide_type = slide.get('type', 'content')

        if slide_type == 'cover':
            slides_html += f"""
            <div class="slide {active_class}" data-slide="{i+1}">
              <h1>{slide.get('title', '')}</h1>
              <p class="subtitle">{slide.get('subtitle', '')}</p>
            </div>
            """
        else:
            content_html = slide.get('content', '').replace('\n', '<br>')
            slides_html += f"""
            <div class="slide {active_class}" data-slide="{i+1}">
              <h2>{slide.get('title', '')}</h2>
              <div class="content">
                <p>{content_html}</p>
              </div>
            </div>
            """

    # 导航点
    nav_dots = "".join([
        f'<div class="nav-dot {"active" if i == 0 else ""}" data-slide="{i+1}"></div>'
        for i in range(len(slides))
    ])

    # JavaScript
    js = """
    let currentSlide = 1;
    const totalSlides = document.querySelectorAll('.slide').length;

    function goToSlide(n) {
      if (n < 1) n = 1;
      if (n > totalSlides) n = totalSlides;

      document.querySelectorAll('.slide').forEach(s => s.classList.remove('active'));
      document.querySelectorAll('.nav-dot').forEach(d => d.classList.remove('active'));

      document.querySelector(`.slide[data-slide="${n}"]`).classList.add('active');
      document.querySelector(`.nav-dot[data-slide="${n}"]`).classList.add('active');

      currentSlide = n;
      updateCounter();
    }

    function nextSlide() {
      if (currentSlide < totalSlides) goToSlide(currentSlide + 1);
    }

    function prevSlide() {
      if (currentSlide > 1) goToSlide(currentSlide - 1);
    }

    function updateCounter() {
      document.getElementById('counter').textContent = `${currentSlide} / ${totalSlides}`;
    }

    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowRight' || e.key === ' ') nextSlide();
      if (e.key === 'ArrowLeft') prevSlide();
      if (e.key === 'Home') goToSlide(1);
      if (e.key === 'End') goToSlide(totalSlides);
    });

    document.querySelectorAll('.nav-dot').forEach(dot => {
      dot.addEventListener('click', () => {
        goToSlide(parseInt(dot.dataset.slide));
      });
    });

    updateCounter();
    """

    # 完整HTML
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>{css}</style>
</head>
<body>
  <div class="slide-container">
    {slides_html}
  </div>

  <div class="nav">{nav_dots}</div>
  <div class="slide-counter" id="counter">1 / {len(slides)}</div>

  <script>{js}</script>
</body>
</html>"""

    return html

def main():
    parser = argparse.ArgumentParser(description='HTML Slides Generator')
    parser.add_argument('--plan', required=True, help='Path to slides-plan.json')
    parser.add_argument('--theme', default='bold-signal', help='Theme name')
    parser.add_argument('--output', default='./output', help='Output directory')

    args = parser.parse_args()
    generate_html(args.plan, args.theme, args.output)

if __name__ == '__main__':
    main()