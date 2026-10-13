#!/usr/bin/env python3
"""
Scene Composer
将音频时间线 + Registry组件 + 7场景模板组合为最终 HTML 视频

用法:
    python3 scene_composer.py timeline.json --output video.html
    python3 scene_composer.py timeline.json --theme neon --output video.html
    python3 scene_composer.py timeline.json --validate
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

SKILL_DIR = Path(__file__).parent.parent
REGISTRY_DIR = SKILL_DIR / "registry"
TEMPLATES_DIR = SKILL_DIR / "templates" / "explainer-video"
PROMPTS_DIR = SKILL_DIR / "prompts"


def load_timeline(path: Path) -> dict:
    """加载时间线 JSON"""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_registry_index() -> str:
    """加载 Registry 入口文件"""
    idx = REGISTRY_DIR / "index.js"
    if idx.exists():
        return idx.read_text(encoding="utf-8")
    return ""


def load_scene_template(scene_type: str) -> Optional[str]:
    """加载场景模板 HTML"""
    template_map = {
        "hero": "hero.html",
        "philosophy": "philosophy.html",
        "architecture": "architecture.html",
        "core-tech": "core-tech.html",
        "differentiation": "differentiation.html",
        "vision": "vision.html",
        "cta": "cta.html",
    }
    template_file = TEMPLATES_DIR / template_map.get(scene_type, "")
    if template_file.exists():
        return template_file.read_text(encoding="utf-8")
    return None


def build_scene_html(scene: dict, theme_config: dict) -> str:
    """构建单个场景 HTML"""
    scene_type = scene.get("type", "hero")
    content = scene.get("content", {})

    template = load_scene_template(scene_type)
    if template is None:
        template = _default_scene_template(scene_type)

    # 替换占位符
    html = template
    for key, value in content.items():
        html = html.replace(f"{{{{{key}}}}}", str(value))

    # 应用主题色
    primary = theme_config.get("primary", "#6366f1")
    html = html.replace("{{primary}}", primary)
    return html


def _default_scene_template(scene_type: str) -> str:
    """默认场景模板"""
    templates = {
        "hero": """<div class="scene scene-hero" data-scene="hero" style="opacity:0;">
  <canvas id="particle-hero" data-component="particle-orbit"></canvas>
  <div class="scene-content">
    <h1 class="scene-title">{{title}}</h1>
    <p class="scene-subtitle">{{subtitle}}</p>
  </div>
</div>""",
        "philosophy": """<div class="scene scene-philosophy" style="opacity:0;">
  <div class="philosophy-bg gradient-radial"></div>
  <canvas id="particle-philosophy" data-component="particle-bloom"></canvas>
  <div class="philosophy-content">
    <p class="philosophy-slogan">{{slogan1}}</p>
    <p class="philosophy-slogan">{{slogan2}}</p>
    <p class="philosophy-slogan">{{slogan3}}</p>
  </div>
</div>""",
        "architecture": """<div class="scene scene-architecture" style="opacity:0;">
  <div class="arch-diagram">
    <div class="arch-node" data-node="a"><div class="node-icon">A</div><div class="node-label">{{nodeA}}</div></div>
    <div class="arch-connector"></div>
    <div class="arch-node" data-node="b"><div class="node-icon">B</div><div class="node-label">{{nodeB}}</div></div>
    <div class="arch-connector"></div>
    <div class="arch-node" data-node="c"><div class="node-icon">C</div><div class="node-label">{{nodeC}}</div></div>
  </div>
  <p class="arch-text">{{description}}</p>
</div>""",
        "core-tech": """<div class="scene scene-core-tech" style="opacity:0;">
  <canvas id="particle-core" data-component="particle-spiral"></canvas>
  <div class="core-tech-content">
    <h2 class="core-title">{{title}}</h2>
    <div class="core-metrics">
      <div class="metric">
        <span class="metric-value">{{metricValue}}</span>
        <span class="metric-unit">{{metricUnit}}</span>
        <span class="metric-label">{{metricLabel}}</span>
      </div>
    </div>
    <p class="core-desc">{{description}}</p>
  </div>
