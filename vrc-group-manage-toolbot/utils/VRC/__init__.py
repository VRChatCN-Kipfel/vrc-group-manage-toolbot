from .vrc_client import VRCClient
from .vrc_config import VRCConfig
from .vrc_models import (
    User, Instance, Group, World,
    GroupMember, GroupRole, Announcement, JoinRequest, AuditLogEntry,
)

_vrc_client: VRCClient = None


def get_vrc_client() -> VRCClient:
    global _vrc_client
    if _vrc_client is None:
        config = VRCConfig.from_env()
        _vrc_client = VRCClient(config)
    return _vrc_client


__all__ = [
    "VRCClient", "VRCConfig",
    "User", "Instance", "Group", "World",
    "GroupMember", "GroupRole", "Announcement", "JoinRequest", "AuditLogEntry",
    "get_vrc_client",
]
