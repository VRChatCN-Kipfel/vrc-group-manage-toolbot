"""
工具模块包
"""

from .VRC import (
    VRCClient, VRCConfig, get_vrc_client,
)
from .VRC.vrc_models import (
    User, Instance, Group, World,
    GroupMember, GroupRole, Announcement, JoinRequest, AuditLogEntry,
)


def check_vrc_auth(client: VRCClient) -> str | None:
    if not client.config.auth_cookie:
        return "⚠️ 尚未登录 VRChat API\n请先使用 #vrclLogin 或 #vrclLogin cookie=xxx"
    return None


async def ensure_vrc_auth(matcher, client: VRCClient):
    err = check_vrc_auth(client)
    if err:
        await matcher.finish(err)


__all__ = [
    "VRCClient", "VRCConfig",
    "User", "Instance", "Group", "World",
    "GroupMember", "GroupRole", "Announcement", "JoinRequest", "AuditLogEntry",
    "get_vrc_client",
    "check_vrc_auth",
    "ensure_vrc_auth",
]
