"""
Services 模块测试 - 虚实结合

虚测：模块导入、配置验证、权限检查逻辑
实测试：配置持久化、数据存储等
"""
import pytest
from nonebug import App


class TestGroupConfig:
    """群组配置服务测试"""
    
    @pytest.mark.asyncio
    async def test_command_defaults_exist(self):
        """虚测：验证默认命令配置存在且合法"""
        from services.group_config import COMMAND_DEFAULTS
        
        # 验证命令数量
        assert len(COMMAND_DEFAULTS) > 0, "应该定义至少一个命令"
        
        # 验证关键命令存在
        required_commands = [
            "vrclLogin", "2fa", "vrcCheck", "whereis", "instances", 
            "whois", "bind", "confirm", "unbind", "bindinfo",
            "gmembers", "ginvite", "gkick", "gban", "gunban",
            "grole", "grequests", "gaccept", "greject",
            "gannounce", "gdelannounce", "gaudit"
        ]
        
        for cmd in required_commands:
            assert cmd in COMMAND_DEFAULTS, f"命令 #{cmd} 未定义"
            config = COMMAND_DEFAULTS[cmd]
            assert "enabled" in config, f"命令 #{cmd} 缺少 enabled 字段"
            assert "permission" in config, f"命令 #{cmd} 缺少 permission 字段"
            assert isinstance(config["enabled"], bool), f"命令 #{cmd} 的 enabled 应该是布尔值"
    
    @pytest.mark.asyncio
    async def test_group_config_crud(self, app: App, test_group_id: str, cleanup_after_test):
        """实测试：群组配置的增删改查（带自动清理）"""
        from services.group_config import group_config_store, GroupConfig
        from services.permission import PermissionLevel
        from tests import create_mock_bot
        
        # 创建模拟 Bot
        bot, ctx = await create_mock_bot(app)
        
        # 获取配置
        config = group_config_store.get(test_group_id)
        assert config is not None
        assert isinstance(config, GroupConfig)
        
        # 修改配置
        config.set_command_enabled("gban", False)
        config.set_command_permission("whereis", PermissionLevel.BOUND_ADMIN)
        
        # 保存并重新加载
        group_config_store.set(config)
        config_reloaded = group_config_store.get(test_group_id)
        
        assert config_reloaded.is_command_enabled('gban') == False
        assert config_reloaded.get_command_permission('whereis') == PermissionLevel.BOUND_ADMIN
        
        # 注意：不需要手动清理，cleanup_after_test fixture 会在测试结束后自动清理


class TestPermission:
    """权限服务测试"""
    
    @pytest.mark.asyncio
    async def test_permission_level_from_str(self):
        """虚测：权限级别字符串转换"""
        from services.permission import PermissionLevel
        
        test_cases = [
            ("unbound_user", PermissionLevel.UNBOUND_USER),
            ("bound_user", PermissionLevel.BOUND_USER),
            ("unbound_admin", PermissionLevel.UNBOUND_ADMIN),
            ("bound_admin", PermissionLevel.BOUND_ADMIN),
            ("owner", PermissionLevel.OWNER),
            ("superuser", PermissionLevel.SUPERUSER),
            ("0", PermissionLevel.UNBOUND_USER),
            ("1", PermissionLevel.BOUND_USER),
            ("2", PermissionLevel.UNBOUND_ADMIN),
            ("3", PermissionLevel.BOUND_ADMIN),
            ("4", PermissionLevel.OWNER),
            ("5", PermissionLevel.SUPERUSER),
        ]
        
        for input_str, expected in test_cases:
            result = PermissionLevel.from_str(input_str)
            assert result == expected, f"'{input_str}' 应该转换为 {expected}"
    
    @pytest.mark.asyncio
    async def test_permission_comparison(self):
        """虚测：权限级别比较逻辑"""
        from services.permission import PermissionLevel
        
        # 验证权限等级顺序
        assert PermissionLevel.UNBOUND_USER < PermissionLevel.BOUND_USER
        assert PermissionLevel.BOUND_USER < PermissionLevel.UNBOUND_ADMIN
        assert PermissionLevel.UNBOUND_ADMIN < PermissionLevel.BOUND_ADMIN
        assert PermissionLevel.BOUND_ADMIN < PermissionLevel.OWNER
        assert PermissionLevel.OWNER < PermissionLevel.SUPERUSER


class TestUserBinding:
    """用户绑定服务测试"""
    
    @pytest.mark.asyncio
    async def test_user_binding_import(self):
        """虚测：验证用户绑定模块可导入"""
        from services.user_binding import user_binding_store
        assert user_binding_store is not None


class TestMessageUtils:
    """消息工具测试"""
    
    @pytest.mark.asyncio
    async def test_message_utils_import(self):
        """虚测：验证消息工具模块可导入"""
        from services.message_utils import format_success, format_error, send_long_message
        assert format_success is not None
        assert format_error is not None
        assert send_long_message is not None


class TestApiGuard:
    """API 守卫测试"""
    
    @pytest.mark.asyncio
    async def test_api_guard_import(self):
        """虚测：验证 API 守卫模块可导入"""
        from services.api_guard import api_guard
        assert api_guard is not None
