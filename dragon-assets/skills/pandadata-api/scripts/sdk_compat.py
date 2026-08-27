#!/usr/bin/env python3
"""
Pandadata SDK 兼容层

提供与官方 pandadata SDK 的兼容接口

Usage:
    from sdk_compat import PandadataSDK
    sdk = PandadataSDK(api_key="your-key")
    data = sdk.get_stock_daily("600519")
"""

import os
from typing import Dict, Any, Optional, List

from .pandadata_runtime import PandadataRuntime


class PandadataSDK:
    """
    Pandadata SDK 兼容层

    提供与官方 SDK 兼容的接口
    """

    def __init__(self, api_key: Optional[str] = None, **kwargs):
        """
        初始化 SDK

        Args:
            api_key: API 密钥
            **kwargs: 其他配置参数
        """
        self.api_key = api_key or os.environ.get("PANDADATA_API_KEY", "")
        self.runtime = PandadataRuntime(api_key=self.api_key, **kwargs)

    def get_stock_daily(
        self,
        code: str,
        date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """获取股票日线数据"""
        return self.runtime.get_stock_daily(code, date, **kwargs)

    def get_stock_detail(
        self,
        code: str,
        **kwargs
    ) -> Dict[str, Any]:
        """获取股票基本信息"""
        return self.runtime.get_stock_detail(code, **kwargs)

    def get_money_flow(
        self,
        code: str,
        date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """获取资金流向"""
        return self.runtime.get_money_flow(code, date, **kwargs)

    def get_fina_indicator(
        self,
        code: str,
        **kwargs
    ) -> Dict[str, Any]:
        """获取财务指标"""
        return self.runtime.get_fina_indicator(code, **kwargs)

    def get_fina_report(
        self,
        code: str,
        count: int = 4,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取财务报表"""
        return self.runtime.call("get_fina_report", code=code, count=count, **kwargs)

    def get_research_report(
        self,
        code: str,
        **kwargs
    ) -> Dict[str, Any]:
        """获取研报汇总"""
        return self.runtime.call("get_research_report", code=code, **kwargs)

    def get_margin(
        self,
        code: str,
        date: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """获取融资融券"""
        return self.runtime.get_margin(code, date, **kwargs)

    def get_lhb_list(
        self,
        date: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取龙虎榜列表"""
        return self.runtime.call("get_lhb_list", date=date, **kwargs)

    def get_lhb_detail(
        self,
        code: str,
        count: int = 5,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取龙虎榜明细"""
        return self.runtime.call("get_lhb_detail", code=code, count=count, **kwargs)

    def get_shareholder_count(
        self,
        code: str,
        **kwargs
    ) -> Dict[str, Any]:
        """获取股东户数"""
        return self.runtime.call("get_shareholder_count", code=code, **kwargs)

    def get_notice(
        self,
        code: str,
        count: int = 10,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取重要公告"""
        return self.runtime.call("get_notice", code=code, count=count, **kwargs)

    def get_index_daily(
        self,
        date: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取指数日线"""
        return self.runtime.call("get_index_daily", date=date, **kwargs)

    def get_index_indicator(
        self,
        date: str,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """获取指数指标"""
        return self.runtime.call("get_index_indicator", date=date, **kwargs)

    def call(self, method: str, **kwargs) -> Any:
        """通用调用接口"""
        return self.runtime.call(method, **kwargs)


# 别名
SDK = PandadataSDK
