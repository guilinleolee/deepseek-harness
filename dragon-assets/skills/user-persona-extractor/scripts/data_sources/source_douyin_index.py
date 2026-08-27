#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
抖音指数数据源 - 使用 MCP Chrome DevTools 爬取
Douyin Index Data Source - Web Scraping with MCP Chrome DevTools

数据来源：https://ecom.oceanengine.com（巨量算数）
"""

import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
from .base_source import BaseDataSource, DataSourceNotAvailableError, DataSourceFetchError


class SourceDouyinIndex(BaseDataSource):
    """抖音指数（抖音创作者中心）数据源

    头条指数已整合到抖音指数平台
    数据来源：https://creator.douyin.com/creator-micro/creator-count/arithmetic-index
    """

    URL = "https://creator.douyin.com"
    INDEX_URL = "https://creator.douyin.com/creator-micro/creator-count/arithmetic-index"

    def __init__(self, config: Dict[str, Any], mcp_tools=None):
        """
        初始化抖音指数数据源

        Args:
            config: 数据源配置
            mcp_tools: MCP Chrome DevTools 工具实例
        """
        super().__init__(config)
        self.mcp_tools = mcp_tools
        self.cookies = config.get('cookies', [])
        self.logged_in = config.get('logged_in', False)
        self.timeout = config.get('timeout', 30000)

    def is_available(self) -> bool:
        """检查数据源是否可用"""
        # 抖音指数需要登录，检查 cookies 是否存在
        return len(self.cookies) > 0 or self.logged_in

    async def fetch_persona_data(self, keyword: str) -> Dict[str, Any]:
        """
        获取用户画像数据

        Args:
            keyword: 关键词

        Returns:
            标准化的用户画像数据
        """
        try:
            # 1. 检查登录状态
            if not self.is_available():
                return self._create_error_response(
                    keyword=keyword,
                    error_message="需要登录抖音创作者中心。请在浏览器中登录 https://creator.douyin.com"
                )

            # 2. 打开新页面并导航
            page_idx = await self._navigate_to_douyin_index()

            # 3. 输入关键词并搜索
            await self._search_keyword(page_idx, keyword)

            # 4. 切换到人群画像标签
            await self._switch_to_persona_tab(page_idx)

            # 5. 提取数据
            demographics = await self._extract_demographics(page_idx)

            # 6. 返回结果
            return self._create_success_response(
                keyword=keyword,
                demographics=demographics,
                data_freshness='近30天',
                source_url=self.INDEX_URL
            )

        except Exception as e:
            return self._create_error_response(
                keyword=keyword,
                error_message=f"数据获取失败: {str(e)}"
            )

    async def _navigate_to_douyin_index(self) -> int:
        """导航到抖音指数页面"""
        if self.mcp_tools is None:
            raise DataSourceNotAvailableError(
                self.source_name,
                "MCP Chrome DevTools 工具未配置"
            )

        # 打开新页面
        result = await self.mcp_tools['new_page'](url=self.INDEX_URL)

        # 加载 cookies
        if self.cookies:
            await self._load_cookies(result.get('pageIdx', 0))

        # 刷新页面以应用 cookies
        await self.mcp_tools['navigate_page'](
            type='reload',
            ignoreCache=True
        )

        await asyncio.sleep(2)

        return result.get('pageIdx', 0)

    async def _load_cookies(self, page_idx: int):
        """加载 cookies 到页面"""
        # 通过 JavaScript 设置 cookies
        for cookie in self.cookies:
            await self.mcp_tools['evaluate_script'](
                function=f"""
                () => {{
                    document.cookie = '{cookie['name']}={cookie['value']}; domain={cookie.get('domain', '.douyin.com')}; path=/';
                }}
                """
            )

    async def _search_keyword(self, page_idx: int, keyword: str):
        """输入关键词并搜索"""
        # 获取页面快照
        snapshot = await self.mcp_tools['take_snapshot'](page_idx=page_idx)

        # 查找搜索框（根据实际页面结构调整）
        search_input = None
        for element in snapshot.get('elements', []):
            if 'input' in element.get('role', '').lower():
                # 检查是否是搜索框
                placeholder = element.get('placeholder', '')
                if '关键词' in placeholder or '搜索' in placeholder:
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
        """切换到人群分析标签"""
        # 等待人群分析标签出现
        try:
            await self.mcp_tools['wait_for'](
                text='人群分析',
                timeout=15000
            )
        except Exception as e:
            raise DataSourceFetchError(
                self.source_name,
                f"等待人群分析标签超时: {str(e)}"
            )

        # 点击人群分析标签
        snapshot = await self.mcp_tools['take_snapshot'](page_idx=page_idx)
        for element in snapshot.get('elements', []):
            if '人群分析' in element.get('text', ''):
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
                            const results = [];
                            charts.forEach(chart => {
                                const instance = echarts.getInstanceByDom(chart);
                                if (instance) {
                                    results.push(instance.getOption());
                                }
                            });
                            return results;
                        }
                    }
                    // 尝试从 React/Vue 状态获取
                    if (window.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
                        const fiber = document.querySelector('#root')?._reactRootContainer?._internalRoot?.current;
                        if (fiber) {
                            return fiber.memoizedProps;
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
        demographics = {
            'age': {},
            'gender': {},
            'region': []
        }

        # 处理多个 ECharts 实例的数据
        if isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    self._parse_echarts_option(item, demographics)
        elif isinstance(data, dict):
            self._parse_echarts_option(data, demographics)

        return demographics

    def _parse_echarts_option(self, option: Dict, demographics: Dict):
        """解析 ECharts option 格式数据"""
        if 'series' in option:
            for series in option['series']:
                series_name = series.get('name', '').lower()

                if 'age' in series_name or '年龄' in series_name:
                    demographics['age'] = self._parse_pie_series(series)

                elif 'gender' in series_name or '性别' in series_name:
                    demographics['gender'] = self._parse_pie_series(series)

                elif 'region' in series_name or '地域' in series_name or '省份' in series_name:
                    demographics['region'] = self._parse_bar_series(series)

    def _parse_pie_series(self, series: Dict) -> Dict:
        """解析饼图 series 数据"""
        result = {}
        for item in series.get('data', []):
            name = item.get('name', '')
            value = item.get('value', 0)

            # 标准化年龄段名称
            if name in ['18-24', '18岁以下']:
                result['18-24'] = value
            elif name in ['25-30', '25-29']:
                result['25-30'] = value
            elif name in ['31-35', '30-34']:
                result['31-35'] = value
            elif name in ['36-40', '35-39']:
                result['36-40'] = value
            elif name in ['40+', '40岁以上']:
                result['40+'] = value
            elif name in ['男', 'male']:
                result['male'] = value
            elif name in ['女', 'female']:
                result['female'] = value
            else:
                result[name] = value

        return result

    def _parse_bar_series(self, series: Dict) -> list:
        """解析柱状图 series 数据"""
        result = []

        # 从 xAxis 获取类别
        categories = []
        if 'xAxis' in series:
            xAxis = series['xAxis']
            if isinstance(xAxis, list):
                for axis in xAxis:
                    if 'data' in axis:
                        categories.extend(axis['data'])
            elif isinstance(xAxis, dict) and 'data' in xAxis:
                categories = xAxis['data']

        # 从 series 获取值
        values = series.get('data', [])

        # 组合数据
        for idx, category in enumerate(categories):
            if idx < len(values):
                result.append({
                    'region': category,
                    'percentage': values[idx]
                })

        return result

    async def _extract_age_from_dom(self, page_idx: int) -> Dict:
        """从 DOM 提取年龄数据（备选方案）"""
        # 使用 OCR 或其他方法
        return {}

    async def _extract_gender_from_dom(self, page_idx: int) -> Dict:
        """从 DOM 提取性别数据（备选方案）"""
        return {}

    async def _extract_region_from_dom(self, page_idx: int) -> list:
        """从 DOM 提取地域数据（备选方案）"""
        return []

    async def save_login_state(self, page_idx: int):
        """
        保存登录状态（cookies）

        使用方法：
        1. 用户在浏览器中手动登录
        2. 调用此方法保存 cookies
        3. 后续访问使用保存的 cookies
        """
        # 获取当前页面的 cookies
        cookies = await self.mcp_tools['evaluate_script'](
            function="""
            () => {
                return document.cookie;
            }
            """
        )

        # 解析并保存 cookies
        if cookies:
            self.cookies = []
            for cookie in cookies.split(';'):
                parts = cookie.strip().split('=')
                if len(parts) == 2:
                    self.cookies.append({
                        'name': parts[0],
                        'value': parts[1],
                        'domain': '.douyin.com'
                    })

            self.logged_in = True

            # 保存到配置文件
            # TODO: 实现 cookies 持久化存储
