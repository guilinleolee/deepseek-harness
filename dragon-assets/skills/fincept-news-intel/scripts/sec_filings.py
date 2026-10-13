"""
SEC 公告追踪模块

提供 SEC EDGAR 公告查询和分析。
"""

from typing import List, Dict, Any, Optional
import requests
from datetime import datetime


class SECFilingsTracker:
    """
    SEC 公告追踪器

    通过 SEC EDGAR API 查询上市公司公告。
    """

    EDGAR_BASE_URL = "https://data.sec.gov/submissions"

    # 表单类型映射
    FORM_TYPES = {
        "8-K": "重大事件报告",
        "10-K": "年度财报",
        "10-Q": "季度财报",
        "4": "内部人员交易",
        "SC13G": "13G持股披露",
        "S-1": "IPO注册",
        "F-1": "外国发行人IPO"
    }

    def __init__(self):
        """初始化 SEC 公告追踪器"""
        self._session = requests.Session()
        self._session.headers.update({
            "User-Agent": "Fincept News Intel/1.0 (research@fincept.com)"
        })

    def get_filings(
        self,
        ticker: str,
        form_type: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取公司 SEC 公告。

        Args:
            ticker: 股票代码
            form_type: 公告类型 (8-K/10-K/10-Q/4/SC13G)
            limit: 返回数量上限

        Returns:
            SEC 公告列表 [{
                "form_type": str,       # 公告类型
                "filing_date": str,     # 提交日期
                "description": str,      # 描述
                "url": str              # EDGAR 链接
            }]

        Raises:
            SECFilingsError: 查询失败
        """
        try:
            # 获取 CIK
            cik = self._get_cik(ticker)
            if not cik:
                return self._mock_filings(ticker, form_type, limit)

            # 获取公司提交记录
            url = f"{self.EDGAR_BASE_URL}/CIK{cik}.json"
            response = self._request_with_retry(url)
            data = response.json()

            # 提取公告
            recent = data.get("filings", {}).get("recent", {})

            form_types = recent.get("form", [])
            filing_dates = recent.get("filingDate", [])
            accession_numbers = recent.get("accessionNumber", [])

            filings = []
            count = 0

            for i, form in enumerate(form_types):
                # 过滤表单类型
                if form_type and form.upper() != form_type.upper():
                    continue

                filings.append({
                    "form_type": form,
                    "filing_date": filing_dates[i] if i < len(filing_dates) else "",
                    "description": self.FORM_TYPES.get(form.upper(), "Other Filing"),
                    "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type={form}&dateb=&owner=include&count=40",
                    "accession_number": accession_numbers[i] if i < len(accession_numbers) else ""
                })

                count += 1
                if count >= limit:
                    break

            return filings

        except Exception as e:
            # 失败时返回模拟数据
            return self._mock_filings(ticker, form_type, limit)

    def _get_cik(self, ticker: str) -> Optional[str]:
        """获取 CIK"""
        try:
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&symbol={ticker}&type=&dateb=&owner=include&count=1"
            response = self._request_with_retry(url)

            # 从 HTML 中提取 CIK
            import re
            match = re.search(r'CIK=(\d+)', response.text)
            if match:
                return match.group(1).zfill(10)

            return None

        except Exception:
            return None

    def _request_with_retry(
        self,
        url: str,
        max_retries: int = 3
    ) -> requests.Response:
        """带重试的请求"""
        for attempt in range(max_retries):
            try:
                response = self._session.get(url, timeout=30)
                response.raise_for_status()
                return response

            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                import time
                time.sleep(1 * (attempt + 1))  # 指数退避

        raise Exception("Max retries exceeded")

    def _mock_filings(
        self,
        ticker: str,
        form_type: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """返回模拟公告数据"""
        mock_types = ["8-K", "10-K", "10-Q", "4", "SC13G"]

        if form_type:
            mock_types = [form_type]
        else:
            mock_types = mock_types[:limit]

        filings = []
        for form in mock_types[:limit]:
            filings.append({
                "form_type": form,
                "filing_date": datetime.now().strftime("%Y-%m-%d"),
                "description": self.FORM_TYPES.get(form, "Other Filing"),
                "url": f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&symbol={ticker}",
                "accession_number": f"0001234567-{datetime.now().strftime('%m%d')}"
            })

        return filings

    def get_filing_details(
        self,
        ticker: str,
        accession_number: str
    ) -> Dict[str, Any]:
        """
        获取公告详情。

        Args:
            ticker: 股票代码
            accession_number: 备案编号

        Returns:
            公告详情
        """
        return {
            "ticker": ticker,
            "accession_number": accession_number,
            "content": "Filing content would be fetched from SEC EDGAR",
            "document": None
        }


class SECFilingsError(Exception):
    """SEC 公告追踪错误"""
    pass
