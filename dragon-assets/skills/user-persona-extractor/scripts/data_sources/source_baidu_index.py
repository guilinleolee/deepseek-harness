#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百度指数数据源 - 使用 MCP Chrome DevTools 爬取
Baidu Index Data Source - Web Scraping with MCP Chrome DevTools

数据来源：https://index.baidu.com
"""

import asyncio
import json
from typing import Dict, Any, Optional
from datetime import datetime
from .base_source import BaseDataSource, DataSourceNotAvailableError, DataSourceFetchError


class SourceBaiduIndex(BaseDataSource):
    """百度指数数据源"""

    URL = "https://index.baidu.com/v2/main/index.html"

    def __init__(self, config: Dict[str, Any], mcp_tools=None):
        """
        初始化百度指数数据源

        Args:
            config: 数据源配置
            mcp_tools: MCP Chrome DevTools 工具实例
        """
        super().__init__(config)
        self.mcp_tools = mcp_tools
        self.cookies = config.get('cookies', [])
        self.timeout = config.get('timeout', 30000)

    def is_available(self) -> bool:
        """检查数据源是否可用"""
        # 百度指数始终可用（无需 API 密钥）
        return True

    async def fetch_persona_data(self, keyword: str) -> Dict[str, Any]:
        """
        获取用户画像数据

        Args:
            keyword: 关键词

        Returns:
            标准化的用户画像数据
        """
        try:
            # 1. 打开新页面并导航
            page_idx = await self._navigate_to_baidu_index()

            # 2. 输入关键词并搜索
            await self._search_keyword(page_idx, keyword)

            # 3. 切换到人群画像标签
            await self._switch_to_persona_tab(page_idx)

            # 4. 提取数据
            demographics = await self._extract_demographics(page_idx)

            # 5. 返回结果
            return self._create_success_response(
                keyword=keyword,
                demographics=demographics,
                data_freshness='近30天',
                source_url=self.URL
            )

        except Exception as e:
            return self._create_error_response(
                keyword=keyword,
                error_message=f"数据获取失败: {str(e)}"
            )

    async def _navigate_to_baidu_index(self) -> int:
        """导航到百度指数页面"""
        if self.mcp_tools is None:
            raise DataSourceNotAvailableError(
                self.source_name,
                "MCP Chrome DevTools 工具未配置"
            )

        # 打开新页面
        result = await self.mcp_tools['new_page'](url=self.URL)
        # 返回页面索引（从 MCP 工具结果中提取）
        # 实际实现需要根据 MCP 工具的返回值调整
        return 0  # 假设返回第一个页面

    async def _search_keyword(self, page_idx: int, keyword: str):
        """输入关键词并搜索"""
        # 获取页面快照
        snapshot = await self.mcp_tools['take_snapshot'](page_idx=page_idx)

        # 查找搜索框（根据实际页面结构调整）
        search_input = None
        for element in snapshot.get('elements', []):
            if 'search' in element.get('text', '').lower():
                search_input = element
                break

        if search_input is None:
            raise DataSourceFetchError(
                self.source_name,
                "未找到搜索框"
            )

        # 输入关键词
        await self.mcp_tools['fill'](
            uid=search_input['uid'],
            value=keyword
        )

        # 按回车搜索
        await self.mcp_tools['press_key'](key='Enter')

        # 等待搜索结果加载
        await asyncio.sleep(3)

    async def _switch_to_persona_tab(self, page_idx: int):
        """切换到人群画像标签"""
        # 等待人群画像标签出现
        try:
            await self.mcp_tools['wait_for'](
                text='人群画像',
                timeout=10000
            )
        except Exception as e:
            raise DataSourceFetchError(
                self.source_name,
                f"等待人群画像标签超时: {str(e)}"
            )

        # 点击人群画像标签
        snapshot = await self.mcp_tools['take_snapshot'](page_idx=page_idx)
        for element in snapshot.get('elements', []):
            if '人群画像' in element.get('text', ''):
                await self.mcp_tools['click'](uid=element['uid'])
                break

        # 等待图表加载
        await asyncio.sleep(2)

    async def _extract_demographics(self, page_idx: int) -> Dict[str, Any]:
        """
        提取人口统计数据

        Returns:
            {
                'age': {'18-24': 0.15, ...},
                'gender': {'male': 0.62, 'female': 0.38},
                'region': [{'region': '广东', 'percentage': 0.18, 'rank': 1}, ...]
            }
        """
        demographics = {
            'age': {},
            'gender': {},
            'region': []
        }

        # 尝试多种数据提取策略
        # 策略 1：从全局变量提取
        try:
            data = await self.mcp_tools['evaluate_script'](
                function="""
                () => {
                    // 尝试从全局变量获取数据
                    if (window.__INITIAL_STATE__?.data) {
                        return window.__INITIAL_STATE__.data;
                    }
                    // 尝试从 ECharts 实例获取
                    if (window.echarts) {
                        const charts = document.querySelectorAll('canvas[_echarts_instance_]');
                        if (charts.length > 0) {
                            const chart = echarts.getInstanceByDom(charts[0]);
                            if (chart) {
                                return chart.getOption();
                            }
                        }
                    }
                    return null;
                }
                """
            )

            if data:
                # 解析提取的数据
                demographics = self._parse_extracted_data(data)
        except Exception as e:
            print(f"策略1失败: {str(e)}")

        # 策略 2：从 DOM 元素解析（如果策略1失败）
        if not demographics['age']:
            try:
                demographics['age'] = await self._extract_age_from_dom(page_idx)
            except Exception as e:
                print(f"年龄数据提取失败: {str(e)}")

        if not demographics['gender']:
            try:
                demographics['gender'] = await self._extract_gender_from_dom(page_idx)
            except Exception as e:
                print(f"性别数据提取失败: {str(e)}")

        if not demographics['region']:
            try:
                demographics['region'] = await self._extract_region_from_dom(page_idx)
            except Exception as e:
                print(f"地域数据提取失败: {str(e)}")

        # 标准化数据
        return {
            'age': self._standardize_age_data(demographics['age']),
            'gender': self._standardize_gender_data(demographics['gender']),
            'region': self._standardize_region_data(demographics['region'])
        }

    def _parse_extracted_data(self, data: Any) -> Dict[str, Any]:
        """解析从页面提取的数据"""
        # 这里需要根据百度指数的实际数据结构进行解析
        # 由于数据结构可能变化，这里提供一个通用框架

        demographics = {
            'age': {},
            'gender': {},
            'region': []
        }

        # 示例：解析 ECharts option 格式
        if isinstance(data, dict):
            # 解析年龄数据
            if 'series' in data:
                for series in data['series']:
                    if 'age' in series.get('name', '').lower():
                        demographics['age'] = self._parse_chart_series(series)

                    if 'gender' in series.get('name', '').lower():
                        demographics['gender'] = self._parse_chart_series(series)

                    if 'region' in series.get('name', '').lower():
                        demographics['region'] = self._parse_chart_series(series)

        return demographics

    def _parse_chart_series(self, series: Dict) -> Any:
        """解析 ECharts series 数据"""
        # 根据 series 类型解析数据
        data_type = series.get('type', '')

        if data_type == 'pie':
            # 饼图数据
            result = {}
            for item in series.get('data', []):
                name = item.get('name', '')
                value = item.get('value', 0)
                result[name] = value
            return result

        elif data_type == 'bar':
            # 柱状图数据
            result = []
            categories = series.get('xAxis', {}).get('data', [])
            values = series.get('data', [])
            for idx, category in enumerate(categories):
                if idx < len(values):
                    result.append({
                        'region': category,
                        'percentage': values[idx]
                    })
            return result

        return {}

    async def _extract_age_from_dom(self, page_idx: int) -> Dict:
        """从 DOM 提取年龄数据（备选方案）"""
        # 使用 OCR 或其他方法
        # 这里提供一个框架，实际实现需要根据页面结构调整
        return {}

    async def _extract_gender_from_dom(self, page_idx: int) -> Dict:
        """从 DOM 提取性别数据（备选方案）"""
        return {}

    async def _extract_region_from_dom(self, page_idx: int) -> list:
        """从 DOM 提取地域数据（备选方案）"""
        return []


# 辅助函数

def find_element_by_text(snapshot: Dict, text: str) -> Optional[Dict]:
    """
    在快照中查找包含指定文本的元素

    Args:
        snapshot: 页面快照
        text: 要查找的文本

    Returns:
        找到的元素，未找到返回 None
    """
    for element in snapshot.get('elements', []):
        if text in element.get('text', ''):
            return element
    return None


def find_element_by_placeholder(snapshot: Dict, placeholder: str) -> Optional[Dict]:
    """
    在快照中查找包含指定 placeholder 的元素

    Args:
        snapshot: 页面快照
        placeholder: 要查找的 placeholder

    Returns:
        找到的元素，未找到返回 None
    """
    for element in snapshot.get('elements', []):
        if placeholder in element.get('placeholder', ''):
            return element
    return None
