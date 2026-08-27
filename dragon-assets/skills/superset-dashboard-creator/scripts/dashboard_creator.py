#!/usr/bin/env python3
"""
Apache Superset 仪表板创建器
支持 50+ 图表类型、自动图表选择、仪表板布局、嵌入配置

天龙引擎 V8.41 集成
"""

import os
import json
from typing import Optional, Dict, Any, List, Union
from dataclasses import dataclass, field
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# 导入依赖
try:
    from superset_auth import SupersetAuth
    from database_manager import DatabaseManager, DatasetInfo
except ImportError:
    pass


@dataclass
class ChartConfig:
    """图表配置"""
    chart_type: str
    title: str
    dataset_id: int
    x_axis: Optional[str] = None
    y_axis: Optional[str] = None
    groupby: Optional[List[str]] = None
    metric: Optional[str] = None
    filters: Optional[List[Dict[str, Any]]] = None
    extra: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DashboardInfo:
    """仪表板信息"""
    id: int
    title: str
    slug: Optional[str] = None
    url: Optional[str] = None
    charts: List[int] = field(default_factory=list)


class ChartRecommender:
    """图表推荐引擎"""

    # 图表类型映射
    CHART_TYPE_MAP = {
        "趋势": ["line", "area", "scatter"],
        "时间": ["line", "area"],
        "对比": ["bar", "dist_bar", "scatter"],
        "占比": ["pie", "treemap", "dist_bar"],
        "分布": ["histogram", "scatter", "heatmap"],
        "密度": ["heatmap", "histogram"],
        "层级": ["treemap", "sunburst"],
        "流向": ["sankey"],
        "转化": ["funnel"],
        "地理": ["map", "deck_gl"],
        "KPI": ["gauge", "big_number", "big_number_total"],
        "相关": ["scatter", "heatmap"],
        "价格": ["candlestick", "line"],
        "增减": ["waterfall", "bar"]
    }

    # 数据类型到图表的映射
    DATA_TYPE_MAP = {
        ("DATE", "FLOAT"): "line",  # 时间 + 数值 = 折线图
        ("DATE", "INT"): "line",
        ("STRING", "FLOAT"): "bar",  # 分类 + 数值 = 柱状图
        ("STRING", "INT"): "bar",
        ("STRING", "STRING"): "pie",  # 分类 + 分类 = 饼图
        ("FLOAT", "FLOAT"): "scatter",  # 数值 + 数值 = 散点图
    }

    def recommend(
        self,
        columns: List[Dict[str, str]],
        intent: Optional[str] = None,
        row_count: int = 1000
    ) -> Dict[str, Any]:
        """推荐图表类型

        Args:
            columns: 列信息 [{"name": "date", "type": "DATE"}, ...]
            intent: 用户意图
            row_count: 数据行数

        Returns:
            推荐结果
        """
        # 基于意图推荐
        if intent:
            for keyword, chart_types in self.CHART_TYPE_MAP.items():
                if keyword in intent:
                    return {
                        "chart_type": chart_types[0],
                        "alternatives": chart_types[1:],
                        "confidence": 0.8,
                        "reason": f"基于意图关键词 '{keyword}' 推荐"
                    }

        # 基于数据类型推荐
        types = [col["type"].upper() for col in columns[:2]]
        type_key = tuple(types)

        if type_key in self.DATA_TYPE_MAP:
            chart_type = self.DATA_TYPE_MAP[type_key]
            return {
                "chart_type": chart_type,
                "alternatives": list(set(["line", "bar", "pie"]) - {chart_type}),
                "confidence": 0.7,
                "reason": f"基于数据类型 {types} 推荐"
            }

        # 默认推荐
        return {
            "chart_type": "bar",
            "alternatives": ["line", "pie"],
            "confidence": 0.5,
            "reason": "默认推荐"
        }


