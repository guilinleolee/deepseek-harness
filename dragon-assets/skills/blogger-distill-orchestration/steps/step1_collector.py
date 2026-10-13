# -*- coding: utf-8 -*-
"""
Step1Collector — 采集管道
来源: blogger-distill-orchestration SKILL.md (lines 44-88)

采集管道：UniversalApiClient + MultiSchemaNormalizer + CheckpointManager + EndpointPoolRouter
输出: {blogger_name}_raw.json (原始笔记列表，含补调前 partial 数据)
"""

import json
import os
import time
from typing import Any, Optional


class UniversalApiClient:
    """小红书 API 客户端，支持 web_v3/app/web_v2/app_v2 四端点探测"""

    ENDPOINTS = ["web_v3", "app", "web_v2", "app_v2"]

    def __init__(self, api_token: Optional[str] = None):
        self.api_token = api_token

    def search_notes(self, blogger_id: str, count: int = 100) -> list[dict]:
        """
        获取博主笔记列表（模拟实现）
        实际使用时应调用真实的小红书 API
        """
        return [
            {
                "id": f"note_{i}",
                "title": f"笔记标题 {i}",
                "author_id": blogger_id,
                "like_count": 100 + i * 10,
                "collected_count": 50 + i * 5,
                "comment_count": 20 + i,
                "share_count": 10 + i,
                "created_at": f"2024-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}",
                "note_type": "normal" if i % 3 != 0 else "video",
            }
            for i in range(min(count, 100))
        ]

    def fetch_note_detail(self, note_id: str) -> dict:
        """
        获取单条笔记详情（模拟实现）
        实际使用时应调用真实的小红书 API
        """
        return {
            "id": note_id,
            "title": f"笔记 {note_id} 详情标题",
            "content": f"这是笔记 {note_id} 的完整正文内容，包含详细描述和分享。",
            "author": {
                "id": "author_1",
                "nickname": "博主昵称",
                "avatar": "https://example.com/avatar.jpg",
                "followers": 10000,
            },
            "interact": {
                "liked_count": 1234,
                "collected_count": 567,
                "comment_count": 89,
                "share_count": 45,
            },
            "tags": ["标签1", "标签2", "标签3"],
            "images": [
                {"url": f"https://example.com/img_{i}.jpg", "width": 1080, "height": 1440}
                for i in range(3)
            ],
            "type": "normal",
        }


class MultiSchemaNormalizer:
    """
    多模式响应标准化器
    统一 D/B/A/C 四种响应结构
    """

    def normalize(self, raw_data: dict) -> dict:
        """
        统一不同 API 响应结构
        D: dict 结构 (most common)
        B: {data: {...}} 结构
        A: {result: {...}} 结构
        C: {content: {...}} 结构
        """
        # D 模式：已经是标准 dict
        if isinstance(raw_data, dict) and "id" in raw_data:
            return self._normalize_D(raw_data)

        # B 模式：{data: {...}}
        if "data" in raw_data and isinstance(raw_data["data"], dict):
            return self._normalize_D(raw_data["data"])

        # A 模式：{result: {...}}
        if "result" in raw_data and isinstance(raw_data["result"], dict):
            return self._normalize_D(raw_data["result"])

        # C 模式：{content: {...}}
        if "content" in raw_data and isinstance(raw_data["content"], dict):
            return self._normalize_D(raw_data["content"])

        # 默认返回原始数据
        return raw_data

    def _normalize_D(self, data: dict) -> dict:
        """标准化 D 模式数据"""
        normalized = {
            "id": data.get("id", ""),
            "title": data.get("title", data.get("note_title", "")),
            "content": data.get("content", data.get("desc", data.get("note_content", ""))),
            "author": {
                "id": self._get_nested(data, "author", "id", default=data.get("user_id", "")),
                "nickname": self._get_nested(data, "author", "nickname", default=data.get("user_nickname", "")),
                "avatar": self._get_nested(data, "author", "avatar", default=""),
                "followers": self._get_nested(data, "author", "followers", default=0),
            },
            "interact": {
                "liked_count": self._get_nested(data, "interact", "liked_count", default=data.get("like_count", 0)),
                "collected_count": self._get_nested(data, "interact", "collected_count", default=data.get("collected_count", 0)),
                "comment_count": self._get_nested(data, "interact", "comment_count", default=data.get("comment_count", 0)),
                "share_count": self._get_nested(data, "interact", "share_count", default=data.get("share_count", 0)),
            },
            "tags": data.get("tags", data.get("tag_list", [])),
            "images": data.get("images", data.get("image_list", [])),
            "type": data.get("type", data.get("note_type", "normal")),
            "created_at": data.get("created_at", data.get("time", data.get("publish_time", ""))),
            "_meta": {
                "repaired": False,
                "verified": False,
            },
        }
        return normalized

    def _get_nested(self, data: dict, *keys, default=None):
        """安全获取嵌套字典值"""
        result = data
        for key in keys:
            if isinstance(result, dict):
                result = result.get(key)
                if result is None:
                    return default
            else:
                return default
        return result if result is not None else default


