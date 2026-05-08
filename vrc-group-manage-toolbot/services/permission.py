from enum import IntEnum
from typing import TYPE_CHECKING, Optional

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

if TYPE_CHECKING:
    from utils import VRCClient


class PermissionLevel(IntEnum):
    UNBOUND_USER = 0      # 未绑定普通成员
    BOUND_USER = 1        # 已绑定普通成员
    UNBOUND_ADMIN = 2     # 未绑定管理员
    BOUND_ADMIN = 3       # 已绑定管理员
    OWNER = 4             # 群主
    SUPERUSER = 5         # 机器人超级管理员
    
    @classmethod
    def from_str(cls, level_str: str) -> "PermissionLevel":
        """从字符串转换为权限等级"""
        mapping = {
            "unbound_user": cls.UNBOUND_USER, "0": cls.UNBOUND_USER,
            "bound_user": cls.BOUND_USER, "1": cls.BOUND_USER,
            "unbound_admin": cls.UNBOUND_ADMIN, "2": cls.UNBOUND_ADMIN,
            "bound_admin": cls.BOUND_ADMIN, "3": cls.BOUND_ADMIN,
            "owner": cls.OWNER, "4": cls.OWNER,
            "superuser": cls.SUPERUSER, "5": cls.SUPERUSER,
        }
        return mapping.get(level_str.lower(), cls.UNBOUND_USER)


async def get_permission_level(bot: Bot, event: GroupMessageEvent) -> PermissionLevel:
    from .user_binding import user_binding_store
    
    user_id = event.user_id
    sender = event.sender
    qq_id = str(user_id)
    
    # 1. 检查是否为机器人超管 (Lv5)
    if qq_id in bot.config.superusers:
        return PermissionLevel.SUPERUSER
    
    # 2. 检查是否为群主 (Lv4)
    if sender.role == "owner":
        return PermissionLevel.OWNER
    
    # 3. 检查是否为管理员 (Lv2 or Lv3)
    if sender.role == "admin":
        # 检查是否已绑定
        binding = user_binding_store.get_by_qq(qq_id)
        if binding and binding.confirmed:
            return PermissionLevel.BOUND_ADMIN
        else:
            return PermissionLevel.UNBOUND_ADMIN
    
    # 4. 检查普通成员 (Lv0 or Lv1)
    binding = user_binding_store.get_by_qq(qq_id)
    if binding and binding.confirmed:
        return PermissionLevel.BOUND_USER
    else:
        return PermissionLevel.UNBOUND_USER


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
            PermissionLevel.UNBOUND_USER: "未绑定成员",
            PermissionLevel.BOUND_USER: "已绑定成员",
            PermissionLevel.UNBOUND_ADMIN: "未绑定管理员",
            PermissionLevel.BOUND_ADMIN: "已绑定管理员",
            PermissionLevel.OWNER: "群主",
            PermissionLevel.SUPERUSER: "超级管理员",
        }
        return False, f"❌ 权限不足：需要{level_names.get(required_level, '未知')}权限"
    
    return True, ""
