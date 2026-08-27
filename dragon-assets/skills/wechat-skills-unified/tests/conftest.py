"""
pytest配置文件 - 修复导入问题
"""

import sys
from pathlib import Path

# 将项目根目录添加到sys.path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


# 启用测试模式（允许临时目录路径）
def pytest_configure(config):
    """pytest配置钩子"""
    from utils.path_security import set_test_mode
    set_test_mode(True)
