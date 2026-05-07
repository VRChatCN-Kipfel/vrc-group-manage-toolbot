import asyncio

from .vrc_client import VRCClient
from .vrc_config import VRCConfig


_vrc_client: VRCClient = None
_lock: asyncio.Lock = None


def _get_lock():
    global _lock
    if _lock is None:
        _lock = asyncio.Lock()
    return _lock


def get_vrc_client() -> VRCClient:
    global _vrc_client
    if _vrc_client is None:
        _vrc_client = VRCClient(VRCConfig.from_env())
    return _vrc_client


async def get_vrc_client_safe() -> VRCClient:
    global _vrc_client
    if _vrc_client is None:
        async with _get_lock():
            if _vrc_client is None:
                _vrc_client = VRCClient(VRCConfig.from_env())
    return _vrc_client


__all__ = [
    "VRCClient", "VRCConfig",
    "User", "Instance", "Group", "World",
    "GroupMember", "GroupRole", "Announcement", "JoinRequest", "AuditLogEntry",
    "get_vrc_client",
]
