#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基础数据源抽象类
Base Data Source Abstract Class

所有数据源适配器的基类，定义了统一的接口和数据格式。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio


class BaseDataSource(ABC):
    """数据源基类"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化数据源

        Args:
            config: 数据源配置
        """
        self.config = config
        self.source_name = self.__class__.__name__
        self.enabled = config.get('enabled', True)
        self.priority = config.get('priority', 0)

    @abstractmethod
    async def fetch_persona_data(self, keyword: str) -> Dict[str, Any]:
        """
        获取用户画像数据（抽象方法，子类必须实现）

        Args:
            keyword: 关键词

        Returns:
            标准化的用户画像数据
            {
                'source': '数据源名称',
                'keyword': '关键词',
                'success': True/False,
                'error': '错误信息（如果失败）',
                'demographics': {
                    'age': {},      # 年龄分布 {'18-24': 0.15, '25-30': 0.35, ...}
                    'gender': {},   # 性别分布 {'male': 0.62, 'female': 0.38}
                    'region': [],   # 地域分布 [{'region': '广东', 'percentage': 0.18, 'rank': 1}, ...]
                },
                'content_preferences': {},  # 内容偏好（可选）
                'platforms': {},            # 平台分布（可选）
                'metadata': {
                    'fetch_time': datetime.now().isoformat(),
                    'data_freshness': '数据时间范围',
                    'source_url': '数据来源URL',
                }
            }
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """检查数据源是否可用（抽象方法，子类必须实现）"""
        pass

    def _standardize_age_data(self, raw_data: Dict) -> Dict[str, float]:
        """
        标准化年龄数据

        Args:
            raw_data: 原始年龄数据

        Returns:
            标准化的年龄分布
            {
                '18-24': 0.15,
                '25-30': 0.35,
                '31-35': 0.28,
                '36-40': 0.15,
                '40+': 0.07
            }
        """
        # 默认实现，子类可以覆盖
        age_groups = ['18-24', '25-30', '31-35', '36-40', '40+']
        standardized = {}

        for group in age_groups:
            if group in raw_data:
                value = raw_data[group]
                # 确保值在 0-1 之间
                if value > 1:
                    value = value / 100
                standardized[group] = round(value, 4)
            else:
                standardized[group] = 0.0

        return standardized

    def _standardize_gender_data(self, raw_data: Dict) -> Dict[str, float]:
        """
        标准化性别数据

        Args:
            raw_data: 原始性别数据

        Returns:
            标准化的性别分布
            {
                'male': 0.62,
                'female': 0.38
            }
        """
        standardized = {}

        # 处理男性数据
        male_value = 0
        if 'male' in raw_data:
            male_value = raw_data['male']
        elif '男' in raw_data:
            male_value = raw_data['男']
        elif 'M' in raw_data:
            male_value = raw_data['M']

        # 处理女性数据
        female_value = 0
        if 'female' in raw_data:
            female_value = raw_data['female']
        elif '女' in raw_data:
            female_value = raw_data['女']
        elif 'F' in raw_data:
            female_value = raw_data['F']

        # 确保值在 0-1 之间
        if male_value > 1:
            male_value = male_value / 100
        if female_value > 1:
            female_value = female_value / 100

        # 归一化（确保总和为1）
        total = male_value + female_value
        if total > 0:
            standardized['male'] = round(male_value / total, 4)
            standardized['female'] = round(female_value / total, 4)
        else:
            standardized['male'] = 0.5
            standardized['female'] = 0.5

        return standardized

    def _standardize_region_data(self, raw_data: List) -> List[Dict]:
        """
        标准化地域数据

        Args:
            raw_data: 原始地域数据

        Returns:
            标准化的地域分布
            [
                {'region': '广东', 'percentage': 0.18, 'rank': 1},
                {'region': '北京', 'percentage': 0.15, 'rank': 2},
                ...
            ]
        """
        standardized = []

        for idx, item in enumerate(raw_data[:10], 1):  # 只取 TOP 10
            if isinstance(item, dict):
                region = item.get('region') or item.get('name') or item.get('province') or ''
                percentage = item.get('percentage') or item.get('value') or item.get('pct') or 0

                # 确保值在 0-1 之间
                if percentage > 1:
                    percentage = percentage / 100

                standardized.append({
                    'rank': idx,
                    'region': region,
                    'percentage': round(percentage, 4),
                })

        return standardized

    def _create_error_response(self, keyword: str, error_message: str) -> Dict[str, Any]:
        """
        创建错误响应

        Args:
            keyword: 关键词
            error_message: 错误信息

        Returns:
            错误响应
        """
        return {
            'source': self.source_name,
            'keyword': keyword,
            'success': False,
            'error': error_message,
            'demographics': {
                'age': {},
                'gender': {},
                'region': [],
            },
            'metadata': {
                'fetch_time': datetime.now().isoformat(),
            }
        }

    def _create_success_response(self, keyword: str, demographics: Dict, **kwargs) -> Dict[str, Any]:
        """
        创建成功响应

        Args:
            keyword: 关键词
            demographics: 人口统计数据
            **kwargs: 其他可选字段

        Returns:
            成功响应
        """
        response = {
            'source': self.source_name,
            'keyword': keyword,
            'success': True,
            'demographics': demographics,
            'metadata': {
                'fetch_time': datetime.now().isoformat(),
                'data_freshness': kwargs.get('data_freshness', '近30天'),
                'source_url': kwargs.get('source_url', ''),
            }
        }

        # 添加可选字段
        if 'content_preferences' in kwargs:
            response['content_preferences'] = kwargs['content_preferences']
        if 'platforms' in kwargs:
            response['platforms'] = kwargs['platforms']

        return response


class DataSourceError(Exception):
    """数据源错误基类"""

    def __init__(self, source_name: str, message: str):
        self.source_name = source_name
        self.message = message
        super().__init__(f"[{source_name}] {message}")


class DataSourceNotAvailableError(DataSourceError):
    """数据源不可用错误"""

    pass


class DataSourceFetchError(DataSourceError):
    """数据获取错误"""

    pass


class DataSourceParseError(DataSourceError):
    """数据解析错误"""

    pass