</div>""",
        "differentiation": """<div class="scene scene-differentiation" style="opacity:0;">
  <div class="diff-comparison">
    <div class="diff-column competitor"><h3>竞品</h3><ul class="diff-list">{{competitorList}}</ul></div>
    <div class="diff-divider"></div>
    <div class="diff-column ours"><h3>我们</h3><ul class="diff-list">{{oursList}}</ul></div>
  </div>
  <p class="diff-summary">{{summary}}</p>
</div>""",
        "vision": """<div class="scene scene-vision" style="opacity:0;">
  <canvas id="particle-vision" data-component="particle-orbit"></canvas>
  <div class="vision-content">
    <h2 class="vision-title">{{title}}</h2>
    <p class="vision-text">{{text}}</p>
  </div>
</div>""",
        "cta": """<div class="scene scene-cta" style="opacity:0;">
  <div class="cta-content">
    <img src="{{logo}}" class="cta-logo" alt="Logo" />
    <h2 class="cta-title">{{title}}</h2>
    <a href="{{link}}" class="cta-button">{{buttonText}}</a>
    <p class="cta-thanks">{{thanks}}</p>
  </div>
</div>""",
    }
    return templates.get(scene_type, templates["hero"])


def load_theme(theme_name: str) -> dict:
    """加载主题配置"""
    theme_map = {
        "neon": {
            "name": "Neon",
            "primary": "#6366f1",
            "secondary": "#8b5cf6",
            "accent": "#06b6d4",
            "background": "#0f0f23",
            "text": "#f1f5f9",
            "particle": "rgba(99,102,241,0.8)",
        },
        "minimal": {
            "name": "Minimal",
            "primary": "#1a1a2e",
            "secondary": "#16213e",
            "accent": "#0f3460",
            "background": "#ffffff",
            "text": "#1a1a2e",
            "particle": "rgba(26,26,46,0.6)",
        },
        "dark": {
            "name": "Dark",
            "primary": "#1e293b",
            "secondary": "#334155",
            "accent": "#64748b",
            "background": "#0f172a",
            "text": "#f8fafc",
            "particle": "rgba(100,116,139,0.6)",
        },
    }
    return theme_map.get(theme_name, theme_map["neon"])


def compose_html(timeline: dict, theme_config: dict, title: str = "Explainer Video") -> str:
    """组合完整 HTML"""
    scenes_html = ""
    scene_configs = timeline.get("scenes", [])

    for scene in scene_configs:
        scenes_html += build_scene_html(scene, theme_config) + "\n"

    # 加载 Registry JS
    registry_js = load_registry_index()

    # 构建主时间线
    main_timeline = _build_main_timeline(timeline)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}</title>
  <style>
    :root {{
      --primary: {theme_config['primary']};
      --secondary: {theme_config['secondary']};
      --accent: {theme_config['accent']};
      --background: {theme_config['background']};
      --text: {theme_config['text']};
      --particle: {theme_config['particle']};
    }}
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{
      background: var(--background);
      color: var(--text);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      overflow: hidden;
    }}
    .scene {{
      position: absolute;
      top: 0; left: 0;
      width: 100vw; height: 100vh;
      display: flex; align-items: center; justify-content: center;
      flex-direction: column;
    }}
    .gradient-radial {{
      background: radial-gradient(ellipse at center, var(--secondary) 0%, var(--background) 70%);
    }}
    canvas {{ position: absolute; top: 0; left: 0; pointer-events: none; }}
    .scene-content, .philosophy-content, .core-tech-content, .vision-content, .cta-content {{
      position: relative; z-index: 10; text-align: center; padding: 2rem;
    }}
    .hero-title {{ font-size: 4rem; font-weight: 700; margin-bottom: 1rem; }}
    .hero-subtitle {{ font-size: 1.5rem; opacity: 0.8; }}
    .philosophy-slogan {{ font-size: 2.5rem; font-weight: 600; margin: 1rem 0; }}
    .arch-diagram {{ display: flex; align-items: center; gap: 2rem; }}
    .arch-node {{ background: var(--secondary); padding: 1.5rem 2rem; border-radius: 12px; }}
    .node-icon {{ font-size: 2rem; font-weight: bold; color: var(--accent); }}
    .core-title {{ font-size: 3rem; font-weight: 700; margin-bottom: 1.5rem; }}
    .metric {{ display: flex; flex-direction: column; align-items: center; }}
    .metric-value {{ font-size: 5rem; font-weight: 800; color: var(--accent); }}
    .metric-unit {{ font-size: 2rem; }}
    .metric-label {{ font-size: 1.2rem; opacity: 0.7; margin-top: 0.5rem; }}
    .diff-comparison {{ display: flex; gap: 3rem; }}
    .diff-column {{ flex: 1; padding: 2rem; border-radius: 16px; }}
    .diff-column.competitor {{ background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); }}
    .diff-column.ours {{ background: rgba(34,197,94,0.1); border: 1px solid rgba(34,197,94,0.3); }}
    .diff-list {{ list-style: none; margin-top: 1rem; }}
    .diff-list li {{ padding: 0.5rem 0; font-size: 1.2rem; }}
    .diff-column.ours .diff-list li {{ color: #22c55e; }}
    .cta-button {{
      display: inline-block; margin-top: 2rem; padding: 1rem 3rem;
      background: var(--primary); color: white; text-decoration: none;
      border-radius: 50px; font-size: 1.2rem; font-weight: 600;
      transition: transform 0.2s, box-shadow 0.2s;
    }}
    .cta-button:hover {{ transform: scale(1.05); box-shadow: 0 8px 30px rgba(99,102,241,0.4); }}
  </style>
</head>
<body>
{scenes_html}

<!-- GSAP CDN -->
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<!-- Registry Components -->
{registry_js}
<!-- Scene Timelines -->
<script>
// Scene timelines loaded from timeline JSON
const sceneConfigs = {json.dumps(scene_configs, ensure_ascii=False, indent=2)};

window.__timelines = {{}};
window.__currentScene = 0;

function initScenes() {{
  // Register all scenes
  for (const scene of sceneConfigs) {{
    const type = scene.type;
    if (type === 'hero') {{
      const heroTl = gsap.timeline({{ paused: true }});
      heroTl.call(() => window.__registry?.['particle-orbit']?.mount(), null, 0);
      heroTl.fromTo(".scene-hero .logo", {{ scale: 0.5, opacity: 0 }}, {{ scale: 1, opacity: 1, duration: 0.8, ease: "power4.out" }}, 0.3);
      heroTl.fromTo(".hero-title", {{ y: 40, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.6, ease: "power3.out" }}, 0.5);
      heroTl.fromTo(".hero-subtitle", {{ y: 30, opacity: 0 }}, {{ y: 0, opacity: 1, duration: 0.5, ease: "sine.out" }}, 0.8);
      heroTl.call(() => window.__registry?.['particle-orbit']?.unmount(), null, 7);
      window.__timelines['hero'] = heroTl;
    }}
  }}
}}

// Main orchestration timeline
function buildMainTimeline() {{
  let currentTime = 0;
  const tl = gsap.timeline();

  for (let i = 0; i < sceneConfigs.length; i++) {{
    const scene = sceneConfigs[i];
    const sceneEl = document.querySelector(`[data-scene]`) || document.querySelectorAll('.scene')[i];

    // Scene entry
    tl.fromTo(sceneEl,
      {{ opacity: 0, scale: 1.02 }},
      {{ opacity: 1, scale: 1, duration: 0.4, ease: 'power3.out' }},
      currentTime
    );

    // Trigger scene timeline
    tl.call(() => {{
      const sceneTl = window.__timelines[scene.type];
      if (sceneTl) sceneTl.play();
    }}, null, currentTime);

    currentTime += scene.duration || 5;

    // Scene exit
    tl.to(sceneEl, {{ opacity: 0, duration: 0.3 }}, currentTime);
    tl.set(sceneEl, {{ opacity: 0 }});
  }}

  return tl;
}}

// Preview mode: play scene by scene
function previewScene(index) {{
  if (index >= sceneConfigs.length) return;
  const scene = sceneConfigs[index];
  const sceneEl = document.querySelectorAll('.scene')[index];
  gsap.to(sceneEl, {{ opacity: 1, duration: 0.5 }});
  const sceneTl = window.__timelines[scene.type];
  if (sceneTl) sceneTl.restart();
}}

// Export for debugging
window.__composer = {{
  previewScene,
  getConfigs: () => sceneConfigs,
  getTimeline: buildMainTimeline
}};

document.addEventListener('DOMContentLoaded', () => {{
  initScenes();
  const mainTl = buildMainTimeline();
  // Auto-play by default in video mode
  if (window.__videoMode) mainTl.play();
}});
</script>
</body>
</html>"""


