from enum import IntEnum
from typing import TYPE_CHECKING, Optional

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

if TYPE_CHECKING:
    from utils import VRCClient


class PermissionLevel(IntEnum):
    USER = 0
    GROUP_ADMIN = 1
    SUPERUSER = 2
    
    @classmethod
    def from_str(cls, level_str: str) -> "PermissionLevel":
        """从字符串转换为权限等级"""
        mapping = {
            "user": cls.USER,
            "admin": cls.GROUP_ADMIN,
            "superuser": cls.SUPERUSER,
            "0": cls.USER,
            "1": cls.GROUP_ADMIN,
            "2": cls.SUPERUSER,
        }
        return mapping.get(level_str.lower(), cls.USER)


async def get_permission_level(bot: Bot, event: GroupMessageEvent) -> PermissionLevel:
    user_id = event.user_id

    if str(user_id) in bot.config.superusers:
        return PermissionLevel.SUPERUSER

    sender = event.sender
    if sender.role in ("admin", "owner"):
        return PermissionLevel.GROUP_ADMIN

    return PermissionLevel.USER


async def check_vrc_group_role(
    vrc_client: "VRCClient",
    user_id: str,
    group_id: str,
    required_roles: list = None,
) -> bool:
    if required_roles is None:
        required_roles = ["owner", "moderator"]

    try:
        member = await vrc_client.get_group_member(group_id, user_id)
        if not member or not member.roleIds:
            return False

        roles = await vrc_client.get_group_roles(group_id)
        role_map = {r.id: r for r in roles}

        for role_id in member.roleIds:
            role = role_map.get(role_id)
            if role and role.name.lower() in required_roles:
                return True
        return False
    except Exception:
        return False


async def check_command_permission(
    bot: Bot,
    event: GroupMessageEvent,
    command_name: str,
    required_level: Optional[PermissionLevel] = None,
) -> tuple[bool, str]:
    """
    检查用户是否有权限执行指定命令
    
    Args:
        bot: Bot实例
        event: 事件对象
        command_name: 命令名称
        required_level: 要求的最低权限等级（如果为None则从配置中读取）
    
    Returns:
        (是否有权限, 错误消息)
    """
    from .group_config import group_config_store
    
    # 获取当前群的配置
    config = group_config_store.get(str(event.group_id))
    
    # 获取用户的权限等级
    user_level = await get_permission_level(bot, event)
    
    # 如果未指定required_level，从配置中读取
    if required_level is None:
        required_level = config.get_command_permission(command_name)
    
    # 检查功能是否启用
    if not config.is_command_enabled(command_name):
        return False, f"❌ 命令 #{command_name} 在此群已被禁用"
    
    # 检查权限等级
    if user_level < required_level:
        level_names = {
            PermissionLevel.USER: "普通用户",
            PermissionLevel.GROUP_ADMIN: "群管理员",
            PermissionLevel.SUPERUSER: "超级管理员",
        }
        return False, f"❌ 权限不足：需要{level_names.get(required_level, '未知')}权限"
    
    return True, ""
