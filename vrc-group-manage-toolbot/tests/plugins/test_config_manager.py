"""
配置管理插件测试 - 虚测为主

测试配置管理命令的存在性和基本结构
"""
import pytest
from unittest.mock import Mock
from nonebug import App
from tests import create_mock_bot


class TestConfigManagerCommands:
    """配置管理命令存在性测试"""
    
    @pytest.mark.asyncio
    async def test_bot_command_exists(self, app: App):
        """
        虚测：bot 命令存在
        
        验证 bot 配置管理命令已正确注册
        """
        from plugins.config_manager import config_cmd
        
        bot, ctx = await create_mock_bot(app)
        
        assert config_cmd is not None
        assert hasattr(config_cmd, 'handle')
    
    @pytest.mark.asyncio
    async def test_handle_functions_exist(self, app: App):
        """
        虚测：命令处理函数存在
        
        验证所有子命令处理函数都已定义
        """
        from plugins.config_manager import (
            handle_config,
            handle_status,
            handle_list,
            handle_enable,
            handle_disable,
            handle_permission,
            handle_reset,
        )
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证函数存在且可调用
        assert callable(handle_config)
        assert callable(handle_status)
        assert callable(handle_list)
        assert callable(handle_enable)
        assert callable(handle_disable)
        assert callable(handle_permission)
        assert callable(handle_reset)
    
    @pytest.mark.asyncio
    async def test_temp_permission_functions_exist(self, app: App):
        """
        虚测：临时权限函数存在
        
        验证临时权限相关函数已定义
        """
        from plugins.config_manager import (
            handle_set_temp_permission,
            handle_clear_temp_permission,
            handle_show_temp_permissions,
        )
        
        bot, ctx = await create_mock_bot(app)
        
        assert callable(handle_set_temp_permission)
        assert callable(handle_clear_temp_permission)
        assert callable(handle_show_temp_permissions)
    
    @pytest.mark.asyncio
    async def test_command_defaults_imported(self, app: App):
        """
        虚测：命令默认配置已导入
        
        验证 COMMAND_DEFAULTS 已正确导入
        """
        from plugins.config_manager import COMMAND_DEFAULTS
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证是字典且非空
        assert isinstance(COMMAND_DEFAULTS, dict)
        assert len(COMMAND_DEFAULTS) > 0
    
    @pytest.mark.asyncio
    async def test_permission_level_imported(self, app: App):
        """
        虚测：权限级别已导入
        
        验证 PermissionLevel 已正确导入
        """
        from plugins.config_manager import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证可以使用
        assert hasattr(PermissionLevel, 'SUPERUSER')
        assert hasattr(PermissionLevel, 'OWNER')


class TestExtractAtQQ:
    def _make_event(self, raw_message: str, segments=None):
        from nonebot.adapters.onebot.v11 import Message, MessageSegment

        event = Mock()
        event.raw_message = raw_message

        if segments is not None:
            event.get_message.return_value = Message(segments)
        else:
            event.get_message.return_value = Message(raw_message)

        return event

    @pytest.mark.asyncio
    async def test_cq_format(self, app: App):
        from plugins.config_manager import _extract_at_qq

        bot, ctx = await create_mock_bot(app)
        event = self._make_event(
            "#bot settemppermission [CQ:at,qq=123456] 3"
        )

        result = _extract_at_qq(event)
        assert result == "123456"

    @pytest.mark.asyncio
    async def test_napcat_format(self, app: App):
        from plugins.config_manager import _extract_at_qq

        bot, ctx = await create_mock_bot(app)
        event = self._make_event(
            "#bot settemppermission [at:qq=789012] 3"
        )

        result = _extract_at_qq(event)
        assert result == "789012"

    @pytest.mark.asyncio
    async def test_segment_fallback(self, app: App):
        from plugins.config_manager import _extract_at_qq
        from nonebot.adapters.onebot.v11 import MessageSegment

        bot, ctx = await create_mock_bot(app)
        at_seg = MessageSegment.at("111222")
        event = self._make_event(
            "#bot settemppermission @someone 3",
            segments=[at_seg]
        )

        result = _extract_at_qq(event)
        assert result == "111222"

    @pytest.mark.asyncio
    async def test_at_all_ignored(self, app: App):
        from plugins.config_manager import _extract_at_qq

        bot, ctx = await create_mock_bot(app)
        event = self._make_event(
            "[CQ:at,qq=all] test message"
        )

        result = _extract_at_qq(event)
        assert result is None

    @pytest.mark.asyncio
    async def test_no_at(self, app: App):
        from plugins.config_manager import _extract_at_qq

        bot, ctx = await create_mock_bot(app)
        event = self._make_event(
            "#bot status"
        )

        result = _extract_at_qq(event)
        assert result is None
