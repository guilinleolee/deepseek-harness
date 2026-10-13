"""
配置管理模块
化学视角：配置是催化剂，影响反应速率和方向
"""

import os
import json
from dataclasses import dataclass, field, asdict
from typing import Optional, List
from pathlib import Path
from utils.path_security import validate_cache_path


# 默认User-Agent池（模拟真实浏览器）
DEFAULT_USER_AGENTS = [
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.47(0x18002f2f) NetType/WIFI Language/zh_CN",
    "Mozilla/5.0 (Linux; Android 13; SM-S908B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 MicroMessenger/8.0.47(0x28002f31) NetType/WIFI Language/zh_CN",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 NetType/WIFI",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]


@dataclass
class Config:
    """全局配置对象

    设计原则：
    - 默认值优先：开箱即用
    - 可覆盖性：支持环境变量和配置文件
    - 类型安全：使用dataclass确保类型正确
    """

    # 缓存配置
    cache_enabled: bool = True
    cache_path: str = "./cache/articles.db"
    cache_ttl_days: int = 30
    l1_cache_size: int = 100

    def __post_init__(self):
        """初始化后验证缓存路径"""
        # 验证缓存路径合法性
        try:
            validated_path = validate_cache_path(self.cache_path)
            self.cache_path = str(validated_path)
        except ValueError as e:
            # 使用默认路径
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"缓存路径验证失败: {e}，使用默认路径")
            self.cache_path = "./cache/articles.db"

    # 网络配置
    timeout: int = 30
    retry_times: int = 3
    retry_delay: float = 2.0
    request_interval: float = 3.0

    # 降级配置
    api_key: Optional[str] = None
    api_endpoint: str = "https://down.mptext.top"

    # User-Agent配置
    user_agents: List[str] = field(default_factory=lambda: DEFAULT_USER_AGENTS[:])

    # 日志配置
    log_level: str = "INFO"
    log_file: Optional[str] = None

    # 其他配置
    verify_ssl: bool = True
    max_concurrent: int = 3
    enable_fallback: bool = True

    @classmethod
    def from_file(cls, path: str) -> 'Config':
        """从配置文件加载

        Args:
            path: 配置文件路径（.json或.yaml）

        Returns:
            Config对象
        """
        path_obj = Path(path)

        if not path_obj.exists():
            return cls()

        if path_obj.suffix == '.json':
            with open(path_obj, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return cls(**data)
        # TODO: 支持YAML格式
        else:
            raise ValueError(f"Unsupported config format: {path_obj.suffix}")

    def to_file(self, path: str) -> None:
        """保存配置到文件

        Args:
            path: 配置文件路径
        """
        path_obj = Path(path)
        path_obj.parent.mkdir(parents=True, exist_ok=True)

        if path_obj.suffix == '.json':
            with open(path_obj, 'w', encoding='utf-8') as f:
                json.dump(asdict(self), f, ensure_ascii=False, indent=2)
        else:
            raise ValueError(f"Unsupported config format: {path_obj.suffix}")

    @classmethod
    def from_env(cls) -> 'Config':
        """从环境变量加载配置

        环境变量命名规则：WECHAT_{配置名大写}
        例如：WECHAT_CACHE_PATH, WECHAT_TIMEOUT
        """
        config = cls()

        # 缓存配置
        if 'WECHAT_CACHE_PATH' in os.environ:
            config.cache_path = os.environ['WECHAT_CACHE_PATH']
        if 'WECHAT_CACHE_TTL_DAYS' in os.environ:
            config.cache_ttl_days = int(os.environ['WECHAT_CACHE_TTL_DAYS'])
        if 'WECHAT_CACHE_ENABLED' in os.environ:
            config.cache_enabled = os.environ['WECHAT_CACHE_ENABLED'].lower() == 'true'

        # 网络配置
        if 'WECHAT_TIMEOUT' in os.environ:
            config.timeout = int(os.environ['WECHAT_TIMEOUT'])
        if 'WECHAT_RETRY_TIMES' in os.environ:
            config.retry_times = int(os.environ['WECHAT_RETRY_TIMES'])

        # 降级配置
        if 'WECHAT_API_KEY' in os.environ:
            config.api_key = os.environ['WECHAT_API_KEY']
        if 'WECHAT_API_ENDPOINT' in os.environ:
            config.api_endpoint = os.environ['WECHAT_API_ENDPOINT']

        return config

    def get_user_agent(self) -> str:
        """随机获取一个User-Agent"""
        import random
        return random.choice(self.user_agents)


# 全局默认配置实例
_default_config: Optional[Config] = None


def get_default_config() -> Config:
    """获取全局默认配置

    Returns:
        Config: 全局配置对象（单例）
    """
    global _default_config
    if _default_config is None:
        _default_config = Config.from_env()
    return _default_config


def set_default_config(config: Config) -> None:
    """设置全局默认配置

    Args:
        config: 新的配置对象
    """
    global _default_config
    _default_config = config
