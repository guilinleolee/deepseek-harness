#!/usr/bin/env python3
"""
permission_checker.py - 权限检查器
基于 IM 用户的角色控制 Claude Code 操作权限
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class Permission(Enum):
    SESSION_CREATE = "session_create"    # 创建会话
    CODE_EXECUTE = "code_execute"         # 执行代码
    FILE_WRITE = "file_write"             # 写入文件
    DANGEROUS = "dangerous"               # 危险操作
    COMMAND_RUN = "command_run"            # 运行命令
    SESSION_READ = "session_read"         # 查看会话
    SESSION_CANCEL = "session_cancel"    # 取消会话
    LOGS_VIEW = "logs_view"              # 查看日志
    ADMIN = "admin"                      # 管理员操作


class Role(Enum):
    ADMIN = "admin"          # 完全权限
    USER = "user"             # 普通用户
    READONLY = "readonly"     # 只读
    BLOCKED = "blocked"       # 被封禁


@dataclass
class PermissionMatrix:
    """权限矩阵定义"""
    role: Role
    permissions: set[Permission]


# 权限矩阵
ROLE_PERMISSIONS = {
    Role.ADMIN: {
        Permission.SESSION_CREATE,
        Permission.CODE_EXECUTE,
        Permission.FILE_WRITE,
        Permission.DANGEROUS,
        Permission.COMMAND_RUN,
        Permission.SESSION_READ,
        Permission.SESSION_CANCEL,
        Permission.LOGS_VIEW,
        Permission.ADMIN,
    },
    Role.USER: {
        Permission.SESSION_CREATE,
        Permission.CODE_EXECUTE,
        Permission.FILE_WRITE,
        Permission.SESSION_READ,
        Permission.SESSION_CANCEL,
        Permission.LOGS_VIEW,
    },
    Role.READONLY: {
        Permission.SESSION_READ,
        Permission.LOGS_VIEW,
    },
    Role.BLOCKED: set(),
}


@dataclass
class PermissionCheckResult:
    """权限检查结果"""
    allowed: bool
    role: Role
    permission: Permission
    reason: Optional[str] = None


class PermissionChecker:
    """权限检查器"""

    def __init__(self):
        self.user_roles: dict[str, Role] = {}  # user_id -> role

    def set_user_role(self, user_id: str, role: Role):
        """设置用户角色"""
        self.user_roles[user_id] = role

    def get_user_role(self, user_id: str) -> Role:
        """获取用户角色"""
        return self.user_roles.get(user_id, Role.READONLY)

    def check(self, user_id: str, permission: Permission) -> PermissionCheckResult:
        """检查用户是否拥有指定权限"""
        role = self.get_user_role(user_id)
        allowed = permission in ROLE_PERMISSIONS.get(role, set())

        if allowed:
            return PermissionCheckResult(allowed=True, role=role, permission=permission)
        else:
            reason = self._get_denial_reason(role, permission)
            return PermissionCheckResult(allowed=False, role=role, permission=permission, reason=reason)

    def _get_denial_reason(self, role: Role, permission: Permission) -> str:
        """获取拒绝原因"""
        reasons = {
            (Role.READONLY, Permission.SESSION_CREATE): "只读用户不能创建会话",
            (Role.READONLY, Permission.CODE_EXECUTE): "只读用户不能执行代码",
            (Role.READONLY, Permission.FILE_WRITE): "只读用户不能写入文件",
            (Role.READONLY, Permission.COMMAND_RUN): "只读用户不能运行命令",
            (Role.READONLY, Permission.SESSION_CANCEL): "只读用户不能取消会话",
            (Role.READONLY, Permission.DANGEROUS): "只读用户不能执行危险操作",
            (Role.BLOCKED, Permission.SESSION_READ): "被封禁用户不能查看会话",
            (Role.BLOCKED, Permission.LOGS_VIEW): "被封禁用户不能查看日志",
            (Role.USER, Permission.DANGEROUS): "需要管理员权限执行危险操作",
            (Role.USER, Permission.ADMIN): "需要超级管理员权限",
        }
        return reasons.get((role, permission), f"权限不足: {role.value} 不能 {permission.value}")

    def check_or_raise(self, user_id: str, permission: Permission):
        """检查权限，不通过则抛出异常"""
        result = self.check(user_id, permission)
        if not result.allowed:
            raise PermissionDeniedError(result.reason or "权限不足", result.role, permission)
        return True

    def get_role_permissions(self, user_id: str) -> set[Permission]:
        """获取用户所有权限"""
        role = self.get_user_role(user_id)
        return ROLE_PERMISSIONS.get(role, set()).copy()

    def list_user_permissions(self, user_id: str) -> list[str]:
        """列出用户所有权限"""
        perms = self.get_role_permissions(user_id)
        return [p.value for p in perms]


class PermissionDeniedError(Exception):
    """权限被拒绝异常"""

    def __init__(self, message: str, role: Role, permission: Permission):
        super().__init__(message)
        self.role = role
        self.permission = permission


# ============ 便捷函数 ============
_checker = PermissionChecker()


def check_permission(user_id: str, permission: Permission) -> bool:
    """快速权限检查"""
    return _checker.check(user_id, permission).allowed


def require_permission(user_id: str, permission: Permission):
    """要求权限，不通过则抛出异常"""
    _checker.check_or_raise(user_id, permission)


def set_user_role(user_id: str, role: str):
    """设置用户角色"""
    try:
        _checker.set_user_role(user_id, Role(role))
    except ValueError:
        raise ValueError(f"无效角色: {role}")


def get_user_role(user_id: str) -> str:
    """获取用户角色"""
    return _checker.get_user_role(user_id).value


def list_permissions(user_id: str) -> list[str]:
    """列出用户权限"""
    return _checker.list_user_permissions(user_id)
