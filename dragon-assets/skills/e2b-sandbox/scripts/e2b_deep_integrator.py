#!/usr/bin/env python3
"""
E2B Deep Integrator - 天龙引擎深度集成
为05安全师、03构建师、04验证师提供深度云沙箱能力

基于E2B深度研究成果设计:
- 05安全师: 隔离安全测试环境
- 03构建师: 云端代码验证
- 04验证师: 隔离测试执行
"""

import os
import re
import json
import time
import hashlib
import subprocess
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# 配置
# ============================================================================

@dataclass
class DeepIntegratorConfig:
    """深度集成器配置"""
    api_key: str = ""
    base_url: str = "https://api.e2b.dev/v1"
    default_timeout: int = 60
    max_retries: int = 3
    output_dir: str = "~/.claude/e2b-deep-integrator"

    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("E2B_API_KEY", ""),
            base_url=os.getenv("E2B_BASE_URL", "https://api.e2b.dev/v1"),
            default_timeout=int(os.getenv("E2B_TIMEOUT", "60")),
            max_retries=int(os.getenv("E2B_MAX_RETRIES", "3")),
            output_dir=os.getenv("E2B_OUTPUT_DIR", "~/.claude/e2b-deep-integrator")
        )

# ============================================================================
# 安全模式枚举
# ============================================================================

class SecurityLevel(Enum):
    """安全等级"""
    SAFE = "safe"           # 基础沙箱
    RESTRICTED = "restricted" # 受限环境
    ISOLATED = "isolated"    # 完全隔离
    UNTRUSTED = "untrusted"   # 不可信代码

# ============================================================================
# Agent类型枚举
# ============================================================================

class AgentType(Enum):
    """天龙Agent类型"""
    SECURITY = "05_security"    # 05安全师
    BUILDER = "03_builder"      # 03构建师
    VALIDATOR = "04_validator"  # 04验证师
    RESEARCHER = "01_researcher" # 01调研师

# ============================================================================
# 危险模式检测器
# ============================================================================

@dataclass
class DangerPattern:
    """危险代码模式"""
    pattern: str
    severity: str  # critical, high, medium, low
    description: str
    remediation: str

# E2B深度研究识别的危险模式
DANGER_PATTERNS: List[DangerPattern] = [
    DangerPattern(
        pattern=r"rm\s+-rf\s+/\s*&\s*&\s*rm",
        severity="critical",
        description="Fork bomb with rm -rf",
        remediation="BLOCK: This pattern indicates a destructive fork bomb attack"
    ),
    DangerPattern(
        pattern=r"eval\s*\(\s*input\s*\(",
        severity="high",
        description="eval(input()) - arbitrary code execution",
        remediation="WARN: Consider sandboxing or use ast.literal_eval"
    ),
    DangerPattern(
        pattern=r"__import__\s*\(\s*['\"]os['\"]",
        severity="high",
        description="Dynamic os import - potential system access",
        remediation="WARN: Restrict dynamic imports in production"
    ),
    DangerPattern(
        pattern=r"subprocess\s*\.\s*run\s*\(\s*\[.*['\"]rm['\"]",
        severity="critical",
        description="subprocess with rm command",
        remediation="BLOCK: Dangerous subprocess with rm"
    ),
    DangerPattern(
        pattern=r"open\s*\(\s*/etc/passwd",
        severity="critical",
        description="Attempting to read /etc/passwd",
        remediation="BLOCK: Access to system files is forbidden"
    ),
    DangerPattern(
        pattern=r"socket\s*\.\s*create_connection\s*\(",
        severity="medium",
        description="Network socket creation",
        remediation="INFO: Network access detected, ensure it's intentional"
    ),
    DangerPattern(
        pattern=r"requests\s*\.\s*(get|post|put)",
        severity="medium",
        description="HTTP request library usage",
        remediation="INFO: External network access detected"
    ),
    DangerPattern(
        pattern=r"urllib\s*\.\s*(request|error)",
        severity="medium",
        description="urllib network access",
        remediation="INFO: External network access detected"
    ),
    DangerPattern(
        pattern=r"os\.system\s*\(",
        severity="high",
        description="os.system() - shell command injection risk",
        remediation="WARN: Consider subprocess.run with list args instead"
    ),
    DangerPattern(
        pattern=r"os\.popen\s*\(",
        severity="high",
        description="os.popen() - shell injection risk",
        remediation="WARN: Use subprocess module with proper escaping"
    ),
    DangerPattern(
        pattern=r"exec\s*\(",
        severity="high",
        description="exec() - arbitrary code execution",
        remediation="WARN: Evaluate if exec is necessary, prefer safer alternatives"
    ),
    DangerPattern(
        pattern=r"pickle\.load\s*\(",
        severity="high",
        description="pickle.load() - deserialization vulnerability",
        remediation="WARN: Never unpickle untrusted data"
    ),
    DangerPattern(
        pattern=r"yaml\.load\s*\([^,)]*\)",
        severity="medium",
        description="yaml.load() without Loader - arbitrary code execution",
        remediation="WARN: Use yaml.safe_load() or yaml.load(..., Loader=yaml.SafeLoader)"
    ),
]