def _build_main_timeline(timeline: dict) -> str:
    """生成主时间线 JS 代码"""
    scenes = timeline.get("scenes", [])
    lines = ["function buildMainTimeline() {", "  const tl = gsap.timeline();"]

    current_time = 0.0
    for i, scene in enumerate(scenes):
        duration = scene.get("duration", 5.0)
        scene_type = scene.get("type", "hero")
        lines.append(f"  // Scene {i+1}: {scene_type} ({current_time}s - {current_time + duration}s)")
        lines.append(f"  const scene{i}El = document.querySelectorAll('.scene')[{i}];")
        lines.append(f"  tl.fromTo(scene{i}El, {{opacity:0, scale:1.02}}, {{opacity:1, scale:1, duration:0.4, ease:'power3.out'}}, {current_time});")
        lines.append(f"  tl.call(() => {{const s=window.__timelines['{scene_type}'];if(s)s.play();}}, null, {current_time});")
        lines.append(f"  tl.to(scene{i}El, {{opacity:0, duration:0.3}}, {current_time + duration - 0.3});")
        lines.append(f"  tl.set(scene{i}El, {{opacity:0}});")
        lines.append("")
        current_time += duration

    lines.append("  return tl;")
    lines.append("}")
    return "\n".join(lines)


def validate_composition(timeline: dict) -> list:
    """验证组合完整性"""
    errors = []
    scenes = timeline.get("scenes", [])

    if not scenes:
        errors.append("时间线中没有场景")

    for i, scene in enumerate(scenes):
        if "type" not in scene:
            errors.append(f"场景 {i} 缺少 type 字段")
        if "duration" not in scene:
            errors.append(f"场景 {i} 缺少 duration 字段")
        if scene.get("duration", 0) < 1:
            errors.append(f"场景 {i} 时长 < 1秒，可能太短")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Scene Composer")
    parser.add_argument("timeline", type=Path, help="Timeline JSON file")
    parser.add_argument("--output", "-o", type=Path, help="Output HTML file")
    parser.add_argument("--theme", default="neon", choices=["neon", "minimal", "dark"], help="Theme")
    parser.add_argument("--title", default="Explainer Video", help="Video title")
    parser.add_argument("--validate", action="store_true", help="Validate composition")

    args = parser.parse_args()

    if not args.timeline.exists():
        print(f"ERROR: Timeline file not found: {args.timeline}")
        sys.exit(1)

    timeline = load_timeline(args.timeline)
    theme = load_theme(args.theme)

    if args.validate:
        errors = validate_composition(timeline)
        if errors:
            print("VALIDATION ERRORS:")
            for e in errors:
                print(f"  - {e}")
            sys.exit(1)
        else:
            print(f"VALIDATION PASSED ({len(timeline.get('scenes', []))} scenes)")
            return

    html = compose_html(timeline, theme, args.title)

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(html, encoding="utf-8")
        print(f"Video HTML saved to: {args.output}")
    else:
        print(html)


if __name__ == "__main__":
    main()