class CheckpointManager:
    """
    检查点管理器
    每 N 条自动保存，支持崩溃恢复
    """

    def __init__(self, output_dir: str, task_name: str, batch_size: int = 10):
        self.output_dir = output_dir
        self.task_name = task_name
        self.batch_size = batch_size
        self.state_file = os.path.join(output_dir, f"{task_name}_checkpoint.json")
        self._load()

    def _load(self) -> dict:
        """加载检查点状态"""
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return {"done_ids": [], "last_idx": 0, "total_collected": 0}

    def auto_save(self, current_count: int, state: dict):
        """自动保存检查点"""
        state["total_collected"] = current_count
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

    def add_done(self, note_id: str, state: dict):
        """标记笔记已完成"""
        if note_id not in state["done_ids"]:
            state["done_ids"].append(note_id)

    def save(self, state: dict):
        """保存检查点到文件"""
        with open(self.state_file, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)


class EndpointPoolRouter:
    """
    端点池路由器
    按优先级探测可用端点，400 降级、500 重试、429 限流等待
    """

    def __init__(self, client: UniversalApiClient, max_retries: int = 3):
        self.client = client
        self.max_retries = max_retries
        self.current_endpoint = 0

    def probe(self, note_id: str) -> dict:
        """
        探测并获取笔记详情
        优先级: web_v3 > app > web_v2 > app_v2
        """
        for endpoint_idx in range(self.current_endpoint, len(UniversalApiClient.ENDPOINTS)):
            endpoint = UniversalApiClient.ENDPOINTS[endpoint_idx]
            for retry in range(self.max_retries):
                try:
                    detail = self.client.fetch_note_detail(note_id)
                    self.current_endpoint = endpoint_idx
                    return {"endpoint": endpoint, "data": detail, "success": True}
                except Exception as e:
                    error_code = self._parse_error_code(e)
                    if error_code == 400:
                        # 400 错误，跳过当前端点，降级到下一个
                        if endpoint_idx + 1 < len(UniversalApiClient.ENDPOINTS):
                            self.current_endpoint = endpoint_idx + 1
                            break
                        raise
                    elif error_code == 429:
                        # 限流，等待后重试
                        wait_time = 5 * (retry + 1)
                        time.sleep(wait_time)
                        continue
                    elif error_code == 500:
                        # 服务端错误，等待后重试
                        time.sleep(2)
                        continue
                    else:
                        raise
        return {"endpoint": "unknown", "data": {}, "success": False}

    def _parse_error_code(self, exc: Exception) -> int:
        """从异常中解析 HTTP 错误码"""
        exc_str = str(exc)
        if "400" in exc_str:
            return 400
        if "429" in exc_str:
            return 429
        if "500" in exc_str:
            return 500
        return 0