# ============================================================================
# 预配置沙箱模板
# ============================================================================

@dataclass
class SandboxTemplate:
    """沙箱模板定义"""
    name: str
    description: str
    language: str
    packages: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    network: bool = True
    timeout: int = 60
    env_vars: Dict[str, str] = field(default_factory=dict)
    agent_type: AgentType = AgentType.BUILDER
    security_level: SecurityLevel = SecurityLevel.SAFE

# E2B深度研究设计的预配置模板
SANDBOX_TEMPLATES: Dict[str, SandboxTemplate] = {
    # 05安全师模板
    "security-audit": SandboxTemplate(
        name="security-audit",
        description="安全审计专用沙箱 - 完全隔离环境",
        language="python",
        packages=["bandit", "safety", "pip-audit", "snyk"],
        tools=["filesystem", "network"],
        network=True,
        timeout=120,
        agent_type=AgentType.SECURITY,
        security_level=SecurityLevel.ISOLATED
    ),
    "untrusted-code": SandboxTemplate(
        name="untrusted-code",
        description="不可信代码执行沙箱 - 最高隔离级别",
        language="python",
        packages=[""],
        tools=["filesystem:read-only"],
        network=False,
        timeout=30,
        agent_type=AgentType.SECURITY,
        security_level=SecurityLevel.UNTRUSTED
    ),

    # 03构建师模板
    "code-validator": SandboxTemplate(
        name="code-validator",
        description="代码验证沙箱 - 快速验证",
        language="python",
        packages=["pytest", "black", "ruff", "mypy"],
        tools=["filesystem"],
        network=False,
        timeout=60,
        agent_type=AgentType.BUILDER,
        security_level=SecurityLevel.SAFE
    ),
    "data-science": SandboxTemplate(
        name="data-science",
        description="数据科学沙箱 - Python数据分析",
        language="python",
        packages=["pandas", "numpy", "matplotlib", "scipy", "scikit-learn"],
        tools=["filesystem", "network"],
        network=True,
        timeout=180,
        agent_type=AgentType.BUILDER,
        security_level=SecurityLevel.SAFE
    ),
    "web-dev": SandboxTemplate(
        name="web-dev",
        description="Web开发沙箱",
        language="node",
        packages=["express", "react", "next"],
        tools=["filesystem", "network"],
        network=True,
        timeout=120,
        agent_type=AgentType.BUILDER,
        security_level=SecurityLevel.RESTRICTED
    ),

    # 04验证师模板
    "test-runner": SandboxTemplate(
        name="test-runner",
        description="测试运行沙箱 - 隔离测试执行",
        language="python",
        packages=["pytest", "pytest-cov", "pytest-asyncio", "playwright"],
        tools=["filesystem"],
        network=False,
        timeout=120,
        agent_type=AgentType.VALIDATOR,
        security_level=SecurityLevel.SAFE
    ),
    "e2e-testing": SandboxTemplate(
        name="e2e-testing",
        description="E2E测试沙箱",
        language="python",
        packages=["playwright", "selenium", "pytest"],
        tools=["filesystem", "browser"],
        network=True,
        timeout=180,
        agent_type=AgentType.VALIDATOR,
        security_level=SecurityLevel.RESTRICTED
    ),

    # 01调研师模板
    "research": SandboxTemplate(
        name="research",
        description="研究环境沙箱",
        language="python",
        packages=["requests", "beautifulsoup4", "scrapy", "arxiv"],
        tools=["filesystem", "network"],
        network=True,
        timeout=300,
        agent_type=AgentType.RESEARCHER,
        security_level=SecurityLevel.RESTRICTED
    ),
}

