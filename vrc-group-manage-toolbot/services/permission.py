from enum import IntEnum
from typing import TYPE_CHECKING

from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent

if TYPE_CHECKING:
    from utils import VRCClient


class PermissionLevel(IntEnum):
    USER = 0
    GROUP_ADMIN = 1
    SUPERUSER = 2


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
