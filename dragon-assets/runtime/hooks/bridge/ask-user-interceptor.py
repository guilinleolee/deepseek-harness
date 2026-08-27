---
license: UNKNOWN
---

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AskUserQuestion拦截器
天龙引擎Bridge系统 V1.0

解决半夜无人值守时Claude Code提问卡住的问题

机制：
1. 预设响应配置 - 根据question_id或模式匹配自动回答
2. 默认值回退 - 使用问题的默认值
3. 延迟处理标记 - 标记为等待输入，稍后处理
4. 无人值守模式 - 全局开关控制行为

使用方式：
1. 在bridge-config.json中配置preset_responses
2. 设置unattended_mode=True启用无人值守
3. 任务执行时自动拦截并处理AskUserQuestion
"""

import json
import os
import re
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from pathlib import Path

# Windows编码修复
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


@dataclass
class UserQuestion:
    """用户问题结构"""
    question: str
    question_id: str
    options: Optional[List[str]] = None
    default: Optional[Any] = None
    defer_allowed: bool = False
    timeout: Optional[int] = None  # 秒
    context: Optional[Dict[str, Any]] = None


class AskUserQuestionInterceptor:
    """
    AskUserQuestion拦截器

    支持的响应策略：
    1. 预设响应 - 精确匹配question_id或正则匹配问题文本
    2. 无人值守模式 - 使用默认值或abort
    3. 延迟处理 - 标记为waiting_for_input

    配置示例：
    {
        "unattended_mode": true,
        "unattended_behavior": "default",  # default | abort | first_option
        "preset_responses": {
            "continue?": "yes",
            "confirm delete": "no",
            "regex:.*proceed\\?.*": "yes",
            "target_language": "Chinese"
        },
        "timeout_behavior": "default"
    }
    """

    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._find_config_path()
        self.config = self._load_config()
        self.response_cache: Dict[str, Any] = {}

    def _find_config_path(self) -> str:
        """查找配置文件路径"""
        possible_paths = [
            # 当前目录
            os.path.join(os.path.dirname(__file__), 'bridge-config.json'),
            # 用户主目录
            os.path.expanduser('~/.claude/hooks/bridge/bridge-config.json'),
            # 项目目录
            os.path.join(os.getcwd(), '.claude', 'bridge-config.json'),
        ]

        for path in possible_paths:
            if os.path.exists(path):
                return path

        # 默认返回当前目录
        return possible_paths[0]

    def _load_config(self) -> Dict[str, Any]:
        """加载配置"""
        default_config = {
            'enabled': True,
            'unattended_mode': False,
            'unattended_behavior': 'default',  # default | abort | first_option
            'preset_responses': {},
            'timeout_behavior': 'default',
            'log_interceptions': True
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                    # 合并配置
                    default_config.update(user_config)
        except Exception as e:
            print(f"[AskUserInterceptor] Failed to load config: {e}", file=__import__('sys').stderr)

        return default_config

    def reload_config(self):
        """重新加载配置"""
        self.config = self._load_config()

    def intercept(self, question: UserQuestion) -> Optional[Any]:
        """
        拦截AskUserQuestion

        返回：
        - None: 不拦截，需要人工回答
        - 其他值：使用该值作为响应

        决策优先级：
        1. 精确匹配question_id
        2. 正则模式匹配
        3. 部分文本匹配
        4. 无人值守模式处理
        5. 超时行为处理
        """
        if not self.config.get('enabled', True):
            return None

        # 1. 检查预设响应（精确匹配question_id）
        preset_responses = self.config.get('preset_responses', {})

        if question.question_id in preset_responses:
            response = preset_responses[question.question_id]
            self._log_interception(question, response, 'preset_id')
            return response

        # 2. 检查正则模式匹配
        for pattern, response in preset_responses.items():
            if pattern.startswith('regex:'):
                regex = pattern[6:]
                try:
                    if re.search(regex, question.question, re.IGNORECASE):
                        self._log_interception(question, response, 'regex')
                        return response
                except re.error:
                    continue

        # 3. 检查部分文本匹配
        question_lower = question.question.lower()
        for pattern, response in preset_responses.items():
            if not pattern.startswith('regex:'):
                if pattern.lower() in question_lower:
                    self._log_interception(question, response, 'partial')
                    return response

        # 4. 检查无人值守模式
        if self.config.get('unattended_mode', False):
            response = self._handle_unattended(question)
            if response is not None:
                return response

        # 5. 检查超时响应
        if question.timeout and self.config.get('timeout_behavior') == 'default':
            if question.default is not None:
                self._log_interception(question, question.default, 'timeout')
                return question.default

        # 6. 检查是否允许延迟
        if question.defer_allowed:
            self._log_interception(question, None, 'defer')
            return {'action': 'defer', 'question_id': question.question_id}

        # 无法自动处理
        self._log_interception(question, None, 'no_match')
        return None

    def _handle_unattended(self, question: UserQuestion) -> Optional[Any]:
        """处理无人值守模式"""
        behavior = self.config.get('unattended_behavior', 'default')

        if behavior == 'default' and question.default is not None:
            self._log_interception(question, question.default, 'unattended_default')
            return question.default

        elif behavior == 'abort':
            self._log_interception(question, None, 'unattended_abort')
            return {'action': 'abort', 'reason': 'unattended_mode'}

        elif behavior == 'first_option' and question.options:
            self._log_interception(question, question.options[0], 'unattended_first')
            return question.options[0]

        return None

    def _log_interception(self, question: UserQuestion, response: Any, method: str):
        """记录拦截日志"""
        if not self.config.get('log_interceptions', True):
            return

        log_entry = {
            'timestamp': __import__('datetime').datetime.now().isoformat(),
            'question': question.question[:100],
            'question_id': question.question_id,
            'response': str(response)[:100] if response else None,
            'method': method
        }

        # 写入日志文件
        try:
            log_dir = os.path.join(os.path.dirname(self.config_path), '..', '..', 'state', 'bridge', 'logs')
            os.makedirs(log_dir, exist_ok=True)
            log_path = os.path.join(log_dir, 'interceptions.jsonl')

            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception:
            pass

    def get_response(self, question_id: str) -> Optional[Any]:
        """获取缓存的响应"""
        return self.response_cache.get(question_id)

    def set_response(self, question_id: str, response: Any):
        """设置响应（供外部注入）"""
        self.response_cache[question_id] = response

    def clear_cache(self):
        """清除响应缓存"""
        self.response_cache.clear()


# =============================================================
# SDK集成补丁（可选）
# =============================================================

def patch_claude_sdk():
    """
    为Claude Code SDK打补丁，拦截AskUserQuestion

    注意：实际实现取决于Claude Code SDK的具体API
    这是一个示例框架，需要根据实际SDK调整
    """
    try:
        # 尝试导入SDK
        # from claude_code import sdk
        # 或
        # from anthropic import Claude

        interceptor = AskUserQuestionInterceptor()

        # 示例：假设SDK有一个ask_user_question函数
        # original_func = sdk.ask_user_question

        def patched_ask_user_question(question: str, **kwargs):
            """补丁后的ask_user_question"""
            q = UserQuestion(
                question=question,
                question_id=kwargs.get('question_id', str(hash(question))),
                options=kwargs.get('options'),
                default=kwargs.get('default'),
                defer_allowed=kwargs.get('defer_allowed', False),
                timeout=kwargs.get('timeout')
            )

            response = interceptor.intercept(q)

            if response is not None:
                return response

            # 无法自动处理，调用原始函数
            # return original_func(question, **kwargs)
            raise Exception("Cannot automatically answer question and no original function available")

        # sdk.ask_user_question = patched_ask_user_question
        print("[AskUserInterceptor] SDK patch applied")

    except ImportError:
        print("[AskUserInterceptor] SDK not found, skipping patch")


# =============================================================
# CLI入口
# =============================================================

if __name__ == '__main__':
    import sys

    print("=" * 60)
    print("AskUserQuestion Interceptor - 天龙引擎Bridge系统 V1.0")
    print("=" * 60)

    interceptor = AskUserQuestionInterceptor()

    print(f"\n配置文件: {interceptor.config_path}")
    print(f"配置内容:")
    print(json.dumps(interceptor.config, ensure_ascii=False, indent=2))

    # 测试拦截
    print("\n" + "=" * 60)
    print("测试拦截:")
    print("=" * 60)

    test_questions = [
        UserQuestion(
            question="是否继续执行?",
            question_id="q1",
            options=["yes", "no"],
            default="yes"
        ),
        UserQuestion(
            question="请确认删除文件",
            question_id="q2",
            options=["confirm", "cancel"],
            default="cancel"
        ),
        UserQuestion(
            question="请选择目标语言",
            question_id="target_language",
            options=["English", "Chinese", "Japanese"],
            default="English"
        ),
        UserQuestion(
            question="这是一个未知问题，需要人工回答",
            question_id="q_unknown",
            default=None
        ),
    ]

    for q in test_questions:
        print(f"\n问题: {q.question}")
        print(f"ID: {q.question_id}")
        print(f"选项: {q.options}")
        print(f"默认: {q.default}")

        response = interceptor.intercept(q)

        if response is None:
            print("结果: ⚠️ 需要人工回答")
        else:
            print(f"结果: ✅ 自动回答 -> {response}")