# ============================================================================
# 执行结果
# ============================================================================

@dataclass
class ExecutionResult:
    """执行结果"""
    status: str  # success, error, blocked, timeout
    output: str = ""
    error: str = ""
    execution_time: float = 0.0
    danger_warnings: List[Dict] = field(default_factory=list)
    sandbox_id: str = ""
    template: str = ""
    agent_type: AgentType = AgentType.BUILDER

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "output": self.output,
            "error": self.error,
            "execution_time": self.execution_time,
            "danger_warnings": self.danger_warnings,
            "sandbox_id": self.sandbox_id,
            "template": self.template,
            "agent_type": self.agent_type.value
        }

# ============================================================================
# E2B深度集成器
# ============================================================================

class E2BDeepIntegrator:
    """
    E2B深度集成器 - 天龙引擎专用

    核心功能:
    - 05安全师: 隔离安全测试环境
    - 03构建师: 云端代码验证
    - 04验证师: 隔离测试执行
    """

    def __init__(self, config: Optional[DeepIntegratorConfig] = None):
        self.config = config or DeepIntegratorConfig.from_env()
        self.api_key = self.config.api_key
        self.output_dir = Path(self.config.output_dir).expanduser()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self._active_sandboxes: Dict[str, Dict] = {}
        self._execution_history: List[Dict] = []

    # =========================================================================
    # 05安全师集成
    # =========================================================================

    def setup_e2b_for_security_agent(
        self,
        sandbox_type: str = "security-audit"
    ) -> Dict[str, str]:
        """
        为05安全师设置E2B沙箱环境

        使用场景:
        - 不可信代码安全测试
        - 恶意代码隔离执行
        - 依赖漏洞扫描
        - 渗透测试环境
        """
        template = SANDBOX_TEMPLATES.get(sandbox_type, SANDBOX_TEMPLATES["security-audit"])

        # 创建安全配置
        config = {
            "sandbox_type": sandbox_type,
            "template": template.name,
            "agent": "05安全师",
            "security_level": template.security_level.value,
            "tools_enabled": template.tools,
            "network_access": template.network,
            "timeout": template.timeout,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        sandbox_id = self._create_sandbox(template)
        config["sandbox_id"] = sandbox_id
        self._active_sandboxes[sandbox_id] = config

        return config

    def security_audit_code(
        self,
        code: str,
        language: str = "python",
        check_dependencies: bool = True,
        check_patterns: bool = True
    ) -> Dict[str, Any]:
        """
        05安全师专用: 安全审计代码

        审计维度:
        1. 危险模式检测
        2. 依赖漏洞扫描
        3. 权限提升风险
        4. 网络访问风险
        """
        warnings = []

        # 危险模式检测
        if check_patterns:
            for dp in DANGER_PATTERNS:
                if re.search(dp.pattern, code, re.IGNORECASE):
                    warnings.append({
                        "type": "danger_pattern",
                        "severity": dp.severity,
                        "pattern": dp.pattern,
                        "description": dp.description,
                        "remediation": dp.remediation
                    })

        # 安全审计结果
        result = {
            "audit_status": "completed",
            "code_hash": hashlib.sha256(code.encode()).hexdigest()[:16],
            "danger_warnings": warnings,
            "critical_count": len([w for w in warnings if w["severity"] == "critical"]),
            "high_count": len([w for w in warnings if w["severity"] == "high"]),
            "medium_count": len([w for w in warnings if w["severity"] == "medium"]),
            "low_count": len([w for w in warnings if w["severity"] == "low"]),
            "recommendation": self._get_security_recommendation(warnings),
            "can_execute": len([w for w in warnings if w["severity"] in ["critical"]]) == 0
        }

        # 如果可以执行，在隔离环境中运行
        if result["can_execute"]:
            template = SANDBOX_TEMPLATES["untrusted-code"]
            sandbox_id = self._create_sandbox(template)
            exec_result = self._run_in_sandbox(sandbox_id, code, language, timeout=template.timeout)
            result["execution"] = exec_result.to_dict()

            # 清理沙箱
            self._delete_sandbox(sandbox_id)

        return result

    def _get_security_recommendation(self, warnings: List[Dict]) -> str:
        """根据警告生成安全建议"""
        if not warnings:
            return "Code appears safe for execution"

        critical_count = len([w for w in warnings if w["severity"] == "critical"])

        if critical_count > 0:
            return "BLOCKED: Critical security issues found. Fix before execution."
        elif len([w for w in warnings if w["severity"] == "high"]) > 0:
            return "CAUTION: High severity issues found. Review warnings before execution."
        elif len([w for w in warnings if w["severity"] == "medium"]) > 0:
            return "INFO: Medium severity issues found. Consider addressing warnings."
        else:
            return "PASS: Only low severity informational warnings."

    # =========================================================================
    # 03构建师集成
    # =========================================================================

    def setup_e2b_for_builder_agent(
        self,
        sandbox_type: str = "code-validator"
    ) -> Dict[str, str]:
        """
        为03构建师设置E2B沙箱环境

        使用场景:
        - 第三方库代码验证
        - 开源代码安全测试
        - 跨平台代码测试
        - 依赖冲突检测
        """
        template = SANDBOX_TEMPLATES.get(sandbox_type, SANDBOX_TEMPLATES["code-validator"])

        config = {
            "sandbox_type": sandbox_type,
            "template": template.name,
            "agent": "03构建师",
            "language": template.language,
            "packages": template.packages,
            "tools": template.tools,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        sandbox_id = self._create_sandbox(template)
        config["sandbox_id"] = sandbox_id
        self._active_sandboxes[sandbox_id] = config

        return config

    def validate_code_in_cloud(
        self,
        code: str,
        language: str = "python",
        run_linters: bool = True,
        run_tests: bool = False
    ) -> Dict[str, Any]:
        """
        03构建师专用: 云端代码验证

        验证维度:
        1. 语法检查
        2. 代码格式化检查
        3. 类型检查
        4. 单元测试
        """
        result = {
            "validation_status": "pending",
            "checks": {},
            "overall_result": "pass"
        }

        # 选择验证沙箱
        template = SANDBOX_TEMPLATES["code-validator"]
        sandbox_id = self._create_sandbox(template)

        try:
            # 语法检查
            if language == "python":
                syntax_check = self._check_python_syntax(sandbox_id, code)
                result["checks"]["syntax"] = syntax_check

                if not syntax_check["passed"]:
                    result["overall_result"] = "fail"
                    result["validation_status"] = "failed"
                    return result

            # Linter检查
            if run_linters:
                linter_results = self._run_linters(sandbox_id, code, language)
                result["checks"]["linters"] = linter_results

                if not all(r["passed"] for r in linter_results.values()):
                    result["overall_result"] = "warning"

            result["validation_status"] = "passed"

        finally:
            self._delete_sandbox(sandbox_id)

        return result

    def _check_python_syntax(self, sandbox_id: str, code: str) -> Dict[str, Any]:
        """Python语法检查"""
        check_code = f"""
import ast
import sys

code = {repr(code)}

try:
    ast.parse(code)
    print("SYNTAX_OK")
    sys.exit(0)
except SyntaxError as e:
    print(f"SYNTAX_ERROR: {{e.lineno}}: {{e.msg}}")
    sys.exit(1)
"""
        result = self._run_in_sandbox(sandbox_id, check_code, "python", timeout=10)
        return {
            "passed": result.status == "success" and "SYNTAX_OK" in result.output,
            "output": result.output,
            "error": result.error
        }

    def _run_linters(self, sandbox_id: str, code: str, language: str) -> Dict[str, Any]:
        """运行Linter检查"""
        if language == "python":
            # Black格式化检查
            black_code = f"""
import subprocess
import sys

code = {repr(code)}

# Write to temp file
with open('/tmp/check_code.py', 'w') as f:
    f.write(code)

# Run black --check
result = subprocess.run(
    ['black', '--check', '--diff', '/tmp/check_code.py'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("BLACK:OK")
else:
    print(f"BLACK:NEEDS_FORMAT")
    print(result.stdout)
"""
            result = self._run_in_sandbox(sandbox_id, black_code, "python", timeout=30)

            return {
                "black": {
                    "passed": "BLACK:OK" in result.output,
                    "output": result.output
                }
            }

        return {}

    # =========================================================================
    # 04验证师集成
    # =========================================================================

    def setup_e2b_for_validator_agent(
        self,
        sandbox_type: str = "test-runner"
    ) -> Dict[str, str]:
        """
        为04验证师设置E2B沙箱环境

        使用场景:
        - 隔离测试执行
        - E2E测试运行
        - 回归测试
        - 性能测试
        """
        template = SANDBOX_TEMPLATES.get(sandbox_type, SANDBOX_TEMPLATES["test-runner"])

        config = {
            "sandbox_type": sandbox_type,
            "template": template.name,
            "agent": "04验证师",
            "test_packages": template.packages,
            "tools": template.tools,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }

        sandbox_id = self._create_sandbox(template)
        config["sandbox_id"] = sandbox_id
        self._active_sandboxes[sandbox_id] = config

        return config

    def run_isolated_tests(
        self,
        test_code: str,
        test_framework: str = "pytest",
        coverage: bool = True
    ) -> Dict[str, Any]:
        """
        04验证师专用: 隔离测试执行

        执行维度:
        1. 单元测试执行
        2. 覆盖率统计
        3. 测试报告生成
        4. 失败诊断
        """
        result = {
            "test_status": "pending",
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "coverage": 0.0,
            "test_results": []
        }

        # 选择测试沙箱
        template = SANDBOX_TEMPLATES["test-runner"]
        sandbox_id = self._create_sandbox(template)

        try:
            # 准备测试代码
            if test_framework == "pytest":
                run_code = self._prepare_pytest_code(sandbox_id, test_code, coverage)
            else:
                run_code = test_code

            exec_result = self._run_in_sandbox(sandbox_id, run_code, "python", timeout=template.timeout)

            # 解析测试结果
            parsed = self._parse_test_results(exec_result.output, test_framework)
            result.update(parsed)
            result["test_status"] = "completed"
            result["raw_output"] = exec_result.output
            result["sandbox_id"] = sandbox_id

        except Exception as e:
            result["test_status"] = "error"
            result["error"] = str(e)

        finally:
            # 保持沙箱用于调试
            result["debug_sandbox_id"] = sandbox_id

        return result

    def _prepare_pytest_code(self, sandbox_id: str, test_code: str, coverage: bool) -> str:
        """准备pytest测试代码"""
        base_code = f"""
import subprocess
import sys
import json

test_code = {repr(test_code)}

# Write test file
with open('/tmp/test_code.py', 'w') as f:
    f.write(test_code)

# Build pytest command
cmd = ['pytest', '/tmp/test_code.py', '-v', '--tb=short', '--no-header']
if {coverage}:
    cmd.extend(['--cov=.', '--cov-report=json:/tmp/coverage.json'])

result = subprocess.run(cmd, capture_output=True, text=True)

print("STDOUT:")
print(result.stdout)
print("\\nSTDERR:")
print(result.stderr)
print(f"\\nRETURN_CODE:{{result.returncode}}")
"""

        return base_code

    def _parse_test_results(self, output: str, framework: str) -> Dict[str, Any]:
        """解析测试结果"""
        parsed = {
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "test_results": []
        }

        if framework == "pytest":
            # 简单的正则解析
            passed = len(re.findall(r"PASSED", output))
            failed = len(re.findall(r"FAILED", output))
            errors = len(re.findall(r"ERROR", output))

            parsed["passed"] = passed
            parsed["failed"] = failed
            parsed["errors"] = errors
            parsed["total"] = passed + failed + errors

            # 提取失败的测试详情
            for match in re.finditer(r"FAILED (.*?) - (.*?)(?=\n|$)", output):
                parsed["test_results"].append({
                    "test": match.group(1),
                    "error": match.group(2)
                })

        return parsed

    # =========================================================================
    # 与NeMoClaw对比
    # =========================================================================

    def compare_with_nemoclaw(self) -> Dict[str, Any]:
        """
        比较E2B与NeMoClaw的能力差异

        E2B深度研究结论:
        - E2B: 云端托管，启动~500ms，适合快速验证
        - NeMoClaw: 本地Landlock隔离，适合高安全场景
        """
        comparison = {
            "e2b": {
                "deployment": "cloud",
                "isolation": "vm-level",
                "startup_time": "~500ms",
                "cost": "per-use",
                "network": "configurable",
                "security_audit": "easy",
                "use_cases": [
                    "快速代码验证",
                    "依赖测试",
                    "跨环境测试",
                    "临时研究环境"
                ]
            },
            "nemoclaw": {
                "deployment": "local",
                "isolation": "kernel-level (Landlock+seccomp)",
                "startup_time": "instant",
                "cost": "self-hosted",
                "network": "policy-based",
                "security_audit": "manual",
                "use_cases": [
                    "高安全敏感代码",
                    "生产环境前验证",
                    "持续集成",
                    "合规要求严格场景"
                ]
            },
            "recommendation": {
                "quick_validation": "E2B",
                "high_security": "NeMoClaw",
                "cost_sensitive": "NeMoClaw",
                "prototype_testing": "E2B",
                "ci_cd_pipeline": "NeMoClaw"
            }
        }

        return comparison

    # =========================================================================
    # 内部方法
    # =========================================================================

    def _create_sandbox(self, template: SandboxTemplate) -> str:
        """创建沙箱"""
        # 实际调用E2B API
        # 这里使用模拟实现
        sandbox_id = f"sandbox_{int(time.time())}_{hashlib.md5(template.name.encode()).hexdigest()[:8]}"

        self._active_sandboxes[sandbox_id] = {
            "template": template.name,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "agent": template.agent_type.value
        }

        return sandbox_id

    def _run_in_sandbox(
        self,
        sandbox_id: str,
        code: str,
        language: str = "python",
        timeout: int = 60
    ) -> ExecutionResult:
        """在沙箱中运行代码"""
        start_time = time.time()

        # 实际调用E2B API执行
        # 这里使用模拟实现
        result = ExecutionResult(
            status="success",
            output=f"[Simulated] Executed {language} code in sandbox {sandbox_id}",
            execution_time=time.time() - start_time,
            sandbox_id=sandbox_id,
            template=sandbox_id,
            agent_type=AgentType.BUILDER
        )

        self._execution_history.append(result.to_dict())

        return result

    def _delete_sandbox(self, sandbox_id: str) -> bool:
        """删除沙箱"""
        if sandbox_id in self._active_sandboxes:
            del self._active_sandboxes[sandbox_id]
            return True
        return False

    def cleanup_all(self) -> int:
        """清理所有沙箱"""
        count = 0
        for sandbox_id in list(self._active_sandboxes.keys()):
            if self._delete_sandbox(sandbox_id):
                count += 1
        return count

    def get_active_sandboxes(self) -> List[Dict]:
        """获取活跃沙箱列表"""
        return list(self._active_sandboxes.values())

    def get_execution_history(self) -> List[Dict]:
        """获取执行历史"""
        return self._execution_history

    def generate_report(self) -> Dict[str, Any]:
        """生成集成报告"""
        return {
            "integrator_version": "1.0",
            "e2b_config": {
                "api_key_set": bool(self.api_key),
                "base_url": self.config.base_url,
                "default_timeout": self.config.default_timeout
            },
            "active_sandboxes": len(self._active_sandboxes),
            "execution_count": len(self._execution_history),
            "templates": list(SANDBOX_TEMPLATES.keys()),
            "danger_patterns_count": len(DANGER_PATTERNS),
            "comparison": self.compare_with_nemoclaw()
        }

# ============================================================================
# CLI入口
# ============================================================================

def main():
    """命令行入口"""
    import argparse

    parser = argparse.ArgumentParser(
        description="E2B Deep Integrator - 天龙引擎专用云沙箱集成"
    )

    subparsers = parser.add_subparsers(dest="command", help="命令")

    # setup命令
    setup_parser = subparsers.add_parser("setup", help="设置沙箱环境")
    setup_parser.add_argument(
        "--agent",
        choices=["05", "03", "04", "01"],
        required=True,
        help="天龙Agent类型"
    )
    setup_parser.add_argument(
        "--type",
        default="default",
        help="沙箱类型"
    )

    # audit命令
    audit_parser = subparsers.add_parser("audit", help="05安全师: 安全审计代码")
    audit_parser.add_argument("--code", required=True, help="待审计代码")
    audit_parser.add_argument("--lang", default="python", help="语言")

    # validate命令
    validate_parser = subparsers.add_parser("validate", help="03构建师: 代码验证")
    validate_parser.add_argument("--code", required=True, help="待验证代码")
    validate_parser.add_argument("--lang", default="python", help="语言")

    # test命令
    test_parser = subparsers.add_parser("test", help="04验证师: 隔离测试")
    test_parser.add_argument("--code", required=True, help="测试代码")
    test_parser.add_argument("--framework", default="pytest", help="测试框架")

    # compare命令
    subparsers.add_parser("compare", help="E2B vs NeMoClaw对比")

    # report命令
    subparsers.add_parser("report", help="生成集成报告")

    # list命令
    subparsers.add_parser("list", help="列出活跃沙箱")

    args = parser.parse_args()

    integrator = E2BDeepIntegrator()

    if args.command == "setup":
        agent_map = {
            "05": ("security-audit", AgentType.SECURITY),
            "03": ("code-validator", AgentType.BUILDER),
            "04": ("test-runner", AgentType.VALIDATOR),
            "01": ("research", AgentType.RESEARCHER)
        }
        template_name, agent = agent_map.get(args.agent, ("code-validator", AgentType.BUILDER))

        if args.agent == "05":
            result = integrator.setup_e2b_for_security_agent(args.type)
        elif args.agent == "03":
            result = integrator.setup_e2b_for_builder_agent(args.type)
        elif args.agent == "04":
            result = integrator.setup_e2b_for_validator_agent(args.type)
        else:
            result = integrator.setup_e2b_for_builder_agent(args.type)

        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "audit":
        result = integrator.security_audit_code(args.code, args.lang)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "validate":
        result = integrator.validate_code_in_cloud(args.code, args.lang)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "test":
        result = integrator.run_isolated_tests(args.code, args.framework)
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "compare":
        result = integrator.compare_with_nemoclaw()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "report":
        result = integrator.generate_report()
        print(json.dumps(result, indent=2, ensure_ascii=False))

    elif args.command == "list":
        sandboxes = integrator.get_active_sandboxes()
        print(f"Active sandboxes: {len(sandboxes)}")
        for s in sandboxes:
            print(f"  - {s}")

    else:
        parser.print_help()

if __name__ == "__main__":
    main()
