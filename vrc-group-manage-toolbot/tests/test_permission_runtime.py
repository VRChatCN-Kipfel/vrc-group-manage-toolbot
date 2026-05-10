from unittest.mock import MagicMock, AsyncMock

import pytest

from services.permission import (
    PermissionLevel, get_permission_level, check_command_permission, _temp_permissions,
)
from services.user_binding import BindingRecord, user_binding_store
from services.group_config import group_config_store


# ── _extract_at_qq tests ──

def test_extract_at_cq_format():
    from plugins.config_manager import _extract_at_qq
    event = MagicMock()
    event.raw_message = "你好 [CQ:at,qq=123456] 测试"
    event.get_message.return_value = []
    result = _extract_at_qq(event)
    assert result == "123456"


def test_extract_at_napcat_format():
    from plugins.config_manager import _extract_at_qq
    event = MagicMock()
    event.raw_message = "你好 [at:qq=789012] 测试"
    event.get_message.return_value = []
    result = _extract_at_qq(event)
    assert result == "789012"


def test_extract_at_segment_fallback():
    from plugins.config_manager import _extract_at_qq
    event = MagicMock()
    event.raw_message = "普通文本"
    seg = MagicMock()
    seg.type = "at"
    seg.data = {"qq": "345678"}
    event.get_message.return_value = [seg]
    result = _extract_at_qq(event)
    assert result == "345678"


def test_extract_at_all_ignored():
    from plugins.config_manager import _extract_at_qq
    event = MagicMock()
    event.raw_message = "[CQ:at,qq=all]"
    event.get_message.return_value = []
    result = _extract_at_qq(event)
    assert result is None


def test_extract_at_no_at():
    from plugins.config_manager import _extract_at_qq
    event = MagicMock()
    event.raw_message = "普通文本 无任何 at"
    event.get_message.return_value = []
    result = _extract_at_qq(event)
    assert result is None


# ── permission runtime tests ──

@pytest.mark.asyncio
async def test_get_permission_level_superuser(nonebot_init):
    bot = MagicMock()
    bot.config.superusers = {"super_qq_001", "another_user"}
    event = MagicMock()
    event.user_id = "super_qq_001"
    event.sender.role = "member"

    _temp_permissions.clear()

    level = await get_permission_level(bot, event)
    assert level == PermissionLevel.SUPERUSER


@pytest.mark.asyncio
async def test_get_permission_level_temp(nonebot_init):
    bot = MagicMock()
    bot.config.superusers = set()
    event = MagicMock()
    event.user_id = "temp_qq_001"
    event.sender.role = "member"

    _temp_permissions.clear()
    _temp_permissions["temp_qq_001"] = PermissionLevel.BOUND_ADMIN

    level = await get_permission_level(bot, event)
    assert level == PermissionLevel.BOUND_ADMIN

    _temp_permissions.clear()


@pytest.mark.asyncio
async def test_get_permission_level_owner(nonebot_init):
    bot = MagicMock()
    bot.config.superusers = set()
    event = MagicMock()
    event.user_id = "owner_qq_001"
    event.sender.role = "owner"

    _temp_permissions.clear()

    level = await get_permission_level(bot, event)
    assert level == PermissionLevel.OWNER


@pytest.mark.asyncio
async def test_get_permission_level_private_talk_bound(nonebot_init):
    from nonebot.adapters.onebot.v11 import PrivateMessageEvent

    bot = MagicMock()
    bot.config.superusers = set()
    event = PrivateMessageEvent(
        time=123456,
        self_id=111111,
        post_type="message",
        message_type="private",
        sub_type="friend",
        message_id=1,
        user_id=12345,
        message="test",
        original_message="test",
        raw_message="test",
        font=0,
        sender={"user_id": 12345, "nickname": "test"},
    )

    user_binding_store.set(BindingRecord(
        qq_id="12345",
        vrc_user_id="usr_bound_test",
        vrc_display_name="测试用户",
        bound_at=123456.0,
        confirmed=True,
    ))

    _temp_permissions.clear()

    level = await get_permission_level(bot, event)
    assert level == PermissionLevel.BOUND_USER

    user_binding_store.remove("12345")


@pytest.mark.asyncio
async def test_get_permission_level_private_talk_unbound(nonebot_init):
    from nonebot.adapters.onebot.v11 import PrivateMessageEvent

    bot = MagicMock()
    bot.config.superusers = set()
    event = PrivateMessageEvent(
        time=123456,
        self_id=111111,
        post_type="message",
        message_type="private",
        sub_type="friend",
        message_id=1,
        user_id=99999,
        message="test",
        original_message="test",
        raw_message="test",
        font=0,
        sender={"user_id": 99999, "nickname": "test"},
    )

    _temp_permissions.clear()

    level = await get_permission_level(bot, event)
    assert level == PermissionLevel.UNBOUND_USER


