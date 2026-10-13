#!/usr/bin/env python3
"""
Penpot Plugin API Client
Plugin开发专用API客户端 - 支持文件读取、组件导出、设计令牌提取
"""

import json
import httpx
from typing import Any, Optional
from pathlib import Path


class PenpotPluginClient:
    """Penpot Plugin API Client for plugin development"""

    def __init__(
        self,
        url: str = "http://localhost:9000",
        api_key: Optional[str] = None,
        file_id: Optional[str] = None,
        timeout: float = 30.0,
    ):
        self.url = url.rstrip("/")
        self.api_key = api_key
        self.file_id = file_id
        self.timeout = timeout
        self._client = httpx.Client(timeout=timeout)

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    # ─────────────────────────────────────────────────────────────
    # File Operations
    # ─────────────────────────────────────────────────────────────

    def get_file(self, file_id: str) -> dict:
        """获取文件完整数据"""
        r = self._client.get(
            f"{self.url}/api/files/{file_id}",
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    def get_file_data(self, file_id: str) -> dict:
        """获取文件数据（包含页面和元素）"""
        r = self._client.get(
            f"{self.url}/api/files/{file_id}/data",
            headers=self._headers(),
        )
        r.raise_for_status()
        return r.json()

    def get_pages(self, file_id: str) -> list[dict]:
        """获取文件所有页面"""
        file_data = self.get_file_data(file_id)
        return file_data.get("pages", [])

    def get_components(self, file_id: str) -> list[dict]:
        """获取文件中的组件库"""
        file_data = self.get_file_data(file_id)
        return file_data.get("components", [])

    def get_libraries(self, team_id: str) -> list[dict]:
        """获取团队设计令牌库"""
        r = self._client.get(
            f"{self.url}/api/libraries",
            headers=self._headers(),
            params={"team_id": team_id},
        )
        r.raise_for_status()
        return r.json().get("libraries", [])

    # ─────────────────────────────────────────────────────────────
    # Component Extraction
    # ─────────────────────────────────────────────────────────────

    def extract_components(self, file_id: str) -> list[dict]:
        """提取所有组件"""
        file_data = self.get_file_data(file_id)
        components = []
        for page in file_data.get("pages", []):
            for child in page.get("children", []):
                if child.get("type") == "component":
                    components.append(self._extract_component(child, page))
        return components

    def _extract_component(self, shape: dict, page: dict) -> dict:
        """从shape提取组件元数据"""
        return {
            "id": shape.get("id"),
            "name": shape.get("name"),
            "path": shape.get("path", ""),
            "page_id": page.get("id"),
            "exports": shape.get("exports", []),
            "props": shape.get("props", {}),
        }

    # ─────────────────────────────────────────────────────────────
    # Design Token Extraction
    # ─────────────────────────────────────────────────────────────

    def extract_colors(self, file_id: str) -> list[dict]:
        """提取色板令牌"""
        file_data = self.get_file_data(file_id)
        colors = []

        # 从组件库中提取颜色
        for library in file_data.get("components", []):
            if library.get("type") == "group" and "colors" in library.get("name", "").lower():
                colors.extend(self._extract_color_group(library))

        # 从shape中提取颜色
        for page in file_data.get("pages", []):
            for child in page.get("children", []):
                if child.get("type") == "rect":
                    fill = child.get("fill-color")
                    if fill:
                        colors.append({
                            "name": child.get("name", "unnamed"),
                            "value": fill,
                            "opacity": child.get("fill-opacity", 1.0),
                        })

        return colors

    def _extract_color_group(self, group: dict) -> list[dict]:
        """提取颜色组"""
        colors = []
        for child in group.get("children", []):
            if child.get("type") == "rect" and child.get("fill-color"):
                colors.append({
                    "name": child.get("name"),
                    "value": child.get("fill-color"),
                    "opacity": child.get("fill-opacity", 1.0),
                })
        return colors

    def extract_typography(self, file_id: str) -> list[dict]:
        """提取文字样式令牌"""
        file_data = self.get_file_data(file_id)
        typography = []

        for page in file_data.get("pages", []):
            for child in page.get("children", []):
                if child.get("type") == "text":
                    typography.append({
                        "name": child.get("name", "unnamed"),
                        "font_family": child.get("font-family", "Inter"),
                        "font_size": child.get("font-size", "16px"),
                        "font_weight": child.get("font-weight", "400"),
                        "line_height": child.get("line-height", "1.5"),
                        "letter_spacing": child.get("letter-spacing", "0"),
                        "text_align": child.get("text-align", "left"),
                    })

        return typography

    def extract_spacing(self, file_id: str) -> list[dict]:
        """提取间距令牌（基于常用间距值）"""
        common_spacing = [0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 64, 80, 96]
        return [
            {"name": f"spacing-{v}", "value": f"{v}px", "description": f"{v}px spacing"}
            for v in common_spacing
        ]

    def extract_shadows(self, file_id: str) -> list[dict]:
        """提取阴影令牌"""
        file_data = self.get_file_data(file_id)
        shadows = []

        for page in file_data.get("pages", []):
            for child in page.get("children", []):
                shadow = child.get("shadow")
                if shadow and child.get("type") == "rect":
                    shadows.append({
                        "name": child.get("name", "unnamed"),
                        "value": self._format_shadow(shadow),
                        "description": f"Shadow: {shadow.get('color', '#000')}",
                    })

        return shadows

    def _format_shadow(self, shadow: dict) -> str:
        """格式化阴影值"""
        x = shadow.get("offset-x", 0)
        y = shadow.get("offset-y", 4)
        blur = shadow.get("blur", 8)
        spread = shadow.get("spread", 0)
        color = shadow.get("color", "#000000")
        opacity = shadow.get("opacity", 0.1)
        return f"{x}px {y}px {blur}px {spread}px {color} {opacity}"

    # ─────────────────────────────────────────────────────────────
    # Export & Sync
    # ─────────────────────────────────────────────────────────────

    def export_tokens_json(self, file_id: str, output_path: str) -> Path:
        """导出设计令牌为JSON"""
        tokens = {
            "colors": self.extract_colors(file_id),
            "typography": self.extract_typography(file_id),
            "spacing": self.extract_spacing(file_id),
            "shadows": self.extract_shadows(file_id),
        }

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(tokens, indent=2, ensure_ascii=False), encoding="utf-8")
        return path

    def export_tokens_css(self, file_id: str, output_path: str) -> Path:
        """导出设计令牌为CSS变量"""
        colors = self.extract_colors(file_id)
        typography = self.extract_typography(file_id)
        spacing = self.extract_spacing(file_id)

        css_lines = [":root {"]
        for c in colors:
            var_name = c["name"].lower().replace(" ", "-")
            opacity = c.get("opacity", 1.0)
            if opacity < 1.0:
                css_lines.append(f"  --color-{var_name}: {c['value']}{opacity};")
            else:
                css_lines.append(f"  --color-{var_name}: {c['value']};")

        for t in typography:
            name = t["name"].lower().replace(" ", "-")
            css_lines.append(f"  --font-{name}-family: {t['font_family']};")
            css_lines.append(f"  --font-{name}-size: {t['font_size']};")
            css_lines.append(f"  --font-{name}-weight: {t['font_weight']};")
            css_lines.append(f"  --font-{name}-line-height: {t['line_height']};")

        for s in spacing:
            var_name = s["name"].lower().replace(" ", "-")
            css_lines.append(f"  --spacing-{var_name}: {s['value']};")

        css_lines.append("}")

        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(css_lines), encoding="utf-8")
        return path

    # ─────────────────────────────────────────────────────────────
    # Health Check
    # ─────────────────────────────────────────────────────────────

    def health_check(self) -> dict:
        """检查Penpot服务健康状态"""
        try:
            r = self._client.get(f"{self.url}/health", timeout=5)
            return {"status": "ok" if r.status_code == 200 else "error", "code": r.status_code}
        except Exception as e:
            return {"status": "error", "error": str(e)}

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def create_client(url: str = "http://localhost:9000", api_key: Optional[str] = None) -> PenpotPluginClient:
    """工厂函数创建客户端"""
    return PenpotPluginClient(url=url, api_key=api_key)
