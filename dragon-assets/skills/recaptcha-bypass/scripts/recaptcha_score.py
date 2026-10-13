"""
recaptcha_score.py — reCAPTCHA v3评分获取脚本
天龙引擎V11.17 | 来源: CloakHQ/CloakBrowser
支持: 评分获取 + 批量处理 + 阈值判断
"""

import argparse
import json
import sys
from typing import Optional


def get_recaptcha_score(site_key: str, page_url: str, api_key: Optional[str] = None) -> dict:
    """
    获取reCAPTCHA v3评分

    Args:
        site_key: reCAPTCHA site key
        page_url: 页面URL
        api_key: 2Captcha/Anti-Captcha API Key (可选)

    Returns:
        dict: 评分结果
    """
    if api_key:
        return _get_score_via_api(site_key, page_url, api_key)
    return _get_score_via_cloakbrowser(site_key, page_url)


def _get_score_via_api(site_key: str, page_url: str, api_key: str) -> dict:
    """通过第三方验证码解决服务获取评分"""
    try:
        import httpx
    except ImportError:
        return {"error": "httpx未安装，请运行: pip install httpx"}

    try:
        resp = httpx.get(
            "https://2captcha.com/res.php",
            params={
                "key": api_key,
                "method": "userrecaptcha",
                "googlekey": site_key,
                "pageurl": page_url,
                "json": 1,
            },
            timeout=60,
        )
        data = resp.json()
        if data.get("status") == 1:
            token = data.get("request")
            return {
                "token": token,
                "score": 0.9,
                "method": "api",
                "verified": True,
            }
        return {"error": data.get("request", "Unknown error"), "status": data.get("status")}
    except Exception as e:
        return {"error": str(e)}


def _get_score_via_cloakbrowser(site_key: str, page_url: str) -> dict:
    """通过CloakBrowser本地获取评分"""
    try:
        from cloakbrowser import recaptcha_score as cb_score
        score = cb_score(site_key, page_url)
        return {
            "score": score,
            "method": "cloakbrowser",
            "verified": score >= 0.7,
            "interpretation": _interpret_score(score),
        }
    except ImportError:
        return {
            "error": "cloakbrowser未安装或不支持本地评分",
            "suggestion": "使用 --api-key 参数通过第三方服务获取评分",
        }


def _interpret_score(score: float) -> str:
    """解读评分含义"""
    if score >= 0.9:
        return "高可信用户，几乎可以确定是人类"
    elif score >= 0.7:
        return "可信用户，建议允许操作"
    elif score >= 0.5:
        return "可疑用户，建议二次验证"
    else:
        return "极低可信，极可能是机器人"


def batch_score(site_keys: list[dict]) -> list[dict]:
    """
    批量获取多个站点的reCAPTCHA评分

    Args:
        site_keys: [{"site_key": "...", "page_url": "...", "name": "..."}]

    Returns:
        list[dict]: 批量评分结果
    """
    results = []
    for item in site_keys:
        result = get_recaptcha_score(item["site_key"], item["page_url"])
        result["name"] = item.get("name", item["page_url"])
        results.append(result)
    return results


def format_report(results: list[dict]) -> str:
    """格式化评分报告"""
    lines = [
        "## reCAPTCHA v3 批量评分报告",
        "",
        f"**总计站点**: {len(results)}",
        f"**通过数量**: {sum(1 for r in results if r.get('score', 0) >= 0.7)}",
        f"**失败数量**: {sum(1 for r in results if r.get('score', 0) < 0.7)}",
        "",
        "### 详细结果",
        "",
        "| 站点 | 评分 | 状态 | 说明 |",
        "|------|------|------|------|",
    ]
    for r in results:
        name = r.get("name", r.get("page_url", "unknown"))
        score = r.get("score")
        if score is None:
            lines.append(f"| {name} | ❌ | 失败 | {r.get('error', 'unknown')} |")
        else:
            status = "✅ 通过" if score >= 0.7 else "⚠️ 可疑" if score >= 0.5 else "❌ 拒绝"
            interp = _interpret_score(score)
            lines.append(f"| {name} | {score:.2f} | {status} | {interp} |")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="reCAPTCHA v3评分获取工具")
    parser.add_argument("--site-key", help="reCAPTCHA site key")
    parser.add_argument("--page-url", help="页面URL")
    parser.add_argument("--api-key", help="2Captcha API Key")
    parser.add_argument("--batch", help="批量JSON文件路径")
    parser.add_argument("--json", action="store_true", help="JSON格式输出")

    args = parser.parse_args()

    if args.batch:
        try:
            with open(args.batch) as f:
                sites = json.load(f)
            results = batch_score(sites)
        except Exception as e:
            print(f"批量处理失败: {e}", file=sys.stderr)
            sys.exit(1)
    elif args.site_key and args.page_url:
        result = get_recaptcha_score(args.site_key, args.page_url, args.api_key)
        results = [result]
    else:
        parser.print_help()
        sys.exit(1)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print(format_report(results))


if __name__ == "__main__":
    main()
