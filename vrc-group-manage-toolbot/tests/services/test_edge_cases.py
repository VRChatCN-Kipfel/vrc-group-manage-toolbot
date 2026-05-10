"""
Services 层边界情况和异常处理测试

测试各种边界条件和异常情况下的行为
"""
import pytest
from nonebug import App
from tests import create_mock_bot


class TestPermissionEdgeCases:
    """权限系统边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_permission_level_comparison(self, app: App):
        """
        实测试：权限级别比较
        
        验证不同权限级别的比较逻辑正确
        """
        from services.permission import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证比较操作
        assert PermissionLevel.SUPERUSER > PermissionLevel.OWNER
        assert PermissionLevel.OWNER > PermissionLevel.BOUND_ADMIN
        assert PermissionLevel.BOUND_ADMIN > PermissionLevel.UNBOUND_ADMIN
        assert PermissionLevel.UNBOUND_ADMIN > PermissionLevel.BOUND_USER
        assert PermissionLevel.BOUND_USER > PermissionLevel.UNBOUND_USER
        
        # 验证相等比较
        assert PermissionLevel.SUPERUSER == PermissionLevel.SUPERUSER
        assert PermissionLevel.UNBOUND_USER == 0
    
    @pytest.mark.asyncio
    async def test_permission_level_values(self, app: App):
        """
        实测试：权限级别值范围
        
        验证所有权限级别的值在合理范围内
        """
        from services.permission import PermissionLevel
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证值的范围
        assert 0 <= PermissionLevel.UNBOUND_USER <= 5
        assert 0 <= PermissionLevel.BOUND_USER <= 5
        assert 0 <= PermissionLevel.UNBOUND_ADMIN <= 5
        assert 0 <= PermissionLevel.BOUND_ADMIN <= 5
        assert 0 <= PermissionLevel.OWNER <= 5
        assert 0 <= PermissionLevel.SUPERUSER <= 5


class TestApiGuardEdgeCases:
    """API 守卫边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_cache_with_none_value(self, app: App):
        """
        实测试：缓存 None 值
        
        验证可以缓存 None 值
        """
        from services.api_guard import ApiGuard
        
        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard()
        
        # 缓存 None
        guard.cache_set("none_key", None, ttl=60)
        
        # 读取应该返回 None（但键存在）
        cached = guard.cache_get("none_key")
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_cache_expiry_immediate(self, app: App):
        """
        实测试：缓存立即过期
        
        验证 TTL=0 时缓存立即过期
        """
        from services.api_guard import ApiGuard
        import time
        
        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard()
        
        # 设置 TTL=0
        guard.cache_set("expire_key", "value", ttl=0)
        
        # 等待一小段时间
        time.sleep(0.1)
        
        # 应该已过期
        cached = guard.cache_get("expire_key")
        assert cached is None
    
    @pytest.mark.asyncio
    async def test_retry_with_exception(self, app: App):
        """
        实测试：重试机制处理异常
        
        验证 API 调用抛出异常时的处理逻辑
        """
        from services.api_guard import ApiGuard
        
        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard(max_retries=2)
        
        call_count = 0
        
        async def failing_api():
            nonlocal call_count
            call_count += 1
            raise Exception("API Error")
        
        success, result, error = await guard.call_with_retry(
            failing_api, _endpoint="test"
        )
        
        # 普通异常不重试，只调用1次
        assert success is False
        assert call_count == 1
        assert error is not None
        assert "服务异常" in str(error)
    
    @pytest.mark.asyncio
    async def test_statistics_tracking(self, app: App):
        """
        实测试：统计信息追踪
        
        验证 API 调用统计正确记录
        """
        from services.api_guard import ApiGuard
        
        bot, ctx = await create_mock_bot(app)
        guard = ApiGuard()
        
        async def mock_api():
            return {"data": "test"}
        
        # 多次调用
        await guard.call_with_retry(mock_api, _endpoint="test1")
        await guard.call_with_retry(mock_api, _endpoint="test1")
        await guard.call_with_retry(mock_api, _endpoint="test2")
        
        # 检查统计（键名格式为 "endpoint:ok"）
        stats = guard.get_stats()
        assert stats.get("test1:ok", 0) == 2
        assert stats.get("test2:ok", 0) == 1


