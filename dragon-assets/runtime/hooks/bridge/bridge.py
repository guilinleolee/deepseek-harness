#!/usr/bin/env python3
"""
=============================================================
Bridge.py - 执行间
天龙引擎Bridge系统 V1.0

职责：
1. 核心任务执行
2. Watchdog心跳更新
3. AskUserQuestion拦截
4. BaseException万能兜底（三层保险第二层）

三层保险：
- Layer 1 (Shell): EXIT trap - 自动善后
- Layer 2 (Python): BaseException - 捕获所有异常
- Layer 3 (Watchdog): 超时检测 - 检测死锁/僵死状态
=============================================================
"""

import os
import sys
import json
import signal
import threading
import time
import argparse
from datetime import datetime
from typing import Optional, Dict, Any
from pathlib import Path


class BridgeExecutor:
    """Bridge执行器 - 核心执行逻辑"""

    def __init__(self, task_id: str, task: Dict[str, Any],
                 state_path: str, log_path: str, config: Dict[str, Any] = None):
        self.task_id = task_id
        self.task = task
        self.state_path = state_path
        self.log_path = log_path
        self.config = config or {}

        # 线程控制
        self.watchdog_thread: Optional[threading.Thread] = None
        self.stop_watchdog = threading.Event()

        # 心跳配置
        self.heartbeat_interval = self.config.get('heartbeat_interval', 10)  # 秒

        # 预设响应
        self.preset_responses: Dict[str, Any] = self.config.get('preset_responses', {})

        # 执行状态
        self.execution_started = time.time()
        self.last_heartbeat = time.time()

    def run(self) -> Dict[str, Any]:
        """主执行入口"""
        self.log("Bridge.py started")
        self.log(f"Task ID: {self.task_id}")
        self.log(f"Task: {json.dumps(self.task, ensure_ascii=False)[:200]}")

        # 启动心跳线程
        self.start_heartbeat()

        try:
            # 执行任务
            result = self.execute_task()

            # 更新状态为完成
            self.update_state('completed', result=result)
            self.log("Task completed successfully")

            return {'status': 'completed', 'result': result}

        except AskUserQuestionException as e:
            # AskUserQuestion拦截处理
            return self.handle_ask_user_question(e)

        except Exception as e:
            # 其他异常由run_with_protection处理
            self.log(f"Task execution failed: {e}")
            raise

        finally:
            # 停止心跳线程
            self.stop_watchdog.set()
            if self.watchdog_thread:
                self.watchdog_thread.join(timeout=5)

    def execute_task(self) -> Any:
        """
        执行具体任务

        这里是任务执行的核心逻辑，支持：
        1. 调用外部命令
        2. 执行Python代码
        3. 调用API
        4. 文件操作等

        可根据task.type分发到不同的执行器
        """
        task_type = self.task.get('type', 'general')
        task_content = self.task.get('content', '')

        self.log(f"Executing task type: {task_type}")

        # 更新心跳
        self.update_heartbeat()

        # 模拟任务执行（实际实现中替换为真实逻辑）
        # 这里可以根据task_type执行不同的操作
        if task_type == 'skill':
            # 执行Skill
            return self.execute_skill(task_content)
        elif task_type == 'command':
            # 执行命令
            return self.execute_command(task_content)
        elif task_type == 'agent':
            # 调用Agent
            return self.execute_agent(task_content)
        else:
            # 通用任务执行
            return self.execute_general(task_content)

    def execute_skill(self, skill_name: str) -> Dict[str, Any]:
        """执行Skill"""
        self.log(f"Executing skill: {skill_name}")

        # 查找Skill文件
        skill_paths = [
            os.path.join(os.path.dirname(self.state_path), '..', '..', 'skills', skill_name, 'SKILL.md'),
            os.path.expanduser(f'~/.claude/skills/{skill_name}/SKILL.md')
        ]

        for skill_path in skill_paths:
            if os.path.exists(skill_path):
                self.log(f"Found skill at: {skill_path}")
                # 这里可以调用实际的Skill执行逻辑
                return {
                    'type': 'skill',
                    'skill': skill_name,
                    'executed': True,
                    'path': skill_path
                }

        raise ValueError(f"Skill not found: {skill_name}")

    def execute_command(self, command: str) -> Dict[str, Any]:
        """执行命令"""
        self.log(f"Executing command: {command[:100]}...")

        import subprocess

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.config.get('command_timeout', 60)
            )

            return {
                'type': 'command',
                'executed': True,
                'returncode': result.returncode,
                'stdout': result.stdout[:1000],  # 限制输出长度
                'stderr': result.stderr[:1000]
            }
        except subprocess.TimeoutExpired:
            raise TimeoutError(f"Command timed out: {command[:50]}")

    def execute_agent(self, agent_id: str) -> Dict[str, Any]:
        """调用Agent"""
        self.log(f"Calling agent: {agent_id}")

        # 这里可以集成天龙引擎的Agent调用逻辑
        return {
            'type': 'agent',
            'agent': agent_id,
            'executed': True,
            'message': f'Agent {agent_id} would be called here'
        }

    def execute_general(self, content: str) -> Dict[str, Any]:
        """通用任务执行"""
        self.log(f"Executing general task: {content[:100]}...")

        # 更新心跳
        self.update_heartbeat()

        # 模拟执行
        time.sleep(1)  # 模拟处理时间

        return {
            'type': 'general',
            'executed': True,
            'content': content[:500],
            'duration': time.time() - self.execution_started
        }

    # =============================================================
    # 心跳机制
    # =============================================================

    def start_heartbeat(self):
        """启动心跳线程"""
        self.watchdog_thread = threading.Thread(
            target=self._heartbeat_loop,
            daemon=True
        )
        self.watchdog_thread.start()
        self.log("Heartbeat thread started")

    def _heartbeat_loop(self):
        """心跳循环"""
        while not self.stop_watchdog.is_set():
            try:
                self.update_heartbeat()
            except Exception as e:
                self.log(f"Heartbeat error: {e}")

            # 等待下一次心跳
            self.stop_watchdog.wait(self.heartbeat_interval)

    def update_heartbeat(self):
        """更新心跳时间戳"""
        try:
            self.last_heartbeat = time.time()

            # 读取当前状态
            state = self.read_state()

            # 更新心跳
            state['heartbeat'] = int(time.time())
            state['heartbeat_iso'] = datetime.now().isoformat()

            # 写入状态
            self.write_state(state)

        except Exception as e:
            self.log(f"Failed to update heartbeat: {e}")

    # =============================================================
    # AskUserQuestion拦截机制
    # =============================================================

    def handle_ask_user_question(self, e: 'AskUserQuestionException') -> Dict[str, Any]:
        """处理AskUserQuestion拦截"""
        self.log(f"AskUserQuestion intercepted: {e.question}")

        # 1. 检查预设响应
        if e.question_id in self.preset_responses:
            response = self.preset_responses[e.question_id]
            self.log(f"Using preset response: {response}")
            return self.provide_response(e.question_id, response)

        # 2. 检查模式匹配
        for pattern, response in self.preset_responses.items():
            if pattern.startswith('regex:'):
                import re
                regex = pattern[6:]
                if re.search(regex, e.question):
                    self.log(f"Matched regex pattern: {pattern}")
                    return self.provide_response(e.question_id, response)
            elif pattern.lower() in e.question.lower():
                self.log(f"Matched pattern: {pattern}")
                return self.provide_response(e.question_id, response)

        # 3. 检查无人值守模式
        if self.config.get('unattended_mode', False):
            behavior = self.config.get('unattended_behavior', 'default')

            if behavior == 'default' and e.default is not None:
                self.log(f"Unattended mode, using default: {e.default}")
                return self.provide_response(e.question_id, e.default)
            elif behavior == 'abort':
                self.log("Unattended mode, aborting")
                self.update_state('aborted', error=f"Cannot answer: {e.question}")
                return {'status': 'aborted', 'reason': 'unattended_mode'}
            elif behavior == 'first_option' and e.options:
                self.log(f"Unattended mode, using first option: {e.options[0]}")
                return self.provide_response(e.question_id, e.options[0])

        # 4. 检查是否允许延迟
        if e.defer_allowed:
            self.update_state('waiting_for_input', question=e.question)
            return {'status': 'waiting_for_input', 'question': e.question}

        # 5. 无法处理，记录错误
        self.log(f"Cannot handle AskUserQuestion: {e.question}")
        self.update_state('failed', error=f"No response for: {e.question}")
        return {'status': 'failed', 'error': 'No response available'}

    def provide_response(self, question_id: str, response: Any) -> Dict[str, Any]:
        """提供响应"""
        # 存储响应
        response_file = os.path.join(
            os.path.dirname(self.state_path),
            f"response_{question_id}.json"
        )

        try:
            with open(response_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'question_id': question_id,
                    'response': response,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.log(f"Failed to save response: {e}")

        return {
            'status': 'response_provided',
            'question_id': question_id,
            'response': response
        }

    # =============================================================
    # 状态管理
    # =============================================================

    def read_state(self) -> Dict[str, Any]:
        """读取状态"""
        try:
            with open(self.state_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {'task_id': self.task_id}

    def write_state(self, state: Dict[str, Any]):
        """写入状态（原子操作）"""
        temp_path = f"{self.state_path}.tmp.{os.getpid()}"

        try:
            with open(temp_path, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)

            # 原子替换
            if sys.platform == 'win32':
                try:
                    os.remove(self.state_path)
                except:
                    pass

            os.replace(temp_path, self.state_path)
        except Exception as e:
            self.log(f"Failed to write state: {e}")
            # 清理临时文件
            try:
                os.remove(temp_path)
            except:
                pass

    def update_state(self, status: str, result: Any = None,
                     error: str = None, **kwargs):
        """更新状态"""
        try:
            state = self.read_state()

            state['status'] = status
            state['updated_at'] = datetime.now().isoformat()

            if result is not None:
                state['result'] = result
            if error is not None:
                state['error'] = error

            state.update(kwargs)

            self.write_state(state)
            self.log(f"State updated: {status}")

        except Exception as e:
            self.log(f"Failed to update state: {e}")

    def log(self, message: str):
        """写入日志"""
        timestamp = datetime.now().isoformat()
        log_entry = f"[{timestamp}] {message}\n"

        try:
            # 确保日志目录存在
            log_dir = os.path.dirname(self.log_path)
            if log_dir:
                os.makedirs(log_dir, exist_ok=True)

            with open(self.log_path, 'a', encoding='utf-8') as f:
                f.write(log_entry)
        except Exception:
            pass  # 日志写入失败不应影响执行

        # 同时输出到stderr
        print(log_entry.strip(), file=sys.stderr)


class AskUserQuestionException(Exception):
    """AskUserQuestion拦截异常"""

    def __init__(self, question: str, question_id: str = None,
                 options: list = None, default: Any = None,
                 defer_allowed: bool = False):
        self.question = question
        self.question_id = question_id or str(hash(question))
        self.options = options
        self.default = default
        self.defer_allowed = defer_allowed
        super().__init__(question)


def run_with_protection(executor: BridgeExecutor) -> Dict[str, Any]:
    """
    第二层保险：BaseException万能兜底
    捕获所有异常（包括KeyboardInterrupt、SystemExit等）
    """
    try:
        return executor.run()

    except KeyboardInterrupt:
        executor.update_state('interrupted', error='KeyboardInterrupt')
        return {'status': 'interrupted', 'error': 'KeyboardInterrupt'}

    except SystemExit as e:
        status = 'completed' if e.code == 0 else 'failed'
        executor.update_state(status, error=f'SystemExit({e.code})')
        return {'status': status, 'exit_code': e.code}

    except MemoryError:
        executor.update_state('failed', error='MemoryError')
        return {'status': 'failed', 'error': 'MemoryError'}

    except TimeoutError as e:
        executor.update_state('timeout', error=str(e))
        return {'status': 'timeout', 'error': str(e)}

    except AskUserQuestionException as e:
        return executor.handle_ask_user_question(e)

    except Exception as e:
        executor.update_state('failed', error=str(e))
        return {'status': 'failed', 'error': str(e)}

    except BaseException as e:
        # 捕获所有其他异常
        executor.update_state('failed', error=f'{type(e).__name__}: {e}')
        return {'status': 'failed', 'error': f'{type(e).__name__}: {e}'}


def main():
    parser = argparse.ArgumentParser(description='Bridge Executor')
    parser.add_argument('--task-id', required=True, help='Task ID')
    parser.add_argument('--task-json', required=True, help='Task JSON')
    parser.add_argument('--state-path', required=True, help='State file path')
    parser.add_argument('--log-path', required=True, help='Log file path')

    args = parser.parse_args()

    # 解析任务
    try:
        task = json.loads(args.task_json)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid task JSON: {e}", file=sys.stderr)
        sys.exit(1)

    # 加载配置
    config_path = os.path.join(os.path.dirname(__file__), 'bridge-config.json')
    config = {}

    try:
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
    except Exception:
        pass

    # 创建执行器
    executor = BridgeExecutor(
        task_id=args.task_id,
        task=task,
        state_path=args.state_path,
        log_path=args.log_path,
        config=config
    )

    # 执行（带保护）
    result = run_with_protection(executor)

    # 输出结果
    print(json.dumps(result, ensure_ascii=False, indent=2))

    # 返回退出码
    return 0 if result.get('status') == 'completed' else 1


if __name__ == '__main__':
    sys.exit(main())