@pytest.mark.asyncio
async def test_check_command_permission_private_talk(nonebot_init):
    bot = MagicMock()
    bot.config.superusers = set()
    event = MagicMock()
    event.group_id = 99999999
    event.user_id = 12345
    event.sender = MagicMock()
    event.sender.role = "member"

    from services.permission import check_command_permission
    result = await check_command_permission(bot, event, "whereis")
    assert isinstance(result, tuple)
    assert len(result) == 2
    assert isinstance(result[0], bool)
    assert isinstance(result[1], str)


@pytest.mark.asyncio
async def test_check_command_permission_group_disabled(nonebot_init):
    bot = MagicMock()
    bot.config.superusers = {"admin_qq"}
    event = MagicMock()
    event.group_id = 88888888
    event.user_id = "admin_qq"
    event.sender = MagicMock()
    event.sender.role = "member"

    _temp_permissions.clear()

    config = group_config_store.get(str(event.group_id))
    config.set_command_enabled("gban", False)
    group_config_store.set(config)

    has_perm, msg = await check_command_permission(bot, event, "gban")
    assert has_perm == False
    assert "已被禁用" in msg or "禁用" in msg

    config.commands.clear()
    group_config_store.set(config)


@pytest.mark.asyncio
async def test_get_permission_level_admin_bound(nonebot_init):
    from services.user_binding import BindingRecord

    bot = MagicMock()
    bot.config.superusers = set()
    event = MagicMock()
    event.user_id = "admin_qq_001"
    event.sender = MagicMock()
    event.sender.role = "admin"

    user_binding_store.set(BindingRecord(
        qq_id="admin_qq_001",
        vrc_user_id="usr_admin_bound",
        vrc_display_name="管理员",
        bound_at=123456.0,
        confirmed=True,
    ))

    _temp_permissions.clear()

    level = await get_permission_level(bot, event)
    assert level == PermissionLevel.BOUND_ADMIN

    user_binding_store.remove("admin_qq_001")


@pytest.mark.asyncio
async def test_get_permission_level_admin_unbound(nonebot_init):
    bot = MagicMock()
    bot.config.superusers = set()
    event = MagicMock()
    event.user_id = "admin_qq_002"
    event.sender = MagicMock()
    event.sender.role = "admin"

    _temp_permissions.clear()

    level = await get_permission_level(bot, event)
    assert level == PermissionLevel.UNBOUND_ADMIN


@pytest.mark.asyncio
async def test_check_vrc_group_role_has_role(nonebot_init):
    from services.permission import check_vrc_group_role
    from utils.VRC.vrc_models import GroupMember, GroupRole

    vrc_client = MagicMock()
    member = GroupMember(id="mem_1", groupId="grp_x", userId="usr_x", roleIds=["role_1"])
    vrc_client.get_group_member = AsyncMock(return_value=member)
    roles = [GroupRole(id="role_1", name="moderator")]
    vrc_client.get_group_roles = AsyncMock(return_value=roles)

    result = await check_vrc_group_role(vrc_client, "usr_x", "grp_x")
    assert result == True


@pytest.mark.asyncio
async def test_check_vrc_group_role_no_match(nonebot_init):
    from services.permission import check_vrc_group_role
    from utils.VRC.vrc_models import GroupMember, GroupRole

    vrc_client = MagicMock()
    member = GroupMember(id="mem_1", groupId="grp_x", userId="usr_x", roleIds=["role_2"])
    vrc_client.get_group_member = AsyncMock(return_value=member)
    roles = [GroupRole(id="role_2", name="member")]
    vrc_client.get_group_roles = AsyncMock(return_value=roles)

    result = await check_vrc_group_role(vrc_client, "usr_x", "grp_x")
    assert result == False


@pytest.mark.asyncio
async def test_check_vrc_group_role_no_member(nonebot_init):
    from services.permission import check_vrc_group_role

    vrc_client = MagicMock()
    vrc_client.get_group_member = AsyncMock(return_value=None)
    vrc_client.get_group_roles = AsyncMock(return_value=[])

    result = await check_vrc_group_role(vrc_client, "usr_x", "grp_x")
    assert result == False


@pytest.mark.asyncio
async def test_check_vrc_group_role_exception(nonebot_init):
    from services.permission import check_vrc_group_role

    vrc_client = MagicMock()
    vrc_client.get_group_member = AsyncMock(side_effect=Exception("API down"))

    result = await check_vrc_group_role(vrc_client, "usr_x", "grp_x")
    assert result == False


@pytest.mark.asyncio
async def test_check_command_permission_insufficient_level(nonebot_init):
    bot = MagicMock()
    bot.config.superusers = set()
    event = MagicMock()
    event.group_id = 99999999
    event.user_id = "low_level_user"
    event.sender = MagicMock()
    event.sender.role = "member"

    _temp_permissions.clear()

    config = group_config_store.get(str(event.group_id))
    config.set_command_enabled("gban", True)
    config.set_command_permission("gban", PermissionLevel.SUPERUSER)
    group_config_store.set(config)

    has_perm, msg = await check_command_permission(bot, event, "gban")
    assert has_perm == False
    assert "权限不足" in msg

    config.commands.clear()
    group_config_store.set(config)