class TestMessageUtilsEdgeCases:
    """消息工具边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_format_error_empty_message(self, app: App):
        """
        实测试：格式化空错误消息
        
        验证空消息的处理
        """
        from services.message_utils import format_error
        
        bot, ctx = await create_mock_bot(app)
        
        msg = format_error("")
        assert "❌" in msg
    
    @pytest.mark.asyncio
    async def test_format_success_special_characters(self, app: App):
        """
        实测试：成功消息包含特殊字符
        
        验证特殊字符正确处理
        """
        from services.message_utils import format_success
        
        bot, ctx = await create_mock_bot(app)
        
        msg = format_success("测试\n换行\t制表符")
        assert "✅" in msg
        assert "\n" in msg
        assert "\t" in msg
    
    @pytest.mark.asyncio
    async def test_format_query_result_empty_content(self, app: App):
        """
        实测试：查询结果为空内容
        
        验证空内容的格式化
        """
        from services.message_utils import format_query_result
        
        bot, ctx = await create_mock_bot(app)
        
        msg = format_query_result("标题", "")
        assert "【标题】" in msg
        assert "─" in msg
    
    @pytest.mark.asyncio
    async def test_max_message_length_constant(self, app: App):
        """
        实测试：最大消息长度常量
        
        验证 MAX_MESSAGE_LENGTH 是合理的正整数
        """
        from services.message_utils import MAX_MESSAGE_LENGTH
        
        bot, ctx = await create_mock_bot(app)
        
        assert isinstance(MAX_MESSAGE_LENGTH, int)
        assert MAX_MESSAGE_LENGTH > 0
        assert MAX_MESSAGE_LENGTH <= 5000  # OneBot 限制


class TestUserBindingEdgeCases:
    """用户绑定边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_binding_with_empty_display_name(self, app: App):
        """
        实测试：绑定记录包含空显示名称
        
        验证空显示名称的处理
        """
        from services.user_binding import user_binding_store, BindingRecord
        import time
        
        bot, ctx = await create_mock_bot(app)
        test_user_id = "888888888"  # 使用不同的 ID 避免冲突
        
        # 创建空显示名称的绑定
        binding = BindingRecord(
            qq_id=test_user_id,
            vrc_user_id="usr_test",
            vrc_display_name="",  # 空名称
            bound_at=time.time(),
            confirmed=True
        )
        user_binding_store.set(binding)
        
        # 应该能正常查询
        found = user_binding_store.get_by_qq(test_user_id)
        assert found is not None
        assert found.vrc_display_name == ""
        
        # 清理
        user_binding_store.remove(test_user_id)
    
    @pytest.mark.asyncio
    async def test_binding_store_remove_nonexistent(self, app: App):
        """
        实测试：删除不存在的绑定
        
        验证删除不存在绑定时不会出错
        """
        from services.user_binding import user_binding_store
        
        bot, ctx = await create_mock_bot(app)
        
        # 删除不存在的绑定不应抛出异常
        user_binding_store.remove("nonexistent_user")
    
    @pytest.mark.asyncio
    async def test_binding_record_model_dump(self, app: App):
        """
        实测试：绑定记录序列化
        
        验证 BindingRecord 可以正确序列化为字典
        """
        from services.user_binding import BindingRecord
        import time
        
        bot, ctx = await create_mock_bot(app)
        
        binding = BindingRecord(
            qq_id="123456789",
            vrc_user_id="usr_test",
            vrc_display_name="TestUser",
            bound_at=time.time(),
            confirmed=True
        )
        
        # 序列化
        data = binding.model_dump()
        
        assert isinstance(data, dict)
        assert data["qq_id"] == "123456789"
        assert data["vrc_user_id"] == "usr_test"
        assert data["confirmed"] is True


class TestGroupConfigEdgeCases:
    """群组配置边界情况测试"""
    
    @pytest.mark.asyncio
    async def test_config_with_unknown_command(self, app: App, cleanup_after_test):
        """
        实测试：配置中包含未知命令
        
        验证未知命令可以正常设置（不会报错）
        """
        from services.group_config import group_config_store
        
        bot, ctx = await create_mock_bot(app)
        test_group_id = "999999999"
        
        config = group_config_store.get(test_group_id)
        
        # 设置未知命令的配置（应该不会报错）
        config.set_command_enabled("unknown_command", True)
        
        # 应该能正常获取
        assert config.is_command_enabled("unknown_command") is True
    
    @pytest.mark.asyncio
    async def test_config_default_values(self, app: App):
        """
        实测试：配置默认值
        
        验证新配置的默认值合理
        """
        from services.group_config import GroupConfig
        
        bot, ctx = await create_mock_bot(app)
        
        config = GroupConfig(qq_group_id="test_group")
        
        # 验证默认值
        assert config.notify_enabled is False  # 默认为 False
        assert config.admin_ops_enabled is True
        assert config.allow_user_bind is True
        assert config.default_vrc_group is None