class Step1Collector:
    """
    Step 1 采集管道

    依赖:
      - UniversalApiClient (模拟实现)
      - MultiSchemaNormalizer
      - CheckpointManager
      - EndpointPoolRouter

    输入:
      - blogger_id: str
      - notes_count: int (默认 100)

    处理:
      1. search_notes() → 获取笔记列表
      2. MultiSchemaNormalizer.normalize() → 统一响应结构
      3. EndpointPoolRouter.probe() → 逐条获取详情
      4. CheckpointManager.auto_save() → 每 10 条自动保存

    输出:
      - {blogger_name}_raw.json (原始笔记列表，含补调前 partial 数据)
    """

    def __init__(
        self,
        api_token: Optional[str] = None,
        output_dir: str = "./output",
    ):
        self.api_token = api_token
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

    def run(self, blogger_id: str, notes_count: int = 100) -> dict:
        """
        执行采集流程

        Args:
            blogger_id: 博主 ID
            notes_count: 目标采集数量 (默认 100)

        Returns:
            dict: 采集结果摘要
        """
        blogger_name = blogger_id
        print(f"[Step1Collector] 开始采集 blogger_id={blogger_id}, notes_count={notes_count}")

        # 初始化组件
        client = UniversalApiClient(api_token=self.api_token)
        normalizer = MultiSchemaNormalizer()
        checkpoint_mgr = CheckpointManager(
            output_dir=self.output_dir,
            task_name=blogger_name,
            batch_size=10,
        )
        router = EndpointPoolRouter(client=client, max_retries=3)

        # 加载检查点（崩溃恢复）
        state = checkpoint_mgr._load()
        already_done = set(state["done_ids"])
        start_idx = state["last_idx"]

        # 获取笔记列表
        notes_list = client.search_notes(blogger_id, count=notes_count)
        print(f"[Step1Collector] 获取到 {len(notes_list)} 条笔记列表")

        # 逐条获取详情
        results = []
        failed = []
        checkpoint_interval = 10

        for i, note in enumerate(notes_list):
            if note["id"] in already_done:
                print(f"[Step1Collector] 跳过已采集: {note['id']}")
                continue

            if i < start_idx:
                continue

            try:
                probe_result = router.probe(note["id"])
                if probe_result["success"]:
                    normalized = normalizer.normalize(probe_result["data"])
                    normalized["_meta"]["endpoint"] = probe_result["endpoint"]
                    results.append(normalized)
                    checkpoint_mgr.add_done(note["id"], state)
                else:
                    failed.append({"note_id": note["id"], "reason": "probe failed"})
            except Exception as e:
                failed.append({"note_id": note["id"], "reason": str(e)})

            # 检查点自动保存
            if (i + 1) % checkpoint_interval == 0:
                state["last_idx"] = i + 1
                checkpoint_mgr.auto_save(len(results), state)
                print(f"[Step1Collector] 检查点已保存: {len(results)} 条笔记")

        # 最终保存
        state["last_idx"] = len(notes_list)
        checkpoint_mgr.auto_save(len(results), state)

        # 写入原始数据
        raw_path = os.path.join(self.output_dir, f"{blogger_name}_raw.json")
        with open(raw_path, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "blogger_id": blogger_id,
                    "blogger_name": blogger_name,
                    "total_list": len(notes_list),
                    "collected": len(results),
                    "failed": len(failed),
                    "notes": results,
                    "failed_notes": failed,
                    "checkpoint": state,
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

        print(f"[Step1Collector] 完成: 采集 {len(results)} 条笔记, 失败 {len(failed)} 条")
        return {
            "blogger_id": blogger_id,
            "blogger_name": blogger_name,
            "total_list": len(notes_list),
            "collected": len(results),
            "failed": len(failed),
            "raw_path": raw_path,
        }
