"""
用户绑定服务测试 - 实测试

测试用户绑定的增删改查功能
"""
import pytest
from nonebug import App
from tests import create_mock_bot, get_test_user_id


class TestUserBindingReal:
    """用户绑定实测试"""
    
    @pytest.mark.asyncio
    async def test_binding_record_creation(self, app: App):
        """
        实测试：创建绑定记录
        
        验证 BindingRecord 可以正确创建
        """
        from services.user_binding import BindingRecord
        import time
        
        bot, ctx = await create_mock_bot(app)
        
        binding = BindingRecord(
            qq_id="1000000001",
            vrc_user_id="usr_123456",
            vrc_display_name="TestUser",
            bound_at=time.time(),
            confirmed=True
        )
        
        assert binding.qq_id == "1000000001"
        assert binding.vrc_user_id == "usr_123456"
        assert binding.vrc_display_name == "TestUser"
        assert binding.confirmed is True
    
    @pytest.mark.asyncio
    async def test_binding_record_pending(self, app: App):
        """
        实测试：创建待确认的绑定记录
        
        验证待确认状态的绑定记录
        """
        from services.user_binding import BindingRecord
        import time
        
        bot, ctx = await create_mock_bot(app)
        
        binding = BindingRecord(
            qq_id="1000000001",
            vrc_user_id="usr_123456",
            vrc_display_name="TestUser",
            bound_at=time.time(),
            confirmed=False,
            verify_code="ABC123",
            verify_code_expires=time.time() + 180
        )
        
        assert binding.confirmed is False
        assert binding.verify_code == "ABC123"
        assert binding.verify_code_expires is not None
    
    @pytest.mark.asyncio
    async def test_binding_store_get_by_qq(self, app: App, cleanup_after_test):
        """
        实测试：通过 QQ ID 查询绑定
        
        验证可以通过 QQ ID 获取绑定记录
        """
        from services.user_binding import user_binding_store, BindingRecord
        import time
        
        bot, ctx = await create_mock_bot(app)
        test_user_id = get_test_user_id()
        
        # 创建绑定
        binding = BindingRecord(
            qq_id=test_user_id,
            vrc_user_id="usr_test",
            vrc_display_name="TestUser",
            bound_at=time.time(),
            confirmed=True
        )
        user_binding_store.set(binding)
        
        # 查询绑定
        found = user_binding_store.get_by_qq(test_user_id)
        assert found is not None
        assert found.qq_id == test_user_id
        assert found.vrc_user_id == "usr_test"
    
    @pytest.mark.asyncio
    async def test_binding_store_get_by_vrc(self, app: App, cleanup_after_test):
        """
        实测试：通过 VRC ID 查询绑定
        
        验证可以通过 VRC 用户 ID 获取绑定记录
        """
        from services.user_binding import user_binding_store, BindingRecord
        import time
        
        bot, ctx = await create_mock_bot(app)
        test_user_id = get_test_user_id()
        
        # 创建绑定
        binding = BindingRecord(
            qq_id=test_user_id,
            vrc_user_id="usr_unique_123",
            vrc_display_name="UniqueUser",
            bound_at=time.time(),
            confirmed=True
        )
        user_binding_store.set(binding)
        
        # 通过 VRC ID 查询
        found = user_binding_store.get_by_vrc("usr_unique_123")
        assert found is not None
        assert found.vrc_user_id == "usr_unique_123"
        assert found.qq_id == test_user_id
    
    @pytest.mark.asyncio
    async def test_binding_store_remove(self, app: App, cleanup_after_test):
        """
        实测试：删除绑定
        
        验证可以删除绑定记录
        """
        from services.user_binding import user_binding_store, BindingRecord
        import time
        
        bot, ctx = await create_mock_bot(app)
        test_user_id = get_test_user_id()
        
        # 创建绑定
        binding = BindingRecord(
            qq_id=test_user_id,
            vrc_user_id="usr_temp",
            vrc_display_name="TempUser",
            bound_at=time.time(),
            confirmed=True
        )
        user_binding_store.set(binding)
        
        # 验证存在
        found = user_binding_store.get_by_qq(test_user_id)
        assert found is not None
        
        # 删除绑定
        user_binding_store.remove(test_user_id)
        
        # 验证已删除
        deleted = user_binding_store.get_by_qq(test_user_id)
        assert deleted is None
    
    @pytest.mark.asyncio
    async def test_binding_store_nonexistent_qq(self, app: App):
        """
        实测试：查询不存在的 QQ ID
        
        验证查询不存在的 QQ ID 返回 None
        """
        from services.user_binding import user_binding_store
        
        bot, ctx = await create_mock_bot(app)
        
        # 查询不存在的 QQ
        result = user_binding_store.get_by_qq("999999999")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_binding_store_nonexistent_vrc(self, app: App):
        """
        实测试：查询不存在的 VRC ID
        
        验证查询不存在的 VRC ID 返回 None
        """
        from services.user_binding import user_binding_store
        
        bot, ctx = await create_mock_bot(app)
        
        # 查询不存在的 VRC ID
        result = user_binding_store.get_by_vrc("usr_nonexistent")
        assert result is None
    
    @pytest.mark.asyncio
    async def test_global_user_binding_store_instance(self, app: App):
        """
        实测试：全局用户绑定存储实例
        
        验证全局 user_binding_store 实例存在且可用
        """
        from services.user_binding import user_binding_store, UserBindingStore
        
        bot, ctx = await create_mock_bot(app)
        
        # 验证是 UserBindingStore 实例
        assert isinstance(user_binding_store, UserBindingStore)
        
        # 验证可以使用
        result = user_binding_store.get_by_qq("test")
        assert result is None or hasattr(result, 'qq_id')
