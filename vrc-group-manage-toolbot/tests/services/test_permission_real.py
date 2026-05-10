"""
权限服务测试 - 实测试

测试权限检查、权限级别转换等功能
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from nonebug import App
from tests import create_mock_bot, get_test_group_id, get_test_user_id


class TestPermissionReal:
    """权限服务实测试"""
    
    @pytest.mark.asyncio
    async def test_permission_level_enum(self, app: App):
        """
        实测试：权限级别枚举
        
        验证所有权限级别都正确定义
        """
        from services.permission import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证所有权限级别存在
        assert hasattr(PermissionLevel, 'UNBOUND_USER')
        assert hasattr(PermissionLevel, 'BOUND_USER')
        assert hasattr(PermissionLevel, 'UNBOUND_ADMIN')
        assert hasattr(PermissionLevel, 'BOUND_ADMIN')
        assert hasattr(PermissionLevel, 'OWNER')
        assert hasattr(PermissionLevel, 'SUPERUSER')
        
        # 验证权限级别的值
        assert PermissionLevel.UNBOUND_USER == 0
        assert PermissionLevel.BOUND_USER == 1
        assert PermissionLevel.UNBOUND_ADMIN == 2
        assert PermissionLevel.BOUND_ADMIN == 3
        assert PermissionLevel.OWNER == 4
        assert PermissionLevel.SUPERUSER == 5
    
    @pytest.mark.asyncio
    async def test_permission_level_comparison(self, app: App):
        """
        实测试：权限级别比较
        
        验证权限级别可以正确比较
        """
        from services.permission import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证权限级别的大小关系
        assert PermissionLevel.UNBOUND_USER < PermissionLevel.BOUND_USER
        assert PermissionLevel.BOUND_USER < PermissionLevel.UNBOUND_ADMIN
        assert PermissionLevel.UNBOUND_ADMIN < PermissionLevel.BOUND_ADMIN
        assert PermissionLevel.BOUND_ADMIN < PermissionLevel.OWNER
        assert PermissionLevel.OWNER < PermissionLevel.SUPERUSER
        
        # 验证相等性
        assert PermissionLevel.UNBOUND_USER == PermissionLevel.UNBOUND_USER
        assert PermissionLevel.SUPERUSER != PermissionLevel.UNBOUND_USER
    
    @pytest.mark.asyncio
    async def test_check_command_permission_function_exists(self, app: App):
        """
        实测试：check_command_permission 函数存在
        
        验证权限检查函数已定义
        """
        from services.permission import check_command_permission
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证函数存在且可调用
        assert callable(check_command_permission)
    
    @pytest.mark.asyncio
    async def test_permission_config_defaults(self, app: App):
        """
        实测试：权限配置默认值
        
        验证命令的默认权限配置
        """
        from services.group_config import COMMAND_DEFAULTS
        from services.permission import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证每个命令都有权限配置
        for cmd_name, cmd_config in COMMAND_DEFAULTS.items():
            assert 'enabled' in cmd_config
            assert 'permission' in cmd_config
            
            # 获取权限配置
            perm_value = cmd_config.get('permission')
            assert perm_value is not None
            
            # 验证权限值是 PermissionLevel 类型
            assert isinstance(perm_value, PermissionLevel)


class TestPermissionFromStr:
    @pytest.mark.parametrize("input_str,expected", [
        ("unbound_user", 0),
        ("bound_user", 1),
        ("unbound_admin", 2),
        ("bound_admin", 3),
        ("owner", 4),
        ("superuser", 5),
        ("0", 0),
        ("1", 1),
        ("2", 2),
        ("3", 3),
        ("4", 4),
        ("5", 5),
    ])
    @pytest.mark.asyncio
    async def test_legal_inputs(self, app: App, input_str, expected):
        from services.permission import PermissionLevel

        bot, ctx = await create_mock_bot(app)
        result = PermissionLevel.from_str(input_str)
        assert result == expected

    @pytest.mark.parametrize("input_str,expected", [
        ("  unbound_user  ", 0),
        ("UNBOUND_USER", 0),
        ("BounD_UseR", 1),
    ])
    @pytest.mark.asyncio
    async def test_boundary_inputs(self, app: App, input_str, expected):
        from services.permission import PermissionLevel

        bot, ctx = await create_mock_bot(app)
        result = PermissionLevel.from_str(input_str)
        assert result == expected

    @pytest.mark.parametrize("input_str", [
        "invalid",
        "999",
        "6",
        "-1",
        "",
    ])
    @pytest.mark.asyncio
    async def test_invalid_inputs(self, app: App, input_str):
        from services.permission import PermissionLevel

        bot, ctx = await create_mock_bot(app)
        with pytest.raises(KeyError):
            PermissionLevel.from_str(input_str)


class TestPermissionRuntime:
    @pytest.mark.asyncio
    async def test_get_permission_level_admin_bound(self, app: App):
        from services.permission import get_permission_level, PermissionLevel
        from services.user_binding import user_binding_store, BindingRecord
        import time

        bot, ctx = await create_mock_bot(app)
        test_user_id = get_test_user_id(10)

        binding = BindingRecord(
            qq_id=test_user_id,
            vrc_user_id="usr_admin_bound",
            vrc_display_name="AdminBound",
            bound_at=time.time(),
            confirmed=True,
        )
        user_binding_store.set(binding)

        event = Mock()
        event.user_id = int(test_user_id)
        event.sender.role = "admin"
        from nonebot.adapters.onebot.v11 import GroupMessageEvent
        event.__class__ = GroupMessageEvent

        level = await get_permission_level(bot, event)
        assert level == PermissionLevel.BOUND_ADMIN

        user_binding_store.remove(test_user_id)

    @pytest.mark.asyncio
    async def test_get_permission_level_admin_unbound(self, app: App):
        from services.permission import get_permission_level, PermissionLevel
        from services.user_binding import user_binding_store

        bot, ctx = await create_mock_bot(app)
        test_user_id = get_test_user_id(11)

        user_binding_store.remove(test_user_id)

        event = Mock()
        event.user_id = int(test_user_id)
        event.sender.role = "admin"
        from nonebot.adapters.onebot.v11 import GroupMessageEvent
        event.__class__ = GroupMessageEvent

        level = await get_permission_level(bot, event)
        assert level == PermissionLevel.UNBOUND_ADMIN

    @pytest.mark.asyncio
    async def test_check_command_permission_insufficient(self, app: App):
        from services.permission import check_command_permission, PermissionLevel
        from services.group_config import group_config_store
        from services.user_binding import user_binding_store

        bot, ctx = await create_mock_bot(app)
        test_user_id = get_test_user_id(12)
        test_group_id = get_test_group_id(12)

        user_binding_store.remove(test_user_id)

        config = group_config_store.get(test_group_id)
        config.set_command_enabled("gban", True)
        config.set_command_permission("gban", PermissionLevel.OWNER)
        group_config_store.set(config)

        event = Mock()
        event.user_id = int(test_user_id)
        event.group_id = int(test_group_id)
        event.sender.role = "member"
        from nonebot.adapters.onebot.v11 import GroupMessageEvent
        event.__class__ = GroupMessageEvent
        event.__module__ = "nonebot.adapters.onebot.v11"

        has_perm, msg = await check_command_permission(
            bot, event, "gban"
        )

        assert has_perm is False
        assert "权限不足" in msg

        config.commands.clear()
        group_config_store.set(config)

    @pytest.mark.asyncio
    async def test_check_command_permission_group_disabled(self, app: App):
        from services.permission import check_command_permission, PermissionLevel
        from services.group_config import group_config_store
        from services.user_binding import user_binding_store, BindingRecord
        import time

        bot, ctx = await create_mock_bot(app)
        test_user_id = get_test_user_id(13)
        test_group_id = get_test_group_id(13)

        binding = BindingRecord(
            qq_id=test_user_id,
            vrc_user_id="usr_disabled_test",
            vrc_display_name="DisabledTest",
            bound_at=time.time(),
            confirmed=True,
        )
        user_binding_store.set(binding)

        config = group_config_store.get(test_group_id)
        config.set_command_enabled("gban", False)
        group_config_store.set(config)

        event = Mock()
        event.user_id = int(test_user_id)
        event.group_id = int(test_group_id)
        event.sender.role = "owner"
        from nonebot.adapters.onebot.v11 import GroupMessageEvent
        event.__class__ = GroupMessageEvent
        event.__module__ = "nonebot.adapters.onebot.v11"

        has_perm, msg = await check_command_permission(
            bot, event, "gban"
        )

        assert has_perm is False
        assert "已被禁用" in msg

        config.commands.clear()
        group_config_store.set(config)
        user_binding_store.remove(test_user_id)


class TestCheckVrcGroupRole:
    @pytest.mark.asyncio
    async def test_has_required_role(self, app: App):
        from services.permission import check_vrc_group_role
        from utils.VRC.vrc_models import GroupMember, GroupRole

        bot, ctx = await create_mock_bot(app)

        vrc_client = Mock()
        vrc_client.get_group_member = AsyncMock(return_value=GroupMember(
            id="mem_001", groupId="grp_001", userId="usr_001",
            roleIds=["role_moderator"]
        ))
        vrc_client.get_group_roles = AsyncMock(return_value=[
            GroupRole(id="role_moderator", name="moderator", isManagement=True),
        ])

        result = await check_vrc_group_role(
            vrc_client, "usr_001", "grp_001", required_roles=["moderator"]
        )
        assert result is True

    @pytest.mark.asyncio
    async def test_no_matching_role(self, app: App):
        from services.permission import check_vrc_group_role
        from utils.VRC.vrc_models import GroupMember, GroupRole

        bot, ctx = await create_mock_bot(app)

        vrc_client = Mock()
        vrc_client.get_group_member = AsyncMock(return_value=GroupMember(
            id="mem_002", groupId="grp_001", userId="usr_002",
            roleIds=["role_member"]
        ))
        vrc_client.get_group_roles = AsyncMock(return_value=[
            GroupRole(id="role_member", name="member", isManagement=False),
        ])

        result = await check_vrc_group_role(
            vrc_client, "usr_002", "grp_001", required_roles=["moderator"]
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_no_member(self, app: App):
        from services.permission import check_vrc_group_role

        bot, ctx = await create_mock_bot(app)

        vrc_client = Mock()
        vrc_client.get_group_member = AsyncMock(return_value=None)

        result = await check_vrc_group_role(
            vrc_client, "usr_999", "grp_001"
        )
        assert result is False

    @pytest.mark.asyncio
    async def test_exception(self, app: App):
        from services.permission import check_vrc_group_role

        bot, ctx = await create_mock_bot(app)

        vrc_client = Mock()
        vrc_client.get_group_member = AsyncMock(side_effect=Exception("API error"))

        result = await check_vrc_group_role(
            vrc_client, "usr_err", "grp_001"
        )
        assert result is False


class TestPermissionOrdering:
    @pytest.mark.asyncio
    async def test_ordering(self, app: App):
        from services.permission import PermissionLevel

        bot, ctx = await create_mock_bot(app)

        levels = [
            PermissionLevel.SUPERUSER,
            PermissionLevel.UNBOUND_USER,
            PermissionLevel.BOUND_ADMIN,
            PermissionLevel.OWNER,
            PermissionLevel.UNBOUND_ADMIN,
            PermissionLevel.BOUND_USER,
        ]
        sorted_levels = sorted(levels)

        assert sorted_levels == [
            PermissionLevel.UNBOUND_USER,
            PermissionLevel.BOUND_USER,
            PermissionLevel.UNBOUND_ADMIN,
            PermissionLevel.BOUND_ADMIN,
            PermissionLevel.OWNER,
            PermissionLevel.SUPERUSER,
        ]

    @pytest.mark.asyncio
    async def test_comparison(self, app: App):
        from services.permission import PermissionLevel

        bot, ctx = await create_mock_bot(app)

        assert PermissionLevel.UNBOUND_USER < PermissionLevel.BOUND_USER
        assert PermissionLevel.BOUND_USER <= PermissionLevel.UNBOUND_ADMIN
        assert PermissionLevel.UNBOUND_ADMIN > PermissionLevel.BOUND_USER
        assert PermissionLevel.BOUND_ADMIN >= PermissionLevel.UNBOUND_ADMIN
        assert PermissionLevel.OWNER != PermissionLevel.SUPERUSER
        assert PermissionLevel.SUPERUSER == PermissionLevel.SUPERUSER

class TestTempPermissions:
    @pytest.mark.asyncio
    async def test_set_temp_permission(self, app: App):
        from services.permission import set_temp_permission, clear_temp_permission, get_all_temp_permissions, PermissionLevel

        bot, ctx = await create_mock_bot(app)
        test_qq = "31415926535"

        set_temp_permission(test_qq, PermissionLevel.UNBOUND_ADMIN)
        all_temp = get_all_temp_permissions()
        assert test_qq in all_temp
        assert all_temp[test_qq] == PermissionLevel.UNBOUND_ADMIN

        clear_temp_permission(test_qq)
        all_temp2 = get_all_temp_permissions()
        assert test_qq not in all_temp2

    @pytest.mark.asyncio
    async def test_temp_permission_affects_get_level(self, app: App):
        from services.permission import get_permission_level, set_temp_permission, clear_temp_permission, PermissionLevel
        from unittest.mock import Mock

        bot, ctx = await create_mock_bot(app)
        test_qq = "27182818285"

        event = Mock()
        event.user_id = int(test_qq)
        event.sender.role = "member"
        from nonebot.adapters.onebot.v11 import GroupMessageEvent
        event.__class__ = GroupMessageEvent

        level_before = await get_permission_level(bot, event)
        assert level_before == PermissionLevel.UNBOUND_USER

        set_temp_permission(test_qq, PermissionLevel.OWNER)
        level_after = await get_permission_level(bot, event)
        assert level_after == PermissionLevel.OWNER

        clear_temp_permission(test_qq)

    @pytest.mark.asyncio
    async def test_superuser_path(self, app: App):
        from services.permission import get_permission_level, PermissionLevel
        from unittest.mock import Mock

        bot, ctx = await create_mock_bot(app)
        superusers = bot.config.superusers
        assert superusers, "no superusers configured"
        superuser_id = next(iter(superusers))

        event = Mock()
        event.user_id = int(superuser_id)
        event.sender.role = "member"
        from nonebot.adapters.onebot.v11 import GroupMessageEvent
        event.__class__ = GroupMessageEvent

        level = await get_permission_level(bot, event)
        assert level == PermissionLevel.SUPERUSER

    @pytest.mark.asyncio
    async def test_member_with_binding_become_bound(self, app: App):
        from services.permission import get_permission_level, PermissionLevel
        from services.user_binding import user_binding_store, BindingRecord
        from unittest.mock import Mock
        import time

        bot, ctx = await create_mock_bot(app)
        test_user_id = "1000000030"

        binding = BindingRecord(
            qq_id=test_user_id,
            vrc_user_id="usr_member",
            vrc_display_name="Member",
            bound_at=time.time(),
            confirmed=True,
        )
        user_binding_store.set(binding)

        event = Mock()
        event.user_id = int(test_user_id)
        event.sender.role = "member"
        from nonebot.adapters.onebot.v11 import GroupMessageEvent
        event.__class__ = GroupMessageEvent

        level = await get_permission_level(bot, event)
        assert level == PermissionLevel.BOUND_USER

        user_binding_store.remove(test_user_id)

class TestPermissionPrivateChat:
    @pytest.mark.asyncio
    async def test_get_permission_level_private_unbound(self, app: App):
        from services.permission import get_permission_level, PermissionLevel
        from unittest.mock import Mock

        bot, ctx = await create_mock_bot(app)

        event = Mock()
        event.user_id = 1111111111
        from nonebot.adapters.onebot.v11 import PrivateMessageEvent
        event.__class__ = PrivateMessageEvent

        level = await get_permission_level(bot, event)
        assert level == PermissionLevel.UNBOUND_USER

    @pytest.mark.asyncio
    async def test_get_permission_level_private_bound(self, app: App):
        from services.permission import get_permission_level, PermissionLevel
        from services.user_binding import user_binding_store, BindingRecord
        from unittest.mock import Mock
        import time

        bot, ctx = await create_mock_bot(app)
        test_qq = "31415926535"

        binding = BindingRecord(
            qq_id=test_qq,
            vrc_user_id="usr_priv",
            vrc_display_name="PrivateUser",
            bound_at=time.time(),
            confirmed=True,
        )
        user_binding_store.set(binding)

        event = Mock()
        event.user_id = int(test_qq)
        from nonebot.adapters.onebot.v11 import PrivateMessageEvent
        event.__class__ = PrivateMessageEvent

        level = await get_permission_level(bot, event)
        assert level == PermissionLevel.BOUND_USER

        user_binding_store.remove(test_qq)

    @pytest.mark.asyncio
    async def test_check_command_permission_private_sufficient(self, app: App):
        from services.permission import check_command_permission, PermissionLevel
        from services.user_binding import user_binding_store, BindingRecord
        from unittest.mock import Mock
        import time

        bot, ctx = await create_mock_bot(app)
        test_qq = "27182818285"

        binding = BindingRecord(
            qq_id=test_qq,
            vrc_user_id="usr_priv_cmd",
            vrc_display_name="PrivateCmd",
            bound_at=time.time(),
            confirmed=True,
        )
        user_binding_store.set(binding)

        event = Mock()
        event.user_id = int(test_qq)
        from nonebot.adapters.onebot.v11 import PrivateMessageEvent
        event.__class__ = PrivateMessageEvent

        has_perm, msg = await check_command_permission(
            bot, event, "bindinfo", required_level=PermissionLevel.BOUND_USER
        )

        assert has_perm is True
        assert msg == ""

        user_binding_store.remove(test_qq)

    @pytest.mark.asyncio
    async def test_check_command_permission_private_insufficient(self, app: App):
        from services.permission import check_command_permission, PermissionLevel
        from unittest.mock import Mock

        bot, ctx = await create_mock_bot(app)

        event = Mock()
        event.user_id = 9999999999
        from nonebot.adapters.onebot.v11 import PrivateMessageEvent
        event.__class__ = PrivateMessageEvent

        has_perm, msg = await check_command_permission(
            bot, event, "gban", required_level=PermissionLevel.SUPERUSER
        )

        assert has_perm is False
        assert "not enough" in msg.lower() or "权限" in msg

    @pytest.mark.asyncio
    async def test_check_command_permission_group_sufficient(self, app: App):
        from services.permission import check_command_permission, PermissionLevel
        from services.group_config import group_config_store
        from unittest.mock import Mock

        bot, ctx = await create_mock_bot(app)
        test_user_id = "1000000041"
        test_group_id = "1000000041"

        config = group_config_store.get(test_group_id)
        config.set_command_enabled("whereis", True)
        config.set_command_permission("whereis", PermissionLevel.UNBOUND_USER)
        group_config_store.set(config)

        event = Mock()
        event.user_id = int(test_user_id)
        event.group_id = int(test_group_id)
        event.sender.role = "member"
        from nonebot.adapters.onebot.v11 import GroupMessageEvent
        event.__class__ = GroupMessageEvent
        event.__module__ = "nonebot.adapters.onebot.v11"

        has_perm, msg = await check_command_permission(
            bot, event, "whereis"
        )

        assert has_perm is True
        assert msg == ""

        config.commands.clear()
        group_config_store.set(config)