class DashboardCreator:
    """仪表板创建器"""

    def __init__(self, auth: "SupersetAuth" = None):
        """初始化仪表板创建器

        Args:
            auth: SupersetAuth 认证实例
        """
        self.auth = auth or SupersetAuth.from_env()
        self.base_url = self.auth.config.base_url
        self.recommender = ChartRecommender()

        # 初始化 HTTP 会话
        self.session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

    def _request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """发送 API 请求"""
        url = f"{self.base_url}/api/v1/{endpoint.lstrip('/')}"
        headers = self.auth.get_headers()
        headers.update(kwargs.pop("headers", {}))

        response = self.session.request(
            method, url, headers=headers, timeout=30, **kwargs
        )
        response.raise_for_status()
        return response.json()

    # ==================== 图表管理 ====================

    def create_chart(self, config: ChartConfig) -> Dict[str, Any]:
        """创建图表

        Args:
            config: 图表配置

        Returns:
            创建的图表信息
        """
        # 构建 viz_type
        viz_type_map = {
            "line": "line",
            "bar": "bar",
            "pie": "pie",
            "scatter": "scatter",
            "area": "area",
            "heatmap": "heatmap",
            "treemap": "treemap",
            "sankey": "sankey",
            "funnel": "funnel",
            "gauge": "gauge",
            "map": "mapbox",
            "candlestick": "candlestick",
            "waterfall": "waterfall",
            "big_number": "big_number",
            "histogram": "histogram"
        }

        viz_type = viz_type_map.get(config.chart_type, "bar")

        # 构建查询上下文
        query_context = {
            "datasource": {"id": config.dataset_id, "type": "table"},
            "queries": [{
                "viz_type": viz_type,
                "time_range": "No filter",
            }]
        }

        # 添加维度和指标
        if config.x_axis:
            query_context["queries"][0]["granularity"] = config.x_axis
            query_context["queries"][0]["time_range"] = "No filter"

        if config.y_axis:
            query_context["queries"][0]["metrics"] = [config.y_axis]

        if config.groupby:
            query_context["queries"][0]["groupby"] = config.groupby

        if config.metric:
            query_context["queries"][0]["metrics"] = [config.metric]

        if config.filters:
            query_context["queries"][0]["filters"] = config.filters

        # 合并额外配置
        query_context["queries"][0].update(config.extra)

        payload = {
            "slice_name": config.title,
            "datasource_id": config.dataset_id,
            "datasource_type": "table",
            "viz_type": viz_type,
            "params": json.dumps(query_context)
        }

        result = self._request("POST", "chart/", json=payload)
        return result.get("result", {})

    def get_chart_data(self, chart_id: int) -> Dict[str, Any]:
        """获取图表数据

        Args:
            chart_id: 图表 ID

        Returns:
            图表数据
        """
        result = self._request("GET", f"chart/{chart_id}/data/")
        return result.get("result", {})

    def delete_chart(self, chart_id: int) -> bool:
        """删除图表"""
        try:
            self._request("DELETE", f"chart/{chart_id}")
            return True
        except Exception:
            return False

    # ==================== 仪表板管理 ====================

    def create_dashboard(
        self,
        title: str,
        charts: List[Union[ChartConfig, Dict[str, Any]]],
        description: str = "",
        layout: str = "auto",
        refresh_interval: int = 0
    ) -> DashboardInfo:
        """创建仪表板

        Args:
            title: 仪表板标题
            charts: 图表配置列表
            description: 描述
            layout: 布局方式 (auto, grid, free)
            refresh_interval: 刷新间隔（秒）

        Returns:
            创建的仪表板信息
        """
        # 创建图表
        chart_ids = []
        chart_positions = []

        for i, chart_config in enumerate(charts):
            if isinstance(chart_config, dict):
                config = ChartConfig(
                    chart_type=chart_config.get("type", "bar"),
                    title=chart_config.get("title", f"图表 {i+1}"),
                    dataset_id=chart_config.get("dataset"),
                    x_axis=chart_config.get("x_axis"),
                    y_axis=chart_config.get("y_axis"),
                    groupby=chart_config.get("groupby"),
                    metric=chart_config.get("metric"),
                    filters=chart_config.get("filters"),
                    extra=chart_config.get("extra", {})
                )
            else:
                config = chart_config

            chart = self.create_chart(config)
            chart_id = chart.get("id")
            chart_ids.append(chart_id)

            # 计算位置（自动布局）
            row = i // 2
            col = i % 2
            chart_positions.append({
                "chartId": chart_id,
                "row": row,
                "col": col,
                "size_x": 4,
                "size_y": 4
            })

        # 构建仪表板布局
        position_json = self._build_layout(chart_positions, layout)

        # 创建仪表板
        payload = {
            "dashboard_title": title,
            "description": description,
            "slug": title.lower().replace(" ", "-"),
            "position_json": json.dumps(position_json),
            "metadata": json.dumps({"refresh_frequency": refresh_interval}),
            "published": True
        }

        result = self._request("POST", "dashboard/", json=payload)
        dashboard_data = result.get("result", {})

        return DashboardInfo(
            id=dashboard_data.get("id"),
            title=title,
            slug=dashboard_data.get("slug"),
            url=f"{self.base_url}/superset/dashboard/{dashboard_data.get('id')}/",
            charts=chart_ids
        )

    def _build_layout(self, chart_positions: List[Dict], layout: str) -> Dict[str, Any]:
        """构建仪表板布局"""
        position_json = {
            "DASHBOARD_VERSION_KEY": "v2",
            "ROOT_ID": {"children": [], "id": "ROOT_ID", "type": "ROOT"},
            "GRID_ID": {"children": [], "id": "GRID_ID", "parents": ["ROOT_ID"], "type": "GRID"}
        }

        for pos in chart_positions:
            chart_id = pos["chartId"]
            node_id = f"CHART-{chart_id}"

            position_json[node_id] = {
                "children": [],
                "id": node_id,
                "meta": {"chartId": chart_id, "height": pos["size_y"], "width": pos["size_x"]},
                "parents": ["ROOT_ID", "GRID_ID"],
                "type": "CHART"
            }

            position_json["GRID_ID"]["children"].append(node_id)

        position_json["ROOT_ID"]["children"] = ["GRID_ID"]

        return position_json

    def get_dashboard(self, dashboard_id: int) -> DashboardInfo:
        """获取仪表板详情"""
        result = self._request("GET", f"dashboard/{dashboard_id}")
        data = result.get("result", {})

        return DashboardInfo(
            id=data.get("id"),
            title=data.get("dashboard_title"),
            slug=data.get("slug"),
            url=f"{self.base_url}/superset/dashboard/{data.get('id')}/",
            charts=data.get("position_json", {}).get("chartIds", [])
        )

    def delete_dashboard(self, dashboard_id: int) -> bool:
        """删除仪表板"""
        try:
            self._request("DELETE", f"dashboard/{dashboard_id}")
            return True
        except Exception:
            return False

    # ==================== 嵌入配置 ====================

    def get_embed_config(
        self,
        dashboard_id: int,
        user: Optional[Dict[str, str]] = None,
        rls: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """获取嵌入配置

        Args:
            dashboard_id: 仪表板 ID
            user: 用户信息
            rls: 行级安全规则

        Returns:
            嵌入配置
        """
        # 生成 Guest Token
        resources = [{"type": "dashboard", "id": str(dashboard_id)}]
        guest_token = self.auth.create_guest_token(resources=resources, user=user, rls=rls)

        # 构建嵌入 URL
        embed_url = f"{self.base_url}/embed/dashboard/{dashboard_id}/?token={guest_token}"

        # 构建iframe HTML
        iframe_html = f'''<iframe
    src="{embed_url}"
    width="100%"
    height="600"
    frameborder="0"
    allowfullscreen
></iframe>'''

        return {
            "guest_token": guest_token,
            "embed_url": embed_url,
            "iframe_html": iframe_html,
            "dashboard_id": dashboard_id
        }

    # ==================== 导入导出 ====================

    def export_dashboard(self, dashboard_id: int) -> Dict[str, Any]:
        """导出仪表板

        Args:
            dashboard_id: 仪表板 ID

        Returns:
            导出数据
        """
        result = self._request("GET", f"dashboard/export/{dashboard_id}/")
        return result

    def import_dashboard(
        self,
        file_path: str,
        overwrite: bool = False
    ) -> DashboardInfo:
        """导入仪表板

        Args:
            file_path: 导出文件路径
            overwrite: 是否覆盖已存在的仪表板

        Returns:
            导入的仪表板信息
        """
        with open(file_path, "rb") as f:
            files = {"formData": f}
            data = {"overwrite": str(overwrite).lower()}

            result = self._request("POST", "dashboard/import/", files=files, data=data)

        return result.get("result", {})

    # ==================== 模板 ====================

    def create_from_template(
        self,
        template_name: str,
        dataset_id: int,
        title: Optional[str] = None
    ) -> DashboardInfo:
        """从模板创建仪表板

        Args:
            template_name: 模板名称 (sales, growth, investment, etl_monitor)
            dataset_id: 数据集 ID
            title: 自定义标题

        Returns:
            创建的仪表板信息
        """
        templates = {
            "sales": {
                "title": "销售分析仪表板",
                "charts": [
                    {"type": "line", "title": "销售趋势", "dataset": dataset_id},
                    {"type": "pie", "title": "区域占比", "dataset": dataset_id},
                    {"type": "bar", "title": "产品排名", "dataset": dataset_id},
                    {"type": "funnel", "title": "转化漏斗", "dataset": dataset_id}
                ]
            },
            "growth": {
                "title": "用户增长仪表板",
                "charts": [
                    {"type": "line", "title": "用户增长趋势", "dataset": dataset_id},
                    {"type": "heatmap", "title": "活跃度分布", "dataset": dataset_id},
                    {"type": "treemap", "title": "用户分层", "dataset": dataset_id}
                ]
            },
            "investment": {
                "title": "投资组合仪表板",
                "charts": [
                    {"type": "pie", "title": "资产配置", "dataset": dataset_id},
                    {"type": "line", "title": "净值曲线", "dataset": dataset_id},
                    {"type": "gauge", "title": "夏普比率", "dataset": dataset_id},
                    {"type": "heatmap", "title": "相关性矩阵", "dataset": dataset_id}
                ]
            },
            "etl_monitor": {
                "title": "ETL 监控看板",
                "charts": [
                    {"type": "gauge", "title": "今日完成率", "dataset": dataset_id},
                    {"type": "bar", "title": "任务耗时", "dataset": dataset_id},
                    {"type": "line", "title": "数据量趋势", "dataset": dataset_id}
                ]
            }
        }

        if template_name not in templates:
            raise ValueError(f"未知模板: {template_name}")

        template = templates[template_name]
        template_title = title or template["title"]

        return self.create_dashboard(
            title=template_title,
            charts=template["charts"]
        )


def main():
    """CLI 入口"""
    import argparse

    parser = argparse.ArgumentParser(description="Superset 仪表板创建器")
    parser.add_argument("command", choices=[
        "create", "add-chart", "recommend", "embed", "export", "import", "template"
    ])
    parser.add_argument("--title", help="仪表板/图表标题")
    parser.add_argument("--dashboard-id", type=int, help="仪表板 ID")
    parser.add_argument("--dataset-id", type=int, help="数据集 ID")
    parser.add_argument("--type", default="bar", help="图表类型")
    parser.add_argument("--intent", help="分析意图")
    parser.add_argument("--template", help="模板名称")
    parser.add_argument("--rls", help="行级安全规则（JSON）")
    parser.add_argument("--file", help="导入文件路径")

    args = parser.parse_args()

    creator = DashboardCreator()

    if args.command == "create":
        if not args.title or not args.dataset_id:
            print("错误: 需要 --title 和 --dataset-id")
            return

        dashboard = creator.create_dashboard(
            title=args.title,
            charts=[{"type": args.type, "title": args.title, "dataset": args.dataset_id}]
        )
        print(f"创建成功: [{dashboard.id}] {dashboard.title}")
        print(f"URL: {dashboard.url}")

    elif args.command == "recommend":
        recommender = ChartRecommender()
        result = recommender.recommend(
            columns=[{"name": "date", "type": "DATE"}, {"name": "sales", "type": "FLOAT"}],
            intent=args.intent
        )
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "embed":
        if not args.dashboard_id:
            print("错误: 需要 --dashboard-id")
            return

        rls = json.loads(args.rls) if args.rls else None
        config = creator.get_embed_config(args.dashboard_id, rls=rls)
        print(config["iframe_html"])

    elif args.command == "export":
        if not args.dashboard_id:
            print("错误: 需要 --dashboard-id")
            return

        data = creator.export_dashboard(args.dashboard_id)
        output_file = f"dashboard_{args.dashboard_id}.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=2)
        print(f"导出成功: {output_file}")

    elif args.command == "import":
        if not args.file:
            print("错误: 需要 --file")
            return

        dashboard = creator.import_dashboard(args.file)
        print(f"导入成功: [{dashboard.id}] {dashboard.title}")

    elif args.command == "template":
        if not args.template or not args.dataset_id:
            print("错误: 需要 --template 和 --dataset-id")
            return

        dashboard = creator.create_from_template(args.template, args.dataset_id, args.title)
        print(f"创建成功: [{dashboard.id}] {dashboard.title}")
        print(f"URL: {dashboard.url}")


if __name__ == "__main__":
    main()